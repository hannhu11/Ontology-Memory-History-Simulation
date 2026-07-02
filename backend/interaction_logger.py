from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent / "logs"
INTERACTION_LOG = LOG_DIR / "interactions.jsonl"
FEEDBACK_LOG = LOG_DIR / "feedback.jsonl"


def anonymous_session_id(raw: str) -> str:
    value = raw or "anonymous"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **payload}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_interaction(payload: dict[str, Any]) -> None:
    safe_payload = dict(payload)
    if "session_id" in safe_payload:
        safe_payload["session_id"] = anonymous_session_id(str(safe_payload["session_id"]))
    append_jsonl(INTERACTION_LOG, safe_payload)


def log_feedback(payload: dict[str, Any]) -> None:
    safe_payload = dict(payload)
    if "session_id" in safe_payload:
        safe_payload["session_id"] = anonymous_session_id(str(safe_payload["session_id"]))
    append_jsonl(FEEDBACK_LOG, safe_payload)


def read_jsonl(path: Path, limit: int = 500) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    return [json.loads(line) for line in lines if line.strip()]


def metrics_summary() -> dict[str, Any]:
    interactions = read_jsonl(INTERACTION_LOG)
    feedback = read_jsonl(FEEDBACK_LOG)
    if not interactions:
        return {"interaction_count": 0, "feedback_count": len(feedback)}
    total = len(interactions)
    fallback_count = sum(1 for item in interactions if item.get("fallback_used"))
    citation_counts = [int(item.get("citation_count", 0) or 0) for item in interactions]
    confidences = [int(item.get("grounding_confidence", 0) or 0) for item in interactions]
    latencies = [int((item.get("timings_ms") or {}).get("total_ms", 0) or 0) for item in interactions]
    return {
        "interaction_count": total,
        "feedback_count": len(feedback),
        "fallback_rate": round(fallback_count / total, 3),
        "mean_citation_count": round(sum(citation_counts) / total, 3),
        "mean_grounding_confidence": round(sum(confidences) / total, 3),
        "mean_latency_ms": round(sum(latencies) / total, 3),
        "recent_feedback": feedback[-20:],
    }
