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
