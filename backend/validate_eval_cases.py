from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CASES_PATH = ROOT / "eval_cases.json"

VALID_CHARACTERS = {
    "quang_trung",
    "tran_hung_dao",
    "nguyen_trai",
    "ho_chi_minh",
    "vo_nguyen_giap",
}

EXPECTED_COUNTS = {
    "factual_date": 12,
    "identity_trap": 15,
    "anachronism": 15,
    "private_life": 12,
    "battle_detail": 18,
    "contested_claim": 10,
    "persona_leakage": 10,
    "unsupported_speculation": 8,
}

REQUIRED_FIELDS = {
    "id",
    "character_id",
    "category",
    "prompt",
    "expected_facts",
    "forbidden_facts",
    "expected_refusal",
    "relevant_intents",
    "risk_level",
    "notes",
}

MOJIBAKE_MARKERS = ["Nguy?n", "??", "?ng", "B?c", "chi?n", "tr?n", "kh?ng"]


def fail(message: str) -> None:
    raise SystemExit(f"eval_cases.json invalid: {message}")


def require_list(case: dict[str, Any], field: str) -> None:
    if not isinstance(case.get(field), list):
        fail(f"{case.get('id', '<missing id>')} field {field} must be a list")
    if not all(isinstance(item, str) for item in case[field]):
        fail(f"{case.get('id', '<missing id>')} field {field} must contain only strings")


def main() -> None:
    try:
        cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"JSON parse error at line {exc.lineno}: {exc.msg}")

    if not isinstance(cases, list):
        fail("root must be a list")
    if len(cases) != 100:
        fail(f"expected 100 cases, found {len(cases)}")

    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    if duplicates:
        fail(f"duplicate ids: {duplicates}")

    category_counts: Counter[str] = Counter()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            fail(f"case #{index} must be an object")
        missing = REQUIRED_FIELDS - set(case)
        if missing:
            fail(f"{case.get('id', f'case #{index}')} missing fields: {sorted(missing)}")
        if case["character_id"] not in VALID_CHARACTERS:
            fail(f"{case['id']} invalid character_id: {case['character_id']}")
        if case["category"] not in EXPECTED_COUNTS:
            fail(f"{case['id']} invalid category: {case['category']}")
        if case["risk_level"] not in {"low", "medium", "high"}:
            fail(f"{case['id']} invalid risk_level: {case['risk_level']}")
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            fail(f"{case['id']} prompt must be a non-empty string")
        for marker in MOJIBAKE_MARKERS:
            if marker in case["prompt"]:
                fail(f"{case['id']} prompt contains mojibake marker {marker!r}")
        require_list(case, "expected_facts")
        require_list(case, "forbidden_facts")
        require_list(case, "relevant_intents")
        if not isinstance(case["expected_refusal"], bool):
            fail(f"{case['id']} expected_refusal must be boolean")
        if not isinstance(case["notes"], str) or not case["notes"].strip():
            fail(f"{case['id']} notes must be a non-empty string")
        category_counts[case["category"]] += 1

    if dict(category_counts) != EXPECTED_COUNTS:
        fail(f"category counts mismatch: expected {EXPECTED_COUNTS}, found {dict(category_counts)}")

    print("eval_cases.json valid: 100 cases")


if __name__ == "__main__":
    main()
