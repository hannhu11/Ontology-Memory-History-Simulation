from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_TTS_API_KEY"] = ""
os.environ["LLM_PROVIDER"] = "gemini_api"

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


def parse_sse(text: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        event_name = ""
        data = {}
        for line in block.splitlines():
            if line.startswith("event:"):
                event_name = line[6:].strip()
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
        if event_name:
            events.append((event_name, data))
    return events


def final_answer_for(client: TestClient, character_id: str, message: str) -> dict:
    response = client.post(
        "/api/chat/stream",
        json={"character_id": character_id, "message": message, "history": []},
    )
    assert response.status_code == 200
    events = parse_sse(response.text)
    names = [name for name, _ in events]
    assert names[0] == "start"
    assert "retrieval" in names
    assert "stream_start" in names
    assert "final" in names
    final = [data for name, data in events if name == "final"][-1]
    assert "visual" in final
    assert "llm_status" in final
    assert "fallback_used" in final
    assert "route_source" in final
    assert "timings_ms" in final
    assert "total_ms" in final["timings_ms"]
    assert final["visual"]["emotion"] in {"idle", "thinking", "talking", "happy", "angry", "sad", "confused"}
    return final


def main() -> None:
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        payload = health.json()
        assert payload["ok"] is True
        assert len(payload["characters_loaded"]) == 5

        characters = client.get("/api/characters").json()["characters"]
        assert len(characters) == 5
        assert {item["character_id"] for item in characters} >= {
            "quang_trung",
            "tran_hung_dao",
            "nguyen_trai",
            "ho_chi_minh",
            "vo_nguyen_giap",
        }

        quang_trung = final_answer_for(client, "quang_trung", "ông với Nguyễn Huệ là anh em à")
        assert "Nguyễn Huệ chính là" in quang_trung["answer"]
        assert "không phải" in quang_trung["answer"]
        assert "gươm giáo chỉ là bước mở đường" not in quang_trung["answer"]

        name_relation = final_answer_for(client, "quang_trung", "ông với nguyễn huệ là gì của nhau")
        assert "Nguyễn Huệ chính là" in name_relation["answer"]
        assert "niên hiệu" in name_relation["answer"]
        assert name_relation["visual"]["intent"] == "identity_confusion"

        ngoc_hoi = final_answer_for(
            client,
            "quang_trung",
            "chao vua, vua hay cho toi biet ve tran danh ngoc hoi , dong da di",
        )
        normalized_ngoc_hoi = ngoc_hoi["answer"].lower()
        assert "ta đang nghe" not in normalized_ngoc_hoi
        assert "ngọc hồi" in normalized_ngoc_hoi or "đống đa" in normalized_ngoc_hoi
        assert len(ngoc_hoi["answer"].split()) >= 80
        assert ngoc_hoi["visual"]["motion"] == "attack"

        battle = final_answer_for(client, "quang_trung", "vua kể trận đánh khiến vua hãnh diện nhất đi")
        assert battle["visual"]["motion"] == "attack"
        assert battle["visual"]["emotion"] in {"happy", "angry"}
        assert len(battle["answer"].split()) >= 80

        bac = final_answer_for(client, "ho_chi_minh", "BÁC CÓ VỢ KHÔNG, cho cháu biết đi")
        assert "Chuyện riêng tư" in bac["answer"]
        assert "Việc gì có lợi cho dân" not in bac["answer"]

        hcm_birth = final_answer_for(client, "ho_chi_minh", "bac sinh nam bao nhieu")
        assert "19/5/1890" in hcm_birth["answer"]
        assert "5/6/1911" not in hcm_birth["answer"]
        assert hcm_birth["mode"] == "factual"
        assert hcm_birth["route_source"] == "deterministic"
        assert hcm_birth["llm_status"] == "not_configured"
        assert hcm_birth["visual"]["intent"] == "identity"

        thd_birth = final_answer_for(client, "tran_hung_dao", "đại vương sinh năm bao nhiêu")
        assert "1228" in thd_birth["answer"]
        assert thd_birth["mode"] == "factual"

        nt_birth = final_answer_for(client, "nguyen_trai", "tiên sinh sinh năm bao nhiêu")
        assert "1380" in nt_birth["answer"]
        assert nt_birth["mode"] == "factual"

        giap_birth = final_answer_for(client, "vo_nguyen_giap", "đại tướng sinh năm bao nhiêu")
        assert "1911" in giap_birth["answer"]
        assert "Lộc Thủy" in giap_birth["answer"]
        assert giap_birth["mode"] == "factual"

        giap = final_answer_for(client, "vo_nguyen_giap", "tư tưởng đánh giặc của bác giáp là gì vậy")
        assert "Võ Nguyên Giáp" not in giap["answer"]
        assert "Tôi" in giap["answer"] or "tôi" in giap["answer"]

        dien_bien_phu = final_answer_for(client, "vo_nguyen_giap", "chiến dịch điện biên phủ vì sao thắng")
        lowered_dien_bien = dien_bien_phu["answer"].lower()
        assert "điện biên phủ" in lowered_dien_bien
        assert "1954" in dien_bien_phu["answer"] or "đánh chắc" in lowered_dien_bien
        assert "trên không" not in lowered_dien_bien

        os.environ["GEMINI_API_KEY"] = "fake-key"
        old_fast_local = os.environ.get("FAST_LOCAL_RETRIEVAL")
        os.environ["FAST_LOCAL_RETRIEVAL"] = "0"
        try:
            with patch("main.route_query_json", return_value={"ok": False, "llm_status": "quota_exhausted", "route": None}):
                quota = final_answer_for(client, "vo_nguyen_giap", "chiến dịch điện biên phủ vì sao thắng")
        finally:
            os.environ["GEMINI_API_KEY"] = ""
            if old_fast_local is None:
                os.environ.pop("FAST_LOCAL_RETRIEVAL", None)
            else:
                os.environ["FAST_LOCAL_RETRIEVAL"] = old_fast_local
        assert quota["llm_status"] == "quota_exhausted"
        assert quota["fallback_used"] is True
        assert "Điện Biên Phủ" in quota["answer"]

        tts = client.post("/api/tts", json={"character_id": "ho_chi_minh", "text": "Bác chào các cháu."})
        assert tts.status_code == 200
        assert tts.json()["ok"] is False

    print("backend smoke tests passed")


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    main()
