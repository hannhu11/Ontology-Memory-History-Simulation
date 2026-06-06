import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "quang_trung_web"

CHARACTER_EXPECTATIONS = {
    "quang_trung": {"min_chunks": 100},
    "ho_chi_minh": {"min_chunks": 150},
    "tran_hung_dao": {"min_chunks": 125},
    "nguyen_trai": {"exact_chunks": 50},
    "vo_nguyen_giap": {"exact_chunks": 115},
}

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

VALID_CLAIM_STATUS = {"established", "contested", "interpretive"}


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
                fail(f"{path}:{line_number} is not valid JSON: {exc}")
    return records


def validate_profile(character_id: str) -> dict:
    profile_path = PROJECT_ROOT / f"{character_id}_dataset" / f"{character_id}_profile.json"
    if not profile_path.exists():
        fail(f"Missing profile: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if profile.get("character_id") != character_id:
        fail(f"{profile_path.name} has wrong character_id")
    metadata = profile.get("character_metadata")
    if not isinstance(metadata, dict):
        fail(f"{character_id} metadata must be an object")
    missing = REQUIRED_PROFILE_METADATA - set(metadata)
    if missing:
        fail(f"{character_id} metadata missing: {sorted(missing)}")
    if not isinstance(metadata["aliases"], list) or not metadata["aliases"]:
        fail(f"{character_id} metadata.aliases must be a non-empty list")
    if int(metadata["birth_year"]) >= int(metadata["death_year"]):
        fail(f"{character_id} birth_year/death_year are invalid")
    if not isinstance(profile.get("sample_dialogues"), list) or len(profile["sample_dialogues"]) < 10:
        fail(f"{character_id} needs at least 10 sample dialogues")
    return profile


def validate_chunks(character_id: str) -> list[dict]:
    knowledge_path = PROJECT_ROOT / f"{character_id}_dataset" / f"{character_id}_knowledge.jsonl"
    if not knowledge_path.exists():
        fail(f"Missing knowledge: {knowledge_path}")
    records = load_jsonl(knowledge_path)
    expected = CHARACTER_EXPECTATIONS[character_id]
    if expected.get("exact_chunks") and len(records) != expected["exact_chunks"]:
        fail(f"{character_id} expected {expected['exact_chunks']} chunks, got {len(records)}")
    if len(records) < expected.get("min_chunks", 0):
        fail(f"{character_id} expected at least {expected['min_chunks']} chunks, got {len(records)}")

    seen = set()
    for index, record in enumerate(records, 1):
        missing = REQUIRED_CHUNK_FIELDS - set(record)
        if missing:
            fail(f"{character_id}:{index} missing fields: {sorted(missing)}")
        if record["char_id"] != character_id:
            fail(f"{record['chunk_id']} has wrong char_id")
        if record["chunk_id"] in seen:
            fail(f"{character_id} duplicate chunk_id: {record['chunk_id']}")
        seen.add(record["chunk_id"])
        if record["claim_status"] not in VALID_CLAIM_STATUS:
            fail(f"{record['chunk_id']} has invalid claim_status")
        for field in ("text", "fact", "topic_title", "source_title", "source_quality"):
            if not str(record.get(field, "")).strip():
                fail(f"{record['chunk_id']} has empty {field}")
        if not isinstance(record["tags"], list) or not record["tags"]:
            fail(f"{record['chunk_id']} needs tags")
        if not isinstance(record["answer_intents"], list) or not record["answer_intents"]:
            fail(f"{record['chunk_id']} needs answer_intents")
        if not isinstance(record["canonical_questions"], list) or len(record["canonical_questions"]) < 2:
            fail(f"{record['chunk_id']} needs at least two canonical questions")
    return records


def validate_registry() -> None:
    sys.path.insert(0, str(WEB_ROOT))
    from character_registry import CHARACTER_REGISTRY
    from tts_provider import VOICE_PROFILES

    registry_ids = set(CHARACTER_REGISTRY)
    expected_ids = set(CHARACTER_EXPECTATIONS)
    if registry_ids != expected_ids:
        fail(f"CHARACTER_REGISTRY mismatch: {sorted(registry_ids)} != {sorted(expected_ids)}")
    missing_voices = expected_ids - set(VOICE_PROFILES)
    if missing_voices:
        fail(f"VOICE_PROFILES missing: {sorted(missing_voices)}")
    for character_id, config in CHARACTER_REGISTRY.items():
        if not config["dataset_dir"].exists():
            fail(f"{character_id} dataset_dir does not exist: {config['dataset_dir']}")


def main() -> int:
    try:
        validate_registry()
        for character_id in CHARACTER_EXPECTATIONS:
            profile = validate_profile(character_id)
            records = validate_chunks(character_id)
            print(f"{character_id}: {len(records)} chunks, {len(profile['sample_dialogues'])} dialogues")
    except AssertionError as exc:
        print(f"MULTI VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("MULTI VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
