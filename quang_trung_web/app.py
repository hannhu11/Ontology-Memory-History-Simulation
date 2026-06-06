import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from llm_provider import generate_character_answer, is_configured
from character_registry import (
    CHARACTER_REGISTRY,
    DEFAULT_CHARACTER_ID,
    DISPLAY_NAME_TO_ID,
    get_character_config,
    knowledge_path_for,
    profile_path_for,
)
from rag_core import VectorRetriever, answer_query, load_chunks, load_profile
from tts_provider import synthesize


ROOT_DIR = Path(__file__).resolve().parent

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
    .neutral-portrait {
        border: 1px solid rgba(116, 83, 39, .28);
        background: linear-gradient(180deg, #2c211b 0%, #151311 100%);
        color: #e2c16a;
        border-radius: 7px;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 1rem;
        font-weight: 750;
        letter-spacing: 0;
        box-shadow: inset 0 0 0 1px rgba(226, 193, 106, .16);
    }
    .small-label { color: #6a5a4e; font-size: .82rem; text-transform: uppercase; letter-spacing: 0; }
    .tts-status {
        border: 1px solid rgba(116, 108, 93, .22);
        background: #f7f1e5;
        color: #5b5046;
        padding: .58rem .72rem;
        border-radius: 6px;
        font-size: .86rem;
        margin: .48rem 0 .35rem;
    }
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
def get_runtime(character_id: str, profile_mtime: float, chunks_mtime: float):
    profile = load_profile(character_id)
    chunks = load_chunks(character_id)
    retriever = VectorRetriever(chunks, character_id=character_id)
    return profile, chunks, retriever


def get_sprite_path(character_id: str, state: str) -> Path | None:
    asset_dir = get_character_config(character_id)["asset_dir"]
    path = asset_dir / f"{state}.png"
    if path.exists():
        return path
    fallback = asset_dir / "idle.png"
    if fallback.exists():
        return fallback
    quang_fallback = get_character_config(DEFAULT_CHARACTER_ID)["asset_dir"] / f"{state}.png"
    if quang_fallback.exists() and character_id == DEFAULT_CHARACTER_ID:
        return quang_fallback
    return None


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


def render_audio_player(audio_base64: str, message_id: str, autoplay: bool = True) -> None:
    audio_src = html.escape(f"data:audio/mpeg;base64,{audio_base64}", quote=True)
    safe_id = html.escape(message_id, quote=True)
    autoplay_attr = "autoplay" if autoplay else ""
    player_html = f"""
    <div class="qt-tts-shell" data-player="{safe_id}">
      <audio id="qt-tts-audio" src="{audio_src}" preload="auto" {autoplay_attr}></audio>
      <div class="qt-tts-top">
        <button id="qt-tts-toggle" type="button" aria-label="Phát giọng đọc">Phát</button>
        <div class="qt-tts-copy">
          <div class="qt-tts-kicker"><span></span> Âm thanh nhập vai</div>
          <div id="qt-tts-label" class="qt-tts-label">Bấm phát nếu trình duyệt chặn tự động đọc</div>
        </div>
        <div id="qt-tts-time" class="qt-tts-time">0:00</div>
      </div>
      <button id="qt-tts-track" class="qt-tts-track" type="button" aria-label="Tua giọng đọc">
        <span id="qt-tts-progress"></span>
      </button>
    </div>
    <style>
      :root {{
        --ks-kinpaku: oklch(84% 0.19 80.46);
        --ks-kinpaku-pale: oklch(86% 0.07 84);
        --ks-patina: oklch(70% 0.12 188);
        --ks-lacquer-deep: oklch(4% 0.004 95);
        --ks-lacquer-raised: oklch(11% 0.006 95);
        --ks-graphite: oklch(15% 0.008 95);
        --ks-champagne: oklch(91% 0 0);
        --ks-text: oklch(88% 0 0);
        --ks-text-muted: oklch(72% 0 0);
        --ks-rule: oklch(78% 0 0 / 0.16);
        --ks-ease: cubic-bezier(0.2, 0.8, 0.2, 1);
      }}
      html, body {{
        margin: 0;
        background: transparent;
        color-scheme: dark;
        font-family: "Albert Sans", "Avenir Next", "Helvetica Neue", Arial, system-ui, sans-serif;
      }}
      .qt-tts-shell {{
        box-sizing: border-box;
        width: 100%;
        padding: 12px 14px;
        margin: 2px 0 4px;
        border: 1px solid var(--ks-rule);
        border-radius: 8px;
        background:
          linear-gradient(135deg, oklch(84% 0.19 80.46 / 0.08), transparent 32%),
          linear-gradient(180deg, var(--ks-lacquer-raised), var(--ks-lacquer-deep));
        color: var(--ks-text);
      }}
      .qt-tts-top {{
        display: grid;
        grid-template-columns: 48px minmax(0, 1fr) auto;
        gap: 12px;
        align-items: center;
      }}
      #qt-tts-toggle {{
        width: 44px;
        height: 36px;
        border: 1px solid var(--ks-kinpaku);
        border-radius: 4px;
        background: var(--ks-kinpaku);
        color: var(--ks-lacquer-deep);
        font: 600 0.82rem/1 "Albert Sans", Arial, sans-serif;
        cursor: pointer;
        transition: transform 180ms var(--ks-ease), background 180ms var(--ks-ease);
      }}
      #qt-tts-toggle:hover {{
        background: var(--ks-kinpaku-pale);
        transform: translateY(-1px);
      }}
      .qt-tts-copy {{
        min-width: 0;
      }}
      .qt-tts-kicker {{
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--ks-kinpaku);
        font: 600 0.68rem/1.2 "SFMono-Regular", Consolas, monospace;
        letter-spacing: .12em;
        text-transform: uppercase;
      }}
      .qt-tts-kicker span {{
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: var(--ks-patina);
        box-shadow: 0 0 18px oklch(70% 0.12 188 / .38);
      }}
      .qt-tts-label {{
        margin-top: 5px;
        color: var(--ks-champagne);
        font-size: .86rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }}
      .qt-tts-time {{
        color: var(--ks-text-muted);
        font: 600 .78rem/1 "SFMono-Regular", Consolas, monospace;
      }}
      .qt-tts-track {{
        position: relative;
        display: block;
        width: 100%;
        height: 8px;
        margin-top: 12px;
        padding: 0;
        border: 1px solid oklch(78% 0 0 / .14);
        border-radius: 999px;
        background: var(--ks-graphite);
        overflow: hidden;
        cursor: pointer;
      }}
      #qt-tts-progress {{
        position: absolute;
        inset: 0 auto 0 0;
        width: 0%;
        background: linear-gradient(90deg, var(--ks-kinpaku), var(--ks-patina));
      }}
      @media (max-width: 520px) {{
        .qt-tts-top {{
          grid-template-columns: 46px minmax(0, 1fr);
        }}
        .qt-tts-time {{
          grid-column: 2;
          justify-self: start;
        }}
      }}
    </style>
    <script>
      const audio = document.getElementById("qt-tts-audio");
      const toggle = document.getElementById("qt-tts-toggle");
      const label = document.getElementById("qt-tts-label");
      const progress = document.getElementById("qt-tts-progress");
      const track = document.getElementById("qt-tts-track");
      const time = document.getElementById("qt-tts-time");

      function formatTime(value) {{
        if (!Number.isFinite(value) || value < 0) return "0:00";
        const minutes = Math.floor(value / 60);
        const seconds = Math.floor(value % 60).toString().padStart(2, "0");
        return `${{minutes}}:${{seconds}}`;
      }}

      function updateProgress() {{
        if (!audio.duration) {{
          progress.style.width = "0%";
          time.textContent = "0:00";
          return;
        }}
        const pct = Math.min(100, Math.max(0, (audio.currentTime / audio.duration) * 100));
        progress.style.width = `${{pct}}%`;
        time.textContent = `${{formatTime(audio.currentTime)}} / ${{formatTime(audio.duration)}}`;
      }}

      async function playAudio() {{
        try {{
          await audio.play();
        }} catch (error) {{
          label.textContent = "Trình duyệt đã chặn tự động đọc. Bấm Phát để nghe.";
        }}
      }}

      toggle.addEventListener("click", () => {{
        if (audio.paused) {{
          playAudio();
        }} else {{
          audio.pause();
        }}
      }});

      track.addEventListener("click", (event) => {{
        if (!audio.duration) return;
        const rect = track.getBoundingClientRect();
        const pct = (event.clientX - rect.left) / rect.width;
        audio.currentTime = Math.min(audio.duration, Math.max(0, pct * audio.duration));
      }});

      audio.addEventListener("play", () => {{
        toggle.textContent = "Dừng";
        label.textContent = "Đang đọc lời nhân vật";
      }});
      audio.addEventListener("pause", () => {{
        toggle.textContent = "Phát";
        if (!audio.ended) label.textContent = "Tạm dừng giọng đọc";
      }});
      audio.addEventListener("ended", () => {{
        toggle.textContent = "Phát";
        label.textContent = "Đã đọc xong";
      }});
      audio.addEventListener("loadedmetadata", updateProgress);
      audio.addEventListener("timeupdate", updateProgress);
      if (audio.autoplay) playAudio();
    </script>
    """
    components.html(player_html, height=118, scrolling=False)


if "messages" not in st.session_state:
    st.session_state.messages = []
if "sprite_state" not in st.session_state:
    st.session_state.sprite_state = "idle"
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""
if "character_id" not in st.session_state:
    st.session_state.character_id = DEFAULT_CHARACTER_ID

with st.sidebar:
    st.markdown('<div class="small-label">Nhân vật</div>', unsafe_allow_html=True)
    display_names = [config["display_name"] for config in CHARACTER_REGISTRY.values()]
    current_display = get_character_config(st.session_state.character_id)["display_name"]
    character_name = st.selectbox(
        "Chọn nhân vật lịch sử",
        display_names,
        index=display_names.index(current_display),
        label_visibility="collapsed",
    )
    character_id = DISPLAY_NAME_TO_ID[character_name]
    if character_id != st.session_state.character_id:
        st.session_state.character_id = character_id
        st.session_state.messages = []
        st.session_state.sprite_state = "idle"
        st.session_state.last_answer = ""
        st.session_state.pending_query = ""
        st.rerun()
    character_config = get_character_config(character_id)

    st.markdown("### Kịch bản gài bẫy")
    for case in character_config["edge_cases"]:
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

profile_path = profile_path_for(st.session_state.character_id)
chunks_path = knowledge_path_for(st.session_state.character_id)
profile, chunks, retriever = get_runtime(
    st.session_state.character_id,
    profile_path.stat().st_mtime,
    chunks_path.stat().st_mtime,
)

left, right = st.columns([0.72, 0.28], gap="large")

with right:
    sprite = get_sprite_path(st.session_state.character_id, st.session_state.sprite_state)
    if sprite:
        st.image(str(sprite), width="stretch")
    else:
        st.markdown(
            f'<div class="neutral-portrait">{html.escape(profile["character_metadata"]["name"]).upper()}<br/>SIMULACRA</div>',
            unsafe_allow_html=True,
        )
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
    st.markdown('<div class="qt-title">Đối thoại lịch sử với nhân vật</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qt-subtitle">Nhân vật trả lời nhập vai; phần đối chiếu học thuật nằm riêng bên dưới.</div>',
        unsafe_allow_html=True,
    )

    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if message.get("audio_base64"):
                    render_audio_player(
                        message["audio_base64"],
                        f"assistant-{message_index}",
                        autoplay=message.get("autoplay_audio", False),
                    )
                    message["autoplay_audio"] = False
                elif message.get("tts_message"):
                    safe_tts_message = html.escape(message["tts_message"])
                    st.markdown(f'<div class="tts-status">{safe_tts_message}</div>', unsafe_allow_html=True)
                mode = message.get("mode")
                render_citations(message.get("citations", []))
                render_verification_status(mode)

    submitted_query = st.chat_input(f"Hỏi {profile['character_metadata']['name']} về thân thế, sự nghiệp, tư tưởng...")
    query = st.session_state.pending_query or submitted_query
    st.session_state.pending_query = ""

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        generator = (
            lambda question, active_profile, active_citations: generate_character_answer(
                question,
                active_profile,
                active_citations,
            )
        ) if is_configured() else None
        result = answer_query(query, profile, retriever, generator=generator)
        tts_result = synthesize(result["answer"], st.session_state.character_id)
        st.session_state.sprite_state = result["state"]
        st.session_state.last_answer = result["answer"]
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "citations": result["citations"],
                "mode": result.get("mode", "retrieval"),
                "audio_base64": tts_result.audio_base64,
                "tts_message": tts_result.message,
                "tts_ok": tts_result.ok,
                "autoplay_audio": tts_result.ok,
            }
        )
        st.rerun()
