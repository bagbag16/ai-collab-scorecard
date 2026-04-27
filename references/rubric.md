# Scoring Rubric

## Composite Formula

Score each dimension as an integer from `0` to `100`. Do not output decimals for dimension scores.

Composite score:

`composite = round(sum(dimension_score_i * weight_i) / 100)`

The composite is also an integer from `0` to `100`. Do not output decimals for the composite score.

Weights:

| Dimension | Weight |
|---|---:|
| Problem Framing and Constraint Control | 22 |
| Reasoning and Model Building | 22 |
| Evidence and Verification Discipline | 20 |
| AI Orchestration and Critical Review | 18 |
| Delivery, Transfer, and Iteration | 18 |

Composite bands:

| Composite | Band | Interpretation |
|---:|---|---|
| 90-100 | Exceptional | Stable high-level cognitive work across difficult tasks, with strong evidence and transfer. |
| 80-89 | Strong | Clear above-average collaboration capability with repeatable strengths and manageable gaps. |
| 65-79 | Solid | Useful and reliable in many contexts, but uneven under complexity or weak evidence discipline. |
| 50-64 | Developing | Some strengths appear, but the work depends heavily on AI, narrow context, or external correction. |
| 0-49 | Fragile or Insufficient | Evidence is weak, inconsistent, mostly unowned, or not enough to support capability claims. |

Use `insufficient evidence` instead of a number when a dimension has no meaningful trace.

## General 0-100 Anchor

Use these bands consistently across all dimensions:

| Score | Meaning |
|---:|---|
| 0-19 | Very weak, absent, or actively counter-evidenced in the corpus. |
| 20-39 | Weak; appears occasionally but is unreliable or mostly AI-supplied. |
| 40-59 | Developing; locally useful but uneven, partial, or heavily context-dependent. |
| 60-74 | Solid; usually reliable in familiar contexts with some gaps under complexity. |
| 75-89 | Strong; repeatable across tasks with clear human ownership and few major gaps. |
| 90-100 | Exceptional; stable across difficult tasks, transferable, evidence-backed, and compounding. |

When choosing a specific integer inside a band, use evidence density, task difficulty, cross-sample consistency, and human ownership to place it.

## Required Component Scoring Standard

Do not assign a dimension score by overall impression. Score every dimension with this fixed 100-point component structure, then use the anchor bands as a sanity check.

Dimension score:

`dimension_score = core_behavior + cross_task_consistency + human_ownership + difficulty_transfer + counterexample_adjustment`

Clamp the final score to an integer from `0` to `100` after applying evidence caps.

| Component | Points | What It Measures |
|---|---:|---|
| Core behavior | 45 | The dimension-specific behavior itself. Score three sub-behaviors at `0-15` each. |
| Cross-task consistency | 20 | Whether the behavior repeats across tasks, sessions, and task types. |
| Human ownership | 20 | Whether the corpus shows user-authored steering, correction, judgment, or validation rather than AI-only output. |
| Difficulty and transfer | 15 | Whether the behavior appears under ambiguity, complexity, or transfers into reusable artifacts/process. |
| Counterexample adjustment | `0` to `-15` | Deduct for repeated contradictory evidence. Never add points here. |

### Core Behavior Subscores

For each dimension, score the three listed sub-behaviors from `0` to `15`:

| Subscore | Meaning |
|---:|---|
| 0 | Absent, contradicted, or only AI-supplied. |
| 4 | Incidental or generic; appears once without control effect. |
| 8 | Partially present; useful locally but uneven or incomplete. |
| 12 | Reliable; clearly affects the collaboration outcome. |
| 15 | Strong and transferable; repeatedly shapes difficult work. |

Dimension-specific core behaviors:

| Dimension | Core behavior A | Core behavior B | Core behavior C |
|---|---|---|---|
| Problem Framing and Constraint Control | Defines the real problem, success criteria, and decision target. | Sets constraints, non-goals, scope boundaries, and role/domain expectations. | Corrects wrong layers, hidden assumptions, solution drift, or over-broad framing. |
| Reasoning and Model Building | Builds clear concepts, categories, taxonomies, or mechanism boundaries. | Explains causal links, tradeoffs, dependencies, or failure modes. | Compresses cases into reusable models, principles, rules, or abstractions without losing concrete fit. |
| Evidence and Verification Discipline | Requests evidence, sources, tests, examples, uncertainty labels, or counterexamples. | Performs or uses validation: tests, diffs, previews, hashes, citations, reproduction, review gates. | Revises claims, plans, or outputs when evidence is missing, weak, or contradictory. |
| AI Orchestration and Critical Review | Decomposes and delegates AI work with clear roles, constraints, formats, or checkpoints. | Critically reviews, rejects, edits, or redirects AI output instead of accepting it as authority. | Maintains human-owned decisions, memory, priorities, and final judgment across the workflow. |
| Delivery, Transfer, and Iteration | Produces usable artifacts, files, reports, workflows, or decisions. | Iterates based on feedback, tests, visual checks, user experience, or adoption needs. | Converts repeated work into reusable templates, scripts, standards, skills, or process improvements. |

### Cross-Task Consistency

Score this component from `0` to `20`:

| Score | Evidence Requirement |
|---:|---|
| 0 | No meaningful evidence. |
| 5 | One isolated example. |
| 10 | Two to three examples, mostly one task type. |
| 15 | Four to seven examples across at least two task types. |
| 20 | Eight or more examples across at least three task types or a full-history corpus. |

Do not count repeated messages inside the same narrow episode as independent examples.

### Human Ownership

Score this component from `0` to `20`:

| Score | Evidence Requirement |
|---:|---|
| 0 | Final output only; user steering is invisible. |
| 5 | User gives broad requests but little correction or judgment. |
| 10 | User adds constraints or preferences, but AI still sets most standards. |
| 15 | User repeatedly corrects, validates, rejects, or reframes AI output. |
| 20 | User clearly owns the collaboration: standards, decisions, verification, and final acceptance are visible. |

This component prevents polished AI output from being scored as human capability.

### Difficulty And Transfer

Score this component from `0` to `15`:

| Score | Evidence Requirement |
|---:|---|
| 0 | Only trivial, copied, or routine work. |
| 4 | Familiar low-ambiguity tasks with little adaptation. |
| 8 | Moderate ambiguity or multi-step work handled locally. |
| 12 | Complex, cross-step, or ambiguous work handled with useful adaptation. |
| 15 | Behavior transfers across contexts or becomes a reusable asset, rule, workflow, or standard. |

### Counterexample Adjustment

Apply at most one deduction per dimension:

| Deduction | When To Apply |
|---:|---|
| 0 | No material counterexample or only minor noise. |
| -5 | One clear counterexample or recurring small weakness. |
| -10 | Multiple counterexamples in different episodes. |
| -15 | Counterexamples are strong enough to question the claimed capability pattern. |

Do not use counterexamples to punish style. Use only behavior that directly weakens the dimension.

### Evidence Caps

Caps are mandatory. Apply the lowest relevant cap after component scoring:

| Evidence Condition | Maximum Score |
|---|---:|
| No meaningful user-authored evidence for the dimension | `insufficient evidence` |
| Final artifacts only; no raw prompt/correction/review trace | 39 |
| Fewer than 3 task episodes for the dimension | 59 |
| No visible user correction, rejection, constraint, or validation trace | 64 |
| Evidence is from one narrow domain only | 74 |
| No actual validation action for Evidence and Verification Discipline | 74 |
| No delivered artifact or accepted outcome for Delivery, Transfer, and Iteration | 74 |
| No reusable pattern, cross-task transfer, or difficult-task evidence | 89 |

If a cap changes the score, report it in the scoring breakdown.

### Required Scoring Breakdown

For serious assessments, keep this breakdown internally and include it when the user wants objectivity or repeatability:

```json
{
  "dimension": "problem_framing",
  "core_behavior": {
    "A": 0,
    "B": 0,
    "C": 0,
    "subtotal": 0
  },
  "cross_task_consistency": 0,
  "human_ownership": 0,
  "difficulty_transfer": 0,
  "counterexample_adjustment": 0,
  "raw_total": 0,
  "caps_applied": ["string"],
  "final_score": 0,
  "confidence": "low|medium|high"
}
```

Do not hide uncertainty by rounding upward. If evidence is thin, the component score may be high locally, but confidence and caps must show the limitation.

## Anchor Cross-Check And Repeatability Worksheet

Use this worksheet to make repeated assessments of the same person converge. Apply it once per dimension before outputting the final integer.

1. Compute the component score using the required component scoring standard.
2. Pick the anchor band from the dimension table.
3. If the component score falls outside the selected anchor band by more than `10` points, revisit the evidence and component subscores.
4. If the evidence is still ambiguous, start from the anchor midpoint:
   - `0-19` -> `10`
   - `20-39` -> `30`
   - `40-59` -> `50`
   - `60-74` -> `67`
   - `75-89` -> `82`
   - `90-100` -> `95`
5. Apply these bounded adjustments only as tie-breakers inside the final anchor band, not as a replacement for component scoring:

| Factor | Adjustment |
|---|---:|
| Broad evidence across 5+ tasks or sessions | `+3` |
| Broad evidence across 10+ tasks or sessions | `+5` instead of `+3` |
| High task difficulty or ambiguous input handled well | `+3` |
| Clear human steering/correction evidence | `+3` |
| Reusable artifact, rule, or process produced | `+2` |
| Evidence mostly final-output-only | `-5` |
| Strong counterexamples in multiple tasks | `-5` |
| Domain-narrow evidence only | `-3` |
| Important evidence is missing or edited | `-3` |

6. Apply mandatory evidence caps.
7. Output the final clamped score as an integer.

Do not use decimals. Do not overfit a single excellent or poor example. Score the repeated pattern.

## Dimension 1: Problem Framing and Constraint Control

Measures whether the person can define the real problem, separate layers, freeze constraints, and prevent scope drift.

Anchors:

| Score | Evidence Pattern |
|---:|---|
| 0-19 | No visible problem framing; accepts AI's framing without inspection. |
| 20-39 | States a goal but misses key constraints, stakeholders, or task boundaries. |
| 40-59 | Can clarify local requirements, but often mixes problem, solution, and preference. |
| 60-74 | Usually separates goal, constraints, assumptions, and next step; occasional drift remains. |
| 75-89 | Consistently names the real issue, distinguishes layers, and keeps AI work bounded. |
| 90-100 | Reframes ambiguous situations into stable, testable problem structures across domains. |

Look for:
- Early problem definition
- Explicit constraints and non-goals
- Separation of premise, mechanism, execution, and presentation
- Corrections when AI solves the wrong layer

## Dimension 2: Reasoning and Model Building

Measures abstraction quality, causal reasoning, concept boundaries, and ability to build reusable models without losing contact with the concrete task.

Anchors:

| Score | Evidence Pattern |
|---:|---|
| 0-19 | Mostly surface-level preference or task copying. |
| 20-39 | Uses concepts loosely; analogies or categories do not control the work. |
| 40-59 | Produces partial structures but often overgeneralizes or misses causal links. |
| 60-74 | Builds workable models for familiar problems with mostly coherent boundaries. |
| 75-89 | Handles multi-layer systems, tradeoffs, and failure modes with clear structure. |
| 90-100 | Creates compact, transferable models that explain, predict, and guide action across cases. |

Look for:
- Concept boundary control
- Causal chains and tradeoff reasoning
- Ability to compress complexity without flattening it
- Reusable principles extracted from cases

## Dimension 3: Evidence and Verification Discipline

Measures whether claims are tied to observable evidence, tested against alternatives, and revised when contradicted.

Anchors:

| Score | Evidence Pattern |
|---:|---|
| 0-19 | Treats plausible AI output as true without checks. |
| 20-39 | Asks for evidence occasionally but does not act on gaps. |
| 40-59 | Checks obvious facts, but weakly tracks uncertainty or counterexamples. |
| 60-74 | Often asks for verification, distinguishes evidence from inference, and catches some errors. |
| 75-89 | Maintains traceable evidence, tests alternatives, and prevents unsupported promotion. |
| 90-100 | Builds durable verification loops, regression examples, and update gates for future work. |

Look for:
- Source/evidence requests
- Tests, reviews, diffs, examples, or empirical checks
- Explicit uncertainty
- Revisions after disconfirming evidence

## Dimension 4: AI Orchestration and Critical Review

Measures how well the person uses AI as a collaborator: delegation, prompting, critique, correction, synthesis, and ownership of decisions.

Anchors:

| Score | Evidence Pattern |
|---:|---|
| 0-19 | Mostly copy-pastes AI output or treats AI as authority. |
| 20-39 | Gives broad prompts and accepts generic results with light edits. |
| 40-59 | Can ask follow-ups but often lets AI set the structure and standards. |
| 60-74 | Gives usable constraints, reviews outputs, and corrects visible misses. |
| 75-89 | Steers AI through layered tasks, catches subtle drift, and integrates outputs into owned work. |
| 90-100 | Uses AI as a force multiplier while preserving clear human judgment, validation, and system memory. |

Look for:
- Prompt specificity and constraint quality
- Rejection or correction of flawed AI assumptions
- Good task decomposition
- Human-owned final judgment

## Dimension 5: Delivery, Transfer, and Iteration

Measures whether collaboration produces usable artifacts, learning loops, reusable rules, and improved future performance.

Anchors:

| Score | Evidence Pattern |
|---:|---|
| 0-19 | No usable output or repeated abandoned fragments. |
| 20-39 | Produces isolated outputs that require heavy external cleanup. |
| 40-59 | Produces usable local artifacts, but little transfer or follow-through. |
| 60-74 | Delivers coherent artifacts and incorporates feedback in later work. |
| 75-89 | Turns repeated work into templates, rules, tests, or process improvements. |
| 90-100 | Builds compounding capability: artifacts, standards, and workflows improve across cycles. |

Look for:
- Finished artifacts and adoption
- Iterative improvement
- Reusable templates or rules
- Reduction of repeated failure modes

## Confidence Rules

Use confidence separately from score:

| Confidence | Meaning |
|---|---|
| Low | Corpus is thin, edited, one-domain, final-output-only, or lacks user correction traces. |
| Medium | Multiple tasks are available, but task difficulty, authorship, or outcomes are partly unclear. |
| High | Corpus includes raw prompts, AI outputs, user corrections, artifacts, outcomes, and repeated patterns. |

Do not increase confidence because prose sounds sophisticated. Increase confidence only when evidence is broad, raw, and traceable.

## Common Misreads

- Fluent writing is not automatically strong reasoning.
- Sparse writing is not automatically weak reasoning.
- Final artifact quality is not enough; inspect steering and validation.
- Domain expertise can look like general intelligence; mark domain dependence.
- Repeated use of AI does not mean strong AI collaboration; the user must show judgment over the AI.
- A high score in this rubric does not imply a specific IQ number.

## Colleague Abstraction Pattern

When abstracting a colleague, use this structure:

1. Describe the sample base and role context.
2. Score the five dimensions with evidence and the repeatability worksheet.
3. Derive the worktype from `worktypes.md`.
4. Identify one improvement lever tied to the lowest high-impact dimension.
5. State non-claims: what cannot be concluded from the corpus.

## Worktype Derivation

Use worktypes only after scoring. A worktype is a communication layer over the scorecard, not a separate assessment. For the full registry and matching formula, read `worktypes.md`.

Primary type must come from the full five-dimension score profile, not from the single strongest dimension. Treat the score vector as the source:

`[problem_framing, reasoning_modeling, evidence_verification, ai_orchestration, delivery_iteration]`

Use fixed prototype matching from `worktypes.md`. Report:

- `worktype`
- `fit_score / 100`
- `prototype_fit_score / 100` when producing a serious JSON/report
- `evidence_sufficiency.factor`
- `secondary_tendency`
- `risk_modifier`
- `classification_confidence`

Rules:

- Do not suppress a playful type solely because the sample is small; reduce the displayed `fit_score` through the evidence sufficiency factor.
- Do not use demeaning labels. The playful name can tease a behavior, not attack the person.
- Do not invent strengths to make the card flattering.
- If the user wants public sharing, remove sensitive examples and keep only abstracted patterns.
- If comparing colleagues, keep share-card language equally light across people so the format does not bias perceived performance.
