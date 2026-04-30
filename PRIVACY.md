# Privacy

AI Collab Scorecard is designed to run locally under user control. It does not include telemetry, analytics, or a remote scoring service.

## Data Sources

The skill may use only sources the user explicitly authorizes, such as:

- current visible conversation context
- exported Codex or AI chat transcripts
- user-specified folders or files
- current Codex/software history after explicit read-only permission
- corresponding artifacts, tool logs, commits, or review notes

It must not silently read unrelated private folders, browser profiles, credentials, cookies, hidden app databases, or system caches.

## Local Processing

Scoring and share-card rendering are local workflows. Runtime scorecard generation does not require network access after the skill is installed.

The bootstrap installer may use network access to download this repository or install PyYAML when the user authorizes that setup step.

## Outputs

The serious scorecard may contain sensitive summaries or evidence references from the authorized corpus. The share card should use abstracted patterns and must avoid unnecessary private excerpts.

Before sharing any generated report or image, review it for:

- secrets, tokens, passwords, cookies, or API keys
- personal identifiers not needed for the assessment
- customer, company, or confidential project details
- unrelated private content

## Permission Boundary

If local Codex/software history is requested, the assistant should ask for explicit read-only permission unless the user already granted that scope in the same message. If the source is unavailable, encrypted, proprietary, or mixed with unrelated private data, the assistant should ask for an export or a narrower path instead.
