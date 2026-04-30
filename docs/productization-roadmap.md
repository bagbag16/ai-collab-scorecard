# Productization Roadmap

This file records the GitHub productization work for AI Collab Scorecard. It is repo-facing documentation only and is not installed into the runtime Codex skill.

## Current Product Position

AI Collab Scorecard is best described as an installable Codex skill plus deterministic tooling for evidence-grounded AI collaboration assessment. Its core product promise is:

- read authorized AI collaboration history or exported transcripts
- freeze a repeatable corpus scope
- score five fixed work dimensions with evidence
- derive a fixed worktype from the full score vector
- optionally render a deterministic share-card PNG from the scored JSON

## Completed

- [x] Runtime skill structure: `SKILL.md`, `references/`, `scripts/`, `assets/`, `agents/openai.yaml`
- [x] Bootstrap installer with local, git, and zip acquisition paths
- [x] Environment diagnostics and repair flow for PyYAML
- [x] Deterministic share-card renderer with pinned font and render lock
- [x] Fixed worktype asset manifest
- [x] Installation whitelist so repo-only files are not copied into the skill runtime
- [x] README quick-start prompt for Codex users
- [x] Privacy boundary and non-IQ/non-hiring guardrails in the skill
- [x] Repo-level validator script
- [x] Privacy, security, changelog, contributing, and example artifacts
- [x] GitHub Actions validation workflow

## Remaining Owner Decisions

- [ ] Choose the final license. Current default is all rights reserved.
- [ ] Decide whether this is public open source, public source-available, or private/internal distribution.
- [ ] Decide whether to tag `v0.1.0` after one more colleague-machine install test.
- [ ] Decide whether to compress the PNG assets or keep maximum quality.
- [ ] Decide whether to add GitHub issue templates after the first external feedback cycle.

## Next Product Steps

1. Run one fresh-machine install test from the README quick-start prompt.
2. Capture whether any permission prompt is repetitive or unclear.
3. Verify the final answer contains only one Chinese scorecard plus a concise self-check summary.
4. Tag a first release only after the fresh-machine path succeeds.

## Quality Bar

The repository is ready for team sharing when:

- a new Codex user can install and run with one prompt
- missing dependencies become one consolidated repair request
- no local history is read without explicit permission
- scoring uses `references/rubric.md`, not vague impressions
- the share-card PNG is generated from scored JSON, not a new image model call
- `python scripts/validate_repo.py` passes
- `scripts/self_check_render_determinism.ps1` passes on Windows
