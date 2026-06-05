import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass


DEFAULT_PROVIDER = "auto"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_TIMEOUT_SECONDS = 18.0
PROVIDER_LABELS = {
    "auto": "Tự động",
    "groq": "Groq",
    "gemini": "Gemini",
}

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


def provider_choices() -> list[str]:
    return ["auto", "groq", "gemini"]


def auto_provider_order() -> list[str]:
    raw_order = os.getenv("LLM_PROVIDER_ORDER", "gemini,groq")
    order = [item.strip().lower() for item in raw_order.split(",")]
    return [item for item in order if item in {"groq", "gemini"}] or ["gemini", "groq"]


def configured_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()
    return provider if provider in provider_choices() else DEFAULT_PROVIDER


def configured_model(provider: str | None = None) -> str:
    provider = provider or configured_provider()
    if provider == "gemini":
        return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
    if provider == "auto":
        return " / ".join(configured_model(item) for item in auto_provider_order())
    return os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL


def is_configured(provider: str | None = None) -> bool:
    provider = provider or configured_provider()
    if provider == "auto":
        return is_configured("groq") or is_configured("gemini")
    if provider == "gemini":
        return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    return bool(os.getenv("GROQ_API_KEY"))


def provider_status_label(provider: str) -> str:
    label = PROVIDER_LABELS.get(provider, provider)
    if provider == "auto":
        available = [PROVIDER_LABELS[item] for item in auto_provider_order() if is_configured(item)]
        suffix = ", ".join(available) if available else "chưa có key"
        return f"{label} ({suffix})"
    status = "đã có key" if is_configured(provider) else "chưa có key"
    return f"{label} - {configured_model(provider)} ({status})"


def active_provider_label(provider: str | None = None) -> str:
    provider = provider or configured_provider()
    if provider == "auto":
        ordered = " -> ".join(
            f"{PROVIDER_LABELS[item]} {configured_model(item)}" for item in auto_provider_order()
        )
        return f"Tự động: {ordered}"
    return f"{PROVIDER_LABELS.get(provider, provider)}: {configured_model(provider)}"


def request_timeout_seconds() -> float:
    raw_value = os.getenv("LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    try:
        return max(5.0, float(raw_value))
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


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


def _enforce_first_person(text: str, profile: dict) -> str:
    cleaned = text.strip()
    for name in _self_names(profile):
        escaped = re.escape(name)
        cleaned = re.sub(
            rf"(?<!\w){escaped}\s+(đã|là|sẽ|từng|khởi|cầm|chọn|dừng|nói|cho rằng|không|phải|có|muốn|nhớ|xin)\b",
            r"ta \1",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(rf"\bcủa\s+{escaped}\b", "của ta", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(rf"\btheo\s+{escaped}\b", "theo ta", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("Ta ta", "Ta").replace("ta ta", "ta")
    if cleaned.startswith("ta "):
        cleaned = "Ta " + cleaned[3:]
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


def _build_prompts(query: str, profile: dict, citations: list[dict]) -> tuple[str, str] | None:
    metadata = profile["character_metadata"]
    context = _citation_context(citations)
    if not context:
        return None

    forbidden_names = ", ".join(f'"{name}"' for name in _self_names(profile))
    system_prompt = f"""
Bạn đang đóng vai {metadata["name"]}, nhưng khi trả lời tuyệt đối KHÔNG tự gọi mình bằng các tên sau: {forbidden_names}.
Luôn xưng "ta".
Chỉ trả lời bằng tiếng Việt có dấu đầy đủ.
Không dùng tiếng Anh nếu không bắt buộc. Không dùng tiếng Việt không dấu.
Văn phong: dứt khoát, trang trọng, có khí phách của người cầm quân, nhưng không khoa trương.
Chỉ dùng các tư liệu đối chiếu được cung cấp bên dưới; không bịa thêm sự kiện, năm, tên người hoặc địa danh.
Tuyệt đối không dùng các từ/cụm sau trong câu trả lời: nguồn, truy xuất, guardrail, dataset, API, người học, mô hình, citation, chunk.
Nếu câu hỏi yêu cầu xác nhận truyền thuyết, sự kiện thiếu chứng cứ, hoặc sự kiện sau năm {metadata["death_year"]} như Thế chiến, World War, Internet, Facebook, AI, máy bay hiện đại, hãy nói theo vai: "Việc ấy chưa đủ chứng cứ để ta nhận là thật" hoặc "ngươi hỏi chuyện đời sau khi ta đã mất năm 1792".
Nếu câu hỏi gán sự kiện đúng cho khái niệm đời sau, hãy bác đúng phần đời sau, không bác sự kiện lịch sử đúng.
Không liệt kê nhan đề tư liệu trong thân câu trả lời; giao diện sẽ hiển thị riêng.
Trả lời 1-2 đoạn ngắn, tự nhiên, hợp lý cho hậu thế.
""".strip()

    user_prompt = f"""
CÂU HỎI:
{query}

TƯ LIỆU ĐỐI CHIẾU:
{context}
""".strip()
    return system_prompt, user_prompt


def _call_groq(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        payload = {
            "model": configured_model("groq"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.25,
            "max_completion_tokens": 700,
        }
        response = _post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            payload,
        )
    except Exception:
        return None
    return response["choices"][0]["message"]["content"].strip()


def _call_gemini(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        model = urllib.parse.quote(configured_model("gemini"), safe="")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": 700,
            },
        }
        response = _post_json(url, {"Content-Type": "application/json"}, payload)
    except Exception:
        return None
    parts = response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts)
    return text.strip() if text else None


def _post_json(url: str, headers: dict[str, str], payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=request_timeout_seconds()) as response:
        response_data = response.read().decode("utf-8")
    return json.loads(response_data)


def _provider_order(provider: str) -> list[str]:
    if provider != "auto":
        return [provider]
    return auto_provider_order()


def generate_character_answer(
    query: str,
    profile: dict,
    citations: list[dict],
    provider: str | None = None,
) -> str | None:
    provider = provider or configured_provider()
    if not is_configured(provider):
        return None

    prompts = _build_prompts(query, profile, citations)
    if not prompts:
        return None
    system_prompt, user_prompt = prompts

    callers = {
        "groq": _call_groq,
        "gemini": _call_gemini,
    }
    for item in _provider_order(provider):
        if not is_configured(item):
            continue
        text = callers[item](system_prompt, user_prompt)
        if text:
            cleaned = _enforce_first_person(text, profile)
            if (
                not _looks_truncated(cleaned)
                and not _contains_forbidden_character_terms(cleaned)
                and not _mentions_self_name(cleaned, profile)
            ):
                return cleaned
    return None
