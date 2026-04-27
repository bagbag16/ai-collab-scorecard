---
name: ai-collab-scorecard
description: Evaluate long-term AI/Codex collaboration corpora, chat logs, prompts, revisions, and produced artifacts to build an evidence-grounded cognitive work capability scorecard. Use when the user asks to assess AI collaboration records, abstract a colleague's capability profile from their AI-assisted work, compare collaboration quality across people, or convert long-term chat/productivity traces into neutral dimension scores. Do not use as an IQ test, personality diagnosis, hiring decision automation, or clinical assessment.
---

# AI Collab Scorecard

## Purpose

Assess observable cognitive work behavior in long-term AI collaboration records. The result is a neutral scorecard, not an IQ estimate or total-person judgment.

Use `references/setup-and-data-sources.md` when installing, validating, or collecting historical collaboration records. Use `references/sampling-protocol.md` and `scripts/build_corpus_manifest.py` to freeze corpus scope. Use `references/evidence-abstraction-pipeline.md` and `scripts/extract_collab_signals.py` to turn raw history into five-dimension evidence. Use the detailed scoring anchors in `references/rubric.md` when assigning scores. Use `references/output-schema.md` for machine-readable output. Use `references/worktypes.md` and `scripts/classify_worktype.py` when deriving worktypes. Use `references/share-card-image.md`, `references/share-copy.md`, `scripts/render_share_card_png.ps1`, and `scripts/render_share_card.py` when the user asks for a shareable image/card. Use `references/asset-production/worktype-avatar-brief.md` only when producing or replacing the fixed worktype illustration asset batch outside runtime.

Respond in the user's language. For Chinese users, all human-facing conclusions, headings, score labels, dimension names, worktype descriptions, status notes, evidence bullets, limits, and share-card explanations must be in Chinese. Keep English only for machine-readable JSON keys, script arguments, file paths, fixed `type_id` values, or an optional appendix when cross-person comparison requires canonical English labels.

## Guardrails

- Score only evidence visible in the corpus: prompts, corrections, constraints, decisions, review comments, artifact changes, and follow-up results.
- Separate the user's contribution from the AI's contribution. A polished final artifact is weak evidence unless the corpus shows how the user steered, rejected, corrected, or validated it.
- Prefer "insufficient evidence" over confident inference when the corpus is thin, narrow, edited, or mostly AI-generated.
- Do not infer mental health, moral quality, personality type, or exact IQ. If asked about IQ, state that this skill measures AI-assisted cognitive work performance, not psychometric intelligence.
- Normalize by role, domain, task difficulty, and available context before comparing people.
- Keep the serious assessment and any playful/shareable derivative strictly separate. Humor may make the result easier to share, but must never change scores, evidence, confidence, or capability claims.

## Workflow

0. If the user asks how to install, use, or reuse the skill, read `references/setup-and-data-sources.md` first:
   - Verify the skill folder is installed under the active Codex skills directory
   - Run the basic skill validation when useful
   - Explain required runtime assumptions before collecting private history
   - If installation, validation, rendering, or corpus acquisition is incomplete on the current machine, enter the completion recovery protocol in `references/setup-and-data-sources.md`
   - Do not stop at the first missing dependency or configuration difference; diagnose the gap, ask for the minimum needed permission, repair what can be repaired, and continue toward a complete scorecard

1. Define the assessment scope and data source:
   - Person or team being assessed
   - Time window and corpus sources
   - Role/domain expectations
   - Whether the goal is self-review, coaching, team abstraction, or comparison
   - Corpus manifest or sampling method from `references/sampling-protocol.md`
   - If the user asks to use "all current Codex/software history" but has not explicitly granted local-history access in this turn, first ask for permission to inspect current Codex/software history read-only; do not assume elevated local access
   - After the user grants permission, treat the current local Codex history as the intended corpus: inspect only Codex-owned or clearly session-related history locations read-only, freeze a manifest, and do not require manual pasted logs unless the local history is unavailable
   - If the user asks for "all Codex history" without explicit authorization, use only user-authorized exports, visible conversation context, or explicitly allowed local history directories; do not silently scrape unrelated private app data

2. Build an evidence map:
   - Task types and difficulty
   - User prompts and constraints
   - AI outputs the user accepted, rejected, or revised
   - User corrections, tests, validations, and final artifacts
   - Repeated patterns across tasks
   - Use `references/evidence-abstraction-pipeline.md` for session segmentation, evidence tagging, and dimension mapping

3. Score the five minimum dimensions:
   - 问题定义与约束控制 (`problem_framing`)
   - 推理建模与机制抽象 (`reasoning_modeling`)
   - 证据校验与验证纪律 (`evidence_verification`)
   - AI 编排与批判性审阅 (`ai_orchestration`)
   - 交付转化与迭代沉淀 (`delivery_iteration`)

4. Produce dimension scores and a composite score:
   - Score each dimension as an integer from `0-100`
   - Compute the weighted composite as an integer from `0-100` using `references/rubric.md`
   - Use the required component scoring standard in `references/rubric.md`; do not assign scores by overall impression
   - Use the repeatability worksheet in `references/rubric.md` before finalizing each score
   - Report percentile-like position only when a real comparison set exists; otherwise do not invent one
   - Include confidence for each score: `low`, `medium`, or `high`
   - Attach 2-5 concrete evidence bullets per dimension

5. Derive the worktype when requested or useful:
   - Use the full five-dimension score vector, not only the strongest dimension
   - Match against fixed prototypes in `references/worktypes.md`
   - Prefer `scripts/classify_worktype.py` to compute the primary type, fit score, secondary tendency, and risk modifiers from a score JSON
   - For Chinese reports, display `serious_name_zh`, `share_name_zh`, `secondary_tendency_zh`, `risk_modifiers_zh`, and `band_zh`; do not expose English enum values in the main conclusion
   - Do not invent new canonical type names

6. Explain the profile:
   - Strongest stable capability
   - Most important bottleneck
   - Best-fit collaboration pattern
   - Risks of over-inference
   - One or two next improvement levers

7. If the user asks for a shareable, viral, or image version, create a separate "Share Card" only after the serious scorecard:
   - Derive it from the scored dimensions and evidence, not from vibes.
   - Make it light, memorable, and mildly funny.
   - Keep it respectful and workplace-safe.
   - Avoid IQ claims, personality diagnosis, fixed identity claims, insults, medicalized labels, or hiring recommendations.
   - Include a tiny disclaimer that the card is a playful summary of the evidence-based scorecard.
   - If creating an image, select a confirmed pre-generated worktype illustration from `assets/worktype-illustrations/manifest.json` and render important text with a deterministic renderer.
   - Use `scripts/render_share_card_png.ps1` for the final standard PNG card on Windows. It loads the deterministic contract from `references/render-lock.json`, uses the bundled pinned font from `assets/fonts/NotoSansSC-VF.ttf`, and fails if the font hash changes. Use `scripts/self_check_render_determinism.ps1` after renderer or layout changes. Use `scripts/render_share_card.py` only for SVG debugging or editable inspection.
   - Use `references/share-copy.json` for standard Chinese share-card copy defaults and enforced text-length/layout limits.
   - Do not call an image model during scorecard/card generation. Image models may be used only when producing the fixed asset batch for the skill, following `references/asset-production/worktype-avatar-brief.md`.
   - When returning a rendered share card, include both a direct image file link and a direct link to the containing output directory.

## Output Template

```md
# AI 协作力评分卡

## 测评范围
- 测评对象：
- 语料范围：
- 角色/领域：
- 测评目标：
- 证据置信度：低/中/高

## 分数
| 维度 | 分数 /100 | 权重 | 置信度 | 解读 |
|---|---:|---:|---|---|
| 问题定义与约束控制 |  | 22 |  |  |
| 推理建模与机制抽象 |  | 22 |  |  |
| 证据校验与验证纪律 |  | 20 |  |  |
| AI 编排与批判性审阅 |  | 18 |  |  |
| 交付转化与迭代沉淀 |  | 18 |  |  |

综合分：`__/100`
档位：

## 评分拆解
每个维度保留以下拆解：
`核心行为 /45`、`跨任务一致性 /20`、`人类主导性 /20`、`难度迁移 /15`、`反例修正`、`上限限制`、`最终分`。

## 量化画像
- 五维向量：`[问题定义, 推理建模, 证据校验, AI 编排, 交付迭代]`
- AI 协作工作型：
- 工作型匹配度：`__/100`
- 第二倾向：
- 风险修正：
- 置信度：

## 各维度证据
## 能力画像
## 主要瓶颈
## 可迁移给同事的抽象
## 非声明与限制
```

## Scoring Discipline

When evidence is mixed, score the repeated pattern, not the best sample. When task difficulty differs sharply, report separate sub-scores by task class instead of forcing one number.

Do not hide uncertainty inside smooth prose. A useful scorecard is allowed to say: "high output quality, but low confidence in human contribution because the corpus lacks correction traces."

## Optional Share Card

Use a share card only as a derivative layer. It should be fun to read, but it is not the source of truth. For a standard final image on Windows, use `scripts/render_share_card_png.ps1` with a JSON result that follows `references/output-schema.md`. For SVG debugging or editable inspection, use `scripts/render_share_card.py`. Both renderers select confirmed assets from `assets/worktype-illustrations/manifest.json`; deterministic placeholder art is only a draft fallback until the fixed image batch is approved.

```md
# AI 协作工作型分享卡

类型：
含义：
这个人倾向于如何使用 AI：
高光能力：
喜剧化风险：
最适合的 AI 配置：
严肃评分卡链接：
小字声明：
```

Good share-card names describe work behavior, not inner essence. Prefer names like "Problem Architect", "Evidence Auditor", "Workflow Blacksmith", "Prompt Air-Traffic Controller", or "Scope Boundary Patrol". Avoid names that imply intelligence rank, moral worth, mental health, or permanent personality.
