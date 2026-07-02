from __future__ import annotations

import json
import os
import sys
import time
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
BACKEND_DIR = Path(__file__).resolve().parent
LEGACY_WEB_DIR = PROJECT_ROOT / "quang_trung_web"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(LEGACY_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(LEGACY_WEB_DIR))

try:
    from dotenv import load_dotenv

    load_dotenv(LEGACY_WEB_DIR / ".env")
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from character_registry import CHARACTER_REGISTRY, DEFAULT_CHARACTER_ID, get_character_config  # noqa: E402
from llm_provider import (  # noqa: E402
    GeminiCallError,
    is_configured as llm_is_configured,
    route_query_json,
    stream_fused_generation,
)
from rag_core import (  # noqa: E402
    VectorRetriever,
    answer_query,
    build_local_fallback_answer,
    compact_text,
    is_identity_query,
    is_legacy_afterlife_query,
    is_private_life_query,
    is_quang_trung_self_name_confusion,
    local_route_query,
    load_chunks,
    load_profile,
    query_intents,
)
from tts_provider import synthesize  # noqa: E402
from interaction_logger import log_feedback, log_interaction, metrics_summary  # noqa: E402
from metrics import calculate_grounding_confidence, source_tier_summary  # noqa: E402


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatStreamRequest(BaseModel):
    character_id: str = DEFAULT_CHARACTER_ID
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    variant: str = Field(default="rag", pattern="^(rag|non_rag)$")
    session_id: str = "anonymous"


class TTSRequest(BaseModel):
    character_id: str = DEFAULT_CHARACTER_ID
    text: str = Field(min_length=1, max_length=6000)


class FeedbackRequest(BaseModel):
    message_id: str
    character_id: str = DEFAULT_CHARACTER_ID
    rating: str = Field(min_length=1, max_length=80)
    comment: str = Field(default="", max_length=1000)
    session_id: str = "anonymous"


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

    route_intent = str((result.get("route") or {}).get("intent", ""))
    if character_id == "quang_trung" and is_quang_trung_self_name_confusion(query, profile):
        return {
            "phase": phase,
            "intent": "identity_confusion",
            "emotion": "confused",
            "baseEmotion": "confused",
            "motion": "none",
            "asset": "confused.png",
            "action": "none",
        }
    if route_intent in {"birth", "origin", "real_name", "death", "identity", "smalltalk", "private_life"}:
        intent = "identity" if route_intent in {"birth", "origin", "real_name", "death", "identity"} else route_intent
        emotion = "idle"
        asset = "idle.png"
        return {
            "phase": phase,
            "intent": intent,
            "emotion": emotion,
            "baseEmotion": emotion,
            "motion": "none",
            "asset": asset,
            "action": "none",
        }

    is_pre_1954_character = isinstance(death_year, int) and death_year < 1954
    if character_id == "quang_trung" and is_quang_trung_self_name_confusion(query, profile):
        intent = "identity_confusion"
        emotion = "confused"
        asset = "confused.png"
    elif mode == "guardrail" or state == "confused" or (
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


def fast_local_retrieval_enabled() -> bool:
    return os.getenv("FAST_LOCAL_RETRIEVAL", "1").strip().lower() not in {"0", "false", "no", "off"}


def should_stream_with_gemini(query: str, profile: dict, result: dict, route_llm_status: str, variant: str = "rag") -> bool:
    if variant == "non_rag":
        return llm_is_configured() and route_llm_status not in {"quota_exhausted", "auth_error", "invalid_model", "not_configured"}
    route_intent = str((result.get("route") or {}).get("intent", ""))
    if fast_local_retrieval_enabled() and route_llm_status == "skipped" and result.get("mode") == "retrieval":
        return False
    return (
        llm_is_configured()
        and route_llm_status not in {"quota_exhausted", "auth_error", "invalid_model", "not_configured"}
        and result.get("state") == "talking"
        and result.get("mode") not in {"guardrail", "conversation", "factual"}
        and route_intent not in {"smalltalk", "identity", "birth", "origin", "real_name", "death", "private_life", "anachronism_trap"}
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


LOCAL_FIRST_INTENTS = {
    "smalltalk",
    "identity",
    "birth",
    "origin",
    "real_name",
    "death",
    "private_life",
    "anachronism_trap",
    "history_battle",
    "philosophy",
}


def should_skip_llm_router(local_route: dict) -> bool:
    try:
        confidence = float(local_route.get("confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        confidence = 0.0
    intent = str(local_route.get("intent", ""))
    if intent in {"history_battle", "philosophy"} and not fast_local_retrieval_enabled():
        return False
    threshold = 0.7 if intent in {"history_battle", "philosophy"} else 0.8
    return intent in LOCAL_FIRST_INTENTS and confidence >= threshold


def timing_payload(started_at: float, marks: dict[str, float], *keys: str) -> dict[str, int]:
    payload: dict[str, int] = {}
    for key in keys:
        value = marks.get(key)
        if value is not None:
            payload[f"{key}_ms"] = int((value - started_at) * 1000)
    payload["total_ms"] = int((time.perf_counter() - started_at) * 1000)
    return payload


def stream_chat_response(request: ChatStreamRequest) -> Iterator[str]:
    try:
        started_at = time.perf_counter()
        marks: dict[str, float] = {}
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

        local_route = local_route_query(query, profile)
        if should_skip_llm_router(local_route) or not llm_is_configured():
            router_response = {
                "ok": False,
                "llm_status": "skipped" if llm_is_configured() else "not_configured",
                "route": None,
            }
            route = local_route
            route_source = "deterministic"
            route_llm_status = str(router_response["llm_status"])
        else:
            router_response = route_query_json(query, profile)
            if router_response.get("ok") and router_response.get("route"):
                route = router_response["route"]
                route["source"] = "llm"
                route_source = "llm"
                route_llm_status = "ok"
            else:
                route = local_route
                route_source = "deterministic"
                route_llm_status = str(router_response.get("llm_status", "router_fallback"))
        marks["route"] = time.perf_counter()
        if request.variant == "non_rag":
            route_intent = str(route.get("intent", "history_fact") or "history_fact")
            result = {
                "answer": build_local_fallback_answer(query, profile, route_intent, []),
                "citations": [],
                "mode": "non_rag",
                "state": "talking",
                "fallback_used": not llm_is_configured(),
                "route": route,
            }
        else:
            result = answer_query(query, profile, retriever, generator=None, route=route)
        marks["retrieval"] = time.perf_counter()
        citations = [public_citation(chunk) for chunk in result.get("citations", [])]
        fallback_used = bool(result.get("fallback_used", False))
        llm_status = route_llm_status
        source_summary = source_tier_summary(citations)
        grounding_confidence = calculate_grounding_confidence(
            citations=citations,
            mode=result.get("mode", "retrieval"),
            fallback_used=fallback_used,
            llm_status=llm_status,
        )
        yield sse_event(
            "retrieval",
            {
                "mode": result.get("mode", "retrieval"),
                "state": result.get("state", "talking"),
                "citations": citations,
                "route": route,
                "route_source": route_source,
                "llm_status": llm_status,
                "fallback_used": fallback_used,
                "timings_ms": timing_payload(started_at, marks, "route", "retrieval"),
                "source_summary": source_summary,
                "grounding_confidence": grounding_confidence,
                "variant": request.variant,
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

        if should_stream_with_gemini(query, profile, result, route_llm_status, request.variant):
            collected: list[str] = []
            try:
                generation_citations = [] if request.variant == "non_rag" else result.get("citations", [])
                for token in stream_fused_generation(query, profile, generation_citations, route=route):
                    emitted_stream = True
                    if "first_token" not in marks:
                        marks["first_token"] = time.perf_counter()
                    collected.append(token)
                    yield sse_event("token", {"text": token})
                raw_answer = "".join(collected).strip()
                if raw_answer:
                    final_answer = raw_answer
                    mode = "non_rag" if request.variant == "non_rag" else "api"
                    llm_status = "ok"
                    fallback_used = False
            except GeminiCallError as exc:
                llm_status = exc.kind
                fallback_used = True
            if not emitted_stream:
                for token in tokenized_fallback(fallback_answer):
                    if "first_token" not in marks:
                        marks["first_token"] = time.perf_counter()
                    yield sse_event("token", {"text": token})
                final_answer = fallback_answer
        else:
            fallback_used = True
            for token in tokenized_fallback(fallback_answer):
                if "first_token" not in marks:
                    marks["first_token"] = time.perf_counter()
                yield sse_event("token", {"text": token})

        marks["final"] = time.perf_counter()
        final_timings = timing_payload(started_at, marks, "route", "retrieval", "first_token", "final")
        source_summary = source_tier_summary(citations)
        grounding_confidence = calculate_grounding_confidence(
            citations=citations,
            mode=mode,
            fallback_used=fallback_used,
            llm_status=llm_status,
        )
        log_interaction(
            {
                "session_id": request.session_id,
                "character_id": character_id,
                "variant": request.variant,
                "prompt": query,
                "mode": mode,
                "route_source": route_source,
                "llm_status": llm_status,
                "fallback_used": fallback_used,
                "citation_count": len(citations),
                "source_summary": source_summary,
                "grounding_confidence": grounding_confidence,
                "timings_ms": final_timings,
            }
        )
        yield sse_event(
            "final",
            {
                "answer": final_answer,
                "mode": mode,
                "state": result.get("state", "talking"),
                "citations": citations,
                "route": route,
                "route_source": route_source,
                "llm_status": llm_status,
                "fallback_used": fallback_used,
                "timings_ms": final_timings,
                "source_summary": source_summary,
                "grounding_confidence": grounding_confidence,
                "variant": request.variant,
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


@app.get("/api/metrics/summary")
def metrics() -> dict:
    return metrics_summary()


@app.post("/api/feedback")
def feedback(request: FeedbackRequest) -> dict:
    log_feedback(request.model_dump())
    return {"ok": True}


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
