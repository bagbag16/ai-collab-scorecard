# Share Card Image Rules

Use this file when the user asks for a shareable image/card based on the scorecard.

## Source Of Truth

Generate the serious scorecard first. The image card is a derivative view and cannot change:

- Dimension scores
- Composite score
- Confidence
- Worktype
- Evidence claims
- Non-claims and limits

## Recommended Workflow

Use two separate phases.

### Asset Production Phase

Run this phase only when building or updating the skill's standard image set. This is an external/manual asset-production phase, not part of runtime card generation. The skill must not call an image model while scoring a subject or rendering a share card:

1. Use ChatGPT image2 or an approved equivalent image model to generate a full batch of worktype illustrations.
2. Generate the batch from `references/asset-production/worktype-avatar-brief.md` so the cards have consistent style, camera, lighting, character proportions, and finish.
3. Make each worktype visibly distinct through silhouette, props, scene structure, accent color, and action.
4. Reject any image with embedded text, logos, illegible symbols, distorted UI text, inconsistent style, or unclear worktype identity.
5. Save only confirmed assets under `assets/worktype-illustrations/`.
6. Update `assets/worktype-illustrations/manifest.json` so each confirmed `type_id` maps to the final image file.

### Runtime Card Phase

Run this phase whenever producing a card for a scored subject:

1. Derive the worktype from `worktypes.md`.
2. Select the matching confirmed image asset from `assets/worktype-illustrations/manifest.json`; this asset must already have been generated, reviewed, and approved before runtime.
3. Render the final share image with `scripts/render_share_card_png.ps1` on Windows. Use `scripts/render_share_card.py` only for SVG debugging or editable inspection.
4. Render the selected image, left text module, and right score module in three fixed rectangular modules.
5. Apply the fixed copy limits from `references/share-copy.json`.
6. Export the final card as PNG. Treat SVG as a non-final debug artifact because live SVG text can vary by previewer and font.

Do not call an image model at runtime. Runtime image generation makes repeat cards drift and breaks type consistency. If no confirmed asset exists, use the deterministic placeholder background only for drafts or development previews.

Do not ask an image model to render critical text. It may misspell, omit, or distort the score.

## Copy Length Contract

The standard Chinese card no longer renders `tagline` / `寄语` / `卡牌描述`. The field may remain in machine-readable JSON for backward compatibility, but the standard image renderer must ignore it.

Only two descriptive copy fields are rendered:

- `superpower` / `高光能力`: max `20` chars, font size `35`, one visual line. If a longer value is supplied, truncate deterministically.
- `comedy_failure_mode` / `弱项提醒`: max `20` chars, font size `35`, one visual line. If a longer value is supplied, truncate deterministically.

Use `references/share-copy.json` for the standard per-type defaults. When writing evidence-specific overrides, keep the copy short, concrete, and evidence-compatible; do not pad text just to fill space.

## Card Format

Default ratio: `4:5`

Default size:

- `1080 x 1350` for social sharing
- `1200 x 630` for link preview when requested

Standard illustration asset size:

- Final runtime illustrations must be composed for the actual visible hero image slot: `996 x 666`, ratio `166:111` (`1.4955:1`).
- Recommended source size for approved assets: `1992 x 1332` or another exact multiple of `996 x 666`.
- `4:5` images may be used only as rough concept drafts. Do not accept them as final runtime assets unless they are manually cropped into the hero-slot ratio first.
- Runtime card export defaults to `1080 x 1350`, but only the top `996 x 666` hero window shows the illustration at full opacity.
- Hero image coordinates are local to the `996 x 666` source: keep the primary character, face, hands, and type-defining props inside `x=120..876`, `y=40..540`.
- The fade zone begins near local `y=518`; feet, floor shadows, or low-priority props may enter it, but identity-critical props must stay above it.
- Keep the final visible character height stable at about `520-590px` inside the `996 x 666` hero window.
- Leave the outer `40px` edge clean so rounded-card clipping never cuts off important content.

External asset brief:

- Treat the asset as a horizontal hero image, not a vertical full-body poster.
- Keep face, hands, main action, and identity-defining props clear in the upper and middle part of the image.
- The image should read as one character, one main action, and one core prop system.
- Show an observable AI-collaboration behavior rather than just a costume.
- Keep supporting scene details light; clarity matters more than visual density.

Required content:

- Title: `你的AI协作型人格是`
- Playful share name
- Serious worktype name, displayed as `严肃类型：{serious_name_zh}`
- Composite score
- Worktype fit score
- Five-dimension score bars in canonical order
- Superpower
- Comedy-grade failure mode
- Tiny disclaimer

Optional content:

- QR/link to full report
- Confidence label
- Secondary tendency
- Risk modifier

## Visual Asset Style

Style rules for creating or replacing the fixed illustration batch live in `references/asset-production/worktype-avatar-brief.md`. This runtime card document only records how confirmed assets are selected and rendered.

## Standard Asset Manifest

The standard image set lives at:

`assets/worktype-illustrations/manifest.json`

Manifest status rules:

- `pending_generation`: concept exists but no approved asset is available.
- `candidate`: generated image exists but has not been accepted.
- `confirmed`: approved asset. Runtime may use it.
- `rejected`: do not use.

Runtime card generation must only use `confirmed` assets. Draft previews may use the deterministic SVG placeholder built into `scripts/render_share_card.py`, but final share output should use `scripts/render_share_card_png.ps1`.

## Stable Layout Contract

The standard `1080 x 1350` card is a deterministic composition of one fixed illustration asset, one lower-left text panel, and one lower-right score panel. Runtime must not use image generation, random layout, auto-fit layout, responsive sizing, or model-written visual decisions.

The machine-readable source for the locked layout, font, renderer settings, asset policy, and repeat-render fixture is `references/render-lock.json`. This Markdown section explains that contract for humans; when the JSON lock and this prose conflict, update the prose to match the JSON lock.

Coordinate system:

- Canvas: `1080 x 1350`
- Unit: CSS/SVG px
- Text coordinates in the tables below use the canonical PNG renderer semantics: `x` and `y` are the top-left draw position. SVG implementations must translate these y values to text baselines before rendering.
- Origin: top-left
- Outer background: `#F8FAFC`
- Card rectangle: `x=42`, `y=42`, `w=996`, `h=1266`, `rx=44`
- All visible content must stay inside the card rectangle.

Layer order, from bottom to top:

1. Outer background fill.
2. Rounded white card.
3. Full-card low-opacity illustration wash, clipped to card: `x=42`, `y=42`, `w=996`, `h=1266`, `opacity=0.16`, `preserveAspectRatio="xMidYMid slice"`.
4. Lower content white veil: `x=42`, `y=705`, `w=996`, `h=603`, `fill=rgba(255,255,255,0.96)`.
5. Hero illustration, clipped to top visual area: `x=42`, `y=42`, `w=996`, `h=666`, `opacity=1`, `preserveAspectRatio="xMidYMid slice"`.
6. Hero fade scrim: `x=42`, `y=560`, `w=996`, `h=148`, vertical gradient from transparent white to `rgba(255,255,255,0.93)`.
7. Lower-left panel: `x=66`, `y=728`, `w=548`, `h=552`, `rx=28`, `fill=rgba(255,255,255,0.93)`.
8. Lower-right panel: `x=650`, `y=728`, `w=364`, `h=552`, `rx=28`, `fill=rgba(255,255,255,0.93)`.
9. Deterministic text, score numbers, and bars.

Do not draw a vertical divider between the lower panels. Separation is created only by panel spacing.

### Lower-Left Text Panel

Fixed panel bounds: `x=66`, `y=728`, `w=548`, `h=552`.

Fixed text positions:

| Element | x | y | Size | Weight | Color | Source |
|---|---:|---:|---:|---:|---|---|
| Intro | 106 | 774 | 31 | 700 | accent | literal `你的AI协作型人格是` |
| Playful share name | 106 | 824 | 66 | 700 | `#101828` | `worktype.share_name_zh` or registry fallback |
| Serious name | 108 | 907 | 34 | 700 | `#475467` | `严肃类型：{worktype.serious_name_zh}` |
| Superpower label | 106 | 994 | 28 | 700 | accent | literal `高光能力` |
| Superpower value | 106 | 1038 | 35 | 700 | `#101828` | `share_card.superpower_zh` or `share_card.superpower` |
| Weakness label | 106 | 1127 | 28 | 700 | accent | literal `弱项提醒` |
| Weakness value | 106 | 1171 | 35 | 700 | `#344054` | `share_card.comedy_failure_mode_zh` or `share_card.comedy_failure_mode` |
| Disclaimer | 106 | 1244 | 17 | 400 | `#98A2B3` | standard disclaimer |

Text overflow rules:

- `share_name_zh`: max 7 Chinese characters at `66px`; if longer, reduce font size in fixed steps `66 -> 60 -> 54`, never below `54`.
- `serious_name_zh`: max 11 Chinese characters after `严肃类型：`; if longer, reduce size `34 -> 31 -> 28`, never below `28`.
- `superpower` and `comedy_failure_mode`: max 20 characters; truncate with `…` at character 20.
- Disclaimer: max 34 characters per line, max 2 lines, size `17`.
- No text may wrap into the right panel.

### Lower-Right Score Panel

Fixed panel bounds: `x=650`, `y=728`, `w=364`, `h=552`.

Score tiles:

| Tile | x | y | w | h | rx | Label x/y | Score x/y | `/100` x/y |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Composite | 672 | 768 | 146 | 132 | 22 | 694 / 793 | 688 / 848 | 760 / 870 |
| Worktype fit | 836 | 768 | 146 | 132 | 22 | 858 / 793 | 852 / 848 | 924 / 870 |

Score tile typography:

- Tile fill: `#F8FAFC`
- Label: size `25`, weight `700`, color `#667085`
- Score: size `54`, weight `700`, color `#101828`, integer `0-100`
- `/100`: size `22`, weight `700`, color `#667085`; for `100`, the renderer moves `/100` right enough to avoid overlap.

Five-dimension section:

- Section title top-left: `x=672`, `y=930`, size `35`, weight `700`, color `#344054`, literal `五维分值`
- Bars start at `x=672`
- First bar y: `990`
- Bar row gap: `56`
- Track x offset from row x: `128`
- Track width: `178`
- Track height: `20`
- Track radius: `10`
- Score text x: `row_x + 128 + 178 + 16`
- Label top-left y: `bar_y - 9`
- Score text top-left y: `bar_y - 10`
- Label size: `25`, score size: `27`

Canonical bar order and labels:

1. `scores.problem_framing.score` -> `问题界定`
2. `scores.reasoning_modeling.score` -> `推理建模`
3. `scores.evidence_verification.score` -> `证据验证`
4. `scores.ai_orchestration.score` -> `AI 编排`
5. `scores.delivery_iteration.score` -> `交付迭代`

Bar fill width is exactly `round(178 * score / 100)`. Clamp all score values to integer `0-100`.

### Determinism Requirements

- Select image only from `assets/worktype-illustrations/manifest.json` entries with `status="confirmed"`.
- The selected asset is determined only by `worktype.type_id`.
- Use `scripts/render_share_card_png.ps1` for final PNG output on Windows.
- Use the bundled font file `assets/fonts/NotoSansSC-VF.ttf`.
- The pinned font SHA256 must be `763146584CF0710223441356B4395E279021B0806C196614377A7A0174AE074A`; the renderer must fail if the hash differs.
- Render at `1080 x 1350`, `96 DPI`.
- Use a private font collection instead of system font fallback.
- Use fixed renderer settings: `SmoothingMode=AntiAlias`, `InterpolationMode=HighQualityBicubic`, `TextRenderingHint=AntiAliasGridFit`, `CompositingQuality=HighQuality`, `PixelOffsetMode=Half`.
- Do not render any text embedded inside the image asset.
- Do not call an image model at runtime.
- Do not use randomized colors, positions, font sizes, crops, or decorative elements.
- Do not allow per-user layout changes except text truncation and score-driven bar lengths.
- Use PNG as the canonical share artifact after the layout is approved. SVG may be emitted for debugging or editable inspection, but live SVG text can render differently across previewers and fonts.
- Repeated generation should be checked by comparing PNG SHA256 hashes for the same input JSON, asset files, renderer script, and font file.
- Run `scripts/self_check_render_determinism.ps1` after any change to `render-lock.json`, `render_share_card_png.ps1`, the pinned font, the fixture JSON, or the confirmed worktype images.

Do not hard-code score values in the renderer. Use values from `references/output-schema.md`: `scores.*.score`, `composite.score`, and `worktype.fit_score`.

For Chinese cards, populate the base `share_card` text fields in Chinese or provide optional `*_zh` fields. The renderer prefers Chinese worktype names from `worktype.serious_name_zh` and `worktype.share_name_zh`, with built-in Chinese fallbacks for the fixed registry.

## External Asset Production Brief

When creating or replacing the fixed worktype illustration set, use:

`references/asset-production/worktype-avatar-brief.md`

That brief is for external/manual image generation only. It is not used at runtime. Runtime card rendering must use only confirmed files from `assets/worktype-illustrations/manifest.json`.

## Text Template

```md
你的AI协作型人格是
{share_name_zh}
严肃类型：{serious_name_zh}

综合分：{composite}/100
匹配度：{fit_score}/100

五维分值：
问题界定：{problem_framing}/100
推理建模：{reasoning_modeling}/100
证据验证：{evidence_verification}/100
AI 编排：{ai_orchestration}/100
交付迭代：{delivery_iteration}/100

高光能力：
{superpower}

弱项提醒：
{comedy_failure_mode}

小字说明：
基于证据的 AI 协作摘要，不是 IQ、人格诊断或用人建议。
```


