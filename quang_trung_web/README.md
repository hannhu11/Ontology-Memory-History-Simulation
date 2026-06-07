# Multi-Character History Simulation Web

Ứng dụng Streamlit cho prototype `Ontology-Memory-History-Simulation`: đối thoại nhập vai với 5 nhân vật lịch sử, có RAG đối chiếu tư liệu, guardrail sai thời đại, streaming text và âm thanh nhập vai chạy nền.

## Nhân vật hiện có

- Quang Trung / Nguyễn Huệ: `quang_trung_dataset`
- Hồ Chí Minh: `ho_chi_minh_dataset`
- Nguyễn Trãi: `nguyen_trai_dataset`
- Trần Hưng Đạo: `tran_hung_dao_dataset`
- Võ Nguyên Giáp: `vo_nguyen_giap_dataset`

`character_registry.py` là nguồn cấu hình duy nhất cho UI, dataset path, asset path, edge-case buttons và voice label.

## Chạy local

```powershell
cd quang_trung_web
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Không commit `.env`. Các biến chính:

- `GEMINI_API_KEY` để gọi Gemini API.
- `GOOGLE_TTS_API_KEY` để gọi Google Cloud Text-to-Speech.
- `GOOGLE_TTS_TIMEOUT_SECONDS` mặc định nên đặt `18`.
- `RAG_SCORE_THRESHOLD` mặc định nên đặt `0.42`.
- `RAG_TOP_K` mặc định nên đặt `4`.
- `RAG_EMBEDDING_MODEL` mặc định nên đặt `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `RAG_INDEX_DIR` mặc định nên đặt `.rag_index`.

Chỉ mục vector được tách theo nhân vật tại `.rag_index\<character_id>` và tự rebuild khi JSONL đổi.

## Multi-Character RAG

`rag_core.py` không còn hardcode Quang Trung. Loader nhận `character_id`, tự nạp `<character_id>_profile.json` và `<character_id>_knowledge.jsonl`.

Luồng runtime:

1. UI chọn nhân vật trong sidebar.
2. App reset hội thoại khi đổi nhân vật.
3. RAG nạp đúng profile/chunks và index riêng cho nhân vật.
4. Guardrail dùng `death_year` của nhân vật.
5. Reranker ưu tiên đúng intent, đúng nhân vật, nguồn chính thống hơn và khử trùng lặp citation.
6. Gemini nhận profile, tone, citation và quy tắc bảo toàn Simulacra.
7. Text được render trước; âm thanh nhập vai tạo sau bằng job nền để không block UI.

Với Quang Trung, retriever có query rewriting cho đại từ `vua`, `ngài`, `ông`, `ta`, đồng thời route các câu “trận hãnh diện/đáng nhớ” về Ngọc Hồi - Đống Đa và Rạch Gầm - Xoài Mút. Với các nhân vật khác, runtime dùng query variants theo persona và intent `ideology`, `military_doctrine`, `life_milestone` để tránh trả lời tiểu sử khi người dùng hỏi tư tưởng hoặc chiến lược.

Mỗi chunk có `source_tier` và `source_quality_score`:

- Tier 1: sử liệu cổ, tài liệu nhà nước, bảo tàng/viện/cơ quan chính thống.
- Tier 2: sách, tạp chí nghiên cứu, nguồn học thuật hoặc chuyên ngành.
- Tier 3: báo/chuyên trang có biên tập và trích nguồn.
- Tier 4: Wiki/Wikisource phụ trợ, chỉ dùng khi không có nguồn tốt hơn.

## Simulacra Fallback

Lời nhân vật không được nói như bot đọc dataset. UI citation là nơi minh bạch học thuật; nhân vật chỉ nói bằng vai lịch sử.

- Nếu câu hỏi nằm trong đời nhân vật nhưng context chưa đủ chi tiết, câu trả lời chuyển sang tầng đại cục, không nói `không có dữ liệu`.
- Nếu câu hỏi sau năm mất, nhân vật nói rõ đó là chuyện đời sau.
- Riêng Hồ Chí Minh với các câu liên quan di sản sau 1969 như 1975, app trả theo dạng “sau khi Bác đã đi xa, sử sách đời sau ghi...”, không nói như nhân chứng trực tiếp.
- Không bịa chi tiết vi mô như ngày, địa danh, tên người nếu citation không neo được.
- Post-process chuyển ngôi thứ ba sang ngôi thứ nhất để nhân vật không tự gọi tên mình trong câu trả lời.

## Âm Thanh Nhập Vai

TTS dùng REST API, không dùng Service Account JSON và không ghi MP3 ra ổ đĩa. Audio được trả base64 và phát dưới câu trả lời.

Giao diện không hiển thị provider/model TTS. App mô phỏng khác biệt giọng bằng SSML:

- `quang_trung`: `pitch="-6st"`, `rate="0.95"`
- `tran_hung_dao`: `pitch="-8st"`, `rate="0.85"`
- `nguyen_trai`: `pitch="-2st"`, `rate="0.95"`
- `ho_chi_minh`: `pitch="+1st"`, `rate="0.85"`
- `vo_nguyen_giap`: `pitch="-4st"`, `rate="0.90"`

Nếu browser chặn autoplay, audio player Neo Kinpaku vẫn hiện nút `Phát`.

`tts_provider.py` đã có interface `TTSProvider`, hiện dùng provider Google Cloud ổn định; sau này có thể thêm provider riêng cho từng nhân vật nếu cần giọng vùng miền thật.

## Build Dataset

```powershell
python .\quang_trung_dataset\build_dataset.py
python .\quang_trung_dataset\build_multi_character_datasets.py
```

`build_multi_character_datasets.py` chuẩn hóa dữ liệu nguồn từ `DATASET-Ontology-Memory-History-Simulation-main` thành 4 folder mới ở root:

- `ho_chi_minh_dataset`: 150 chunks.
- `tran_hung_dao_dataset`: 125 chunks.
- `nguyen_trai_dataset`: 50 chunks.
- `vo_nguyen_giap_dataset`: 115 chunks sau repair record lỗi.

## Kiểm thử

```powershell
python .\quang_trung_dataset\validate_dataset.py
python .\quang_trung_dataset\validate_multi_character.py
python -m py_compile .\quang_trung_web\app.py .\quang_trung_web\rag_core.py .\quang_trung_web\llm_provider.py .\quang_trung_web\tts_provider.py .\quang_trung_web\smoke_test.py .\quang_trung_web\character_registry.py
cd quang_trung_web
.\.venv\Scripts\python.exe .\smoke_test.py
```

Smoke test hiện kiểm tra:

- Quang Trung battle reflection và mô tả trận quân Thanh.
- Positive/negative cases cho đủ 5 nhân vật.
- Không lẫn citation giữa nhân vật.
- Không tự gọi tên nhân vật trong câu trả lời tự nhiên.
- Citation có `source_tier` và `source_quality_score`.
- SSML payload dùng `input.ssml`, escape XML và đúng pitch/rate.
- Guardrail công nghệ hiện đại và câu sau năm mất.

## Files

- `character_registry.py`: registry 5 nhân vật.
- `app.py`: Streamlit UI, chọn nhân vật, chat, citation, TTS player.
- `rag_core.py`: loader multi-character, hybrid retrieval, intent routing, guardrail, simulation fallback.
- `llm_provider.py`: Gemini-only generator, prompt bảo toàn Simulacra.
- `tts_provider.py`: Google TTS REST, SSML voice profiles, trả audio base64.
- `smoke_test.py`: regression/runtime tests.
