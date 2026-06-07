# Ontology Memory History Simulation

Repo backup code và dataset cho prototype RAG mô phỏng đối thoại lịch sử. Bản hiện tại đã mở rộng từ Quang Trung-only sang 5 nhân vật lịch sử, có multi-character Hybrid RAG, Gemini-only generator, streaming text và âm thanh nhập vai chạy nền.

## Nội dung chính

- `quang_trung_dataset/`: script build/validate dataset Quang Trung, script chuẩn hóa multi-character, `MEMORY.md`.
- `quang_trung_web/`: app Streamlit, registry 5 nhân vật, RAG core, Gemini provider, Google TTS provider, smoke tests và assets.
- `quang_trung_dataset/MEMORY.md`: nhật ký trạng thái bắt buộc đọc trước khi tiếp tục phát triển hoặc mở chat mới.
- `ho_chi_minh_dataset/`: 150 chunks.
- `tran_hung_dao_dataset/`: 125 chunks.
- `nguyen_trai_dataset/`: 50 chunks.
- `vo_nguyen_giap_dataset/`: 115 chunks.

## Chạy local

```powershell
cd quang_trung_web
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Điền API key trong `.env` local nếu cần gọi Gemini hoặc Google Cloud TTS thật. Không commit `.env`.

Biến cần thiết trong `.env` local: `GEMINI_API_KEY`, `GOOGLE_TTS_API_KEY`, `GOOGLE_TTS_TIMEOUT_SECONDS`.

## Kiến trúc hiện tại

- `character_registry.py` là nguồn cấu hình duy nhất cho UI, dataset path, asset path, edge-case buttons và voice label.
- `rag_core.py` nạp profile/chunks theo `character_id`, tạo index riêng `.rag_index/<character_id>` và dùng guardrail theo `death_year`.
- Quang Trung có query rewriting cho `vua`, `ngài`, `ông`, `ta`; câu “trận hãnh diện/đáng nhớ” được route về Ngọc Hồi - Đống Đa và Rạch Gầm - Xoài Mút.
- Các nhân vật mới dùng cùng runtime, có intent `ideology`, `military_doctrine`, `life_milestone` để tránh trả lời tiểu sử khi người dùng hỏi tư tưởng/chiến lược.
- Citation có `source_tier` và `source_quality_score`; retriever ưu tiên nguồn chính thống, đúng intent, đúng nhân vật và khử trùng lặp.
- Fallback nội bộ bảo toàn Simulacra: nhân vật không nói như bot đọc dataset; UI citation là phần học thuật riêng.
- Câu sau năm mất bị xử lý theo vai. Riêng Hồ Chí Minh với các câu di sản sau 1969 như 1975 trả theo dạng “sau khi Bác đã đi xa, sử sách đời sau ghi...”.
- UI hiển thị câu hỏi ngay, stream text trước, rồi âm thanh nhập vai được tạo bằng job nền để không block câu trả lời.
- TTS dùng provider backend qua SSML, không ghi MP3 ra ổ đĩa và không lộ model/provider trên giao diện.

## Voice Matrix

Provider hiện tại không có voice `vi-VN` theo miền Trung/Bình Định/Nghệ An. App mô phỏng khác biệt giọng bằng SSML:

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
cd quang_trung_web
.\.venv\Scripts\python.exe .\smoke_test.py
```

Smoke test kiểm tra đủ 5 nhân vật, positive/negative cases, Quang Trung battle reflection, Võ Nguyên Giáp Điện Biên Phủ, HCM legacy-afterlife, persona không tự gọi tên mình, citation source-tier và TTS SSML.

## Production

Production đang chạy tại `https://history-simulation-ai.online/` trên VPS Oracle dùng chung với PetHub. Không mở public port `8501`; app Streamlit chạy nội bộ và được Nginx container của PetHub reverse proxy theo `server_name`.

Deploy bản mới:

```bash
cd /home/ubuntu/history-ontology
git pull
sudo systemctl restart history-ontology.service
sudo systemctl status history-ontology.service --no-pager
```

Không sửa Nginx/PetHub nếu chỉ deploy code app. Không in/cat `.env` production.

## Bảo mật

Repo này không lưu API key, token, `.env`, virtualenv, ChromaDB index, cache model, log hoặc file nén backup mới. Chỉ `.env.example` được commit để mô tả tên biến môi trường.
