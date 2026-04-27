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
请安装并运行 AI Collab Scorecard：https://github.com/bagbag16/ai-collab-scorecard。
我授权你在本机完成以下最小必要操作：联网下载或更新仓库，写入本地 Codex skills 目录，运行 skill 自检脚本，必要时安装 PyYAML，必要时用 main.zip 替代 git；并授权你只读访问当前 Codex/当前软件在本机可访问的历史聊天记录作为测评语料。请只读取 Codex 自有或明确属于当前会话历史的记录，不读取浏览器、凭据、无关私人目录或其他软件数据。
安装后如果当前会话还不能通过 $ai-collab-scorecard 触发 skill，请直接读取已安装目录里的 SKILL.md 和 references/setup-and-data-sources.md，并在同一会话继续执行，不要要求我新开窗口。
执行过程使用低打扰模式：只输出必要进度和最终中文结果；不要粘贴安装命令、原始诊断日志、重复检查结果或无关解释。若遇到我未授权或无法自动补齐的外部条件，只列出阻塞项和最小下一步。
```

## Manual Install Without Git

Run this in PowerShell:

```powershell
$Url="https://github.com/bagbag16/ai-collab-scorecard/archive/refs/heads/main.zip"; $Zip=Join-Path $env:TEMP "ai-collab-scorecard.zip"; $Extract=Join-Path $env:TEMP "ai-collab-scorecard-download"; Remove-Item -Recurse -Force $Extract -ErrorAction SilentlyContinue; Invoke-WebRequest $Url -OutFile $Zip; Expand-Archive $Zip -DestinationPath $Extract -Force; $Src=Join-Path $Extract "ai-collab-scorecard-main"; $Root=if($env:CODEX_HOME){$env:CODEX_HOME}else{Join-Path $env:USERPROFILE ".codex"}; $Dst=Join-Path $Root "skills\ai-collab-scorecard"; New-Item -ItemType Directory -Force -Path $Dst | Out-Null; Copy-Item -Recurse -Force -Path (Join-Path $Src "*") -Destination $Dst
```

Then open a new Codex chat and use the post-install prompt above.

## Privacy Boundary

The skill must not silently read local history. If current Codex/software history is needed, it should ask for explicit read-only permission first. If permission is not granted, or the local history is unavailable, unreadable, encrypted, proprietary, or mixed with unrelated private data, use an exported transcript or a user-specified directory instead.

## Completion Behavior

On a new machine, the skill should actively diagnose and repair missing setup before giving up. It includes `scripts/check_environment.ps1` for checking the installed skill folder, Python, PyYAML, PowerShell rendering support, the pinned font, and the 10 fixed worktype images. Missing items should become a concrete permission request or repair step, not an unexplained partial result.

The share card is a playful derivative. The serious scorecard remains the source of truth.
