# Share Card Copy Rules

Use this file when creating or reviewing the playful share-card copy layer. The machine-readable source used by the renderer is `references/share-copy.json`.

## Fixed Copy Zones

All Chinese standard cards use these fixed upper limits. Count normalized characters after collapsing whitespace; punctuation and ASCII letters count as characters.

| Field | Label | Min chars | Max chars | Line width | Max lines | Font size |
|---|---|---:|---:|---:|---:|---:|
| `superpower` | 高光能力 | 0 | 20 | 20 | 1 | 35 |
| `comedy_failure_mode` | 弱项提醒 | 0 | 20 | 20 | 1 | 35 |

The standard image card no longer renders `tagline` / `寄语` / `卡牌描述`. Existing `tagline` values may remain in JSON for backward compatibility, but they must not appear on the standard card. `superpower` and `comedy_failure_mode` should stay objective and concrete.

## Final Naming And Copy

| type_id | 非严肃名 | 严肃名 | 高光能力 | 弱项提醒 |
|---|---|---|---|---|
| `ai-systems-architect` | 赛博包工头 | 工作流架构型 | 搭建规则、流程与状态系统 | 易把轻量问题过度工程化处理 |
| `prompt-air-traffic-controller` | 流水线督工 | 输出调度型 | 调度多轮输出、节奏与接力 | 流程过重会压低探索弹性空间 |
| `evidence-auditor` | 赛博对账人 | 证据校验型 | 核验证据、来源、反例与缺口 | 审查过密会拖慢讨论节奏感 |
| `problem-architect` | 边界判官 | 问题界定型 | 界定目标、边界、非目标范围 | 前置界定容易拉长启动周期 |
| `system-modeler` | 抽象大师 | 机制建构型 | 抽取机制、变量、因果结构 | 抽象过深会延迟落地节奏感 |
| `delivery-integrator` | 落地狠人 | 交付封装型 | 封装成果、模板与交接版本 | 易重交付形态与包装设计感 |
| `fast-ai-delegator` | 初稿仙人 | 初稿驱动型 | 快速生成版本并推动迭代闭环 | 前期约束与校验容易不够清晰 |
| `abstract-explorer` | 脑洞永动机 | 概念发散型 | 持续发散概念、隐喻与方向 | 收束与落地节奏容易失焦漂移 |
| `execution-accelerator` | 光速进度条 | 执行推进型 | 推进明确任务直到完成交付 | 容易跳过问题校准与复查环节 |
| `ai-dependent-operator` | 智驾躺平哥 | AI主导型 | 借力AI快速形成可用产出 | 人工审阅与取舍痕迹偏弱明显 |

## Tone

- Keep the serious scorecard separate from the share-card copy.
- Make the copy concrete, workplace-safe, and mildly funny.
- Prefer compact, memorable lines over explanations.
- Describe observable AI collaboration behavior, not fixed identity, IQ, mental health, morality, or hiring suitability.
- For weak points, write as a collaboration design reminder rather than an insult.

## Overrides

A scored result may override `type_copy` with evidence-specific text, but it must still respect the same limits and keep the same naming boundary: non-serious names are only for the share card, serious names remain the report-facing worktype labels.
