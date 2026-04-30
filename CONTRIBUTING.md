# Contributing

This repository is still in early productization. Keep changes small, evidence-based, and testable.

## Development Checks

Run:

```powershell
python scripts/validate_repo.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\self_check_render_determinism.ps1
```

For Python script changes, also run:

```powershell
python -m py_compile scripts\*.py
```

## Skill Design Rules

- Keep `SKILL.md` concise and route details to `references/`.
- Do not add repo-facing docs to the installed runtime skill package.
- Do not invent new canonical worktype names without updating `references/worktypes.md`, `references/share-copy.json`, and the asset manifest together.
- Do not call image generation during runtime scoring or card rendering.
- Keep score fields as integers from `0` to `100`.
- Keep privacy boundaries explicit and conservative.

## Asset Changes

After changing renderer, font, layout, or worktype images, run the deterministic render self-check and update `references/render-lock.json` only when the visual change is intentional.
