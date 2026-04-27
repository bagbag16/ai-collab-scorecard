# Worktype Registry

Use this file to derive worktypes from the full five-dimension profile. Do not classify by the single strongest dimension.

## Canonical Dimensions

Use this vector order:

`[problem_framing, reasoning_modeling, evidence_verification, ai_orchestration, delivery_iteration]`

All subject dimension scores are integers from `0` to `100`. Normalize them from `0.0` to `1.0` by dividing each score by `100`.

## Quantitative Matching

For each prototype:

1. Normalize the subject score vector.
2. Compare it to each prototype vector.
3. Compute distance:

`distance = sqrt(sum(weight_i * (subject_i - prototype_i)^2) / sum(weight_i))`

Use these dimension weights unless the user asks for a role-specific comparison:

`[1.10, 1.05, 1.00, 1.05, 1.00]`

Convert distance to raw prototype fit:

`prototype_fit_score = round(max(0, 100 * (1 - distance / 0.75)))`

The prototype fit score is an integer from `0` to `100`. Do not output decimals.

Select the highest raw prototype fit score as the primary worktype. If the top two raw prototype fit scores differ by less than `5`, report a hybrid such as `Type A + Type B`, but keep both names from the registry.

Then adjust the displayed match score for evidence sufficiency:

`fit_score = round(prototype_fit_score * evidence_sufficiency_factor)`

Use `fit_score` on the share card. Keep `prototype_fit_score` in the serious JSON/report when possible.

Evidence sufficiency factors:

| Evidence Level | Factor | Typical Signal |
|---|---:|---|
| Full | `1.00` | Full-history or broad raw corpus with many user corrections and validations. |
| Standard | `0.92` | Multiple sessions/tasks with visible steering traces. |
| Basic | `0.78` | Several examples, but limited task range or correction trace. |
| Thin | `0.62` | One or two tasks, sparse raw history, or weak steering trace. |
| Minimal/unknown | `0.45-0.50` | Very little source material or only summary-level evidence. |

Low overall evidence confidence caps the factor at `0.70`; medium evidence confidence caps it at `0.92`.

Do not suppress the worktype solely because the sample is small. If five integer dimension scores exist, output the best matching fixed type and let the evidence-adjusted `fit_score` communicate uncertainty. If dimension scores cannot fairly be produced at all, stop at an evidence-limits note instead of inventing scores.

When a scorecard JSON already exists, prefer `scripts/classify_worktype.py` to apply this formula and fill fixed registry names, raw prototype fit, evidence-adjusted fit score, secondary tendency, risk modifiers, and default share-card copy deterministically.

## Prototype Registry

### ai-systems-architect

- Serious name: `AI Systems Architect`
- Chinese serious name: `工作流架构型`
- Share name: `Cyber Foreman`
- Chinese share name: `赛博包工头`
- Prototype vector: `[0.90, 0.88, 0.78, 0.88, 0.76]`
- Standard illustration asset: `assets/worktype-illustrations/ai-systems-architect.png`
- Meaning: Builds AI-assisted systems, rules, workflows, and reusable structures.
- Best AI setup: Long-running context, explicit state, checklists, review gates.
- Comedy failure mode: Turns a quick request into a governance framework with a runway.

### prompt-air-traffic-controller

- Serious name: `AI Orchestration Controller`
- Chinese serious name: `输出调度型`
- Share name: `Prompt Air-Traffic Controller`
- Chinese share name: `流水线督工`
- Prototype vector: `[0.78, 0.72, 0.72, 0.95, 0.72]`
- Standard illustration asset: `assets/worktype-illustrations/prompt-air-traffic-controller.png`
- Meaning: Strong at routing AI tasks, setting constraints, and preventing output drift.
- Best AI setup: Multi-step task plans, explicit delegation, structured review.
- Comedy failure mode: The AI asks for a prompt and receives an operations manual.

### evidence-auditor

- Serious name: `Evidence Auditor`
- Chinese serious name: `证据校验型`
- Share name: `Receipt Collector`
- Chinese share name: `赛博对账人`
- Prototype vector: `[0.76, 0.72, 0.95, 0.72, 0.70]`
- Standard illustration asset: `assets/worktype-illustrations/evidence-auditor.png`
- Meaning: Strong at checking claims, finding gaps, and preventing unsupported conclusions.
- Best AI setup: Source-linked outputs, test cases, diffs, review rubrics.
- Comedy failure mode: No claim leaves the room without a receipt.

### problem-architect

- Serious name: `Problem Architect`
- Chinese serious name: `问题界定型`
- Share name: `Scope Boundary Patrol`
- Chinese share name: `边界判官`
- Prototype vector: `[0.95, 0.82, 0.72, 0.74, 0.68]`
- Standard illustration asset: `assets/worktype-illustrations/problem-architect.png`
- Meaning: Strong at defining the real problem, boundaries, layers, and non-goals.
- Best AI setup: Discovery first, solution second, with explicit assumptions.
- Comedy failure mode: Stops the meeting to ask whether the problem has permission to exist.

### system-modeler

- Serious name: `System Modeler`
- Chinese serious name: `机制建构型`
- Share name: `Framework Construction Crew`
- Chinese share name: `抽象大师`
- Prototype vector: `[0.78, 0.95, 0.72, 0.70, 0.66]`
- Standard illustration asset: `assets/worktype-illustrations/system-modeler.png`
- Meaning: Strong at abstracting mechanisms, causal models, and reusable concepts.
- Best AI setup: Concept maps, examples, counterexamples, compression into rules.
- Comedy failure mode: Sees one bug and returns with a theory of civilization.

### delivery-integrator

- Serious name: `Delivery Integrator`
- Chinese serious name: `交付封装型`
- Share name: `Workflow Blacksmith`
- Chinese share name: `落地狠人`
- Prototype vector: `[0.76, 0.70, 0.74, 0.78, 0.95]`
- Standard illustration asset: `assets/worktype-illustrations/delivery-integrator.png`
- Meaning: Strong at turning AI-assisted work into usable artifacts, routines, and adoption.
- Best AI setup: Acceptance criteria, final artifacts, templates, release notes.
- Comedy failure mode: Will not leave until the idea has a filename and a checklist.

### fast-ai-delegator

- Serious name: `Fast AI Delegator`
- Chinese serious name: `初稿驱动型`
- Share name: `Ship-It Summoner`
- Chinese share name: `初稿仙人`
- Prototype vector: `[0.62, 0.62, 0.48, 0.88, 0.82]`
- Standard illustration asset: `assets/worktype-illustrations/fast-ai-delegator.png`
- Meaning: Uses AI quickly to produce and iterate, but may under-check assumptions.
- Best AI setup: Guardrails, verification prompts, source checks before shipping.
- Comedy failure mode: Ships first, asks reality to file a ticket.

### abstract-explorer

- Serious name: `Abstract Explorer`
- Chinese serious name: `概念发散型`
- Share name: `Cloud Castle Engineer`
- Chinese share name: `脑洞永动机`
- Prototype vector: `[0.72, 0.90, 0.62, 0.66, 0.45]`
- Standard illustration asset: `assets/worktype-illustrations/abstract-explorer.png`
- Meaning: Strong at exploration and abstraction, weaker at final landing and delivery.
- Best AI setup: Forced landing points, interim conclusions, output deadlines.
- Comedy failure mode: The idea is brilliant; the file is still unnamed.

### execution-accelerator

- Serious name: `Execution Accelerator`
- Chinese serious name: `执行推进型`
- Share name: `Task Bulldozer`
- Chinese share name: `光速进度条`
- Prototype vector: `[0.50, 0.55, 0.58, 0.72, 0.88]`
- Standard illustration asset: `assets/worktype-illustrations/execution-accelerator.png`
- Meaning: Good at moving work forward once goals are set, weaker at redefining the problem.
- Best AI setup: Clear specs, bounded tasks, external review.
- Comedy failure mode: Solves the ticket before asking whether it should exist.

### ai-dependent-operator

- Serious name: `AI-Dependent Operator`
- Chinese serious name: `AI主导型`
- Share name: `Autopilot Enjoyer`
- Chinese share name: `智驾躺平哥`
- Prototype vector: `[0.35, 0.38, 0.32, 0.50, 0.52]`
- Standard illustration asset: `assets/worktype-illustrations/ai-dependent-operator.png`
- Meaning: Output may exist, but human steering, review, or ownership evidence is weak.
- Best AI setup: Small tasks, explicit review questions, required human judgment notes.
- Comedy failure mode: The AI is driving and the user is rating the scenery.

## Secondary Tendency

After selecting the primary type, identify one secondary tendency using the largest positive residual:

`residual_i = subject_i - primary_prototype_i`

Map the largest residual dimension to:

- problem_framing -> `problem-architect tendency`
- reasoning_modeling -> `system-modeler tendency`
- evidence_verification -> `evidence-auditor tendency`
- ai_orchestration -> `ai-orchestration tendency`
- delivery_iteration -> `delivery-integrator tendency`

If no residual exceeds `0.10`, write `balanced within primary type`.

## Risk Modifiers

Add at most two risk modifiers. Use these quantitative triggers:

- `abstraction-outpaces-landing`: reasoning_modeling >= 0.82 and delivery_iteration <= 0.68
- `fast-delegation-risk`: ai_orchestration >= 0.80 and evidence_verification <= 0.62
- `scope-expansion-risk`: problem_framing >= 0.82 and delivery_iteration <= 0.72
- `verification-gap`: evidence_verification <= 0.58 while composite >= 70
- `human-steering-unclear`: AI orchestration evidence is mostly final-output-only
- `delivery-bottleneck`: delivery_iteration is the lowest dimension and below 0.65
- `balanced-high-performer`: all dimensions >= 0.76

Risk modifiers are not insults. Present them as collaboration design constraints.
