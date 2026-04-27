# Setup And Data Sources

Use this file when the user asks how to install the skill, how to run it for another colleague, or how to collect long-term Codex/AI collaboration history.

## Fast Bootstrap For New Users

For a new user, prefer this single-message bootstrap instead of a separate install prompt and a separate usage prompt:

```text
请安装并运行 AI Collab Scorecard：https://github.com/bagbag16/ai-collab-scorecard。优先执行仓库里的 scripts/bootstrap.ps1 自动完成下载、安装、更新、自检和可补齐项；我授权本轮进行必要的联网下载、写入本地 Codex skills、安装 PyYAML、运行自检，并只读访问当前 Codex/当前软件历史作为测评语料。仅限 Codex/当前软件历史，不读浏览器、凭据或无关目录。全程低打扰，最终只输出一份中文完整结果；遇到越界或无法补齐项时只列最小下一步。
```

This message is explicit authorization for the listed scope only. If a required action falls outside that scope, ask once for the missing permission. Platform-level approval dialogs may still appear, but the assistant should not add extra conversational permission loops.

When executing the bootstrap directly from a local checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\bootstrap.ps1"
```

When only the GitHub URL is available, acquire the repository first with `git clone` or `main.zip`, then run `scripts/bootstrap.ps1`. The bootstrap returns JSON with `status`, `installed_to`, self-check summaries, and `continue_in_current_session`. Summarize that JSON for the user; do not paste the raw JSON unless debugging is requested.

## Installation And Validation

Install the skill by placing the folder at one of these locations:

- `%USERPROFILE%\.codex\skills\ai-collab-scorecard`
- The active `$CODEX_HOME\skills\ai-collab-scorecard` directory, when `CODEX_HOME` is set

Manual install handoff, only if bootstrap is unavailable: run the PowerShell install command from the parent directory that contains `ai-collab-scorecard`. If the current session cannot discover `$ai-collab-scorecard` after installation, read the installed `SKILL.md` and continue from disk instead of forcing the user to open a new chat.

```powershell
$Src=(Resolve-Path ".\ai-collab-scorecard").Path; $Root=if($env:CODEX_HOME){$env:CODEX_HOME}else{Join-Path $env:USERPROFILE ".codex"}; $Dst=Join-Path $Root "skills\ai-collab-scorecard"; New-Item -ItemType Directory -Force -Path $Dst | Out-Null; Copy-Item -Recurse -Force -Path (Join-Path $Src "*") -Destination $Dst
```

```text
使用 $ai-collab-scorecard。以低打扰模式运行环境诊断、必要自检和测评；如需读取当前 Codex/当前软件的本机历史，请只在本轮一次性询问只读授权。若缺少可补齐的环境项，请合并列出最小授权请求并继续补齐。最终只输出一份中文完整结果和必要自检摘要，不输出原始日志、重复结果或无关解释。
```

The required runtime files are bundled in the skill:

- `SKILL.md`
- `references/`
- `scripts/`
- `assets/worktype-illustrations/`
- `assets/fonts/NotoSansSC-VF.ttf`

Validate the skill structure with the system skill validator:

```powershell
$env:PYTHONUTF8="1"; python "%USERPROFILE%\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "%USERPROFILE%\.codex\skills\ai-collab-scorecard"
```

Validate deterministic card rendering after any renderer, layout, font, or image-asset change:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\self_check_render_determinism.ps1"
```

Runtime scorecard generation does not require network access. Runtime image generation is disabled.

## Completion Recovery Protocol

Use this protocol whenever a colleague's machine does not produce the full expected result because of missing tools, different local configuration, unavailable history, blocked network, or incomplete assets.

Do not stop at the first failure. The expected behavior is: diagnose, request the minimum permission needed, repair or route around the gap, then continue until a complete scorecard is produced or a concrete external blocker remains.

Default to low-friction output: summarize diagnostics instead of pasting raw JSON, request missing permissions in one consolidated message, and continue after authorization without restarting the conversation.

1. Run the environment diagnostic:

Prefer the integrated bootstrap for install/update/self-check:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\bootstrap.ps1"
```

For diagnostics only, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\check_environment.ps1"
```

2. Classify each diagnostic result:
   - `ok`: proceed.
   - `warn`: continue when non-blocking, but mention the reduced check.
   - `fail`: request the smallest permission or input needed to fix it.

3. Repair in this order:
   - Skill folder placement: install to `%USERPROFILE%\.codex\skills\ai-collab-scorecard` or active `$CODEX_HOME\skills\ai-collab-scorecard`.
   - Repository acquisition: use `git clone` when `git` exists; otherwise download `main.zip`.
   - Python runtime: locate `python` or `py`; if absent, ask the user to install Python 3 or provide a runtime path.
   - Validator dependency: if `PyYAML` is missing and validation is required, ask permission to run `python -m pip install --user PyYAML`.
   - Validator encoding: on non-UTF-8 Windows consoles, run the validator with `$env:PYTHONUTF8="1"` so UTF-8 Chinese instructions are read correctly.
   - Rendering stack: run PowerShell scripts with `-ExecutionPolicy Bypass`; if Windows drawing assemblies are unavailable, report that deterministic PNG rendering is blocked and still complete the serious scorecard.
   - Bundled assets: verify `assets/worktype-illustrations/manifest.json`, 10 confirmed PNG assets, `assets/fonts/NotoSansSC-VF.ttf`, and `references/render-lock.json`; recopy from the repository if missing.
   - Corpus access: ask explicit read-only permission before inspecting current Codex/software history; if denied or unavailable, ask for an export/path and continue.

4. After any repair, rerun the failed check rather than assuming the repair worked.

5. The final response must include:
   - 完成状态：`完整`、`完整但有警告`、或 `阻塞`
   - 已运行检查
   - 已执行或已请求授权的修复
   - 剩余阻塞项，如有
   - 证据足够时的完整评分卡

Only downgrade to a partial result after repair attempts are blocked by missing user permission, unavailable local data, missing external tools the user declines to install, or platform limitations that cannot be fixed from the current session.

## Data Source Boundary

The skill scores observable AI collaboration behavior. It can use history only when the user has authorized the source and the source is relevant to AI-assisted work.

Allowed source classes:

| Source | Examples | Use |
|---|---|---|
| Raw AI/Codex sessions | exported `.jsonl`, `.json`, `.md`, `.txt`, current thread transcript | strongest evidence for prompts, corrections, constraints, and review behavior |
| Tool traces | terminal logs, patch records, test output, diffs, command summaries | evidence for verification and delivery behavior |
| Produced artifacts | code, docs, decks, reports, images, configs | evidence for delivery only when steering history is visible |
| Repo history | commits, PR descriptions, review comments, change logs | evidence for iteration and adoption |
| External collaboration logs | Feishu/Slack/email excerpts, only when explicitly provided | supplementary context, not primary scoring unless raw AI interaction is visible |

Do not silently scrape hidden app databases, unrelated private folders, browser profiles, credentials, or system caches. If the user wants to use "current Codex/software history", first ask for explicit permission to inspect that local history read-only unless permission was already granted in the same turn. After permission is granted, treat it as a source declaration: inspect only Codex-owned or clearly session-related history locations read-only, then freeze a manifest. Ask for an export/path when permission is not granted, no accessible Codex history can be found, or the visible storage is proprietary, encrypted, or mixed with unrelated private data.

## Codex History Acquisition

Use this order:

1. Current visible thread: use the conversation context and files created in the workspace.
2. Current Codex/software history: ask for and receive explicit read-only local-history permission first; then inspect only Codex-owned or clearly session-related local history locations.
3. User-provided export: prefer exported Codex conversations, session transcripts, or copied logs.
4. User-provided directory: scan only the declared folder or files.
5. Known local history directory: inspect read-only only after the user has explicitly asked for all local Codex history or named the location.
6. If the storage format is encrypted, proprietary, unavailable, or mixed with unrelated private data, stop and ask the user to export the relevant conversations.

For repeatability, never score from an implicit moving target. First freeze a corpus manifest.

## Corpus Manifest Builder

Use `scripts/build_corpus_manifest.py` to create a repeatable source list from explicit files or directories:

```powershell
python "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\build_corpus_manifest.py" `
  --subject-id "colleague-name-or-alias" `
  --source "C:\path\to\codex-history-export" `
  --source "C:\path\to\workspace-artifacts" `
  --start "2026-01-01" `
  --end "2026-04-27" `
  --out "C:\path\to\manifest.json"
```

The manifest records paths, kinds, sizes, hashes, modified times, inclusions, and exclusions. If the manifest changes, treat the scorecard as a new assessment version.

After building a manifest, use `scripts/extract_collab_signals.py` to create a compact evidence map from Codex `.jsonl` history:

```powershell
python "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\extract_collab_signals.py" `
  --manifest "C:\path\to\manifest.json" `
  --out "C:\path\to\signals.json"
```

The signal report is not the final score. It is a repeatable evidence map used with `references/rubric.md`.

## Input Normalization

Before scoring, normalize raw records into task episodes:

```json
{
  "episode_id": "stable-id",
  "source_id": "manifest source id",
  "time_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "task_goal": "what the user was trying to do",
  "user_actions": ["prompts, corrections, constraints, decisions"],
  "ai_actions": ["outputs, plans, code, summaries"],
  "tool_actions": ["tests, commands, patches, render checks"],
  "artifacts": ["final files or outputs"],
  "outcome": "accepted|revised|abandoned|unknown"
}
```

If exact normalization is not possible, keep raw excerpts with source references and lower confidence.

## Privacy And Redaction

Redact secrets before producing a report or share card:

- API keys, tokens, passwords, cookies
- personal identifiers not needed for assessment
- customer or internal confidential details
- unrelated personal content

The public/shareable card must use abstracted patterns only. The serious scorecard may cite evidence, but should avoid unnecessary private excerpts.

## Minimum Reusable Package For A Colleague

To assess another colleague consistently, collect:

- Corpus manifest JSON
- Raw session/export folder or selected transcript files
- Role/domain context
- Time window
- Any final artifacts that correspond to the sessions
- Optional prior scorecard for comparison, never as a scoring anchor

Then run the same workflow: freeze manifest, extract evidence, score five dimensions, classify worktype, optionally render the card.
