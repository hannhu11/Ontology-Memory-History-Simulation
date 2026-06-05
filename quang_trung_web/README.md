# Bản mẫu RAG Quang Trung

Ứng dụng Streamlit để thử nghiệm đối thoại với nhân vật lịch sử dựa trên dataset Quang Trung / Nguyễn Huệ.

## Chạy local

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Ứng dụng mặc định đọc dữ liệu từ `..\quang_trung_dataset`. Lần chạy đầu tiên sẽ tạo chỉ mục vector tại `.rag_index\quang_trung`.

## Gọi API AI

Nếu chưa có key, ứng dụng dùng bộ trả lời nội bộ để demo truy xuất nguồn và guardrail.
Khi cần câu trả lời tự nhiên hơn, tạo file `.env` từ `.env.example`:

```powershell
Copy-Item .env.example .env
notepad .env
python -m streamlit run app.py
```

Các biến chính:

- `LLM_PROVIDER=groq`, `gemini`, hoặc `auto`.
- `GROQ_MODEL=llama-3.3-70b-versatile`.
- `GEMINI_MODEL=gemini-2.5-flash`.
- `RAG_SCORE_THRESHOLD=0.42` để chặn truy xuất rác khi câu hỏi không đủ liên quan.
- `RAG_TOP_K=4` để đổi số tư liệu đối chiếu tối đa.
- `RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `RAG_INDEX_DIR=.rag_index\quang_trung`.

Groq phù hợp khi cần tốc độ phản hồi nhanh. Gemini thường diễn đạt tiếng Việt tự nhiên hơn; có thể đổi nhà cung cấp ngay trong sidebar của app.

## Files

- `app.py`: giao diện Streamlit, hội thoại, nguồn truy xuất, trạng thái nhân vật, nút giọng nói.
- `rag_core.py`: nạp JSON/JSONL, truy xuất ChromaDB + sentence-transformers có score threshold, fallback lexical và guardrail câu hỏi ngoài thời đại.
- `llm_provider.py`: lớp gọi Groq hoặc Gemini khi có key.
- `tts_provider.py`: điểm nối để thay bằng nhà cung cấp giọng nói thật.
- `smoke_test.py`: kiểm thử nhanh truy xuất và guardrail.
