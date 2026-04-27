# AI Collab Scorecard

AI Collab Scorecard is a Codex skill for evaluating long-term AI/Codex collaboration records. It turns chat history, prompts, corrections, tool traces, and produced artifacts into an evidence-grounded scorecard.

It is designed for work review, coaching, and collaboration pattern analysis. It is not an IQ test, personality diagnosis, hiring decision tool, or clinical assessment.

## What It Outputs

- 五个单维度整数分值，满分 100
- 综合整数分值，满分 100
- 证据置信度
- AI 协作工作型与匹配度
- 第二倾向与风险修正
- 各维度证据
- 能力画像、主要瓶颈与改进建议
- 可选的确定性分享图 PNG

## Quick Start For Codex

Send this single message to Codex:

```text
请安装并运行 AI Collab Scorecard：https://github.com/bagbag16/ai-collab-scorecard。优先执行仓库里的 scripts/bootstrap.ps1 自动完成下载、安装、更新、自检和可补齐项；我授权本轮进行必要的联网下载、写入本地 Codex skills、安装 PyYAML、运行自检，并只读访问当前 Codex/当前软件历史作为测评语料。仅限 Codex/当前软件历史，不读浏览器、凭据或无关目录。全程低打扰，最终只输出一份中文完整结果；遇到越界或无法补齐项时只列最小下一步。
```

For Codex, this is the preferred path. It should use `scripts/bootstrap.ps1` and continue in the same chat after installation.

## Manual Install Without Git

Run this in PowerShell only when you are installing manually without Codex:

```powershell
$Url="https://github.com/bagbag16/ai-collab-scorecard/archive/refs/heads/main.zip"; $Zip=Join-Path $env:TEMP "ai-collab-scorecard.zip"; $Extract=Join-Path $env:TEMP "ai-collab-scorecard-download"; Remove-Item -Recurse -Force $Extract -ErrorAction SilentlyContinue; Invoke-WebRequest $Url -OutFile $Zip; Expand-Archive $Zip -DestinationPath $Extract -Force; $Src=Join-Path $Extract "ai-collab-scorecard-main"; $Root=if($env:CODEX_HOME){$env:CODEX_HOME}else{Join-Path $env:USERPROFILE ".codex"}; $Dst=Join-Path $Root "skills\ai-collab-scorecard"; New-Item -ItemType Directory -Force -Path $Dst | Out-Null; Copy-Item -Recurse -Force -Path (Join-Path $Src "*") -Destination $Dst
```

Then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\bootstrap.ps1"
```

## Privacy Boundary

The skill must not silently read local history. If current Codex/software history is needed, it should ask for explicit read-only permission first. If permission is not granted, or the local history is unavailable, unreadable, encrypted, proprietary, or mixed with unrelated private data, use an exported transcript or a user-specified directory instead.

## Completion Behavior

On a new machine, the skill should actively diagnose and repair missing setup before giving up. It includes `scripts/check_environment.ps1` for checking the installed skill folder, Python, PyYAML, PowerShell rendering support, the pinned font, and the 10 fixed worktype images. Missing items should become a concrete permission request or repair step, not an unexplained partial result.

The share card is a playful derivative. The serious scorecard remains the source of truth.
