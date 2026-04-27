# Evidence Abstraction Pipeline

Use this file to convert raw AI/Codex collaboration history into the five score dimensions and the final worktype.

## Pipeline Overview

1. Freeze the corpus manifest from `sampling-protocol.md`.
2. Segment raw history into task episodes.
3. Separate author roles: user, AI, tool, system/developer, third party.
4. Extract evidence events.
5. Map evidence events to the five dimensions.
6. Score each dimension with `rubric.md`.
7. Compute the composite score.
8. Run deterministic worktype matching with `worktypes.md` or `scripts/classify_worktype.py`.
9. Produce the serious scorecard first; generate share-card output only as a derivative.

For Codex `.jsonl` history, run `scripts/extract_collab_signals.py` after building the corpus manifest. Treat the output as structured evidence candidates, not as an automatic score.

## Episode Segmentation

Split history by real work unit, not by chat window when possible.

One episode should have:

- A user goal or problem
- The AI outputs used in the work
- User steering, acceptance, rejection, or correction
- Any tool/test/diff/artifact evidence
- An outcome: accepted, revised, abandoned, or unknown

Merge adjacent chats when they continue the same task. Split one long chat when it contains unrelated tasks.

## Author Separation

Score the user's observable behavior, not the AI's raw output quality.

| Content | Treatment |
|---|---|
| User-authored prompts, corrections, constraints, decisions | primary evidence |
| AI-generated plans, code, prose, or images | evidence only when user steering/review is visible |
| Tool output, tests, diffs, command results | verification and delivery evidence |
| System/developer instructions | context only; do not score as the user's capability |
| Final artifacts without steering trace | weak delivery evidence; low confidence for reasoning or orchestration |

## Evidence Event Types

Tag each useful excerpt or artifact trace with one or more event types:

| Event Type | Description | Main Dimension |
|---|---|---|
| `problem_frame` | defines goal, boundary, non-goal, role context, success criteria | Problem Framing and Constraint Control |
| `scope_correction` | catches wrong layer, drift, hidden assumption, or over-broad solution | Problem Framing and Constraint Control |
| `model_build` | creates mechanism, taxonomy, causal structure, abstraction, or reusable rule | Reasoning and Model Building |
| `tradeoff_reasoning` | compares alternatives and explains why one path fits | Reasoning and Model Building |
| `evidence_request` | asks for sources, proof, citations, tests, examples, or uncertainty labels | Evidence and Verification Discipline |
| `verification_action` | runs tests, checks diffs, renders previews, compares hashes, validates facts | Evidence and Verification Discipline |
| `ai_delegation` | decomposes tasks, assigns AI roles, uses substeps, requests structured output | AI Orchestration and Critical Review |
| `critical_review` | rejects, edits, tightens, or redirects AI output | AI Orchestration and Critical Review |
| `artifact_delivery` | creates usable files, docs, templates, cards, scripts, reports, or workflows | Delivery, Transfer, and Iteration |
| `iteration_transfer` | turns a repeated issue into a reusable rule, checklist, script, or skill update | Delivery, Transfer, and Iteration |

One event can support multiple dimensions, but do not duplicate the same evidence as if it were independent.

## Five-Dimension Mapping

Use this as the minimum necessary abstraction layer:

1. Problem framing: whether the user controls what problem is being solved.
2. Reasoning/modeling: whether the user builds transferable structure instead of isolated outputs.
3. Evidence/verification: whether claims and outputs are checked against reality.
4. AI orchestration/review: whether the user uses AI as a controlled collaborator rather than an authority.
5. Delivery/iteration: whether the work becomes usable artifacts and better future process.

These dimensions are fixed for cross-person comparison. Do not add new scoring dimensions unless the user explicitly wants a separate experimental analysis. If a new pattern appears, express it as evidence under the closest fixed dimension or as a qualitative note.

## Scoring From Evidence

For each dimension:

1. Collect 2-5 strongest evidence bullets.
2. Record counterexamples separately.
3. Choose the anchor band from `rubric.md`.
4. Apply the repeatability worksheet adjustments.
5. Clamp to an integer from `0` to `100`.
6. Assign confidence from evidence breadth, rawness, and traceability.

Do not score high from fluent prose alone. Do not score low from short prompts alone. Judge whether the user repeatedly controlled the collaboration.

## Composite Score

Use the fixed weights from `rubric.md`:

```text
Problem Framing and Constraint Control: 22
Reasoning and Model Building: 22
Evidence and Verification Discipline: 20
AI Orchestration and Critical Review: 18
Delivery, Transfer, and Iteration: 18
```

Formula:

```text
composite = round(sum(dimension_score_i * weight_i) / 100)
```

The composite is an integer from `0` to `100`.

## Deterministic Worktype Matching

After scoring, derive the worktype from the full vector:

```text
[problem_framing, reasoning_modeling, evidence_verification, ai_orchestration, delivery_iteration]
```

Use `scripts/classify_worktype.py` when a machine-readable JSON result exists:

```powershell
python "%USERPROFILE%\.codex\skills\ai-collab-scorecard\scripts\classify_worktype.py" `
  "C:\path\to\scorecard.json" `
  --out "C:\path\to\scorecard.with-worktype.json"
```

The script:

- reads integer five-dimension scores
- computes the weighted distance to each fixed prototype
- returns primary type, integer fit score, secondary tendency, and risk modifiers
- fills fixed Chinese/English worktype names from the registry
- can fill default share-card copy when absent

Do not derive the type from the single highest dimension. Do not let the model invent a new type.

## Confidence Gate

Do not suppress a worktype solely because the sample is small. If five integer dimension scores exist, produce the best matching fixed worktype and lower `worktype.fit_score` through the evidence sufficiency factor in `worktypes.md`.

Do not produce a public worktype card only when:

- more than two dimensions are insufficient evidence
- the five dimension scores themselves cannot be fairly produced
- the corpus is mostly final artifacts without enough raw collaboration history to score the dimensions

In those cases, produce only a serious diagnostic note and say what additional history is needed. If scores can be produced but the sample is thin, classify normally and let the lowered match score communicate uncertainty.

## Repeatability Self-Check

Before finalizing:

- The same manifest should lead to the same evidence map.
- The same evidence map should keep each dimension within about 5 points across repeated assessments.
- Composite drift should stay within about 3 points unless the evidence interpretation changed.
- Type should stay the same unless the top two fit scores are very close.
- Any score movement must be explained by evidence, not by a more persuasive writing style.
