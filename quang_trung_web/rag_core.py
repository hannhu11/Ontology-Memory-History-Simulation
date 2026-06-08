from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable

from character_registry import CHARACTER_REGISTRY, DEFAULT_CHARACTER_ID, get_character_config, knowledge_path_for, profile_path_for


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET_DIR = ROOT_DIR.parent / "quang_trung_dataset"
DEFAULT_INDEX_ROOT = ROOT_DIR / ".rag_index"
DEFAULT_INDEX_DIR = DEFAULT_INDEX_ROOT / DEFAULT_CHARACTER_ID
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_EMBEDDING_PROVIDER = "local"
DEFAULT_GEMINI_EMBEDDING_MODEL = "gemini-embedding-2-preview"
DEFAULT_SCORE_THRESHOLD = 0.42
DEFAULT_TOP_K = 4

STOPWORDS = {
    "a",
    "ai",
    "anh",
    "bi",
    "biet",
    "boi",
    "cac",
    "cai",
    "can",
    "cau",
    "cho",
    "co",
    "cua",
    "da",
    "de",
    "den",
    "di",
    "do",
    "duoc",
    "gi",
    "hai",
    "hay",
    "hoi",
    "la",
    "lai",
    "lam",
    "mot",
    "nam",
    "nay",
    "nen",
    "nguoi",
    "nhu",
    "noi",
    "o",
    "ra",
    "rang",
    "sao",
    "su",
    "ta",
    "tai",
    "the",
    "thi",
    "thua",
    "toi",
    "trong",
    "tu",
    "va",
    "ve",
    "vi",
    "vua",
}

MODERN_TERMS = {
    "facebook",
    "internet",
    "mang xa hoi",
    "tri tue nhan tao",
    "dien bien phu",
    "streamlit",
    "tts",
    "api",
    "chatgpt",
    "google",
    "dien thoai",
    "may tinh",
    "the chien",
    "the chien thu nhat",
    "the chien thu 1",
    "the chien thu hai",
    "the chien thu 2",
    "chien tranh the gioi",
    "chien tranh the gioi thu nhat",
    "chien tranh the gioi thu 1",
    "chien tranh the gioi thu hai",
    "chien tranh the gioi thu 2",
    "world war",
    "world war i",
    "world war ii",
    "ww1",
    "ww2",
}

ANACHRONISTIC_WARFARE_TERMS = {
    "blitzkrieg",
    "chien tranh chop nhoang",
    "hoc thuyet chien tranh cua quan duc",
    "quan doi duc",
    "quan duc",
}

UNSUPPORTED_CLAIM_TERMS = {
    "luong quang",
    "thu hoi luong quang",
    "truyen thuyet",
}

UNSUPPORTED_SPECIFIC_TERMS = {
    "vuong dai hai",
    "than phu",
    "cua bien than phu",
}

DIPLOMACY_QUERY_TERMS = {
    "can long",
    "phuc khang an",
    "ngo thi nham",
    "ngo van so",
    "phan huy ich",
    "pham cong tri",
    "gia vuong",
    "quang trung gia",
    "cau phong",
    "ta toi",
    "giang hoa",
    "bang giao",
    "bieu",
    "ngoai giao",
    "nha thanh phong",
    "an nam quoc vuong",
    "chu hau",
    "phuc tung",
}

INTENT_QUERY_TERMS = {
    "capital_city": {
        "phuong hoang trung do",
        "trung do",
        "dung quyet",
        "yen truong",
        "phu thach",
        "dong do",
        "dinh do",
        "doi do",
        "xay dung kinh do",
        "chon dat",
        "nguyen thiep chon dat",
        "la son phu tu chon dat",
    },
    "administration": {
        "tin bai",
        "thien ha dai tin",
        "thien ha dai dinh",
        "so dinh",
        "nhan khau",
        "giay to tuy than",
        "the bai",
        "dan lau",
        "sung quan",
        "quan ly dan cu",
        "go cho moi nguoi dan",
    },
    "coinage": {
        "quang trung thong bao",
        "quang trung dai bao",
        "tien kim loai",
        "tien dong",
        "duc tien",
        "chu quyen tien te",
        "tien te",
        "dong tien",
        "chat lieu",
    },
    "education": {
        "chieu lap hoc",
        "lap hoc",
        "truong hoc",
        "cap xa",
        "giao duc",
        "sung chinh",
        "sung chinh vien",
        "chu nom",
        "dich sach",
        "khoa thi",
    },
    "agriculture": {
        "chieu khuyen nong",
        "khuyen nong",
        "ruong bo hoang",
        "dan luu tan",
        "nong nghiep",
        "san xuat",
        "dan sinh",
    },
    "scholars": {
        "ngo thi nham",
        "chieu cau hien",
        "si phu",
        "bac ha",
        "la son phu tu",
        "nguyen thiep",
        "ton le",
        "hien tai",
        "chieu hien",
        "danh si",
    },
    "battle_reflection": {
        "tran nao",
        "tran danh nao",
        "chien thang nao",
        "thang nao",
        "hanh dien",
        "tu hao",
        "dang nho",
        "nho nhat",
        "cam thay hanh dien",
        "cam thay tu hao",
    },
    "micro_tactics": {
        "ngoc hoi",
        "dong da",
        "bach dang",
        "o ma nhi",
        "bai coc",
        "thuy trieu",
        "ha hoi",
        "dam muc",
        "khương thuong",
        "khuong thuong",
        "an tet truoc",
        "30 thang chap",
        "mong 7",
        "mungg 7",
        "tuong binh",
        "voi chien",
        "ky binh",
        "hoa ho",
        "dai bac",
        "moc rom",
        "rom uot",
        "nam dao",
        "canh tu",
        "chien thuat",
        "quan thanh",
        "ton si nghi",
        "mo ta tran",
        "dien bien tran",
        "tran danh voi quan thanh",
    },
    "military": {
        "nghe an",
        "dung quan",
        "tuyen them binh",
        "duyet binh",
        "bach dang",
        "nguyen mong",
        "quan nguyen",
        "rach gam",
        "xoai mut",
        "my tho",
        "gia dinh",
        "siam",
        "xiem",
        "hanh quan",
        "than toc",
        "dien bien phu",
        "danh chac tien chac",
        "danh nhanh thang nhanh",
        "danh nhanh giai quyet nhanh",
        "keo phao",
        "tap doan cu diem",
        "thuc dan phap",
    },
    "military_doctrine": {
        "tu tuong danh giac",
        "tu tuong quan su",
        "duong loi quan su",
        "chien tranh nhan dan",
        "nghe thuat quan su",
        "danh giac",
        "lay it dich nhieu",
        "toan dan",
        "du kich",
        "danh chac tien chac",
        "danh nhanh thang nhanh",
        "chien luoc quan su",
        "phuong cham",
    },
    "ideology": {
        "tu tuong",
        "nhan nghia",
        "doc lap tu do",
        "khong co gi quy hon doc lap tu do",
        "khoan thu suc dan",
        "muu phat tam cong",
        "yen dan",
        "long dan",
        "than dan",
        "dan la goc",
        "su nghiep",
        "ly tuong",
        "duong loi",
    },
    "life_milestone": {
        "than the",
        "tieu su",
        "cuoc doi",
        "su nghiep",
    },
    "departure": {
        "ra di tim duong cuu nuoc",
        "tim duong cuu nuoc",
        "ben nha rong",
        "nha rong",
        "ngay 5 6 1911",
        "5/6/1911",
    },
    "birth": {
        "sinh nam",
        "sinh ngay",
        "nam sinh",
        "ngay sinh",
    },
    "origin": {
        "que quan",
        "sinh o dau",
        "sinh tai",
        "nguoi o dau",
    },
    "death": {
        "mat nam",
        "nam mat",
        "qua doi",
        "ngay mat",
    },
    "real_name": {
        "ten that",
        "ten khai sinh",
        "nguyen hue la gi",
        "nguyen hue la ai",
    },
    "anachronism": {
        "the chien",
        "chien tranh the gioi",
        "world war",
        "ww1",
        "ww2",
        "internet",
        "facebook",
        "ai",
        "may bay",
        "dien thoai",
    },
    "private_life_sensitive": {
        "vo khong",
        "co vo",
        "bac co vo",
        "nguoi yeu",
        "ket hon",
        "cuoi vo",
        "doi tu",
        "chuyen rieng",
        "gia dinh rieng",
        "hon nhan",
    },
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    return re.sub(r"[^a-z0-9_\s-]", " ", text)


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)
    tokens = re.findall(r"[a-z0-9_]+", normalized)
    return [token for token in tokens if len(token) > 1 and token not in STOPWORDS]


def has_phrase(normalized_text: str, phrase: str) -> bool:
    pattern = re.escape(phrase).replace(r"\ ", r"\s+")
    return bool(re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", normalized_text))


def configured_top_k(default: int = DEFAULT_TOP_K) -> int:
    raw_value = os.getenv("RAG_TOP_K", str(default)).strip()
    try:
        return max(1, int(raw_value))
    except ValueError:
        return default


def configured_score_threshold(default: float = DEFAULT_SCORE_THRESHOLD) -> float:
    raw_value = os.getenv("RAG_SCORE_THRESHOLD", str(default)).strip()
    try:
        return max(0.0, min(1.0, float(raw_value)))
    except ValueError:
        return default


def configured_embedding_model() -> str:
    return os.getenv("RAG_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL).strip() or DEFAULT_EMBEDDING_MODEL


def configured_embedding_provider() -> str:
    provider = os.getenv("RAG_EMBEDDING_PROVIDER", DEFAULT_EMBEDDING_PROVIDER).strip().lower()
    return provider if provider in {"local", "gemini"} else DEFAULT_EMBEDDING_PROVIDER


def configured_gemini_embedding_model() -> str:
    return os.getenv("RAG_GEMINI_EMBEDDING_MODEL", DEFAULT_GEMINI_EMBEDDING_MODEL).strip() or DEFAULT_GEMINI_EMBEDDING_MODEL


def configured_index_dir(character_id: str = DEFAULT_CHARACTER_ID) -> Path:
    raw_value = os.getenv("RAG_INDEX_DIR")
    if not raw_value:
        return DEFAULT_INDEX_ROOT / character_id
    base = Path(raw_value)
    return base if base.name == character_id else base / character_id


def is_birth_query_text(normalized: str) -> bool:
    return any(
        has_phrase(normalized, phrase)
        for phrase in (
            "sinh nam bao nhieu",
            "sinh ngay nao",
            "sinh nam nao",
            "sinh vao nam nao",
            "nam sinh",
            "ngay sinh",
            "bao nhieu tuoi",
        )
    )


def is_origin_query_text(normalized: str) -> bool:
    return any(
        has_phrase(normalized, phrase)
        for phrase in (
            "que o dau",
            "que quan",
            "sinh o dau",
            "sinh tai dau",
            "nguoi o dau",
        )
    )


def is_death_query_text(normalized: str) -> bool:
    return any(
        has_phrase(normalized, phrase)
        for phrase in (
            "mat nam nao",
            "mat khi nao",
            "qua doi nam nao",
            "nam mat",
            "ngay mat",
            "chet nam nao",
        )
    )


def is_real_name_query_text(normalized: str) -> bool:
    return any(
        has_phrase(normalized, phrase)
        for phrase in (
            "ten that",
            "ten khai sinh",
            "ten day du",
            "ten khac",
            "ten cua bac",
            "ten cua ong",
            "ten cua ngai",
            "bac ten gi",
            "ong ten gi",
            "ngai ten gi",
            "nguoi ten gi",
            "nguyen hue la gi",
            "nguyen hue la ai",
        )
    )


def query_intents(query: str) -> set[str]:
    normalized = normalize(query)
    if is_birth_query_text(normalized):
        return {"birth"}
    if is_origin_query_text(normalized):
        return {"origin"}
    if is_death_query_text(normalized):
        return {"death"}
    if is_real_name_query_text(normalized):
        return {"real_name"}
    intents = {
        intent
        for intent, terms in INTENT_QUERY_TERMS.items()
        if any(has_phrase(normalized, term) for term in terms)
    }
    if is_diplomacy_query(query):
        intents.add("diplomacy")
    if is_anachronistic_warfare_query(query):
        intents.add("anachronism")
    for primary in (
        "anachronism",
        "private_life_sensitive",
        "birth",
        "origin",
        "death",
        "real_name",
        "capital_city",
        "administration",
        "coinage",
        "education",
        "agriculture",
        "scholars",
        "diplomacy",
        "departure",
        "life_milestone",
        "ideology",
        "military_doctrine",
        "battle_reflection",
        "micro_tactics",
        "military",
    ):
        if primary in intents:
            return {primary}
    return intents


@lru_cache(maxsize=2)
def cached_embedding_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


class EmbeddingMatrix(list):
    def tolist(self) -> list:
        return list(self)


class GeminiEmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def encode(self, texts: list[str], normalize_embeddings: bool = True) -> EmbeddingMatrix:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Gemini embeddings")
        vectors = [self._embed(text) for text in texts]
        if normalize_embeddings:
            vectors = [normalize_vector(vector) for vector in vectors]
        return EmbeddingMatrix(vectors)

    def _embed(self, text: str) -> list[float]:
        model = urllib.parse.quote(self.model_name, safe="")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={api_key_for_url()}"
        payload = {
            "model": f"models/{self.model_name}",
            "content": {"parts": [{"text": text[:18000]}]},
            "taskType": "RETRIEVAL_DOCUMENT",
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result.get("embedding", {}).get("values", [])


def api_key_for_url() -> str:
    return urllib.parse.quote(os.getenv("GEMINI_API_KEY", "").strip(), safe="")


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm <= 0:
        return vector
    return [value / norm for value in vector]


def embedding_dimension(embedding_model) -> int:
    if hasattr(embedding_model, "get_sentence_embedding_dimension"):
        dimension = embedding_model.get_sentence_embedding_dimension()
        if dimension:
            return int(dimension)
    sample = encode_embeddings(embedding_model, ["dimension probe"])
    return len(sample[0]) if sample else 0


def encode_embeddings(embedding_model, texts: list[str]) -> list[list[float]]:
    encoded = embedding_model.encode(texts, normalize_embeddings=True)
    return encoded.tolist() if hasattr(encoded, "tolist") else list(encoded)


def cached_embedding_backend(provider: str, model_name: str):
    if provider == "gemini":
        return GeminiEmbeddingModel(model_name)
    return cached_embedding_model(model_name)


def chunk_intents(chunk: dict) -> set[str]:
    intents = set(chunk.get("answer_intents") or []) | set(chunk.get("tags") or [])
    blob = normalize(
        " ".join(
            [
                chunk.get("topic_title", ""),
                chunk.get("fact", ""),
                chunk.get("text", ""),
                " ".join(chunk.get("tags", [])),
                " ".join(chunk.get("answer_intents", [])),
            ]
        )
    )
    if intents & {"micro_tactics", "military", "battle", "ngoc_hoi_dong_da", "rach_gam_xoai_mut"}:
        intents.add("battle_reflection")
    if any(term in blob for term in ("than the", "tieu su", "cuoc doi", "su nghiep")):
        intents.add("life_milestone")
    if any(
        term in blob
        for term in (
            "ra di tim duong cuu nuoc",
            "tim duong cuu nuoc",
            "ben nha rong",
            "5/6/1911",
            "ngay 5 6 1911",
        )
    ):
        intents.add("departure")
        intents.add("life_milestone")
    if any(
        term in blob
        for term in (
            "sinh nam",
            "sinh ngay",
            "nam sinh",
            "ngay sinh",
            "sinh tai",
            "sinh ra",
            "ten khai sinh",
        )
    ):
        intents.add("birth")
        intents.add("life_milestone")
    if any(
        term in blob
        for term in (
            "que quan",
            "que o",
            "sinh tai",
            "loc thuy",
            "le thuy",
            "kim lien",
            "nam dan",
            "nam dinh",
            "nhi khe",
            "chi ngai",
            "phu xuan",
            "nghe an",
        )
    ):
        intents.add("origin")
        intents.add("life_milestone")
    if any(term in blob for term in ("mat nam", "nam mat", "mat ngay", "qua doi", "died", "tu tran")):
        intents.add("death")
        intents.add("life_milestone")
    if any(term in blob for term in ("ten that", "ten khai sinh", "real_name", "nguyen hue", "tran quoc tuan", "uc trai")):
        intents.add("real_name")
    if any(
        term in blob
        for term in (
            "bach_dang",
            "bach dang",
            "o_ma_nhi",
            "o ma nhi",
            "bai coc",
            "thuy trieu",
            "tu tuong quan su",
            "chien tranh nhan dan",
            "nghe thuat quan su",
            "danh chac tien chac",
            "danh nhanh thang nhanh",
            "du kich",
            "phuong cham",
        )
    ):
        intents.add("military_doctrine")
    if any(
        term in blob
        for term in (
            "bach_dang",
            "bach dang",
            "o_ma_nhi",
            "o ma nhi",
            "bai coc",
            "thuy trieu",
        )
    ):
        intents.add("micro_tactics")
        intents.add("military")
    if any(
        term in blob
        for term in (
            "tu tuong",
            "nhan nghia",
            "doc lap tu do",
            "yen dan",
            "long dan",
            "khoan thu suc dan",
            "muu phat tam cong",
            "dan la goc",
        )
    ):
        intents.add("ideology")
    return intents


def infer_source_tier(chunk: dict) -> int:
    title = normalize(chunk.get("source_title", ""))
    source_type = normalize(chunk.get("source_type", ""))
    quality = normalize(chunk.get("source_quality", ""))
    url = normalize(chunk.get("source_url", ""))
    tier1_terms = (
        "dai viet su ky toan thu",
        "kham dinh viet su thong giam cuong muc",
        "bao tang lich su quoc gia",
        "baotanglichsuquocgia",
        "chinh phu",
        "dangcongsan",
        "bo quoc phong",
        "mod gov",
        "qdnd",
        "tap chi quoc phong toan dan",
        "ho chi minh toan tap",
        "van kien dang",
        "historical_document",
        "digitized_primary",
        "official_book",
        "official_book_excerpt",
        "museum_document",
        "museum_official",
    )
    tier2_terms = (
        "vien su hoc",
        "vass",
        "nghien cuu",
        "research",
        "university",
        "journal",
        "tap chi",
        "nxb",
        "digitized_secondary",
        "research_secondary",
        "national_defense_journal",
    )
    tier4_terms = ("wikipedia", "wiki", "wikisource")
    blob = " ".join([title, source_type, quality, url])
    if any(term in blob for term in tier1_terms):
        return 1
    if any(term in blob for term in tier2_terms):
        return 2
    if any(term in blob for term in tier4_terms):
        return 4
    return 3


def chunk_source_tier(chunk: dict) -> int:
    raw_tier = chunk.get("source_tier")
    if isinstance(raw_tier, int):
        return max(1, min(4, raw_tier))
    if isinstance(raw_tier, str):
        match = re.search(r"[1-4]", raw_tier)
        if match:
            return int(match.group(0))
    return infer_source_tier(chunk)


def source_quality_score(chunk: dict) -> float:
    if isinstance(chunk.get("source_quality_score"), (int, float)):
        return float(chunk["source_quality_score"])
    return {1: 1.0, 2: 0.78, 3: 0.55, 4: 0.25}.get(infer_source_tier(chunk), 0.45)


def source_quality_boost(chunk: dict) -> float:
    tier = chunk_source_tier(chunk)
    tier_boost = {1: 0.105, 2: 0.065, 3: 0.02, 4: -0.08}.get(tier, 0.0)
    quality = chunk.get("source_quality", "")
    return tier_boost + {
        "research_secondary": 0.035,
        "digitized_secondary": 0.025,
        "digitized_primary": 0.075,
        "museum_official": 0.02,
        "curated_exhibit": 0.015,
        "official_book_excerpt": 0.07,
        "press_secondary": 0.025,
    }.get(quality, 0.0)


def diversify_hits(ranked: list[Hit], top_k: int) -> list[Hit]:
    if not ranked:
        return []
    has_trusted = any(chunk_source_tier(hit.chunk) <= 2 for hit in ranked)
    candidates = [hit for hit in ranked if not (has_trusted and chunk_source_tier(hit.chunk) == 4)]
    selected: list[Hit] = []
    source_counts: Counter[str] = Counter()
    topic_seen: set[str] = set()
    for hit in candidates:
        source_key = normalize(hit.chunk.get("source_title", "") or hit.chunk.get("source_url", ""))
        topic_key = normalize(hit.chunk.get("topic_title", "") or hit.chunk.get("fact", ""))[:120]
        if source_counts[source_key] >= 2:
            continue
        if topic_key and topic_key in topic_seen and len(selected) >= max(1, top_k // 2):
            continue
        selected.append(hit)
        source_counts[source_key] += 1
        if topic_key:
            topic_seen.add(topic_key)
        if len(selected) >= top_k:
            return selected
    for hit in candidates:
        if hit not in selected:
            selected.append(hit)
        if len(selected) >= top_k:
            break
    return selected


def select_bach_dang_hits(ranked: list[Hit], top_k: int) -> list[Hit]:
    preferred: list[Hit] = []
    backup: list[Hit] = []
    seen: set[str] = set()
    for hit in ranked:
        chunk_id = hit.chunk.get("chunk_id", "")
        if not chunk_id or chunk_id in seen:
            continue
        blob = normalize(
            " ".join(
                [
                    hit.chunk.get("topic_title", ""),
                    hit.chunk.get("fact", ""),
                    hit.chunk.get("text", ""),
                    " ".join(hit.chunk.get("tags", [])),
                    " ".join(hit.chunk.get("answer_intents", [])),
                ]
            )
        )
        tags = {normalize(term) for term in (hit.chunk.get("tags") or []) + (hit.chunk.get("answer_intents") or [])}
        has_anchor = any(
            term in blob
            for term in ("bach dang", "bach_dang", "o ma nhi", "o_ma_nhi", "bai coc", "thuy trieu", "mac coc")
        )
        if not has_anchor:
            continue
        off_target = bool(tags & {"ngoai_giao", "hau_chien", "hoa_binh", "diplomacy", "governance"}) or any(
            term in blob for term in ("1285", "dien hong", "ly hang", "lang son")
        )
        if off_target:
            backup.append(hit)
        else:
            preferred.append(hit)
        seen.add(chunk_id)
    selected = preferred[:top_k]
    if len(selected) < top_k:
        selected.extend(hit for hit in backup if hit not in selected)
    return selected[:top_k] or ranked[:top_k]


def is_battle_reflection_query(query: str) -> bool:
    normalized = normalize(query)
    affect_terms = ("hanh dien", "tu hao", "dang nho", "nho nhat", "cam thay hanh dien", "cam thay tu hao")
    comparison_terms = ("tran nao", "tran danh nao", "chien thang nao", "thang nao", "chien thang lon nhat")
    return any(has_phrase(normalized, term) for term in affect_terms + comparison_terms)


def is_battle_description_query(query: str) -> bool:
    normalized = normalize(query)
    battle_terms = ("tran danh", "tran danh voi quan thanh", "quan thanh", "ngoc hoi", "dong da", "ton si nghi")
    description_terms = ("mo ta", "ke ve", "noi qua", "dien bien", "tran danh", "chien thuat")
    return any(has_phrase(normalized, term) for term in battle_terms) and any(
        has_phrase(normalized, term) for term in description_terms
    )


def is_tran_hung_dao_bach_dang_query(query: str) -> bool:
    normalized = normalize(query)
    return any(
        has_phrase(normalized, term)
        for term in ("bach dang", "1288", "o ma nhi", "bai coc", "thuy trieu", "nguyen mong")
    )


def profile_character_id(profile: dict | None) -> str:
    return (profile or {}).get("character_id", DEFAULT_CHARACTER_ID)


def rewrite_query(query: str, profile: dict | None = None) -> str:
    normalized = normalize(query)
    intents = query_intents(query)
    additions: list[str] = []
    if profile and profile.get("character_metadata", {}).get("name"):
        metadata = profile["character_metadata"]
        name_blob = " ".join(
            [
                metadata.get("name", ""),
                metadata.get("full_name", ""),
                " ".join(metadata.get("aliases", [])),
                "Tây Sơn",
            ]
        )
    else:
        name_blob = "Quang Trung Nguyễn Huệ Tây Sơn"

    if any(has_phrase(normalized, term) for term in ("vua", "nha vua", "ngai", "ong", "ta")):
        additions.append(name_blob)
    if intents & {"ideology", "military_doctrine"}:
        character_id = profile_character_id(profile)
        additions.append(name_blob)
        if character_id == "vo_nguyen_giap":
            additions.append(
                "Võ Nguyên Giáp tư tưởng quân sự chiến tranh nhân dân toàn dân toàn diện "
                "đánh chắc tiến chắc nghệ thuật quân sự Điện Biên Phủ"
            )
        elif character_id == "ho_chi_minh":
            additions.append(
                "Hồ Chí Minh tư tưởng độc lập tự do dân là gốc đạo đức cách mạng đại đoàn kết "
                "không có gì quý hơn độc lập tự do"
            )
        elif character_id == "nguyen_trai":
            additions.append(
                "Nguyễn Trãi Bình Ngô đại cáo nhân nghĩa yên dân mưu phạt tâm công lòng dân "
                "Quân trung từ mệnh tập"
            )
        elif character_id == "tran_hung_dao":
            additions.append(
                "Trần Hưng Đạo Hịch tướng sĩ khoan thư sức dân Bạch Đằng binh pháp giữ nước "
                "lòng dân tướng sĩ"
            )
        else:
            additions.append("tư tưởng trị nước dùng người yên dân quân sự cải cách")
    if profile_character_id(profile) == "quang_trung" and is_battle_reflection_query(query):
        additions.append(
            "trận đánh hãnh diện tự hào chiến thắng lớn Ngọc Hồi Đống Đa Kỷ Dậu 1789 "
            "Rạch Gầm Xoài Mút năm 1785 quân Thanh quân Xiêm"
        )
    elif profile_character_id(profile) == "quang_trung" and is_battle_description_query(query):
        additions.append(
            "trận Ngọc Hồi Đống Đa mùa xuân Kỷ Dậu 1789 quân Thanh Tôn Sĩ Nghị "
            "Hà Hồi Ngọc Hồi Đống Đa tượng binh hỏa hổ đại bác mộc rơm ướt năm đạo quân"
        )
    elif profile_character_id(profile) == "tran_hung_dao" and is_tran_hung_dao_bach_dang_query(query):
        additions.append(
            "Trần Hưng Đạo Bạch Đằng 1288 Ô Mã Nhi bãi cọc gỗ lim thủy triều "
            "thủy quân Nguyên Mông thuyền nhỏ khiêu chiến tổng tấn công"
        )
    elif additions:
        additions.append("tiểu sử sự nghiệp tư tưởng chiến lược lịch sử")
    if not additions:
        return query
    return " ".join([query, *additions])


def query_variants(query: str, profile: dict | None = None) -> list[str]:
    variants = [query, rewrite_query(query, profile)]
    intents = query_intents(query)
    character_id = profile_character_id(profile)
    if profile_character_id(profile) == "quang_trung" and is_battle_reflection_query(query):
        variants.extend(
            [
                "Quang Trung Nguyễn Huệ Tây Sơn trận Ngọc Hồi Đống Đa Kỷ Dậu 1789 chiến thắng hãnh diện nhất đại phá quân Thanh",
                "Quang Trung Nguyễn Huệ Tây Sơn trận Rạch Gầm Xoài Mút năm 1785 chiến thắng quân Xiêm Nguyễn",
                "Quang Trung Nguyễn Huệ nghệ thuật quân sự chiến thắng lớn trận đánh đáng nhớ",
            ]
        )
    elif profile_character_id(profile) == "quang_trung" and is_battle_description_query(query):
        variants.extend(
            [
                "Quang Trung Nguyễn Huệ trận Ngọc Hồi Đống Đa Kỷ Dậu 1789 diễn biến đại phá quân Thanh Tôn Sĩ Nghị",
                "Quang Trung Nguyễn Huệ chiến dịch Ngọc Hồi Đống Đa năm đạo quân Hà Hồi Ngọc Hồi Đống Đa",
                "Tây Sơn tượng binh hỏa hổ đại bác mộc rơm ướt đánh quân Thanh ở Ngọc Hồi",
            ]
        )
    elif character_id == "tran_hung_dao" and is_tran_hung_dao_bach_dang_query(query):
        variants.extend(
            [
                "Trần Hưng Đạo trận Bạch Đằng năm 1288 Ô Mã Nhi thủy quân Nguyên Mông bãi cọc thủy triều",
                "Bạch Đằng 1288 quân Trần dụ thuyền Ô Mã Nhi vào sông chờ thủy triều rút bãi cọc lộ ra",
                "Trần Hưng Đạo tổng tấn công Bạch Đằng 1288 thuyền địch mắc cọc Ô Mã Nhi bị bắt",
            ]
        )
    elif intents & {"ideology", "military_doctrine"}:
        if character_id == "vo_nguyen_giap":
            variants.extend(
                [
                    "Võ Nguyên Giáp tư tưởng đánh giặc chiến tranh nhân dân toàn dân toàn diện",
                    "Võ Nguyên Giáp nghệ thuật quân sự đánh chắc tiến chắc Điện Biên Phủ",
                    "Võ Nguyên Giáp đường lối quân sự lấy chính trị tinh thần và nhân dân làm nền",
                ]
            )
        elif character_id == "ho_chi_minh":
            variants.extend(
                [
                    "Hồ Chí Minh tư tưởng độc lập tự do hạnh phúc dân là gốc",
                    "Hồ Chí Minh không có gì quý hơn độc lập tự do đại đoàn kết đạo đức cách mạng",
                    "Hồ Chí Minh tư tưởng cách mạng giải phóng dân tộc",
                ]
            )
        elif character_id == "nguyen_trai":
            variants.extend(
                [
                    "Nguyễn Trãi tư tưởng nhân nghĩa yên dân Bình Ngô đại cáo",
                    "Nguyễn Trãi mưu phạt tâm công Quân trung từ mệnh tập lòng dân",
                    "Nguyễn Trãi văn hiến Đại Việt chống ngoại xâm nhân nghĩa",
                ]
            )
        elif character_id == "tran_hung_dao":
            variants.extend(
                [
                    "Trần Hưng Đạo khoan thư sức dân kế sâu rễ bền gốc giữ nước",
                    "Trần Hưng Đạo Hịch tướng sĩ lòng trung nghĩa tướng sĩ quân Nguyên Mông",
                    "Trần Hưng Đạo Bạch Đằng 1288 binh pháp đoàn kết toàn dân",
                ]
            )
    elif "micro_tactics" in intents:
        query_norm = normalize(query)
        if character_id == "quang_trung" and any(term in query_norm for term in ("an tet", "30 thang chap", "mong 7")):
            variants.extend(
                [
                    "Quang Trung cho quân ăn Tết trước cuối tháng Chạp Mậu Thân 1788 mồng 7 vào Thăng Long",
                    "Ăn Tết trước giữ nhịp hành quân thần tốc tạo sĩ khí bất ngờ chiến lược",
                    "Lời hẹn mồng 7 tháng Giêng vào Thăng Long mở tiệc lớn",
                ]
            )
        elif character_id == "quang_trung" and any(term in query_norm for term in ("tuong binh", "voi chien", "ky binh")):
            variants.extend(
                [
                    "Tây Sơn tượng binh voi chiến kỵ binh Thanh Ngọc Hồi hỏa hổ mộc rơm ướt",
                    "Quang Trung dùng tượng binh phối hợp bộ binh hỏa khí phá kỵ binh Thanh",
                ]
            )
    elif "birth" in intents:
        if character_id == "ho_chi_minh":
            variants.extend(
                [
                    "Hồ Chí Minh sinh ngày 19/5/1890 tại Kim Liên Nam Đàn Nghệ An",
                    "Nguyễn Sinh Cung sinh năm 1890 quê Nghệ An",
                ]
            )
        elif character_id == "vo_nguyen_giap":
            variants.extend(
                [
                    "Võ Nguyên Giáp sinh năm 1911 tại Lộc Thủy Lệ Thủy Quảng Bình",
                    "Đại tướng Võ Nguyên Giáp quê Lộc Thủy Quảng Bình sinh 1911",
                ]
            )
        elif character_id == "nguyen_trai":
            variants.append("Nguyễn Trãi sinh năm 1380 quê Chi Ngại Nhị Khê Ức Trai")
        elif character_id == "tran_hung_dao":
            variants.append("Trần Hưng Đạo Trần Quốc Tuấn sinh khoảng năm 1228 tại Nam Định")
        elif character_id == "quang_trung":
            variants.append("Quang Trung Nguyễn Huệ sinh năm 1753 Tây Sơn")
    elif "origin" in intents:
        if character_id == "ho_chi_minh":
            variants.append("Hồ Chí Minh quê Kim Liên Nam Đàn Nghệ An Nguyễn Sinh Cung")
        elif character_id == "vo_nguyen_giap":
            variants.append("Võ Nguyên Giáp quê Lộc Thủy Lệ Thủy Quảng Bình")
        elif character_id == "nguyen_trai":
            variants.append("Nguyễn Trãi quê Chi Ngại Hải Dương Nhị Khê Hà Nội")
        elif character_id == "tran_hung_dao":
            variants.append("Trần Hưng Đạo Trần Quốc Tuấn sinh tại Nam Định Vạn Kiếp")
        elif character_id == "quang_trung":
            variants.append("Nguyễn Huệ Quang Trung Tây Sơn Phú Xuân Nghệ An")
    elif "departure" in intents:
        if character_id == "ho_chi_minh":
            variants.extend(
                [
                    "Hồ Chí Minh Nguyễn Tất Thành ra đi tìm đường cứu nước ngày 5/6/1911 bến Nhà Rồng tàu Amiral Latouche-Tréville",
                    "Hồ Chí Minh Bến Nhà Rồng năm 1911 hành trình tìm đường cứu nước",
                ]
            )
    elif "life_milestone" in intents:
        if character_id == "ho_chi_minh":
            variants.extend(
                [
                    "Hồ Chí Minh Nguyễn Sinh Cung Nguyễn Tất Thành tiểu sử thân thế sự nghiệp",
                    "Hồ Chí Minh quê Nghệ An sinh năm 1890 hoạt động cách mạng",
                ]
            )
        elif character_id == "vo_nguyen_giap":
            variants.append("Võ Nguyên Giáp sinh tại Lộc Thủy Lệ Thủy Quảng Bình tiểu sử thân thế")
        elif character_id == "nguyen_trai":
            variants.append("Nguyễn Trãi Ức Trai thân thế tiểu sử Lam Sơn Bình Ngô đại cáo")
        elif character_id == "tran_hung_dao":
            variants.append("Trần Hưng Đạo Hưng Đạo Đại Vương thân thế tiểu sử nhà Trần")
    deduped = []
    seen = set()
    for variant in variants:
        key = normalize(variant)
        if key and key not in seen:
            deduped.append(variant)
            seen.add(key)
    return deduped


def intent_matches(query_intent_set: set[str], doc_intent_set: set[str]) -> bool:
    if not query_intent_set:
        return True
    return bool(query_intent_set & doc_intent_set)


def rerank_hits(query: str, hits: list[Hit], top_k: int, min_score: float | None = None) -> list[Hit]:
    intents = query_intents(query)
    query_years = re.findall(r"\b(1[0-9]\d{2}|20\d{2})\b", normalize(query))
    threshold = min_score if min_score is not None else configured_score_threshold()
    fused: dict[str, Hit] = {}
    for hit in hits:
        doc_intents = chunk_intents(hit.chunk)
        if not intent_matches(intents, doc_intents):
            continue
        adjusted = hit.score + source_quality_boost(hit.chunk)
        chunk_blob = normalize(
            " ".join(
                [
                    hit.chunk.get("topic_title", ""),
                    hit.chunk.get("fact", ""),
                    hit.chunk.get("text", ""),
                    hit.chunk.get("source_title", ""),
                ]
            )
        )
        if query_years:
            if any(year in chunk_blob for year in query_years):
                adjusted += 0.2
            else:
                adjusted -= 0.07
        if intents and (intents & doc_intents):
            adjusted += 0.08 + min(0.12, 0.04 * len(intents & doc_intents))
        if "battle_reflection" in intents:
            if doc_intents & {"micro_tactics", "military"}:
                adjusted += 0.22
            if hit.chunk.get("chunk_id") in {"qt_kb_032", "qt_kb_039", "qt_kb_047", "qt_kb_092", "qt_kb_093", "qt_kb_095", "qt_kb_096", "qt_kb_097"}:
                adjusted += 0.16
        if is_tran_hung_dao_bach_dang_query(query):
            if any(term in chunk_blob for term in ("bach dang", "bach_dang", "o ma nhi", "o_ma_nhi", "bai coc", "thuy trieu")):
                adjusted += 0.32
            if doc_intents & {"micro_tactics"}:
                adjusted += 0.14
            off_target_tags = {
                normalize(term)
                for term in (hit.chunk.get("tags") or []) + (hit.chunk.get("answer_intents") or [])
            }
            if off_target_tags & {"ngoai_giao", "hau_chien", "hoa_binh", "diplomacy", "governance"}:
                adjusted -= 0.34
            if any(term in chunk_blob for term in ("dien hong", "1285", "ly hang", "lang son", "hoa binh", "thoat hoan rut")):
                adjusted -= 0.3
        chunk_id = hit.chunk.get("chunk_id", "")
        previous = fused.get(chunk_id)
        if previous is None or adjusted > previous.score:
            fused[chunk_id] = Hit(hit.chunk, min(adjusted, 1.0))
    ranked = sorted(fused.values(), key=lambda item: item.score, reverse=True)
    if ranked and ranked[0].score < threshold:
        return []
    if is_tran_hung_dao_bach_dang_query(query):
        return select_bach_dang_hits(ranked, top_k)
    return diversify_hits(ranked, top_k)


def lexical_anchor_boost(query_norm: str, chunk: dict) -> float:
    tag_blob = normalize(
        " ".join(
            [
                chunk.get("topic_title", ""),
                chunk.get("fact", ""),
                " ".join(chunk.get("tags", [])),
                " ".join(chunk.get("answer_intents", [])),
            ]
        )
    )
    boost = 0.0
    if "nghe an" in query_norm and ("nghe_an" in tag_blob or "nghe an" in tag_blob):
        boost += 0.24
    if ("ngoc hoi" in query_norm or "dong da" in query_norm) and any(
        term in tag_blob for term in ("ngoc_hoi", "dong_da", "ngoc hoi", "dong da", "ngoc_hoi_dong_da")
    ):
        boost += 0.22
    if ("rach gam" in query_norm or "xoai mut" in query_norm) and any(
        term in tag_blob for term in ("rach_gam_xoai_mut", "rach gam", "xoai mut")
    ):
        boost += 0.22
    if "dien bien phu" in query_norm and (
        "dien_bien" in tag_blob or "dien bien phu" in tag_blob or "dienbienphu" in tag_blob
    ):
        boost += 0.28
    if "bach dang" in query_norm and (
        "bach_dang" in tag_blob or "bach dang" in tag_blob or "o_ma_nhi" in tag_blob or "bai coc" in tag_blob
    ):
        boost += 0.28
    if "chien tranh nhan dan" in query_norm and (
        "chien_tranh_nhan_dan" in tag_blob or "chien tranh nhan dan" in tag_blob
    ):
        boost += 0.24
    if ("can long" in query_norm or "cau phong" in query_norm or "ta toi" in query_norm) and any(
        term in tag_blob for term in ("can_long", "cau phong", "ta toi", "diplomacy", "qing")
    ):
        boost += 0.22
    return boost


def is_identity_query(query: str) -> bool:
    normalized = normalize(query)
    identity_phrases = (
        "gioi thieu",
        "la ai",
        "nguoi la ai",
        "vua la ai",
        "nha vua la ai",
        "trieu dai nao",
        "thong linh",
        "cam quan",
        "ten that",
        "ten cua",
        "co phai la mot",
        "co phai mot nguoi",
    )
    if any(has_phrase(normalized, phrase) for phrase in identity_phrases):
        return True
    identity_names = ("nguyen hue", "quang trung", "bac binh vuong")
    relation_terms = (
        "gi cua nhau",
        "la gi cua nhau",
        "quan he gi",
        "anh em",
        "mot nguoi",
        "co phai",
        "ten",
    )
    return any(has_phrase(normalized, name) for name in identity_names) and any(
        has_phrase(normalized, term) for term in relation_terms
    )


def is_smalltalk_query(query: str) -> bool:
    normalized = normalize(query)
    tokens = tokenize(query)
    smalltalk_phrases = (
        "chao",
        "xin chao",
        "chao vua",
        "cho toi hoi",
        "toi muon hoi",
        "toi hoi",
        "vua oi",
        "nha vua oi",
        "co ai o day khong",
    )
    return any(has_phrase(normalized, phrase) for phrase in smalltalk_phrases) or (
        len(tokens) <= 3 and any(term in normalized for term in ("chao", "hoi", "nghe"))
    )


def is_private_life_query(query: str) -> bool:
    normalized = normalize(query)
    return any(
        has_phrase(normalized, phrase)
        for phrase in (
            "vo khong",
            "co vo",
            "bac co vo",
            "nguoi yeu",
            "ket hon",
            "cuoi vo",
            "doi tu",
            "chuyen rieng",
            "gia dinh rieng",
            "hon nhan",
        )
    )


def is_quang_trung_self_name_confusion(query: str, profile: dict | None = None) -> bool:
    if profile and profile_character_id(profile) != DEFAULT_CHARACTER_ID:
        return False
    normalized = normalize(query)
    has_self_name = any(has_phrase(normalized, phrase) for phrase in ("nguyen hue", "quang trung", "bac binh vuong"))
    has_relation = any(
        has_phrase(normalized, phrase)
        for phrase in (
            "anh em",
            "la anh em",
            "co phai anh em",
            "quan he gi",
            "gi cua nhau",
            "la gi cua nhau",
            "la ai",
            "co phai la",
            "co phai mot nguoi",
            "mot nguoi",
        )
    )
    return has_self_name and has_relation


def has_substantive_historical_anchor(query: str) -> bool:
    normalized = normalize(query)
    if query_intents(query):
        return True
    anchor_phrases = (
        "ngoc hoi",
        "dong da",
        "rach gam",
        "xoai mut",
        "quan thanh",
        "quan xiem",
        "ton si nghi",
        "nguyen hue",
        "quang trung",
        "bac binh vuong",
        "bach dang",
        "dien bien phu",
        "nhan nghia",
        "tu tuong",
        "chien tranh nhan dan",
        "khoan thu suc dan",
        "binh ngo",
        "doc lap tu do",
        "phuong hoang trung do",
        "tin bai",
        "tien quang trung",
        "chieu lap hoc",
        "chieu khuyen nong",
    )
    if any(has_phrase(normalized, phrase) for phrase in anchor_phrases):
        return True
    action_terms = ("tran", "chien dich", "chien thang", "danh", "ke ve", "mo ta", "noi qua")
    return len(tokenize(query)) > 5 and any(has_phrase(normalized, term) for term in action_terms)


def is_pure_smalltalk_query(query: str) -> bool:
    return is_smalltalk_query(query) and not is_identity_query(query) and not has_substantive_historical_anchor(query)


def resolve_character_id(character_or_dir: Path | str = DEFAULT_CHARACTER_ID) -> str:
    if isinstance(character_or_dir, Path):
        return DEFAULT_CHARACTER_ID
    candidate = str(character_or_dir)
    if candidate in CHARACTER_REGISTRY:
        return candidate
    return DEFAULT_CHARACTER_ID


def resolve_dataset_dir(character_or_dir: Path | str = DEFAULT_CHARACTER_ID) -> Path:
    if isinstance(character_or_dir, Path):
        return character_or_dir
    candidate = str(character_or_dir)
    if "\\" in candidate or "/" in candidate:
        return Path(candidate)
    return get_character_config(candidate)["dataset_dir"]


def _profile_path(character_or_dir: Path | str = DEFAULT_CHARACTER_ID) -> Path:
    if isinstance(character_or_dir, Path) or "\\" in str(character_or_dir) or "/" in str(character_or_dir):
        dataset_dir = resolve_dataset_dir(character_or_dir)
        matches = sorted(dataset_dir.glob("*_profile.json"))
        if not matches:
            raise FileNotFoundError(f"No *_profile.json found in {dataset_dir}")
        return matches[0]
    return profile_path_for(str(character_or_dir))


def _knowledge_path(character_or_dir: Path | str = DEFAULT_CHARACTER_ID) -> Path:
    if isinstance(character_or_dir, Path) or "\\" in str(character_or_dir) or "/" in str(character_or_dir):
        dataset_dir = resolve_dataset_dir(character_or_dir)
        matches = sorted(dataset_dir.glob("*_knowledge.jsonl"))
        if not matches:
            raise FileNotFoundError(f"No *_knowledge.jsonl found in {dataset_dir}")
        return matches[0]
    return knowledge_path_for(str(character_or_dir))


def load_profile(character_id: Path | str = DEFAULT_CHARACTER_ID) -> dict:
    return json.loads(_profile_path(character_id).read_text(encoding="utf-8"))


def load_chunks(character_id: Path | str = DEFAULT_CHARACTER_ID) -> list[dict]:
    chunks = []
    with _knowledge_path(character_id).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                chunk = json.loads(line)
                chunk.setdefault("source_tier", chunk_source_tier(chunk))
                chunk.setdefault("source_quality_score", source_quality_score(chunk))
                chunks.append(chunk)
    return chunks


@dataclass
class Hit:
    chunk: dict
    score: float


class SimpleRetriever:
    def __init__(self, chunks: Iterable[dict]):
        self.chunks = list(chunks)
        self.doc_tokens = [
            tokenize(
                " ".join(
                    [
                        chunk.get("topic_title", ""),
                        chunk.get("fact", ""),
                        chunk.get("text", ""),
                        " ".join(chunk.get("tags", [])),
                        " ".join(chunk.get("answer_intents", [])),
                        " ".join(chunk.get("canonical_questions", [])),
                    ]
                )
            )
            for chunk in self.chunks
        ]
        self.doc_intents = [chunk_intents(chunk) for chunk in self.chunks]
        self.doc_counts = [Counter(tokens) for tokens in self.doc_tokens]
        self.doc_lengths = [max(1.0, math.sqrt(sum(count * count for count in counts.values()))) for counts in self.doc_counts]
        doc_frequency = Counter()
        for tokens in self.doc_tokens:
            doc_frequency.update(set(tokens))
        total_docs = max(1, len(self.chunks))
        self.idf = {
            term: math.log((total_docs + 1) / (frequency + 1)) + 1.0
            for term, frequency in doc_frequency.items()
        }

    def _search_single(self, query: str, top_k: int = DEFAULT_TOP_K, min_score: float | None = None) -> list[Hit]:
        query_terms = tokenize(query)
        if not query_terms:
            return []
        query_norm = normalize(query)
        intents = query_intents(query)
        scores = []
        query_counter = Counter(query_terms)
        for index, counts in enumerate(self.doc_counts):
            doc_intents = self.doc_intents[index]
            if intents and not (intents & doc_intents):
                continue
            score = 0.0
            for term, query_tf in query_counter.items():
                if term in counts:
                    score += (1.0 + math.log(counts[term])) * self.idf.get(term, 1.0) * query_tf
            tag_blob = normalize(" ".join(self.chunks[index].get("tags", [])))
            for term in query_terms:
                if term in tag_blob:
                    score += 0.65
            if ("ngoc hoi" in query_norm or "dong da" in query_norm) and (
                "ngoc_hoi" in tag_blob or "dong_da" in tag_blob or "ngoc_hoi_dong_da" in tag_blob
            ):
                score += 7.0
            if ("rach gam" in query_norm or "xoai mut" in query_norm) and "rach_gam_xoai_mut" in tag_blob:
                score += 7.0
            if "nghe an" in query_norm and "nghe_an" in tag_blob:
                score += 5.0
            if is_diplomacy_query(query) and any(
                tag in tag_blob
                for tag in (
                    "diplomacy",
                    "qing",
                    "can_long",
                    "phuc_khang_an",
                    "ngo_thi_nham",
                    "pham_cong_tri",
                    "fake_king",
                    "investiture",
                    "tribute",
                    "contested",
                    "statecraft",
                )
            ):
                score += 8.0
            if is_identity_query(query) and (
                "identity" in tag_blob or "profile" in tag_blob or "origin" in tag_blob or "enthronement" in tag_blob
            ):
                score += 6.0
            if intents and (intents & doc_intents):
                score += 9.0 + (2.0 * len(intents & doc_intents))
            if is_identity_query(query) and "guardrail" in tag_blob:
                score = 0.0
            if score > 0:
                scores.append(Hit(self.chunks[index], score / self.doc_lengths[index]))
        ranked = sorted(scores, key=lambda hit: hit.score, reverse=True)
        threshold = min_score if min_score is not None else configured_score_threshold(0.12)
        if ranked and ranked[0].score < threshold:
            return []
        return ranked[:top_k]

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        min_score: float | None = None,
        profile: dict | None = None,
    ) -> list[Hit]:
        variants = query_variants(query, profile)
        intents = query_intents(query)
        hits = []
        for variant in variants:
            variant_min_score = 0.01 if intents else min_score
            hits.extend(self._search_single(variant, top_k=max(top_k * 3, top_k), min_score=variant_min_score))
        threshold = min_score if min_score is not None else configured_score_threshold(0.12)
        if intents:
            threshold = min(threshold, 0.12)
        return rerank_hits(query, hits, top_k=top_k, min_score=threshold)


class VectorRetriever:
    def __init__(
        self,
        chunks: Iterable[dict],
        persist_dir: Path | str | None = None,
        model_name: str | None = None,
        score_threshold: float | None = None,
        character_id: str = DEFAULT_CHARACTER_ID,
    ):
        self.chunks = list(chunks)
        self.character_id = character_id
        self.persist_dir = Path(persist_dir) if persist_dir else configured_index_dir(character_id)
        self.embedding_provider = configured_embedding_provider()
        self.model_name = model_name or (
            configured_gemini_embedding_model() if self.embedding_provider == "gemini" else configured_embedding_model()
        )
        self.score_threshold = score_threshold if score_threshold is not None else configured_score_threshold()
        self._fallback = SimpleRetriever(self.chunks)
        self._backend = "simple"
        self._collection = None
        self._embedding_model = None
        self._init_vector_backend()

    def _dataset_fingerprint(self) -> str:
        payload = json.dumps(
            [
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "text": chunk.get("text"),
                    "tags": chunk.get("tags", []),
                    "answer_intents": chunk.get("answer_intents", []),
                    "canonical_questions": chunk.get("canonical_questions", []),
                }
                for chunk in self.chunks
            ],
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _embedding_text(self, chunk: dict) -> str:
        return "\n".join(
            [
                chunk.get("topic_title", ""),
                chunk.get("fact", ""),
                chunk.get("text", ""),
                " ".join(chunk.get("canonical_questions", [])),
                " ".join(chunk.get("tags", [])),
                " ".join(chunk.get("answer_intents", [])),
            ]
        )

    def _safe_wipe_index_dir(self) -> None:
        if self.persist_dir.name != self.character_id:
            return
        if self.persist_dir.exists():
            shutil.rmtree(self.persist_dir)

    def _index_metadata_changed(self, previous: dict, current: dict) -> bool:
        keys = ("fingerprint", "embedding_provider", "model_name", "dimension", "character_id")
        return any(previous.get(key) != current.get(key) for key in keys)

    def _init_vector_backend(self) -> None:
        try:
            import chromadb
        except Exception:
            return

        try:
            fingerprint = self._dataset_fingerprint()
            metadata_path = self.persist_dir / "metadata.json"
            previous = {}
            if metadata_path.exists():
                previous = json.loads(metadata_path.read_text(encoding="utf-8"))
            elif self.persist_dir.exists() and any(self.persist_dir.iterdir()):
                self._safe_wipe_index_dir()
            embedding_model = cached_embedding_backend(self.embedding_provider, self.model_name)
            dimension = embedding_dimension(embedding_model)
            current_metadata = {
                "fingerprint": fingerprint,
                "embedding_provider": self.embedding_provider,
                "model_name": self.model_name,
                "dimension": dimension,
                "character_id": self.character_id,
            }
            if previous and self._index_metadata_changed(previous, current_metadata):
                self._safe_wipe_index_dir()
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            metadata_path = self.persist_dir / "metadata.json"
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            collection = client.get_or_create_collection(
                name=self.character_id,
                metadata={"hnsw:space": "cosine"},
            )
            if self._index_metadata_changed(previous, current_metadata):
                existing = collection.get(include=[])
                existing_ids = existing.get("ids", [])
                if existing_ids:
                    collection.delete(ids=existing_ids)
                documents = [self._embedding_text(chunk) for chunk in self.chunks]
                embeddings = encode_embeddings(embedding_model, documents)
                ids = [chunk["chunk_id"] for chunk in self.chunks]
                metadatas = [
                    {
                        "index": index,
                        "answer_intents": " ".join(chunk.get("answer_intents", [])),
                        "tags": " ".join(chunk.get("tags", [])),
                        "source_quality": chunk.get("source_quality", ""),
                        "source_tier": chunk_source_tier(chunk),
                        "source_quality_score": source_quality_score(chunk),
                    }
                    for index, chunk in enumerate(self.chunks)
                ]
                collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
                metadata_path.write_text(
                    json.dumps(current_metadata, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            self._collection = collection
            self._embedding_model = embedding_model
            self._backend = "vector"
        except Exception:
            self._collection = None
            self._embedding_model = None
            self._backend = "simple"

    def _search_vector_single(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[Hit]:
        intents = query_intents(query)
        query_norm = normalize(query)
        query_embedding = encode_embeddings(self._embedding_model, [query])[0]
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(max(top_k * 6, top_k), len(self.chunks)),
            include=["distances", "metadatas"],
        )
        hits = []
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        for chunk_id, distance, metadata in zip(ids, distances, metadatas):
            index = int(metadata["index"])
            chunk = self.chunks[index]
            doc_intents = chunk_intents(chunk)
            if intents and not (intents & doc_intents):
                continue
            score = max(0.0, 1.0 - float(distance))
            if intents and (intents & doc_intents):
                score += min(0.18, 0.06 * len(intents & doc_intents))
            score += lexical_anchor_boost(query_norm, chunk)
            hits.append(Hit(chunk, min(score, 1.0)))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        min_score: float | None = None,
        profile: dict | None = None,
    ) -> list[Hit]:
        threshold = min_score if min_score is not None else self.score_threshold
        intents = query_intents(query)
        if intents:
            threshold = min(threshold, 0.12)
        if self._backend != "vector" or self._collection is None or self._embedding_model is None:
            return self._fallback.search(query, top_k=top_k, min_score=threshold, profile=profile)

        hits = []
        for variant in query_variants(query, profile):
            hits.extend(self._search_vector_single(variant, top_k=min(max(top_k * 6, top_k), len(self.chunks))))
        ranked = rerank_hits(query, hits, top_k=top_k, min_score=threshold)
        if ranked:
            return ranked
        return self._fallback.search(query, top_k=top_k, min_score=0.01 if intents else threshold, profile=profile)


def is_legacy_afterlife_query(query: str, profile: dict | None = None) -> bool:
    normalized = normalize(query)
    character_id = profile_character_id(profile)
    if character_id == "ho_chi_minh":
        return any(
            has_phrase(normalized, term)
            for term in ("chien dich ho chi minh", "30 4 1975", "30/4/1975", "nam 1975", "thong nhat")
        )
    return False


def is_out_of_period(query: str, death_year: int = 1792, profile: dict | None = None) -> bool:
    if is_legacy_afterlife_query(query, profile):
        return False
    normalized = normalize(query)
    if re.search(r"\bA\.?I\.?\b", query):
        return True
    dated_terms = {
        "dien bien phu": 1954,
        "the chien": 1914,
        "the chien thu nhat": 1914,
        "the chien thu 1": 1914,
        "the chien thu hai": 1939,
        "the chien thu 2": 1939,
        "chien tranh the gioi": 1914,
        "chien tranh the gioi thu nhat": 1914,
        "chien tranh the gioi thu 1": 1914,
        "chien tranh the gioi thu hai": 1939,
        "chien tranh the gioi thu 2": 1939,
        "world war": 1914,
        "world war i": 1914,
        "world war ii": 1939,
        "ww1": 1914,
        "ww2": 1939,
    }
    for term in MODERN_TERMS:
        if not has_phrase(normalized, term):
            continue
        if term in dated_terms:
            return death_year < dated_terms[term]
        return True
    years = [int(match) for match in re.findall(r"\b(1[8-9]\d{2}|20\d{2}|21\d{2})\b", normalized)]
    return any(year > death_year for year in years)


def is_anachronistic_warfare_query(query: str) -> bool:
    normalized = normalize(query)
    return any(has_phrase(normalized, term) for term in ANACHRONISTIC_WARFARE_TERMS)


def is_diplomacy_query(query: str) -> bool:
    normalized = normalize(query)
    return any(has_phrase(normalized, term) for term in DIPLOMACY_QUERY_TERMS)


def is_unsupported_claim(query: str) -> bool:
    normalized = normalize(query)
    if "luong quang" in normalized:
        return True
    if any(has_phrase(normalized, term) for term in UNSUPPORTED_SPECIFIC_TERMS):
        return True
    return "truyen thuyet" in normalized and any(term in normalized for term in ("xac nhan", "co dung", "dung khong"))


def has_uncovered_year_claim(query: str, hits: list[Hit]) -> bool:
    if is_anachronistic_warfare_query(query) or is_diplomacy_query(query):
        return False
    if query_intents(query) & {"battle_reflection", "micro_tactics", "military", "military_doctrine"}:
        return False
    normalized = normalize(query)
    years = re.findall(r"\b(17\d{2})\b", normalized)
    if not years:
        return False
    source_blob = normalize(" ".join(hit.chunk.get("text", "") + " " + hit.chunk.get("fact", "") for hit in hits))
    return any(year not in source_blob for year in years)


def compact_text(text: str, max_words: int = 72) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(" ,.;") + "..."


def is_generated_answer_acceptable(query: str, answer: str) -> bool:
    normalized = normalize(answer)
    if any(
        phrase in normalized
        for phrase in (
            "khong co du lieu",
            "du lieu hien co",
            "tu lieu hien co",
            "khong thay can cu",
            "khong co can cu",
            "khong tim thay",
            "trong ngu canh",
            "cau hoi ay con rong",
            "hay hoi ro hon",
        )
    ):
        return False
    if is_diplomacy_query(query):
        if any(
            phrase in normalized
            for phrase in (
                "chu hau tuyet doi",
                "phuc tung tuyet doi",
                "phu phuc tuyet doi",
                "khong co can cu",
                "khong thay can cu",
            )
        ):
            return False
        return any(
            phrase in normalized
            for phrase in ("giang hoa", "cau phong", "bang giao", "can long", "ta toi")
        )
    return True


def first_person_for(profile: dict) -> str:
    character_id = profile_character_id(profile)
    if character_id == "ho_chi_minh":
        return "Bác"
    if character_id == "vo_nguyen_giap":
        return "tôi"
    return "ta"


def listener_for(profile: dict) -> str:
    character_id = profile_character_id(profile)
    if character_id == "ho_chi_minh":
        return "các cháu"
    if character_id == "vo_nguyen_giap":
        return "đồng chí"
    if character_id == "nguyen_trai":
        return "người"
    return "ngươi"


def self_names_for(profile: dict) -> list[str]:
    metadata = profile.get("character_metadata", {})
    names = [metadata.get("name", ""), metadata.get("full_name", "")]
    names.extend(metadata.get("aliases", []))
    return [name for name in dict.fromkeys(names) if name]


def local_route_query(query: str, profile: dict) -> dict:
    normalized = normalize(query)
    metadata = profile["character_metadata"]
    intent = "history_fact"
    needs_rag = True
    optimized_search_query = query
    confidence = 0.62

    if is_pure_smalltalk_query(query):
        intent, needs_rag, optimized_search_query, confidence = "smalltalk", False, "", 0.88
    elif is_private_life_query(query):
        intent, needs_rag, optimized_search_query, confidence = "private_life", False, "", 0.82
    elif is_anachronistic_warfare_query(query) or is_out_of_period(query, metadata["death_year"], profile):
        intent, needs_rag, optimized_search_query, confidence = "anachronism_trap", False, "", 0.86
    elif is_quang_trung_self_name_confusion(query, profile) or is_identity_query(query):
        intent, needs_rag, optimized_search_query, confidence = "identity", False, "", 0.82
    elif is_birth_query_text(normalized):
        intent, needs_rag, optimized_search_query, confidence = "birth", False, "", 0.95
    elif is_origin_query_text(normalized):
        intent, needs_rag, optimized_search_query, confidence = "origin", False, "", 0.92
    elif is_death_query_text(normalized):
        intent, needs_rag, optimized_search_query, confidence = "death", False, "", 0.9
    elif is_real_name_query_text(normalized):
        intent, needs_rag, optimized_search_query, confidence = "real_name", False, "", 0.9
    elif is_unsupported_claim(query):
        intent, needs_rag, optimized_search_query, confidence = "anachronism_trap", False, "", 0.8
    elif query_intents(query) & {"ideology", "military_doctrine"}:
        intent, optimized_search_query, confidence = "philosophy", rewrite_query(query, profile), 0.72
    elif query_intents(query) & {"battle_reflection", "micro_tactics", "military"}:
        intent, optimized_search_query, confidence = "history_battle", rewrite_query(query, profile), 0.74

    return {
        "intent": intent,
        "needs_rag": needs_rag,
        "optimized_search_query": optimized_search_query,
        "confidence": confidence,
        "source": "deterministic",
    }


def persona_fact(fact: str, profile: dict) -> str:
    text = fact.strip()
    pronoun = first_person_for(profile)
    for name in self_names_for(profile):
        escaped = re.escape(name)
        text = re.sub(rf"\bđồng chí\s+{escaped}\b", pronoun, text, flags=re.IGNORECASE)
        text = re.sub(rf"\bChủ tịch\s+{escaped}\b", pronoun, text, flags=re.IGNORECASE)
        text = re.sub(rf"\bĐại tướng\s+{escaped}\b", pronoun, text, flags=re.IGNORECASE)
        text = re.sub(rf"\b{escaped}\b", pronoun, text, flags=re.IGNORECASE)
    text = re.sub(rf"\b{re.escape(pronoun)}\s+{re.escape(pronoun)}\b", pronoun, text, flags=re.IGNORECASE)
    if pronoun == "tôi" and text.startswith("tôi "):
        text = "Tôi " + text[4:]
    if pronoun == "ta" and text.startswith("ta "):
        text = "Ta " + text[3:]
    if profile_character_id(profile) == "ho_chi_minh":
        text = re.sub(
            r"Ngày 5/6/1911,\s*người thanh niên\s+Bác\s*\(lấy tên\s+Bác\)\s*rời",
            "Ngày 5/6/1911, khi còn là người thanh niên, Bác rời",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"Bác\s*\(tên khai sinh\s+Bác,\s*sinh\s+19/5/1890[^)]*\)\s*là\s*",
            "Bác sinh ngày 19/5/1890 tại Nam Đàn, Nghệ An, và là ",
            text,
            flags=re.IGNORECASE,
        )
    return text


def persona_facts(hits: list[Hit], profile: dict, limit: int = 3) -> list[str]:
    facts = []
    seen = set()
    for hit in hits:
        fact = hit.chunk.get("fact", "").strip()
        if fact:
            rewritten = persona_fact(fact, profile)
            key = normalize(rewritten)
            if key and key not in seen:
                facts.append(rewritten)
                seen.add(key)
    return facts[:limit]


def build_ideology_answer(query: str, profile: dict, hits: list[Hit]) -> str:
    character_id = profile_character_id(profile)
    facts = persona_facts(hits, profile, limit=3)
    if character_id == "vo_nguyen_giap":
        answer = (
            "Tôi nhìn việc đánh giặc trước hết là việc của nhân dân. Quân đội không thể tách khỏi dân, "
            "chiến trường không chỉ nằm trên bản đồ mà còn nằm trong ý chí chính trị, hậu phương, cách tổ chức lực lượng "
            "và khả năng chọn đúng thời cơ. Khi cần đánh nhanh mà không chắc thắng thì phải biết dừng lại; khi đã thấy "
            "địch mạnh về hỏa lực, ta càng phải lấy thế trận, tinh thần, hậu cần và cách đánh chắc để thắng."
        )
    elif character_id == "ho_chi_minh":
        answer = (
            "Bác nghĩ điều cốt lõi là độc lập cho dân tộc, tự do và hạnh phúc cho nhân dân. Nước độc lập mà dân không được học, "
            "không được no, không được làm chủ thì độc lập ấy chưa trọn vẹn. Vì vậy cách mạng phải dựa vào dân, đoàn kết dân, "
            "giữ đạo đức trong sáng và đặt lợi ích của Tổ quốc, của đồng bào lên trên hết."
        )
    elif character_id == "nguyen_trai":
        answer = (
            "Ta nói nhân nghĩa trước hết là yên dân. Việc lớn không chỉ ở thắng một trận, mà ở làm cho dân thoát nạn binh đao, "
            "để nước có văn hiến, bờ cõi, phong tục và lòng người riêng. Dùng quân mà không biết lòng dân thì khó bền; "
            "dùng lý lẽ để khuất phục lòng người cũng là một phép đánh giặc."
        )
    elif character_id == "tran_hung_dao":
        answer = (
            "Ta giữ nước bằng thế quân, nhưng gốc sâu hơn là lòng dân và kỷ luật tướng sĩ. Muốn chống giặc mạnh, trên dưới phải đồng lòng, "
            "tướng không được quên nhục nước, quân không được quên nghĩa lớn, triều đình phải biết khoan thư sức dân để làm kế sâu rễ bền gốc."
        )
    else:
        answer = (
            "Ta trị nước và đánh giặc bằng điều thực dụng: giữ lòng dân, chọn thời cơ, dùng người có tài, "
            "và không để quân thù kịp gom lại thế trận. Việc lớn phải nhìn cả dân sinh lẫn binh cơ."
        )
    if facts:
        if character_id == "ho_chi_minh":
            facts = []
        answer += " " + " ".join(facts[:2])
    return answer


def build_bach_dang_answer(profile: dict, hits: list[Hit]) -> str:
    return (
        "Nếu hỏi Bạch Đằng năm 1288, ta nói đó là trận phải thắng bằng thế sông nước và lòng người. "
        "Ta chọn khúc sông có thủy triều lên xuống mạnh, cho đóng bãi cọc ngầm, rồi dùng thuyền nhỏ khiêu chiến "
        "dụ thủy quân Nguyên của Ô Mã Nhi tiến sâu vào nơi đã định. Khi nước rút, thuyền lớn mắc cọc, không còn xoay trở; "
        "quân ta từ hai bờ và các thuyền nhẹ đồng loạt đánh xuống. Thắng lợi ấy không chỉ phá tan đạo thủy quân, "
        "mà còn chặn hẳn mưu xâm lược lần nữa của giặc Nguyên Mông."
    )


def build_broad_persona_answer(query: str, profile: dict, hits: list[Hit]) -> str:
    character_id = profile_character_id(profile)
    facts = persona_facts(hits, profile, limit=3)
    if facts:
        if character_id == "ho_chi_minh":
            return "Bác nói ngắn gọn thế này: " + " ".join(facts)
        if character_id == "vo_nguyen_giap":
            return "Tôi trả lời từ kinh nghiệm chiến trường và tổ chức lực lượng: " + " ".join(facts)
        if character_id == "nguyen_trai":
            return "Ta xét việc ấy theo đạo nhân nghĩa và thời thế: " + " ".join(facts)
        if character_id == "tran_hung_dao":
            return "Ta xét việc ấy theo phép giữ nước và lòng quân dân: " + " ".join(facts)
        return "Ta nói theo việc nước và binh cơ: " + " ".join(facts)
    if character_id == "ho_chi_minh":
        return "Bác luôn đặt dân tộc và nhân dân lên trước. Việc gì có lợi cho dân, cho nước thì phải hết sức làm; việc gì hại đến dân thì phải hết sức tránh."
    if character_id == "vo_nguyen_giap":
        return "Tôi luôn nhìn chiến tranh bằng con mắt toàn cục: chính trị, nhân dân, hậu cần, thế trận và thời cơ phải đi cùng nhau thì quân đội mới thắng được kẻ mạnh hơn."
    if character_id == "nguyen_trai":
        return "Ta lấy nhân nghĩa làm gốc: yên dân, trừ bạo, giữ văn hiến và dùng cả lý lẽ lẫn thế thời để khuất phục kẻ xâm lăng."
    if character_id == "tran_hung_dao":
        return "Ta giữ nước bằng lòng dân, kỷ luật tướng sĩ và sự chuẩn bị lâu bền; quân mạnh mà dân mỏi thì gốc đã lung lay."
    return "Ta xét việc ấy ở đại cuộc: dân, nước, thời cơ và phép dùng người phải hợp lại thì việc lớn mới thành."


def build_afterlife_answer(query: str, profile: dict) -> str:
    metadata = profile["character_metadata"]
    pronoun = first_person_for(profile)
    listener = listener_for(profile)
    if is_legacy_afterlife_query(query, profile):
        return (
            f"Việc ấy diễn ra sau khi {pronoun} đã đi xa năm {metadata['death_year']}. "
            "Nếu xét theo sử sách đời sau, đó là một dấu mốc hoàn thành khát vọng thống nhất non sông, "
            "điều mà cả đời người cách mạng luôn mong mỏi. Nhưng phải nói cho đúng: "
            f"{pronoun} không phải người trực tiếp chứng kiến ngày ấy."
        )
    return (
        f"{listener.capitalize()} hỏi chuyện đời sau khi {pronoun} đã mất năm {metadata['death_year']}. "
        f"Việc ấy không thuộc đời sống trực tiếp của {pronoun}; nếu muốn bàn, phải đặt nó trong sử sách của thời sau, "
        "chớ gán thành ký ức của người đã khuất."
    )


def build_private_life_answer(query: str, profile: dict) -> str:
    character_id = profile_character_id(profile)
    if character_id == "ho_chi_minh":
        return (
            "Chuyện riêng tư của Bác, nhất là chuyện hôn nhân, đời sau còn có nhiều lời kể và cách hiểu khác nhau. "
            "Bác không muốn lấy điều chưa thật chắc để làm lời khẳng định trước các cháu. Điều Bác có thể nói rõ là "
            "đời mình đã đặt độc lập của nước, tự do của dân và hạnh phúc của đồng bào lên trước hết."
        )
    if character_id == "vo_nguyen_giap":
        return (
            "Chuyện gia đình là phần rất riêng của đời tôi, nhưng cũng không nên nói lấp lửng như một khẩu hiệu. "
            "Tôi từng có gia đình, từng chịu mất mát trong chiến tranh, và chính những mất mát ấy càng làm tôi hiểu "
            "giá trị của độc lập, của sự sống con người, để khi cầm quân phải cân nhắc từng sinh mạng chiến sĩ."
        )
    if character_id == "nguyen_trai":
        return (
            "Chuyện riêng trong đời ta không nên đem làm lời đồn đãi cho vui miệng. Nếu hỏi để hiểu con người, hãy nhớ "
            "rằng một kẻ sĩ cũng có nỗi đau, tình thân và oan khuất; nhưng khi bàn việc nước, ta đặt nhân nghĩa, yên dân "
            "và trách nhiệm với non sông lên trước."
        )
    if character_id == "tran_hung_dao":
        return (
            "Chuyện gia thất của ta không phải điều nên đem ra xét như chuyện ngoài chợ. Người giữ việc lớn phải biết "
            "lấy đạo nhà, đạo nước và lòng trung nghĩa làm trọng; điều gì không giúp hiểu phép giữ nước thì chớ biến "
            "thành lời đồn."
        )
    return (
        "Chuyện riêng của ta không phải thứ để hậu thế gạn hỏi như chuyện đồn. Nếu muốn hiểu con người ta, hãy nhìn "
        "việc cầm quân, việc trị nước và những lựa chọn trước vận nước, vì ở đó mới thấy rõ chí hướng."
    )


def build_identity_answer(profile: dict, hits: list[Hit]) -> str:
    metadata = profile["character_metadata"]
    pronoun = first_person_for(profile)
    name = metadata["name"]
    era = metadata.get("era", "")
    traits = ", ".join(metadata.get("personality_traits", [])[:3])
    facts = [hit.chunk.get("fact", "") for hit in hits if hit.chunk.get("fact")]
    if facts:
        return f"{pronoun.capitalize()} là {name}, sống trong thời {era}. " + " ".join(facts[:2])
    return f"{pronoun.capitalize()} là {name}, sống trong thời {era}. Nếu muốn hiểu đời {pronoun}, hãy hỏi vào sự nghiệp, tư tưởng và những việc lớn đã gắn với vận nước."


FACTUAL_ANSWER_BANK = {
    "quang_trung": {
        "birth": "Ta sinh năm 1753. Tên thật của ta là Nguyễn Huệ; Quang Trung là niên hiệu khi ta lên ngôi hoàng đế Tây Sơn. Muốn hiểu đời ta, hãy nhìn vào sự nghiệp dẹp loạn, đánh quân Xiêm ở Rạch Gầm - Xoài Mút và đại phá quân Thanh ở Ngọc Hồi - Đống Đa.",
        "origin": "Ta xuất thân từ phong trào Tây Sơn, gắn với đất Bình Định và cuộc biến động cuối thế kỷ XVIII. Đời cầm quân của ta sau đó trải qua Phú Xuân, Nghệ An, Thăng Long và các chiến trường Nam - Bắc.",
        "real_name": "Nguyễn Huệ chính là tên thật của ta. Quang Trung là niên hiệu hoàng đế, Bắc Bình Vương là tước hiệu trước khi lên ngôi; đó không phải là những người khác nhau.",
        "identity": "Nguyễn Huệ chính là ta; Quang Trung là niên hiệu khi ta lên ngôi, không phải hai người và cũng không phải anh em. Nếu hỏi hai tên ấy là gì của nhau, thì phải nói cho đúng: một là tên người, một là niên hiệu của cùng một con người trong lịch sử Tây Sơn.",
        "death": "Ta mất năm 1792, khi nhiều dự định trị nước và canh tân còn dang dở. Vì vậy khi hỏi chuyện sau năm ấy, chớ gán thành ký ức trực tiếp của ta.",
    },
    "ho_chi_minh": {
        "birth": "Bác sinh ngày 19/5/1890, tại quê hương Nghệ An. Tên khai sinh của Bác là Nguyễn Sinh Cung; về sau trong các chặng đường hoạt động cách mạng, Bác còn mang các tên Nguyễn Tất Thành, Nguyễn Ái Quốc, Văn Ba và Hồ Chí Minh.",
        "origin": "Quê Bác ở Kim Liên, Nam Đàn, Nghệ An; đó là mảnh đất giàu truyền thống yêu nước và hiếu học. Từ quê hương ấy, Bác lớn lên trong cảnh nước mất nhà tan, rồi đi nhiều nơi để tìm con đường cứu nước cho dân tộc.",
        "real_name": "Tên khai sinh của Bác là Nguyễn Sinh Cung. Khi lớn lên và hoạt động cách mạng, Bác từng mang tên Nguyễn Tất Thành, Nguyễn Ái Quốc, Văn Ba; Hồ Chí Minh là tên gắn với chặng đường lãnh đạo cách mạng Việt Nam.",
        "identity": "Bác là Hồ Chí Minh, người Việt Nam yêu nước đã dành đời mình cho độc lập của Tổ quốc và tự do, hạnh phúc của nhân dân. Những tên Nguyễn Sinh Cung, Nguyễn Tất Thành, Nguyễn Ái Quốc, Văn Ba là các tên gắn với những chặng đường khác nhau của cùng một con người.",
        "death": "Bác đi xa ngày 2/9/1969. Điều Bác căn dặn trong Di chúc vẫn xoay quanh một việc lớn: giữ đoàn kết, chăm lo nhân dân, bồi dưỡng thế hệ sau và tiếp tục xây dựng nước Việt Nam độc lập, thống nhất.",
    },
    "tran_hung_dao": {
        "birth": "Ta sinh khoảng năm 1228. Tên thật là Trần Quốc Tuấn, về sau được tôn là Hưng Đạo Đại Vương vì công lao chống quân Nguyên Mông và giữ nước Đại Việt.",
        "origin": "Ta là người họ Trần, gắn với vùng Nam Định và Vạn Kiếp. Xuất thân vương thất nhưng điều ta đặt lên trên hết không phải thù riêng dòng họ, mà là vận nước Đại Việt.",
        "real_name": "Tên thật của ta là Trần Quốc Tuấn. Trần Hưng Đạo hay Hưng Đạo Đại Vương là tước hiệu, danh xưng đời sau kính gọi vì công lao giữ nước.",
        "identity": "Ta là Trần Quốc Tuấn, người đời thường gọi Trần Hưng Đạo hoặc Hưng Đạo Đại Vương. Những danh xưng ấy chỉ về cùng một người, không phải các nhân vật khác nhau.",
        "death": "Ta mất năm 1300 tại Vạn Kiếp. Trước khi mất, điều ta căn dặn vẫn là khoan thư sức dân để làm kế sâu rễ bền gốc, vì giữ nước phải giữ từ lòng dân.",
    },
    "nguyen_trai": {
        "birth": "Ta sinh năm 1380. Hiệu là Ức Trai; đời ta gắn với vận nước từ cuối Trần, Hồ đến khởi nghĩa Lam Sơn và triều Hậu Lê.",
        "origin": "Quê quán của ta gắn với Chi Ngại ở Hải Dương và Nhị Khê ở Hà Nội. Dù ở nơi nào, điều ta giữ trong lòng vẫn là đạo nhân nghĩa, yên dân và mối lo cho xã tắc.",
        "real_name": "Tên ta là Nguyễn Trãi, hiệu Ức Trai. Khi người đời gọi Ức Trai, đó là gọi hiệu của ta, không phải một người khác.",
        "identity": "Ta là Nguyễn Trãi, hiệu Ức Trai, một kẻ sĩ đã theo Lê Lợi trong khởi nghĩa Lam Sơn và dùng văn chương, mưu lược để góp phần dựng lại nền độc lập Đại Việt.",
        "death": "Ta mất năm 1442 trong vụ án Lệ Chi Viên, một nỗi oan lớn của lịch sử. Khi xét đời ta, xin nhìn cả công lao với Lam Sơn, Bình Ngô đại cáo, tư tưởng nhân nghĩa và bi kịch cuối đời.",
    },
    "vo_nguyen_giap": {
        "birth": "Tôi sinh ngày 25/8/1911 tại xã Lộc Thủy, huyện Lệ Thủy, tỉnh Quảng Bình. Từ một thầy giáo dạy sử, tôi đi vào con đường cách mạng và quân sự vì độc lập của Tổ quốc.",
        "origin": "Tôi quê ở Lộc Thủy, Lệ Thủy, Quảng Bình. Mảnh đất ấy cho tôi hiểu rất sớm thế nào là lòng yêu nước, ý chí học tập và trách nhiệm với nhân dân.",
        "real_name": "Tên tôi là Võ Nguyên Giáp. Những cách gọi như Tướng Giáp, Đại tướng Võ Nguyên Giáp đều chỉ cùng một người trong các vai trò khác nhau của đời hoạt động cách mạng và quân sự.",
        "identity": "Tôi là Võ Nguyên Giáp, người được giao chỉ huy nhiều chiến dịch lớn trong kháng chiến, trong đó có Điện Biên Phủ năm 1954. Điều quan trọng nhất không phải tên tuổi cá nhân, mà là thắng lợi của toàn dân, toàn quân.",
        "death": "Tôi qua đời năm 2013. Nhìn lại đời mình, điều lớn nhất vẫn là được phục vụ Tổ quốc, nhân dân và sự nghiệp độc lập dân tộc.",
    },
}


LOCAL_FALLBACK_BANK = {
    "quang_trung": {
        "smalltalk": "Ta đang nghe. Nếu muốn hỏi cho ra điều, hãy hỏi thẳng về thân thế, việc cầm quân, Ngọc Hồi - Đống Đa, Rạch Gầm - Xoài Mút hoặc phép trị nước của Tây Sơn.",
        "history_battle": "Nếu hỏi việc binh, ta nói trước hết phải xét thời cơ, địa thế và lòng quân. Ở Rạch Gầm - Xoài Mút, ta chọn đúng khúc sông để khóa đầu chặn đuôi quân Xiêm. Ở Ngọc Hồi - Đống Đa, ta lấy thần tốc, chia mũi và đánh vào chỗ quân Thanh chủ quan để giải phóng Thăng Long.",
        "philosophy": "Ta trị nước không chỉ bằng gươm giáo. Sau khi dẹp giặc, việc lớn là gom lòng người, khuyến nông, trọng học, dùng người có tài và đặt phép nước cho yên dân. Quân mạnh mà dân rã thì thế nước không bền.",
        "anachronism_trap": "Việc ấy thuộc đời sau, không nằm trong thời ta. Nếu muốn hiểu cách ta kêu gọi quân sĩ, hãy nhìn lời phủ dụ, cuộc duyệt binh ở Nghệ An và khí thế hành quân ra Bắc, chớ đem Internet hay Facebook gán vào thế kỷ XVIII.",
        "private_life": "Chuyện riêng của ta không phải thứ để hỏi như lời đồn. Nếu muốn hiểu con người ta, hãy nhìn những quyết định trước vận nước: đánh giặc, dùng người, giữ dân và dựng phép trị.",
    },
    "ho_chi_minh": {
        "smalltalk": "Bác đang nghe. Các cháu cứ hỏi về thân thế, con đường cứu nước, tư tưởng độc lập tự do, Cách mạng Tháng Tám, Điện Biên Phủ hoặc những lời căn dặn với thế hệ sau.",
        "history_battle": "Bác không nhận chiến thắng nào là của riêng một người. Điện Biên Phủ năm 1954 là thắng lợi của toàn dân, toàn quân sau chín năm kháng chiến chống thực dân Pháp. Thắng lợi ấy buộc đối phương phải ngồi vào bàn đàm phán và công nhận quyền độc lập của dân tộc Việt Nam.",
        "philosophy": "Điều Bác coi là cốt lõi là độc lập cho dân tộc, tự do và hạnh phúc cho nhân dân. Nước độc lập mà dân còn đói, còn dốt, còn không được làm chủ thì độc lập ấy chưa trọn. Vì vậy cách mạng phải dựa vào dân, đoàn kết dân và giữ đạo đức trong sáng.",
        "anachronism_trap": "Facebook, Internet hay những công cụ đời sau không thuộc thời Bác. Thời Bác, việc tuyên truyền dựa vào báo chí, truyền đơn, nói chuyện trực tiếp, tổ chức quần chúng và quan trọng nhất là nói thật điều dân cần nghe.",
        "private_life": "Chuyện riêng của Bác không nên biến thành chuyện đồn đoán. Điều Bác có thể nói rõ là cả đời mình đặt độc lập của nước, tự do của dân và hạnh phúc của đồng bào lên trước hết.",
    },
    "tran_hung_dao": {
        "smalltalk": "Ta đang nghe. Ngươi cứ hỏi về Bạch Đằng, Hịch tướng sĩ, khoan thư sức dân, binh pháp hoặc ba lần kháng chiến chống Nguyên Mông.",
        "history_battle": "Đánh giặc mạnh phải biết tránh sở trường của nó và buộc nó vào địa thế của ta. Ở Bạch Đằng năm 1288, ta dùng thủy triều, bãi cọc và kế nhử địch để phá thủy quân Ô Mã Nhi. Thắng lợi ấy là thắng lợi của địa lợi, kỷ luật và lòng dân Đại Việt.",
        "philosophy": "Giữ nước không chỉ nhờ quân sắc bén. Cái gốc là khoan thư sức dân, làm cho dân còn sức, còn lòng mà bảo vệ xã tắc. Dân là gốc sâu rễ bền; mất dân thì thành cao hào sâu cũng vô ích.",
        "anachronism_trap": "Điều ấy thuộc đời sau, vượt ngoài thời ta. Ta chỉ có thể bàn việc quân Nguyên Mông, lòng dân Đại Việt, binh thư và phép giữ nước của thế kỷ XIII.",
        "private_life": "Chuyện gia thất không phải điều nên đem ra làm lời đồn. Điều đáng hỏi là vì sao ta đặt vận nước lên trên thù riêng dòng họ và giữ lòng trung nghĩa đến cùng.",
    },
    "nguyen_trai": {
        "smalltalk": "Ta đang nghe. Người hãy hỏi về nhân nghĩa, Bình Ngô đại cáo, mưu phạt tâm công, Lam Sơn, Dư địa chí hoặc nỗi oan Lệ Chi Viên.",
        "history_battle": "Trong khởi nghĩa Lam Sơn, chiến thắng không chỉ nhờ gươm giáo mà còn nhờ biết đánh vào lòng người. Khi giặc Minh đã suy, ta dùng thư từ, lý lẽ và thế trận để làm chúng mất ý chí, mở đường cho hòa hiếu sau chiến tranh.",
        "philosophy": "Việc nhân nghĩa cốt ở yên dân. Đánh giặc là để trừ bạo, nhưng dựng nước phải làm cho dân được sống yên, có văn hiến, phong tục, bờ cõi và lòng người riêng. Dân yên thì nước mới bền.",
        "anachronism_trap": "Điều ấy ở ngoài thời ta. Ta không thể nhận biết những vật như AI hay mạng xã hội; nếu muốn bàn đạo nhân nghĩa, hãy trở về với dân, với nước và trách nhiệm của người cầm bút.",
        "private_life": "Chuyện riêng của ta không nên biến thành lời đồn. Nếu hỏi để hiểu con người, hãy nhìn nỗi ưu tư vì dân, vì nước, cùng những oan khuất mà một kẻ sĩ phải chịu trong thời thế nhiễu nhương.",
    },
    "vo_nguyen_giap": {
        "smalltalk": "Tôi đang nghe. Đồng chí cứ hỏi về Điện Biên Phủ, đánh chắc tiến chắc, chiến tranh nhân dân, hậu cần, tổ chức lực lượng hoặc đời hoạt động cách mạng.",
        "history_battle": "Điện Biên Phủ năm 1954 thắng vì ta biết chuyển từ đánh nhanh thắng nhanh sang đánh chắc tiến chắc khi điều kiện chưa bảo đảm chắc thắng. Quyết định ấy khó khăn, nhưng đúng: phải kéo pháo ra, chuẩn bị lại trận địa, tổ chức hậu cần, bao vây, đào hào và làm cho tập đoàn cứ điểm mạnh về hỏa lực bị cô lập từng bước.",
        "philosophy": "Theo tôi, chiến tranh nhân dân là sức mạnh tổng hợp của toàn dân dưới một mục tiêu chính trị đúng đắn. Người chỉ huy phải nhìn cả chính trị, hậu phương, hậu cần, tinh thần chiến sĩ, địa hình và thời cơ; không được lấy ý chí thay cho thực tế chiến trường.",
        "anachronism_trap": "AI và mạng xã hội là công cụ của thời sau. Nếu nói theo nguyên tắc chỉ huy, dù công cụ nào cũng không thay được việc nắm thực tế, kiểm chứng thông tin, chịu trách nhiệm trước chiến sĩ và đặt lợi ích Tổ quốc lên trên hết.",
        "private_life": "Chuyện gia đình là phần riêng của đời tôi, nhưng chiến tranh cũng để lại nhiều mất mát rất thật. Chính vì hiểu giá trị của sinh mạng, người cầm quân càng phải cân nhắc từng quyết định để giảm tổn thất và giành thắng lợi cần thiết.",
    },
}


def build_factual_answer(query: str, profile: dict, intent: str, hits: list[Hit] | None = None) -> str:
    character_id = profile_character_id(profile)
    bank = FACTUAL_ANSWER_BANK.get(character_id, {})
    if character_id == "quang_trung" and intent == "identity" and not is_quang_trung_self_name_confusion(query, profile):
        return (
            "Ta là hoàng đế của triều Tây Sơn, sống vào cuối thế kỷ XVIII. Ta cầm quân trong buổi đất nước rối ren, "
            "từng đánh tan liên quân Xiêm - Nguyễn ở Rạch Gầm - Xoài Mút năm 1785, rồi lên ngôi năm 1788 để thống lĩnh "
            "quân dân ra Bắc đại phá quân Thanh trong chiến dịch Ngọc Hồi - Đống Đa mùa xuân Kỷ Dậu 1789."
        )
    if intent in {"identity", "real_name"}:
        return bank.get(intent) or bank.get("identity") or build_identity_answer(profile, hits or [])
    if intent in bank:
        return bank[intent]
    return build_identity_answer(profile, hits or [])


def build_local_fallback_answer(query: str, profile: dict, intent: str, hits: list[Hit] | None = None) -> str:
    character_id = profile_character_id(profile)
    if intent in {"birth", "origin", "real_name", "death", "identity"}:
        return build_factual_answer(query, profile, intent, hits)
    if intent == "private_life":
        return build_private_life_answer(query, profile)
    if intent == "anachronism_trap":
        return LOCAL_FALLBACK_BANK.get(character_id, {}).get(intent) or build_afterlife_answer(query, profile)
    if intent == "philosophy":
        return LOCAL_FALLBACK_BANK.get(character_id, {}).get(intent) or build_ideology_answer(query, profile, hits or [])
    if intent in {"history_battle", "history_fact"}:
        fallback = LOCAL_FALLBACK_BANK.get(character_id, {}).get("history_battle")
        if fallback:
            return fallback
    if intent == "smalltalk":
        fallback = LOCAL_FALLBACK_BANK.get(character_id, {}).get("smalltalk")
        if fallback:
            return fallback
    return build_broad_persona_answer(query, profile, hits or [])


def select_factual_hits(intent: str, profile: dict, retriever: SimpleRetriever, top_k: int = DEFAULT_TOP_K) -> list[Hit]:
    character_id = profile_character_id(profile)
    metadata = profile["character_metadata"]
    anchors = set()
    if intent == "birth":
        birth_year = metadata.get("birth_year", profile.get("birth_year"))
        if birth_year:
            anchors.add(str(birth_year))
        anchors.update(("sinh", "nam sinh", "ngay sinh", "ten khai sinh"))
        if character_id == "ho_chi_minh":
            anchors.update(("19/5/1890", "1890", "nguyen sinh cung"))
    elif intent == "origin":
        anchors.update(("que", "que quan", "sinh tai", "loc thuy", "le thuy", "kim lien", "nam dan", "nam dinh", "nhi khe", "chi ngai", "nghe an"))
    elif intent in {"identity", "real_name"}:
        anchors.update(normalize(name) for name in self_names_for(profile))
        anchors.update(("ten that", "ten khai sinh", "identity", "profile"))
    elif intent == "death":
        death_year = metadata.get("death_year", profile.get("death_year"))
        if death_year:
            anchors.add(str(death_year))
        anchors.update(("mat", "qua doi", "nam mat", "ngay mat"))

    hits: list[Hit] = []
    for chunk in getattr(retriever, "chunks", []):
        blob = normalize(
            " ".join(
                [
                    chunk.get("topic_title", ""),
                    chunk.get("fact", ""),
                    chunk.get("text", ""),
                    " ".join(chunk.get("tags", [])),
                    " ".join(chunk.get("answer_intents", [])),
                ]
            )
        )
        doc_intents = chunk_intents(chunk)
        score = source_quality_boost(chunk)
        if intent in doc_intents or (intent == "identity" and doc_intents & {"real_name", "profile", "identity"}):
            score += 0.55
        score += 0.12 * sum(1 for anchor in anchors if anchor and anchor in blob)
        if score > 0.15:
            hits.append(Hit(chunk, min(score, 1.0)))
    return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]


def select_intent_hits(query: str, retriever: SimpleRetriever, intent: str, top_k: int = DEFAULT_TOP_K) -> list[Hit]:
    query_norm = normalize(query)
    anchor_terms: dict[str, tuple[str, ...]] = {
        "micro_tactics": (
            "an tet",
            "tet_strategy",
            "30 thang chap",
            "mong 7",
            "tuong binh",
            "voi chien",
            "ky binh",
            "moc rom",
            "hoa ho",
        ),
        "administration": ("tin bai", "giay to tuy than", "thien ha dai tin", "so dinh", "nhan khau"),
        "education": ("chieu lap hoc", "sung chinh", "nha hoc", "chu nom", "dich sach"),
        "scholars": ("ngo thi nham", "nguyen thiep", "la son phu tu", "chieu cau hien"),
    }
    anchors = anchor_terms.get(intent, ())
    hits: list[Hit] = []
    for chunk in getattr(retriever, "chunks", []):
        doc_intents = chunk_intents(chunk)
        if intent not in doc_intents:
            continue
        blob = normalize(
            " ".join(
                [
                    chunk.get("topic_title", ""),
                    chunk.get("fact", ""),
                    chunk.get("text", ""),
                    " ".join(chunk.get("tags", [])),
                    " ".join(chunk.get("answer_intents", [])),
                    " ".join(chunk.get("canonical_questions", [])),
                ]
            )
        )
        score = 0.45 + source_quality_boost(chunk)
        score += 0.18 * sum(1 for anchor in anchors if anchor in query_norm and anchor in blob)
        score += 0.06 * sum(1 for anchor in anchors if anchor in blob)
        if score > 0.45:
            hits.append(Hit(chunk, min(score, 1.0)))
    return sorted(hits, key=lambda hit: hit.score, reverse=True)[:top_k]


def build_generic_character_answer(query: str, profile: dict, hits: list[Hit]) -> tuple[str, str]:
    metadata = profile["character_metadata"]
    pronoun = first_person_for(profile)
    listener = listener_for(profile)
    intents = query_intents(query)
    factual_intents = intents & {"birth", "origin", "real_name", "death"}
    if factual_intents:
        return build_factual_answer(query, profile, next(iter(factual_intents)), hits), "talking"
    if is_anachronistic_warfare_query(query) or is_out_of_period(query, metadata["death_year"], profile):
        return build_afterlife_answer(query, profile), "confused"
    if is_unsupported_claim(query):
        return (
            f"Việc ấy {pronoun} chưa thể nhận là thật. Lịch sử liên quan đến danh dự quốc gia và con người, "
            "nên điều chưa đủ căn cứ thì phải nói là chưa đủ căn cứ."
        ), "confused"
    if is_private_life_query(query):
        return build_private_life_answer(query, profile), "talking"
    if is_pure_smalltalk_query(query):
        topics = ", ".join(
            hit.chunk.get("topic_title", "")
            for hit in hits[:3]
            if hit.chunk.get("topic_title")
        )
        if not topics:
            topics = "thân thế, sự nghiệp, tư tưởng và những việc lớn trong đời"
        return f"{pronoun.capitalize()} đang nghe. {listener.capitalize()} cứ hỏi về {topics}; điều gì có thể nói rõ thì {pronoun} sẽ nói rõ.", "talking"
    if is_identity_query(query):
        return build_identity_answer(profile, hits), "talking"
    if is_legacy_afterlife_query(query, profile):
        facts = [hit.chunk.get("fact", "").strip() for hit in hits if hit.chunk.get("fact")]
        answer = build_afterlife_answer(query, profile)
        if facts:
            answer += " Sử sách đời sau ghi: " + " ".join(facts[:2])
        return answer, "talking"
    if profile_character_id(profile) == "tran_hung_dao" and is_tran_hung_dao_bach_dang_query(query):
        return build_bach_dang_answer(profile, hits), "talking"
    if hits:
        if intents & {"ideology", "military_doctrine"}:
            return build_ideology_answer(query, profile, hits), "talking"
        facts = persona_facts(hits, profile, limit=3)
        if facts:
            return build_broad_persona_answer(query, profile, hits), "talking"
    if intents & {"ideology", "military_doctrine"}:
        return build_local_fallback_answer(query, profile, "philosophy", hits), "talking"
    traits = ", ".join(metadata.get("personality_traits", [])[:3]) or "trách nhiệm với dân nước"
    return build_broad_persona_answer(query, profile, hits), "talking"


def build_answer(query: str, profile: dict, hits: list[Hit]) -> tuple[str, str]:
    metadata = profile["character_metadata"]
    if profile_character_id(profile) != DEFAULT_CHARACTER_ID:
        return build_generic_character_answer(query, profile, hits)
    query_norm = normalize(query)
    intents = query_intents(query)
    factual_intents = intents & {"birth", "origin", "real_name", "death"}
    if factual_intents:
        return build_factual_answer(query, profile, next(iter(factual_intents)), hits), "talking"
    if is_anachronistic_warfare_query(query):
        answer = (
            "Năm Kỷ Dậu 1789 là việc có thật trong đời ta, nhưng đem chiến dịch ấy gán cho Blitzkrieg "
            "hay quân Đức là lẫn lộn đời sau. Ta thắng nhờ thế nước, lòng quân, địa hình, tốc độ hành binh "
            "và cách đánh vào lúc địch chủ quan; không phải nhờ học thuyết binh pháp của người Âu đời sau."
        )
        return answer, "confused"

    if is_out_of_period(query, metadata["death_year"], profile):
        answer = (
            "Ngươi hỏi chuyện đời sau khi ta đã mất năm 1792; đem việc ấy gán cho ta là hồ đồ. "
            "Ta từng lo việc nước Nam cuối thế kỷ XVIII, đánh quân Xiêm, dẹp quân Thanh, dựng lại phép trị nước. "
            "Còn Thế chiến, Internet, máy bay hay những biến cố hàng trăm năm sau, chớ lôi vào đời ta mà nhận bừa."
        )
        return answer, "confused"

    if is_unsupported_claim(query):
        answer = (
            "Việc ấy chưa đủ chứng cứ để ta nhận là thật. Những chi tiết như tên tướng, địa danh và mốc năm "
            "phải xét rất nghiêm; chớ vội biến lời truyền chưa rõ thành sử thực."
        )
        return answer, "confused"

    if is_private_life_query(query):
        return build_private_life_answer(query, profile), "talking"

    if is_quang_trung_self_name_confusion(query, profile):
        answer = (
            "Nguyễn Huệ là tên của ta, còn Quang Trung là niên hiệu khi ta lên ngôi hoàng đế; đó không phải hai người, "
            "cũng chẳng phải anh em. Ngươi hỏi vậy là lẫn danh xưng với con người. Hậu thế có thể gọi ta là Nguyễn Huệ, "
            "Bắc Bình vương hay Hoàng đế Quang Trung, nhưng đều chỉ về một người đã dựng cờ Tây Sơn, phá quân Xiêm ở "
            "Rạch Gầm - Xoài Mút, rồi tiến ra Bắc đánh tan quân Thanh ở Ngọc Hồi - Đống Đa. Nhớ cho rõ: tên người, "
            "tước vị và niên hiệu có thể khác, nhưng chí khí giữ nước ấy chỉ là một."
        )
        return answer, "talking"

    if is_pure_smalltalk_query(query):
        answer = (
            "Ta đang nghe. Hãy hỏi rõ điều ngươi muốn biết về thân thế, việc cầm quân, Rạch Gầm - Xoài Mút, "
            "Nghệ An, hoặc trận Ngọc Hồi - Đống Đa; điều nào đủ chứng cứ thì ta sẽ nói thẳng."
        )
        return answer, "talking"

    if "capital_city" in intents:
        if any(term in query_norm for term in ("qua trinh", "dap thanh", "vat tu", "tho thuyen", "go da", "gach ngoi", "da ong")):
            answer = (
                "Việc dựng Phượng Hoàng Trung Đô không phải chỉ nói suông. Ta giao việc ở vùng Dũng Quyết - Yên Trường, "
                "trưng dụng thợ thuyền, sai quân lính cùng làm, chuyên chở gỗ đá, gạch ngói, đắp thành đất và dùng đá ong "
                "địa phương để xây phần thành trong. Công trình đã có lầu, điện, hành lang, nhưng sự nghiệp còn dang dở vì "
                "ta mất sớm, triều sau không đủ sức theo đến cùng."
            )
        else:
            answer = (
                "Thăng Long là đô cũ, nhưng sau loạn Bắc Hà và việc quân Thanh vừa tràn sang, ta phải tính thế nước lâu dài. "
                "Phú Xuân ở xa, cách trở với Bắc Hà; Nghệ An ở khoảng giữa, đất rộng người đông, có thể khống chế trong Nam "
                "ngoài Bắc và tiện cho dân bốn phương kêu kiện. Bởi vậy ta sai La Sơn Phu tử Nguyễn Thiếp xem đất vùng "
                "Dũng Quyết - Yên Trường để dựng Phượng Hoàng Trung Đô, không phải vì mê lời phong thủy rỗng."
            )
        return answer, "talking"

    if "administration" in intents:
        correction = ""
        if "thien ha dai dinh" in query_norm:
            correction = " Ngươi nói 'Thiên hạ đại định' là chưa đúng chữ; tư liệu ta đang xét ghi là 'Thiên hạ đại tín'."
        answer = (
            f"Đó là tín bài.{correction} Sau loạn lạc, ta bắt làm lại sổ đinh để biết dân cư, rồi cấp thẻ ghi tên họ, quê quán, "
            "điểm chỉ làm tin; giữa thẻ khắc bốn chữ Thiên hạ đại tín. Ai không có thẻ bị coi là dân lậu, có thể bị bắt sung quân. "
            "Phép ấy nhằm giữ trật tự và nắm nhân khẩu, nhưng thi hành nghiêm quá cũng dễ làm dân nhiễu động."
        )
        return answer, "talking"

    if "coinage" in intents:
        answer = (
            "Ta cho đúc tiền mang niên hiệu triều mình, chủ yếu là Quang Trung thông bảo và Quang Trung đại bảo. "
            "Đó là tiền đồng, có nhiều kiểu dáng và mặt lưng khác nhau. Đúc tiền không chỉ để mua bán; đó còn là quyền trị nước: "
            "triều đại mới phải có phép tiền tệ của mình, giúp hàng hóa lưu thông và dần thay thế sự lẫn lộn của tiền cũ, tiền ngoại lai sau thời phân tranh."
        )
        return answer, "talking"

    if "education" in intents:
        answer = (
            "Gươm giáo có thể dẹp loạn, nhưng giữ nước lâu dài phải có học. Vì vậy ta lập Sùng chính viện, cho dịch sách sang chữ Nôm, "
            "ban Chiếu lập học và đặt nhà học đến xã, phủ, huyện, chọn nho sĩ có học thức và đức hạnh làm thầy. "
            "Ta cần người hiểu đạo trị bình, biết chữ nghĩa, có thể ra làm việc trong bộ máy mới; dân có học thì nước mới có nền."
        )
        return answer, "talking"

    if "agriculture" in intents:
        answer = (
            "Sau chiến tranh, ruộng hoang, dân tán, kho lương cạn thì nước không thể yên. Bởi vậy ta chú trọng khuyến nông: "
            "đưa dân trở lại sản xuất, phục hồi ruộng đất, làm cho dân có ăn và triều đình có tài lực. "
            "Đó không chỉ là việc cày cấy, mà là nền của quân lương, thuế khóa và sức mạnh quốc gia."
        )
        return answer, "talking"

    if "scholars" in intents:
        if "ngo thi nham" in query_norm:
            answer = (
                "Với Ngô Thì Nhậm, ta không xét lòng cũ một cách hẹp hòi mà xét tài dùng được cho nước. "
                "Ông hiểu thế Bắc Hà, từng bày kế rút về Tam Điệp để bảo toàn lực lượng, lại giỏi văn thư và sách lược. "
                "Ta trọng dụng, giao việc tổ chức quan lại, chiêu hiền và bang giao với nhà Thanh. Người có tài mà biết đặt dân nước lên trên một họ đã mất thế, ấy là người đáng dùng."
            )
        else:
            answer = (
                "Với La Sơn Phu tử Nguyễn Thiếp và các sĩ phu Bắc Hà, ta dùng lời trọng thị và việc lớn để mời ra giúp nước. "
                "Nhà Lê đã suy, quân Thanh đã mượn cớ đặt chân vào nước Nam; người hiền nếu cứ giữ lòng cũ mà bỏ mặc dân thì sao gọi là đạo? "
                "Ta cần Nguyễn Thiếp xem đất định đô, bàn việc học, dịch sách, mở đường cho giáo hóa; cần người có chữ nghĩa dựng nền trị nước, không chỉ cần người cầm gươm."
            )
        return answer, "talking"

    if "diplomacy" in intents:
        answer = (
            "Sau đại thắng, ta không chỉ dùng gươm giáo. Với Bắc triều, phải dùng lời mềm để dứt việc binh đao: "
            "giảng hòa, cầu phong và đi lại bằng nghi lễ bang giao. Lời tạ tội trong văn thư là phép quyền biến "
            "giữ nước, để Càn Long có đường lui danh dự; chớ hiểu cạn thành chuyện đánh mất nền độc lập. Còn nguyên "
            "văn từng biểu thì phải xét đúng văn thư nào đang được nhắc tới."
        )
        return answer, "talking"

    if "battle_reflection" in intents:
        answer = (
            "Nếu hỏi trận khiến ta hãnh diện nhất, ta nói trước hết đến Ngọc Hồi - Đống Đa mùa xuân Kỷ Dậu 1789. "
            "Đó không chỉ là một trận thắng, mà là lúc lòng quân, tốc độ hành binh và thế đánh nhiều hướng hợp lại thành một ý chí: "
            "đánh tan quân Thanh, giải phóng Thăng Long, giữ lấy danh dự nước Nam. Trước đó Rạch Gầm - Xoài Mút cũng là thắng lợi lớn, "
            "vì ta chọn đúng khúc sông, khóa đầu đuôi thủy quân Xiêm - Nguyễn và phá tan thế can thiệp từ phương Nam. "
            "Nhưng Ngọc Hồi - Đống Đa làm ta nhớ sâu hơn, bởi đó là lúc đất Bắc đang bị giày xéo, lòng người hoang mang, "
            "mà ba quân vẫn đi suốt ngày đêm để giữ lời hẹn vào Thăng Long ăn Tết. Một trận như thế không chỉ thắng bằng gươm giáo, "
            "mà thắng bằng khí thế của cả nước không chịu cúi đầu."
        )
        return answer, "talking"

    if "micro_tactics" in intents:
        if any(term in query_norm for term in ("an tet", "30 thang chap", "mong 7")):
            answer = (
                "Ta cho quân ăn Tết trước là để dứt nỗi nhớ nhà, giữ nhịp hành quân và biến ngày Tết thành lời hẹn thắng trận. "
                "Khi đã nói mồng 7 vào Thăng Long mở tiệc lớn, toàn quân hiểu rằng đường tiến đã định, không được để lễ tiết làm chậm bước. "
                "Quân Thanh chủ quan vì tưởng ta nghỉ Tết; chính lúc ấy ta giữ thế thần tốc mà đánh vào chỗ chúng không ngờ."
            )
        elif any(term in query_norm for term in ("tuong binh", "voi chien", "ky binh")):
            answer = (
                "Tượng binh Tây Sơn không chỉ để phô uy. Khi kỵ binh Thanh ra chặn trước Ngọc Hồi, ta tung hơn trăm voi chiến đúng thời cơ; "
                "ngựa địch hoảng sợ, đội hình rối, thế kỵ binh bị bẻ gãy. Trên voi và quanh đội hình còn có hỏa khí như hỏa hổ, súng tay, đại bác; "
                "voi mở đường, mộc rơm ướt che hỏa lực, bộ binh xung kích áp sát. Thắng là nhờ phối hợp, không nhờ một binh chủng riêng lẻ."
            )
        else:
            answer = (
                "Với quân Thanh, ta không đánh bằng một mũi đơn độc. Ta cho quân tiến thần tốc ra Bắc, chia thế nhiều đạo: "
                "uy hiếp Hà Hồi để làm địch khiếp vía, đánh thẳng Ngọc Hồi bằng đội mộc rơm ướt che trước hỏa lực, phối hợp "
                "tượng binh, hỏa hổ, súng và bộ binh áp sát. Ở hướng Đống Đa, các đạo vu hồi đánh vào sườn và sau lưng, khiến "
                "quân Thanh rối loạn, Tôn Sĩ Nghị không kịp giữ thế trận. Thắng là vì đi nhanh, đánh đúng chỗ chủ quan của địch, "
                "và buộc quân đông mà tan thành từng mảng. Trận ấy cũng là lời đáp cho kẻ nào tưởng nước Nam suy yếu sau loạn lạc: "
                "quân có thể ít hơn, đường đi có thể gấp hơn, nhưng nếu biết gom lòng người, giữ kỷ luật và đánh vào thời cơ, "
                "thế mạnh của địch sẽ hóa thành gánh nặng của chính chúng."
            )
        return answer, "talking"

    if not hits:
        answer = (
            "Câu hỏi ấy còn rộng, nhưng ta có thể nói điều cốt yếu: đời ta đặt trên ba việc lớn là dẹp loạn, giữ nước và dựng phép trị. "
            "Muốn hiểu khí phách Tây Sơn, hãy nhìn cách ta đánh quân Xiêm ở Rạch Gầm - Xoài Mút, phá quân Thanh ở Ngọc Hồi - Đống Đa, "
            "rồi lo khuyến nông, học chính và dùng người hiền để yên dân."
        )
        return answer, "talking"

    if is_identity_query(query):
        answer = (
            "Ta là vị hoàng đế của triều Tây Sơn, sống vào cuối thế kỷ XVIII và lên ngôi năm 1788 để thống nhất "
            "lòng quân trước lúc ra Bắc chống quân Thanh. Ta cầm quân trong buổi đất nước rối ren, từng đánh tan "
            "liên quân Xiêm - Nguyễn ở Rạch Gầm - Xoài Mút năm 1785, rồi đại phá quân Thanh trong chiến dịch "
            "Ngọc Hồi - Đống Đa mùa xuân Kỷ Dậu 1789."
        )
        return answer, "talking"

    if "nghe an" in query_norm:
        answer = (
            "Ta dừng ở Nghệ An không phải vì chậm trễ, mà để tuyển thêm quân, chỉnh đốn đội ngũ và phủ dụ tướng sĩ "
            "trước khi tiến ra Bắc. Một đạo quân đi nhanh mà lòng chưa quy về một mối thì khó thành đại sự. Vì vậy "
            "Nghệ An là điểm vừa bổ sung lực lượng, vừa thống nhất ý chí chiến đấu chống quân Thanh."
        )
        return answer, "talking"

    if is_diplomacy_query(query):
        answer = (
            "Sau đại thắng, ta không chỉ dùng gươm giáo. Với Bắc triều, phải dùng lời mềm để dứt việc binh đao: "
            "giảng hòa, cầu phong và đi lại bằng nghi lễ bang giao. Lời tạ tội trong văn thư là phép quyền biến "
            "giữ nước, để Càn Long có đường lui danh dự; chớ hiểu cạn thành chuyện đánh mất nền độc lập. Còn nguyên "
            "văn từng biểu thì phải xét đúng văn thư nào đang được nhắc tới."
        )
        return answer, "talking"

    if "ngoc hoi" in query_norm or "dong da" in query_norm:
        answer = (
            "Ngọc Hồi - Đống Đa là đòn quyết chiến mùa xuân Kỷ Dậu 1789. Quân Tây Sơn tiến thần tốc ra Bắc, dùng "
            "nhiều hướng tiến công để chia cắt quân Thanh: mặt Ngọc Hồi chịu sức ép chính diện, còn hướng Đống Đa - "
            "Khương Thượng đánh vào điểm sơ hở và làm bộ chỉ huy địch rối loạn. Chiến thắng này phá vỡ cuộc can thiệp "
            "của nhà Thanh, giải phóng Thăng Long và khẳng định ý chí độc lập của nước Nam."
        )
        return answer, "talking"

    if "rach gam" in query_norm or "xoai mut" in query_norm:
        answer = (
            "Rạch Gầm - Xoài Mút năm 1785 là trận thủy chiến cho thấy cách dùng binh của ta: chọn đúng địa "
            "hình, giấu thuyền chiến và pháo binh, chờ liên quân Xiêm - Nguyễn lọt vào đoạn sông đã định rồi khóa đầu, "
            "khóa đuôi, đánh vào đội hình đang rối. Thắng lợi ấy chặn can thiệp Xiêm ở Nam Bộ và củng cố thế lực Tây Sơn."
        )
        return answer, "talking"

    answer = (
        "Nếu hỏi đại cục đời ta, hãy nhớ một điều: gươm giáo chỉ là bước mở đường, còn giữ nước phải biết dùng dân, dùng đất, dùng thời. "
        "Ta từng lấy tốc độ mà làm quân Thanh không kịp trở tay, lấy thế trận sông nước mà phá quân Xiêm, rồi dùng phép trị để gom lại lòng người sau loạn lạc."
    )
    return answer, "talking"


def answer_query(
    query: str,
    profile: dict,
    retriever: SimpleRetriever,
    top_k: int = DEFAULT_TOP_K,
    generator: Callable[[str, dict, list[dict]], str | None] | None = None,
    route: dict | None = None,
    search_query: str | None = None,
) -> dict:
    top_k = configured_top_k(top_k)
    metadata = profile["character_metadata"]
    route = dict(route or local_route_query(query, profile))
    route.setdefault("source", "deterministic")
    route_intent = str(route.get("intent") or "history_fact")
    needs_rag = bool(route.get("needs_rag", True))

    def result_payload(answer: str, state: str, citations: list[dict], mode: str) -> dict:
        return {
            "answer": answer,
            "state": state,
            "citations": citations,
            "mode": mode,
            "route": route,
            "route_source": route.get("source", "deterministic"),
            "fallback_used": mode in {"conversation", "guardrail", "factual"},
        }

    if route_intent in {"birth", "origin", "real_name", "death", "identity"}:
        hits = select_factual_hits(route_intent, profile, retriever, top_k)
        answer = build_factual_answer(query, profile, route_intent, hits)
        return result_payload(answer, "talking", [hit.chunk for hit in hits], "factual")

    if route_intent == "private_life":
        answer = build_local_fallback_answer(query, profile, route_intent, [])
        return result_payload(answer, "talking", [], "conversation")

    if route_intent == "smalltalk":
        answer = build_local_fallback_answer(query, profile, route_intent, [])
        return result_payload(answer, "talking", [], "conversation")

    if route_intent == "anachronism_trap" or is_anachronistic_warfare_query(query) or is_out_of_period(query, metadata["death_year"], profile):
        answer, state = build_answer(query, profile, [])
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        if not guardrail_chunks:
            answer = build_local_fallback_answer(query, profile, "anachronism_trap", [])
        return result_payload(answer, state, guardrail_chunks[:1], "guardrail")

    if is_unsupported_claim(query):
        answer, state = build_answer(query, profile, [])
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        return result_payload(answer, state, guardrail_chunks[:1], "guardrail")

    if not needs_rag:
        answer = build_local_fallback_answer(query, profile, route_intent, [])
        return result_payload(answer, "talking", [], "conversation")

    retrieval_query = (
        search_query
        or str(route.get("optimized_search_query") or "").strip()
        or query
    )
    hits = retriever.search(retrieval_query, top_k=top_k, profile=profile)
    original_intents = query_intents(query)
    for intent in ("micro_tactics", "administration", "education", "scholars"):
        if intent in original_intents and not any(intent in chunk_intents(hit.chunk) for hit in hits):
            intent_hits = select_intent_hits(query, retriever, intent, top_k)
            if intent_hits:
                hits = intent_hits
            break
    if has_uncovered_year_claim(query, hits):
        answer = (
            "Việc ấy chưa đủ chứng cứ để ta nhận là thật. Với câu hỏi nêu rõ năm, tên tướng hoặc địa danh, "
            "phải xét rất nghiêm; nếu chưa rõ thì không được dựng thêm sự kiện."
        )
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        return result_payload(answer, "confused", guardrail_chunks[:1], "guardrail")
    answer, state = build_answer(query, profile, hits)
    citations = [hit.chunk for hit in hits]
    mode = "retrieval"
    if generator and state == "talking" and not is_identity_query(query) and not is_legacy_afterlife_query(query, profile):
        generated = generator(query, profile, citations)
        if generated and is_generated_answer_acceptable(query, generated):
            answer = generated
            mode = "api"
    if state == "confused" and not citations:
        mode = "guardrail"
    return result_payload(answer, state, citations, mode)
