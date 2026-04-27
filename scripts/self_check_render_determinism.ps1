param(
  [string]$SkillDir = "",
  [string]$InputJson = "",
  [string]$WorkDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $SkillDir) {
  $SkillDir = Split-Path -Parent $PSScriptRoot
}
$SkillDir = (Resolve-Path -LiteralPath $SkillDir).Path

$lockPath = Join-Path $SkillDir "references\render-lock.json"
$renderer = Join-Path $SkillDir "scripts\render_share_card_png.ps1"
$lock = Get-Content -Raw -Encoding UTF8 -LiteralPath $lockPath | ConvertFrom-Json

if (-not $InputJson) {
  $InputJson = Join-Path $SkillDir ($lock.validation.reference_fixture.input -replace "/", "\")
}
if (-not $WorkDir) {
  $WorkDir = Join-Path $env:TEMP "score-ai-collab-render-selfcheck"
}
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

$fontPath = Join-Path $SkillDir ($lock.font.path -replace "/", "\")
$fontHash = (Get-FileHash -LiteralPath $fontPath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($fontHash -ne $lock.font.sha256.ToUpperInvariant()) {
  throw "Pinned font hash mismatch. Expected $($lock.font.sha256), got $fontHash"
}

$out1 = Join-Path $WorkDir "render-selfcheck-1.png"
$out2 = Join-Path $WorkDir "render-selfcheck-2.png"

powershell -NoProfile -ExecutionPolicy Bypass -File $renderer -InputJson $InputJson -Out $out1 | Out-Null
powershell -NoProfile -ExecutionPolicy Bypass -File $renderer -InputJson $InputJson -Out $out2 | Out-Null

$hash1 = (Get-FileHash -LiteralPath $out1 -Algorithm SHA256).Hash.ToUpperInvariant()
$hash2 = (Get-FileHash -LiteralPath $out2 -Algorithm SHA256).Hash.ToUpperInvariant()
if ($hash1 -ne $hash2) {
  throw "Repeat render hash mismatch: $hash1 vs $hash2"
}

$expected = [string]$lock.validation.reference_fixture.output_sha256
if ($expected -and $hash1 -ne $expected.ToUpperInvariant()) {
  throw "Reference fixture hash mismatch. Expected $expected, got $hash1"
}

Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile($out1)
try {
  if ($img.Width -ne [int]$lock.canonical_output.width -or $img.Height -ne [int]$lock.canonical_output.height) {
    throw "Image size mismatch: $($img.Width)x$($img.Height)"
  }
} finally {
  $img.Dispose()
}

[PSCustomObject]@{
  status = "ok"
  input = $InputJson
  output1 = $out1
  output2 = $out2
  png_sha256 = $hash1
  font_sha256 = $fontHash
  size = "$($lock.canonical_output.width)x$($lock.canonical_output.height)"
} | ConvertTo-Json -Depth 3
