import json
import shutil
from json import JSONDecoder
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "DATASET-Ontology-Memory-History-Simulation-main"

SOURCE_CONFIGS = {
    "ho_chi_minh": {
        "source_dir": SOURCE_ROOT / "ho_chi_minh_dataset",
        "profile": "ho_chi_minh_profile.json",
        "knowledge": "ho_chi_minh_knowledge.jsonl",
    },
    "tran_hung_dao": {
        "source_dir": SOURCE_ROOT / "tran_hung_dao_dataset",
        "profile": "tran_hung_dao_profile.json",
        "knowledge": "tran_hung_dao_knowledge.jsonl",
        "profile_knowledge": True,
    },
    "nguyen_trai": {
        "source_dir": SOURCE_ROOT / "nguyen_trai_dataset",
        "profile": "Nguyen_Trai_profile.json",
        "knowledge": "Nguyen_Trai_knowledge.json",
    },
    "vo_nguyen_giap": {
        "source_dir": SOURCE_ROOT / "vo_nguyen_giap_dataset",
        "profile": "vo_nguyen_giap_profile.json",
        "knowledge": "vo_nguyen_giap_knowledge_base.jsonl",
    },
}

QUALITY_BY_SOURCE_TYPE = {
    "co_quan_nha_nuoc": "official_secondary",
    "bao_chinh_thong": "press_secondary",
    "báo_chính_thống": "press_secondary",
    "bao_quan_doi": "army_press",
    "báo_quân_đội": "army_press",
    "historical_document": "digitized_primary",
    "tai_lieu_lich_su": "research_secondary",
    "wikisource": "digitized_primary",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def as_list(value) -> list:
    if not value:
        return []
    if isinstance(value, list):
        return [item for item in value if item]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def recover_embedded_json_line(line: str) -> list[dict]:
    marker = '{"char_id"'
    second_start = line.find(marker, len(marker))
    if second_start == -1:
        return [json.loads(line)]
    decoder = JSONDecoder()
    second_record, end_offset = decoder.raw_decode(line[second_start:])
    first_line = line[:second_start] + line[second_start + end_offset :]
    return [json.loads(first_line), second_record]


def load_jsonl_like(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.extend(recover_embedded_json_line(line))
    return records


def normalize_profile(character_id: str, profile: dict) -> dict:
    metadata = profile.get("character_metadata", {})
    if character_id == "tran_hung_dao":
        metadata = {
            **metadata,
            "full_name": metadata.get("real_name", "Trần Quốc Tuấn"),
            "aliases": [
                "Trần Quốc Tuấn",
                "Trần Hưng Đạo",
                "Hưng Đạo Vương",
                "Hưng Đạo Đại Vương",
            ],
            "birth_year": profile.get("birth_year", 1228),
            "death_year": profile.get("death_year", 1300),
            "region": "Nam Định, Vạn Kiếp, Bạch Đằng, Thăng Long",
            "personality_traits": as_list(metadata.get("personality_traits")),
        }
    elif character_id == "nguyen_trai":
        metadata = {
            **metadata,
            "aliases": as_list(metadata.get("aliases") or metadata.get("alias") or "Ức Trai"),
        }
    else:
        metadata = {
            **metadata,
            "aliases": as_list(metadata.get("aliases")),
        }
    metadata["birth_year"] = int(metadata.get("birth_year", profile.get("birth_year", 0)))
    metadata["death_year"] = int(metadata.get("death_year", profile.get("death_year", 0)))
    metadata["personality_traits"] = as_list(metadata.get("personality_traits"))
    profile = {key: value for key, value in profile.items() if key != "knowledge_base"}
    profile["character_id"] = character_id
    profile["character_metadata"] = metadata
    profile.setdefault("sample_dialogues", [])
    return profile


def infer_source_quality(source_type: str) -> str:
    normalized = str(source_type or "").strip().lower().replace(" ", "_")
    return QUALITY_BY_SOURCE_TYPE.get(normalized, "curated_secondary")


def infer_intents(record: dict) -> list[str]:
    blob = " ".join(
        [
            str(record.get("topic_title", "")),
            str(record.get("fact", "")),
            str(record.get("text", record.get("page_content", ""))),
            " ".join(as_list(record.get("tags"))),
        ]
    ).lower()
    intents = set()
    if any(term in blob for term in ("tiểu sử", "tieu_su", "quê quán", "xuat than", "identity")):
        intents.add("identity")
    if any(term in blob for term in ("trận", "chiến dịch", "quân", "binh", "bạch đằng", "dien_bien", "điện biên")):
        intents.add("military")
    if any(term in blob for term in ("chiến thuật", "chien_thuat", "nghệ thuật quân sự", "danh_diem_diet_vien")):
        intents.add("micro_tactics")
    if any(term in blob for term in ("nhân nghĩa", "nhan_nghia", "lòng dân", "long_dan", "khoan thư", "dân")):
        intents.add("governance")
    if any(term in blob for term in ("văn hiến", "chữ nôm", "thơ", "bình ngô", "di chúc", "tuyên ngôn")):
        intents.add("culture")
    if any(term in blob for term in ("ngoại giao", "bang giao", "thuyết phục", "mưu phạt")):
        intents.add("diplomacy")
    if any(term in blob for term in ("đảng", "cách mạng", "việt minh", "độc lập")):
        intents.add("revolution")
    if not intents:
        intents.add("general_history")
    return sorted(intents)


def canonical_questions(record: dict) -> list[str]:
    questions = []
    if record.get("query_context"):
        questions.append(str(record["query_context"]).strip())
    topic = str(record.get("topic_title") or record.get("source_title") or "sự kiện này").strip()
    questions.append(f"{topic} là gì?")
    questions.append(f"{topic} có ý nghĩa lịch sử gì?")
    return list(dict.fromkeys(question for question in questions if question))


def normalize_record(character_id: str, record: dict) -> dict:
    tags = as_list(record.get("tags"))
    text = record.get("text") or record.get("page_content") or record.get("fact") or ""
    topic_title = record.get("topic_title") or record.get("source_title") or record.get("chunk_id")
    fact = record.get("fact") or text.split(".")[0].strip()
    source_year = record.get("source_year", record.get("year", ""))
    source_type = record.get("source_type", "curated_secondary")
    inferred_intents = record.get("answer_intents") or infer_intents(record)
    if not tags:
        tags = [str(topic_title).lower().replace(" ", "_")[:48], *inferred_intents]
    normalized = {
        "char_id": character_id,
        "chunk_id": record["chunk_id"],
        "source_title": record.get("source_title", "Tư liệu chưa rõ nhan đề"),
        "source_year": source_year,
        "source_type": source_type,
        "source_url": record.get("source_url", ""),
        "source_quality": infer_source_quality(source_type),
        "topic_title": topic_title,
        "fact": fact,
        "text": text,
        "claim_status": record.get("claim_status", "established"),
        "tags": tags,
        "answer_intents": inferred_intents,
        "canonical_questions": record.get("canonical_questions") or canonical_questions(record),
    }
    normalized["tag_blob"] = " ".join(
        [
            " ".join(normalized["tags"]),
            " ".join(normalized["answer_intents"]),
            str(normalized["topic_title"]),
            str(normalized["fact"]),
        ]
    )
    return normalized


def load_records(character_id: str, config: dict, profile: dict) -> list[dict]:
    records = load_jsonl_like(config["source_dir"] / config["knowledge"])
    if config.get("profile_knowledge"):
        records.extend(profile.get("knowledge_base", []))
    deduped = {}
    for record in records:
        chunk_id = record.get("chunk_id")
        if not chunk_id:
            continue
        deduped.setdefault(chunk_id, record)
    return [normalize_record(character_id, record) for _, record in sorted(deduped.items())]


def build_character(character_id: str, config: dict) -> tuple[dict, list[dict]]:
    source_profile = read_json(config["source_dir"] / config["profile"])
    profile = normalize_profile(character_id, source_profile)
    records = load_records(character_id, config, source_profile)
    return profile, records


def main() -> int:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(SOURCE_ROOT)
    for character_id, config in SOURCE_CONFIGS.items():
        target_dir = PROJECT_ROOT / f"{character_id}_dataset"
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True)
        profile, records = build_character(character_id, config)
        write_json(target_dir / f"{character_id}_profile.json", profile)
        with (target_dir / f"{character_id}_knowledge.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{character_id}: {len(records)} chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
