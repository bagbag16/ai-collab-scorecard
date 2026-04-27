#!/usr/bin/env python3
"""Deterministically classify an AI collaboration worktype from score JSON."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DIMENSIONS = [
    "problem_framing",
    "reasoning_modeling",
    "evidence_verification",
    "ai_orchestration",
    "delivery_iteration",
]

MATCH_WEIGHTS = [1.10, 1.05, 1.00, 1.05, 1.00]
COMPOSITE_WEIGHTS = [22, 22, 20, 18, 18]

REGISTRY = {
    "ai-systems-architect": {
        "serious_name": "AI Systems Architect",
        "share_name": "Cyber Foreman",
        "prototype": [0.90, 0.88, 0.78, 0.88, 0.76],
    },
    "prompt-air-traffic-controller": {
        "serious_name": "AI Orchestration Controller",
        "share_name": "Prompt Air-Traffic Controller",
        "prototype": [0.78, 0.72, 0.72, 0.95, 0.72],
    },
    "evidence-auditor": {
        "serious_name": "Evidence Auditor",
        "share_name": "Receipt Collector",
        "prototype": [0.76, 0.72, 0.95, 0.72, 0.70],
    },
    "problem-architect": {
        "serious_name": "Problem Architect",
        "share_name": "Scope Boundary Patrol",
        "prototype": [0.95, 0.82, 0.72, 0.74, 0.68],
    },
    "system-modeler": {
        "serious_name": "System Modeler",
        "share_name": "Framework Construction Crew",
        "prototype": [0.78, 0.95, 0.72, 0.70, 0.66],
    },
    "delivery-integrator": {
        "serious_name": "Delivery Integrator",
        "share_name": "Workflow Blacksmith",
        "prototype": [0.76, 0.70, 0.74, 0.78, 0.95],
    },
    "fast-ai-delegator": {
        "serious_name": "Fast AI Delegator",
        "share_name": "Ship-It Summoner",
        "prototype": [0.62, 0.62, 0.48, 0.88, 0.82],
    },
    "abstract-explorer": {
        "serious_name": "Abstract Explorer",
        "share_name": "Cloud Castle Engineer",
        "prototype": [0.72, 0.90, 0.62, 0.66, 0.45],
    },
    "execution-accelerator": {
        "serious_name": "Execution Accelerator",
        "share_name": "Task Bulldozer",
        "prototype": [0.50, 0.55, 0.58, 0.72, 0.88],
    },
    "ai-dependent-operator": {
        "serious_name": "AI-Dependent Operator",
        "share_name": "Autopilot Enjoyer",
        "prototype": [0.35, 0.38, 0.32, 0.50, 0.52],
    },
}

SECONDARY_BY_DIMENSION = {
    "problem_framing": "problem-architect tendency",
    "reasoning_modeling": "system-modeler tendency",
    "evidence_verification": "evidence-auditor tendency",
    "ai_orchestration": "ai-orchestration tendency",
    "delivery_iteration": "delivery-integrator tendency",
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clamp_score(value: Any, key: str) -> int:
    if isinstance(value, dict):
        value = value.get("score")
    if value is None:
        raise ValueError(f"missing score for {key}")
    score = int(round(float(value)))
    return max(0, min(100, score))


def score_vector(data: dict[str, Any]) -> list[int]:
    scores = data.get("scores", {})
    return [clamp_score(scores.get(key), key) for key in DIMENSIONS]


def fit_score(subject: list[float], prototype: list[float]) -> int:
    weighted = sum(w * ((s - p) ** 2) for s, p, w in zip(subject, prototype, MATCH_WEIGHTS))
    distance = math.sqrt(weighted / sum(MATCH_WEIGHTS))
    return max(0, min(100, round(100 * (1 - distance / 0.75))))


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def evidence_sufficiency(data: dict[str, Any]) -> dict[str, Any]:
    """Return the evidence factor used to discount displayed worktype fit."""
    corpus = data.get("corpus", {}) or {}
    signal_summary = corpus.get("signal_summary") or data.get("signals") or {}
    evidence_confidence = str(corpus.get("evidence_confidence", "medium")).lower()
    source_count = as_int(corpus.get("source_count"))
    reasons: list[str] = []

    if signal_summary:
        session_count = as_int(signal_summary.get("session_count"))
        user_messages = as_int(signal_summary.get("user_messages"))
        corrections = as_int(
            signal_summary.get("correction_or_constraint_messages")
            or signal_summary.get("user_correction_or_constraint_messages")
        )
        validations = as_int(signal_summary.get("validation_messages") or signal_summary.get("user_validation_messages"))

        if user_messages >= 200 and session_count >= 20 and corrections >= 30:
            sample_level, sample_factor = "full", 1.00
        elif user_messages >= 80 and session_count >= 8 and corrections >= 10:
            sample_level, sample_factor = "standard", 0.92
        elif user_messages >= 20 and session_count >= 3:
            sample_level, sample_factor = "basic", 0.78
        elif user_messages >= 5 or source_count >= 1:
            sample_level, sample_factor = "thin", 0.62
        else:
            sample_level, sample_factor = "minimal", 0.45

        reasons.append(
            f"sample:{sample_level}; sessions={session_count}, user_messages={user_messages}, corrections={corrections}, validations={validations}"
        )
        if corrections == 0:
            sample_factor = min(sample_factor, 0.70)
            reasons.append("no visible user correction/constraint trace")
    else:
        if source_count >= 20:
            sample_level, sample_factor = "source-rich", 0.95
        elif source_count >= 8:
            sample_level, sample_factor = "source-standard", 0.88
        elif source_count >= 3:
            sample_level, sample_factor = "source-basic", 0.75
        elif source_count >= 1:
            sample_level, sample_factor = "source-thin", 0.60
        else:
            sample_level, sample_factor = "unknown", 0.50
        reasons.append(f"sample:{sample_level}; source_count={source_count}; no signal_summary")

    confidence_factor = {"high": 1.00, "medium": 0.92, "low": 0.70}.get(evidence_confidence, 0.85)
    reasons.append(f"evidence_confidence:{evidence_confidence}")

    factor = min(sample_factor, confidence_factor)
    if factor >= 0.95:
        adjusted_confidence = "high"
    elif factor >= 0.75:
        adjusted_confidence = "medium"
    else:
        adjusted_confidence = "low"

    return {
        "factor": round(factor, 2),
        "sample_level": sample_level,
        "classification_confidence": adjusted_confidence,
        "reasons": reasons,
    }


def composite(scores: list[int]) -> int:
    return round(sum(score * weight for score, weight in zip(scores, COMPOSITE_WEIGHTS)) / 100)


def composite_band(score: int) -> str:
    if score >= 90:
        return "Exceptional"
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Solid"
    if score >= 50:
        return "Developing"
    return "Fragile or Insufficient"


def risk_modifiers(normalized: list[float], data: dict[str, Any]) -> list[str]:
    p, r, e, a, d = normalized
    risks: list[str] = []
    if r >= 0.82 and d <= 0.68:
        risks.append("abstraction-outpaces-landing")
    if a >= 0.80 and e <= 0.62:
        risks.append("fast-delegation-risk")
    if p >= 0.82 and d <= 0.72:
        risks.append("scope-expansion-risk")
    if e <= 0.58 and composite([round(x * 100) for x in normalized]) >= 70:
        risks.append("verification-gap")
    signals = data.get("signals", {})
    if signals.get("human_steering_unclear") or data.get("worktype", {}).get("human_steering_unclear"):
        risks.append("human-steering-unclear")
    if d == min(normalized) and d < 0.65:
        risks.append("delivery-bottleneck")
    if all(x >= 0.76 for x in normalized):
        risks.append("balanced-high-performer")
    return risks[:2]


def secondary_tendency(normalized: list[float], primary_type: str) -> str:
    prototype = REGISTRY[primary_type]["prototype"]
    residuals = [score - base for score, base in zip(normalized, prototype)]
    index = max(range(len(residuals)), key=residuals.__getitem__)
    if residuals[index] <= 0.10:
        return "balanced within primary type"
    return SECONDARY_BY_DIMENSION[DIMENSIONS[index]]


def load_copy_defaults() -> dict[str, Any]:
    path = skill_dir() / "references" / "share-copy.json"
    return load_json(path)


def classify(data: dict[str, Any], fill_share_copy: bool = True) -> dict[str, Any]:
    raw_scores = score_vector(data)
    normalized = [score / 100 for score in raw_scores]
    raw_all_fits = {
        type_id: fit_score(normalized, spec["prototype"])
        for type_id, spec in REGISTRY.items()
    }
    evidence_fit = evidence_sufficiency(data)
    factor = float(evidence_fit["factor"])
    all_fits = {
        type_id: max(0, min(100, round(raw_fit * factor)))
        for type_id, raw_fit in raw_all_fits.items()
    }
    ranked = sorted(raw_all_fits.items(), key=lambda item: (-item[1], item[0]))
    primary_type, primary_raw_fit = ranked[0]
    second_type, second_raw_fit = ranked[1]
    primary_fit = all_fits[primary_type]

    copy_defaults = load_copy_defaults()
    type_names = copy_defaults.get("type_names", {}).get(primary_type, {})
    type_copy = copy_defaults.get("type_copy", {}).get(primary_type, {})
    registry = REGISTRY[primary_type]

    worktype = {
        "type_id": primary_type,
        "serious_name": registry["serious_name"],
        "serious_name_zh": type_names.get("serious_name_zh", ""),
        "share_name": registry["share_name"],
        "share_name_zh": type_names.get("share_name_zh", ""),
        "fit_score": primary_fit,
        "prototype_fit_score": primary_raw_fit,
        "evidence_sufficiency": evidence_fit,
        "secondary_tendency": secondary_tendency(normalized, primary_type),
        "risk_modifiers": risk_modifiers(normalized, data),
        "classification_confidence": evidence_fit["classification_confidence"],
        "all_fit_scores": all_fits,
        "all_prototype_fit_scores": raw_all_fits,
    }

    if primary_raw_fit - second_raw_fit < 5:
        worktype["hybrid_type_ids"] = [primary_type, second_type]

    result = dict(data)
    result["worktype"] = worktype
    result.setdefault("composite", {})
    result["composite"]["score"] = composite(raw_scores)
    result["composite"]["band"] = composite_band(result["composite"]["score"])

    if fill_share_copy:
        share_card = dict(result.get("share_card", {}))
        share_card.setdefault("superpower", type_copy.get("superpower", ""))
        share_card.setdefault("comedy_failure_mode", type_copy.get("comedy_failure_mode", ""))
        share_card.setdefault(
            "tiny_disclaimer",
            "Evidence-based AI collaboration summary. Not IQ, personality, or hiring advice.",
        )
        result["share_card"] = share_card

    if result.get("corpus", {}).get("evidence_confidence") == "low":
        result.setdefault("limits", [])
        result["limits"].append("Low corpus confidence: worktype is tentative and displayed fit_score has been reduced for evidence sufficiency.")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--no-share-copy", action="store_true")
    args = parser.parse_args()

    data = load_json(args.input_json)
    result = classify(data, fill_share_copy=not args.no_share_copy)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
