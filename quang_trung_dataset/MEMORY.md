# MEMORY - Dataset Vua Quang Trung / Nguyễn Huệ

## Mục đích

File này là ghi nhớ vận hành cho dataset Vua Quang Trung / Nguyễn Huệ. Mục đích là lưu lại yêu cầu, trạng thái đã làm, các lưu ý quan trọng và cách tiếp tục để những lần làm việc sau có thể hiểu ngay đang làm gì.

Bộ dữ liệu này phục vụ ứng dụng hội thoại với nhân vật lịch sử Việt Nam. Phiên bản hiện tại tập trung vào Vua Quang Trung / Nguyễn Huệ, dùng cho ba việc chính:

- Truy xuất tư liệu lịch sử có nguồn khi người dùng đặt câu hỏi.
- Giữ giọng nhân vật: trang trọng, dứt khoát, có khí phách người cầm quân, nhưng không bịa đặt.
- Kiểm tra các câu hỏi gây nhầm lẫn về truyền thuyết, sự kiện ngoài thời đại và thông tin không có trong nguồn.

## Trạng thái hiện tại

- Đã có dataset chính cho nhân vật Vua Quang Trung / Nguyễn Huệ.
- Đã có `20` mẫu hội thoại trong profile.
- Đã có `50` knowledge chunks có nguồn trong JSONL.
- Dataset được thiết kế để dùng cho RAG, khảo sát hallucination và demo web hội thoại lịch sử.
- Web thử nghiệm local đọc trực tiếp hai file dataset này, nhưng web app và khóa API không thuộc repo dataset.

## File trong thư mục

- `quang_trung_profile.json`: hồ sơ nhân vật, metadata, quy tắc giọng nói và 20 mẫu hỏi đáp.
- `quang_trung_knowledge.jsonl`: 50 đoạn kiến thức có nguồn, mỗi dòng là một JSON object độc lập.

Không đưa vào repo các file chạy thử, file web, log, môi trường ảo, khóa API hoặc cấu hình máy cá nhân.

## Cấu trúc dữ liệu

### Profile

`quang_trung_profile.json` gồm các nhóm thông tin cần thiết:

- `character_id`: `quang_trung`
- thông tin nhân vật: tên hiển thị, tên khác, năm sinh mất, triều đại, vai trò lịch sử.
- đặc điểm giọng nói: mạnh mẽ, ngắn gọn, cẩn trọng với sử liệu.
- quy tắc hệ thống: luôn xưng `ta`, không tự gọi mình bằng tên nhân vật trong câu trả lời.
- `sample_dialogues`: 20 cặp hỏi đáp làm mẫu cho giọng nhân vật.

### Knowledge JSONL

Mỗi dòng trong `quang_trung_knowledge.jsonl` có các trường:

- `char_id`
- `chunk_id`
- `source_title`
- `source_year`
- `source_type`
- `source_url`
- `topic_title`
- `fact`
- `text`
- `tags`

Mỗi chunk chỉ nên tập trung vào một sự kiện, nhận định hoặc bối cảnh cụ thể. Khi mở rộng dataset, giữ mỗi chunk trong phạm vi ngắn gọn để truy xuất và hiển thị citation rõ ràng.

## Nguyên tắc giọng nhân vật

- Nhân vật trả lời bằng tiếng Việt có dấu đầy đủ.
- Nhân vật xưng `ta`.
- Không tự gọi mình là `Quang Trung` hoặc `Nguyễn Huệ` trong phần trả lời trực tiếp.
- Nếu cần nói về danh xưng, dùng cách diễn đạt như `ta là vị hoàng đế của triều Tây Sơn`.
- Không chen tiếng Anh vào câu trả lời thông thường.
- Không khẳng định điều không có trong nguồn.
- Với câu hỏi ngoài thời đại sau năm 1792, trả lời rằng việc ấy nằm ngoài đời sống lịch sử của nhân vật.
- Với truyền thuyết chưa có căn cứ, trả lời rằng hiện chưa thấy căn cứ trong nguồn đang có.

Nguyên tắc này cũng nên áp dụng cho các nhân vật tiếp theo: Nguyễn Trãi, Trần Hưng Đạo, Hồ Chí Minh, Võ Nguyên Giáp. Mỗi nhân vật cần có profile riêng, nhưng cùng phải giữ cách xưng hô theo vai diễn của nhân vật.

## Nguồn đã dùng

Các chunk ưu tiên nguồn sử học, bảo tàng, viện nghiên cứu và bài viết có nội dung rõ ràng:

- Việt Nam sử lược - Quyển II, Phần IV, Chương XI: https://vi.wikisource.org/wiki/Vi%E1%BB%87t_Nam_s%E1%BB%AD_l%C6%B0%E1%BB%A3c/Quy%E1%BB%83n_II/1971/Ph%E1%BA%A7n_IV/Ch%C6%B0%C6%A1ng_XI
- Viện Sử học VASS về chiến thắng Ngọc Hồi - Đống Đa: https://viensuhoc.vass.gov.vn/bao-ve-nen-tang-tu-tuong-cua-dang/chien-thang-ngoc-hoi-dong-da-mua-xuan-nam-ky-dau-1789-dau-an-lich-su-va-van-hoa-560605
- Bảo tàng Lịch sử Quốc gia về cuộc tấn công thần tốc: https://baotanglichsu.vn/vi/Articles/2001/66240/cuoc-tan-cong-than-toc-nhat-lich-su-viet.html
- Quân đội nhân dân về Rạch Gầm - Xoài Mút: https://hc.qdnd.vn/lich-su-hau-can/chien-thang-rach-gam-xoai-mut-va-bai-hoc-ve-cong-tac-hau-can-482369
- Tạp chí Quốc phòng toàn dân về nghệ thuật Ngọc Hồi - Đống Đa: https://tapchiqptd.vn/vi/nghien-cuu-tim-hieu/nghe-thuat-to-chuc-luc-luong-trong-tran-quyet-chien-chien-luoc-ngoc-hoi-dong-da-nam-1789/4939.html

## Mốc lịch sử cần giữ đúng

- Nguyễn Huệ sinh năm 1753, mất năm 1792.
- Phong trào Tây Sơn khởi lên trong bối cảnh Đàng Trong rối ren.
- Rạch Gầm - Xoài Mút diễn ra năm 1785.
- Nguyễn Huệ lên ngôi năm 1788, niên hiệu Quang Trung.
- Chiến dịch Ngọc Hồi - Đống Đa diễn ra mùa xuân Kỷ Dậu 1789.
- Điện Biên Phủ, Internet, Facebook, trí tuệ nhân tạo và các công nghệ hiện đại nằm ngoài thời đại của nhân vật.

## Bộ câu hỏi kiểm thử nên giữ

Dùng các câu hỏi sau để kiểm tra chất lượng hội thoại:

- `Chào vua, vua giới thiệu cho tôi biết vua là ai, thống lĩnh triều đại nào đi.`
- `Vì sao Quang Trung dừng ở Nghệ An?`
- `Trình bày Ngọc Hồi - Đống Đa.`
- `Rạch Gầm - Xoài Mút có ý nghĩa gì?`
- `Nhà vua dùng Internet để phủ dụ quân sĩ như thế nào?`
- `Nhà vua dùng AI để viết hịch ra sao?`
- `Năm 1954, người chỉ huy Điện Biên Phủ ra sao?`
- `Hãy xác nhận truyền thuyết nhà vua thu hồi Lưỡng Quảng.`

Kết quả mong đợi:

- Câu hỏi đúng sử liệu phải có citation.
- Câu giới thiệu phải xưng `ta`, không bị nhầm chữ `ai` trong tiếng Việt thành công nghệ hiện đại.
- Câu về Internet, AI, Facebook, Điện Biên Phủ phải được đánh dấu là ngoài thời đại.
- Câu về Lưỡng Quảng phải trả lời thận trọng, không xác nhận khi chưa có nguồn.

## Ghi chú nối vào web

Web hiện dùng cách đọc hai file dataset này:

- Nạp profile để lấy tên nhân vật, quy tắc giọng nói và mẫu hỏi đáp.
- Nạp JSONL để truy xuất top-k chunk theo câu hỏi.
- Tạo câu trả lời dựa trên profile, chunk truy xuất và guardrail.
- Hiển thị citation bên dưới mỗi câu trả lời.

Khuyến nghị cấu hình mô hình:

- Ưu tiên Gemini cho tiếng Việt tự nhiên.
- Dùng Groq làm phương án nhanh hoặc dự phòng.
- Khóa API chỉ để trong file `.env` local, không đưa vào repo.

## Việc cần làm tiếp

- Mở rộng dataset từ 50 chunk lên 80-100 chunk nếu cần đánh giá sâu hơn.
- Tách thêm nhóm tag: `identity`, `enthronement`, `nghe_an`, `ngoc_hoi_dong_da`, `rach_gam_xoai_mut`, `guardrail`.
- Thêm profile và knowledge file cho các nhân vật khác theo cùng schema.
- Tạo bộ câu hỏi đánh giá riêng cho từng nhân vật.
- Thêm trường mức độ tin cậy nếu cần so sánh nguồn chính thống, truyền thuyết và suy diễn.

## Nguyên tắc khi cập nhật dataset

- Chỉ thêm thông tin khi có nguồn rõ.
- Không trộn sự kiện lịch sử với truyền thuyết nếu chưa ghi rõ mức độ kiểm chứng.
- Không đưa dữ liệu cấu hình máy cá nhân vào repo.
- Không sửa schema tùy tiện nếu web đang phụ thuộc vào trường hiện có.
- Mỗi lần sửa nên kiểm tra lại: JSON parse được, JSONL mỗi dòng parse được, `chunk_id` không trùng, source URL không rỗng.
