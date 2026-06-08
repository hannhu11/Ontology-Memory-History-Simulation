# Legacy Streamlit + Shared RAG Runtime

Thư mục này hiện giữ hai vai trò:

- Runtime dùng chung cho production mới: `character_registry.py`, `rag_core.py`, `llm_provider.py`, `tts_provider.py`, assets và smoke tests.
- Ứng dụng Streamlit legacy để rollback nếu service Next.js/FastAPI gặp lỗi production.

Production chính hiện nằm ở `backend/` + `frontend/`; không phát triển UI mới trên Streamlit trừ khi cần hotfix rollback.

## Nhân vật hiện có

- Quang Trung / Nguyễn Huệ: `quang_trung_dataset`
- Hồ Chí Minh: `ho_chi_minh_dataset`
- Nguyễn Trãi: `nguyen_trai_dataset`
- Trần Hưng Đạo: `tran_hung_dao_dataset`
- Võ Nguyên Giáp: `vo_nguyen_giap_dataset`

`character_registry.py` là nguồn cấu hình duy nhất cho UI, dataset path, asset path, edge-case buttons và voice label.

## Chạy legacy Streamlit local

```powershell
cd quang_trung_web
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Không commit `.env`. Các biến chính:

- `LLM_PROVIDER`: `gemini_api` để gọi Gemini API key cũ, hoặc `vertex` để gọi Vertex AI bằng ADC.
- `GEMINI_API_KEY` chỉ dùng khi `LLM_PROVIDER=gemini_api`.
- `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_GENAI_USE_VERTEXAI=true` dùng khi `LLM_PROVIDER=vertex`.
- `GEMINI_MODEL_NAME`, `GEMINI_ROUTER_MODEL_NAME`; production Vertex mặc định dùng `gemini-2.5-flash`.
- `VERTEX_THINKING_BUDGET=0` để giảm hidden thinking tokens/latency cho chat realtime.
- `GOOGLE_TTS_API_KEY` để gọi Google Cloud Text-to-Speech.
- `GOOGLE_TTS_TIMEOUT_SECONDS` mặc định nên đặt `18`.
- `RAG_SCORE_THRESHOLD` mặc định nên đặt `0.42`.
- `RAG_TOP_K` mặc định nên đặt `4`.
- `RAG_EMBEDDING_MODEL` mặc định nên đặt `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `RAG_INDEX_DIR` mặc định nên đặt `.rag_index`.

Chỉ mục vector được tách theo nhân vật tại `.rag_index\<character_id>` và tự rebuild khi JSONL đổi.

## Multi-Character RAG Shared Runtime

`rag_core.py` không còn hardcode Quang Trung. Loader nhận `character_id`, tự nạp `<character_id>_profile.json` và `<character_id>_knowledge.jsonl`.

Luồng production mới:

1. FastAPI preload đúng profile/chunks/retriever cho 5 nhân vật lúc server start.
2. Next.js đổi nhân vật bằng state client, reset chat/citation/audio ngay, không rerun Python script.
3. RAG dùng đúng `character_id`, index riêng và guardrail theo `death_year`.
4. Reranker ưu tiên đúng intent, đúng nhân vật, nguồn chính thống hơn và khử trùng lặp citation.
5. Gemini nhận profile, tone, citation và quy tắc bảo toàn Simulacra.
6. Text stream qua SSE; âm thanh nhập vai gọi qua `/api/tts` sau `final`, không block chữ.

Với Quang Trung, retriever có query rewriting cho đại từ `vua`, `ngài`, `ông`, `ta`, đồng thời route các câu “trận hãnh diện/đáng nhớ” về Ngọc Hồi - Đống Đa và Rạch Gầm - Xoài Mút. Với các nhân vật khác, runtime dùng query variants theo persona và intent `ideology`, `military_doctrine`, `life_milestone` để tránh trả lời tiểu sử khi người dùng hỏi tư tưởng hoặc chiến lược.

Mỗi chunk có `source_tier` và `source_quality_score`:

- Tier 1: sử liệu cổ, tài liệu nhà nước, bảo tàng/viện/cơ quan chính thống.
- Tier 2: sách, tạp chí nghiên cứu, nguồn học thuật hoặc chuyên ngành.
- Tier 3: báo/chuyên trang có biên tập và trích nguồn.
- Tier 4: Wiki/Wikisource phụ trợ, chỉ dùng khi không có nguồn tốt hơn.

## Simulacra Fallback

Lời nhân vật không được nói như bot đọc dataset. UI citation là nơi minh bạch học thuật; nhân vật chỉ nói bằng vai lịch sử.

- Nếu câu hỏi nằm trong đời nhân vật nhưng context chưa đủ chi tiết, câu trả lời chuyển sang tầng đại cục, không nói `không có dữ liệu`.
- Chỉ chào hỏi thuần túy mới dùng fallback conversation. Các câu có `chào`, `cho tôi biết`, `tôi hỏi` nhưng chứa trận đánh, tư tưởng, tên riêng hoặc địa danh lịch sử vẫn đi qua hybrid retrieval/Gemini.
- Quang Trung có guard identity-confusion: `Nguyễn Huệ` là tên người, `Quang Trung` là niên hiệu, không phải hai nhân vật hoặc anh em.
- Nếu câu hỏi sau năm mất, nhân vật nói rõ đó là chuyện đời sau.
- Riêng Hồ Chí Minh với các câu liên quan di sản sau 1969 như 1975, app trả theo dạng “sau khi Bác đã đi xa, sử sách đời sau ghi...”, không nói như nhân chứng trực tiếp.
- Không bịa chi tiết vi mô như ngày, địa danh, tên người nếu citation không neo được.
- Post-process chuyển ngôi thứ ba sang ngôi thứ nhất để nhân vật không tự gọi tên mình trong câu trả lời.

## Real-Time Fused CRAG

Runtime backend/FastAPI dùng kiến trúc fused CRAG tối đa 2 Gemini/Vertex calls/request:

- `llm_provider.route_query_json()` là call router JSON nhanh, cấu hình bằng `GEMINI_ROUTER_MODEL_NAME` hoặc `GEMINI_MODEL_NAME`.
- `rag_core.answer_query()` nhận route, xử lý factual exact/local retrieval và không tự gọi LLM grader.
- `llm_provider.stream_fused_generation()` là call generator stream duy nhất; prompt yêu cầu mô hình tự bỏ chunk rác, dùng tri thức lịch sử nền khi context thiếu, không lộ `dataset/chunk/citation`.
- `LLM_PROVIDER=vertex` dùng `google-genai` với `genai.Client(vertexai=True, project=..., location=...)`; không cần Service Account JSON nếu host đã có `gcloud auth application-default login`.
- Không có post-generation reflection vì SSE đã stream token ra UI. Kiểm soát xưng hô/thuật ngữ hệ thống chạy bằng streaming mask trước khi yield.
- Nếu Gemini 429/timeout/chưa cấu hình, `local_route_query()` và local fallback bank theo nhân vật/intent vẫn tạo câu nhập vai; SSE metadata có `llm_status`, `fallback_used`, `route_source`.
- Factual exact trước RAG: `birth`, `origin`, `real_name`, `death`, `identity`. Điều này chặn lỗi HCM `sinh năm` bị bốc chunk Bến Nhà Rồng 1911.
- Chroma index safety ghi `embedding_provider`, `model_name`, `dimension`, `fingerprint`, `character_id`; đổi `RAG_EMBEDDING_PROVIDER`/model sẽ wipe và rebuild riêng index của nhân vật.

Kiểm tra Vertex AI ADC trên VPS:

```bash
/home/ubuntu/history-ontology/quang_trung_web/.venv/bin/python quang_trung_web/verify_vertex.py
```

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
python -m py_compile .\backend\main.py .\backend\smoke_test.py
python .\backend\smoke_test.py
cd quang_trung_web
.\.venv\Scripts\python.exe .\smoke_test.py
cd ..\frontend
npm install
npm run build
```

Smoke test hiện kiểm tra:

- Quang Trung battle reflection và mô tả trận quân Thanh.
- Regression câu thật của user: `chao vua, vua hay cho toi biet ve tran danh ngoc hoi , dong da di` không được trả fallback `Ta đang nghe`; `ông với nguyễn huệ là gì của nhau` phải trả đúng quan hệ tên/niên hiệu.
- Factual regressions: `bac sinh nam bao nhieu` -> `19/5/1890`; birth/origin/identity cho 5 nhân vật; Võ Nguyên Giáp Điện Biên Phủ phải giữ 1954/`đánh chắc tiến chắc`.
- Mock 429: UI vẫn nhận token fallback local và final metadata có `llm_status=quota_exhausted`.
- Unit smoke: streaming mask không lộ self-name/dataset/chunk; index metadata mismatch rebuild không giữ dimension cũ.
- Positive/negative cases cho đủ 5 nhân vật.
- Không lẫn citation giữa nhân vật.
- Không tự gọi tên nhân vật trong câu trả lời tự nhiên.
- Citation có `source_tier` và `source_quality_score`.
- SSML payload dùng `input.ssml`, escape XML và đúng pitch/rate.
- Guardrail công nghệ hiện đại và câu sau năm mất.

## Files

- `character_registry.py`: registry 5 nhân vật.
- `app.py`: Streamlit legacy UI/rollback.
- `rag_core.py`: loader multi-character, hybrid retrieval, intent routing, guardrail, simulation fallback.
- `llm_provider.py`: Gemini-only generator, prompt bảo toàn Simulacra.
- Prompt Gemini yêu cầu câu lịch sử/trận đánh/tư tưởng trả 2-4 đoạn văn xuôi, tối thiểu 5 câu; chỉ smalltalk thuần túy mới được ngắn.
- `tts_provider.py`: Google TTS REST, SSML voice profiles, trả audio base64.
- `smoke_test.py`: regression/runtime tests.
