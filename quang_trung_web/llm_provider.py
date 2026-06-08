import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable, Iterator


ROOT_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass


MODEL_NAME = "gemini-3.5-flash"
DEFAULT_TIMEOUT_SECONDS = 18.0
MAX_OUTPUT_TOKENS = 1400

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


def _post_json(url: str, headers: dict[str, str], payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=request_timeout_seconds()) as response:
        response_data = response.read().decode("utf-8")
    return json.loads(response_data)


def clean_generated_answer(text: str, profile: dict) -> str | None:
    cleaned = _enforce_first_person(text, profile)
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
