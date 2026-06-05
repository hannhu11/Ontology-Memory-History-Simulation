# Ontology Memory History Simulation

Repo backup code và dataset cho prototype RAG mô phỏng đối thoại lịch sử, hiện tập trung vào nhân vật Vua Quang Trung / Nguyễn Huệ.

## Nội dung chính

- `quang_trung_dataset/`: script build dataset, validator, profile nhân vật và `quang_trung_knowledge.jsonl` đã mở rộng lên 100 chunk.
- `quang_trung_web/`: app Streamlit, RAG core dùng ChromaDB + sentence-transformers, Hybrid Simulacra RAG, Gemini-only provider, Google TTS SSML, smoke tests và asset UI.
- `quang_trung_dataset/MEMORY.md`: nhật ký trạng thái bắt buộc đọc trước khi tiếp tục phát triển hoặc mở chat mới.

## Chạy local

```powershell
cd quang_trung_web
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Điền API key trong `.env` local nếu cần gọi Gemini hoặc Google Cloud TTS thật. Không commit `.env`.

Biến cần thiết:

```powershell
GEMINI_API_KEY=
GOOGLE_TTS_API_KEY=
GOOGLE_TTS_TIMEOUT_SECONDS=18
```

## Kiến trúc hiện tại

- RAG đã có query rewriting cho đại từ mơ hồ như `vua`, `ngài`, `ông`, `ta`, ánh xạ về Quang Trung / Nguyễn Huệ / Tây Sơn trước khi truy xuất.
- Intent `battle_reflection` xử lý câu hỏi tự nhiên kiểu “vua nói qua về một trận đánh hãnh diện nhất”, ưu tiên Ngọc Hồi - Đống Đa và Rạch Gầm - Xoài Mút.
- Retriever chạy hybrid deterministic trên original query, rewritten query và canonical variants, rồi fuse/rerank theo intent, chất lượng nguồn và tag lịch sử.
- Fallback nội bộ giữ vai quân vương cho câu trong thời đại, nhưng guardrail vẫn chặn nghiêm các câu sau năm 1792 hoặc claim sai mốc.
- TTS dùng Google Cloud `vi-VN-Neural2-D` qua SSML `<prosody pitch="-7st" rate="0.90">` để mô phỏng giọng trầm, uy nghi hơn. Google Cloud hiện không có nhãn giọng miền Trung/Bình Định riêng cho `vi-VN`.

## Build và kiểm thử

```powershell
python .\quang_trung_dataset\build_dataset.py
python .\quang_trung_dataset\validate_dataset.py
.\quang_trung_web\.venv\Scripts\python.exe -m py_compile .\quang_trung_web\app.py .\quang_trung_web\rag_core.py .\quang_trung_web\llm_provider.py .\quang_trung_web\tts_provider.py .\quang_trung_web\smoke_test.py
cd quang_trung_web
.\.venv\Scripts\python.exe .\smoke_test.py
```

`.rag_index/quang_trung` là cache local, tự rebuild khi JSONL đổi và không được push.

## Bảo mật

Repo này không lưu API key, token, `.env`, virtualenv, ChromaDB index, cache model, log hoặc file nén backup. Chỉ `.env.example` được commit để mô tả tên biến môi trường.
