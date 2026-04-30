# Security

## Supported Version

The repository currently tracks the `main` branch only. Use tagged releases once they are introduced.

## Reporting

For now, report security or privacy issues through the repository owner or a private channel. Do not include secrets, private transcripts, customer data, or full local paths unless they are necessary and redacted.

## Local Execution Model

This project is a Codex skill with local scripts. Review scripts before running them on sensitive machines.

Expected local behaviors:

- `scripts/bootstrap.ps1` may write to the active Codex skills directory.
- `scripts/bootstrap.ps1` may download the repository or install PyYAML when authorized.
- `scripts/check_environment.ps1` checks local runtime readiness.
- `scripts/render_share_card_png.ps1` reads bundled assets and writes a PNG.
- Corpus acquisition should be read-only and limited to user-authorized sources.

Unexpected behaviors to treat as security bugs:

- reading browser profiles, credentials, cookies, or unrelated private folders
- uploading private corpus data
- generating share cards by sending private content to an image service at runtime
- modifying user projects outside the explicit output path
- installing dependencies without clear user authorization

## Secrets

Do not commit real transcripts, API keys, credentials, browser exports, cookies, or company-confidential corpora. Use privacy-safe examples in `examples/`.
