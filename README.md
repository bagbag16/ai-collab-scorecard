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

Send this to Codex to install the skill:

```text
请从 https://github.com/bagbag16/ai-collab-scorecard 安装这个 skill 到本地 Codex skills 目录，skill 名为 ai-collab-scorecard。如果本机没有 git，请下载 main.zip 解压安装；如果缺少网络、写入权限、Python、PowerShell 或其他环境条件，请列出缺失项和需要我授权的最小操作，获得授权后继续补齐，不要因为第一处失败就停止。
```

After installation, start a new Codex chat and send:

```text
使用 $ai-collab-scorecard。请先运行环境诊断、skill 结构校验和分享图确定性渲染自检；如果缺少 git、Python、PyYAML、PowerShell 渲染能力、字体、图片资产、写入权限、网络权限或历史记录权限，不要直接停止或输出半成品，而是列出缺失项、说明需要我授权的最小操作，并在我授权后主动补齐。请先询问我是否授权你只读访问当前 Codex/当前软件在本机可访问的历史聊天记录作为测评语料；在我明确授权前，不要读取本机历史。获得授权后，只读检查 Codex 自有或明确属于当前会话历史的本地记录，冻结可复现的语料范围，并直接输出完整测评结果。除 JSON key、脚本路径、文件名和固定 type_id 外，面向用户的测评结论全部使用中文。若我不授权，或本机历史不可访问、格式不可读取、混有无关私密数据，则改为请求我提供导出语料或指定目录。
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
