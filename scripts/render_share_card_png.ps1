param(
  [Parameter(Mandatory = $true)]
  [string]$InputJson,

  [Parameter(Mandatory = $true)]
  [string]$Out,

  [string]$AssetManifest = "",
  [string]$ShareCopy = "",
  [string]$FontPath = "",
  [string]$RenderLock = ""
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

$SkillDir = Split-Path -Parent $PSScriptRoot
if (-not $AssetManifest) {
  $AssetManifest = Join-Path $SkillDir "assets\worktype-illustrations\manifest.json"
}
if (-not $ShareCopy) {
  $ShareCopy = Join-Path $SkillDir "references\share-copy.json"
}
if (-not $RenderLock) {
  $RenderLock = Join-Path $SkillDir "references\render-lock.json"
}
if (-not (Test-Path -LiteralPath $RenderLock)) {
  throw "Render lock not found: $RenderLock"
}
$renderLockData = Get-Content -Raw -Encoding UTF8 -LiteralPath $RenderLock | ConvertFrom-Json
if (-not $FontPath) {
  $fontRelPath = [string]$renderLockData.font.path
  $FontPath = Join-Path $SkillDir ($fontRelPath -replace "/", "\")
}

$ExpectedFontSha256 = ([string]$renderLockData.font.sha256).ToUpperInvariant()
if (-not (Test-Path -LiteralPath $FontPath)) {
  throw "Pinned font not found: $FontPath"
}
$actualFontSha256 = (Get-FileHash -LiteralPath $FontPath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualFontSha256 -ne $ExpectedFontSha256) {
  throw "Pinned font hash mismatch: $FontPath. Expected $ExpectedFontSha256, got $actualFontSha256"
}
$script:FontCollection = New-Object System.Drawing.Text.PrivateFontCollection
$script:FontCollection.AddFontFile($FontPath)
$script:CardFontFamily = $script:FontCollection.Families[0]
$script:CanvasWidth = [int]$renderLockData.canonical_output.width
$script:CanvasHeight = [int]$renderLockData.canonical_output.height
$script:CanvasDpi = [int]$renderLockData.canonical_output.dpi

function S([string]$Base64) {
  return [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Base64))
}

function Get-Prop($Object, [string]$Name, $Default = $null) {
  if ($null -eq $Object) { return $Default }
  $prop = $Object.PSObject.Properties[$Name]
  if ($null -eq $prop) { return $Default }
  if ($null -eq $prop.Value -or $prop.Value -eq "") { return $Default }
  return $prop.Value
}

function Coalesce($Values) {
  foreach ($value in $Values) {
    if ($null -ne $value -and [string]$value -ne "") { return $value }
  }
  return ""
}

function Clamp-Score($Value) {
  try { $score = [int]$Value } catch { $score = 0 }
  return [Math]::Max(0, [Math]::Min(100, $score))
}

function Limit-Text([string]$Text, [int]$MaxChars) {
  $normalized = (($Text -as [string]) -replace "\s+", " ").Trim()
  if ($MaxChars -le 0 -or $normalized.Length -le $MaxChars) { return $normalized }
  if ($MaxChars -le 1) { return [string][char]0x2026 }
  return $normalized.Substring(0, $MaxChars - 1).TrimEnd() + [string][char]0x2026
}

function Get-Score($Data, [string]$Key) {
  $scores = Get-Prop $Data "scores"
  $item = Get-Prop $scores $Key
  return Clamp-Score (Get-Prop $item "score" 0)
}

function New-RoundRectPath([float]$X, [float]$Y, [float]$W, [float]$H, [float]$R) {
  $path = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $R * 2
  $path.AddArc($X, $Y, $d, $d, 180, 90)
  $path.AddArc($X + $W - $d, $Y, $d, $d, 270, 90)
  $path.AddArc($X + $W - $d, $Y + $H - $d, $d, $d, 0, 90)
  $path.AddArc($X, $Y + $H - $d, $d, $d, 90, 90)
  $path.CloseFigure()
  return $path
}

function Draw-RoundedFill($G, [float]$X, [float]$Y, [float]$W, [float]$H, [float]$R, $Brush) {
  $path = New-RoundRectPath $X $Y $W $H $R
  $G.FillPath($Brush, $path)
  $path.Dispose()
}

function Draw-CoverImage($G, $Image, [float]$X, [float]$Y, [float]$W, [float]$H, [float]$Opacity) {
  $scale = [Math]::Max($W / $Image.Width, $H / $Image.Height)
  $sw = $W / $scale
  $sh = $H / $scale
  $sx = ($Image.Width - $sw) / 2
  $sy = ($Image.Height - $sh) / 2

  $cm = New-Object System.Drawing.Imaging.ColorMatrix
  $cm.Matrix33 = $Opacity
  $ia = New-Object System.Drawing.Imaging.ImageAttributes
  $ia.SetColorMatrix($cm, [System.Drawing.Imaging.ColorMatrixFlag]::Default, [System.Drawing.Imaging.ColorAdjustType]::Bitmap)
  $dest = New-Object System.Drawing.RectangleF($X, $Y, $W, $H)
  $G.DrawImage($Image, [System.Drawing.Rectangle]::Round($dest), [int]$sx, [int]$sy, [int]$sw, [int]$sh, [System.Drawing.GraphicsUnit]::Pixel, $ia)
  $ia.Dispose()
}

function Draw-Text($G, [string]$Text, [float]$X, [float]$Y, [float]$Size, [bool]$Bold, [string]$Color) {
  $style = if ($Bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
  $font = New-Object System.Drawing.Font($script:CardFontFamily, $Size, $style, [System.Drawing.GraphicsUnit]::Pixel)
  $brush = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($Color))
  $G.DrawString($Text, $font, $brush, $X, $Y)
  $font.Dispose()
  $brush.Dispose()
}

function Draw-Bar($G, [string]$Label, [int]$Score, [float]$X, [float]$Y, [float]$W, [string]$Accent) {
  Draw-Text $G $Label $X ($Y - 9) 25 $true "#344054"
  $track = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml("#EAECF0"))
  $fill = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($Accent))
  Draw-RoundedFill $G ($X + 128) $Y $W 20 10 $track
  Draw-RoundedFill $G ($X + 128) $Y ([Math]::Round($W * $Score / 100)) 20 10 $fill
  Draw-Text $G ([string]$Score) ($X + 128 + $W + 16) ($Y - 10) 27 $true "#101828"
  $track.Dispose()
  $fill.Dispose()
}

function Draw-ScoreBox($G, [string]$Label, [int]$Score, [float]$X, [float]$Y, [string]$Dark) {
  $scoreBg = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml("#F8FAFC"))
  Draw-RoundedFill $G $X $Y 146 132 22 $scoreBg
  Draw-Text $G $Label ($X + 22) ($Y + 25) 25 $true "#667085"
  $denominatorOffset = if ($Score -ge 100) { 100 } else { 88 }
  Draw-Text $G ([string]$Score) ($X + 16) ($Y + 62) 54 $true $Dark
  Draw-Text $G "/100" ($X + $denominatorOffset) ($Y + 92) 22 $true "#667085"
  $scoreBg.Dispose()
}

$data = Get-Content -Raw -Encoding UTF8 -LiteralPath $InputJson | ConvertFrom-Json
$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $AssetManifest | ConvertFrom-Json
$copybook = Get-Content -Raw -Encoding UTF8 -LiteralPath $ShareCopy | ConvertFrom-Json

$worktype = Get-Prop $data "worktype"
$share = Get-Prop $data "share_card"
$typeId = [string](Get-Prop $worktype "type_id" "ai-systems-architect")
$manifestTypes = Get-Prop $manifest "types"
$entry = Get-Prop $manifestTypes $typeId
if ($null -eq $entry -or (Get-Prop $entry "status" "") -ne "confirmed") {
  throw "No confirmed asset for type_id: $typeId"
}

$assetRoot = [string](Get-Prop $manifest "asset_root" "assets/worktype-illustrations")
$assetFile = [string](Get-Prop $entry "file" "")
if (-not $assetFile) { throw "Manifest entry has no file for type_id: $typeId" }
$assetPath = Join-Path (Join-Path $SkillDir $assetRoot) $assetFile
if (-not (Test-Path -LiteralPath $assetPath)) { throw "Asset not found: $assetPath" }

$typeNames = Get-Prop (Get-Prop $copybook "type_names") $typeId
$typeCopy = Get-Prop (Get-Prop $copybook "type_copy") $typeId
$seriousName = [string](Coalesce @(
  (Get-Prop $worktype "serious_name_zh"),
  (Get-Prop $typeNames "serious_name_zh"),
  (Get-Prop $worktype "serious_name"),
  $typeId
))
$shareName = [string](Coalesce @(
  (Get-Prop $worktype "share_name_zh"),
  (Get-Prop $typeNames "share_name_zh"),
  (Get-Prop $worktype "share_name"),
  $typeId
))
$superpower = Limit-Text ([string](Coalesce @(
  (Get-Prop $share "superpower_zh"),
  (Get-Prop $share "superpower"),
  (Get-Prop $typeCopy "superpower"),
  ""
))) 20
$weakness = Limit-Text ([string](Coalesce @(
  (Get-Prop $share "comedy_failure_mode_zh"),
  (Get-Prop $share "comedy_failure_mode"),
  (Get-Prop $typeCopy "comedy_failure_mode"),
  ""
))) 20

$accentByType = @{
  "ai-systems-architect" = "#3B82F6"
  "prompt-air-traffic-controller" = "#06B6D4"
  "evidence-auditor" = "#F59E0B"
  "problem-architect" = "#8B5CF6"
  "system-modeler" = "#0EA5E9"
  "delivery-integrator" = "#EF4444"
  "fast-ai-delegator" = "#F97316"
  "abstract-explorer" = "#7C3AED"
  "execution-accelerator" = "#22C55E"
  "ai-dependent-operator" = "#64748B"
}
$accent = if ($accentByType.ContainsKey($typeId)) { $accentByType[$typeId] } else { "#3B82F6" }
$dark = "#101828"

$composite = Clamp-Score (Get-Prop (Get-Prop $data "composite") "score" 0)
$fit = Clamp-Score (Get-Prop $worktype "fit_score" 0)
$dimRows = @(
  @{ key = "problem_framing"; label = (S "6Zeu6aKY55WM5a6a") },
  @{ key = "reasoning_modeling"; label = (S "5o6o55CG5bu65qih") },
  @{ key = "evidence_verification"; label = (S "6K+B5o2u6aqM6K+B") },
  @{ key = "ai_orchestration"; label = (S "QUkg57yW5o6S") },
  @{ key = "delivery_iteration"; label = (S "5Lqk5LuY6L+t5Luj") }
)

$outDir = Split-Path -Parent $Out
if ($outDir) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }

$bmp = New-Object System.Drawing.Bitmap($script:CanvasWidth, $script:CanvasHeight)
$bmp.SetResolution($script:CanvasDpi, $script:CanvasDpi)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.Clear([System.Drawing.ColorTranslator]::FromHtml("#F8FAFC"))

$asset = [System.Drawing.Image]::FromFile($assetPath)
$cardPath = New-RoundRectPath 42 42 996 1266 44
$oldClip = $g.Clip.Clone()
$g.SetClip($cardPath)

Draw-CoverImage $g $asset 42 42 996 1266 0.16
$veil = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245, 255, 255, 255))
$g.FillRectangle($veil, 42, 705, 996, 603)
Draw-CoverImage $g $asset 42 42 996 666 1.0
$fade = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
  (New-Object System.Drawing.RectangleF(42, 560, 996, 148)),
  [System.Drawing.Color]::FromArgb(0, 255, 255, 255),
  [System.Drawing.Color]::FromArgb(237, 255, 255, 255),
  [System.Drawing.Drawing2D.LinearGradientMode]::Vertical
)
$g.FillRectangle($fade, 42, 560, 996, 148)
$g.Clip = $oldClip

$panel = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(237, 255, 255, 255))
Draw-RoundedFill $g 66 728 548 552 28 $panel
Draw-RoundedFill $g 650 728 364 552 28 $panel

Draw-Text $g (S "5L2g55qEQUnljY/kvZzlnovkurrmoLzmmK8=") 106 774 31 $true $accent
Draw-Text $g $shareName 106 824 66 $true $dark
Draw-Text $g ((S "5Lil6IKD57G75Z6L77ya") + $seriousName) 108 907 34 $true "#475467"
Draw-Text $g (S "6auY5YWJ6IO95Yqb") 106 994 28 $true $accent
Draw-Text $g $superpower 106 1038 35 $true "#101828"
Draw-Text $g (S "5byx6aG55o+Q6YaS") 106 1127 28 $true $accent
Draw-Text $g $weakness 106 1171 35 $true "#344054"
Draw-Text $g (S "5Z+65LqO6K+B5o2u55qEQUnljY/kvZzmkZjopoHvvIzkuI3mmK9JUeOAgeS6uuagvOiviuaWreaIlueUqOS6uuW7uuiuruOAgg==") 106 1244 17 $false "#98A2B3"

Draw-ScoreBox $g (S "57u85ZCI5YiG") $composite 672 768 $dark
Draw-ScoreBox $g (S "5Yy56YWN5bqm") $fit 836 768 $dark
Draw-Text $g (S "5LqU57u05YiG5YC8") 672 930 35 $true "#344054"

$barY = 990
for ($i = 0; $i -lt $dimRows.Count; $i++) {
  $row = $dimRows[$i]
  Draw-Bar $g $row.label (Get-Score $data $row.key) 672 ($barY + $i * 56) 178 $accent
}

$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)

$oldClip.Dispose()
$cardPath.Dispose()
$asset.Dispose()
$veil.Dispose()
$fade.Dispose()
$panel.Dispose()
$g.Dispose()
$bmp.Dispose()
$script:FontCollection.Dispose()

Write-Output $Out
