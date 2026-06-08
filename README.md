# Ontology Memory History Simulation

Repo backup code và dataset cho prototype RAG mô phỏng đối thoại lịch sử. Production hiện đã chuyển khỏi Streamlit sang kiến trúc tách rời: Next.js frontend + FastAPI backend + runtime RAG preload cho 5 nhân vật.

## Nội dung chính

- `quang_trung_dataset/`: script build/validate dataset Quang Trung, script chuẩn hóa multi-character, `MEMORY.md`.
- `backend/`: FastAPI API, preload profile/chunks/retriever cho 5 nhân vật, SSE chat stream và TTS endpoint riêng.
- `frontend/`: Next.js App Router, TypeScript, Zustand state, UI Neo Kinpaku và SSE client.
- `quang_trung_web/`: legacy Streamlit rollback, registry 5 nhân vật, RAG core, Gemini provider, TTS provider, smoke tests và assets dùng chung.
- `quang_trung_dataset/MEMORY.md`: nhật ký trạng thái bắt buộc đọc trước khi tiếp tục phát triển hoặc mở chat mới.
- `ho_chi_minh_dataset/`: 150 chunks.
- `tran_hung_dao_dataset/`: 125 chunks.
- `nguyen_trai_dataset/`: 50 chunks.
- `vo_nguyen_giap_dataset/`: 115 chunks.

## Chạy local production stack

```powershell
cd quang_trung_web
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r ..\backend\requirements.txt
Copy-Item .env.example .env
notepad .env

cd ..
.\quang_trung_web\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8601
```

Mở terminal khác:

```powershell
cd frontend
npm install
$env:HISTORY_API_URL="http://127.0.0.1:8601"
npm run dev -- --hostname 127.0.0.1 --port 8501
```

Điền API key trong `quang_trung_web/.env` local nếu cần gọi Gemini hoặc âm thanh thật. Không commit `.env`.

## Chạy legacy Streamlit rollback

```powershell
cd quang_trung_web
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Biến cần thiết: `GEMINI_API_KEY`, `GOOGLE_TTS_API_KEY`, `GOOGLE_TTS_TIMEOUT_SECONDS`, `LLM_TIMEOUT_SECONDS`, `RAG_SCORE_THRESHOLD`, `RAG_TOP_K`, `RAG_EMBEDDING_MODEL`, `RAG_INDEX_DIR`.

## Kiến trúc hiện tại

- Next.js render khung nhập ngay, quản lý chọn nhân vật bằng Zustand và reset chat/citation/audio trong một transaction khi đổi `character_id`.
- FastAPI expose `GET /api/characters`, `POST /api/chat/stream`, `POST /api/tts`, `GET /api/health`.
- `POST /api/chat/stream` trả SSE theo thứ tự `start -> retrieval -> token* -> final`; chữ hiện trước, audio gọi sau bằng `/api/tts`.
- SSE hiện có thêm `stream_start` và `visual` payload để frontend điều khiển asset nhập vai theo câu hỏi/câu trả lời: `thinking` khi đang gợi ký ức, `attack` cho câu chiến trận/xung trận, và portrait cảm xúc `idle/talking/happy/angry/sad/confused`.
- `character_registry.py` là nguồn cấu hình duy nhất cho dataset path, asset path và edge-case buttons.
- `rag_core.py` nạp profile/chunks theo `character_id`, tạo index riêng `.rag_index/<character_id>` và dùng guardrail theo `death_year`.
- Quang Trung có query rewriting cho `vua`, `ngài`, `ông`, `ta`; câu “trận hãnh diện/đáng nhớ” được route về Ngọc Hồi - Đống Đa và Rạch Gầm - Xoài Mút.
- Smalltalk gate chỉ áp dụng cho chào hỏi thuần túy. Câu có tiền tố `chào`, `cho tôi biết` nhưng chứa trận đánh, tư tưởng, tên riêng hoặc địa danh lịch sử vẫn phải đi qua hybrid RAG, tránh fallback `Ta đang nghe...`.
- Câu nhầm tên Quang Trung/Nguyễn Huệ được xử lý như identity-confusion: Nguyễn Huệ là tên người, Quang Trung là niên hiệu, không phải hai nhân vật hay anh em.
- Các nhân vật mới dùng cùng runtime, có intent `ideology`, `military_doctrine`, `life_milestone` để tránh trả lời tiểu sử khi người dùng hỏi tư tưởng/chiến lược.
- Citation có `source_tier` và `source_quality_score`; retriever ưu tiên nguồn chính thống, đúng intent, đúng nhân vật và khử trùng lặp.
- Fallback nội bộ bảo toàn Simulacra: nhân vật không nói như bot đọc dataset; UI citation là phần học thuật riêng.
- Câu sau năm mất bị xử lý theo vai. Riêng Hồ Chí Minh với các câu di sản sau 1969 như 1975 trả theo dạng “sau khi Bác đã đi xa, sử sách đời sau ghi...”.
- TTS chạy sau `final`, không ghi MP3 ra ổ đĩa và không lộ model/provider trên giao diện.
- Quang Trung dùng bộ asset 1254x1254 trong `quang_trung_web/assets/quang_trung/` và 2 sprite sheet `Quang Trung-hero_thinking.png`, `Quang Trung-attack.png`. Frontend render trong `CharacterViewer`, không scale ảnh làm vỡ layout; right rail dùng sticky container để asset đi cùng khi người dùng cuộn hội thoại.
- Audio của tin nhắn cũ không điều khiển asset hiện tại. Nếu `attack` đang chạy, audio không hủy motion; sprite kết thúc rồi mới chuyển sang lip-sync/talking.

## Voice Matrix

Provider hiện tại không có voice `vi-VN` theo miền Trung/Bình Định/Nghệ An. App mô phỏng khác biệt giọng bằng SSML ở backend:

- `quang_trung`: `pitch="-6st"`, `rate="0.95"`.
- `tran_hung_dao`: `pitch="-8st"`, `rate="0.85"`.
- `nguyen_trai`: `pitch="-2st"`, `rate="0.95"`.
- `ho_chi_minh`: `pitch="+1.5st"`, `rate="0.85"`.
- `vo_nguyen_giap`: `pitch="-4st"`, `rate="0.90"`.

## Build Dataset

```powershell
python .\quang_trung_dataset\build_dataset.py
python .\quang_trung_dataset\build_multi_character_datasets.py
```

`build_multi_character_datasets.py` đọc source `DATASET-Ontology-Memory-History-Simulation-main` khi có trong workspace local. Repo backup đã chứa output chuẩn hóa nên không cần source folder để chạy web.

## Kiểm thử

```powershell
python .\quang_trung_dataset\validate_dataset.py
python .\quang_trung_dataset\validate_multi_character.py
python -m py_compile .\quang_trung_web\app.py .\quang_trung_web\rag_core.py .\quang_trung_web\llm_provider.py .\quang_trung_web\tts_provider.py .\quang_trung_web\smoke_test.py .\quang_trung_web\character_registry.py
python -m py_compile .\backend\main.py .\backend\smoke_test.py
python .\backend\smoke_test.py
cd quang_trung_web
.\.venv\Scripts\python.exe .\smoke_test.py
cd ..\frontend
npm install
npm run build
```

Smoke test kiểm tra đủ 5 nhân vật, positive/negative cases, Quang Trung battle reflection, visual payload cho asset state machine, Võ Nguyên Giáp Điện Biên Phủ, HCM legacy-afterlife, persona không tự gọi tên mình, citation source-tier và TTS SSML.
Regression mới bắt buộc:

- `chao vua, vua hay cho toi biet ve tran danh ngoc hoi , dong da di` không được trả `Ta đang nghe`, phải route về Ngọc Hồi - Đống Đa và motion `attack`.
- `ông với nguyễn huệ là gì của nhau` phải trả identity-confusion đúng, không rơi về câu đại cục chung chung.

## Production

Production chạy tại `https://history-simulation-ai.online/` trên VPS Oracle dùng chung với PetHub. Không mở public port `8501`; Next.js nghe nội bộ `172.19.0.1:8501`, FastAPI nghe `127.0.0.1:8601`, Nginx container của PetHub reverse proxy theo `server_name`.

Deploy bản mới:

```bash
cd /home/ubuntu/history-ontology
git pull
/home/ubuntu/history-ontology/quang_trung_web/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend && npm ci && npm run build
sudo cp ../deploy/systemd/history-ontology-api.service /etc/systemd/system/
sudo cp ../deploy/systemd/history-ontology-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now history-ontology-api.service
curl -fsS http://127.0.0.1:8601/api/health
sudo systemctl stop history-ontology.service
sudo systemctl enable --now history-ontology-web.service
curl -I http://172.19.0.1:8501
```

Rollback nhanh nếu Next/FastAPI lỗi:

```bash
sudo systemctl stop history-ontology-web.service history-ontology-api.service
sudo systemctl start history-ontology.service
```

Không sửa Nginx/PetHub nếu chỉ deploy code app. Không in/cat `.env` production.

## Bảo mật

Repo này không lưu API key, token, `.env`, virtualenv, ChromaDB index, cache model, log hoặc file nén backup mới. Chỉ `.env.example` được commit để mô tả tên biến môi trường.
