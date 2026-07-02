from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from main import app
from metrics import score_case


ROOT = Path(__file__).resolve().parent


def parse_sse(text: str) -> list[tuple[str, dict[str, Any]]]:
    events: list[tuple[str, dict[str, Any]]] = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        event_name = ""
        data: dict[str, Any] = {}
        for line in block.splitlines():
            if line.startswith("event:"):
                event_name = line[6:].strip()
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
        if event_name:
            events.append((event_name, data))
    return events


def final_answer_for(client: TestClient, case: dict[str, Any], variant: str) -> dict[str, Any]:
    response = client.post(
        "/api/chat/stream",
        json={"character_id": case["character_id"], "message": case["prompt"], "history": [], "variant": variant},
    )
    response.raise_for_status()
    events = parse_sse(response.text)
    final = [data for name, data in events if name == "final"][-1]
    return final


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if not total:
        return {}
    def avg(key: str) -> float | None:
        values = [row[key] for row in rows if row.get(key) is not None]
        return round(sum(values) / len(values), 3) if values else None
    return {
        "total_cases": total,
        "hallucination_rate": round(sum(1 for row in rows if row["hallucinated"]) / total, 3),
        "refusal_accuracy": avg("refusal_score"),
        "persona_consistency": avg("persona_score"),
        "expected_fact_score": avg("expected_fact_score"),
        "retrieval_precision_at_4": avg("retrieval_precision_at_4"),
        "citation_faithfulness": avg("citation_faithfulness"),
        "mean_grounding_confidence": avg("grounding_confidence"),
        "mean_latency_ms": avg("total_ms"),
    }


def run_evaluation(cases_path: Path, variants: list[str], limit: int = 0) -> dict[str, Any]:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    if limit > 0:
        cases = cases[:limit]
    results: dict[str, Any] = {"variants": {}, "cases_path": str(cases_path)}
    with TestClient(app) as client:
        for variant in variants:
            rows = []
            for case in cases:
                final = final_answer_for(client, case, variant)
                scored = score_case(case, final.get("answer", ""), final.get("citations", []))
                timings = final.get("timings_ms", {}) or {}
                rows.append({
                    **scored,
                    "variant": variant,
                    "prompt": case.get("prompt"),
                    "mode": final.get("mode"),
                    "route_source": final.get("route_source"),
                    "fallback_used": final.get("fallback_used"),
                    "citation_count": len(final.get("citations", [])),
                    "grounding_confidence": final.get("grounding_confidence"),
                    "total_ms": timings.get("total_ms"),
                    "answer_preview": final.get("answer", "")[:220],
                })
            results["variants"][variant] = {"summary": summarize(rows), "rows": rows}
    return results


def write_csv(results: dict[str, Any], csv_path: Path) -> None:
    rows = [row for variant in results["variants"].values() for row in variant["rows"]]
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run historical hallucination benchmark.")
    parser.add_argument("--cases", default=str(ROOT / "eval_cases.json"))
    parser.add_argument("--out", default=str(ROOT / "benchmark_results.json"))
    parser.add_argument("--csv", default=str(ROOT / "benchmark_results.csv"))
    parser.add_argument("--variants", default="rag,non_rag")
    parser.add_argument("--limit", type=int, default=0, help="Evaluate only the first N cases. Use 0 for all cases.")
    args = parser.parse_args()

    results = run_evaluation(Path(args.cases), [item.strip() for item in args.variants.split(",") if item.strip()], args.limit)
    out_path = Path(args.out)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(results, Path(args.csv))
    print(json.dumps({variant: data["summary"] for variant, data in results["variants"].items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
