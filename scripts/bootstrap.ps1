param(
  [string]$RepoUrl = "https://github.com/bagbag16/ai-collab-scorecard",
  [string]$Branch = "main",
  [string]$SourcePath = "",
  [string]$CodexHome = "",
  [switch]$NoNetwork,
  [switch]$NoInstallPyYAML,
  [switch]$NoRenderSelfCheck
)

$ErrorActionPreference = "Stop"

$SkillName = "ai-collab-scorecard"
$Result = [ordered]@{
  status = "ok"
  skill_name = $SkillName
  source = ""
  acquisition = ""
  installed_to = ""
  checks = [ordered]@{}
  repairs = @()
  warnings = @()
  blockers = @()
  continue_in_current_session = ""
}

function Add-Warning([string]$Message) {
  $script:Result.warnings += $Message
  if ($script:Result.status -eq "ok") { $script:Result.status = "warn" }
}

function Add-Blocker([string]$Message) {
  $script:Result.blockers += $Message
  $script:Result.status = "blocked"
}

function Resolve-CodexRoot {
  if ($CodexHome) { return (New-Item -ItemType Directory -Force -Path $CodexHome).FullName }
  if ($env:CODEX_HOME) { return (New-Item -ItemType Directory -Force -Path $env:CODEX_HOME).FullName }
  return (New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE ".codex")).FullName
}

function Test-SkillSource([string]$Path) {
  if (-not $Path) { return $false }
  return (Test-Path -LiteralPath (Join-Path $Path "SKILL.md")) -and
    (Test-Path -LiteralPath (Join-Path $Path "scripts")) -and
    (Test-Path -LiteralPath (Join-Path $Path "references")) -and
    (Test-Path -LiteralPath (Join-Path $Path "assets"))
}

function Get-LocalSource {
  if ($SourcePath -and (Test-SkillSource $SourcePath)) {
    $script:Result.acquisition = "source-path"
    return (Resolve-Path -LiteralPath $SourcePath).Path
  }

  $repoRoot = Split-Path -Parent $PSScriptRoot
  if (Test-SkillSource $repoRoot) {
    $script:Result.acquisition = "current-repository"
    return (Resolve-Path -LiteralPath $repoRoot).Path
  }

  return ""
}

function Assert-SafeTempPath([string]$Path) {
  $tempRoot = [System.IO.Path]::GetFullPath($env:TEMP)
  $full = [System.IO.Path]::GetFullPath($Path)
  if (-not $full.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to clean non-temp path: $full"
  }
}

function Acquire-FromNetwork {
  if ($NoNetwork) {
    Add-Blocker "No local skill source was found, and network acquisition is disabled."
    return ""
  }

  $workRoot = Join-Path $env:TEMP "ai-collab-scorecard-bootstrap"
  Assert-SafeTempPath $workRoot
  Remove-Item -Recurse -Force $workRoot -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $workRoot | Out-Null

  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($git) {
    $cloneDir = Join-Path $workRoot $SkillName
    try {
      & git clone --depth 1 --branch $Branch $RepoUrl $cloneDir | Out-Null
      if (Test-SkillSource $cloneDir) {
        $script:Result.acquisition = "git"
        return (Resolve-Path -LiteralPath $cloneDir).Path
      }
      Add-Warning "Git clone completed, but the skill structure was not detected. Falling back to zip."
    } catch {
      Add-Warning "Git clone failed. Falling back to zip. $($_.Exception.Message)"
    }
  } else {
    Add-Warning "Git was not found. Falling back to main.zip."
  }

  $zipUrl = ($RepoUrl.TrimEnd("/")) + "/archive/refs/heads/$Branch.zip"
  $zipPath = Join-Path $workRoot "$SkillName.zip"
  $extractDir = Join-Path $workRoot "zip"
  try {
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    Expand-Archive -LiteralPath $zipPath -DestinationPath $extractDir -Force
    $source = Get-ChildItem -LiteralPath $extractDir -Directory |
      Where-Object { Test-SkillSource $_.FullName } |
      Select-Object -First 1
    if ($source) {
      $script:Result.acquisition = "zip"
      return $source.FullName
    }
    Add-Blocker "The zip archive was downloaded, but no complete skill folder was found."
  } catch {
    Add-Blocker "Could not download or extract the repository. $($_.Exception.Message)"
  }
  return ""
}

function Copy-Skill([string]$Source, [string]$Destination) {
  if (-not (Test-SkillSource $Source)) {
    Add-Blocker "The source folder is not a complete skill: $Source"
    return
  }
  New-Item -ItemType Directory -Force -Path $Destination | Out-Null
  $srcFull = [System.IO.Path]::GetFullPath($Source).TrimEnd("\")
  $dstFull = [System.IO.Path]::GetFullPath($Destination).TrimEnd("\")
  if ($srcFull -ieq $dstFull) {
    $script:Result.repairs += "Source is already the install directory; copy skipped."
    return
  }
  Copy-Item -Recurse -Force -Path (Join-Path $Source "*") -Destination $Destination
  $script:Result.repairs += "Installed or updated the skill in the local Codex skills directory."
}

function Run-JsonScript([string]$ScriptPath) {
  if (-not (Test-Path -LiteralPath $ScriptPath)) {
    return @{ status = "missing"; detail = "not found" }
  }
  try {
    $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath 2>&1
    $text = ($raw | Out-String).Trim()
    if (-not $text) { return @{ status = "warn"; detail = "no output" } }
    return ($text | ConvertFrom-Json)
  } catch {
    return @{ status = "fail"; detail = $_.Exception.Message }
  }
}

function Ensure-PyYAML($Diagnostic) {
  if ($NoInstallPyYAML) { return }
  $pyyaml = @($Diagnostic.checks | Where-Object { $_.name -eq "pyyaml" } | Select-Object -First 1)
  if (-not $pyyaml -or $pyyaml.status -eq "ok") { return }
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    Add-Warning "PyYAML is missing, but python was not found. Automatic install skipped."
    return
  }
  try {
    & python -m pip install --user PyYAML | Out-Null
    $script:Result.repairs += "Installed or confirmed PyYAML."
  } catch {
    Add-Warning "Automatic PyYAML install failed. $($_.Exception.Message)"
  }
}

function Run-QuickValidate([string]$SkillDir) {
  $codexRoot = Resolve-CodexRoot
  $validator = Join-Path $codexRoot "skills\.system\skill-creator\scripts\quick_validate.py"
  if (-not (Test-Path -LiteralPath $validator)) {
    Add-Warning "System skill validator was not found. Structure validation skipped."
    return "skipped"
  }
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    Add-Warning "Python was not found. Structure validation skipped."
    return "skipped"
  }
  try {
    $old = $env:PYTHONUTF8
    $env:PYTHONUTF8 = "1"
    & python $validator $SkillDir | Out-Null
    return "ok"
  } catch {
    Add-Warning "Skill structure validation failed. $($_.Exception.Message)"
    return "warn"
  } finally {
    $env:PYTHONUTF8 = $old
  }
}

function Run-RenderSelfCheck([string]$SkillDir) {
  if ($NoRenderSelfCheck) { return "skipped" }
  $scriptPath = Join-Path $SkillDir "scripts\self_check_render_determinism.ps1"
  if (-not (Test-Path -LiteralPath $scriptPath)) { return "missing" }
  try {
    $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath 2>&1
    $json = (($raw | Out-String).Trim() | ConvertFrom-Json)
    if ($json.status -eq "ok") { return "ok" }
    Add-Warning "Deterministic share-card render self-check did not pass."
    return "warn"
  } catch {
    Add-Warning "Deterministic share-card render self-check failed. $($_.Exception.Message)"
    return "warn"
  }
}

$source = Get-LocalSource
if (-not $source) { $source = Acquire-FromNetwork }
if ($source) {
  $Result.source = $source
  $codexRoot = Resolve-CodexRoot
  $skillsRoot = New-Item -ItemType Directory -Force -Path (Join-Path $codexRoot "skills")
  $destination = Join-Path $skillsRoot.FullName $SkillName
  $Result.installed_to = $destination
  Copy-Skill $source $destination

  $diagScript = Join-Path $destination "scripts\check_environment.ps1"
  $diag = Run-JsonScript $diagScript
  $Result.checks.environment = $diag.status
  if ($diag.status -eq "fail") { Add-Warning "Environment diagnostic has failed checks." }
  Ensure-PyYAML $diag

  $diag2 = Run-JsonScript $diagScript
  $Result.checks.environment_after_repair = $diag2.status
  $Result.checks.quick_validate = Run-QuickValidate $destination
  $Result.checks.render_self_check = Run-RenderSelfCheck $destination
  $Result.continue_in_current_session = "Read $destination\SKILL.md and $destination\references\setup-and-data-sources.md, then continue the assessment in this same chat. Do not ask the user to open a new window."
}

if ($Result.blockers.Count -gt 0) { $Result.status = "blocked" }
elseif ($Result.warnings.Count -gt 0 -and $Result.status -eq "ok") { $Result.status = "warn" }

$Result | ConvertTo-Json -Depth 8
