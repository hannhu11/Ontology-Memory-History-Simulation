from dataclasses import dataclass
from pathlib import Path


@dataclass
class TTSResult:
    audio_path: Path | None
    message: str


def synthesize(text: str, character_id: str) -> TTSResult:
    """Placeholder TTS provider.

    The app calls this function from the UI, so a real provider can be added later
    without changing the Streamlit screen. For now it deliberately returns no
    audio instead of faking speech.
    """
    _ = text
    _ = character_id
    return TTSResult(
        audio_path=None,
        message=(
            "TTS chưa được cấu hình API key/provider. Hook đã sẵn sàng trong "
            "tts_provider.py để nối ElevenLabs, OpenAI TTS hoặc dịch vụ nội bộ."
        ),
    )
