#!/usr/bin/env python3
"""Extract repeatable evidence signals from Codex JSONL collaboration history."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DIMENSION_RULES = {
    "problem_framing": [
        "需求", "目标", "边界", "范围", "约束", "预期", "设计", "客观", "严肃", "中立",
        "固定", "不要", "不应该", "不是", "改为", "回退", "区分", "稳定", "漂移",
    ],
    "reasoning_modeling": [
        "抽象", "机制", "维度", "整合", "类型", "结构", "模型", "上层", "语义",
        "重叠", "全面", "最小", "必要", "拆解", "深刻", "skill化",
    ],
    "evidence_verification": [
        "自检", "验证", "测试", "确认", "看看", "客观", "量化", "分值", "评分",
        "哈希", "重复", "预览", "回退", "无误", "漏洞",
    ],
    "ai_orchestration": [
        "调用", "接管", "继续", "生成", "跑", "做", "用", "skill", "ACH", "CFR",
        "CCA", "模型", "协作", "对话", "历史记录", "产出",
    ],
    "delivery_iteration": [
        "图片", "路径", "输出", "布局", "字号", "贴图", "PNG", "SVG", "标准版",
        "脚本", "安装", "获取", "外化", "记录", "完成", "应用", "生成图",
    ],
}

CORRECTION_MARKERS = [
    "不", "不是", "不要", "不应该", "不够", "回退", "改为", "调整", "重叠",
    "看不到", "僵硬", "漂移", "漏洞", "还差", "重新", "换成",
]
VALIDATION_MARKERS = ["自检", "验证", "测试", "确认", "看看", "客观", "量化", "稳定", "一致", "哈希", "无误"]
DELIVERY_MARKERS = ["生成", "输出", "图片", "路径", "脚本", "文档", "skill", "完成", "应用", "安装", "获取"]
COMMAND_MARKERS = [
    "test", "pytest", "quick_validate", "self_check", "Get-FileHash", "git diff",
    "playwright", "render", "hash", "json.tool", "py_compile",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in {"input_text", "output_text", "text"}:
                parts.append(str(item.get("text", "")))
        return "\n".join(parts)
    return ""


def clean_text(text: str) -> str:
    text = text.strip()
    if text.startswith("<environment_context>") or text.startswith("<permissions instructions>"):
        return ""
    return re.sub(r"\s+", " ", text)


def clip(text: str, limit: int = 180) -> str:
    text = clean_text(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def source_files(manifest_path: Path) -> list[Path]:
    manifest = load_json(manifest_path)
    files = []
    for source in manifest.get("sources", []):
        path = Path(source.get("path_or_id", ""))
        if source.get("included") and path.suffix.lower() == ".jsonl" and path.exists():
            files.append(path)
    return files


def parse_arguments(raw: Any) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return raw
    if isinstance(raw, dict):
        return " ".join(str(raw.get(key, "")) for key in ("command", "cmd", "input", "path") if raw.get(key))
    return str(raw)


def add_sample(samples: dict[str, list[dict[str, str]]], dimension: str, sample: dict[str, str], limit: int) -> None:
    if len(samples[dimension]) >= limit:
        return
    if not sample["text"]:
        return
    if any(existing["text"] == sample["text"] for existing in samples[dimension]):
        return
    samples[dimension].append(sample)


def analyze(files: list[Path], sample_limit: int) -> dict[str, Any]:
    stats = Counter()
    tools = Counter()
    dimension_hits = Counter()
    samples: dict[str, list[dict[str, str]]] = defaultdict(list)
    sessions: dict[str, dict[str, Any]] = {}
    openers = Counter()

    for file_path in files:
        session_id = file_path.stem
        sessions.setdefault(session_id, {"path": str(file_path), "user_messages": 0, "tool_calls": 0})
        with file_path.open(encoding="utf-8-sig", errors="replace") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    stats["json_decode_errors"] += 1
                    continue
                payload = record.get("payload") or {}
                if record.get("type") == "session_meta" and isinstance(payload, dict):
                    session_id = payload.get("id") or session_id
                    sessions.setdefault(session_id, {"path": str(file_path), "user_messages": 0, "tool_calls": 0})
                    sessions[session_id]["started_at"] = payload.get("timestamp", record.get("timestamp", ""))
                    sessions[session_id]["cwd"] = payload.get("cwd", "")
                    continue
                if record.get("type") != "response_item" or not isinstance(payload, dict):
                    continue
                payload_type = payload.get("type")
                if payload_type == "message" and payload.get("role") == "user":
                    text = clean_text(text_from_content(payload.get("content")))
                    if not text:
                        continue
                    stats["user_messages"] += 1
                    sessions[session_id]["user_messages"] += 1
                    opener = re.split(r"[。！？!?\n]", text)[0][:44]
                    if opener:
                        openers[opener] += 1
                    if any(marker in text for marker in CORRECTION_MARKERS):
                        stats["user_correction_or_constraint_messages"] += 1
                    if any(marker in text for marker in VALIDATION_MARKERS):
                        stats["user_validation_messages"] += 1
                    if any(marker in text for marker in DELIVERY_MARKERS):
                        stats["user_delivery_messages"] += 1
                    sample = {
                        "session_id": session_id,
                        "path": str(file_path),
                        "line": str(line_number),
                        "timestamp": record.get("timestamp", ""),
                        "text": clip(text),
                    }
                    for dimension, keywords in DIMENSION_RULES.items():
                        hit_count = sum(1 for keyword in keywords if keyword in text)
                        if hit_count:
                            dimension_hits[dimension] += hit_count
                            add_sample(samples, dimension, sample, sample_limit)
                elif payload_type in {"function_call", "custom_tool_call"}:
                    name = payload.get("name") or payload.get("callable") or "unknown"
                    tools[name] += 1
                    stats["tool_calls"] += 1
                    sessions[session_id]["tool_calls"] += 1
                    args_text = parse_arguments(payload.get("arguments") or payload.get("input"))
                    if name == "apply_patch":
                        stats["patch_calls"] += 1
                    if any(marker.lower() in args_text.lower() for marker in COMMAND_MARKERS):
                        stats["verification_or_render_commands"] += 1

    return {
        "schema_version": 1,
        "source_file_count": len(files),
        "session_count": len(sessions),
        "stats": dict(stats),
        "tool_counts": dict(tools.most_common()),
        "dimension_keyword_hits": dict(dimension_hits),
        "dimension_samples": dict(samples),
        "top_user_openers": [{"text": text, "count": count} for text, count in openers.most_common(30)],
        "sessions": sessions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--sample-limit", default=12, type=int)
    args = parser.parse_args()

    result = analyze(source_files(args.manifest), args.sample_limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "source_file_count": result["source_file_count"], "session_count": result["session_count"], "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
