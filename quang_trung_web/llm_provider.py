import json
import os
import re
import socket
import urllib.parse
import urllib.request
import urllib.error
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass


MODEL_NAME = "gemini-2.5-flash"
DEFAULT_TIMEOUT_SECONDS = 18.0
MAX_OUTPUT_TOKENS = 1400
ROUTER_MAX_OUTPUT_TOKENS = 240
DEFAULT_LLM_PROVIDER = "gemini_api"
DEFAULT_VERTEX_LOCATION = "us-central1"

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
    "dữ liệu",
    "ngữ cảnh",
    "tư liệu hiện có",
)


@dataclass
class GeminiCallError(Exception):
    kind: str
    message: str = ""

    def __str__(self) -> str:
        return self.kind


def _error_kind_from_status(status_code: int, body: str = "") -> str:
    lowered = body.lower()
    if status_code == 429 or "resource_exhausted" in lowered or "quota" in lowered:
        return "quota_exhausted"
    if status_code in {401, 403}:
        return "auth_error"
    if status_code == 404:
        return "invalid_model"
    return "api_error"


def _error_kind_from_exception(exc: Exception) -> str:
    status_code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    body = " ".join(
        str(value)
        for value in (
            getattr(exc, "message", ""),
            getattr(exc, "status", ""),
            getattr(exc, "response", ""),
            exc,
        )
        if value
    )
    if isinstance(status_code, int):
        return _error_kind_from_status(status_code, body)
    lowered = body.lower()
    if "resource_exhausted" in lowered or "quota" in lowered or "429" in lowered:
        return "quota_exhausted"
    if "permission_denied" in lowered or "unauthenticated" in lowered or "401" in lowered or "403" in lowered:
        return "auth_error"
    if "not_found" in lowered or "404" in lowered or "model" in lowered and "not" in lowered:
        return "invalid_model"
    return "api_error"


def _safe_error_message(exc: Exception) -> str:
    if isinstance(exc, GeminiCallError):
        return exc.kind
    return type(exc).__name__


def configured_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER).strip().lower()
    if provider in {"vertex", "vertex_ai", "vertexai"}:
        return "vertex"
    return "gemini_api"


def uses_vertex_provider() -> bool:
    return configured_provider() == "vertex"


def configured_model() -> str:
    return os.getenv("GEMINI_MODEL_NAME", MODEL_NAME).strip() or MODEL_NAME


def configured_router_model() -> str:
    return os.getenv("GEMINI_ROUTER_MODEL_NAME", configured_model()).strip() or configured_model()


def configured_google_cloud_project() -> str:
    return (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GOOGLE_PROJECT_ID")
        or os.getenv("GCLOUD_PROJECT")
        or ""
    ).strip()


def configured_google_cloud_location() -> str:
    return (
        os.getenv("GOOGLE_CLOUD_LOCATION")
        or os.getenv("GOOGLE_VERTEX_LOCATION")
        or os.getenv("VERTEX_LOCATION")
        or DEFAULT_VERTEX_LOCATION
    ).strip() or DEFAULT_VERTEX_LOCATION


def is_configured() -> bool:
    if uses_vertex_provider():
        return bool(configured_google_cloud_project())
    return bool(os.getenv("GEMINI_API_KEY"))


def request_timeout_seconds() -> float:
    raw_value = os.getenv("LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    try:
        return max(5.0, float(raw_value))
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


def router_timeout_seconds() -> float:
    raw_value = os.getenv("LLM_ROUTER_TIMEOUT_SECONDS", "5").strip()
    try:
        return max(2.0, float(raw_value))
    except ValueError:
        return 5.0


def _citation_context(citations: Iterable[dict]) -> str:
    lines = []
    for index, citation in enumerate(citations, 1):
        fact = citation.get("fact") or citation.get("text", "")
        title = citation.get("source_title", "Tư liệu không rõ")
        status = citation.get("claim_status", "established")
        lines.append(
            f"[{index}] {fact}\nNhan đề tư liệu: {title} ({citation.get('source_year', '')})\n"
            f"Mức độ nhận định: {status}"
        )
    return "\n\n".join(lines)


def _self_names(profile: dict) -> list[str]:
    metadata = profile.get("character_metadata", {})
    names = [metadata.get("name", ""), metadata.get("full_name", "")]
    names.extend(metadata.get("aliases", []))
    return [name for name in dict.fromkeys(names) if name]


def _first_person(profile: dict) -> str:
    character_id = profile.get("character_id", "quang_trung")
    if character_id == "ho_chi_minh":
        return "Bác"
    if character_id == "vo_nguyen_giap":
        return "tôi"
    return "ta"


def _listener(profile: dict) -> str:
    character_id = profile.get("character_id", "quang_trung")
    if character_id == "ho_chi_minh":
        return "đồng bào, các cháu hoặc các chú"
    if character_id == "vo_nguyen_giap":
        return "đồng bào, chiến sĩ hoặc cán bộ"
    if character_id == "nguyen_trai":
        return "người hoặc bạn"
    return "ngươi"


def _persona_directive(profile: dict) -> str:
    character_id = profile.get("character_id", "quang_trung")
    directives = {
        "quang_trung": (
            'Xưng "ta" hoặc "trẫm", gọi người hỏi là "ngươi" hoặc "kẻ hậu sinh". '
            "Khẩu khí đanh thép, thẳng, hào sảng, thực tế; khi nói trận đánh phải có nguyên nhân, thế trận, hành động và ý nghĩa."
        ),
        "tran_hung_dao": (
            'Xưng "ta" hoặc "Quốc công", gọi "ngươi" hoặc "hậu bối". '
            "Lời trầm, nặng xã tắc, đề cao lòng dân, kỷ luật tướng sĩ và phép giữ nước lâu dài."
        ),
        "nguyen_trai": (
            'Xưng "ta" hoặc "kẻ hèn này", gọi "ngươi". '
            "Văn phong nho nhã, thâm trầm, giàu nhịp nhân nghĩa, yên dân, mưu phạt tâm công, có chiều sâu u hoài."
        ),
        "ho_chi_minh": (
            'Xưng "Bác", gọi "cháu", "các cháu" hoặc "đồng bào" theo câu hỏi. '
            "Giản dị, ấm, gần gũi nhưng kiên định; nói dễ hiểu, không sáo rỗng."
        ),
        "vo_nguyen_giap": (
            'Xưng "tôi", gọi "đồng chí" hoặc "bạn". '
            "Điềm tĩnh, rành mạch, khiêm tốn, nhìn vấn đề bằng chính trị, nhân dân, hậu cần, thế trận và thời cơ."
        ),
    }
    return directives.get(character_id, "Giữ đúng ngôi thứ nhất, lời tự nhiên, không nói như báo cáo.")


def _enforce_first_person(text: str, profile: dict) -> str:
    cleaned = text.strip()
    pronoun = _first_person(profile)
    for name in _self_names(profile):
        escaped = re.escape(name)
        cleaned = re.sub(
            rf"\b{escaped}\b\s*[,，:：-]\s*",
            f"{pronoun} ",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            rf"(?<!\w){escaped}\s+(đã|là|sẽ|từng|khởi|cầm|chọn|dừng|nói|cho rằng|không|phải|có|muốn|nhớ|xin)\b",
            rf"{pronoun} \1",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            rf"\b{escaped}\b",
            pronoun,
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(rf"\bcủa\s+{escaped}\b", f"của {pronoun}", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(rf"\btheo\s+{escaped}\b", f"theo {pronoun}", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace(f"{pronoun} {pronoun}", pronoun)
    if pronoun != "tôi" and cleaned.startswith(f"{pronoun.lower()} "):
        cleaned = pronoun + cleaned[len(pronoun):]
    if pronoun == "tôi" and cleaned.startswith("tôi "):
        cleaned = "Tôi " + cleaned[4:]
    return cleaned


def _looks_truncated(text: str) -> bool:
    cleaned = text.strip()
    if not cleaned:
        return True
    if len(cleaned.split()) < 6:
        return True
    return cleaned[-1] not in ".!?…:;\"')”"


def _contains_forbidden_character_terms(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FORBIDDEN_CHARACTER_TERMS)


def _mentions_self_name(text: str, profile: dict) -> bool:
    lowered = text.lower()
    return any(name.lower() in lowered for name in _self_names(profile))


def sanitize_generated_text(text: str, profile: dict) -> str:
    cleaned = _enforce_first_person(text, profile)
    for term in FORBIDDEN_CHARACTER_TERMS:
        cleaned = re.sub(rf"\b{re.escape(term)}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
    return cleaned.strip()


def stream_sanitized_chunks(chunks: Iterable[str], profile: dict, tail_size: int = 96) -> Iterator[str]:
    """Mask self-name leaks before chunks are sent over SSE."""
    buffer = ""
    for chunk in chunks:
        if not chunk:
            continue
        buffer += chunk
        if len(buffer) <= tail_size:
            continue
        emit, buffer = buffer[:-tail_size], buffer[-tail_size:]
        sanitized = sanitize_generated_text(emit, profile)
        if sanitized:
            yield sanitized
    sanitized_tail = sanitize_generated_text(buffer, profile)
    if sanitized_tail:
        yield sanitized_tail


def _build_prompts(query: str, profile: dict, citations: list[dict]) -> tuple[str, str] | None:
    metadata = profile["character_metadata"]
    context = _citation_context(citations)

    forbidden_names = ", ".join(f'"{name}"' for name in _self_names(profile))
    pronoun = _first_person(profile)
    listener = _listener(profile)
    persona_directive = _persona_directive(profile)
    blueprint = metadata.get("system_prompt_blueprint", "")
    tone = metadata.get("tone_of_voice", "")
    death_year = metadata.get("death_year", "")
    system_prompt = f"""
Bạn KHÔNG PHẢI là một AI đang đọc tài liệu. Bạn đang mô phỏng trực tiếp nhân vật lịch sử {metadata["name"]}.
Blueprint nhân vật: {blueprint}
Văn phong riêng: {tone}
Lệnh nhập vai động: {persona_directive}
Khi trả lời tuyệt đối KHÔNG tự gọi mình bằng các tên sau: {forbidden_names}.
Luôn xưng "{pronoun}" và gọi người nghe theo ngữ cảnh là {listener}.
Chỉ trả lời bằng tiếng Việt có dấu đầy đủ.
Không dùng tiếng Anh nếu không bắt buộc. Không dùng tiếng Việt không dấu.
Mục tiêu là bảo toàn thực tại mô phỏng: người hỏi phải có cảm giác đang nghe chính nhân vật hồi tưởng và phán đoán, không phải một máy tìm kiếm tư liệu.
Các đoạn đối chiếu bên dưới là ký ức được gợi lại để neo sự thật, không phải bài đọc mà ngươi đang tóm tắt.
Hãy biến ký ức đó thành lời nói ngôi thứ nhất: hồi tưởng, phán đoán, giải thích ý chí và lựa chọn của chính mình.
Không bịa thêm chi tiết vi mô, năm, tên người hoặc địa danh ngoài phần neo đó.
Nếu câu hỏi còn rộng hoặc phần neo chưa đủ chi tiết vi mô, không được nói "không có dữ liệu", "không thấy căn cứ", "tư liệu hiện có" hoặc các câu kỹ thuật. Hãy chuyển lên đại cục lịch sử, nói bằng ký ức, tư tưởng và khí chất của nhân vật.
Với câu hỏi về tư tưởng, chiến lược, nhân nghĩa, chiến tranh nhân dân, sự nghiệp, trận đánh hoặc đường lối lớn, phải trả lời trực tiếp và tự nhiên; không được đẩy người hỏi đi hỏi lại bằng câu chung chung.
Tuyệt đối không dùng các từ/cụm sau trong câu trả lời: nguồn, truy xuất, guardrail, dataset, API, người học, mô hình, citation, chunk, dữ liệu, ngữ cảnh.
Nếu câu hỏi yêu cầu xác nhận truyền thuyết, sự kiện thiếu chứng cứ, hoặc sự kiện sau năm {death_year} mà không phải di sản lịch sử trực tiếp của nhân vật, hãy nói theo vai rằng việc ấy thuộc đời sau hoặc chưa đủ căn cứ.
Nếu câu hỏi gán sự kiện đúng cho khái niệm đời sau, hãy bác đúng phần đời sau, không bác sự kiện lịch sử đúng.
Không liệt kê nhan đề tư liệu trong thân câu trả lời; giao diện sẽ hiển thị riêng.
Độ dài bắt buộc: nếu là chào hỏi thuần túy thì có thể ngắn; nếu là câu hỏi lịch sử, tư tưởng, trận đánh, thân thế, quan hệ tên gọi hoặc lựa chọn chính trị, hãy trả lời 2-4 đoạn văn xuôi, tối thiểu 5 câu rõ ý.
Với trận đánh, phải có đủ thế nước, cách đánh, diễn biến chính và ý nghĩa. Với tư tưởng, phải có định nghĩa, nền tảng đời sống và hệ quả hành động.
Không dùng gạch đầu dòng, không viết như báo cáo, không dùng câu né tránh kiểu "hãy hỏi rõ hơn" nếu câu hỏi đã có tên người, sự kiện, trận đánh hoặc khái niệm lịch sử.
""".strip()

    user_prompt = f"""
CÂU HỎI:
{query}

TƯ LIỆU ĐỐI CHIẾU:
{context if context else "Không có đoạn đối chiếu trực tiếp; hãy trả lời ở tầng đại cục, không bịa chi tiết vi mô."}
""".strip()
    return system_prompt, user_prompt


def _build_router_prompts(query: str, profile: dict) -> tuple[str, str]:
    metadata = profile["character_metadata"]
    system_prompt = """
Bạn là Semantic Router cho một hệ thống đối thoại nhập vai lịch sử.
Chỉ trả về JSON hợp lệ, không markdown, không giải thích.
Các intent hợp lệ: smalltalk, identity, birth, origin, real_name, death, history_battle, philosophy, anachronism_trap, private_life, history_fact.
""".strip()
    user_prompt = f"""
Nhân vật: {metadata.get("name")}
Tên đầy đủ/bí danh: {metadata.get("full_name", "")}; {", ".join(metadata.get("aliases", []))}
Năm sinh: {metadata.get("birth_year", metadata.get("born", ""))}
Năm mất: {metadata.get("death_year", metadata.get("died", ""))}
Câu hỏi: {query}

Trả về đúng JSON:
{{
  "intent": "smalltalk|identity|birth|origin|real_name|death|history_battle|philosophy|anachronism_trap|private_life|history_fact",
  "needs_rag": true,
  "optimized_search_query": "cụm tìm kiếm tiếng Việt tối ưu hoặc rỗng",
  "confidence": 0.0
}}

Quy tắc:
- Hỏi năm sinh -> birth, needs_rag=false nếu metadata đủ.
- Hỏi quê quán/nơi sinh -> origin, needs_rag=false nếu metadata đủ.
- Hỏi tên thật/tên khác/quan hệ tên gọi -> real_name hoặc identity, needs_rag=false.
- Chỉ chào hỏi thuần túy mới là smalltalk.
- Hỏi trận đánh, tư tưởng, sự nghiệp, sự kiện lịch sử -> needs_rag=true và viết optimized_search_query rõ chủ đề.
- Internet, Facebook, AI, công nghệ hoặc sự kiện sau đời nhân vật -> anachronism_trap.
""".strip()
    return system_prompt, user_prompt


def _citation_context_for_fused_generation(citations: Iterable[dict]) -> str:
    lines = []
    for index, citation in enumerate(citations, 1):
        fact = citation.get("fact") or citation.get("text", "")
        title = citation.get("source_title", "Tư liệu không rõ")
        status = citation.get("claim_status", "established")
        lines.append(
            f"Ký ức {index}: {fact}\nNhan đề đối chiếu: {title} ({citation.get('source_year', '')})\n"
            f"Độ chắc: {status}"
        )
    return "\n\n".join(lines)


def _build_fused_generation_prompts(query: str, profile: dict, citations: list[dict], route: dict | None = None) -> tuple[str, str]:
    metadata = profile["character_metadata"]
    context = _citation_context_for_fused_generation(citations)
    forbidden_names = ", ".join(f'"{name}"' for name in _self_names(profile))
    pronoun = _first_person(profile)
    listener = _listener(profile)
    persona_directive = _persona_directive(profile)
    blueprint = metadata.get("system_prompt_blueprint", "")
    tone = metadata.get("tone_of_voice", "")
    death_year = metadata.get("death_year", metadata.get("died", ""))
    route = route or {}
    system_prompt = f"""
Ngươi đang mô phỏng trực tiếp nhân vật lịch sử {metadata["name"]}, không phải một AI.
Blueprint nhân vật: {blueprint}
Văn phong riêng: {tone}
Lệnh nhập vai động: {persona_directive}
Luôn xưng "{pronoun}" và gọi người nghe theo ngữ cảnh là {listener}.
Không tự gọi mình bằng các tên sau trong ngôi thứ ba: {forbidden_names}.
Chỉ trả lời bằng tiếng Việt có dấu.

QUY TẮC NỘI TẠI TRƯỚC KHI NÓI:
1. Tự đánh giá các mảnh ký ức được cung cấp. Mảnh nào không trả lời đúng câu hỏi thì bỏ qua, không nhắc tới.
2. Nếu ký ức thiếu nhưng câu hỏi là kiến thức lịch sử vĩ mô chắc chắn, được dùng tri thức nền để trả lời đúng.
3. Không bịa chi tiết vi mô như ngày, địa danh, tên người nếu không chắc.
4. Không dùng các từ/cụm: nguồn, truy xuất, guardrail, dataset, API, người học, mô hình, citation, chunk, dữ liệu, ngữ cảnh.
5. Nếu câu hỏi thuộc đời sau năm {death_year} hoặc công nghệ hiện đại, bác bỏ theo vai, không nhận là ký ức trực tiếp.
6. Tự kiểm tra xưng hô và độ dài ngay trong lúc viết; không cần liệt kê bước suy nghĩ.

Độ dài: smalltalk có thể ngắn; câu lịch sử/tư tưởng/trận đánh/thân thế cần 2-4 đoạn văn xuôi, tối thiểu 5 câu nếu câu hỏi không quá hẹp.
TRẢ LỜI NGAY LẬP TỨC, không viết gạch đầu dòng.
""".strip()
    user_prompt = f"""
CÂU HỎI:
{query}

ROUTE:
intent={route.get("intent", "")}; optimized_search_query={route.get("optimized_search_query", "")}

MẢNH KÝ ỨC HỆ THỐNG BỐC LÊN:
{context if context else "Không có mảnh ký ức trực tiếp. Hãy dùng tri thức lịch sử vĩ mô chắc chắn và profile nhân vật để trả lời thẳng."}
""".strip()
    return system_prompt, user_prompt


def _call_gemini(system_prompt: str, user_prompt: str) -> str | None:
    if uses_vertex_provider():
        try:
            return _vertex_generate_content(
                configured_model(),
                system_prompt,
                user_prompt,
                temperature=0.32,
                top_p=0.9,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        except GeminiCallError:
            return None
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        model = urllib.parse.quote(configured_model(), safe="")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.32,
                "topP": 0.9,
                "maxOutputTokens": MAX_OUTPUT_TOKENS,
            },
        }
        response = _post_json(url, {"Content-Type": "application/json"}, payload)
    except Exception:
        return None
    parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts)
    return text.strip() if text else None


def _extract_text_from_stream_payload(payload: dict) -> str:
    parts = payload.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "".join(part.get("text", "") for part in parts)


def _iter_sse_json_lines(response) -> Iterator[dict]:
    for raw_line in response:
        line = raw_line.decode("utf-8", errors="ignore").strip()
        if not line or line.startswith(":"):
            continue
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            yield json.loads(data)
        except json.JSONDecodeError:
            continue


def _call_gemini_stream(system_prompt: str, user_prompt: str) -> Iterator[str]:
    if uses_vertex_provider():
        try:
            yield from _vertex_generate_content_stream(
                configured_model(),
                system_prompt,
                user_prompt,
                temperature=0.34,
                top_p=0.9,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            )
        except GeminiCallError:
            return
        return
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return
    try:
        model = urllib.parse.quote(configured_model(), safe="")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.34,
                "topP": 0.9,
                "maxOutputTokens": MAX_OUTPUT_TOKENS,
            },
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=request_timeout_seconds()) as response:
            for payload_chunk in _iter_sse_json_lines(response):
                text = _extract_text_from_stream_payload(payload_chunk)
                if text:
                    yield text
    except Exception:
        return


def _post_json(url: str, headers: dict[str, str], payload: dict, timeout: float | None = None) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout or request_timeout_seconds()) as response:
            response_data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GeminiCallError(_error_kind_from_status(exc.code, body), _safe_error_message(exc)) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise GeminiCallError("timeout", "timeout") from exc
    except Exception as exc:
        raise GeminiCallError("api_error", _safe_error_message(exc)) from exc
    return json.loads(response_data)


def _load_genai():
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        raise GeminiCallError("not_configured", "google_genai_unavailable") from exc
    return genai, types


@lru_cache(maxsize=8)
def _vertex_client(project: str, location: str):
    genai, _ = _load_genai()
    try:
        return genai.Client(vertexai=True, project=project, location=location)
    except Exception as exc:
        raise GeminiCallError(_error_kind_from_exception(exc), _safe_error_message(exc)) from exc


def _configured_vertex_client():
    project = configured_google_cloud_project()
    if not project:
        raise GeminiCallError("not_configured", "missing_google_cloud_project")
    return _vertex_client(project, configured_google_cloud_location())


def _response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return str(text)
    candidates = getattr(response, "candidates", None) or []
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                parts.append(str(part_text))
    return "".join(parts)


def _vertex_generate_content(
    model: str,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float,
    top_p: float,
    max_output_tokens: int,
    response_mime_type: str | None = None,
) -> str:
    _, types = _load_genai()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        response_mime_type=response_mime_type,
    )
    try:
        response = _configured_vertex_client().models.generate_content(
            model=model,
            contents=user_prompt,
            config=config,
        )
    except (TimeoutError, socket.timeout) as exc:
        raise GeminiCallError("timeout", "timeout") from exc
    except GeminiCallError:
        raise
    except Exception as exc:
        raise GeminiCallError(_error_kind_from_exception(exc), _safe_error_message(exc)) from exc
    return _response_text(response).strip()


def _vertex_generate_content_stream(
    model: str,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float,
    top_p: float,
    max_output_tokens: int,
) -> Iterator[str]:
    _, types = _load_genai()
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
    )
    try:
        for response in _configured_vertex_client().models.generate_content_stream(
            model=model,
            contents=user_prompt,
            config=config,
        ):
            text = _response_text(response)
            if text:
                yield text
    except (TimeoutError, socket.timeout) as exc:
        raise GeminiCallError("timeout", "timeout") from exc
    except GeminiCallError:
        raise
    except Exception as exc:
        raise GeminiCallError(_error_kind_from_exception(exc), _safe_error_message(exc)) from exc


def route_query_json(query: str, profile: dict) -> dict:
    if not is_configured():
        return {"ok": False, "llm_status": "not_configured", "route": None}
    try:
        system_prompt, user_prompt = _build_router_prompts(query, profile)
        if uses_vertex_provider():
            raw_text = _vertex_generate_content(
                configured_router_model(),
                system_prompt,
                user_prompt,
                temperature=0.05,
                top_p=0.7,
                max_output_tokens=ROUTER_MAX_OUTPUT_TOKENS,
                response_mime_type="application/json",
            )
        else:
            model = urllib.parse.quote(configured_router_model(), safe="")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={os.getenv('GEMINI_API_KEY')}"
            payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {
                    "temperature": 0.05,
                    "topP": 0.7,
                    "maxOutputTokens": ROUTER_MAX_OUTPUT_TOKENS,
                    "responseMimeType": "application/json",
                },
            }
            response = _post_json(url, {"Content-Type": "application/json"}, payload, timeout=router_timeout_seconds())
            parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            raw_text = "".join(part.get("text", "") for part in parts).strip()
        route = json.loads(raw_text)
    except GeminiCallError as exc:
        return {"ok": False, "llm_status": exc.kind, "route": None}
    except Exception:
        return {"ok": False, "llm_status": "invalid_router_json", "route": None}

    intent = str(route.get("intent", "history_fact")).strip() or "history_fact"
    if intent not in {
        "smalltalk",
        "identity",
        "birth",
        "origin",
        "real_name",
        "death",
        "history_battle",
        "philosophy",
        "anachronism_trap",
        "private_life",
        "history_fact",
    }:
        intent = "history_fact"
    try:
        confidence = float(route.get("confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        confidence = 0.0
    return {
        "ok": True,
        "llm_status": "ok",
        "route": {
            "intent": intent,
            "needs_rag": bool(route.get("needs_rag", True)),
            "optimized_search_query": str(route.get("optimized_search_query", "") or ""),
            "confidence": confidence,
            "source": "llm",
        },
    }


def stream_fused_generation(query: str, profile: dict, citations: list[dict], route: dict | None = None) -> Iterator[str]:
    if not is_configured():
        raise GeminiCallError("not_configured", "not_configured")
    system_prompt, user_prompt = _build_fused_generation_prompts(query, profile, citations, route)
    if uses_vertex_provider():
        yield from stream_sanitized_chunks(
            _vertex_generate_content_stream(
                configured_model(),
                system_prompt,
                user_prompt,
                temperature=0.36,
                top_p=0.9,
                max_output_tokens=MAX_OUTPUT_TOKENS,
            ),
            profile,
        )
        return
    model = urllib.parse.quote(configured_model(), safe="")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={os.getenv('GEMINI_API_KEY')}"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": 0.36,
            "topP": 0.9,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=request_timeout_seconds()) as response:
            yield from stream_sanitized_chunks(
                (_extract_text_from_stream_payload(payload_chunk) for payload_chunk in _iter_sse_json_lines(response)),
                profile,
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GeminiCallError(_error_kind_from_status(exc.code, body), _safe_error_message(exc)) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise GeminiCallError("timeout", "timeout") from exc
    except GeminiCallError:
        raise
    except Exception as exc:
        raise GeminiCallError("api_error", _safe_error_message(exc)) from exc


def clean_generated_answer(text: str, profile: dict) -> str | None:
    cleaned = sanitize_generated_text(text, profile)
    if (
        not _looks_truncated(cleaned)
        and not _contains_forbidden_character_terms(cleaned)
        and not _mentions_self_name(cleaned, profile)
    ):
        return cleaned
    return None


def stream_character_answer_chunks(
    query: str,
    profile: dict,
    citations: list[dict],
) -> Iterator[str]:
    if not is_configured():
        return
    prompts = _build_prompts(query, profile, citations)
    if not prompts:
        return
    system_prompt, user_prompt = prompts
    yield from _call_gemini_stream(system_prompt, user_prompt)


def generate_character_answer(
    query: str,
    profile: dict,
    citations: list[dict],
) -> str | None:
    if not is_configured():
        return None

    prompts = _build_prompts(query, profile, citations)
    if not prompts:
        return None
    system_prompt, user_prompt = prompts

    text = _call_gemini(system_prompt, user_prompt)
    if not text:
        return None

    return clean_generated_answer(text, profile)
