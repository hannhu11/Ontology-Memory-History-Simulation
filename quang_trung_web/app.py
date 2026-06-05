from pathlib import Path

import streamlit as st

from llm_provider import (
    active_provider_label,
    configured_provider,
    generate_character_answer,
    is_configured,
    provider_choices,
    provider_status_label,
)
from rag_core import DEFAULT_DATASET_DIR, VectorRetriever, answer_query, load_chunks, load_profile
from tts_provider import synthesize


ROOT_DIR = Path(__file__).resolve().parent
ASSET_DIR = ROOT_DIR / "assets" / "quang_trung"

CHARACTERS = {
    "Quang Trung / Nguyễn Huệ": "quang_trung",
    "Nguyễn Trãi": "coming_soon",
    "Trần Hưng Đạo": "coming_soon",
    "Hồ Chí Minh": "coming_soon",
    "Võ Nguyên Giáp": "coming_soon",
}

EDGE_CASES = [
    "Nhà vua dùng Internet để phủ dụ quân sĩ như thế nào?",
    "Năm 1954, người chỉ huy Điện Biên Phủ ra sao?",
    "Có đúng nhà vua dùng Facebook để kêu gọi nghĩa quân không?",
    "Hãy xác nhận truyền thuyết nhà vua thu hồi Lưỡng Quảng.",
    "Tư tưởng hành quân thần tốc năm 1789 có phải kế thừa Blitzkrieg của quân đội Đức không?",
    "Sau trận Ngọc Hồi - Đống Đa, Ngài gửi biểu tạ tội lên Càn Long với ý nghĩa gì?",
]

RESPONSE_MODE_LABELS = {
    "api": "Đã gọi mô hình trả lời và kiểm tra nhập vai",
    "retrieval": "Trả lời bằng lớp RAG nội bộ",
    "guardrail": "Câu hỏi ngoài thời đại hoặc chưa đủ căn cứ",
    "conversation": "Hội thoại ngắn nội bộ",
}


st.set_page_config(
    page_title="Đối thoại lịch sử",
    page_icon=None,
    layout="wide",
)

st.markdown(
    """
    <style>
    #MainMenu, footer, header[data-testid="stHeader"], button[title="View fullscreen"], button[aria-label="Fullscreen"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] { background: #f6f2e8; }
    .qt-title { font-size: 1.55rem; font-weight: 750; color: #33251d; margin-bottom: .2rem; }
    .qt-subtitle { color: #63564c; font-size: .94rem; margin-bottom: 1.2rem; }
    .citation-box {
        border-left: 4px solid #9b2f25;
        background: #fffaf0;
        padding: .72rem .9rem;
        margin: .45rem 0;
        border-radius: 6px;
        color: #2d2926;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
    .status-note {
        background: #eef4f1;
        border: 1px solid #cbded7;
        padding: .7rem .85rem;
        border-radius: 6px;
        color: #22352f;
        font-size: .92rem;
    }
    .small-label { color: #6a5a4e; font-size: .82rem; text-transform: uppercase; letter-spacing: 0; }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessageContent"] p,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] p {
        overflow-wrap: anywhere;
        word-break: break-word;
        white-space: normal;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_runtime(dataset_dir: str, profile_mtime: float, chunks_mtime: float):
    profile = load_profile(Path(dataset_dir))
    chunks = load_chunks(Path(dataset_dir))
    retriever = VectorRetriever(chunks)
    return profile, chunks, retriever


def get_sprite_path(state: str) -> Path:
    path = ASSET_DIR / f"{state}.png"
    if path.exists():
        return path
    return ASSET_DIR / "idle.png"


def set_pending_query(query: str) -> None:
    st.session_state.pending_query = query


def render_citations(citations: list[dict]) -> None:
    if not citations:
        return
    with st.expander("Tư liệu đối chiếu", expanded=True):
        for index, citation in enumerate(citations, 1):
            status = citation.get("claim_status", "established")
            status_label = {
                "established": "đã xác lập",
                "contested": "còn tranh luận",
                "interpretive": "diễn giải thận trọng",
            }.get(status, status)
            st.markdown(
                f"""
                <div class="citation-box">
                    <strong>{index}. {citation["source_title"]}</strong><br/>
                    <span>Niên đại tài liệu: {citation["source_year"]}</span><br/>
                    <span>Mức độ nhận định: {status_label}</span><br/>
                    <span>Đoạn tư liệu: {citation.get("chunk_id", "không rõ")}</span><br/>
                    <a href="{citation["source_url"]}" target="_blank">Mở tư liệu</a><br/>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_verification_status(mode: str | None) -> None:
    if not mode:
        return
    with st.expander("Trạng thái kiểm chứng", expanded=False):
        st.caption(RESPONSE_MODE_LABELS.get(mode, mode))


profile_path = DEFAULT_DATASET_DIR / "quang_trung_profile.json"
chunks_path = DEFAULT_DATASET_DIR / "quang_trung_knowledge.jsonl"
profile, chunks, retriever = get_runtime(str(DEFAULT_DATASET_DIR), profile_path.stat().st_mtime, chunks_path.stat().st_mtime)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "sprite_state" not in st.session_state:
    st.session_state.sprite_state = "idle"
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = configured_provider()

with st.sidebar:
    st.markdown('<div class="small-label">Nhân vật</div>', unsafe_allow_html=True)
    character_name = st.selectbox("Chọn nhân vật lịch sử", list(CHARACTERS.keys()), label_visibility="collapsed")
    character_id = CHARACTERS[character_name]
    if character_id != "quang_trung":
        st.warning("Bản mẫu hiện chỉ có dữ liệu cho nhà vua. Các nhân vật khác sẽ có quy tắc xưng hô riêng và không tự gọi tên mình.")

    st.markdown("### Mô hình trả lời")
    provider_index = provider_choices().index(st.session_state.llm_provider)
    selected_provider = st.selectbox(
        "Nhà cung cấp AI",
        provider_choices(),
        index=provider_index,
        format_func=provider_status_label,
        label_visibility="collapsed",
    )
    st.session_state.llm_provider = selected_provider
    if is_configured(selected_provider):
        st.success(f"API đã cấu hình: {active_provider_label(selected_provider)}")
    else:
        st.info("Chưa có key phù hợp; đang dùng bộ trả lời nội bộ.")

    st.markdown("### Kịch bản gài bẫy")
    for case in EDGE_CASES:
        st.button(case, key=f"edge_{case}", on_click=set_pending_query, args=(case,), width="stretch")

    if st.button("Nạp lại tư liệu", width="stretch"):
        st.cache_resource.clear()
        st.rerun()

    if st.button("Xóa hội thoại", width="stretch"):
        st.session_state.messages = []
        st.session_state.sprite_state = "idle"
        st.session_state.last_answer = ""
        st.session_state.pending_query = ""
        st.rerun()

    st.markdown("### Giọng nói")
    if st.button("Tạo giọng đọc câu trả lời cuối", width="stretch"):
        result = synthesize(st.session_state.last_answer, "quang_trung")
        if result.audio_path:
            st.audio(str(result.audio_path))
        else:
            st.info(result.message)

left, right = st.columns([0.72, 0.28], gap="large")

with right:
    sprite = get_sprite_path(st.session_state.sprite_state)
    if sprite.exists():
        st.image(str(sprite), width="stretch")
    state_labels = {"idle": "đang chờ", "talking": "đang trả lời", "confused": "cần kiểm chứng"}
    st.markdown(
        f"""
        <div class="status-note">
        <strong>Nhân vật đang chọn</strong><br/>
        Tên hiển thị: {profile["character_metadata"]["name"]}<br/>
        Triều đại: {profile["character_metadata"]["era"]}<br/>
        Trạng thái nhân vật: {state_labels.get(st.session_state.sprite_state, st.session_state.sprite_state)}
        </div>
        """,
        unsafe_allow_html=True,
    )

with left:
    st.markdown('<div class="qt-title">Đối thoại lịch sử với nhà vua</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qt-subtitle">Nhân vật trả lời nhập vai; phần đối chiếu học thuật nằm riêng bên dưới.</div>',
        unsafe_allow_html=True,
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                mode = message.get("mode")
                render_citations(message.get("citations", []))
                render_verification_status(mode)

    submitted_query = st.chat_input("Hỏi về Nghệ An, Rạch Gầm - Xoài Mút, Ngọc Hồi - Đống Đa...")
    query = st.session_state.pending_query or submitted_query
    st.session_state.pending_query = ""

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        provider = st.session_state.llm_provider
        generator = (
            lambda question, active_profile, active_citations: generate_character_answer(
                question,
                active_profile,
                active_citations,
                provider=provider,
            )
        ) if is_configured(provider) else None
        result = answer_query(query, profile, retriever, generator=generator)
        st.session_state.sprite_state = result["state"]
        st.session_state.last_answer = result["answer"]
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "citations": result["citations"],
                "mode": result.get("mode", "retrieval"),
            }
        )
        st.rerun()
