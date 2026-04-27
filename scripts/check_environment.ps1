param(
  [string]$SkillDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $SkillDir) {
  $SkillDir = Split-Path -Parent $PSScriptRoot
}

$checks = New-Object System.Collections.Generic.List[object]

function Add-Check([string]$Name, [string]$Status, [string]$Detail, [string]$Fix = "") {
  $script:checks.Add([pscustomobject]@{
    name = $Name
    status = $Status
    detail = $Detail
    fix = $Fix
  }) | Out-Null
}

function Test-RequiredPath([string]$Name, [string]$Path, [string]$Fix) {
  if (Test-Path -LiteralPath $Path) {
    Add-Check $Name "ok" $Path
  } else {
    Add-Check $Name "fail" "Missing: $Path" $Fix
  }
}

$resolvedSkillDir = $null
try {
  $resolvedSkillDir = (Resolve-Path -LiteralPath $SkillDir).Path
  Add-Check "skill_dir" "ok" $resolvedSkillDir
} catch {
  Add-Check "skill_dir" "fail" "Cannot resolve skill directory: $SkillDir" "Install the repository contents to the Codex skills directory as ai-collab-scorecard."
}

if ($resolvedSkillDir) {
  Test-RequiredPath "SKILL.md" (Join-Path $resolvedSkillDir "SKILL.md") "Reinstall or recopy the full skill folder."
  Test-RequiredPath "references" (Join-Path $resolvedSkillDir "references") "Reinstall or recopy the full skill folder."
  Test-RequiredPath "scripts" (Join-Path $resolvedSkillDir "scripts") "Reinstall or recopy the full skill folder."
  Test-RequiredPath "worktype_assets" (Join-Path $resolvedSkillDir "assets\worktype-illustrations") "Reinstall assets/worktype-illustrations from the repository."
  Test-RequiredPath "font" (Join-Path $resolvedSkillDir "assets\fonts\NotoSansSC-VF.ttf") "Reinstall assets/fonts/NotoSansSC-VF.ttf from the repository."
}

$pythonCommand = $null
foreach ($candidate in @("python", "py")) {
  $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
  if ($cmd) {
    $pythonCommand = $candidate
    break
  }
}

if ($pythonCommand) {
  try {
    $version = & $pythonCommand --version 2>&1
    Add-Check "python" "ok" "${pythonCommand}: $version"
    try {
      $encoding = (& $pythonCommand -c "import locale; print(locale.getencoding())" 2>$null).Trim()
      if ($encoding -match "UTF-?8") {
        Add-Check "python_text_encoding" "ok" "Python default text encoding: $encoding"
      } else {
        Add-Check "python_text_encoding" "warn" "Python default text encoding is $encoding; UTF-8 skill files may fail in validators that do not set encoding." 'Run validation with: $env:PYTHONUTF8="1"; python ...'
      }
    } catch {
      Add-Check "python_text_encoding" "warn" "Could not inspect Python text encoding." 'Run validation with: $env:PYTHONUTF8="1"; python ...'
    }
    try {
      & $pythonCommand -c "import yaml" 2>$null
      Add-Check "pyyaml" "ok" "PyYAML is available for the system skill validator."
    } catch {
      Add-Check "pyyaml" "warn" "PyYAML is missing; runtime scripts still use the Python standard library, but quick_validate.py needs PyYAML." "Ask permission to run: python -m pip install --user PyYAML"
    }
  } catch {
    Add-Check "python" "fail" "Python command exists but cannot run: $pythonCommand" "Repair Python PATH or install Python 3."
  }
} else {
  Add-Check "python" "fail" "No python or py command found." "Install Python 3 or provide a Python runtime path."
}

$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$quickValidate = Join-Path $codexRoot "skills\.system\skill-creator\scripts\quick_validate.py"
if (Test-Path -LiteralPath $quickValidate) {
  Add-Check "quick_validate" "ok" $quickValidate
} else {
  Add-Check "quick_validate" "warn" "System skill validator not found at expected path: $quickValidate" "If unavailable, validate SKILL.md frontmatter manually and continue other checks."
}

try {
  Add-Type -AssemblyName System.Drawing
  Add-Type -AssemblyName System.Windows.Forms
  Add-Check "windows_rendering" "ok" "System.Drawing and System.Windows.Forms are available."
} catch {
  Add-Check "windows_rendering" "fail" "PowerShell/.NET drawing assemblies are unavailable: $($_.Exception.Message)" "Use Windows PowerShell with .NET drawing support, or skip PNG rendering and report the blocker."
}

if ($resolvedSkillDir) {
  $renderLockPath = Join-Path $resolvedSkillDir "references\render-lock.json"
  $fontPath = Join-Path $resolvedSkillDir "assets\fonts\NotoSansSC-VF.ttf"
  if ((Test-Path -LiteralPath $renderLockPath) -and (Test-Path -LiteralPath $fontPath)) {
    try {
      $renderLock = Get-Content -Raw -Encoding UTF8 -LiteralPath $renderLockPath | ConvertFrom-Json
      $expectedFontHash = ([string]$renderLock.font.sha256).ToUpperInvariant()
      $actualFontHash = (Get-FileHash -LiteralPath $fontPath -Algorithm SHA256).Hash.ToUpperInvariant()
      if ($expectedFontHash -eq $actualFontHash) {
        Add-Check "font_hash" "ok" $actualFontHash
      } else {
        Add-Check "font_hash" "fail" "Expected $expectedFontHash, got $actualFontHash" "Restore the bundled pinned font from the repository."
      }
    } catch {
      Add-Check "font_hash" "fail" "Cannot verify font hash: $($_.Exception.Message)" "Restore references/render-lock.json and assets/fonts/NotoSansSC-VF.ttf."
    }
  }

  $manifestPath = Join-Path $resolvedSkillDir "assets\worktype-illustrations\manifest.json"
  if (Test-Path -LiteralPath $manifestPath) {
    try {
      $manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestPath | ConvertFrom-Json
      $assetDir = Join-Path $resolvedSkillDir (($manifest.asset_root -as [string]) -replace "/", "\")
      $types = @($manifest.types.PSObject.Properties)
      $missing = @()
      foreach ($type in $types) {
        $file = [string]$type.Value.file
        if (-not (Test-Path -LiteralPath (Join-Path $assetDir $file))) {
          $missing += $file
        }
      }
      if ($types.Count -eq 10 -and $missing.Count -eq 0 -and [string]$manifest.runtime_generation -eq "disabled") {
        Add-Check "asset_manifest" "ok" "10 types, 10 assets, runtime_generation=disabled"
      } else {
        Add-Check "asset_manifest" "fail" "types=$($types.Count); missing=$($missing -join ','); runtime_generation=$($manifest.runtime_generation)" "Restore assets/worktype-illustrations from the repository."
      }
    } catch {
      Add-Check "asset_manifest" "fail" "Cannot parse asset manifest: $($_.Exception.Message)" "Restore assets/worktype-illustrations/manifest.json from the repository."
    }
  } else {
    Add-Check "asset_manifest" "fail" "Missing manifest: $manifestPath" "Restore assets/worktype-illustrations/manifest.json from the repository."
  }
}

$statuses = @($checks | ForEach-Object { $_.status })
$overall = if ($statuses -contains "fail") {
  "fail"
} elseif ($statuses -contains "warn") {
  "warn"
} else {
  "ok"
}

[pscustomobject]@{
  status = $overall
  skill_dir = $resolvedSkillDir
  checks = $checks
} | ConvertTo-Json -Depth 5
