# Setup And Data Sources

Use this file when the user asks how to install the skill, how to run it for another colleague, or how to collect long-term Codex/AI collaboration history.

## Installation And Validation

Install the skill by placing the folder at one of these locations:

- `%USERPROFILE%\.codex\skills\ai-collab-scorecard`
- The active `$CODEX_HOME\skills\ai-collab-scorecard` directory, when `CODEX_HOME` is set

One-line install-and-use handoff: run the PowerShell install command from the parent directory that contains `ai-collab-scorecard`, then open a new Codex chat and send the smoke-test prompt to verify the installed skill.

```powershell
$Src=(Resolve-Path ".\ai-collab-scorecard").Path; $Root=if($env:CODEX_HOME){$env:CODEX_HOME}else{Join-Path $env:USERPROFILE ".codex"}; $Dst=Join-Path $Root "skills\ai-collab-scorecard"; New-Item -ItemType Directory -Force -Path $Dst | Out-Null; Copy-Item -Recurse -Force -Path (Join-Path $Src "*") -Destination $Dst
```

```text
Use $ai-collab-scorecard. Run the installed skill validation and deterministic share-card render self-check, then report whether the skill is ready to assess an explicitly provided AI collaboration corpus.
```

The required runtime files are bundled in the skill:

- `SKILL.md`
- `references/`
- `scripts/`
- `assets/worktype-illustrations/`
- `assets/fonts/NotoSansSC-VF.ttf`

Validate the skill structure with the system skill validator:

```powershell
python "%USERPROFILE%\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "%USERPROFILE%\.codex\skills\ai-collab-scorecard"
```

Validate deterministic card rendering after any renderer, layout, font, or image-asset change:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\self_check_render_determinism.ps1"
```

Runtime scorecard generation does not require network access. Runtime image generation is disabled.

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

Do not silently scrape hidden app databases, unrelated private folders, browser profiles, credentials, or system caches. If the user asks for "all Codex history" and no source path or export is available, ask for the export/path or inspect only clearly named, user-authorized Codex history locations.

## Codex History Acquisition

Use this order:

1. Current visible thread: use the conversation context and files created in the workspace.
2. User-provided export: prefer exported Codex conversations, session transcripts, or copied logs.
3. User-provided directory: scan only the declared folder or files.
4. Known local history directory: inspect read-only only after the user has explicitly asked for all local Codex history or named the location.
5. If the storage format is encrypted, proprietary, unavailable, or mixed with unrelated private data, stop and ask the user to export the relevant conversations.

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
