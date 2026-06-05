# MEMORY - Dataset và Prototype Quang Trung

Tài liệu này dùng để ghi nhớ trạng thái dự án, lỗi đã phát hiện và quy tắc bắt buộc khi tiếp tục phát triển dataset hoặc web prototype. Đây là file local-only trong thư mục dataset; không dùng làm README công khai.

## Mục tiêu hiện tại

- Xây dựng dataset và web MVP cho nhân vật Vua Quang Trung / Nguyễn Huệ.
- Web cho phép người dùng trò chuyện với nhân vật lịch sử, có lớp RAG đối chiếu tư liệu và guardrail chống ảo giác.
- Nhân vật phải nói như một vị vua đang đối thoại với hậu thế; phần kiểm chứng học thuật nằm ở UI, không nằm trong miệng nhân vật.

## Lỗi nghiêm trọng đã phát hiện

1. Lời nhân vật bị Out of Character: xuất hiện các cụm như "nguồn đang có", "nguồn truy xuất", "guardrail", "dataset", "API", "người học".
2. Guardrail trả lời máy móc và sai trọng tâm. Ví dụ câu Blitzkrieg có năm 1789 đúng, nhưng hệ thống lại bác mốc 1789 thay vì bác khái niệm Blitzkrieg/quân Đức là đời sau.
3. Dataset thiên về quân sự, thiếu nặng mảng ngoại giao Tây Sơn - Thanh sau Ngọc Hồi - Đống Đa.
4. Câu hỏi về Càn Long, biểu tạ tội, cầu phong có nguy cơ bị hệ thống chối bỏ do thiếu dữ liệu. Đây là lỗi sử học nghiêm trọng.
5. UI dùng nhãn "Nguồn truy xuất" và hiển thị "Guardrail nội bộ" ngay dưới câu trả lời, làm sụp hình tượng nhập vai.

## Quy tắc tách vai

- Nhân vật chỉ nói bằng giọng nhập vai: xưng "ta", không tự gọi mình là Quang Trung / Nguyễn Huệ.
- UI chịu trách nhiệm minh bạch học thuật: panel citation dùng "Tư liệu đối chiếu".
- Nhân vật không được nhắc cơ chế vận hành của hệ thống.
- Khi thiếu chứng cứ, nhân vật nói: "Việc ấy chưa đủ chứng cứ để ta nhận là thật. Chớ vội biến lời truyền chưa rõ thành sử thực."
- Khi gặp khái niệm đời sau, nhân vật bác đúng phần sai, không bác sự kiện lịch sử đúng.

## Từ cấm trong lời nhân vật

Các từ/cụm sau không được xuất hiện trong `character_response`, fallback RAG, hoặc câu trả lời API:

- nguồn
- truy xuất
- guardrail
- dataset
- API
- người học
- mô hình
- citation
- chunk

Ngoại lệ: các từ kỹ thuật có thể xuất hiện trong tài liệu kỹ thuật, log kiểm thử, README nội bộ, tên biến, hoặc UI kiểm chứng; nhưng không được nằm trong lời nhân vật.

## Case test bắt buộc

- Càn Long / biểu tạ tội / cầu phong: phải trả lời rằng sau đại thắng vẫn có giảng hòa, cầu phong, dùng ngôn ngữ bang giao mềm dẻo; không được chối bỏ sự kiện; không diễn giải thành "phục tùng tuyệt đối".
- Blitzkrieg / quân Đức: phải công nhận năm Kỷ Dậu 1789 là đúng, nhưng bác Blitzkrieg là khái niệm đời sau.
- Vương Đại Hải / cửa biển Thần Phù / năm 1790: không bịa trận; trả lời nhập vai rằng việc ấy chưa đủ chứng cứ.
- Internet / Facebook / AI / Điện Biên Phủ: bác ngoài thời đại, giữ giọng vua.
- Ngọc Hồi - Đống Đa, Nghệ An, Rạch Gầm - Xoài Mút: vẫn phải trả lời factual, có tư liệu đối chiếu ở UI.

## Dữ liệu cần bổ sung

Ưu tiên bổ sung cụm ngoại giao Tây Sơn - Thanh:

- Ngô Thì Nhậm và đường lối giảng hòa sau chiến thắng.
- Thư tạ tội / thư giảng hòa trong ngôn ngữ bang giao.
- Phúc Khang An và vai trò làm trung gian xử lý hậu chiến.
- Càn Long, cầu phong và việc nhà Thanh phong vương theo nghi lễ bang giao.
- Phạm Công Trị / giả vương sang Thanh: đánh dấu `claim_status = contested` nếu nguồn có tranh luận.
- Phân biệt ngoại giao triều cống với việc "phục tùng tuyệt đối".

## Quy tắc đánh giá nghiêm khắc

- Nhập vai nhân vật không đạt nếu còn lộ thuật ngữ kỹ thuật.
- RAG không đạt nếu chặn bịa nhưng bác sai trọng tâm.
- Dataset không đạt nếu chỉ tạo một Quang Trung võ biền mà bỏ thiếu ngoại giao.
- UI không đạt nếu panel kiểm chứng làm người dùng tưởng nhân vật tự nói về hệ thống.

## Ghi chú vận hành

- Bước hiện tại là local-only, không push GitHub.
- Sau khi sửa phải regenerate `quang_trung_profile.json` và `quang_trung_knowledge.jsonl`.
- Chạy validation dataset và smoke test web trước khi dùng demo.

## Trạng thái cập nhật 2026-06-03

- Đã regenerate dataset lên 62 chunks.
- Đã thêm 12 chunks ngoại giao `qt_kb_051`-`qt_kb_062`.
- Đã thêm trường `claim_status` cho từng chunk: mặc định `established`, riêng các nhận định diễn giải là `interpretive`, các vấn đề Phạm Công Trị / giả vương là `contested`.
- Đã sửa sample dialogues để lời nhân vật không dùng "nguồn", "truy xuất", "người học", "guardrail", "dataset", "API".
- Đã sửa RAG fallback để nhân vật nói nhập vai: thiếu chứng cứ thì nói "Việc ấy chưa đủ chứng cứ để ta nhận là thật"; không nhắc cơ chế hệ thống.
- Đã sửa case Blitzkrieg: giữ mốc Kỷ Dậu 1789 là đúng, bác Blitzkrieg/quân Đức là khái niệm đời sau.
- Đã sửa case Càn Long: trả lời theo hướng ngoại giao mềm, giảng hòa/cầu phong/bang giao, không diễn giải thành mất độc lập hoặc phục tùng tuyệt đối.
- Đã đổi UI: "Nguồn truy xuất" thành "Tư liệu đối chiếu"; "Năm nguồn" thành "Niên đại tài liệu"; "Mở nguồn" thành "Mở tư liệu"; trạng thái kỹ thuật nằm trong expander "Trạng thái kiểm chứng".
- Đã lọc hậu xử lý API: nếu Gemini/Groq sinh thuật ngữ cấm hoặc tự gọi tên nhân vật, app bỏ câu đó và dùng fallback nội bộ.

## Trạng thái cập nhật lần 2 ngày 2026-06-03

- Đã mở rộng dataset lên 100 chunks, mỗi chunk dài 130-164 từ, có `source_quality`, `answer_intents`, `canonical_questions`, `tag_blob`.
- Đã bổ sung các cụm dữ liệu thiếu: Phượng Hoàng Trung Đô, Nguyễn Thiếp, tín bài, sổ đinh, Chiếu khuyến nông, tiền Quang Trung thông bảo / Quang Trung đại bảo, Chiếu lập học, Sùng chính viện, Ngô Thì Nhậm, Chiếu cầu hiền, ăn Tết trước, tượng binh, hỏa hổ, mộc rơm ướt.
- Đã sửa ground truth tín bài: dùng `Thiên hạ đại tín`; `Thiên hạ đại định` chỉ còn xuất hiện trong chunk correction để hệ thống chỉnh lại khi người dùng hỏi sai.
- Đã chuyển web sang `VectorRetriever` dùng ChromaDB + `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, có `RAG_SCORE_THRESHOLD`, `RAG_TOP_K`, `RAG_EMBEDDING_MODEL`, `RAG_INDEX_DIR`.
- Đã giữ fallback lexical có intent filter để xử lý tiếng Việt có dấu/không dấu và tránh rơi lại lỗi bắt rác top-K.
- Đã bổ sung guardrail cho `thế chiến`, `chiến tranh thế giới`, `world war`, `WW1`, `WW2`, năm 1939, 1945 và mọi mốc sau 1792.
- Đã thay fallback chung "Việc ấy có liên quan tới những điều đã chép..." bằng các câu trả lời intent-specific hoặc câu thiếu chứng cứ hẹp hơn.
- Đã thêm positive tests nâng cao cho 9 câu cải cách/định đô/sĩ phu/quân sự vi mô và negative tests Thế chiến.

## Kiểm thử đã chạy 2026-06-03

- `python .\quang_trung_dataset\build_dataset.py`
- `python .\quang_trung_dataset\validate_dataset.py`
- `.\quang_trung_web\.venv\Scripts\python.exe -m py_compile ...`
- `.\quang_trung_web\.venv\Scripts\python.exe .\smoke_test.py`
- Kiểm tra UI trên `http://localhost:8501`: câu Càn Long hiển thị `qt_kb_061`, `qt_kb_056`, `qt_kb_057`; câu Blitzkrieg hiển thị `qt_kb_050`; panel là "Tư liệu đối chiếu".
- Kiểm tra API thực tế với câu Nghệ An: `mode: api`, câu trả lời tiếng Việt có dấu, xưng "ta", không lộ thuật ngữ kỹ thuật.

## Trạng thái backup GitHub ngày 2026-06-05

- Repo backup chính thức: `https://github.com/hannhu11/Ontology-Memory-History-Simulation`.
- Nội dung đưa lên repo backup gồm `quang_trung_dataset/` và `quang_trung_web/`, bao gồm dataset JSONL đã build, profile, script build/validate, app Streamlit, RAG core, provider API, smoke test, README và asset UI cần thiết.
- Tuyệt đối không push `.env`, API key, token, `.venv/`, `.rag_index/`, log Streamlit, `__pycache__/`, file model cache hoặc file build tạm. `.env.example` chỉ giữ tên biến rỗng để người triển khai tự điền local.
- Khi clone repo mới, chạy từ thư mục gốc:
  - `cd quang_trung_web`
  - `python -m venv .venv`
  - `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
  - copy `.env.example` thành `.env` ở local và tự điền `GROQ_API_KEY`, `GEMINI_API_KEY` nếu muốn dùng API thật; không commit `.env`.
  - `.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`
- Lệnh build và kiểm thử trước demo:
  - `python .\quang_trung_dataset\build_dataset.py`
  - `python .\quang_trung_dataset\validate_dataset.py`
  - `.\quang_trung_web\.venv\Scripts\python.exe -m py_compile .\quang_trung_web\app.py .\quang_trung_web\rag_core.py .\quang_trung_web\llm_provider.py .\quang_trung_web\tts_provider.py .\quang_trung_web\smoke_test.py`
  - `cd quang_trung_web; .\.venv\Scripts\python.exe .\smoke_test.py`
- `.rag_index/quang_trung` là cache ChromaDB local, tự rebuild khi JSONL đổi; không cần và không được đưa lên GitHub.
- Mỗi khi hoàn thành một plan hoặc nhiệm vụ đáng kể, cập nhật file này trước khi commit/push để agent ở chat mới đọc một file là biết trạng thái dự án, cách setup và các ràng buộc hiện tại.
