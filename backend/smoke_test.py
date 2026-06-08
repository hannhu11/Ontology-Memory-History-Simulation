from __future__ import annotations

import json
import os
from pathlib import Path

os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_TTS_API_KEY"] = ""

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
        assert "tên của ta" in quang_trung["answer"]
        assert "không phải" in quang_trung["answer"]
        assert "gươm giáo chỉ là bước mở đường" not in quang_trung["answer"]

        name_relation = final_answer_for(client, "quang_trung", "ông với nguyễn huệ là gì của nhau")
        assert "tên của ta" in name_relation["answer"]
        assert "không phải" in name_relation["answer"]
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

        giap = final_answer_for(client, "vo_nguyen_giap", "tư tưởng đánh giặc của bác giáp là gì vậy")
        assert "Võ Nguyên Giáp" not in giap["answer"]
        assert "Tôi" in giap["answer"] or "tôi" in giap["answer"]

        tts = client.post("/api/tts", json={"character_id": "ho_chi_minh", "text": "Bác chào các cháu."})
        assert tts.status_code == 200
        assert tts.json()["ok"] is False

    print("backend smoke tests passed")


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    main()
