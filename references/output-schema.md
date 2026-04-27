# Output Schema

Use this schema when the result should be machine-readable, reusable, or used to render a share card.

All score fields are integers from `0` to `100`.

```json
{
  "schema_version": 1,
  "subject": {
    "id": "string",
    "display_name": "string",
    "role_context": "string"
  },
  "corpus": {
    "time_window": {
      "start": "YYYY-MM-DD",
      "end": "YYYY-MM-DD"
    },
    "source_count": 0,
    "manifest_id": "string",
    "manifest_sha256": "string",
    "evidence_confidence": "low|medium|high"
  },
  "scores": {
    "problem_framing": {
      "score": 0,
      "confidence": "low|medium|high",
      "readout": "string",
      "evidence": ["string"]
    },
    "reasoning_modeling": {
      "score": 0,
      "confidence": "low|medium|high",
      "readout": "string",
      "evidence": ["string"]
    },
    "evidence_verification": {
      "score": 0,
      "confidence": "low|medium|high",
      "readout": "string",
      "evidence": ["string"]
    },
    "ai_orchestration": {
      "score": 0,
      "confidence": "low|medium|high",
      "readout": "string",
      "evidence": ["string"]
    },
    "delivery_iteration": {
      "score": 0,
      "confidence": "low|medium|high",
      "readout": "string",
      "evidence": ["string"]
    }
  },
  "composite": {
    "score": 0,
    "band": "Fragile or Insufficient|Developing|Solid|Strong|Exceptional"
  },
  "scoring_breakdown": {
    "problem_framing": {
      "core_behavior": {"A": 0, "B": 0, "C": 0, "subtotal": 0},
      "cross_task_consistency": 0,
      "human_ownership": 0,
      "difficulty_transfer": 0,
      "counterexample_adjustment": 0,
      "raw_total": 0,
      "caps_applied": ["string"],
      "final_score": 0,
      "confidence": "low|medium|high"
    }
  },
  "worktype": {
    "type_id": "string",
    "serious_name": "string",
    "serious_name_zh": "string",
    "share_name": "string",
    "share_name_zh": "string",
    "fit_score": 0,
    "prototype_fit_score": 0,
    "evidence_sufficiency": {
      "factor": 1.0,
      "sample_level": "minimal|thin|basic|standard|full|source-thin|source-basic|source-standard|source-rich|unknown",
      "classification_confidence": "low|medium|high",
      "reasons": ["string"]
    },
    "secondary_tendency": "string",
    "risk_modifiers": ["string"],
    "classification_confidence": "low|medium|high",
    "all_fit_scores": {
      "ai-systems-architect": 0,
      "prompt-air-traffic-controller": 0,
      "evidence-auditor": 0,
      "problem-architect": 0,
      "system-modeler": 0,
      "delivery-integrator": 0,
      "fast-ai-delegator": 0,
      "abstract-explorer": 0,
      "execution-accelerator": 0,
      "ai-dependent-operator": 0
    },
    "all_prototype_fit_scores": {
      "ai-systems-architect": 0,
      "prompt-air-traffic-controller": 0,
      "evidence-auditor": 0,
      "problem-architect": 0,
      "system-modeler": 0,
      "delivery-integrator": 0,
      "fast-ai-delegator": 0,
      "abstract-explorer": 0,
      "execution-accelerator": 0,
      "ai-dependent-operator": 0
    }
  },
  "share_card": {
    "tagline": "string (optional, retained for backward compatibility; ignored by the standard image renderer)",
    "superpower": "string",
    "comedy_failure_mode": "string",
    "best_ai_setup": "string",
    "tiny_disclaimer": "Evidence-based AI collaboration summary. Not IQ, personality, or hiring advice."
  },
  "limits": ["string"]
}
```

## Required For Rendering

The standard share-card renderer requires:

- `subject.display_name`
- `scores.*.score`
- `composite.score`
- `worktype.type_id`
- `worktype.serious_name`
- `worktype.share_name`
- `worktype.fit_score`
- `share_card.superpower`
- `share_card.comedy_failure_mode`

Chinese fields are optional but should be filled for Chinese reports.

Use `references/setup-and-data-sources.md` and `references/sampling-protocol.md` to build `corpus.manifest_id`, `corpus.manifest_sha256`, `corpus.source_count`, and `corpus.evidence_confidence`. Use `references/evidence-abstraction-pipeline.md` to map raw records into dimension evidence. Use `scripts/classify_worktype.py` to fill `worktype` deterministically after the five dimension scores are finalized.

`worktype.fit_score` is the evidence-adjusted match score used on the share card. `worktype.prototype_fit_score` is the raw five-vector similarity to the selected prototype. When sample size is small or corpus confidence is low, keep the type but reduce `fit_score` through `worktype.evidence_sufficiency.factor`.

For Chinese share-card rendering, keep score fields numeric and populate `share_card.superpower` and `share_card.comedy_failure_mode` in Chinese, or provide optional `superpower_zh` and `comedy_failure_mode_zh` fields. The renderer must read scores from this JSON rather than hard-code display values. `tagline` / `tagline_zh` may be present in older outputs, but the standard image renderer ignores it.

When rendering the standard Chinese image card, the renderer enforces the copy limits in `references/share-copy.json`: `superpower` max `20` chars and `comedy_failure_mode` max `20` chars. Write personalized overrides as concise, high-density short lines rather than padded explanations.
