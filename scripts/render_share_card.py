#!/usr/bin/env python3
"""Render a standard AI collaboration worktype share card as SVG.

Runtime never calls image generation. It selects a confirmed image asset from
the worktype manifest when available and overlays deterministic text. If no
confirmed asset exists, it can use a deterministic vector placeholder for draft
previews.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import pathlib
import textwrap
from typing import Any, Dict, Iterable, List, Optional, Tuple


WIDTH = 1080
HEIGHT = 1350
SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "worktype-illustrations" / "manifest.json"
DEFAULT_SHARE_COPY = SKILL_DIR / "references" / "share-copy.json"

MODULES = {
    "card": {"x": 42, "y": 42, "w": 996, "h": 1266, "rx": 44},
    "image": {"x": 42, "y": 42, "w": 996, "h": 666, "rx": 44},
    "text": {"x": 66, "y": 728, "w": 548, "h": 552, "rx": 28},
    "scores": {"x": 650, "y": 728, "w": 364, "h": 552, "rx": 28},
}

FALLBACK_COPY_SPECS = {
    "tagline": {
        "label_zh": "寄语",
        "max_chars": 40,
        "target_min_chars": 24,
        "line_width": 17,
        "max_lines": 3,
        "font_size": 27,
    },
    "superpower": {
        "label_zh": "高光能力",
        "max_chars": 20,
        "target_min_chars": 12,
        "line_width": 20,
        "max_lines": 1,
        "font_size": 35,
    },
    "comedy_failure_mode": {
        "label_zh": "弱项提醒",
        "max_chars": 20,
        "target_min_chars": 12,
        "line_width": 20,
        "max_lines": 1,
        "font_size": 35,
    },
}

TYPE_STYLES = {
    "ai-systems-architect": {
        "accent": "#3B82F6",
        "accent2": "#22C55E",
        "dark": "#101828",
        "shape": "tower",
    },
    "prompt-air-traffic-controller": {
        "accent": "#06B6D4",
        "accent2": "#6366F1",
        "dark": "#101828",
        "shape": "routes",
    },
    "evidence-auditor": {
        "accent": "#F59E0B",
        "accent2": "#10B981",
        "dark": "#111827",
        "shape": "receipts",
    },
    "problem-architect": {
        "accent": "#8B5CF6",
        "accent2": "#14B8A6",
        "dark": "#111827",
        "shape": "maze",
    },
    "system-modeler": {
        "accent": "#0EA5E9",
        "accent2": "#A855F7",
        "dark": "#111827",
        "shape": "blocks",
    },
    "delivery-integrator": {
        "accent": "#EF4444",
        "accent2": "#F97316",
        "dark": "#111827",
        "shape": "forge",
    },
    "fast-ai-delegator": {
        "accent": "#F97316",
        "accent2": "#84CC16",
        "dark": "#111827",
        "shape": "launch",
    },
    "abstract-explorer": {
        "accent": "#7C3AED",
        "accent2": "#38BDF8",
        "dark": "#111827",
        "shape": "cloud",
    },
    "execution-accelerator": {
        "accent": "#22C55E",
        "accent2": "#0EA5E9",
        "dark": "#111827",
        "shape": "lane",
    },
    "ai-dependent-operator": {
        "accent": "#64748B",
        "accent2": "#94A3B8",
        "dark": "#111827",
        "shape": "autopilot",
    },
}

DIM_LABELS = [
    ("problem_framing", "问题界定"),
    ("reasoning_modeling", "推理建模"),
    ("evidence_verification", "证据验证"),
    ("ai_orchestration", "AI 编排"),
    ("delivery_iteration", "交付迭代"),
]

TYPE_LABELS_ZH = {
    "ai-systems-architect": ("工作流架构型", "赛博包工头"),
    "prompt-air-traffic-controller": ("输出调度型", "流水线督工"),
    "evidence-auditor": ("证据校验型", "赛博对账人"),
    "problem-architect": ("问题界定型", "边界判官"),
    "system-modeler": ("机制建构型", "抽象大师"),
    "delivery-integrator": ("交付封装型", "落地狠人"),
    "fast-ai-delegator": ("初稿驱动型", "初稿仙人"),
    "abstract-explorer": ("概念发散型", "脑洞永动机"),
    "execution-accelerator": ("执行推进型", "光速进度条"),
    "ai-dependent-operator": ("AI主导型", "智驾躺平哥"),
}


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def get_score(data: Dict[str, Any], key: str) -> int:
    try:
        return as_int(data["scores"][key]["score"])
    except Exception:
        return 0


def wrap_text(text: str, width: int) -> List[str]:
    text = " ".join(str(text or "").split())
    if not text:
        return []
    # Mixed Chinese/English text often wraps better by character count.
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return [text[i : i + width] for i in range(0, len(text), width)]
    return textwrap.wrap(text, width=width)


def share_value(share: Dict[str, Any], key: str, fallback: str) -> str:
    return str(share.get(f"{key}_zh") or share.get(key) or fallback)


def load_share_copy(path: pathlib.Path = DEFAULT_SHARE_COPY) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get_copy_spec(copybook: Dict[str, Any], key: str) -> Dict[str, Any]:
    spec = dict(FALLBACK_COPY_SPECS[key])
    configured = copybook.get("copy_specs", {}).get(key, {})
    if isinstance(configured, dict):
        spec.update({k: v for k, v in configured.items() if v not in (None, "")})
    for int_key in ("max_chars", "target_min_chars", "line_width", "max_lines", "font_size"):
        spec[int_key] = as_int(spec.get(int_key), FALLBACK_COPY_SPECS[key][int_key])
    return spec


def standard_share_text(copybook: Dict[str, Any], type_id: str, key: str, fallback: str) -> str:
    typed = copybook.get("type_copy", {}).get(type_id, {})
    if not isinstance(typed, dict):
        return fallback
    return str(typed.get(key) or fallback)


def standard_type_name(copybook: Dict[str, Any], type_id: str, key: str, fallback: str) -> str:
    typed = copybook.get("type_names", {}).get(type_id, {})
    if not isinstance(typed, dict):
        return fallback
    return str(typed.get(key) or fallback)


def limit_text(text: str, max_chars: int) -> str:
    normalized = " ".join(str(text or "").split())
    if max_chars <= 0 or len(normalized) <= max_chars:
        return normalized
    if max_chars == 1:
        return "…"
    return normalized[: max_chars - 1].rstrip() + "…"


def copy_lines(text: str, spec: Dict[str, Any]) -> List[str]:
    limited = limit_text(text, as_int(spec.get("max_chars"), 0))
    lines = wrap_text(limited, as_int(spec.get("line_width"), 18))
    return lines[: as_int(spec.get("max_lines"), 2)]


def svg_text_lines(
    lines: Iterable[str],
    x: int,
    y: int,
    size: int,
    color: str,
    weight: int = 500,
    gap: int = 1,
) -> str:
    out = []
    line_height = int(size * 1.32) + gap
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * line_height}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(line)}</text>'
        )
    return "\n".join(out)


def load_asset_manifest(path: pathlib.Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_asset_path(manifest: Dict[str, Any], manifest_path: pathlib.Path, entry: Dict[str, Any]) -> Optional[pathlib.Path]:
    file_value = entry.get("file") or entry.get("path")
    if not file_value:
        return None

    candidate = pathlib.Path(str(file_value))
    if candidate.is_absolute():
        return candidate

    asset_root = str(manifest.get("asset_root") or "").strip()
    candidate_posix = str(candidate).replace("\\", "/")
    root_posix = asset_root.replace("\\", "/")
    if root_posix and not (candidate_posix == root_posix or candidate_posix.startswith(root_posix + "/")):
        candidate = pathlib.Path(asset_root) / candidate

    candidates = [
        SKILL_DIR / candidate,
        manifest_path.parent / candidate,
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def select_confirmed_asset(
    type_id: str,
    manifest: Dict[str, Any],
    manifest_path: pathlib.Path,
) -> Tuple[Optional[pathlib.Path], str]:
    if not manifest:
        return None, "asset manifest not found"

    entry = manifest.get("types", {}).get(type_id)
    if not isinstance(entry, dict):
        return None, f"no manifest entry for {type_id}"

    status = str(entry.get("status") or "missing")
    if status != "confirmed":
        return None, f"asset status is {status}"

    asset_path = resolve_asset_path(manifest, manifest_path, entry)
    if not asset_path:
        return None, f"manifest entry for {type_id} has no file"
    if not asset_path.exists():
        return None, f"confirmed asset file is missing: {asset_path}"
    return asset_path, "confirmed"


def image_data_uri(path: pathlib.Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def placeholder_background_svg(style: Dict[str, str]) -> str:
    accent = style["accent"]
    accent2 = style["accent2"]
    dark = style["dark"]
    shape = style["shape"]
    decorative = []
    if shape == "routes":
        decorative.append(f'<path d="M130 260 C310 120 510 340 790 165" stroke="{accent}" stroke-width="10" fill="none" opacity="0.9"/>')
        decorative.append(f'<path d="M180 340 C420 210 610 430 900 250" stroke="{accent2}" stroke-width="8" fill="none" opacity="0.75"/>')
        for x, y in [(130, 260), (510, 340), (790, 165), (900, 250)]:
            decorative.append(f'<circle cx="{x}" cy="{y}" r="18" fill="white" opacity="0.95"/>')
    elif shape == "tower":
        decorative.append(f'<rect x="460" y="140" width="160" height="290" rx="20" fill="{accent}" opacity="0.95"/>')
        decorative.append(f'<path d="M330 430 L750 430 L850 620 L230 620 Z" fill="{accent2}" opacity="0.88"/>')
        decorative.append(f'<path d="M540 430 L500 760 M540 430 L580 760" stroke="{dark}" stroke-width="18" opacity="0.28"/>')
    elif shape == "receipts":
        for i, x in enumerate([230, 410, 590]):
            decorative.append(f'<rect x="{x}" y="{150+i*35}" width="220" height="310" rx="18" fill="white" opacity="0.82"/>')
            decorative.append(f'<path d="M{x+35} {220+i*35} H{x+185} M{x+35} {270+i*35} H{x+160} M{x+35} {320+i*35} H{x+190}" stroke="{accent}" stroke-width="10" opacity="0.75"/>')
    elif shape == "maze":
        for i in range(7):
            decorative.append(f'<rect x="{160+i*70}" y="{150+i*28}" width="{520-i*45}" height="{320-i*22}" rx="18" fill="none" stroke="{accent if i % 2 == 0 else accent2}" stroke-width="10" opacity="0.72"/>')
    elif shape == "blocks":
        for i, (x, y) in enumerate([(220, 180), (420, 125), (620, 210), (350, 350), (570, 390)]):
            decorative.append(f'<rect x="{x}" y="{y}" width="160" height="120" rx="18" fill="{accent if i % 2 == 0 else accent2}" opacity="0.86"/>')
            decorative.append(f'<line x1="{x+80}" y1="{y+120}" x2="{x+80}" y2="{y+175}" stroke="white" stroke-width="8" opacity="0.55"/>')
    elif shape == "forge":
        decorative.append(f'<path d="M220 430 C350 250 730 250 860 430 C740 570 350 570 220 430 Z" fill="{accent}" opacity="0.85"/>')
        decorative.append(f'<rect x="300" y="500" width="480" height="90" rx="20" fill="{dark}" opacity="0.65"/>')
        decorative.append(f'<path d="M475 130 L605 430 H345 Z" fill="{accent2}" opacity="0.9"/>')
    elif shape == "launch":
        decorative.append(f'<path d="M540 110 C650 260 650 460 540 620 C430 460 430 260 540 110 Z" fill="{accent}" opacity="0.9"/>')
        decorative.append(f'<path d="M480 610 L420 760 L540 700 L660 760 L600 610 Z" fill="{accent2}" opacity="0.88"/>')
    elif shape == "cloud":
        for x, y, r in [(300, 300, 95), (420, 235, 125), (570, 290, 115), (700, 330, 90)]:
            decorative.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{accent if x % 2 == 0 else accent2}" opacity="0.72"/>')
        decorative.append('<rect x="250" y="315" width="520" height="120" rx="60" fill="white" opacity="0.25"/>')
    elif shape == "lane":
        for i in range(6):
            decorative.append(f'<path d="M170 {180+i*70} H900" stroke="{accent if i % 2 == 0 else accent2}" stroke-width="20" opacity="0.65"/>')
        decorative.append(f'<rect x="720" y="210" width="160" height="260" rx="22" fill="{dark}" opacity="0.5"/>')
    else:
        decorative.append(f'<rect x="250" y="150" width="580" height="380" rx="55" fill="{accent}" opacity="0.45"/>')
        decorative.append(f'<circle cx="540" cy="340" r="160" fill="{accent2}" opacity="0.50"/>')

    return f"""
<g id="background" data-source="deterministic-placeholder">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#F8FAFC"/>
  <rect x="42" y="42" width="{WIDTH-84}" height="{HEIGHT-84}" rx="44" fill="white"/>
  <circle cx="940" cy="150" r="170" fill="{accent}" opacity="0.12"/>
  <circle cx="120" cy="1180" r="220" fill="{accent2}" opacity="0.13"/>
  <g opacity="0.95">
    {''.join(decorative)}
  </g>
  <rect x="42" y="705" width="996" height="603" fill="#FFFFFF" opacity="0.96" clip-path="url(#card-clip)"/>
  <rect x="66" y="728" width="548" height="552" rx="28" fill="#FFFFFF" opacity="0.93"/>
  <rect x="650" y="728" width="364" height="552" rx="28" fill="#FFFFFF" opacity="0.93"/>
</g>
"""


def asset_background_svg(style: Dict[str, str], asset_path: pathlib.Path) -> str:
    accent = style["accent"]
    accent2 = style["accent2"]
    card = MODULES["card"]
    image = MODULES["image"]
    text = MODULES["text"]
    scores = MODULES["scores"]
    uri = image_data_uri(asset_path)
    return f"""
<g id="background" data-source="confirmed-asset" data-asset="{esc(asset_path.name)}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#F8FAFC"/>
  <rect x="{card["x"]}" y="{card["y"]}" width="{card["w"]}" height="{card["h"]}" rx="{card["rx"]}" fill="white"/>
  <image x="{card["x"]}" y="{card["y"]}" width="{card["w"]}" height="{card["h"]}" preserveAspectRatio="xMidYMid slice" href="{uri}" opacity="0.16" clip-path="url(#card-clip)"/>
  <rect x="{card["x"]}" y="705" width="{card["w"]}" height="603" fill="#FFFFFF" opacity="0.96" clip-path="url(#card-clip)"/>
  <image x="{image["x"]}" y="{image["y"]}" width="{image["w"]}" height="{image["h"]}" preserveAspectRatio="xMidYMid slice" href="{uri}" clip-path="url(#image-module-clip)"/>
  <rect x="42" y="560" width="996" height="148" fill="url(#hero-scrim)" clip-path="url(#card-clip)"/>
  <rect x="{text["x"]}" y="{text["y"]}" width="{text["w"]}" height="{text["h"]}" rx="{text["rx"]}" fill="#FFFFFF" opacity="0.93"/>
  <rect x="{scores["x"]}" y="{scores["y"]}" width="{scores["w"]}" height="{scores["h"]}" rx="{scores["rx"]}" fill="#FFFFFF" opacity="0.93"/>
  <circle cx="940" cy="150" r="170" fill="{accent}" opacity="0.10"/>
  <circle cx="132" cy="1215" r="190" fill="{accent2}" opacity="0.08"/>
</g>
"""


def bar_svg(label: str, score: int, x: int, y: int, width: int, accent: str) -> str:
    score = max(0, min(100, int(score)))
    fill_w = round(width * score / 100)
    return f"""
<g>
  <text x="{x}" y="{y + 17}" font-size="25" font-weight="750" fill="#344054">{esc(label)}</text>
  <rect x="{x+128}" y="{y}" width="{width}" height="20" rx="10" fill="#EAECF0"/>
  <rect x="{x+128}" y="{y}" width="{fill_w}" height="20" rx="10" fill="{accent}"/>
  <text x="{x+128+width+16}" y="{y + 17}" font-size="27" font-weight="850" fill="#101828">{score}</text>
</g>
"""


def score_tile_svg(label: str, score: int, x: int, y: int, dark: str) -> str:
    return f"""
<g>
  <rect x="{x}" y="{y}" width="146" height="132" rx="22" fill="#F8FAFC"/>
  <text x="{x + 22}" y="{y + 50}" font-size="25" font-weight="800" fill="#667085">{esc(label)}</text>
  <text x="{x + 22}" y="{y + 116}" font-size="54" font-weight="900" fill="{dark}">{score}</text>
  <text x="{x + 94}" y="{y + 114}" font-size="22" font-weight="850" fill="#667085">/100</text>
</g>
"""


def render(
    data: Dict[str, Any],
    asset_path: Optional[pathlib.Path] = None,
    copybook: Optional[Dict[str, Any]] = None,
) -> str:
    worktype = data.get("worktype", {})
    share = data.get("share_card", {})
    subject = data.get("subject", {})
    type_id = worktype.get("type_id", "ai-systems-architect")
    copybook = copybook or load_share_copy()
    style = TYPE_STYLES.get(type_id, TYPE_STYLES["ai-systems-architect"])
    accent = style["accent"]
    dark = style["dark"]
    display_name = subject.get("display_name") or subject.get("id") or "Subject"
    fallback_serious_zh, fallback_share_zh = TYPE_LABELS_ZH.get(type_id, ("AI 协作工作型", "协作画像"))
    default_serious_zh = standard_type_name(copybook, type_id, "serious_name_zh", fallback_serious_zh)
    default_share_zh = standard_type_name(copybook, type_id, "share_name_zh", fallback_share_zh)
    serious = worktype.get("serious_name") or "AI Collaboration Worktype"
    serious_zh = worktype.get("serious_name_zh") or default_serious_zh
    share_name = worktype.get("share_name") or ""
    share_name_zh = worktype.get("share_name_zh") or default_share_zh
    composite = as_int(data.get("composite", {}).get("score"))
    fit = as_int(worktype.get("fit_score"))
    superpower = share_value(
        share,
        "superpower",
        standard_share_text(copybook, type_id, "superpower", "把模糊任务整理成更清楚的协作路径。"),
    )
    failure = share_value(
        share,
        "comedy_failure_mode",
        standard_share_text(copybook, type_id, "comedy_failure_mode", "可能把一个小提示词升级成一套工作流。"),
    )
    disclaimer = share_value(share, "tiny_disclaimer", "基于证据的 AI 协作摘要，不是 IQ、人格诊断或用人建议。")

    scores = [(label, get_score(data, key)) for key, label in DIM_LABELS]
    dimension_scores = scores
    background = asset_background_svg(style, asset_path) if asset_path else placeholder_background_svg(style)
    background_source = asset_path.name if asset_path else "deterministic-placeholder"
    text_module = MODULES["text"]
    score_module = MODULES["scores"]
    left_x = 106
    right_x = 684
    playful_name = share_name_zh or share_name or default_share_zh
    serious_name = serious_zh or serious or default_serious_zh

    text_parts = ['<g id="text-module" clip-path="url(#text-module-clip)">']
    text_parts.append(f'<text x="{left_x}" y="805" font-size="31" font-weight="850" fill="{accent}">你的AI协作型人格是</text>')
    text_parts.append(f'<text x="{left_x}" y="890" font-size="66" font-weight="900" fill="{dark}">{esc(playful_name)}</text>')
    text_parts.append(f'<text x="108" y="941" font-size="34" font-weight="850" fill="#475467">严肃类型：{esc(serious_name)}</text>')

    superpower_spec = get_copy_spec(copybook, "superpower")
    failure_spec = get_copy_spec(copybook, "comedy_failure_mode")

    text_parts.append(f'<text x="{left_x}" y="1022" font-size="28" font-weight="900" fill="{accent}">{esc(superpower_spec["label_zh"])}</text>')
    text_parts.append(svg_text_lines(copy_lines(superpower, superpower_spec), left_x, 1073, superpower_spec["font_size"], "#101828", 760))
    text_parts.append(f'<text x="{left_x}" y="1155" font-size="28" font-weight="900" fill="{accent}">{esc(failure_spec["label_zh"])}</text>')
    text_parts.append(svg_text_lines(copy_lines(failure, failure_spec), left_x, 1206, failure_spec["font_size"], "#344054", 720))
    text_parts.append(svg_text_lines(wrap_text(disclaimer, 34)[:2], left_x, 1261, 17, "#98A2B3", 600))
    text_parts.append("</g>")

    score_parts = ['<g id="score-module" clip-path="url(#score-module-clip)">']
    score_parts.append(score_tile_svg("综合分", composite, 684, 768, dark))
    score_parts.append(score_tile_svg("匹配度", fit, 848, 768, dark))
    score_parts.append(f'<text x="{right_x}" y="965" font-size="35" font-weight="900" fill="#344054">五维分值</text>')
    bar_y = 990
    for i, (label, score) in enumerate(dimension_scores):
        score_parts.append(bar_svg(label, score, right_x, bar_y + i * 56, 178, accent))
    score_parts.append("</g>")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<title>{esc(serious)} share card</title>
<!-- background-source: {esc(background_source)} -->
<defs>
  <style>
    text {{ font-family: Inter, Arial, 'Microsoft YaHei', sans-serif; letter-spacing: 0; }}
  </style>
  <clipPath id="card-clip">
    <rect x="{MODULES["card"]["x"]}" y="{MODULES["card"]["y"]}" width="{MODULES["card"]["w"]}" height="{MODULES["card"]["h"]}" rx="{MODULES["card"]["rx"]}"/>
  </clipPath>
  <clipPath id="image-module-clip">
    <rect x="{MODULES["image"]["x"]}" y="{MODULES["image"]["y"]}" width="{MODULES["image"]["w"]}" height="{MODULES["image"]["h"]}" rx="{MODULES["image"]["rx"]}"/>
  </clipPath>
  <clipPath id="text-module-clip">
    <rect x="{MODULES["text"]["x"]}" y="{MODULES["text"]["y"]}" width="{MODULES["text"]["w"]}" height="{MODULES["text"]["h"]}"/>
  </clipPath>
  <clipPath id="score-module-clip">
    <rect x="{MODULES["scores"]["x"]}" y="{MODULES["scores"]["y"]}" width="{MODULES["scores"]["w"]}" height="{MODULES["scores"]["h"]}"/>
  </clipPath>
  <linearGradient id="hero-scrim" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.93"/>
  </linearGradient>
</defs>
{background}
<g id="text-layer">
  {''.join(text_parts)}
  {''.join(score_parts)}
</g>
</svg>
"""


def demo_data() -> Dict[str, Any]:
    return {
        "subject": {"id": "demo", "display_name": "示例用户", "role_context": "AI collaboration"},
        "scores": {
            "problem_framing": {"score": 94},
            "reasoning_modeling": {"score": 90},
            "evidence_verification": {"score": 82},
            "ai_orchestration": {"score": 96},
            "delivery_iteration": {"score": 86},
        },
        "composite": {"score": 90, "band": "Exceptional"},
        "worktype": {
            "type_id": "ai-systems-architect",
            "serious_name": "AI Systems Architect",
            "serious_name_zh": "AI 系统架构型",
            "share_name": "Cyber Foreman",
            "share_name_zh": "工作流控制塔",
            "fit_score": 92,
        },
        "share_card": {
            "tagline": "把模糊的 AI 协作变成可治理的工作系统。",
            "superpower": "定义问题、调度 AI，并留下可复用的操作轨迹。",
            "comedy_failure_mode": "别人要一个提示词，他交付一座塔台和一本安全手册。",
            "tiny_disclaimer": "基于证据的 AI 协作摘要，不是 IQ、人格诊断或用人建议。",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a standard AI collaboration worktype SVG card.")
    parser.add_argument("input", nargs="?", help="Path to JSON result following output-schema.md")
    parser.add_argument("--out", required=True, help="Output SVG path")
    parser.add_argument("--demo", action="store_true", help="Render built-in demo data")
    parser.add_argument(
        "--asset-manifest",
        default=str(DEFAULT_MANIFEST),
        help="Path to worktype illustration manifest. Defaults to the skill asset manifest.",
    )
    parser.add_argument(
        "--share-copy",
        default=str(DEFAULT_SHARE_COPY),
        help="Path to standard worktype share-copy JSON. Defaults to the skill reference copybook.",
    )
    parser.add_argument(
        "--require-asset",
        action="store_true",
        help="Fail instead of using the deterministic placeholder when a confirmed asset is unavailable.",
    )
    args = parser.parse_args()

    if args.demo:
        data = demo_data()
    else:
        if not args.input:
            raise SystemExit("input JSON is required unless --demo is used")
        data = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8-sig"))

    manifest_path = pathlib.Path(args.asset_manifest)
    manifest = load_asset_manifest(manifest_path)
    copybook = load_share_copy(pathlib.Path(args.share_copy))
    type_id = data.get("worktype", {}).get("type_id", "ai-systems-architect")
    asset_path, asset_message = select_confirmed_asset(type_id, manifest, manifest_path)
    if args.require_asset and asset_path is None:
        raise SystemExit(f"confirmed asset required for {type_id}: {asset_message}")

    svg = render(data, asset_path=asset_path, copybook=copybook)
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
