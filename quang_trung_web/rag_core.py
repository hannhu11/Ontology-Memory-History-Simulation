from __future__ import annotations

import hashlib
import json
import math
import os
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET_DIR = ROOT_DIR.parent / "quang_trung_dataset"
DEFAULT_INDEX_DIR = ROOT_DIR / ".rag_index" / "quang_trung"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
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
        "rach gam",
        "xoai mut",
        "my tho",
        "gia dinh",
        "siam",
        "xiem",
        "hanh quan",
        "than toc",
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
        "dien bien phu",
        "may bay",
        "dien thoai",
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


def configured_index_dir() -> Path:
    raw_value = os.getenv("RAG_INDEX_DIR")
    return Path(raw_value) if raw_value else DEFAULT_INDEX_DIR


def query_intents(query: str) -> set[str]:
    normalized = normalize(query)
    intents = {
        intent
        for intent, terms in INTENT_QUERY_TERMS.items()
        if any(has_phrase(normalized, term) for term in terms)
    }
    if is_diplomacy_query(query):
        intents.add("diplomacy")
    if is_anachronistic_warfare_query(query) or is_out_of_period(query):
        intents.add("anachronism")
    for primary in (
        "anachronism",
        "capital_city",
        "administration",
        "coinage",
        "education",
        "agriculture",
        "scholars",
        "diplomacy",
        "battle_reflection",
        "micro_tactics",
        "military",
    ):
        if primary in intents:
            return {primary}
    return intents


def chunk_intents(chunk: dict) -> set[str]:
    intents = set(chunk.get("answer_intents") or []) | set(chunk.get("tags") or [])
    if intents & {"micro_tactics", "military", "battle", "ngoc_hoi_dong_da", "rach_gam_xoai_mut"}:
        intents.add("battle_reflection")
    return intents


def source_quality_boost(chunk: dict) -> float:
    quality = chunk.get("source_quality", "")
    return {
        "research_secondary": 0.035,
        "digitized_secondary": 0.025,
        "museum_official": 0.02,
        "curated_exhibit": 0.015,
    }.get(quality, 0.0)


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


def rewrite_query(query: str, profile: dict | None = None) -> str:
    normalized = normalize(query)
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
    if is_battle_reflection_query(query):
        additions.append(
            "trận đánh hãnh diện tự hào chiến thắng lớn Ngọc Hồi Đống Đa Kỷ Dậu 1789 "
            "Rạch Gầm Xoài Mút năm 1785 quân Thanh quân Xiêm"
        )
    elif is_battle_description_query(query):
        additions.append(
            "trận Ngọc Hồi Đống Đa mùa xuân Kỷ Dậu 1789 quân Thanh Tôn Sĩ Nghị "
            "Hà Hồi Ngọc Hồi Đống Đa tượng binh hỏa hổ đại bác mộc rơm ướt năm đạo quân"
        )
    if not additions:
        return query
    return " ".join([query, *additions])


def query_variants(query: str, profile: dict | None = None) -> list[str]:
    variants = [query, rewrite_query(query, profile)]
    if is_battle_reflection_query(query):
        variants.extend(
            [
                "Quang Trung Nguyễn Huệ Tây Sơn trận Ngọc Hồi Đống Đa Kỷ Dậu 1789 chiến thắng hãnh diện nhất đại phá quân Thanh",
                "Quang Trung Nguyễn Huệ Tây Sơn trận Rạch Gầm Xoài Mút năm 1785 chiến thắng quân Xiêm Nguyễn",
                "Quang Trung Nguyễn Huệ nghệ thuật quân sự chiến thắng lớn trận đánh đáng nhớ",
            ]
        )
    elif is_battle_description_query(query):
        variants.extend(
            [
                "Quang Trung Nguyễn Huệ trận Ngọc Hồi Đống Đa Kỷ Dậu 1789 diễn biến đại phá quân Thanh Tôn Sĩ Nghị",
                "Quang Trung Nguyễn Huệ chiến dịch Ngọc Hồi Đống Đa năm đạo quân Hà Hồi Ngọc Hồi Đống Đa",
                "Tây Sơn tượng binh hỏa hổ đại bác mộc rơm ướt đánh quân Thanh ở Ngọc Hồi",
            ]
        )
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
    threshold = min_score if min_score is not None else configured_score_threshold()
    fused: dict[str, Hit] = {}
    for hit in hits:
        doc_intents = chunk_intents(hit.chunk)
        if not intent_matches(intents, doc_intents):
            continue
        adjusted = hit.score + source_quality_boost(hit.chunk)
        if intents and (intents & doc_intents):
            adjusted += 0.08 + min(0.12, 0.04 * len(intents & doc_intents))
        if "battle_reflection" in intents:
            if doc_intents & {"micro_tactics", "military"}:
                adjusted += 0.22
            if hit.chunk.get("chunk_id") in {"qt_kb_032", "qt_kb_039", "qt_kb_047", "qt_kb_092", "qt_kb_093", "qt_kb_095", "qt_kb_096", "qt_kb_097"}:
                adjusted += 0.16
        chunk_id = hit.chunk.get("chunk_id", "")
        previous = fused.get(chunk_id)
        if previous is None or adjusted > previous.score:
            fused[chunk_id] = Hit(hit.chunk, min(adjusted, 1.0))
    ranked = sorted(fused.values(), key=lambda item: item.score, reverse=True)
    if ranked and ranked[0].score < threshold:
        return []
    return ranked[:top_k]


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
    )
    return any(has_phrase(normalized, phrase) for phrase in identity_phrases)


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


def load_profile(dataset_dir: Path | str = DEFAULT_DATASET_DIR) -> dict:
    dataset_dir = Path(dataset_dir)
    return json.loads((dataset_dir / "quang_trung_profile.json").read_text(encoding="utf-8"))


def load_chunks(dataset_dir: Path | str = DEFAULT_DATASET_DIR) -> list[dict]:
    dataset_dir = Path(dataset_dir)
    chunks = []
    with (dataset_dir / "quang_trung_knowledge.jsonl").open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
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
    ):
        self.chunks = list(chunks)
        self.persist_dir = Path(persist_dir) if persist_dir else configured_index_dir()
        self.model_name = model_name or configured_embedding_model()
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

    def _init_vector_backend(self) -> None:
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except Exception:
            return

        try:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(self.persist_dir))
            collection = client.get_or_create_collection(
                name="quang_trung",
                metadata={"hnsw:space": "cosine"},
            )
            fingerprint = self._dataset_fingerprint()
            metadata_path = self.persist_dir / "metadata.json"
            previous = {}
            if metadata_path.exists():
                previous = json.loads(metadata_path.read_text(encoding="utf-8"))
            embedding_model = SentenceTransformer(self.model_name)
            if previous.get("fingerprint") != fingerprint or previous.get("model_name") != self.model_name:
                existing = collection.get(include=[])
                existing_ids = existing.get("ids", [])
                if existing_ids:
                    collection.delete(ids=existing_ids)
                documents = [self._embedding_text(chunk) for chunk in self.chunks]
                embeddings = embedding_model.encode(documents, normalize_embeddings=True).tolist()
                ids = [chunk["chunk_id"] for chunk in self.chunks]
                metadatas = [
                    {
                        "index": index,
                        "answer_intents": " ".join(chunk.get("answer_intents", [])),
                        "tags": " ".join(chunk.get("tags", [])),
                        "source_quality": chunk.get("source_quality", ""),
                    }
                    for index, chunk in enumerate(self.chunks)
                ]
                collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
                metadata_path.write_text(
                    json.dumps({"fingerprint": fingerprint, "model_name": self.model_name}, ensure_ascii=False, indent=2),
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
        query_embedding = self._embedding_model.encode([query], normalize_embeddings=True).tolist()[0]
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


def is_out_of_period(query: str, death_year: int = 1792) -> bool:
    normalized = normalize(query)
    if re.search(r"\bA\.?I\.?\b", query):
        return True
    if any(has_phrase(normalized, term) for term in MODERN_TERMS):
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


def build_answer(query: str, profile: dict, hits: list[Hit]) -> tuple[str, str]:
    metadata = profile["character_metadata"]
    query_norm = normalize(query)
    if is_anachronistic_warfare_query(query):
        answer = (
            "Năm Kỷ Dậu 1789 là việc có thật trong đời ta, nhưng đem chiến dịch ấy gán cho Blitzkrieg "
            "hay quân Đức là lẫn lộn đời sau. Ta thắng nhờ thế nước, lòng quân, địa hình, tốc độ hành binh "
            "và cách đánh vào lúc địch chủ quan; không phải nhờ học thuyết binh pháp của người Âu đời sau."
        )
        return answer, "confused"

    if is_out_of_period(query, metadata["death_year"]):
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

    if is_smalltalk_query(query) and not is_identity_query(query):
        answer = (
            "Ta đang nghe. Hãy hỏi rõ điều ngươi muốn biết về thân thế, việc cầm quân, Rạch Gầm - Xoài Mút, "
            "Nghệ An, hoặc trận Ngọc Hồi - Đống Đa; điều nào đủ chứng cứ thì ta sẽ nói thẳng."
        )
        return answer, "talking"

    intents = query_intents(query)
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
            "vì ta chọn đúng khúc sông, khóa đầu đuôi thủy quân Xiêm - Nguyễn và phá tan thế can thiệp từ phương Nam."
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
                "và buộc quân đông mà tan thành từng mảng."
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
) -> dict:
    top_k = configured_top_k(top_k)
    metadata = profile["character_metadata"]
    if is_smalltalk_query(query) and not is_identity_query(query):
        answer, state = build_answer(query, profile, [])
        return {
            "answer": answer,
            "state": state,
            "citations": [],
            "mode": "conversation",
        }

    if is_anachronistic_warfare_query(query):
        answer, state = build_answer(query, profile, [])
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        return {
            "answer": answer,
            "state": state,
            "citations": guardrail_chunks[:1],
            "mode": "guardrail",
        }

    if is_out_of_period(query, metadata["death_year"]):
        answer, state = build_answer(query, profile, [])
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        return {
            "answer": answer,
            "state": state,
            "citations": guardrail_chunks[:1],
            "mode": "guardrail",
        }

    if is_unsupported_claim(query):
        answer, state = build_answer(query, profile, [])
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        return {
            "answer": answer,
            "state": state,
            "citations": guardrail_chunks[:1],
            "mode": "guardrail",
        }

    if is_identity_query(query):
        chunk_map = {chunk.get("chunk_id"): chunk for chunk in retriever.chunks}
        identity_ids = ("qt_kb_001", "qt_kb_012", "qt_kb_032", "qt_kb_043")
        hits = [Hit(chunk_map[chunk_id], 1.0) for chunk_id in identity_ids if chunk_id in chunk_map][:top_k]
    else:
        hits = retriever.search(query, top_k=top_k, profile=profile)
    if has_uncovered_year_claim(query, hits):
        answer = (
            "Việc ấy chưa đủ chứng cứ để ta nhận là thật. Với câu hỏi nêu rõ năm, tên tướng hoặc địa danh, "
            "phải xét rất nghiêm; nếu chưa rõ thì không được dựng thêm sự kiện."
        )
        guardrail_chunks = [chunk for chunk in retriever.chunks if "guardrail" in chunk.get("tags", [])]
        return {
            "answer": answer,
            "state": "confused",
            "citations": guardrail_chunks[:1],
            "mode": "guardrail",
        }
    answer, state = build_answer(query, profile, hits)
    citations = [hit.chunk for hit in hits]
    mode = "retrieval"
    if generator and citations and state == "talking" and not is_identity_query(query):
        generated = generator(query, profile, citations)
        if generated and is_generated_answer_acceptable(query, generated):
            answer = generated
            mode = "api"
    if is_smalltalk_query(query) and not is_identity_query(query):
        mode = "conversation"
    elif state == "confused" and not citations:
        mode = "guardrail"
    return {
        "answer": answer,
        "state": state,
        "citations": citations,
        "mode": mode,
    }
