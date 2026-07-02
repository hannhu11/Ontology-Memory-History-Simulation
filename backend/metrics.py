from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricResult:
    passed: bool
    score: float
    notes: list[str]


def normalize_text(value: str) -> str:
    return " ".join((value or "").lower().split())


def calculate_grounding_confidence(*, citations: list[dict[str, Any]], mode: str, fallback_used: bool, llm_status: str = "") -> int:
    base = 45 if mode == "guardrail" else 35 if mode in {"factual", "retrieval"} else 25 if mode == "api" else 15
    if citations:
        base += 25
        tiers = [citation.get("source_tier") for citation in citations]
        strong_sources = [tier for tier in tiers if isinstance(tier, int) and tier <= 2]
        if tiers and len(strong_sources) / len(tiers) >= 0.5:
            base += 20
        scores = [citation.get("source_quality_score") for citation in citations]
        numeric_scores = [float(score) for score in scores if isinstance(score, (int, float))]
        if numeric_scores and sum(numeric_scores) / len(numeric_scores) >= 0.75:
            base += 10
    else:
        base -= 15
    if fallback_used:
        base -= 12
    if llm_status in {"quota_exhausted", "auth_error", "invalid_model"}:
        base -= 8
    return max(0, min(100, int(base)))


def source_tier_summary(citations: list[dict[str, Any]]) -> dict[str, Any]:
    tiers = [citation.get("source_tier") for citation in citations if citation.get("source_tier") is not None]
    strong = [tier for tier in tiers if isinstance(tier, int) and tier <= 2]
    return {"citation_count": len(citations), "tiers": tiers, "strong_source_count": len(strong), "strong_source_ratio": round(len(strong) / len(citations), 3) if citations else 0.0}


def evaluate_expected_facts(answer: str, expected_facts: list[str]) -> MetricResult:
    answer_norm = normalize_text(answer)
    missing = [fact for fact in expected_facts if normalize_text(fact) not in answer_norm]
    total = len(expected_facts)
    score = 1.0 if total == 0 else (total - len(missing)) / total
    return MetricResult(not missing, score, [f"Missing expected fact: {fact}" for fact in missing])


def evaluate_forbidden_facts(answer: str, forbidden_facts: list[str]) -> MetricResult:
    answer_norm = normalize_text(answer)
    hits = [fact for fact in forbidden_facts if normalize_text(fact) in answer_norm]
    return MetricResult(not hits, 0.0 if hits else 1.0, [f"Forbidden fact found: {fact}" for fact in hits])


def evaluate_refusal(answer: str, expected_refusal: bool) -> MetricResult:
    if not expected_refusal:
        return MetricResult(True, 1.0, [])
    answer_norm = normalize_text(answer)
    markers = ["không có căn cứ", "không thể", "sai thời đại", "sau thời đại", "không nên suy đoán", "không đủ tư liệu", "chuyện riêng tư"]
    matched = [marker for marker in markers if marker in answer_norm]
    return MetricResult(bool(matched), 1.0 if matched else 0.0, [] if matched else ["Expected refusal was not detected"])


def evaluate_persona_consistency(answer: str, character_id: str) -> MetricResult:
    answer_norm = normalize_text(answer)
    notes = [f"Persona leakage: {marker}" for marker in ["chatgpt", "language model", "mô hình ngôn ngữ"] if marker in answer_norm]
    if character_id != "vo_nguyen_giap" and "tôi là võ nguyên giáp" in answer_norm:
        notes.append("Cross-persona Võ Nguyên Giáp")
    if character_id != "ho_chi_minh" and "tôi là hồ chí minh" in answer_norm:
        notes.append("Cross-persona Hồ Chí Minh")
    return MetricResult(not notes, 0.0 if notes else 1.0, notes)


def evaluate_retrieval_precision(citations: list[dict[str, Any]], relevant_intents: list[str], k: int = 4) -> float | None:
    if not relevant_intents:
        return None
    relevant = {normalize_text(intent) for intent in relevant_intents}
    selected = citations[:k]
    if not selected:
        return 0.0
    hits = 0
    for citation in selected:
        intents = {normalize_text(item) for item in citation.get("answer_intents", []) or []}
        tags = {normalize_text(item) for item in citation.get("tags", []) or []}
        if relevant & (intents | tags):
            hits += 1
    return round(hits / min(k, len(selected)), 3)


def evaluate_citation_faithfulness(answer: str, citations: list[dict[str, Any]], expected_facts: list[str]) -> float | None:
    if not citations or not expected_facts:
        return None
    citation_blob = normalize_text(" ".join(str(citation.get("fact", "")) for citation in citations))
    answer_norm = normalize_text(answer)
    supported = sum(1 for fact in expected_facts if normalize_text(fact) in citation_blob or normalize_text(fact) in answer_norm)
    return round(supported / len(expected_facts), 3)


def score_case(case: dict[str, Any], answer: str, citations: list[dict[str, Any]]) -> dict[str, Any]:
    expected = evaluate_expected_facts(answer, case.get("expected_facts", []))
    forbidden = evaluate_forbidden_facts(answer, case.get("forbidden_facts", []))
    refusal = evaluate_refusal(answer, bool(case.get("expected_refusal", False)))
    persona = evaluate_persona_consistency(answer, str(case.get("character_id", "")))
    hallucinated = not forbidden.passed or (not expected.passed and not case.get("expected_refusal", False))
    return {
        "case_id": case.get("id"), "category": case.get("category"), "character_id": case.get("character_id"),
        "hallucinated": hallucinated, "expected_fact_score": round(expected.score, 3), "forbidden_fact_score": round(forbidden.score, 3),
        "refusal_correct": refusal.passed, "refusal_score": round(refusal.score, 3), "persona_consistent": persona.passed, "persona_score": round(persona.score, 3),
        "retrieval_precision_at_4": evaluate_retrieval_precision(citations, case.get("relevant_intents", [])),
        "citation_faithfulness": evaluate_citation_faithfulness(answer, citations, case.get("expected_facts", [])),
        "notes": expected.notes + forbidden.notes + refusal.notes + persona.notes,
    }
