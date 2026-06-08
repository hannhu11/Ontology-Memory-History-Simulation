from __future__ import annotations

import json
import os
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGACY_WEB_DIR = PROJECT_ROOT / "quang_trung_web"
if str(LEGACY_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_WEB_DIR))

try:
    from dotenv import load_dotenv

    load_dotenv(LEGACY_WEB_DIR / ".env")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from character_registry import CHARACTER_REGISTRY, DEFAULT_CHARACTER_ID, get_character_config  # noqa: E402
from llm_provider import clean_generated_answer, is_configured as llm_is_configured, stream_character_answer_chunks  # noqa: E402
from rag_core import (  # noqa: E402
    VectorRetriever,
    answer_query,
    compact_text,
    is_generated_answer_acceptable,
    is_identity_query,
    is_legacy_afterlife_query,
    is_private_life_query,
    load_chunks,
    load_profile,
    query_intents,
)
from tts_provider import synthesize  # noqa: E402


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatStreamRequest(BaseModel):
    character_id: str = DEFAULT_CHARACTER_ID
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)


class TTSRequest(BaseModel):
    character_id: str = DEFAULT_CHARACTER_ID
    text: str = Field(min_length=1, max_length=6000)


def sse_event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def public_citation(chunk: dict) -> dict:
    return {
        "chunk_id": chunk.get("chunk_id", ""),
        "source_title": chunk.get("source_title", "Tư liệu không rõ"),
        "source_url": chunk.get("source_url", ""),
        "source_year": chunk.get("source_year", ""),
        "claim_status": chunk.get("claim_status", "established"),
        "source_tier": chunk.get("source_tier"),
        "source_quality_score": chunk.get("source_quality_score"),
        "answer_intents": chunk.get("answer_intents", []),
        "tags": chunk.get("tags", []),
        "fact": compact_text(chunk.get("fact") or chunk.get("text", ""), max_words=80),
    }


def text_blob(*values: Any) -> str:
    return " ".join(str(value or "") for value in values).lower()


def visual_payload(
    query: str,
    answer: str,
    profile: dict,
    result: dict | None = None,
    citations: Iterable[dict] | None = None,
    phase: str = "answering",
) -> dict[str, Any]:
    result = result or {}
    citations = list(citations or [])
    metadata = profile.get("character_metadata", {})
    character_id = profile.get("character_id") or metadata.get("character_id", "")
    death_year = metadata.get("death_year")
    mode = result.get("mode", "")
    state = result.get("state", "talking")
    citation_intents: set[str] = set()
    citation_tags: set[str] = set()
    for citation in citations:
        citation_intents.update(str(item).lower() for item in citation.get("answer_intents", []) or [])
        citation_tags.update(str(item).lower() for item in citation.get("tags", []) or [])

    detected = {item.lower() for item in query_intents(query)}
    combined = text_blob(query, answer, mode, state, " ".join(detected), " ".join(citation_intents), " ".join(citation_tags))

    intent = "historical_fact"
    emotion = "idle"
    motion = "none"
    action = "none"
    asset = "idle.png"

    if phase == "thinking":
        return {
            "phase": "thinking",
            "intent": "retrieval",
            "emotion": "thinking",
            "baseEmotion": "thinking",
            "motion": "thinking" if character_id == "quang_trung" else "none",
            "asset": "thinking.png",
            "action": "loop" if character_id == "quang_trung" else "none",
        }

    is_pre_1954_character = isinstance(death_year, int) and death_year < 1954
    if mode == "guardrail" or state == "confused" or (
        is_pre_1954_character and "điện biên phủ" in combined
    ) or any(
        marker in combined
        for marker in [
            "facebook",
            "internet",
            "thế chiến",
            "world war",
            "ww2",
            "ww1",
            "sau khi ta đã mất",
            "sau khi bác đã đi xa",
        ]
    ):
        intent = "anachronism"
        emotion = "confused"
        asset = "confused.png"
    elif any(
        marker in combined
        for marker in [
            "battle_reflection",
            "battle_detail",
            "micro_tactics",
            "military",
            "trận",
            "đánh",
            "giặc",
            "quân thanh",
            "quân xiêm",
            "ngọc hồi",
            "đống đa",
            "rạch gầm",
            "xoài mút",
            "bạch đằng",
            "điện biên phủ",
            "xung trận",
            "ngoại xâm",
            "đại phá",
            "đập tan",
        ]
    ):
        intent = "battle_detail"
        if any(
            marker in combined
            for marker in [
                "giặc",
                "quân thanh",
                "quân xiêm",
                "ngoại xâm",
                "xâm lược",
                "xâm lăng",
                "phản bội",
                "hồ đồ",
                "đập tan",
            ]
        ):
            emotion = "angry"
            asset = "angry_2.png"
        elif any(marker in combined for marker in ["chiến thắng", "đại thắng", "hãnh diện", "tự hào", "vinh quang"]):
            emotion = "happy"
            asset = "happy.png"
        else:
            emotion = "angry"
            asset = "angry.png"
        if character_id == "quang_trung":
            motion = "attack"
            action = "play_once"
    elif any(
        marker in combined
        for marker in [
            "dân lầm than",
            "mất mát",
            "hy sinh",
            "tang tóc",
            "đau xót",
            "ruộng hoang",
            "loạn lạc",
            "dang dở",
        ]
    ):
        intent = "suffering"
        emotion = "sad"
        asset = "sad.png"
    elif any(marker in combined for marker in ["tư tưởng", "nhân nghĩa", "khoan thư", "độc lập", "tự do", "đại đoàn kết"]):
        intent = "ideology"
        emotion = "thinking"
        asset = "thinking.png"
    elif any(marker in combined for marker in ["chào", "bạn là ai", "giới thiệu", "tên của ta", "ta là"]):
        intent = "identity"
        emotion = "idle"
        asset = "idle.png"
    elif any(marker in combined for marker in ["cười", "vui", "mừng", "khải hoàn", "vinh"]):
        intent = "smalltalk"
        emotion = "happy"
        asset = "happy.png"

    return {
        "phase": phase,
        "intent": intent,
        "emotion": emotion,
        "baseEmotion": emotion,
        "motion": motion,
        "asset": asset,
        "action": action,
    }


def portrait_url_for(character_id: str) -> str | None:
    asset_dir = get_character_config(character_id)["asset_dir"]
    idle_path = asset_dir / "idle.png"
    if idle_path.exists():
        return f"/assets/{character_id}/idle.png"
    return None


class RuntimeStore:
    def __init__(self) -> None:
        self.profiles: dict[str, dict] = {}
        self.chunks: dict[str, list[dict]] = {}
        self.retrievers: dict[str, VectorRetriever] = {}
        self.loaded = False

    def preload(self) -> None:
        if self.loaded:
            return
        for character_id in CHARACTER_REGISTRY:
            profile = load_profile(character_id)
            chunks = load_chunks(character_id)
            retriever = VectorRetriever(chunks, character_id=character_id)
            self.profiles[character_id] = profile
            self.chunks[character_id] = chunks
            self.retrievers[character_id] = retriever
        self.loaded = True

    def character_ids(self) -> list[str]:
        return list(self.profiles.keys())

    def get(self, character_id: str) -> tuple[dict, VectorRetriever]:
        if character_id not in self.profiles:
            raise HTTPException(status_code=404, detail="Unknown character_id")
        return self.profiles[character_id], self.retrievers[character_id]


runtime = RuntimeStore()


@asynccontextmanager
async def lifespan(_: FastAPI):
    runtime.preload()
    yield


app = FastAPI(title="History Ontology Simulation API", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSET_ROOT = LEGACY_WEB_DIR / "assets"
if ASSET_ROOT.exists():
    app.mount("/assets", StaticFiles(directory=ASSET_ROOT), name="assets")


@app.get("/api/health")
def health() -> dict:
    if not runtime.loaded:
        runtime.preload()
    return {
        "ok": True,
        "runtime": "fastapi",
        "characters_loaded": runtime.character_ids(),
        "llm_configured": llm_is_configured(),
    }


@app.get("/api/characters")
def characters() -> dict:
    if not runtime.loaded:
        runtime.preload()
    payload = []
    for character_id, config in CHARACTER_REGISTRY.items():
        profile = runtime.profiles.get(character_id) or load_profile(character_id)
        metadata = profile.get("character_metadata", {})
        payload.append(
            {
                "character_id": character_id,
                "display_name": config["display_name"],
                "era": metadata.get("era", ""),
                "death_year": metadata.get("death_year"),
                "edge_cases": config.get("edge_cases", []),
                "portrait_url": portrait_url_for(character_id),
            }
        )
    return {"characters": payload, "default_character_id": DEFAULT_CHARACTER_ID}


def should_stream_with_gemini(query: str, profile: dict, result: dict) -> bool:
    return (
        llm_is_configured()
        and result.get("state") == "talking"
        and result.get("mode") not in {"guardrail", "conversation"}
        and not is_identity_query(query)
        and not is_private_life_query(query)
        and not is_legacy_afterlife_query(query, profile)
    )


def tokenized_fallback(answer: str) -> Iterator[str]:
    words = answer.split(" ")
    for index, word in enumerate(words):
        if index:
            yield " "
        yield word


def stream_chat_response(request: ChatStreamRequest) -> Iterator[str]:
    try:
        character_id = request.character_id if request.character_id in CHARACTER_REGISTRY else DEFAULT_CHARACTER_ID
        profile, retriever = runtime.get(character_id)
        query = request.message.strip()
        thinking_visual = visual_payload(query, "", profile, phase="thinking")
        yield sse_event(
            "start",
            {
                "character_id": character_id,
                "status": "Đang gợi ký ức",
                "visual": thinking_visual,
            },
        )

        result = answer_query(query, profile, retriever, generator=None)
        citations = [public_citation(chunk) for chunk in result.get("citations", [])]
        yield sse_event(
            "retrieval",
            {
                "mode": result.get("mode", "retrieval"),
                "state": result.get("state", "talking"),
                "citations": citations,
            },
        )

        fallback_answer = result.get("answer", "")
        final_answer = fallback_answer
        mode = result.get("mode", "retrieval")
        emitted_stream = False
        early_visual = visual_payload(query, fallback_answer, profile, result, citations, phase="answering")
        yield sse_event(
            "stream_start",
            {
                "intent": early_visual["intent"],
                "emotion": early_visual["emotion"],
                "visual": early_visual,
            },
        )

        if should_stream_with_gemini(query, profile, result):
            collected: list[str] = []
            for token in stream_character_answer_chunks(query, profile, result.get("citations", [])):
                emitted_stream = True
                collected.append(token)
                yield sse_event("token", {"text": token})
            raw_answer = "".join(collected).strip()
            cleaned = clean_generated_answer(raw_answer, profile) if raw_answer else None
            if cleaned and is_generated_answer_acceptable(query, cleaned):
                final_answer = cleaned
                mode = "api"
            elif not emitted_stream:
                for token in tokenized_fallback(fallback_answer):
                    yield sse_event("token", {"text": token})
                final_answer = fallback_answer
        else:
            for token in tokenized_fallback(fallback_answer):
                yield sse_event("token", {"text": token})

        yield sse_event(
            "final",
            {
                "answer": final_answer,
                "mode": mode,
                "state": result.get("state", "talking"),
                "citations": citations,
                "visual": visual_payload(query, final_answer, profile, {**result, "mode": mode}, citations, phase="answering"),
            },
        )
    except Exception as exc:
        if os.getenv("HISTORY_DEBUG_ERRORS") == "1":
            traceback.print_exc()
        yield sse_event("error", {"message": "Không tạo được câu trả lời trong lượt này.", "detail": str(exc)})


@app.post("/api/chat/stream")
def chat_stream(request: ChatStreamRequest) -> StreamingResponse:
    if not runtime.loaded:
        runtime.preload()
    return StreamingResponse(
        stream_chat_response(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.post("/api/tts")
def tts(request: TTSRequest) -> dict:
    character_id = request.character_id if request.character_id in CHARACTER_REGISTRY else DEFAULT_CHARACTER_ID
    result = synthesize(request.text, character_id)
    return {
        "ok": result.ok,
        "audio_base64": result.audio_base64,
        "mime_type": result.mime_type,
        "message": result.message,
    }
