# Sampling Protocol

Use this protocol to make repeat assessments of one person converge.

## Source Priority

Prefer raw collaboration records over polished outputs:

1. Raw AI chat/Codex session logs
2. User prompts, corrections, and explicit constraints
3. Tool calls, tests, diffs, commits, or generated artifacts
4. Final documents or code
5. Self-description or third-party description

Final artifacts alone are insufficient for high confidence because they may hide the user's steering and the AI's contribution.

## Minimum Sample Levels

| Level | Minimum Corpus | Allowed Output |
|---|---|---|
| Thin | 1-2 tasks or final artifacts only | Qualitative notes; no fair worktype unless obvious |
| Basic | 3-5 tasks with prompts and outputs | Scorecard with low/medium confidence |
| Standard | 8-15 tasks across at least 2 task types | Scorecard + worktype with medium/high confidence |
| Full history | All accessible records in a defined window | Scorecard + worktype + share card allowed |

## Corpus Manifest

For repeatable scoring, freeze a manifest before scoring. Prefer `scripts/build_corpus_manifest.py` for user-authorized files and folders, then add any manual notes that the script cannot infer. Record:

```json
{
  "subject_id": "person-or-alias",
  "time_window": {
    "start": "YYYY-MM-DD",
    "end": "YYYY-MM-DD"
  },
  "sources": [
    {
      "path_or_id": "source identifier",
      "kind": "codex-session|chat-log|artifact|repo|other",
      "size_bytes": 0,
      "sha256": "optional stable file hash",
      "included": true,
      "reason": "why this source is in scope"
    }
  ],
  "exclusions": [
    {
      "path_or_id": "source identifier",
      "reason": "duplicate|system-noise|secret|not-collaboration|unreadable"
    }
  ]
}
```

If the manifest changes, treat the result as a new assessment version.

Use `references/setup-and-data-sources.md` when deciding where history may be collected from and what requires explicit user authorization.

## Extraction Rules

Extract only assessment-relevant signals:

- User problem statements
- Constraint-setting and non-goals
- User corrections of AI assumptions
- Requests for verification, tests, sources, or reviews
- Tool use and validation traces
- Final artifacts and whether they were adopted or iterated
- Repeated failure modes

Exclude or downweight:

- System/developer instructions not authored by the subject
- Tool boilerplate
- Duplicate auto-review sessions
- Purely personal or sensitive content unrelated to AI collaboration ability
- Final outputs where user steering is invisible

## Evidence Quotas

For each scored dimension, try to collect:

- At least `3` evidence bullets
- At least `2` different tasks or sessions
- At least `1` user-authored correction, constraint, or validation trace

If a dimension lacks these quotas, lower confidence even if the score seems high.

## Repeat Assessment Rule

When re-scoring the same frozen manifest:

- Reuse the same sample scope.
- Reuse the same role/domain expectation.
- Score with the same five dimensions and weights.
- Use the repeatability worksheet in `rubric.md`.
- Preserve old scores only as comparison, not as anchors.

If a repeated run differs by more than `5` points on any dimension or more than `3` points composite, inspect the evidence basis and explain the divergence before finalizing.
