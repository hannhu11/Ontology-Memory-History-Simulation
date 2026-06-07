import html
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass


GOOGLE_TTS_ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"
GOOGLE_TTS_VOICE_NAME = "vi-VN-Neural2-D"
GOOGLE_TTS_LANGUAGE_CODE = "vi-VN"
GOOGLE_TTS_GENDER = "MALE"
GOOGLE_TTS_AUDIO_ENCODING = "MP3"
DEFAULT_VOICE_PROFILE = "quang_trung"
VOICE_PROFILES = {
    "quang_trung": {"pitch": "-6st", "rate": "0.95", "label": "Chiến tướng uy dũng"},
    "tran_hung_dao": {"pitch": "-8st", "rate": "0.85", "label": "Quốc công Tiết chế"},
    "nguyen_trai": {"pitch": "-2st", "rate": "0.95", "label": "Ức Trai văn thần"},
    "ho_chi_minh": {"pitch": "+1.5st", "rate": "0.85", "label": "Ấm áp, gần gũi"},
    "vo_nguyen_giap": {"pitch": "-4st", "rate": "0.90", "label": "Đại tướng điềm tĩnh"},
}
GOOGLE_TTS_SSML_PITCH = VOICE_PROFILES[DEFAULT_VOICE_PROFILE]["pitch"]
GOOGLE_TTS_SSML_RATE = VOICE_PROFILES[DEFAULT_VOICE_PROFILE]["rate"]
DEFAULT_TTS_TIMEOUT_SECONDS = 18.0


@dataclass
class TTSResult:
    audio_base64: str | None
    message: str
    ok: bool = False
    mime_type: str = "audio/mpeg"


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, character_id: str) -> TTSResult:
        raise NotImplementedError


def is_configured() -> bool:
    return bool(os.getenv("GOOGLE_TTS_API_KEY"))


def request_timeout_seconds() -> float:
    raw_value = os.getenv("GOOGLE_TTS_TIMEOUT_SECONDS", str(DEFAULT_TTS_TIMEOUT_SECONDS)).strip()
    try:
        return max(5.0, float(raw_value))
    except ValueError:
        return DEFAULT_TTS_TIMEOUT_SECONDS


def voice_profile_for(character_id: str) -> dict:
    return VOICE_PROFILES.get(character_id, VOICE_PROFILES[DEFAULT_VOICE_PROFILE])


def build_ssml(text: str, character_id: str = DEFAULT_VOICE_PROFILE) -> str:
    voice_profile = voice_profile_for(character_id)
    escaped_text = html.escape(text.strip(), quote=False)
    return (
        f'<speak><prosody pitch="{voice_profile["pitch"]}" rate="{voice_profile["rate"]}">'
        f'<emphasis level="strong">{escaped_text}</emphasis>'
        "</prosody></speak>"
    )


def build_tts_payload(text: str, character_id: str = DEFAULT_VOICE_PROFILE) -> dict:
    return {
        "input": {"ssml": build_ssml(text, character_id)},
        "voice": {
            "languageCode": GOOGLE_TTS_LANGUAGE_CODE,
            "name": GOOGLE_TTS_VOICE_NAME,
            "ssmlGender": GOOGLE_TTS_GENDER,
        },
        "audioConfig": {"audioEncoding": GOOGLE_TTS_AUDIO_ENCODING},
    }


class GoogleCloudTTSProvider(TTSProvider):
    def synthesize(self, text: str, character_id: str) -> TTSResult:
        cleaned_text = text.strip()
        if not cleaned_text:
            return TTSResult(audio_base64=None, message="Chưa có nội dung để tạo âm thanh.")

        api_key = os.getenv("GOOGLE_TTS_API_KEY")
        if not api_key:
            return TTSResult(audio_base64=None, message="Âm thanh chưa được cấu hình.")

        try:
            response = requests.post(
                GOOGLE_TTS_ENDPOINT,
                params={"key": api_key},
                json=build_tts_payload(cleaned_text, character_id),
                timeout=request_timeout_seconds(),
            )
        except requests.RequestException:
            return TTSResult(audio_base64=None, message="Âm thanh chưa tạo được trong lượt này.")

        if response.status_code != 200:
            return TTSResult(
                audio_base64=None,
                message="Âm thanh chưa tạo được trong lượt này.",
            )

        try:
            payload = response.json()
        except ValueError:
            return TTSResult(audio_base64=None, message="Âm thanh trả về không hợp lệ.")

        audio_base64 = payload.get("audioContent")
        if not audio_base64:
            return TTSResult(audio_base64=None, message="Âm thanh trả về không hợp lệ.")

        return TTSResult(audio_base64=audio_base64, message="Đã tạo âm thanh.", ok=True)


def get_tts_provider() -> TTSProvider:
    return GoogleCloudTTSProvider()


def synthesize(text: str, character_id: str) -> TTSResult:
    return get_tts_provider().synthesize(text, character_id)
