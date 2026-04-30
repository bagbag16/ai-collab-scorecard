# Examples

This directory contains privacy-safe sample artifacts for product preview and validation.

- `sample-scorecard.json`: a minimal scored output that follows `references/output-schema.md` closely enough to render a share card.
- `sample-share-card.png`: deterministic PNG rendered from `sample-scorecard.json`.

These examples are synthetic. They are not based on private user history.

Regenerate the image on Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ..\scripts\render_share_card_png.ps1 -InputJson .\sample-scorecard.json -Out .\sample-share-card.png
```
