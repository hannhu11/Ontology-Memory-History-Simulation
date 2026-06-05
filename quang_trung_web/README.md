# Bản mẫu RAG Quang Trung

Ứng dụng Streamlit để thử nghiệm đối thoại với nhân vật lịch sử dựa trên dataset Quang Trung / Nguyễn Huệ.

## Chạy local

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Ứng dụng mặc định đọc dữ liệu từ `..\quang_trung_dataset`. Lần chạy đầu tiên sẽ tạo chỉ mục vector tại `.rag_index\quang_trung`.

## Hybrid Simulacra RAG

Luồng truy xuất không chỉ lấy top-K vector thô. `rag_core.py` có lớp Query Rewriting để hiểu các đại từ tự nhiên như `vua`, `ngài`, `ông`, `ta` là Quang Trung / Nguyễn Huệ / Tây Sơn. Các câu hỏi kiểu "vua nói qua về một trận đánh hãnh diện nhất" được gắn intent `battle_reflection` và mở rộng sang các ký ức chiến trận cốt lõi như Ngọc Hồi - Đống Đa và Rạch Gầm - Xoài Mút.

Retriever chạy hybrid deterministic: original query, rewritten query và canonical query variants được truy xuất rồi fuse/rerank theo intent, source quality và tag lịch sử. Vì vậy câu hỏi về trận đánh sẽ không lấy nhầm citation tiền tệ, sĩ phu hoặc ngoại giao.

Fallback nội bộ ưu tiên bảo toàn Simulacra: nếu câu hỏi còn rộng nhưng vẫn thuộc đời Quang Trung, nhân vật trả lời bằng đại cục lịch sử nhập vai thay vì nói như bot kiểm chứng. Guardrail vẫn chặn nghiêm các câu ngoài thời đại, truyền thuyết hoặc claim sai mốc.

## Gọi API AI

Nếu chưa có key, ứng dụng dùng bộ trả lời nội bộ để demo truy xuất nguồn và guardrail.
Khi cần câu trả lời tự nhiên hơn, tạo file `.env` từ `.env.example` và điền `GEMINI_API_KEY`:

```powershell
Copy-Item .env.example .env
notepad .env
python -m streamlit run app.py
```

Các biến chính:

- `GEMINI_API_KEY=` để gọi Gemini API.
- `LLM_TIMEOUT_SECONDS=18` để đổi timeout gọi Gemini.
- `RAG_SCORE_THRESHOLD=0.42` để chặn truy xuất rác khi câu hỏi không đủ liên quan.
- `RAG_TOP_K=4` để đổi số tư liệu đối chiếu tối đa.
- `RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `RAG_INDEX_DIR=.rag_index\quang_trung`.

Provider LLM hiện được tinh gọn về một đường duy nhất: Gemini với model cố định `gemini-3.5-flash`. Sidebar không hiển thị lựa chọn model để giữ trải nghiệm nhập vai liền mạch; người dùng chỉ thấy nhân vật và phần kiểm chứng học thuật.

## Google Cloud Text-to-Speech

Giọng đọc dùng REST API của Google Cloud Text-to-Speech, không dùng Service Account JSON và không ghi file MP3 xuống ổ đĩa. Audio được giữ dạng base64 trong session message và phát ngay dưới câu trả lời của nhân vật.

Thêm các biến sau vào `.env` local:

```powershell
GOOGLE_TTS_API_KEY=
GOOGLE_TTS_TIMEOUT_SECONDS=18
```

Provider cố định giọng `vi-VN-Neural2-D`, `languageCode=vi-VN`, `ssmlGender=MALE`, `audioEncoding=MP3`. Không có giọng miền Trung/Bình Định riêng trong voice list của Google Cloud TTS, nên app mô phỏng chất giọng trầm uy nghi bằng SSML: `<prosody pitch="-7st" rate="0.90"><emphasis level="strong">...</emphasis></prosody>`. Nếu trình duyệt chặn autoplay, thanh phát vẫn hiện nút `Phát` để nghe thủ công.

Không commit `.env` hoặc bất kỳ file nào chứa API key. Chỉ `.env.example` được đưa lên Git.

## Files

- `app.py`: giao diện Streamlit, hội thoại, nguồn truy xuất, trạng thái nhân vật, nút giọng nói.
- `rag_core.py`: nạp JSON/JSONL, hybrid RAG với ChromaDB + sentence-transformers, query rewriting, intent routing, fallback lexical, simulation fallback và guardrail câu hỏi ngoài thời đại.
- `llm_provider.py`: lớp gọi Gemini-only khi có `GEMINI_API_KEY`.
- `tts_provider.py`: lớp gọi Google Cloud Text-to-Speech REST API, trả audio base64 trong bộ nhớ.
- `smoke_test.py`: kiểm thử nhanh truy xuất và guardrail.
