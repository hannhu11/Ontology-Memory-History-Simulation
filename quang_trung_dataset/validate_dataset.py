import json
import re
import sys
import unicodedata
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "quang_trung_profile.json"
KNOWLEDGE_PATH = BASE_DIR / "quang_trung_knowledge.jsonl"

REQUIRED_PROFILE_METADATA = {
    "name",
    "full_name",
    "aliases",
    "birth_year",
    "death_year",
    "era",
    "personality_traits",
    "tone_of_voice",
    "system_prompt_blueprint",
}

REQUIRED_CHUNK_FIELDS = {
    "char_id",
    "chunk_id",
    "claim_status",
    "source_quality",
    "source_title",
    "source_year",
    "source_type",
    "source_url",
    "text",
    "fact",
    "topic_title",
    "tags",
    "answer_intents",
    "canonical_questions",
    "tag_blob",
}

FORBIDDEN_UNACCENTED_PHRASES = (
    "Nguyen Hue",
    "Tay Son",
    "Nghe An",
    "Phu Xuan",
    "Thang Long",
    "Gia Dinh",
    "My Tho",
    "Dien Bien Phu",
    "Ton Si Nghi",
    "Le Chieu Thong",
    "Rach Gam",
    "Xoai Mut",
    "Ngoc Hoi",
    "Dong Da",
)

FORBIDDEN_CHARACTER_TERMS = (
    "nguồn",
    "truy xuất",
    "guardrail",
    "dataset",
    "api",
    "người học",
    "mô hình",
    "citation",
    "chunk",
)

VALID_CLAIM_STATUS = {"established", "contested", "interpretive"}
REQUIRED_INTENTS = {
    "capital_city",
    "administration",
    "coinage",
    "education",
    "agriculture",
    "scholars",
    "micro_tactics",
    "anachronism",
}


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\wÀ-ỹ]+\b", text, flags=re.UNICODE))


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d")


def fail(message: str) -> None:
    raise AssertionError(message)


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                fail(f"{path.name}:{line_number} is not valid JSON: {exc}")
    return records


def validate_profile() -> dict:
    if not PROFILE_PATH.exists():
        fail(f"Missing {PROFILE_PATH}")
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if profile.get("character_id") != "quang_trung":
        fail("profile.character_id must be quang_trung")

    metadata = profile.get("character_metadata")
    if not isinstance(metadata, dict):
        fail("profile.character_metadata must be an object")
    missing = REQUIRED_PROFILE_METADATA - set(metadata)
    if missing:
        fail(f"profile.character_metadata missing fields: {sorted(missing)}")
    if metadata["birth_year"] != 1753 or metadata["death_year"] != 1792:
        fail("Quang Trung birth/death years must be 1753/1792")

    dialogues = profile.get("sample_dialogues")
    if not isinstance(dialogues, list) or len(dialogues) < 20:
        fail("profile.sample_dialogues must contain at least 20 examples")
    ids = [item.get("example_id") for item in dialogues]
    if len(ids) != len(set(ids)):
        fail("Duplicate sample_dialogues example_id values")
    for item in dialogues:
        if not item.get("user_query") or not item.get("character_response"):
            fail(f"Dialogue {item.get('example_id')} is missing query/response")
        response = item["character_response"]
        if "Quang Trung" in response or "Nguyễn Huệ" in response or "Nguyen Hue" in response:
            fail(f"Dialogue {item.get('example_id')} response must use first-person voice, not self-name")
        if "ta" not in response.lower():
            fail(f"Dialogue {item.get('example_id')} response should include first-person pronoun 'ta'")
        normalized_response = normalize(response)
        for term in FORBIDDEN_CHARACTER_TERMS:
            if normalize(term) in normalized_response:
                fail(f"Dialogue {item.get('example_id')} contains character-forbidden term: {term}")
        for phrase in FORBIDDEN_UNACCENTED_PHRASES:
            if phrase in item["user_query"] or phrase in response:
                fail(f"Dialogue {item.get('example_id')} contains unaccented phrase: {phrase}")
    return profile


def validate_knowledge() -> list[dict]:
    if not KNOWLEDGE_PATH.exists():
        fail(f"Missing {KNOWLEDGE_PATH}")
    records = load_jsonl(KNOWLEDGE_PATH)
    if len(records) < 90:
        fail("knowledge file must contain at least 90 chunks")

    seen_ids = set()
    all_text = normalize("\n".join(record.get("text", "") for record in records))
    all_intents = set()
    for index, record in enumerate(records, 1):
        missing = REQUIRED_CHUNK_FIELDS - set(record)
        if missing:
            fail(f"Chunk line {index} missing fields: {sorted(missing)}")
        if record["char_id"] != "quang_trung":
            fail(f"Chunk {record['chunk_id']} has wrong char_id")
        if record["chunk_id"] in seen_ids:
            fail(f"Duplicate chunk_id: {record['chunk_id']}")
        seen_ids.add(record["chunk_id"])
        if not str(record["source_url"]).startswith("https://"):
            fail(f"Chunk {record['chunk_id']} has invalid source_url")
        if not isinstance(record["tags"], list) or not record["tags"]:
            fail(f"Chunk {record['chunk_id']} must have non-empty tags")
        if record["claim_status"] not in VALID_CLAIM_STATUS:
            fail(f"Chunk {record['chunk_id']} has invalid claim_status: {record['claim_status']}")
        if not isinstance(record["answer_intents"], list) or not record["answer_intents"]:
            fail(f"Chunk {record['chunk_id']} must have non-empty answer_intents")
        if not isinstance(record["canonical_questions"], list) or len(record["canonical_questions"]) < 2:
            fail(f"Chunk {record['chunk_id']} must have at least two canonical_questions")
        all_intents.update(record["answer_intents"])
        words = count_words(record["text"])
        if words < 120 or words > 260:
            fail(f"Chunk {record['chunk_id']} has {words} words; expected 120-260 for improved RAG")
        visible_text = "\n".join(
            str(record.get(field, "")) for field in ("topic_title", "fact", "text", "source_title")
        )
        for phrase in FORBIDDEN_UNACCENTED_PHRASES:
            if phrase in visible_text:
                fail(f"Chunk {record['chunk_id']} contains unaccented phrase: {phrase}")

    required_terms = [
        "1753",
        "1792",
        "1788",
        "1785",
        "1789",
        "1939",
        "1945",
        "ngoc hoi",
        "dong da",
        "rach gam",
        "xoai mut",
        "can long",
        "cau phong",
        "pham cong tri",
        "ngo thi nham",
        "phuc khang an",
        "phuong hoang trung do",
        "dung quyet",
        "tin bai",
        "thien ha dai tin",
        "quang trung thong bao",
        "quang trung dai bao",
        "chieu lap hoc",
        "chieu khuyen nong",
        "sung chinh",
    ]
    for term in required_terms:
        if term not in all_text:
            fail(f"Knowledge text missing required historical term: {term}")
    missing_intents = REQUIRED_INTENTS - all_intents
    if missing_intents:
        fail(f"Knowledge text missing required answer_intents: {sorted(missing_intents)}")
    for record in records:
        text = normalize(record.get("text", "") + " " + record.get("fact", ""))
        if "thien ha dai dinh" in text and record.get("chunk_id") not in {"qt_kb_069", "qt_kb_100"}:
            fail("The incorrect tín bài phrase 'Thiên hạ đại định' is only allowed in the correction chunk")
    return records


def main() -> int:
    try:
        profile = validate_profile()
        records = validate_knowledge()
    except AssertionError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1

    print("VALIDATION PASSED")
    print(f"profile: {profile['character_id']}")
    print(f"sample_dialogues: {len(profile['sample_dialogues'])}")
    print(f"knowledge_chunks: {len(records)}")
    print(f"min_words: {min(count_words(record['text']) for record in records)}")
    print(f"max_words: {max(count_words(record['text']) for record in records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
