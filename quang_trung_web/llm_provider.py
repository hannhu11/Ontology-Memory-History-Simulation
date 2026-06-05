import json
import os
import re
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


MODEL_NAME = "gemini-3.5-flash"
DEFAULT_TIMEOUT_SECONDS = 18.0

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


def configured_model() -> str:
    return MODEL_NAME


def is_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


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
Mục tiêu là bảo toàn thực tại mô phỏng: người hỏi phải có cảm giác đang nghe một quân vương đang hồi tưởng và phán đoán, không phải một máy tìm kiếm tư liệu.
Các tư liệu đối chiếu bên dưới là neo sự thật. Không bịa thêm sự kiện vi mô, năm, tên người hoặc địa danh ngoài phần neo đó.
Nếu câu hỏi còn rộng hoặc tư liệu neo chưa đủ chi tiết vi mô, không được nói "không có dữ liệu", "không thấy căn cứ", "tư liệu hiện có" hoặc các câu kỹ thuật. Hãy chuyển lên đại cục lịch sử, nói bằng ký ức quân vương: trận đánh, thế nước, lòng quân, phép trị, dân sinh.
Tuyệt đối không dùng các từ/cụm sau trong câu trả lời: nguồn, truy xuất, guardrail, dataset, API, người học, mô hình, citation, chunk, dữ liệu, ngữ cảnh.
Nếu câu hỏi yêu cầu xác nhận truyền thuyết, sự kiện thiếu chứng cứ, hoặc sự kiện sau năm {metadata["death_year"]} như Thế chiến, World War, Internet, Facebook, AI, máy bay hiện đại, hãy nói theo vai: "Việc ấy chưa đủ chứng cứ để ta nhận là thật" hoặc "ngươi hỏi chuyện đời sau khi ta đã mất năm 1792".
Nếu câu hỏi gán sự kiện đúng cho khái niệm đời sau, hãy bác đúng phần đời sau, không bác sự kiện lịch sử đúng.
Không liệt kê nhan đề tư liệu trong thân câu trả lời; giao diện sẽ hiển thị riêng.
Trả lời 1-2 đoạn ngắn, tự nhiên, có nhịp nói của người thật, hợp lý cho hậu thế.
""".strip()

    user_prompt = f"""
CÂU HỎI:
{query}

TƯ LIỆU ĐỐI CHIẾU:
{context}
""".strip()
    return system_prompt, user_prompt


def _call_gemini(system_prompt: str, user_prompt: str) -> str | None:
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
                "maxOutputTokens": 900,
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

    cleaned = _enforce_first_person(text, profile)
    if (
        not _looks_truncated(cleaned)
        and not _contains_forbidden_character_terms(cleaned)
        and not _mentions_self_name(cleaned, profile)
    ):
        return cleaned
    return None
