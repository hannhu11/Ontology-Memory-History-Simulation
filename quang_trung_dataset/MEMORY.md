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
- Đã lọc hậu xử lý API: nếu nhà cung cấp LLM sinh thuật ngữ cấm hoặc tự gọi tên nhân vật, app bỏ câu đó và dùng fallback nội bộ.

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
- Commit backup đã push: `310f792` trên branch `main`.
- Nội dung đưa lên repo backup gồm `quang_trung_dataset/` và `quang_trung_web/`, bao gồm dataset JSONL đã build, profile, script build/validate, app Streamlit, RAG core, provider API, smoke test, README và asset UI cần thiết.
- Tuyệt đối không push `.env`, API key, token, `.venv/`, `.rag_index/`, log Streamlit, `__pycache__/`, file model cache hoặc file build tạm. `.env.example` chỉ giữ tên biến rỗng để người triển khai tự điền local.
- Khi clone repo mới, chạy từ thư mục gốc:
  - `cd quang_trung_web`
  - `python -m venv .venv`
  - `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
  - copy `.env.example` thành `.env` ở local và tự điền `GEMINI_API_KEY` nếu muốn dùng API thật; không commit `.env`.
  - `.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`
- Lệnh build và kiểm thử trước demo:
  - `python .\quang_trung_dataset\build_dataset.py`
  - `python .\quang_trung_dataset\validate_dataset.py`
  - `.\quang_trung_web\.venv\Scripts\python.exe -m py_compile .\quang_trung_web\app.py .\quang_trung_web\rag_core.py .\quang_trung_web\llm_provider.py .\quang_trung_web\tts_provider.py .\quang_trung_web\smoke_test.py`
  - `cd quang_trung_web; .\.venv\Scripts\python.exe .\smoke_test.py`
- `.rag_index/quang_trung` là cache ChromaDB local, tự rebuild khi JSONL đổi; không cần và không được đưa lên GitHub.
- Mỗi khi hoàn thành một plan hoặc nhiệm vụ đáng kể, cập nhật file này trước khi commit/push để agent ở chat mới đọc một file là biết trạng thái dự án, cách setup và các ràng buộc hiện tại.

## Ràng buộc làm việc do user nhắc ngày 2026-06-05

- Không tự ý sửa, xóa hoặc thay đổi backend, frontend hay chức năng ngoài phạm vi user yêu cầu. Nếu cần đụng vào một phần không nằm trong yêu cầu rõ ràng, phải hỏi user trước.
- Được phép copy logic/chức năng và được phép đụng backend/frontend trong đúng phần được yêu cầu nếu cần để hoàn thành nhiệm vụ.
- Tuyệt đối không push file key, token, `.env`, credential hoặc artifact vi phạm chuẩn bảo mật lên GitHub.
- Nếu nhiệm vụ có liên quan đến design, phải đọc và lấy hướng style trong folder `impeccable-main` trước khi áp dụng vào `signsafe`.
- Mỗi nhiệm vụ/plan hoàn thành phải cập nhật `MEMORY.md` để agent ở chat mới nắm được trạng thái cũ, setup, cách chạy server, thay đổi mới và các ràng buộc đang còn hiệu lực.

## Trạng thái tích hợp TTS ngày 2026-06-05

- Đã nối Google Cloud Text-to-Speech cho web Quang Trung bằng REST API `text:synthesize`, không dùng Service Account JSON và không ghi MP3 ra ổ đĩa.
- File đã chạm trong nhiệm vụ TTS: `quang_trung_web/tts_provider.py`, `quang_trung_web/app.py`, `quang_trung_web/.env.example`, `quang_trung_web/.gitignore`, `quang_trung_web/requirements.txt`, `quang_trung_web/README.md`, `quang_trung_dataset/MEMORY.md`.
- Provider TTS cố định `vi-VN-Neural2-D`, `languageCode=vi-VN`, `ssmlGender=MALE`, `audioEncoding=MP3`; hàm `synthesize()` trả `audio_base64` trong session message.
- UI audio player tự hiện dưới câu trả lời assistant và chỉ đọc đúng `result["answer"]`; không đọc citation, metadata, chunk, trạng thái kiểm chứng hay nội dung UI học thuật.
- Style audio player học từ `C:\Users\ADMIN\Downloads\Research MLN111\impeccable-main`: lacquer dark surface, kinpaku gold, patina status, hairline border, radius nhỏ, không glass/neon/card lồng nhau.
- Cấu hình local cần có trong `quang_trung_web/.env`: `GOOGLE_TTS_API_KEY` và tùy chọn `GOOGLE_TTS_TIMEOUT_SECONDS=18`. Không commit `.env`, `.env.*`, key, token, audio cache, `.venv`, `.rag_index` hoặc log.
- Nếu browser chặn autoplay, player vẫn hiện nút `Phát` để người dùng nghe thủ công.

## Trạng thái Gemini-only và TTS đanh thép ngày 2026-06-05

- Đã tinh gọn LLM provider về một đường duy nhất: Gemini API với model cố định `gemini-3.5-flash`. Lý do chọn: cân bằng tốt giữa chất lượng suy luận, tiếng Việt, độ ổn định production và chi phí trung bình hơn nhóm Pro/Preview.
- Đã xóa logic provider switching cũ khỏi code active: không còn chọn `auto`, không còn provider order, không còn dropdown chọn model trong sidebar. Người dùng chỉ thấy nhân vật, kịch bản gài bẫy, reload/clear và trạng thái Google TTS.
- Cấu hình local hiện cần `GEMINI_API_KEY` trong `quang_trung_web/.env`; `.env.example` không còn các biến provider cũ hoặc biến đổi model thủ công.
- `llm_provider.py` gọi Gemini REST `generateContent` qua `GEMINI_API_KEY`, `temperature=0.32`, `topP=0.9`, `maxOutputTokens=900`, sau đó vẫn lọc nhập vai để không lộ thuật ngữ kỹ thuật hoặc tự gọi tên nhân vật.
- `tts_provider.py` vẫn dùng Google Cloud TTS `vi-VN-Neural2-D`, nhưng đã thêm `pitch=-4.0` và `speakingRate=1.05` trong `audioConfig` để giọng trầm, chắc và dứt khoát hơn. Audio vẫn trả base64 trong bộ nhớ, không ghi MP3 xuống ổ đĩa.
- README và `.env.example` đã cập nhật theo Gemini-only. `requirements.txt` không còn dependency provider cũ.
- Live check bằng `GEMINI_API_KEY` local ngày 2026-06-05 trả `HTTP 403 PERMISSION_DENIED` cho cả `gemini-3.5-flash` và `gemini-2.5-flash`; đây là lỗi quyền truy cập project/key của Google API, không phải lỗi routing provider cũ hay UI. Khi có key/project hợp lệ, code sẽ gọi Gemini-only; nếu API trả lỗi, app vẫn dùng fallback nội bộ để không làm hỏng hội thoại.
- Khi test hoặc push sau này, luôn kiểm tra `.env` không staged và không đưa API key/token vào code, README, MEMORY, log, `.rag_index`, `.venv` hoặc cache.

## Trạng thái Hybrid Simulacra RAG và SSML TTS ngày 2026-06-05

- Đã sửa lỗi câu tự nhiên như `vua nói qua về 1 trận đánh vua cảm thấy hãnh diện nhất đi`. Nguyên nhân không phải thiếu dataset mà là intent routing không nhận ra `vua` là Quang Trung và không nhận ra cụm `trận đánh/hãnh diện` là câu hỏi hồi tưởng chiến trận.
- `rag_core.py` đã có `rewrite_query(query, profile)`: mở rộng `vua`, `ngài`, `ông`, `ta` thành Quang Trung / Nguyễn Huệ / Tây Sơn và mở rộng các câu hỏi battle reflection sang Ngọc Hồi - Đống Đa, Rạch Gầm - Xoài Mút.
- Đã thêm intent `battle_reflection`; các chunk `micro_tactics` và `military` được suy luận là có thể phục vụ battle reflection. Retriever chạy hybrid deterministic bằng original query, rewritten query và canonical variants, sau đó fuse/rerank theo intent, source quality và tag lịch sử.
- Câu hỏi battle reflection hiện phải trả citation chiến trận, không được lấy nhầm tiền tệ, sĩ phu hoặc ngoại giao. Câu trả lời nội bộ chọn Ngọc Hồi - Đống Đa là ký ức hãnh diện nhất và có thể nhắc thêm Rạch Gầm - Xoài Mút như chiến thắng lớn ở phương Nam.
- Fallback nội bộ đã đổi từ lối trả lời kiểu bot kiểm chứng sang simulation fallback: với câu hỏi còn rộng nhưng trong thời đại Quang Trung, nhân vật nói đại cục lịch sử bằng vai quân vương. Guardrail vẫn giữ nghiêm với câu sau 1792, truyền thuyết hoặc claim sai mốc.
- `llm_provider.py` đã cập nhật prompt “bảo toàn Simulacra”: Gemini phải dùng citation làm neo nhưng không được nói `không có dữ liệu`, `không thấy căn cứ`, `tư liệu hiện có`, `ngữ cảnh` hoặc các thuật ngữ kỹ thuật trong lời nhân vật.
- `tts_provider.py` đã chuyển từ `input.text` sang `input.ssml`, giữ voice `vi-VN-Neural2-D` nhưng bọc câu trả lời bằng `<prosody pitch="-7st" rate="0.90"><emphasis level="strong">...</emphasis></prosody>` để mô phỏng giọng trầm, chậm và uy nghi hơn. Google Cloud TTS hiện không có nhãn giọng miền Trung/Bình Định riêng cho `vi-VN`.
- `smoke_test.py` đã bổ sung regression tests cho pronoun rewriting, battle reflection retrieval và SSML payload escaping.

## Hotfix battle description ngày 2026-06-06

- User phát hiện câu `vua hãy mô tả về trận đánh với quân thanh đi` vẫn có lúc trả lời như fallback cũ hoặc quá chung. Nguyên nhân thực tế gồm hai lớp: server Streamlit đang chạy process cũ trước khi nạp patch, và logic intent trước đó xếp mọi câu có `trận đánh` + đại từ `vua/ngài` vào `battle_reflection`.
- Đã tách rõ hai nhóm:
  - `battle_reflection`: chỉ dùng cho câu hỏi hãnh diện/tự hào/đáng nhớ/chiến thắng nào.
  - `micro_tactics`: dùng cho câu mô tả/kể/diễn biến trận với quân Thanh, Ngọc Hồi, Đống Đa, Tôn Sĩ Nghị.
- `rag_core.py` đã thêm từ khóa `quân Thanh`, `Tôn Sĩ Nghị`, `mô tả trận`, `diễn biến trận`, `trận đánh với quân Thanh` vào `micro_tactics`; `query_variants()` cũng thêm biến thể Ngọc Hồi - Đống Đa, Hà Hồi, tượng binh, hỏa hổ, đại bác, mộc rơm ướt.
- Câu trả lời `micro_tactics` mặc định đã đổi thành mô tả cụ thể chiến dịch chống quân Thanh: tiến thần tốc, chia nhiều đạo, uy hiếp Hà Hồi, đánh Ngọc Hồi bằng mộc rơm ướt, phối hợp tượng binh/hỏa hổ/súng/bộ binh, vu hồi Đống Đa và làm Tôn Sĩ Nghị rối loạn.
- `smoke_test.py` đã thêm `BATTLE_DESCRIPTION_CASES`, trong đó có đúng câu user báo lỗi. Test yêu cầu intent phải là `micro_tactics`, không phải `battle_reflection`, answer phải nhắc `quân Thanh`, `Ngọc Hồi`, `Đống Đa`, và citation phải thuộc nhóm chiến trận.
- Nếu trình duyệt còn hiện câu cũ sau hotfix, cần hard refresh hoặc bấm `Xóa hội thoại`; câu cũ đã được sinh trong session trước đó sẽ không tự biến mất.

## Trạng thái mở rộng 5 nhân vật ngày 2026-06-06

- Đã mở rộng runtime từ Quang Trung-only sang multi-character RAG cho 5 nhân vật: `quang_trung`, `ho_chi_minh`, `nguyen_trai`, `tran_hung_dao`, `vo_nguyen_giap`.
- Đã thêm `quang_trung_web/character_registry.py`. Đây là registry trung tâm map display name, `character_id`, dataset dir, asset dir, voice label và edge-case buttons. `app.py` lấy danh sách nhân vật từ registry và reset hội thoại khi đổi nhân vật.
- Đã chuẩn hóa thêm 4 dataset từ `DATASET-Ontology-Memory-History-Simulation-main`:
  - `ho_chi_minh_dataset`: 150 chunks.
  - `tran_hung_dao_dataset`: 125 chunks, gồm 120 JSONL + 5 profile knowledge không trùng ID.
  - `nguyen_trai_dataset`: 50 chunks, chuyển file `.json` dạng JSONL thành JSONL hợp lệ.
  - `vo_nguyen_giap_dataset`: 115 chunks, repair lỗi dòng `vng_kb_085` bị dính record `vng_kb_071`.
- Script mới:
  - `quang_trung_dataset/build_multi_character_datasets.py` để rebuild 4 dataset mới từ source folder.
  - `quang_trung_dataset/validate_multi_character.py` để kiểm tra đủ profile, chunk schema, chunk ID không trùng, registry và voice profile.
- `rag_core.py` đã generalize loader:
  - `load_profile(character_id)`.
  - `load_chunks(character_id)`.
  - `VectorRetriever(chunks, character_id=...)`.
  - Index/cache tách theo `.rag_index/<character_id>` để tránh lẫn dữ liệu.
- Guardrail hiện dùng `death_year` theo profile. Câu sau khi nhân vật mất bị chặn đúng vai; riêng Hồ Chí Minh với câu di sản sau 1969 như Chiến dịch Hồ Chí Minh/30-4-1975 được trả theo dạng `sau khi Bác đã đi xa, sử sách đời sau ghi...`, không nói như nhân chứng trực tiếp.
- Đã sửa lỗi intent `Điện Biên Phủ`: vẫn là guardrail với nhân vật mất trước 1954, nhưng với Võ Nguyên Giáp thì được route vào `military` để retrieve đúng các chunk `vng_kb_065`, `vng_kb_068`, `vng_kb_067`, `vng_kb_054` về quyết định chuyển từ `đánh nhanh` sang `đánh chắc tiến chắc`.
- `llm_provider.py` dùng `system_prompt_blueprint`, `tone_of_voice` và metadata từ profile, nhưng override các câu prompt máy móc để bảo toàn Simulacra: không được lộ thuật ngữ kỹ thuật, không nói như AI đọc dataset, được trả lời tầng đại cục khi context thiếu nhưng không bịa chi tiết vi mô.
- `tts_provider.py` đã có voice matrix SSML cho từng nhân vật, dùng chung Google Cloud `vi-VN-Neural2-D`:
  - Quang Trung: `pitch="-6st"`, `rate="0.95"`.
  - Trần Hưng Đạo: `pitch="-8st"`, `rate="0.85"`.
  - Nguyễn Trãi: `pitch="-2st"`, `rate="0.95"`.
  - Hồ Chí Minh: `pitch="+1st"`, `rate="0.85"`.
  - Võ Nguyên Giáp: `pitch="-4st"`, `rate="0.90"`.
- Google Cloud hiện không có voice `vi-VN` theo vùng miền miền Trung/Bình Định/Nghệ An; khác biệt giọng đang được mô phỏng bằng SSML pitch/rate, không thêm provider mới.
- `smoke_test.py` đã mở rộng regression:
  - Battle reflection và battle description cho Quang Trung.
  - 2 positive + 2 negative/multi checks cho các nhân vật mới.
  - HCM legacy-afterlife case.
  - TTS payload SSML theo từng nhân vật và XML escaping.

## Kiểm thử đã chạy cho multi-character ngày 2026-06-06

- `python -m py_compile quang_trung_web\app.py quang_trung_web\rag_core.py quang_trung_web\llm_provider.py quang_trung_web\tts_provider.py quang_trung_web\smoke_test.py quang_trung_web\character_registry.py quang_trung_dataset\build_multi_character_datasets.py quang_trung_dataset\validate_multi_character.py`
- `python quang_trung_dataset\validate_dataset.py` -> Quang Trung 100 chunks, pass.
- `python quang_trung_dataset\validate_multi_character.py` -> 5 nhân vật pass: 100/150/125/50/115 chunks.
- `cd quang_trung_web; .\.venv\Scripts\python.exe .\smoke_test.py` -> pass. Smoke output xác nhận câu `vua nói qua về 1 trận đánh...` trả Ngọc Hồi - Đống Đa/Rạch Gầm, câu `vua hãy mô tả về trận đánh với quân thanh đi` trả micro tactics, và Võ Nguyên Giáp retrieve đúng Điện Biên Phủ.

## Cách chạy sau khi clone mới

- Từ root repo:
  - `python .\quang_trung_dataset\build_dataset.py`
  - `python .\quang_trung_dataset\build_multi_character_datasets.py` nếu cần rebuild 4 dataset mới từ source folder.
  - `python .\quang_trung_dataset\validate_dataset.py`
  - `python .\quang_trung_dataset\validate_multi_character.py`
  - `cd quang_trung_web`
  - `python -m venv .venv`
  - `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
  - copy `.env.example` thành `.env`, điền `GEMINI_API_KEY` và `GOOGLE_TTS_API_KEY` local nếu có; không commit `.env`.
  - `.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501`
- Nếu UI còn hiện câu trả lời cũ sau khi patch, bấm `Xóa hội thoại`, hard refresh trình duyệt, hoặc restart process Streamlit. Session cũ không tự cập nhật câu đã sinh.
- Không push `.env`, API key, token, `.venv`, `.rag_index`, `__pycache__`, log, cache model hoặc file tạm. Mọi plan/nhiệm vụ xong phải cập nhật `MEMORY.md` trước commit/push.

## Trạng thái backup GitHub multi-character ngày 2026-06-06

- Đã đồng bộ `quang_trung_web/`, `quang_trung_dataset/` và 4 dataset mới vào repo backup `https://github.com/hannhu11/Ontology-Memory-History-Simulation`.
- Commit code/dataset chính đã push lên branch `main`: `bf5b679` (`Add multi-character simulacra RAG`).
- Trước khi push đã chạy secret scan trong `github_dataset_repo`, không phát hiện `GEMINI_API_KEY`, Google TTS key, token hoặc Groq/provider cũ trong staged diff.

## Hotfix kiểm soát câu Bạch Đằng Trần Hưng Đạo ngày 2026-06-08

- Sau smoke test production phát hiện câu `Đại Vương kể trận Bạch Đằng năm 1288` tuy pass nhưng câu trả lời/citation có nguy cơ lẫn chunk ngoại giao hậu chiến và sự kiện 1285.
- Đã thêm route riêng trong `rag_core.py` cho Trần Hưng Đạo/Bạch Đằng 1288:
  - nhận diện `Bạch Đằng`, `Ô Mã Nhi`, `bãi cọc`, `thủy triều`, `1288`;
  - bổ sung query variants theo diễn biến trận thủy chiến;
  - selector citation riêng ưu tiên chunk đúng trận, loại/đẩy lùi `ngoại_giao`, `hậu_chiến`, `hòa_bình`, `1285`, `Diên Hồng`, `Lý Hằng`;
  - câu trả lời nhập vai nói trực tiếp về thủy triều, bãi cọc, dụ Ô Mã Nhi và tổng công kích, không ghép fact rời.
- `smoke_test.py` đã siết case này: câu trả lời phải có đủ `Bạch Đằng`, `Ô Mã Nhi`, `bãi cọc`, `thủy triều` và citation không được lẫn off-target 1285/ngoại giao/hậu chiến.

## Deploy production sau nâng cấp ngày 2026-06-08

- Đã push GitHub các commit:
  - `93e9b9f` - `Improve simulacra RAG performance`
  - `9522207` - `Tighten Bach Dang retrieval routing`
- Production server Oracle: `/home/ubuntu/history-ontology`, service `history-ontology.service`.
- Đã `git pull --ff-only origin main`, chạy `py_compile`, `validate_dataset.py`, `validate_multi_character.py` và `quang_trung_web/smoke_test.py` trên VPS: pass.
- Đã restart `history-ontology.service`; service active, Streamlit chạy qua `/home/ubuntu/history-ontology/quang_trung_web/.venv/bin/streamlit run app.py --server.address 172.19.0.1 --server.port 8501`.
- Acceptance check sau restart:
  - `http://172.19.0.1:8501` trả `HTTP 200`.
  - Nginx host `history-simulation-ai.online` trả `HTTP 200`.
  - `https://history-simulation-ai.online/` trả `HTTP 200`.
  - `https://pethubvn.store/` vẫn trả `HTTP 200`; không sửa Nginx/PetHub, không mở public port `8501`.
- Production repo còn thư mục untracked `deploy/`; để nguyên vì không liên quan đến app/history service.
- Server local đã restart ở `http://127.0.0.1:8501`; browser check xác nhận sidebar có đủ 5 nhân vật, selectbox/profile khớp sau khi clear session, audio status chỉ còn một block theo nhân vật đang chọn.
- Nếu chat mới tiếp tục nhiệm vụ, đọc file này trước, sau đó kiểm tra `git -C github_dataset_repo log -1 --oneline` để biết commit backup mới nhất.

## Hotfix ẩn thông tin TTS trên UI ngày 2026-06-06

- User yêu cầu không để lộ provider/model TTS trong giao diện. UI không được hiển thị các chuỗi như `Google TTS`, `vi-VN-Neural2-D`, hoặc block sidebar `Giọng nói / Google TTS đã cấu hình`.
- `quang_trung_web/app.py` đã đổi nhãn audio player thành `Âm thanh nhập vai` và `Đang đọc lời nhân vật`; đã xóa toàn bộ khối sidebar `Giọng nói`, status cấu hình TTS và caption tự động đọc.
- Cấu hình kỹ thuật trong `tts_provider.py` vẫn giữ để gọi API, nhưng chỉ nằm ở backend/source code; người dùng cuối không thấy provider/model/voice name trong web.

## Trạng thái production Oracle/Cloudflare ngày 2026-06-07

- Domain production của History Ontology: `https://history-simulation-ai.online/`.
- VPS Oracle dùng chung với PetHub: `140.245.119.189`, SSH bằng user `ubuntu`. Không ghi private key vào repo/MEMORY.
- Cloudflare DNS cho `history-simulation-ai.online`: root `A` và `www` đang proxied qua Cloudflare về IP `140.245.119.189`. Không cần DNS record chứa port `8501`.
- PetHub đang chạy trong Docker, Nginx nằm trong container `pethub-nginx`, không phải Nginx cài trực tiếp trên host. Port public `80/443` đang do Docker proxy vào `pethub-nginx`.
- Không mở public port `8501` trong OCI. History Streamlit chạy bằng systemd service riêng `history-ontology.service`, bind nội bộ vào Docker bridge `172.19.0.1:8501`.
- Code production clone tại `/home/ubuntu/history-ontology`, app tại `/home/ubuntu/history-ontology/quang_trung_web`, venv tại `/home/ubuntu/history-ontology/quang_trung_web/.venv`.
- `.env` production đã copy vào `/home/ubuntu/history-ontology/quang_trung_web/.env`, chmod `600`; tuyệt đối không in/cat/push file này.
- Nginx History config được nạp vào container tại `/etc/nginx/conf.d/history-simulation-ai.online.conf`, host giữ bản copy tại `/home/ubuntu/history-ontology/deploy/history-simulation-ai.online.conf`.
- Script khôi phục/reload Nginx đã tạo tại `/home/ubuntu/history-ontology/deploy/apply-history-nginx.sh`.
- Vì config Nginx History đang nằm trong writable layer của container, nếu sau này PetHub redeploy/recreate `pethub-nginx`, cần copy lại host file vào container:
  - Cách nhanh: `/home/ubuntu/history-ontology/deploy/apply-history-nginx.sh`
  - Hoặc chạy thủ công:
  - `docker cp /home/ubuntu/history-ontology/deploy/history-simulation-ai.online.conf pethub-nginx:/etc/nginx/conf.d/history-simulation-ai.online.conf`
  - `docker exec pethub-nginx nginx -t`
  - `docker exec pethub-nginx nginx -s reload`
- Lệnh vận hành:
  - Xem app: `systemctl status history-ontology.service`
  - Log app: `journalctl -u history-ontology.service -n 100 --no-pager`
  - Restart app: `sudo systemctl restart history-ontology.service`
  - Test nội bộ app: `curl -I http://172.19.0.1:8501`
  - Test Nginx host-header: `curl -I -H 'Host: history-simulation-ai.online' http://127.0.0.1`
- Kiểm tra đã chạy ngày 2026-06-07:
  - `history-ontology.service` active/running.
  - `curl -I http://172.19.0.1:8501` trả `HTTP/1.1 200 OK`.
  - `curl -I -H 'Host: history-simulation-ai.online' http://127.0.0.1` trả `200 OK`, không còn redirect sang PetHub.
  - `https://history-simulation-ai.online/` mở đúng app `Đối thoại lịch sử`.
  - `https://pethubvn.store/` vẫn trả `200 OK`, không bị ảnh hưởng.

## Trạng thái nâng cấp hiệu năng, RAG và Simulacra ngày 2026-06-08

- User phản ánh web lag, nhân vật trả lời một màu, RAG có citation lệch intent, đôi khi tự gọi tên mình ở ngôi thứ ba như `Võ Nguyên Giáp...`, và âm thanh làm chậm câu chữ.
- Nguyên nhân chính trong code cũ: `app.py` xử lý tuần tự `answer_query -> synthesize -> append assistant -> rerun`, nên giao diện phải đợi xong cả Gemini/TTS mới hiện phản hồi; `rag_core.py` còn fallback chung cho nhiều nhân vật; metadata nguồn chưa có tier/rerank đủ mạnh.
- Đã sửa `quang_trung_web/app.py`:
  - Thêm cơ chế `pending_answer`: khi submit, câu hỏi user được đưa vào session và rerun trước, sau đó mới xử lý retrieval/answer.
  - Thêm streaming text qua Gemini SSE ở lớp UI bằng placeholder cập nhật dần; nếu stream không đạt guard nhập vai thì thay bằng fallback nội bộ an toàn.
  - TTS chạy bằng `ThreadPoolExecutor` nền, lưu `Future` trong session message. Text và citation hiện trước; audio xuất hiện khi job xong. Không block UI vì TTS.
  - UI vẫn chỉ hiển thị `Âm thanh nhập vai`, không lộ provider/model TTS.
- Đã sửa `quang_trung_web/llm_provider.py`:
  - Thêm `stream_character_answer_chunks()` gọi Gemini `streamGenerateContent` dạng SSE.
  - Thêm `clean_generated_answer()` dùng chung cho stream/non-stream để ép ngôi thứ nhất, lọc thuật ngữ kỹ thuật và tự gọi tên nhân vật.
  - Prompt được siết lại: context là ký ức được gợi lại, không phải tài liệu để đọc; câu hỏi tư tưởng/chiến lược phải trả lời trực tiếp, không đẩy người dùng hỏi lại.
- Đã sửa `quang_trung_web/rag_core.py`:
  - Thêm intent `ideology`, `military_doctrine`, `life_milestone`.
  - Query rewriting theo từng nhân vật: Võ Nguyên Giáp -> chiến tranh nhân dân/đánh chắc tiến chắc; Hồ Chí Minh -> độc lập tự do/dân là gốc/1911; Nguyễn Trãi -> nhân nghĩa/yên dân/mưu phạt tâm công; Trần Hưng Đạo -> khoan thư sức dân/Hịch tướng sĩ/Bạch Đằng.
  - Thêm `source_tier` và `source_quality_score` runtime, trust boost, source diversification, giảm Tier 4 khi có nguồn Tier 1/2.
  - Rerank cộng điểm cho chunk chứa đúng năm trong câu hỏi và anchor mạnh hơn cho Điện Biên Phủ, chiến tranh nhân dân, Ngọc Hồi - Đống Đa.
  - Fallback multi-character đổi từ câu chung “Câu hỏi ấy còn rộng...” sang persona-specific answer. Câu tư tưởng của Hồ Chí Minh, Nguyễn Trãi, Võ Nguyên Giáp, Trần Hưng Đạo trả lời trực tiếp bằng vai.
  - Post-process fact chuyển self-name sang ngôi thứ nhất; đã xử lý lỗi “người thanh niên Bác (lấy tên Bác)” thành câu tự nhiên hơn.
- Đã sửa `quang_trung_web/tts_provider.py`:
  - Thêm interface `TTSProvider` và `GoogleCloudTTSProvider` để sau này có thể thay provider theo nhân vật mà không phá UI.
  - Tăng khác biệt Hồ Chí Minh thành `pitch="+1.5st"`, giữ các profile SSML khác như trước.
  - Error message TTS trong provider đã trung tính, không lộ tên provider/model lên UI.
- Đã bổ sung metadata `source_tier` và `source_quality_score` vào 5 JSONL dataset:
  - `quang_trung_dataset/quang_trung_knowledge.jsonl`
  - `ho_chi_minh_dataset/ho_chi_minh_knowledge.jsonl`
  - `tran_hung_dao_dataset/tran_hung_dao_knowledge.jsonl`
  - `nguyen_trai_dataset/nguyen_trai_knowledge.jsonl`
  - `vo_nguyen_giap_dataset/vo_nguyen_giap_knowledge.jsonl`
- Đã cập nhật script build/validate:
  - `build_dataset.py` và `build_multi_character_datasets.py` sinh `source_tier/source_quality_score`.
  - `validate_dataset.py` và `validate_multi_character.py` bắt buộc kiểm tra hai field này.
  - `smoke_test.py` có regression cho persona tự nhiên: Võ Nguyên Giáp không tự gọi tên mình, Hồ Chí Minh không trả lời “câu hỏi còn rộng”, Nguyễn Trãi trả lời trực tiếp về nhân nghĩa.
- Kiểm thử local đã chạy ngày 2026-06-08:
  - `python -m py_compile ...` cho app/rag/llm/tts/smoke/validators/build scripts -> pass.
  - `python quang_trung_dataset/validate_dataset.py` -> pass 100 chunks.
  - `python quang_trung_dataset/validate_multi_character.py` -> pass 5 nhân vật.
  - `cd quang_trung_web; .\.venv\Scripts\python.exe .\smoke_test.py` -> pass.
- Lưu ý còn lại: dataset nguồn của 4 nhân vật vẫn cần một đợt bổ sung học thuật riêng để tăng Tier 1 từ các nguồn như `Đại Việt sử ký toàn thư`, `Khâm định Việt sử thông giám cương mục`, Hồ Chí Minh toàn tập, Cổng Bộ Quốc phòng/Quân đội nhân dân. Lượt này mới thêm metadata/rerank và sửa runtime, chưa thay toàn bộ corpus.
- Khi deploy production: chỉ `git pull` trong `/home/ubuntu/history-ontology`, cài dependency nếu requirements đổi, restart `history-ontology.service`. Không sửa Nginx/PetHub, không mở port 8501, không cat/in `.env`.

## Chuyển production khỏi Streamlit sang FastAPI + Next.js ngày 2026-06-08

- User quyết định thay trực tiếp production vì Streamlit còn lag khi mở trang/chuyển nhân vật và có nguy cơ state stale do cơ chế rerun/file watcher.
- Đã thêm kiến trúc mới:
  - `backend/`: FastAPI API, preload 5 nhân vật khi startup, endpoint `GET /api/health`, `GET /api/characters`, `POST /api/chat/stream` SSE, `POST /api/tts`.
  - `frontend/`: Next.js App Router + TypeScript + Zustand, UI Neo Kinpaku, SSE client, audio gọi sau `final`, không lộ provider/model TTS.
  - `deploy/systemd/history-ontology-api.service`: FastAPI nghe `127.0.0.1:8601`.
  - `deploy/systemd/history-ontology-web.service`: Next.js nghe `172.19.0.1:8501` để giữ Nginx/PetHub hiện tại.
- `quang_trung_web/` không bị xóa; giờ là shared RAG runtime + legacy Streamlit rollback. Nếu service mới lỗi, rollback:
  - `sudo systemctl stop history-ontology-web.service history-ontology-api.service`
  - `sudo systemctl start history-ontology.service`
- Đã vá lõi RAG dùng chung:
  - `rag_core.py` dùng `cached_embedding_model()` bằng `lru_cache`, giảm load embedding model lặp lại giữa các retriever.
  - Thêm intent/hàm xử lý `private_life_sensitive`; câu `BÁC CÓ VỢ KHÔNG` trả lời thận trọng, không còn fallback khẩu hiệu `Việc gì có lợi cho dân...`.
  - Thêm nhận diện nhầm lẫn `Nguyễn Huệ`/`Quang Trung`; câu `ông với Nguyễn Huệ là anh em à` trả lời rõ Nguyễn Huệ là tên của ta, không phải anh em.
- Đã thêm `source_manifest.json` để ghi chính sách Tier 1-4 và các intent còn yếu cho từng nhân vật. Manifest là định hướng data quality, không chứa secret.
- Kiểm thử local đã chạy trước deploy:
  - `python -m py_compile backend\main.py backend\smoke_test.py quang_trung_web\rag_core.py quang_trung_web\llm_provider.py quang_trung_web\tts_provider.py quang_trung_web\character_registry.py` -> pass.
  - `python quang_trung_dataset\validate_dataset.py` -> pass.
  - `python quang_trung_dataset\validate_multi_character.py` -> pass.
  - `python backend\smoke_test.py` -> pass, gồm các regression: Nguyễn Huệ/Quang Trung, đời tư Hồ Chí Minh, Võ Nguyên Giáp không tự gọi tên mình.
  - `cd frontend; npm install; npm run build` -> pass, First Load JS khoảng 108 kB.
  - Playwright local `127.0.0.1:8502`: đổi Quang Trung -> Trần Hưng Đạo -> Hồ Chí Minh reset đúng state; Bạch Đằng trả lời đúng vai; câu đời tư Hồ Chí Minh không còn fallback lặp; UI không hiển thị `Google TTS`/`vi-VN-Neural2-D`.
- Cảnh báo npm: `npm install` báo 2 moderate vulnerabilities. Không chạy `npm audit fix --force` vì có thể nâng major dependency và phá build. Cần xử lý riêng nếu muốn hardening sau production.
- Quy trình deploy production mới:
  - `cd /home/ubuntu/history-ontology && git pull --ff-only origin main`
  - `/home/ubuntu/history-ontology/quang_trung_web/.venv/bin/python -m pip install -r backend/requirements.txt`
  - `cd frontend && npm ci && npm run build`
  - `sudo cp /home/ubuntu/history-ontology/deploy/systemd/history-ontology-api.service /etc/systemd/system/`
  - `sudo cp /home/ubuntu/history-ontology/deploy/systemd/history-ontology-web.service /etc/systemd/system/`
  - `sudo systemctl daemon-reload`
  - `sudo systemctl enable --now history-ontology-api.service`
  - `curl -fsS http://127.0.0.1:8601/api/health`
  - `sudo systemctl stop history-ontology.service`
  - `sudo systemctl enable --now history-ontology-web.service`
  - `curl -I http://172.19.0.1:8501`
  - kiểm tra `https://history-simulation-ai.online/` và `https://pethubvn.store/`.
- Không push/cat `.env`, API key, SSH key, `.rag_index`, `.venv`, cache, log, `.next`, `node_modules`.

## Deploy production FastAPI + Next.js hoàn tất ngày 2026-06-08

- Commit production đã deploy: `9f6c107` (`Replace Streamlit production with FastAPI Next stack`).
- Server `/home/ubuntu/history-ontology` đã `git pull --ff-only origin main`, cài `backend/requirements.txt`, chạy validate/smoke và build Next.js.
- Service mới:
  - `history-ontology-api.service`: active, FastAPI nghe `127.0.0.1:8601`, health `{"ok": true, "runtime": "fastapi", "characters_loaded": [...]}`.
  - `history-ontology-web.service`: active, Next.js nghe `172.19.0.1:8501`, log báo `Ready in 360ms`.
  - `history-ontology.service`: inactive, giữ làm rollback Streamlit.
- Acceptance checks sau deploy:
  - `curl -fsS http://127.0.0.1:8601/api/health` -> pass.
  - `curl -I http://172.19.0.1:8501` -> `HTTP/1.1 200 OK`, header `X-Powered-By: Next.js`.
  - `curl -I -H 'Host: history-simulation-ai.online' http://127.0.0.1` -> `HTTP/1.1 200 OK`, không redirect sang PetHub.
  - `https://history-simulation-ai.online/` -> `HTTP/2 200`, Cloudflare phục vụ app Next.js.
  - `https://pethubvn.store/` -> `HTTP/2 200`, không bị ảnh hưởng.
  - Đo nhanh trên VPS: History `time_total≈0.058s`, PetHub `time_total≈0.056s`.
- Browser production bằng Playwright:
  - Load app mới thấy selectbox đủ 5 nhân vật.
  - Câu `ông với Nguyễn Huệ là anh em à` trả lời đúng: Nguyễn Huệ là tên của ta, không phải anh em.
  - Audio xuất hiện nhưng UI chỉ hiển thị `Âm thanh nhập vai`, không lộ provider/model TTS.
  - Đổi từ Quang Trung sang Hồ Chí Minh reset sạch chat/audio/portrait, không stale state.
- Cảnh báo còn lại:
  - FastAPI startup lần đầu khoảng 15 giây vì preload embedding/RAG cho 5 nhân vật; runtime sau warm nhanh.
  - Log API có cảnh báo HF Hub unauthenticated; không ảnh hưởng chạy hiện tại nhưng có thể đặt `HF_TOKEN` sau nếu muốn tải model nhanh/ổn định hơn.
  - `npm ci` báo 2 moderate vulnerabilities; chưa chạy `npm audit fix --force` để tránh phá dependency trước production.

## Nâng cấp asset state machine Quang Trung ngày 2026-06-08

- User cung cấp bộ asset Quang Trung mới trong `C:\Users\ADMIN\Downloads\Research MLN111\Asset Quang Trung` và yêu cầu AI tự phán đoán asset theo câu hỏi/câu trả lời, không đổi máy móc.
- Đã copy bộ asset vào runtime repo tại `quang_trung_web/assets/quang_trung/`:
  - portrait tĩnh 1254x1254: `idle.png`, `talking.png`, `thinking.png`, `confused.png`, `happy.png`, `angry.png`, `angry_2.png`, `sad.png`;
  - sprite sheet 5x5: `Quang Trung-hero_thinking.png`, `Quang Trung-attack.png` (file nguồn hiện là 1280x1280, frontend scale vào khung vuông ổn định).
- `backend/main.py` đã thêm visual classifier nhẹ và SSE contract mới:
  - `start` gửi `visual.phase=thinking`, `motion=thinking` để frontend chạy sprite suy nghĩ khi đang gợi ký ức;
  - `stream_start` gửi `intent/emotion/visual` sau retrieval, trước token;
  - `final` gửi lại `visual` theo câu trả lời cuối.
- Logic visual hiện ưu tiên:
  - câu chiến trận/quân Thanh/quân Xiêm/ngoại xâm/Ngọc Hồi/Đống Đa/Rạch Gầm -> `intent=battle_detail`, motion `attack` cho Quang Trung, emotion `angry` hoặc `happy`;
  - câu sai thời đại/guardrail -> `confused`;
  - dân lầm than/mất mát/loạn lạc -> `sad`;
  - tư tưởng/nhân nghĩa/độc lập -> `thinking`;
  - smalltalk/identity -> `idle` hoặc `happy`.
- `frontend/components/CharacterViewer.tsx` mới xử lý:
  - render portrait tĩnh theo `visual.emotion`;
  - render sprite sheet 5 cột x 5 hàng bằng background-position, `thinking` loop và `attack` play once;
  - khi audio phát, avatar luân phiên `talking.png` với emotion nền để tạo cảm giác khẩu hình.
- `frontend/lib/store.ts`, `frontend/types.ts`, `frontend/lib/api.ts`, `frontend/app/page.tsx` đã thêm `CharacterVisual`, `setVisual`, `completeVisualMotion`, `beginSpeaking/endSpeaking` và handler `stream_start`.
- Đã sửa lỗi asset bên phải không đi cùng cuộc trò chuyện: right rail trong Next.js hiện bọc bằng sticky container `sticky top-8 h-[calc(100vh-4rem)] overflow-y-auto`; kiểm tra DOM local cho thấy top giữ 32px trước/sau khi cuộn.
- Kiểm thử đã chạy:
  - `python -m py_compile backend\main.py backend\smoke_test.py` -> pass;
  - `python backend\smoke_test.py` -> pass, có regression Quang Trung battle phải có visual `motion=attack`;
  - `cd frontend; npm run build` -> pass;
  - Playwright local `127.0.0.1:8502`: ảnh `/assets/quang_trung/idle.png` load xong, right rail sticky, câu `vua kể trận đánh khiến vua hãnh diện nhất đi` chuyển visual về `angry_2.png` sau attack.
- Khi deploy production: cần `git pull`, build lại frontend, restart cả `history-ontology-api.service` và `history-ontology-web.service` vì thay cả backend SSE contract lẫn frontend runtime. Không cần sửa Nginx/PetHub và không mở public port mới.

## Deploy asset state machine Quang Trung hoàn tất ngày 2026-06-08

- Commit code/assets đã push và deploy: `6eb92ab` (`Add Quang Trung visual state machine`).
- Production `/home/ubuntu/history-ontology` đã `git pull --ff-only origin main`, `python -m py_compile backend/main.py backend/smoke_test.py`, `cd frontend && npm run build`, restart `history-ontology-api.service` và `history-ontology-web.service`.
- Acceptance checks sau deploy:
  - FastAPI health `http://127.0.0.1:8601/api/health` trả `ok=true`, đủ 5 nhân vật, `llm_configured=true`.
  - Next local `http://172.19.0.1:8501` trả `HTTP/1.1 200 OK`.
  - Nginx host-header `history-simulation-ai.online` trả `HTTP/1.1 200 OK`.
  - `https://history-simulation-ai.online/` trả `HTTP/2 200`.
  - `https://pethubvn.store/` vẫn trả `HTTP/2 200`; không đụng Nginx/PetHub.
- Browser production bằng Playwright:
  - asset mới load từ `/assets/quang_trung/idle.png`, right rail `position: sticky`, `top=32px`;
  - câu `vua kể trận đánh khiến vua hãnh diện nhất đi` trả Ngọc Hồi - Đống Đa/Rạch Gầm - Xoài Mút;
  - khi audio phát, avatar chuyển sang `talking.png`;
  - sau `window.scrollTo(...)`, right rail vẫn giữ top 32px, asset đi cùng cuộc trò chuyện.
- Production repo còn hai file untracked trong `deploy/` do cấu hình Nginx trước đó: `deploy/apply-history-nginx.sh`, `deploy/history-simulation-ai.online.conf`; để nguyên, không commit từ VPS nếu chưa quyết định chuẩn hóa deploy scripts.

## Hotfix Simulacra RAG và animation ngày 2026-06-08

- Root cause user thấy câu trả lời vẫn như cũ: `rag_core.py` nhận nhầm các câu có tiền tố `chào`, `cho tôi biết`, `tôi hỏi` thành smalltalk trước retrieval. Vì vậy câu có nội dung thật như `chao vua, vua hay cho toi biet ve tran danh ngoc hoi, dong da di` bị chặn trước khi hybrid RAG/query rewrite chạy và trả fallback `Ta đang nghe...`.
- Đã thêm `has_substantive_historical_anchor()` và `is_pure_smalltalk_query()`:
  - chỉ chào hỏi thuần túy mới đi vào conversation fallback;
  - câu có trận đánh, nhân vật, tư tưởng, địa danh, niên hiệu, tên riêng hoặc intent lịch sử sẽ đi qua retrieval/Gemini.
- Đã mở rộng identity/self-name confusion:
  - câu `ông với Nguyễn Huệ là gì của nhau` hoặc `ông với Nguyễn Huệ là anh em à` được xử lý trực tiếp;
  - trả lời rõ Nguyễn Huệ là tên người, Quang Trung là niên hiệu, không phải hai người hay anh em.
- Đã tăng chất lượng câu trả lời:
  - `llm_provider.py` bỏ giới hạn `Trả lời 1-2 đoạn ngắn`;
  - prompt mới yêu cầu câu lịch sử/trận đánh/tư tưởng/thân thế trả 2-4 đoạn, tối thiểu 5 câu, có nguyên nhân, diễn biến, ý nghĩa;
  - `maxOutputTokens` tăng từ 900 lên 1400.
- Đã sửa animation sync:
  - audio của các tin nhắn cũ không còn điều khiển asset hiện tại; chỉ audio của assistant message mới nhất mới gọi `beginSpeaking/endSpeaking`;
  - nếu `attack` đang chạy, audio không được hủy motion; sprite đánh xong mới chuyển sang talking;
  - sprite `attack` giữ frame cuối thêm 560ms để dừng bớt gắt.
- Đã thêm visual intent riêng `identity_confusion` trong FastAPI để câu nhầm tên Quang Trung/Nguyễn Huệ dùng asset `confused`, không bật attack.
- Regression tests đã thêm vào `backend/smoke_test.py`:
  - `chao vua, vua hay cho toi biet ve tran danh ngoc hoi , dong da di` không được trả `Ta đang nghe`, phải nhắc Ngọc Hồi/Đống Đa, tối thiểu 80 từ và visual `attack`;
  - `ông với nguyễn huệ là gì của nhau` phải có `tên của ta`, `không phải`, visual intent `identity_confusion`;
  - battle reflection phải tối thiểu 80 từ.
- Kiểm thử local đã chạy:
  - `python -m py_compile backend\main.py backend\smoke_test.py quang_trung_web\rag_core.py quang_trung_web\llm_provider.py` -> pass;
  - `python backend\smoke_test.py` -> pass;
  - `cd frontend && npm run build` -> pass.
- Khi deploy bản này: pull commit mới, build frontend, restart `history-ontology-api.service` và `history-ontology-web.service`. Không cần sửa Nginx/PetHub, không mở port mới.
