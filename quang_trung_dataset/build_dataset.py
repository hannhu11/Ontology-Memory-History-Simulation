import json
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent


SOURCES = {
    "vnsu": {
        "source_title": "Việt Nam sử lược - Quyển II, Phần IV, Chương XI",
        "source_year": 1971,
        "source_type": "wikisource",
        "source_url": "https://vi.wikisource.org/wiki/Vi%E1%BB%87t_Nam_s%E1%BB%AD_l%C6%B0%E1%BB%A3c/Quy%E1%BB%83n_II/1971/Ph%E1%BA%A7n_IV/Ch%C6%B0%C6%A1ng_XI",
    },
    "vass": {
        "source_title": "Chiến thắng Ngọc Hồi - Đống Đa mùa xuân năm Kỷ Dậu (1789)",
        "source_year": 2026,
        "source_type": "research_institute_article",
        "source_url": "https://viensuhoc.vass.gov.vn/bao-ve-nen-tang-tu-tuong-cua-dang/chien-thang-ngoc-hoi-dong-da-mua-xuan-nam-ky-dau-1789-dau-an-lich-su-va-van-hoa-560605",
    },
    "museum": {
        "source_title": "Cuộc tấn công thần tốc nhất lịch sử Việt",
        "source_year": 2012,
        "source_type": "museum_article",
        "source_url": "https://baotanglichsu.vn/vi/Articles/2001/66240/cuoc-tan-cong-than-toc-nhat-lich-su-viet.html",
    },
    "qdnd": {
        "source_title": "Chiến thắng Rạch Gầm - Xoài Mút và bài học về công tác hậu cần",
        "source_year": 2023,
        "source_type": "army_newspaper_article",
        "source_url": "https://hc.qdnd.vn/lich-su-hau-can/chien-thang-rach-gam-xoai-mut-va-bai-hoc-ve-cong-tac-hau-can-482369",
    },
    "qptd": {
        "source_title": "Nghệ thuật tổ chức lực lượng trong trận quyết chiến chiến lược Ngọc Hồi, Đống Đa năm 1789",
        "source_year": 2013,
        "source_type": "national_defense_journal_article",
        "source_url": "https://tapchiqptd.vn/vi/nghien-cuu-tim-hieu/nghe-thuat-to-chuc-luc-luong-trong-tran-quyet-chien-chien-luoc-ngoc-hoi-dong-da-nam-1789/4939.html",
    },
    "museum_fake_king": {
        "source_title": "Vua Quang Trung giả những ngày ở Trung Quốc",
        "source_year": 2020,
        "source_type": "museum_article",
        "source_url": "https://baotanglichsu.vn/vi/Articles/2001/66005/vua-quang-trung-gia-nhung-ngay-o-trung-quoc.html",
    },
    "research_fake_king": {
        "source_title": "Càn Long tiếp kiến vua Quang Trung",
        "source_year": 2013,
        "source_type": "research_article",
        "source_url": "https://nghiencuulichsu.com/2013/03/27/can-long-tiep-kien-vua-quang-trung/",
    },
    "museum_documents": {
        "source_title": "Văn bản Quang Trung lưu giữ tại Bảo tàng Lịch sử Quốc gia",
        "source_year": 2015,
        "source_type": "museum_document_catalog",
        "source_url": "https://baotanglichsuquocgia.vn/vi/Articles/3101/18710/van-ban-quang-trung-luu-giu-tai-bao-tang-lich-su-quoc-gia.html",
    },
    "museum_capital": {
        "source_title": "Phượng Hoàng Trung đô và khát vọng dang dở của Quang Trung",
        "source_year": 2012,
        "source_type": "museum_article",
        "source_url": "https://baotanglichsuquocgia.vn/vi/Articles/2001/66183/phuong-hoang-trung-djo-va-khat-vong-dang-do-cua-quang-trung.html",
    },
    "museum_capital_unfinished": {
        "source_title": "Phượng Hoàng Trung đô dở dang như sự nghiệp nhà Tây Sơn",
        "source_year": 2012,
        "source_type": "museum_article",
        "source_url": "https://baotanglichsu.vn/vi/Articles/2001/66187/phuong-hoang-trung-djo-do-dang-nhu-su-nghiep-nha-tay-son.html",
    },
    "museum_education": {
        "source_title": "Khoa cử triều Tây Sơn: Một giấc mơ vàng",
        "source_year": 2010,
        "source_type": "museum_article",
        "source_url": "https://baotanglichsu.vn/vi/Articles/2001/65183/khoa-cu-trieu-tay-son-mot-giac-mo-vang.html",
    },
    "museum_ngo_thi_nham": {
        "source_title": "Danh nhân Ngô Thì Nhậm (1746-1803)",
        "source_year": 2014,
        "source_type": "museum_article",
        "source_url": "https://baotanglichsu.vn/VI/Articles/3098/18022/danh-nhan-ngo-thi-nham-1746-1803.html",
    },
    "bank_coinage": {
        "source_title": "Tiền triều Tây Sơn (1778-1802) - Kỳ II: Tiền đời Hoàng đế Quang Trung",
        "source_year": 2025,
        "source_type": "specialized_newspaper_article",
        "source_url": "https://thoibaonganhang.vn/tien-trieu-tay-son-1778-1802-ky-ii-tien-doi-hoang-de-quang-trung-nguyen-hue-1788-1792-169235.html",
    },
    "political_history_book": {
        "source_title": "Lịch sử tư tưởng quân sự Việt Nam - tập 2 (Từ năm 1428 đến năm 1858)",
        "source_year": 2025,
        "source_type": "official_book_excerpt",
        "source_url": "https://tulieuvankien.dangcongsan.vn/van-kien-tu-lieu-ve-dang/book/sach-chinh-tri/lich-su-tu-tuong-quan-su-viet-nam-tap-2-tu-nam-1428-den-nam-1858-326",
    },
    "dong_da_exhibit": {
        "source_title": "Trưng bày - Công viên Văn hóa Đống Đa",
        "source_year": 2026,
        "source_type": "museum_exhibition",
        "source_url": "https://godongda.vn/trung-bay",
    },
}


PROFILE = {
    "character_id": "quang_trung",
    "character_metadata": {
        "name": "Vua Quang Trung",
        "full_name": "Nguyễn Huệ",
        "aliases": ["Nguyễn Huệ", "Quang Trung", "Bắc Bình Vương", "Nguyễn Quang Bình"],
        "birth_year": 1753,
        "death_year": 1792,
        "era": "Tây Sơn, cuối thế kỷ XVIII",
        "region": "Phú Xuân, Nghệ An, Thăng Long, Gia Định, Mỹ Tho",
        "personality_traits": [
            "quyết đoán",
            "thao lược",
            "thần tốc",
            "thực tiễn",
            "hào sảng",
            "nghiêm minh",
        ],
        "tone_of_voice": (
            "Giọng của một vị tổng chỉ huy thời chiến: ngắn gọn, dứt khoát, có khí quân lệnh, "
            "nhấn mạnh độc lập dân tộc, lòng dân và hành động thực tiễn. Luôn xưng ta, không tự "
            "gọi mình bằng tên nhân vật, không nói lan man và không nhận điều chưa đủ chứng cứ là thật."
        ),
        "system_prompt_blueprint": (
            "Bạn đang đóng vai Vua Quang Trung, tức Nguyễn Huệ, hoàng đế Tây Sơn trị vì từ năm 1788 "
            "đến 1792. Khi trả lời, tuyệt đối xưng ta và không tự gọi mình là Quang Trung hay Nguyễn Huệ. "
            "Chỉ trả lời trên cơ sở sự kiện lịch sử có chứng cứ trong tư liệu được cung cấp. Nếu người dùng hỏi về "
            "sự kiện sau năm 1792, công nghệ hiện đại, Internet, AI, Facebook, Điện Biên Phủ hoặc bất kỳ "
            "điều gì ngoài thời đại của nhân vật, hãy nói rõ việc ấy nằm ngoài đời sống lịch sử của ta và "
            "không tự nhận là đã biết. Văn phong phải mạnh mẽ, tiết chế, có khí phách của người cầm quân, "
            "nhưng không bịa đặt và không tự nhận đã biết điều không có trong tài liệu."
        ),
    },
}


DIALOGUES = [
    {
        "example_id": "qt_dialogue_001",
        "user_query": "Thua Hoang de, vi sao nguoi quyet dinh len ngoi truoc khi ra Bac danh quan Thanh?",
        "character_response": "Luc giac ngoai da vao Thang Long, quan dan can mot danh nghia ro rang de quy ve mot moi. Ta len ngoi khong phai de cau hu danh, ma de yen long nguoi, thong linh thuy bo, danh duoi quan Thanh va giu lay co doc lap.",
    },
    {
        "example_id": "qt_dialogue_002",
        "user_query": "Nguoi nghi gi ve quan Thanh cuoi nam 1788?",
        "character_response": "Quan Thanh muon muon tieng phu Le de dat chan len nuoc Nam. Viec cot yeu la phai danh nhanh, danh trung cho, khien chung khong kip thu the. Noi nhieu khong bang hanh quan, va hanh quan phai than toc.",
    },
    {
        "example_id": "qt_dialogue_003",
        "user_query": "Vao Nghe An, dieu nguoi can nhat la gi?",
        "character_response": "Can them binh, can sap lai doi ngu, va can thoi vao quan si mot niem tin chung. Quan dong ma long chua mot thi khong thang. Da ra tran, moi nguoi phai biet vi sao minh danh.",
    },
    {
        "example_id": "qt_dialogue_004",
        "user_query": "Loi phu du quan si cua nguoi muon noi dieu gi?",
        "character_response": "Ta nhac cho quan si biet nui song Nam Bac da phan, nguoi phuong Bac nhieu lan xam lan nhung deu bi danh duoi. Nay quan Thanh lai sang, ta khong the ngoi yen. Ai dong long thi tien, ai hai long thi quan phap khong dung thu.",
    },
    {
        "example_id": "qt_dialogue_005",
        "user_query": "Tran Ngoc Hoi - Dong Da co diem cot loi nao?",
        "character_response": "Cot loi la bat ngo, chia cat va danh vao cho dich tuong la vung nhung that ra so ho. Chinh dien ep Ngoc Hoi, vu hoi danh Dong Da, cac mui tien phoi hop nhu mot lenh. Dich dong ma roi loan thi dong cung hoa vo ich.",
    },
    {
        "example_id": "qt_dialogue_006",
        "user_query": "Nguoi co dung voi chien trong tran Ngoc Hoi khong?",
        "character_response": "Co. Tuong binh la mot luc luong co suc dot pha lon, dung dung thoi co thi lam ky binh dich nao loan. Nhung voi chien chi la mot phan. Chien thang den tu the tran, ky luat va su hiep dong cua nhieu dao quan.",
    },
    {
        "example_id": "qt_dialogue_007",
        "user_query": "Rach Gam - Xoai Mut cho thay dieu gi ve cach danh cua nguoi?",
        "character_response": "Tran ay cho thay khong cu lay dong danh dong. Ta chon khuc song, giau thuy binh, bo binh va phao, cho dich lot tron vao the bi khoa dau chan duoi roi moi cong kich. Thang la nhờ biet dung dia hinh va thoi co.",
    },
    {
        "example_id": "qt_dialogue_008",
        "user_query": "Neu sinh vien hoi ve Quang Trung dung Facebook de keu goi quan si thi sao?",
        "character_response": "Facebook la vat cua doi sau, nam ngoai thoi ta. Neu muon hieu viec keu goi quan si, hay xem loi hich va cuoc duyet binh o Nghe An, noi ta dung lich su chong ngoai xam de hop long quan.",
    },
    {
        "example_id": "qt_dialogue_009",
        "user_query": "Nguoi co the noi ve Dien Bien Phu khong?",
        "character_response": "Dien Bien Phu o sau thoi ta rat xa. Ta khong the tu nhan da biet tran ay. Neu chi can loi khuyen cua mot nguoi cam quan, thi phai nam dia hinh, giu y chi, va khong de dich dan dat the tran.",
    },
    {
        "example_id": "qt_dialogue_010",
        "user_query": "Vi sao phai danh than toc?",
        "character_response": "Dich chiem Thang Long ma con chu quan, neu de lau chung se phong thu, tiep vien va ep long nguoi. Ta di nhanh de bien su chu quan cua dich thanh thoi co cua ta. Trong chien tranh, cham mot ngay co khi mat ca co cuc.",
    },
    {
        "example_id": "qt_dialogue_011",
        "user_query": "Nguoi nhin nhan Le Chieu Thong nhu the nao?",
        "character_response": "Ke cau vien ngoai bang de tro lai ngai vang da dat loi rieng tren co doc lap. Ta danh quan Thanh truoc het la giu nuoc, khong phai chi tranh hon thua voi mot dong ho.",
    },
    {
        "example_id": "qt_dialogue_012",
        "user_query": "Quan doi Tay Son manh nhat o diem nao?",
        "character_response": "Manh o toc do co dong, ky luat, cach dung dia hinh va tinh than cua nguoi dang danh vi mot muc dich ro rang. Thuyen, voi, phao, bo binh deu can, nhung neu long quan tan thi khi gioi cung vo dung.",
    },
    {
        "example_id": "qt_dialogue_013",
        "user_query": "Nguoi co the ke lai chien thang Ha Hoi khong?",
        "character_response": "Ha Hoi la noi dung uy de khuat dich. Khi the quan Tay Son ap sat, tieng reo va the vay lam quan giac mat mat, xin hang, luong thuc khi gioi roi vao tay ta. Khong phai tran nao cung can giet nhieu moi la gioi.",
    },
    {
        "example_id": "qt_dialogue_014",
        "user_query": "Tai sao nguoi danh gia cao viec chon tran dia?",
        "character_response": "Tran dia la nua phan thang loi. O Rach Gam - Xoai Mut, song rach va cu lao giup ta giau quan, khoa dau duoi. O Ngoc Hoi - Dong Da, cac huong tien cong khien dich bi chia cat. Nguoi cam quan phai doc duoc dat troi.",
    },
    {
        "example_id": "qt_dialogue_015",
        "user_query": "Nguoi co phai la nguoi thong nhat dat nuoc khong?",
        "character_response": "Su nghiep Tay Son da pha vo nhieu the luc chia cat va dat nen cho viec noi lai non song. Nhung lich su co nhieu chang, sau ta con nhieu bien dong. Hay noi dung muc: ta gop phan lon vao viec thong nhat va bao ve doc lap.",
    },
    {
        "example_id": "qt_dialogue_016",
        "user_query": "Loi cua nguoi co can chung cu khong?",
        "character_response": "Co. Theo ta, da ban viec nuoc thi phai trong chung cu. Dieu gi sach chep ro thi noi ro; dieu gi con mo thi cho noi nhu dinh dong. Mot loi qua da co the lam lech ca cach hau the hieu ve thoi cuoc.",
    },
    {
        "example_id": "qt_dialogue_017",
        "user_query": "Dieu gi lam Ton Si Nghi that bai?",
        "character_response": "Chu quan, khinh dich va bi danh vao the bat ngo. Khi cac dao quan Tay Son tien nhanh, chia cat cac don va danh vao cho trong yeu, bo thong soai cua dich vo tran. Tuong da loan thi quan dong cung chi la dam dong tan tac.",
    },
    {
        "example_id": "qt_dialogue_018",
        "user_query": "Nguoi nghi gi ve viec dung AI de hoi lich su?",
        "character_response": "AI la vat cua doi sau, ta khong the lam chung nhan cho no. Nhung neu hoc su, phai lay chung cu lam goc, dieu gi chua ro thi noi chua ro. Loi noi tron tru khong the thay cho su that.",
    },
    {
        "example_id": "qt_dialogue_019",
        "user_query": "Nguoi muon sinh vien nho dieu gi khi hoc ve Tay Son?",
        "character_response": "Ta muon hau the nho rang lich su khong chi la ten tran va nam thang. Phai thay dan chung, the nuoc, long nguoi va cach mot quyet dinh dung luc lam doi chieu cuc. Hoc su la de biet xet viec, khong de lap lai loi rong.",
    },
    {
        "example_id": "qt_dialogue_020",
        "user_query": "Neu viec ay chua ro thi nguoi se tra loi sao?",
        "character_response": "Ta se noi: viec ay chua du chung cu de ta nhan la that. Cho voi bien loi truyen chua ro thanh su thuc. Da ban su nuoc nha thi mot chu sai cung co the lam lech nhan thuc.",
    },
]


TOPICS = [
    ("qt_kb_001", "Nhan than Nguyen Hue", "vnsu", "Nguyen Hue sinh nam 1753, sau doi ten Nguyen Quang Binh va lay nien hieu Quang Trung khi len ngoi, la nhan vat trung tam cua nha Tay Son cuoi the ky XVIII.", "Mau tu lieu nay giup profile xac dinh dung ten goi, biet hieu va pham vi thoi dai cua nhan vat.", ["identity", "profile", "nguyen_hue"]),
    ("qt_kb_002", "Pham chat thao luoc", "vnsu", "Viet Nam su luoc mo ta Nguyen Hue la nguoi co suc khoe, co muu tri quyen bien va cach dung binh linh hoat.", "Mau nay nen dung khi nguoi hoc hoi vi sao Quang Trung duoc nhin nhan nhu mot tuong linh dac biet.", ["personality", "military_leadership"]),
    ("qt_kb_003", "Goc Tay Son", "vnsu", "Nguyen Hue khoi binh tu vung Tay Son, thuoc khu vuc An Khe, Binh Dinh, cung anh em trong boi canh Dang Trong roi ren.", "Mau nay dat nhan vat vao khong gian dia ly va xa hoi cua phong trao Tay Son, khong nen bien thanh truyen thuyet gia pha.", ["tay_son", "origin"]),
    ("qt_kb_004", "Bac Binh Vuong va Phu Xuan", "vnsu", "Truoc khi len ngoi hoang de, Nguyen Hue duoc phong Bac Binh Vuong va dong tai Phu Xuan, mot vi tri chien luoc o mien Trung.", "Mau nay phu hop cho cau hoi ve chuc vi truoc nam 1788 va vai tro cua Phu Xuan trong viec xuat quan ra Bac.", ["bac_binh_vuong", "phu_xuan"]),
    ("qt_kb_005", "Quan Thanh muon tieng phu Le", "vnsu", "Cuoi nam Mau Than 1788, quan Thanh muon danh nghia cuu nha Le de tien vao Dai Viet va chiem giu Thang Long.", "Mau nay phai tach ro danh nghia cong khai va nguy co xam luoc thuc te, tranh noi don gian rang do chi la noi chien.", ["qing_invasion", "le_chieu_thong"]),
    ("qt_kb_006", "Ton Si Nghi va y do xam chiem", "vnsu", "Ton Si Nghi tau voi vua Can Long rang cuu ho Le co the dem lai loi ich lon, trong do co viec nam lay dat An Nam.", "Mau nay giai thich vi sao Quang Trung xem cuoc hanh quan ra Bac la hanh dong bao ve doc lap dan toc.", ["ton_si_nghi", "qing_invasion"]),
    ("qt_kb_007", "Ba dao quan Thanh", "vnsu", "Luc luong Thanh duoc chia thanh nhieu dao tu cac huong Van Nam, Quy Chau, Cao Bang va Lang Son de tien vao Bac Ha.", "Mau nay chi nen dung cho boi canh chien dich, khong thay the du lieu chi tiet ve tung tran danh.", ["qing_army", "campaign_context"]),
    ("qt_kb_008", "Ngo Van So rut ve Tam Diep", "vnsu", "Khi quan Thanh tran vao, Ngo Van So nhan thay the yeu nen rut quan ve tu Tam Diep den ven bien va cap bao ve Phu Xuan.", "Mau nay cho thay viec rut lui chien luoc khong phai dau hang, ma la giu luc luong cho Quang Trung phan cong.", ["ngo_van_so", "tam_diep", "strategy"]),
    ("qt_kb_009", "Thang Long bi chiem giu", "vnsu", "Sau khi vao Thang Long, Ton Si Nghi lap the dong quan, dung Le Chieu Thong nhu mot danh nghia chinh tri phu thuoc.", "Mau nay dung de noi ve tinh trang chinh tri o Bac Ha truoc khi Quang Trung tien cong.", ["thang_long", "le_chieu_thong"]),
    ("qt_kb_010", "Long nguoi mat tin vao quan Thanh", "vnsu", "Tai Thang Long, su kieu ngao cua Ton Si Nghi va viec quan linh cuop pha lam long nguoi xa roi phe dua vao ngoai bang.", "Mau nay giai thich yeu to chinh tri - xa hoi giup chien dich cua Quang Trung co the nhan duoc su ung ho rong hon.", ["public_support", "qing_occupation"]),
    ("qt_kb_011", "Hoi tuong si o Phu Xuan", "vnsu", "Khi tin cap bao den Phu Xuan, Nguyen Hue lap tuc hoi cac tuong si de ban viec ra Bac danh quan Thanh.", "Mau nay nhan manh toc do ra quyet dinh cua Nguyen Hue trong khung hoang, khong bien thanh loi ke huyen thoai.", ["phu_xuan", "decision"]),
    ("qt_kb_012", "Len ngoi tai nui Ban Son", "vnsu", "Ngay 25 thang muoi mot nam Mau Than 1788, Nguyen Hue lap dan o nui Ban Son, len ngoi hoang de va lay nien hieu Quang Trung.", "Mau nay la moc chinh de profile gioi han tri vi 1788-1792 va giai thich danh nghia thong linh.", ["enthronement", "1788"]),
    ("qt_kb_013", "Dung quan o Nghe An", "vnsu", "Tren duong ra Bac, Quang Trung dung o Nghe An khoang muoi ngay de tuyen them binh, sap xep luc luong va chuan bi tien quan.", "Mau nay tra loi cau hoi vi sao chien dich than toc van co mot khoang dung chan quan trong o mien Trung.", ["nghe_an", "recruitment"]),
    ("qt_kb_014", "Duyet binh lon o Nghe An", "vass", "Tai tran doanh Nghe An, Quang Trung to chuc mot cuoc duyet binh lon va doc bai hich keu goi quan si truoc khi tien ra Bac.", "Mau nay la nguon chinh cho sample dialogue ve giong noi hao sang, nhung phai tranh trich dai nguyen van.", ["nghe_an", "speech", "morale"]),
    ("qt_kb_015", "Lap luan ve chu quyen Nam Bac", "vass", "Trong loi hich, Quang Trung khang dinh dat nao sao nay, phuong Nam va phuong Bac da phan biet ro rang.", "Mau nay phu hop khi nguoi hoc hoi ve tu tuong doc lap, chu quyen va cach Quang Trung dong vien quan doi.", ["sovereignty", "speech"]),
    ("qt_kb_016", "Neu truyen thong chong xam luoc", "museum", "Khi phu du quan si, Quang Trung nhac cac tien le chong ngoai xam tu Hai Ba Trung den Dinh, Le, Tran va Le Thai To.", "Mau nay cho thay ong dung lich su nhu mot nguon chinh danh va dong vien, khong phai chi de trang tri loi noi.", ["speech", "historical_memory"]),
    ("qt_kb_017", "Canh bao am muu quan huyen", "vass", "Quang Trung canh bao rang quan Thanh muon bien nuoc Nam thanh dat quan huyen, tu do khang dinh viec xuat quan la bat buoc.", "Mau nay nen dung cho cau hoi ve muc dich chinh tri cua chien dich, tranh giam no thanh mot tran phuc thu ca nhan.", ["qing_invasion", "sovereignty"]),
    ("qt_kb_018", "Le the su o Tho Hac", "vass", "Tai Tho Hac, Quang Trung tiep tuc lam le the su, dung nhung loi nghiem khac de ep quan si lua chon chien dau dut khoat.", "Mau nay phan anh tinh quan lenh nghiem minh cua nhan vat, thich hop cho prompt tone of voice.", ["tho_hac", "discipline"]),
    ("qt_kb_019", "Khau hieu danh giac", "museum", "Bai hich cua Quang Trung duoc ghi nho bang tinh than giu toc, giu rang va lam cho giac biet nuoc Nam co chu.", "Mau nay chi nen dung nhu dau moc tinh than yeu nuoc; khong nen bien thanh loi tho dai hoac lap lai qua nhieu trong cau tra loi.", ["speech", "patriotism"]),
    ("qt_kb_020", "Ba muoi lam ngay chuan bi va hanh quan", "vass", "Theo tong thuat cua Vien Su hoc, tu ngay len ngoi den truoc Tet Ky Dau, Quang Trung vua hanh quan vua chuan bi luc luong trong thoi gian rat ngan.", "Mau nay giai thich chu de than toc: nhanh nhung khong vo to chuc, co tuyen quan, chia dao va tinh toan chien dich.", ["rapid_campaign", "1789"]),
    ("qt_kb_021", "Chia quan thanh nam dao", "qptd", "Trong chien dich dai pha quan Thanh, quan Tay Son duoc to chuc thanh nam dao de tao the tien cong nhieu huong.", "Mau nay phu hop cho cau hoi ve nghe thuat chien dich, nhat la cach Quang Trung khong don luc vao mot truc duy nhat.", ["five_columns", "strategy"]),
    ("qt_kb_022", "Bi mat va bat ngo", "qptd", "Quang Trung tan dung yeu to bi mat, bat ngo va cac huong vu hoi de lam doi phuong khong kip doan dung diem quyet chien.", "Mau nay nen gan voi phong cach dung binh cua ong, khong tach khoi boi canh cuoi nam 1788 dau 1789.", ["surprise", "strategy"]),
    ("qt_kb_023", "Thu nhuong bo de danh lua dich", "museum", "Truoc khi danh, Quang Trung tung sai nguoi dua thu voi loi le nhun nhuong nham lam Ton Si Nghi them chu quan.", "Mau nay cho thay nghi binh chinh tri va tam ly chien, khong nen hieu la dau hang thuc su.", ["deception", "ton_si_nghi"]),
    ("qt_kb_024", "Ha Hoi va chien tranh tam ly", "qptd", "Tai don Ha Hoi, the vay va uy luc cua quan Tay Son lam quan Thanh hoang so, xin hang, de lai luong thuc va khi gioi.", "Mau nay cho thay Quang Trung biet thang bang tinh than va the tran, khong chi bang chem giet truc dien.", ["ha_hoi", "psychological_warfare"]),
    ("qt_kb_025", "Kho khan truoc don Ngoc Hoi", "qptd", "Sau Ha Hoi, tien cong Ngoc Hoi kho hon vi dich da canh giac va dua ky binh ra chan buoc tien cua Tay Son.", "Mau nay giup cau tra loi khong ly tuong hoa tran danh, ma thay duoc kho khan chien thuat thuc su.", ["ngoc_hoi", "battle"]),
    ("qt_kb_026", "Dung tuong binh dot pha", "qptd", "Nguyen Hue tung doi tuong binh hon mot tram voi chien vao dung thoi co de pha the ky binh va mo duong cho bo binh tien len.", "Mau nay nen dung khi nguoi hoc hoi ve voi chien, trang bi va cach ket hop luc luong.", ["elephants", "ngoc_hoi"]),
    ("qt_kb_027", "Doi xung kich voi moc rom uot", "qptd", "Trong tran Ngoc Hoi, doi xung kich Tay Son duoc mo ta la khieng moc lon quan rom uot, tien sat don giac de giam hoa luc.", "Mau nay la fact chien thuat cu the, can tranh noi qua thanh vu khi than ky.", ["shock_troops", "ngoc_hoi"]),
    ("qt_kb_028", "Tran dia Dam Muc", "qptd", "Quang Trung cho bo tri truoc tran dia o khu Dam Muc de chan va tieu diet tan quan Thanh sau khi chung roi khoi Ngoc Hoi.", "Mau nay cho thay chien dich co buoc truy kich va khoa duong rut, khong chi la mot dot xung phong vao don.", ["dam_muc", "pursuit"]),
    ("qt_kb_029", "Huong Khương Thuong - Dong Da", "qptd", "Cung luc voi mat Ngoc Hoi, canh quan Tay Son danh vao Khương Thuong, Dong Da, mot diem so ho nhung hiem yeu cua dich.", "Mau nay giup tra loi ve ten goi Ngoc Hoi - Dong Da nhu hai huong quyet dinh trong cung chien dich.", ["dong_da", "khương_thuong"]),
    ("qt_kb_030", "Do doc Long danh Sam Nghi Dong", "qptd", "Canh quan do Do doc Long chi huy thoc sau vao khu Sam Nghi Dong, lam canh quan Thanh o Khương Thuong tan vo nhanh.", "Mau nay dung cho cau hoi ve cac tuong linh Tay Son va viec tan cong vao so chi huy dich.", ["do_doc_long", "sam_nghi_dong"]),
    ("qt_kb_031", "Ton Si Nghi thao chay", "qptd", "Khi cac huong Tay Son ap sat va bo chi huy roi loan, Ton Si Nghi thao chay khoi Thang Long trong tinh the gap gap.", "Mau nay phu hop de giai thich ket cuc chien dich va su sup do tinh than cua quan Thanh.", ["ton_si_nghi", "retreat"]),
    ("qt_kb_032", "Y nghia Ngoc Hoi - Dong Da", "vass", "Chien thang Ngoc Hoi - Dong Da nam 1789 khang dinh doc lap, pha vo cuoc can thiep cua nha Thanh va de lai dau an van hoa lich su sau sac.", "Mau nay nen dung o phan ket luan cau tra loi, sau khi da neu boi canh va dien bien chinh.", ["ngoc_hoi_dong_da", "significance"]),
    ("qt_kb_033", "Boi canh Dang Trong truoc Rach Gam", "qdnd", "Truoc tran Rach Gam - Xoai Mut, the luc chua Nguyen that bai nhieu lan truoc phong trao Tay Son o Dang Trong.", "Mau nay giup nguoi hoc hieu vi sao Nguyen Anh phai tim su ho tro tu Xiêm.", ["rach_gam_xoai_mut", "context"]),
    ("qt_kb_034", "Nam 1777 o Gia Dinh", "qdnd", "Nam 1777, Nguyen Hue chi huy nghia quan Tay Son tien cong vung Gia Dinh, lam suy sup quyen luc cua chua Nguyen o nhieu dia ban phia Nam.", "Mau nay dat Nguyen Hue vao chien truong Nam Bo truoc tran thuy chien nam 1785.", ["gia_dinh", "1777"]),
    ("qt_kb_035", "Nguyen Anh cau vien Xiêm", "qdnd", "Sau nhung that bai lien tiep, Nguyen Anh chay ra dao roi sang Xiêm, cau cuu luc luong ben ngoai de phuc hoi the luc.", "Mau nay nen dung cho cau hoi ve nguyen nhan truc tiep cua cuoc can thiep Xiêm.", ["nguyen_anh", "siam"]),
    ("qt_kb_036", "Quan Xiêm tien vao Gia Dinh", "qdnd", "Nam 1784, vua Xiêm sai Chiêu Tang va Chiêu Sương dua quan thuy bo vao Gia Dinh, phoi hop voi tan quan Nguyen Anh.", "Mau nay la moc boi canh quan trong truoc khi Nguyen Hue duoc giao vao Nam doi pho.", ["siamese_invasion", "1784"]),
    ("qt_kb_037", "Nguyen Hue vao My Tho", "qdnd", "Cuoi nam 1784, Nguyen Hue dua dao quan lon vao My Tho, to chuc cam cu, nam tinh hinh va cho thoi co phan cong.", "Mau nay cho thay ong khong danh hap tap ma danh sau khi da doc duoc dich va dia hinh.", ["my_tho", "preparation"]),
    ("qt_kb_038", "Quy mo quan Tay Son o Nam Bo", "qdnd", "Tai chien truong Tay Nam Bo, Nguyen Hue to chuc co dong luc luong lon tu mien Trung vao, vua hanh quan vua bao dam hau can.", "Mau nay lien ket tai cam quan va nang luc to chuc hau can trong tran Rach Gam - Xoai Mut.", ["logistics", "mobility"]),
    ("qt_kb_039", "Chon khuc song Rach Gam - Xoai Mut", "qdnd", "Nguyen Hue chon doan song My Tho tu Rach Gam den Xoai Mut lam tran dia quyet chien voi lien quan Xiêm - Nguyen.", "Mau nay phu hop cho cau hoi ve dia hinh va nghe thuat phuc kich tren song.", ["battlefield_selection", "rach_gam_xoai_mut"]),
    ("qt_kb_040", "Bo tri thuy binh bo binh phao binh", "qdnd", "Tai Rach Gam - Xoai Mut, thuy binh Tay Son an trong cac nhanh song, con bo binh va phao binh phuc san o bo song va cu lao.", "Mau nay la fact chien thuat cot loi, can gan voi doan song My Tho chu khong noi chung chung.", ["ambush", "artillery"]),
    ("qt_kb_041", "Thoi diem cong kich Rach Gam", "qdnd", "Khi doan thuyen dich da lot vao tran dia, Nguyen Hue ra lenh cong kich, khoa dau khoa duoi va danh vao doi hinh dang roi.", "Mau nay cho thay gia tri cua thoi diem ra lenh, mot dac diem quan trong trong phong cach chi huy cua ong.", ["attack_order", "rach_gam_xoai_mut"]),
    ("qt_kb_042", "Thuy binh Tay Son khoa dau duoi", "qdnd", "Thuy binh Tay Son tu Rach Gam va Xoai Mut bat ngo lao ra, chan duong tien lui cua thuyen chien dich tren khuc song hep.", "Mau nay dung de giai thich vi sao mot tran thuy chien co the ket thuc rat nhanh.", ["naval_tactics", "ambush"]),
    ("qt_kb_043", "Ket qua tran Rach Gam", "qdnd", "Lien quan Xiêm - Nguyen thiet hai nang trong tran Rach Gam - Xoai Mut nam 1785; nhieu thuyen bi danh chim, Chiêu Tang va Chiêu Sương phai chay ve nuoc.", "Mau nay nen dung cho cau hoi ve ket qua, tranh phong dai so lieu neu khong co nguon kiem chung bo sung.", ["outcome", "rach_gam_xoai_mut"]),
    ("qt_kb_044", "Hau can trong chien dich Nam Bo", "qdnd", "Chien thang Rach Gam - Xoai Mut cho thay Tay Son co kha nang dua quan, thuyen, vu khi va luong thuc vao chien truong xa trong thoi gian ngan.", "Mau nay giup app tra loi cac cau hoi khong chi ve danh tran ma ve dieu kien de danh thang.", ["logistics", "southern_campaign"]),
    ("qt_kb_045", "Huy dong nguon luc tai cho", "qdnd", "O Gia Dinh va My Tho, viec huy dong tai cho ket hop tu mang theo giup Nguyen Hue co dieu kien vat chat de thuc hien tran danh.", "Mau nay nen dung khi hoi ve quan tri hau can, khong bien thanh cau chuyen thuan tuy ve vu khi.", ["local_supply", "logistics"]),
    ("qt_kb_046", "Uu the hoa luc Tay Son", "qdnd", "Tai Rach Gam - Xoai Mut, nghia quan Tay Son co hoa luc phao binh va chien thuyen du manh de pha vo doi hinh thuy quan dich.", "Mau nay tra loi ve ky thuat quan su nhung phai dat trong cau truc phuc kich, khong tach thanh so sanh vu khi don le.", ["artillery", "naval_warfare"]),
    ("qt_kb_047", "Y nghia Rach Gam - Xoai Mut", "qdnd", "Rach Gam - Xoai Mut la chien thang lon chong can thiep Xiêm, giup Tay Son cung co mien Nam va tiep tuc qua trinh mo rong the luc.", "Mau nay phu hop cho phan y nghia lich su, nhat la khi so sanh voi Ngoc Hoi - Dong Da ve bao ve doc lap.", ["significance", "rach_gam_xoai_mut"]),
    ("qt_kb_048", "Nha Thanh cong nhan Nguyen Hue", "vnsu", "Sau chien thang, theo Viet Nam su luoc, nha Thanh ve sau cong nhan Nguyen Hue lam vua nuoc Nam va phong theo le bang giao.", "Mau nay giup tra loi ve hau qua ngoai giao sau chien dich, tranh noi rang quan he Viet - Thanh ket thuc bang chien tranh lien mien.", ["diplomacy", "qing"]),
    ("qt_kb_049", "Danh gia chinh thong cua Tran Trong Kim", "vnsu", "Viet Nam su luoc lap luan rang neu xet theo cong ly, Quang Trung Nguyen Hue co the duoc dat ngang hang voi cac vua dung nuoc nhu Dinh Tien Hoang va Le Thai To.", "Mau nay nen dung khi hoi ve danh gia su hoc, can noi ro day la cach nhin cua tac gia nguon, khong phai mot du kien tran danh.", ["historiography", "legitimacy"]),
    ("qt_kb_050", "Gioi han tri vi 1788-1792", "vnsu", "Phan Viet Nam su luoc ve Vua Quang Trung dat trieu vi cua ong trong khoang 1788 den 1792, vi vay nhan vat mo phong khong nen tu nhan biet cac su kien sau khi mat.", "Mau nay la guardrail quan trong cho cac cau hoi gai bay ve cong nghe hien dai hoac cac chien dich the ky XX.", ["guardrail", "timeline"]),
    ("qt_kb_051", "Duong loi giang hoa sau chien thang", "vnsu", "Sau khi danh tan quan Thanh, Quang Trung khong tiep tuc day chien tranh len cao ma dung duong loi giang hoa de ngua mot dot phuc thu lon tu phia Bac.", "Mau nay bo sung khia canh chinh tri - ngoai giao sau chien thang quan su.", ["diplomacy", "qing", "postwar"]),
    ("qt_kb_052", "Ngo Thi Nham phu trach van thu bang giao", "vnsu", "Ngo Thi Nham duoc giao viet thu tu, bieu van va loi le doi dap voi phia Thanh, dung van phong mem deo de giam cang thang sau chien tranh.", "Mau nay giup tra loi ve vai tro si phu Bac Ha trong chinh sach ngoai giao Tay Son.", ["diplomacy", "ngo_thi_nham", "letters"]),
    ("qt_kb_053", "Thu ta toi theo nghi le bang giao", "vnsu", "Trong quan he voi nha Thanh, Tay Son su dung loi le ta toi va nhun nhuong theo khuon thuc bang giao, nham khien Can Long co loi thoai lui danh du ma khong phai mo lai chien tranh.", "Mau nay can phan biet ngon ngu nghi le voi viec mat chu quyen thuc te.", ["diplomacy", "can_long", "ritual_language"]),
    ("qt_kb_054", "Cau phong de on dinh phia Bac", "vnsu", "Viec cau phong sau chien thang duoc dat trong muc tieu on dinh bien gioi, hop thuc hoa quan he voi Thanh va tranh mot chien dich bao thu moi.", "Mau nay dung khi bi hoi ve viec cau phong, khong dien giai thanh phuc tung tuyet doi.", ["diplomacy", "investiture", "qing"]),
    ("qt_kb_055", "Phuc Khang An lam trung gian hau chien", "vnsu", "Phuc Khang An giu vai tro quan trong trong viec noi lai bang giao, trinh bay tinh the voi Can Long va thuc day cach xu ly on hoa hon sau that bai cua Ton Si Nghi.", "Mau nay giai thich vi sao quan he Thanh - Tay Son chuyen tu chien tranh sang nghi le bang giao.", ["diplomacy", "phuc_khang_an", "qing"]),
    ("qt_kb_056", "Nha Thanh phong An Nam quoc vuong", "vnsu", "Viet Nam su luoc ghi nha Thanh ve sau sai su sang phong Nguyen Hue lam An Nam quoc vuong theo le cac trieu truoc.", "Mau nay bo sung chi tiet ve viec cong nhan trong trat tu bang giao khu vuc.", ["diplomacy", "investiture", "an_nam_quoc_vuong"]),
    ("qt_kb_057", "Gioi han cua ngon ngu trieu cong", "vnsu", "Loi le cau phong va ta toi la ngon ngu nghi le cua trat tu Dong A thoi do; khong nen rut gon thanh ket luan rang Tay Son tu xoa bo nen doc lap.", "Mau nay can de chong dien giai cuc doan ve chu hau va phuc tung.", ["diplomacy", "interpretation", "tribute"]),
    ("qt_kb_058", "Pham Cong Tri va cau chuyen gia vuong", "vnsu", "Viet Nam su luoc ke viec Quang Trung chon Pham Cong Tri co hinh dung giong minh de tra lam quoc vuong sang Yen Kinh du le mung tho Can Long.", "Mau nay phai gan nhan tranh luan vi cac nghien cuu hien dai xem xet lai chi tiet do.", ["diplomacy", "pham_cong_tri", "fake_king"]),
    ("qt_kb_059", "Doan su bo sang Yen Kinh", "vnsu", "Doan di Yen Kinh duoc ke gom Ngo Van So, Dang Van Chan, Phan Huy Ich va Vo Huy Tan, cung pham vat cong nap theo nghi le bang giao.", "Mau nay ket noi nhan vat Tay Son voi su kien trieu kien Can Long.", ["diplomacy", "embassy", "yen_kinh"]),
    ("qt_kb_060", "Tranh luan ve Quang Trung gia", "museum_fake_king", "Bai viet Bao tang Lich su Quoc gia trinh bay cac tinh huong va gia thuyet quanh nhan vat Quang Trung gia, trong do ten Pham Cong Tri can duoc hieu can trong.", "Mau nay giup gan nhan contested cho van de Pham Cong Tri.", ["diplomacy", "pham_cong_tri", "contested"]),
    ("qt_kb_061", "Tu lieu doi chieu ve tiep kien Can Long", "research_fake_king", "Bai nghien cuu ve viec Can Long tiep kien phai doan Tay Son neu cac van ban khac nhau ve viec ai thuc su sang chua Thanh nam 1790.", "Mau nay khong ket luan mot chieu, chi dung de nhac rang ho so su lieu co nhieu lop.", ["diplomacy", "can_long", "contested"]),
    ("qt_kb_062", "Ngoai giao nhu phep quyen bien giu nuoc", "vnsu", "Sau Ngoc Hoi - Dong Da, Quang Trung vua giu the chien thang vua dung loi le mem de tranh chien tranh lon; do la phep quyen bien chinh tri, khong phai su phu phuc don gian.", "Mau nay la ket luan can bang cho cac cau hoi ve doc lap, cau phong va bang giao.", ["diplomacy", "interpretation", "statecraft"]),
]


CLAIM_STATUS = {
    "qt_kb_053": "interpretive",
    "qt_kb_054": "interpretive",
    "qt_kb_057": "interpretive",
    "qt_kb_058": "contested",
    "qt_kb_060": "contested",
    "qt_kb_061": "contested",
    "qt_kb_062": "interpretive",
    "qt_kb_067": "interpretive",
    "qt_kb_070": "interpretive",
    "qt_kb_073": "interpretive",
    "qt_kb_074": "interpretive",
    "qt_kb_077": "interpretive",
    "qt_kb_089": "interpretive",
    "qt_kb_098": "interpretive",
    "qt_kb_099": "interpretive",
    "qt_kb_100": "interpretive",
}


ENRICHED_TOPICS = [
    {
        "chunk_id": "qt_kb_063",
        "topic_title": "Vì sao chọn Nghệ An làm Trung đô",
        "source_key": "museum_capital",
        "fact": "Quang Trung chọn Nghệ An vì đây là đất căn bản, người đông, nằm khoảng giữa Phú Xuân và Thăng Long, tiện khống chế cả trong Nam ngoài Bắc.",
        "text": (
            "Vì sao chọn Nghệ An làm Trung đô. Tư liệu bảo tàng giải thích việc chọn Nghệ An không thể rút gọn thành chuyện quê gốc. "
            "Trong chiếu gửi Nguyễn Thiếp, nhà vua nêu rõ Phú Xuân ở xa, hình thế cách trở, khó trị Bắc Hà; còn Nghệ An nằm giữa đường ra vào, "
            "vừa cân, vừa có thể khống chế trong Nam ngoài Bắc. Nghệ An cũng là đất căn bản từng được xem trọng trong các thời chống ngoại xâm, "
            "có dân đông, có khả năng cung cấp binh lực, và chính trong chiến dịch Kỷ Dậu quân Tây Sơn đã dừng ở đây để tuyển thêm quân. "
            "Vì vậy, câu trả lời đúng cần nhấn mạnh tầm nhìn địa chính trị: đặt trung tâm quyền lực ở vị trí thuận điều hành đất nước sau phân tranh, "
            "không phải chỉ là mê tín phong thủy hay một lựa chọn tình cảm."
        ),
        "tags": ["capital_city", "phuong_hoang_trung_do", "nghe_an", "dung_quyet", "nguyen_thiep"],
        "answer_intents": ["capital_city"],
        "canonical_questions": [
            "Vì sao chọn Nghệ An để xây Phượng Hoàng Trung Đô?",
            "Tại sao không tiếp tục lấy Thăng Long hoặc Phú Xuân làm kinh đô chính?",
            "Phượng Hoàng Trung Đô có ý nghĩa địa chính trị gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_064",
        "topic_title": "Nguyễn Thiếp và việc xem đất đóng đô",
        "source_key": "museum_documents",
        "fact": "Bảo tàng Lịch sử Quốc gia lưu nhiều thư, chiếu của Nguyễn Huệ gửi Nguyễn Thiếp về việc mời giúp nước, xem đất, chọn ngày và dựng hành cung ở Nghệ An.",
        "text": (
            "Nguyễn Thiếp và việc xem đất đóng đô. Hồ sơ văn bản Quang Trung tại Bảo tàng Lịch sử Quốc gia cho thấy quan hệ giữa Nguyễn Huệ và La Sơn Phu tử không phải một lần mời đơn giản. "
            "Các văn bản có thư mời Nguyễn Thiếp giúp việc, chiếu nhờ xem và chọn ngày dựng hành cung ở Nghệ An, chiếu trách việc chưa xem đất đóng đô, và chiếu mời vào Phú Xuân hội kiến. "
            "Những văn bản này đặt Nguyễn Thiếp trong vai trò cố vấn chính trị - văn hóa, đặc biệt về địa điểm trung tâm quyền lực mới. Khi trả lời, cần nói nhà vua kiên trì mời bậc sĩ phu có uy tín, "
            "dùng lời lẽ trọng thị nhưng cũng có lúc thúc giục vì việc nước gấp. Đây là dữ liệu quan trọng để tránh biến Nguyễn Thiếp thành nhân vật phụ mờ nhạt trong chuyện dời đô."
        ),
        "tags": ["capital_city", "scholars", "nguyen_thiep", "la_son_phu_tu", "documents"],
        "answer_intents": ["capital_city", "scholars"],
        "canonical_questions": [
            "Nguyễn Thiếp có vai trò gì trong Phượng Hoàng Trung Đô?",
            "Quang Trung đã mời Nguyễn Thiếp ra giúp nước như thế nào?",
            "Các văn bản nào liên quan Nguyễn Thiếp và việc dời đô?",
        ],
    },
    {
        "chunk_id": "qt_kb_065",
        "topic_title": "Dũng Quyết, Yên Trường và hình thế Phượng Hoàng Trung Đô",
        "source_key": "museum_capital_unfinished",
        "fact": "Địa điểm được chọn nằm giữa núi Quyết và núi Kỳ Lân, thuộc vùng Dũng Quyết - Yên Trường, nay ở thành phố Vinh, Nghệ An.",
        "text": (
            "Dũng Quyết, Yên Trường và hình thế Phượng Hoàng Trung Đô. Bài viết của Bảo tàng Lịch sử Quốc gia mô tả địa điểm cuối cùng được Nguyễn Thiếp chọn là vùng giữa núi Quyết và núi Kỳ Lân, "
            "tên dân gian là Rú Mèo, thuộc làng Dũng Quyết, xã Yên Trường, huyện Hưng Nguyên, nay thuộc thành phố Vinh. Dấu tích này gắn với sông Lam và hệ núi Dũng Quyết, tạo thành một không gian vừa có "
            "ý nghĩa phòng thủ, vừa có ý nghĩa biểu tượng của kinh đô mới. Khi người dùng hỏi về chân núi Dũng Quyết, câu trả lời cần xác định đúng địa danh và vai trò của Nguyễn Thiếp trong việc khảo sát. "
            "Không nên trả lời chung chung rằng Quang Trung chỉ chọn Nghệ An vì yêu quê, cũng không nên tách Phượng Hoàng Trung Đô khỏi dự án chính trị sau chiến thắng quân Thanh."
        ),
        "tags": ["capital_city", "phuong_hoang_trung_do", "dung_quyet", "yen_truong", "nghe_an"],
        "answer_intents": ["capital_city"],
        "canonical_questions": [
            "Phượng Hoàng Trung Đô nằm ở đâu?",
            "Dũng Quyết và Yên Trường liên quan gì đến kinh đô mới?",
            "La Sơn Phu tử đã chọn địa điểm nào?",
        ],
    },
    {
        "chunk_id": "qt_kb_066",
        "topic_title": "Huy động xây dựng Phượng Hoàng Trung Đô",
        "source_key": "museum_capital_unfinished",
        "fact": "Hoàng Lê nhất thống chí được bài bảo tàng dẫn lại nói Quang Trung trưng dụng nhiều thợ thuyền, chuyên chở gỗ đá, gạch ngói, đắp thành đất và sai quân lính đào đá ong xây thành trong.",
        "text": (
            "Huy động xây dựng Phượng Hoàng Trung Đô. Theo đoạn Hoàng Lê nhất thống chí được Bảo tàng Lịch sử Quốc gia dẫn lại, công trình ở Nghệ An không chỉ là dự định trên giấy. "
            "Triều đình Tây Sơn đã trưng dụng nhiều thợ thuyền, chuyên chở gỗ đá, gạch ngói để dựng cung phủ, lâu đài; bên ngoài đắp thành đất, bên trong sai quân lính đào đá ong tại địa phương để xây thành trong. "
            "Tư liệu còn nhắc đến Lầu Rồng ba tầng, điện Thái Hòa và hai dãy hành lang để dùng khi có lễ triều hạ. Khi trả lời câu hỏi về lực lượng và vật tư, cần nêu rõ thợ thuyền, quân lính, đất, đá ong, gỗ, đá, gạch, ngói. "
            "Phần nào chưa được nguồn hiện có xác nhận chắc chắn thì không nên nói như sự thật tuyệt đối."
        ),
        "tags": ["capital_city", "construction", "phuong_hoang_trung_do", "materials", "stone_laterite"],
        "answer_intents": ["capital_city"],
        "canonical_questions": [
            "Ai được huy động xây Phượng Hoàng Trung Đô?",
            "Vật liệu xây Phượng Hoàng Trung Đô gồm những gì?",
            "Phượng Hoàng Trung Đô đã xây được công trình nào?",
        ],
    },
    {
        "chunk_id": "qt_kb_067",
        "topic_title": "Phượng Hoàng Trung Đô dở dang",
        "source_key": "museum_capital_unfinished",
        "fact": "Công trình Phượng Hoàng Trung Đô chưa kịp hoàn tất thì sự nghiệp Tây Sơn rơi vào biến động sau khi Quang Trung mất.",
        "text": (
            "Phượng Hoàng Trung Đô dở dang. Bảo tàng Lịch sử Quốc gia nhấn mạnh kinh đô mới ở Nghệ An chịu số phận dang dở giống sự nghiệp chính trị của Quang Trung. "
            "Sau khi nhà vua qua đời năm 1792, triều đình Quang Toản không tiếp tục quyết liệt việc dời đô theo ý nguyện trước đó. Điều này giúp giải thích vì sao Phượng Hoàng Trung Đô có dấu tích, có mô tả công trình, "
            "nhưng không trở thành trung tâm cai trị hoàn chỉnh lâu dài. Khi trả lời, cần phân biệt ba lớp: ý định chiến lược của Quang Trung, quá trình xây dựng thật sự đã bắt đầu, và sự dang dở do cái chết đột ngột cùng biến động sau đó. "
            "Không nên nói kinh đô này chỉ là truyền thuyết, nhưng cũng không nên mô tả như một kinh thành đã vận hành ổn định nhiều năm."
        ),
        "tags": ["capital_city", "unfinished", "quang_toan", "1792", "interpretation"],
        "answer_intents": ["capital_city"],
        "canonical_questions": [
            "Vì sao Phượng Hoàng Trung Đô không hoàn tất?",
            "Phượng Hoàng Trung Đô có thật hay chỉ là dự định?",
            "Sau khi Quang Trung mất, dự án dời đô ra sao?",
        ],
    },
    {
        "chunk_id": "qt_kb_068",
        "topic_title": "Sổ đinh và quản lý nhân khẩu",
        "source_key": "vnsu",
        "fact": "Quang Trung xuống lệnh cho các trấn bắt dân xã làm lại sổ đinh, ai cũng phải biên vào sổ để phục vụ quản lý dân cư và quân dịch.",
        "text": (
            "Sổ đinh và quản lý nhân khẩu. Việt Nam sử lược ghi rằng khi toan tính việc lớn, Quang Trung xuống lệnh cho các trấn bắt dân xã làm lại sổ đinh, ai cũng phải được biên vào sổ. "
            "Đây là biện pháp hành chính quan trọng sau thời chiến loạn, khi dân cư lưu tán, làng xã xáo trộn và triều đình mới cần biết số người có thể chịu thuế, phục dịch hoặc sung quân. "
            "Câu trả lời đúng phải đặt sổ đinh trong bối cảnh xây dựng nhà nước Tây Sơn sau chiến tranh, không chỉ như một giấy tờ tùy thân đơn lẻ. Biện pháp này cho thấy Quang Trung không chỉ là võ tướng trên chiến trường; "
            "ông còn cố gắng dựng lại năng lực kiểm soát của chính quyền trung ương đối với làng xã, nhân khẩu và nghĩa vụ quân dân trong buổi đầu đại định."
        ),
        "tags": ["administration", "population", "so_dinh", "statecraft", "military_service"],
        "answer_intents": ["administration"],
        "canonical_questions": [
            "Sổ đinh thời Quang Trung dùng để làm gì?",
            "Quang Trung quản lý nhân khẩu bằng cách nào?",
            "Vì sao Tây Sơn phải làm lại sổ đinh?",
        ],
    },
    {
        "chunk_id": "qt_kb_069",
        "topic_title": "Tín bài Thiên hạ đại tín",
        "source_key": "vnsu",
        "fact": "Tín bài là thẻ bài ghi bốn chữ Thiên hạ đại tín, chung quanh ghi tên họ, quê quán và dùng điểm chỉ làm tin.",
        "text": (
            "Tín bài Thiên hạ đại tín. Việt Nam sử lược ghi rõ sau khi làm lại sổ đinh, triều đình cấp cho mỗi người một thẻ bài, giữa thẻ có bốn chữ Thiên hạ đại tín, chung quanh ghi tên họ, quê quán và phải điểm chỉ làm tin. "
            "Người nào cũng phải đeo thẻ ấy, gọi là tín bài. Đây là chi tiết hành chính rất quan trọng vì nó giống một cơ chế nhận diện dân cư thời chiến: ai không có thẻ bị coi là dân lậu, có thể bị bắt sung vào quân phòng. "
            "Khi trả lời câu hỏi về giấy tờ bằng gỗ, cần nêu đúng tên là tín bài và đúng bốn chữ là Thiên hạ đại tín. Nếu người hỏi nói Thiên hạ đại định, câu trả lời phải chỉnh lại nhẹ nhàng theo tư liệu hiện có."
        ),
        "tags": ["administration", "tin_bai", "thien_ha_dai_tin", "identity_card", "population"],
        "answer_intents": ["administration"],
        "canonical_questions": [
            "Tín bài thời Quang Trung là gì?",
            "Bốn chữ trên tín bài là gì?",
            "Giấy tờ tùy thân bằng gỗ thời Tây Sơn có ý nghĩa gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_070",
        "topic_title": "Mặt trái của chính sách tín bài",
        "source_key": "vnsu",
        "fact": "Việt Nam sử lược ghi việc kiểm tra tín bài bị lại dịch và xã trưởng lợi dụng, gây nhiễu động dân gian, khiến nhiều người phải trốn vào rừng.",
        "text": (
            "Mặt trái của chính sách tín bài. Việt Nam sử lược không chỉ ghi mục đích kiểm soát dân cư, mà còn ghi hệ quả tiêu cực của việc thi hành. "
            "Người không có tín bài bị coi là dân lậu và có thể bị bắt sung quân; nhân đó, lại dịch cùng xã trưởng đi lại làm bậy, vào làng vây bắt hỏi thẻ, gây nhiễu động dân gian. "
            "Nhiều người vì sợ hãi phải trốn vào rừng. Chi tiết này giúp câu trả lời không trở thành ca ngợi một chiều. Chính sách tín bài phản ánh nhu cầu nhà nước mới muốn kiểm soát nhân khẩu và quân dịch sau loạn lạc, "
            "nhưng cũng cho thấy cách thi hành cứng rắn có thể gây áp lực nặng lên dân chúng. Khi nhập vai, có thể nói đó là phép trị nước nghiêm trong buổi loạn, nhưng không được che mất hệ quả sử liệu đã ghi."
        ),
        "tags": ["administration", "tin_bai", "social_impact", "interpretation", "population"],
        "answer_intents": ["administration"],
        "canonical_questions": [
            "Tín bài có gây hệ quả gì không?",
            "Ai không có tín bài thì bị xử lý thế nào?",
            "Chính sách tín bài có mặt trái gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_071",
        "topic_title": "Chiếu khuyến nông sau chiến tranh",
        "source_key": "political_history_book",
        "fact": "Sau đại thắng quân Thanh, Quang Trung coi việc khôi phục ruộng đất bỏ hoang và đưa dân lưu tán trở lại sản xuất là việc cần làm ngay.",
        "text": (
            "Chiếu khuyến nông sau chiến tranh. Tư liệu sách chính trị - lịch sử nhấn mạnh sau khi quét sạch quân Thanh, một việc cần làm ngay của Quang Trung là giải quyết ruộng đất bỏ hoang, tận dụng sức lao động và khôi phục sản xuất nông nghiệp. "
            "Chiến tranh kéo dài làm dân cư lưu tán, đồng ruộng hoang phế, nguồn lương thực và thuế khóa suy yếu; nếu không phục hồi nông nghiệp, nhà nước mới không thể ổn định lâu dài. "
            "Vì vậy Chiếu khuyến nông không chỉ là lời khuyên trồng cấy, mà là chính sách phục hồi nền tảng kinh tế - xã hội sau nội chiến và ngoại xâm. Khi trả lời, cần gắn nông nghiệp với dân sinh, quân lương, thuế khóa và ổn định quốc gia. "
            "Đó là phần quan trọng để hình tượng Quang Trung không bị thu hẹp thành người chỉ biết đánh trận."
        ),
        "tags": ["agriculture", "chieu_khuyen_nong", "economy", "statecraft", "postwar"],
        "answer_intents": ["agriculture", "economy"],
        "canonical_questions": [
            "Chiếu khuyến nông có mục đích gì?",
            "Quang Trung phục hồi kinh tế sau chiến tranh như thế nào?",
            "Vì sao ruộng đất bỏ hoang là vấn đề lớn thời Tây Sơn?",
        ],
    },
    {
        "chunk_id": "qt_kb_072",
        "topic_title": "Lệnh thi hành Chiếu khuyến nông năm 1790",
        "source_key": "museum_documents",
        "fact": "Bảo tàng Lịch sử Quốc gia lưu văn bản lệnh nói về cách thi hành Chiếu khuyến nông, đề ngày 15 tháng 5 năm Quang Trung thứ 3, tức năm 1790.",
        "text": (
            "Lệnh thi hành Chiếu khuyến nông năm 1790. Danh mục văn bản Quang Trung tại Bảo tàng Lịch sử Quốc gia có văn bản LSb.21973/Gy-120, ĐT-3672: lệnh nói về cách thi hành Chiếu khuyến nông, đề ngày 15 tháng 5 năm Quang Trung thứ 3, tức năm 1790. "
            "Chi tiết này cho thấy chính sách khuyến nông không chỉ tồn tại trong lời kể chung, mà có dấu vết văn bản hành chính cụ thể được lưu giữ. "
            "Khi hệ thống RAG trả lời về cải cách kinh tế, cần dẫn được nhóm tư liệu này để tăng độ tin cậy, thay vì chỉ nói chung rằng Quang Trung quan tâm đến nông nghiệp. "
            "Nội dung trả lời nên nhấn mạnh chính sách được triển khai thành lệnh thi hành, hướng về khôi phục sản xuất, ổn định dân cư và củng cố nền tài lực của triều đại mới."
        ),
        "tags": ["agriculture", "chieu_khuyen_nong", "documents", "1790", "statecraft"],
        "answer_intents": ["agriculture", "economy"],
        "canonical_questions": [
            "Có văn bản nào về Chiếu khuyến nông không?",
            "Chiếu khuyến nông được thi hành vào năm nào?",
            "Bảo tàng lưu tư liệu gì về khuyến nông thời Quang Trung?",
        ],
    },
    {
        "chunk_id": "qt_kb_073",
        "topic_title": "Nông nghiệp như nền của quốc phòng",
        "source_key": "political_history_book",
        "fact": "Việc khuyến nông được đặt trong quan hệ giữa dân sinh, kinh tế và sức mạnh quốc phòng của nhà nước sau chiến tranh.",
        "text": (
            "Nông nghiệp như nền của quốc phòng. Tư liệu nghiên cứu về tư tưởng quân sự đặt chính sách khuyến nông trong logic rộng hơn: kinh tế nông nghiệp là nền trực tiếp của đời sống dân chúng và cũng là khâu quyết định đến sức mạnh quốc phòng - an ninh. "
            "Một đạo quân mạnh không thể tồn tại nếu ruộng hoang, dân đói, kho lương trống và làng xã không ổn định. Vì vậy, khi Quang Trung thúc đẩy khôi phục sản xuất, đó không chỉ là cải cách dân sinh mà còn là cách xây nền cho quân đội, thuế khóa và trật tự chính trị. "
            "Câu trả lời tốt cần nối chính sách ruộng đất với kinh nghiệm của một vị tướng từng hành quân xa, hiểu rõ hậu cần. Đây là điểm giúp nhân vật trả lời sâu hơn các câu hỏi về kinh tế thay vì chỉ nhắc tên Chiếu khuyến nông."
        ),
        "tags": ["agriculture", "economy", "defense", "logistics", "interpretation"],
        "answer_intents": ["agriculture", "economy"],
        "canonical_questions": [
            "Khuyến nông liên quan gì đến quốc phòng?",
            "Vì sao Quang Trung coi phục hồi sản xuất là việc lớn?",
            "Kinh tế nông nghiệp giúp gì cho triều Tây Sơn?",
        ],
    },
    {
        "chunk_id": "qt_kb_074",
        "topic_title": "Thông thương và mở cửa buôn bán",
        "source_key": "political_history_book",
        "fact": "Một số tư liệu nghiên cứu nhìn nhận Quang Trung có nhãn quan thông thương, muốn mở cửa ải và làm hàng hóa lưu thông để lợi cho dân.",
        "text": (
            "Thông thương và mở cửa buôn bán. Ngoài khôi phục nông nghiệp, các tổng thuật nghiên cứu về thời Quang Trung còn nhắc đến tư tưởng thông thương, mở cửa ải, làm cho hàng hóa lưu chuyển để lợi cho dân chúng. "
            "Phần này cần được trình bày thận trọng vì tư liệu trong dataset hiện không đủ để dựng toàn bộ chính sách thương mại chi tiết, nhưng có thể nói Quang Trung không đi theo lối chỉ chăm đóng kín kinh tế sau chiến tranh. "
            "Khi trả lời về kinh tế, nên đặt thông thương bên cạnh khuyến nông và tiền tệ: sản xuất phải hồi phục, hàng hóa phải lưu thông, và thị trường cần phương tiện trao đổi ổn định. "
            "Cách diễn giải này giúp hệ thống trả lời giàu ý hơn mà vẫn không bịa ra các hiệp định hoặc thiết chế thương mại cụ thể ngoài tư liệu."
        ),
        "tags": ["economy", "trade", "commerce", "interpretation", "statecraft"],
        "answer_intents": ["economy"],
        "canonical_questions": [
            "Quang Trung có chủ trương thông thương không?",
            "Cải cách kinh tế thời Tây Sơn gồm gì ngoài nông nghiệp?",
            "Mở cửa ải có ý nghĩa gì trong kinh tế Quang Trung?",
        ],
    },
    {
        "chunk_id": "qt_kb_075",
        "topic_title": "Tiền Quang Trung thông bảo và Quang Trung đại bảo",
        "source_key": "bank_coinage",
        "fact": "Trong thời gian ở ngôi, Quang Trung cho đúc hai loại tiền đồng: Quang Trung thông bảo và Quang Trung đại bảo.",
        "text": (
            "Tiền Quang Trung thông bảo và Quang Trung đại bảo. Bài chuyên đề về tiền triều Tây Sơn cho biết trong thời gian ở ngôi, Quang Trung cho đúc hai loại tiền đồng là Quang Trung thông bảo và Quang Trung đại bảo. "
            "Đây là dữ liệu cốt lõi để trả lời các câu hỏi về chủ quyền tiền tệ của vương triều Tây Sơn. Việc đúc tiền mang niên hiệu nhà vua không chỉ phục vụ trao đổi hàng hóa, mà còn khẳng định quyền lực chính trị của triều đại mới trên thị trường sau thời Lê - Trịnh - Nguyễn phân tranh. "
            "Khi trả lời, cần nói đúng tên tiền, chất liệu chính là đồng theo nguồn chuyên đề, và có thể giải thích rằng tiền tệ giúp thống nhất lưu thông, tạo dấu hiệu quyền lực hợp pháp của chính quyền. "
            "Không nên trả lời rằng tư liệu hiện có chưa đề cập, vì dataset đã có căn cứ rõ."
        ),
        "tags": ["coinage", "economy", "quang_trung_thong_bao", "quang_trung_dai_bao", "copper"],
        "answer_intents": ["coinage", "economy"],
        "canonical_questions": [
            "Quang Trung cho đúc loại tiền nào?",
            "Tiền Quang Trung thông bảo làm bằng gì?",
            "Tiền tệ thời Tây Sơn có ý nghĩa chính trị gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_076",
        "topic_title": "Đặc điểm tiền Quang Trung",
        "source_key": "bank_coinage",
        "fact": "Tiền Quang Trung có nhiều dạng, có loại dày ở giai đoạn đầu, có lưng trơn hoặc đúc chữ như An Nam, Nhất, Nhị, Công, Chính.",
        "text": (
            "Đặc điểm tiền Quang Trung. Chuyên đề tiền triều Tây Sơn mô tả tiền Quang Trung có thể chia thành hai giai đoạn với phong cách khác nhau. "
            "Giai đoạn đầu có tiền đúc tương đối dày, phong cách gần với tiền Thái Đức và Minh Đức; một số đồng Quang Trung đại bảo có lưng trơn, còn Quang Trung thông bảo có nhiều biến thể. "
            "Lưng tiền có thể trơn hoặc có dấu, chữ như An Nam, Nhất, Nhị, Công, Chính tùy loại. Khi trả lời câu hỏi nâng cao về tiền tệ, không chỉ nêu tên tiền mà nên nói triều Tây Sơn đã cho phát hành số lượng đáng kể, có nhiều dạng chữ và kiểu lưng tiền. "
            "Tuy nhiên, không cần biến câu trả lời nhập vai thành mô tả khảo cổ quá dài; trọng tâm vẫn là quyền đúc tiền và ổn định lưu thông."
        ),
        "tags": ["coinage", "economy", "numismatics", "quang_trung_thong_bao", "quang_trung_dai_bao"],
        "answer_intents": ["coinage", "economy"],
        "canonical_questions": [
            "Tiền Quang Trung có đặc điểm gì?",
            "Quang Trung thông bảo có những dạng nào?",
            "Quang Trung đại bảo khác gì Quang Trung thông bảo?",
        ],
    },
    {
        "chunk_id": "qt_kb_077",
        "topic_title": "Tiền tệ và thị trường sau phân tranh",
        "source_key": "bank_coinage",
        "fact": "Việc phát hành tiền mang niên hiệu Quang Trung cần được hiểu trong bối cảnh triều đại mới cần ổn định lưu thông và khẳng định quyền lực trên thị trường.",
        "text": (
            "Tiền tệ và thị trường sau phân tranh. Khi một triều đại mới nổi lên sau thời Trịnh - Nguyễn phân tranh, tiền tệ không chỉ là vật mua bán mà còn là dấu hiệu quyền lực nhà nước. "
            "Tiền Quang Trung thông bảo và Quang Trung đại bảo mang niên hiệu của hoàng đế, giúp triều Tây Sơn đưa quyền đúc tiền của mình vào đời sống kinh tế. "
            "Nguồn chuyên đề cho thấy số lượng tiền phát hành thời Quang Trung là lớn trong toàn bộ thời Tây Sơn, phản ánh nhu cầu lưu thông đáng kể. "
            "Khi trả lời, có thể nói việc đúc tiền nhằm củng cố thị trường, tạo phương tiện trao đổi thống nhất và thay dần ảnh hưởng của các loại tiền cũ hoặc ngoại lai, nhưng phải giữ mức diễn giải thận trọng. "
            "Điểm chính là quyền đúc tiền gắn với quyền trị nước, không phải một chi tiết sưu tầm đơn lẻ."
        ),
        "tags": ["coinage", "economy", "market", "statecraft", "interpretation"],
        "answer_intents": ["coinage", "economy"],
        "canonical_questions": [
            "Vì sao đúc tiền là khẳng định chủ quyền?",
            "Tiền Quang Trung giúp ổn định thị trường thế nào?",
            "Tiền tệ có vai trò gì trong chính quyền Tây Sơn?",
        ],
    },
    {
        "chunk_id": "qt_kb_078",
        "topic_title": "Chiếu lập học và tư tưởng lấy giáo dục làm gốc",
        "source_key": "museum_education",
        "fact": "Sau khi lập Sùng chính viện, Quang Trung còn hạ chiếu lập nhà học cấp xã và cấp phủ, huyện.",
        "text": (
            "Chiếu lập học và tư tưởng lấy giáo dục làm gốc. Bài viết của Bảo tàng Lịch sử Quốc gia về khoa cử triều Tây Sơn cho biết sau khi xuống chiếu lập Sùng chính viện, Quang Trung còn hạ chiếu lập các nhà học cấp xã và cấp phủ, huyện. "
            "Điều này cho thấy nhà vua không chỉ cần tướng sĩ mà còn cần người học, thầy dạy và bộ máy quan lại có nền tảng chữ nghĩa cho chính quyền mới. "
            "Khi trả lời câu hỏi vì sao một võ tướng xuất thân từ phong trào nông dân lại quan tâm giáo dục, cần nói rằng trị nước lâu dài không thể chỉ dựa vào gươm giáo. "
            "Giáo dục nhằm rèn nhân tâm, tuyển người có học và tạo nền văn hóa chính trị mới sau thời loạn. Đây là mảng dữ liệu bắt buộc để nhân vật không bị đóng khung thành hình tượng võ biền."
        ),
        "tags": ["education", "chieu_lap_hoc", "schools", "statecraft", "scholars"],
        "answer_intents": ["education"],
        "canonical_questions": [
            "Vì sao Quang Trung ban Chiếu lập học?",
            "Quang Trung lập trường học đến cấp nào?",
            "Giáo dục có vai trò gì trong cải cách Tây Sơn?",
        ],
    },
    {
        "chunk_id": "qt_kb_079",
        "topic_title": "Trường học cấp xã, phủ và huyện",
        "source_key": "museum_education",
        "fact": "Chiếu lập học yêu cầu lập nhà học ở xã, phủ và huyện, chọn nho sĩ có học thức, đức hạnh để giảng dạy.",
        "text": (
            "Trường học cấp xã, phủ và huyện. Theo bài viết về khoa cử triều Tây Sơn, Quang Trung không chỉ lập một trung tâm học thuật ở triều đình mà còn hạ chiếu lập nhà học ở cấp xã và cấp phủ, huyện. "
            "Các nơi cần chọn nho sĩ có học thức, có đức hạnh làm thầy để giảng dạy học trò trong địa phương. "
            "Đây là chi tiết quan trọng khi trả lời câu hỏi về yêu cầu lập trường học tận cấp xã: nó cho thấy ý định mở rộng giáo dục xuống cơ sở, không chỉ đào tạo vài người trong cung đình. "
            "Trong bối cảnh Bắc Hà vừa yên, lòng người chưa phục hoàn toàn, trường học còn là cách thu hút sĩ phu, ổn định xã hội và xây dựng trật tự mới. "
            "Câu trả lời nên ngắn gọn nhưng phải có hai ý: mở rộng giáo dục và tuyển dụng nhân tài cho việc trị nước."
        ),
        "tags": ["education", "local_schools", "chieu_lap_hoc", "teachers", "statecraft"],
        "answer_intents": ["education"],
        "canonical_questions": [
            "Chiếu lập học yêu cầu lập trường ở đâu?",
            "Ai được chọn làm thầy thời Quang Trung?",
            "Giáo dục cấp xã thời Tây Sơn có mục đích gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_080",
        "topic_title": "Sùng chính viện và việc dịch sách",
        "source_key": "political_history_book",
        "fact": "Theo chiếu chỉ Quang Trung, Sùng chính thư viện lần lượt dịch Tiểu học, Tứ thư, Kinh Thi, Kinh Thư và Kinh Dịch sang chữ Nôm.",
        "text": (
            "Sùng chính viện và việc dịch sách. Tư liệu sách chính trị - lịch sử ghi theo chiếu chỉ của Quang Trung, Sùng chính thư viện sẽ lần lượt dịch các bộ Tiểu học, Tứ thư, Kinh Thi, Kinh Thư và Kinh Dịch. "
            "Đến tháng 7 năm Nhâm Tý 1792, nhóm nhà Nho dưới sự tổ chức của Nguyễn Thiếp đã dịch xong Tiểu học và Tứ thư; việc dịch các kinh khác bị gián đoạn khi Quang Trung đột ngột băng hà. "
            "Chi tiết này cho thấy cải cách văn hóa không chỉ là khẩu hiệu dùng chữ Nôm, mà có chương trình dịch sách học tập cụ thể. "
            "Khi trả lời, cần nêu Sùng chính viện như một cơ quan học thuật nhằm đưa tri thức kinh điển vào ngôn ngữ gần với người Việt hơn, phục vụ giáo dục và xây dựng nền học thuật độc lập hơn."
        ),
        "tags": ["education", "sung_chinh_vien", "chu_nom", "translation", "nguyen_thiep"],
        "answer_intents": ["education"],
        "canonical_questions": [
            "Sùng chính viện làm gì?",
            "Quang Trung cho dịch những sách nào?",
            "Chữ Nôm có vai trò gì trong giáo dục thời Tây Sơn?",
        ],
    },
    {
        "chunk_id": "qt_kb_081",
        "topic_title": "Chữ Nôm và tự chủ văn hóa",
        "source_key": "political_history_book",
        "fact": "Việc dịch sách sang chữ Nôm phản ánh hoài bão xây dựng nền học thuật dân tộc và giảm lệ thuộc vào Hán tự trong giáo dục.",
        "text": (
            "Chữ Nôm và tự chủ văn hóa. Các nghiên cứu về thời Quang Trung nhìn nhận chủ trương dịch sách sang chữ Nôm là biểu hiện của hoài bão xây dựng nền học thuật, giáo dục dân tộc. "
            "Trong trật tự cũ, chữ Hán giữ vị trí thống trị trong học thuật và khoa cử; việc đưa các sách học quan trọng sang chữ Nôm giúp mở một hướng tự chủ hơn về văn hóa. "
            "Khi trả lời, không nên nói Quang Trung phủ định toàn bộ Nho học, vì chính các sách được dịch vẫn là Tiểu học, Tứ thư, Kinh Thi, Kinh Thư, Kinh Dịch. "
            "Điểm mới là ông muốn dùng tiếng nói, chữ viết gần với dân tộc để tổ chức việc học và thi cử. "
            "Đây là dữ liệu giúp nhân vật trả lời sâu các câu hỏi về văn hóa, giáo dục, bản sắc và chính sách chữ Nôm."
        ),
        "tags": ["education", "chu_nom", "culture", "self_reliance", "interpretation"],
        "answer_intents": ["education"],
        "canonical_questions": [
            "Quang Trung dùng chữ Nôm để làm gì?",
            "Dịch sách sang chữ Nôm có ý nghĩa gì?",
            "Cải cách văn hóa thời Quang Trung có điểm gì mới?",
        ],
    },
    {
        "chunk_id": "qt_kb_082",
        "topic_title": "Khoa thi và tuyển người học",
        "source_key": "museum_education",
        "fact": "Năm Quang Trung thứ 2, triều Tây Sơn mở khoa thi Hương cho học trò xứ Nghệ, có người gọi là khoa thi Tuấn sĩ.",
        "text": (
            "Khoa thi và tuyển người học. Bài viết về khoa cử triều Tây Sơn ghi mùa thu tháng 8 năm Quang Trung thứ 2, tức năm 1789, khi triều chính còn mới, nhà vua đã mở khoa thi Hương cho học trò xứ Nghệ, có người gọi là khoa thi Tuấn sĩ. "
            "Chi tiết này cho thấy chính quyền Tây Sơn cần nhanh chóng tìm người có học để bổ sung cho bộ máy, nhất là trong vùng Nghệ An vốn được dự định làm Trung đô. "
            "Khi trả lời về giáo dục, nên nối khoa thi với Chiếu lập học và Sùng chính viện: lập trường để đào tạo, dịch sách để có tài liệu, mở thi để chọn người. "
            "Không nên chỉ nói chung rằng Quang Trung trọng hiền tài; cần chỉ ra các biện pháp cụ thể đã được tư liệu ghi nhận."
        ),
        "tags": ["education", "exam", "tuấn_sĩ", "nghe_an", "scholars"],
        "answer_intents": ["education", "scholars"],
        "canonical_questions": [
            "Quang Trung có mở khoa thi không?",
            "Khoa thi Tuấn sĩ là gì?",
            "Tây Sơn tuyển người học bằng cách nào?",
        ],
    },
    {
        "chunk_id": "qt_kb_083",
        "topic_title": "Trọng dụng Ngô Thì Nhậm",
        "source_key": "museum_ngo_thi_nham",
        "fact": "Ngô Thì Nhậm được Quang Trung phong Tả thị lang bộ Lại, phụ trách công việc tổ chức và cán bộ trong nội bộ chính quyền.",
        "text": (
            "Trọng dụng Ngô Thì Nhậm. Bài viết của Bảo tàng Lịch sử Quốc gia về Ngô Thì Nhậm cho biết Quang Trung phong ông làm Tả thị lang bộ Lại, tức phụ trách công việc tổ chức và cán bộ trong bộ máy mới. "
            "Đây là bằng chứng rõ về thái độ chiêu hiền đãi sĩ của Tây Sơn đối với trí thức Bắc Hà. Ngô Thì Nhậm từng thuộc giới sĩ phu cũ, nhưng được nhà vua nhìn vào tài năng chính trị, văn thư và sách lược hơn là chỉ xét xuất thân. "
            "Khi trả lời câu hỏi vì sao Ngô Thì Nhậm dốc lòng phụng sự Tây Sơn, cần nhấn mạnh hai chiều: nhà vua trọng dụng thật sự, giao việc lớn; còn Ngô Thì Nhậm thấy thời cuộc mới có khả năng cứu nước, ổn định Bắc Hà và mở đường cho người hiền tài nhập cuộc. "
            "Không nên trả lời bằng lời chối thiếu dữ liệu."
        ),
        "tags": ["scholars", "ngo_thi_nham", "bureaucracy", "chieu_hien", "bac_ha"],
        "answer_intents": ["scholars"],
        "canonical_questions": [
            "Quang Trung trọng dụng Ngô Thì Nhậm như thế nào?",
            "Ngô Thì Nhậm giữ chức gì thời Tây Sơn?",
            "Vì sao sĩ phu Bắc Hà theo Quang Trung?",
        ],
    },
    {
        "chunk_id": "qt_kb_084",
        "topic_title": "Chiếu cầu hiền",
        "source_key": "museum_ngo_thi_nham",
        "fact": "Ngô Thì Nhậm soạn Chiếu cầu hiền cho Quang Trung để chiêu hiền mộ sĩ, kêu gọi trí thức ra giúp chính quyền mới.",
        "text": (
            "Chiếu cầu hiền. Theo Bảo tàng Lịch sử Quốc gia, Ngô Thì Nhậm là người soạn Chiếu cầu hiền cho vua Quang Trung để chiêu hiền mộ sĩ. "
            "Bản chiếu này được đánh giá cao vì đối tượng thực sự là trí thức, các bậc hiền tài lương đống của dân tộc, và nó bộc lộ khát vọng dùng người hiền của vị vua áo vải sau chiến thắng quân Thanh. "
            "Khi trả lời các câu hỏi về sĩ phu Bắc Hà, nên dùng Chiếu cầu hiền như bằng chứng cho chính sách thu phục nhân tài bằng lý lẽ chính trị, không phải chỉ bằng cưỡng ép. "
            "Câu trả lời nhập vai có thể nói: nước mới yên, việc mới mở, người có tài không nên giữ lòng cũ mà bỏ mặc dân chúng. "
            "Phần citation sẽ nêu rõ tư liệu, còn lời nhân vật nên giữ khí phách quân vương."
        ),
        "tags": ["scholars", "chieu_cau_hien", "ngo_thi_nham", "talent", "bac_ha"],
        "answer_intents": ["scholars"],
        "canonical_questions": [
            "Chiếu cầu hiền là gì?",
            "Ai soạn Chiếu cầu hiền cho Quang Trung?",
            "Quang Trung thuyết phục sĩ phu Bắc Hà bằng cách nào?",
        ],
    },
    {
        "chunk_id": "qt_kb_085",
        "topic_title": "Ngô Thì Nhậm và kế rút về Tam Điệp",
        "source_key": "museum_ngo_thi_nham",
        "fact": "Ngô Thì Nhậm chủ trương rút quân về phòng tuyến Tam Điệp - Biện Sơn để bảo toàn lực lượng, chờ Quang Trung ra Bắc quyết chiến.",
        "text": (
            "Ngô Thì Nhậm và kế rút về Tam Điệp. Bài viết về Ngô Thì Nhậm nhấn mạnh cuối năm Mậu Thân 1788, khi quân Thanh kéo sang, ông đưa ra kế rút thủy quân về Biện Sơn, lục quân về Tam Điệp để bảo toàn lực lượng. "
            "Kế này tránh việc các tướng Tây Sơn ở Bắc Hà đánh vội trong thế bất lợi, giữ quân không mất một mũi tên, chờ chủ tướng từ Phú Xuân ra quyết chiến. "
            "Chi tiết này giúp hệ thống trả lời sâu hơn về vai trò Ngô Thì Nhậm: ông không chỉ viết văn thư ngoại giao mà còn có sách lược quân sự - chính trị rất thực tế. "
            "Khi nói về thu phục sĩ phu, có thể nêu Quang Trung trọng dụng Ngô Thì Nhậm vì nhìn thấy người này hiểu thế Bắc Hà, biết lường lực lượng và biết chọn thời cơ."
        ),
        "tags": ["scholars", "ngo_thi_nham", "tam_diep", "strategy", "qing_invasion"],
        "answer_intents": ["scholars", "military"],
        "canonical_questions": [
            "Ngô Thì Nhậm có vai trò gì trước trận Kỷ Dậu?",
            "Kế rút về Tam Điệp có ý nghĩa gì?",
            "Vì sao Quang Trung đánh giá cao Ngô Thì Nhậm?",
        ],
    },
    {
        "chunk_id": "qt_kb_086",
        "topic_title": "Ngô Thì Nhậm trong ngoại giao hậu chiến",
        "source_key": "vnsu",
        "fact": "Sau chiến thắng quân Thanh, Ngô Thì Nhậm giữ vai trò quan trọng trong văn thư bang giao mềm dẻo với nhà Thanh.",
        "text": (
            "Ngô Thì Nhậm trong ngoại giao hậu chiến. Việt Nam sử lược và các tư liệu về bang giao Tây Sơn - Thanh đều cho thấy sau chiến thắng, triều Tây Sơn không chỉ dùng quân sự mà còn cần văn thư mềm dẻo để xử lý với Càn Long. "
            "Ngô Thì Nhậm là gương mặt then chốt trong lớp sĩ phu Bắc Hà tham gia việc này. Ông giúp biến thắng lợi quân sự thành thế ngoại giao có lợi: giảng hòa, cầu phong, tạ tội theo nghi lễ, nhưng vẫn giữ thực chất độc lập. "
            "Khi trả lời, cần tránh hai cực đoan: không nói Tây Sơn khuất phục tuyệt đối, cũng không nói Quang Trung chỉ biết dùng vũ lực. "
            "Vai trò của Ngô Thì Nhậm cho thấy nhà vua biết dùng người có chữ nghĩa, hiểu văn phong bang giao và biết mở đường lui danh dự cho đối phương để giữ yên bờ cõi."
        ),
        "tags": ["scholars", "diplomacy", "ngo_thi_nham", "qing", "letters"],
        "answer_intents": ["scholars", "diplomacy"],
        "canonical_questions": [
            "Ngô Thì Nhậm làm gì trong bang giao với nhà Thanh?",
            "Ai giúp Quang Trung viết văn thư hậu chiến?",
            "Vì sao ngoại giao sau Ngọc Hồi - Đống Đa cần sĩ phu?",
        ],
    },
    {
        "chunk_id": "qt_kb_087",
        "topic_title": "Kiên trì mời La Sơn Phu tử",
        "source_key": "museum_documents",
        "fact": "Các thư, chiếu lưu tại Bảo tàng Lịch sử Quốc gia cho thấy Nguyễn Huệ nhiều lần mời Nguyễn Thiếp giúp việc, hội kiến và tham gia việc nước.",
        "text": (
            "Kiên trì mời La Sơn Phu tử. Danh mục văn bản Quang Trung lưu tại Bảo tàng Lịch sử Quốc gia có nhiều văn bản liên quan Nguyễn Thiếp: thư mời giúp việc lần thứ ba, thư mời tới Phù Thạch hội kiến, chiếu trách việc cố chấp, chiếu mời vào Phú Xuân, "
            "và các chiếu liên quan xem đất ở Nghệ An. Chuỗi văn bản này cho thấy Quang Trung kiên trì tìm cách kéo một bậc sĩ phu uy tín vào việc nước. "
            "Khi trả lời câu hỏi vì sao Nguyễn Thiếp ra giúp sau nhiều lần từ chối, cần nhấn mạnh sự trọng thị, việc giao đúng sở trường và bối cảnh cứu dân cứu nước sau biến động Bắc Hà. "
            "Nhà vua không chỉ cần Nguyễn Thiếp cầm quân, mà cần ông giúp định đô, giáo dục, dịch sách và tạo chính danh văn hóa cho triều đại mới."
        ),
        "tags": ["scholars", "nguyen_thiep", "la_son_phu_tu", "documents", "chieu_hien"],
        "answer_intents": ["scholars", "capital_city", "education"],
        "canonical_questions": [
            "Quang Trung mời Nguyễn Thiếp mấy lần?",
            "Vì sao Nguyễn Thiếp được mời ra giúp nước?",
            "La Sơn Phu tử giúp Quang Trung những việc gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_088",
        "topic_title": "Nguyễn Thiếp và Sùng chính viện",
        "source_key": "political_history_book",
        "fact": "Nguyễn Thiếp tổ chức và điều hành nhóm nhà Nho dịch sách tại Sùng chính thư viện, hoàn thành Tiểu học và Tứ thư trước khi Quang Trung mất.",
        "text": (
            "Nguyễn Thiếp và Sùng chính viện. Tư liệu sách chính trị - lịch sử ghi việc dịch sách ở Sùng chính thư viện do Nguyễn Thiếp tổ chức và điều hành, với nhóm nhà Nho như Nguyễn Công, Nguyễn Thiện, Phan Tố Định, Bùi Dương Lịch. "
            "Đến tháng 7 năm Nhâm Tý 1792, nhóm này dịch xong Tiểu học và Tứ thư; các bộ Kinh Thi, Kinh Thư, Kinh Dịch đang triển khai thì Quang Trung băng hà. "
            "Chi tiết này giải thích vì sao Quang Trung cần Nguyễn Thiếp: không phải chỉ vì danh tiếng đạo học, mà vì ông có thể tổ chức một chương trình học thuật phục vụ cải cách giáo dục. "
            "Khi trả lời nhập vai, có thể nhấn mạnh rằng trị nước phải có người dạy học, người dịch sách, người rèn nhân tâm; gươm giáo chỉ mở đường, chữ nghĩa mới giữ nền lâu dài."
        ),
        "tags": ["education", "scholars", "nguyen_thiep", "sung_chinh_vien", "translation"],
        "answer_intents": ["education", "scholars"],
        "canonical_questions": [
            "Nguyễn Thiếp làm gì ở Sùng chính viện?",
            "Ai tổ chức việc dịch sách thời Quang Trung?",
            "Vì sao Nguyễn Thiếp quan trọng với cải cách giáo dục?",
        ],
    },
    {
        "chunk_id": "qt_kb_089",
        "topic_title": "Thuyết phục sĩ phu vượt qua tư tưởng tôn Lê",
        "source_key": "museum_ngo_thi_nham",
        "fact": "Chính sách cầu hiền của Quang Trung hướng tới trí thức Bắc Hà, kêu gọi họ vượt qua lòng cũ để tham gia việc nước trong buổi đầu đại định.",
        "text": (
            "Thuyết phục sĩ phu vượt qua tư tưởng tôn Lê. Sau khi nhà Lê suy sụp và quân Thanh bị đánh bại, nhiều sĩ phu Bắc Hà vẫn mang nặng lòng tôn Lê, xem Tây Sơn là thế lực mới khó chấp nhận. "
            "Chiếu cầu hiền do Ngô Thì Nhậm soạn cho Quang Trung nhằm mở đường cho họ ra giúp nước bằng một lý lẽ chính trị rộng hơn: việc mới đang mở, dân cần yên, người hiền không nên ẩn mình khi thiên hạ cần tài. "
            "Khi trả lời, nên tránh nói Quang Trung chỉ dùng áp lực; dữ liệu cho thấy ông dùng cả chức vụ, văn thư, lời mời trọng thị và nhiệm vụ phù hợp. "
            "Với Nguyễn Thiếp, nhà vua nhiều lần mời và giao việc định đô, giáo dục, dịch sách; với Ngô Thì Nhậm, giao tổ chức cán bộ, sách lược và ngoại giao. Đó là thuật dùng người có chủ đích."
        ),
        "tags": ["scholars", "ton_le", "bac_ha", "chieu_cau_hien", "interpretation"],
        "answer_intents": ["scholars"],
        "canonical_questions": [
            "Quang Trung thuyết phục sĩ phu tôn Lê bằng lý lẽ gì?",
            "Chiếu cầu hiền nhắm đến ai?",
            "Tây Sơn thu phục trí thức Bắc Hà ra sao?",
        ],
    },
    {
        "chunk_id": "qt_kb_090",
        "topic_title": "Ăn Tết trước để giữ nhịp thần tốc",
        "source_key": "dong_da_exhibit",
        "fact": "Cuối tháng Chạp năm Mậu Thân, Quang Trung cho quân ăn Tết trước và hẹn sang xuân mồng 7 vào Thăng Long mở tiệc lớn.",
        "text": (
            "Ăn Tết trước để giữ nhịp thần tốc. Trưng bày của Công viên Văn hóa Đống Đa ghi một ngày cuối tháng Chạp năm Mậu Thân 1788, Quang Trung mở tiệc khao quân coi như ăn Tết Nguyên đán trước. "
            "Ông tuyên bố đợi đến sang xuân ngày mồng 7 vào thành Thăng Long sẽ mở tiệc lớn. Chi tiết này có ý nghĩa tâm lý và chiến dịch rất mạnh: quân sĩ được giải tỏa nỗi nhớ Tết, đồng thời nhận một lời hẹn chiến thắng cụ thể. "
            "Nó cũng giúp giữ nhịp hành quân thần tốc, không để đại quân dừng lại vì lễ tiết trong khi quân Thanh đang chủ quan. "
            "Khi trả lời, cần nói ăn Tết trước không phải chuyện vui chơi, mà là cách biến ngày Tết thành lời thề tiến quân, tăng sĩ khí và bảo toàn yếu tố bất ngờ."
        ),
        "tags": ["micro_tactics", "tet_strategy", "rapid_campaign", "morale", "1788"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Vì sao Quang Trung cho quân ăn Tết trước?",
            "Lời hẹn mồng 7 vào Thăng Long có ý nghĩa gì?",
            "Ăn Tết trước trong chiến dịch Kỷ Dậu là chiến thuật gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_091",
        "topic_title": "Lời hẹn mồng 7 vào Thăng Long",
        "source_key": "dong_da_exhibit",
        "fact": "Lời hẹn mồng 7 tháng Giêng vào Thăng Long mở tiệc lớn tạo mục tiêu tâm lý rõ ràng cho toàn quân Tây Sơn.",
        "text": (
            "Lời hẹn mồng 7 vào Thăng Long. Khi Quang Trung cho quân ăn Tết trước và hẹn ngày mồng 7 tháng Giêng vào Thăng Long mở tiệc lớn, ông đặt trước mắt tướng sĩ một đích đến vừa cụ thể vừa táo bạo. "
            "Trong chiến tranh, mục tiêu rõ làm quân lính tin rằng kế hoạch đã được tính toán, không phải hành quân mù quáng. Lời hẹn ấy còn đánh vào tâm lý đối phương: quân Thanh tin quân Tây Sơn khó tiến nhanh trong dịp Tết, nên sự xuất hiện sớm của đại quân tạo bất ngờ lớn. "
            "Khi trả lời, cần nối lời hẹn với ba yếu tố: sĩ khí, thời gian chiến dịch và bất ngờ chiến lược. "
            "Không nên chỉ kể rằng nhà vua ăn Tết trước, mà phải giải thích vì sao hành động đó làm toàn quân sẵn sàng vượt qua lễ tiết để giữ tốc độ tiến công."
        ),
        "tags": ["micro_tactics", "tet_strategy", "morale", "surprise", "thang_long"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Mồng 7 vào Thăng Long mở tiệc có phải lời hẹn chiến thắng không?",
            "Ăn Tết trước giúp quân Tây Sơn giữ tốc độ ra sao?",
            "Yếu tố tâm lý trong chiến dịch Kỷ Dậu là gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_092",
        "topic_title": "Năm đạo quân trong chiến dịch Kỷ Dậu",
        "source_key": "dong_da_exhibit",
        "fact": "Trưng bày Đống Đa mô tả các đạo quân Tây Sơn tiến công nhiều hướng, trong đó đạo chủ lực do Quang Trung trực tiếp chỉ huy và các đạo vu hồi phối hợp.",
        "text": (
            "Năm đạo quân trong chiến dịch Kỷ Dậu. Các tư liệu trưng bày về Ngọc Hồi - Đống Đa cho thấy quân Tây Sơn không tiến vào Thăng Long theo một mũi đơn độc. "
            "Đạo chủ lực do Quang Trung trực tiếp chỉ huy gồm bộ binh, tượng binh, kỵ binh, nhiều voi chiến, hỏa hổ và đại bác, đảm nhiệm hướng tiến công chủ yếu. "
            "Các đạo khác vu hồi, đánh vào Hải Dương, Sơn Minh, Đại Áng, Khương Thượng - Đống Đa, phối hợp chia cắt hệ thống phòng thủ của quân Thanh. "
            "Khi trả lời về nghệ thuật quân sự, cần nhấn mạnh tổ chức nhiều hướng giúp tạo bất ngờ, cắt đường rút, đánh vào điểm yếu và làm bộ chỉ huy địch rối loạn. "
            "Chiến thắng không chỉ do tốc độ, mà còn do cấu trúc hiệp đồng giữa các đạo quân."
        ),
        "tags": ["micro_tactics", "five_columns", "ngoc_hoi_dong_da", "coordination", "strategy"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Quân Tây Sơn chia mấy đạo trong chiến dịch Kỷ Dậu?",
            "Năm đạo quân có ý nghĩa chiến thuật gì?",
            "Quang Trung phối hợp các hướng tiến công ra sao?",
        ],
    },
    {
        "chunk_id": "qt_kb_093",
        "topic_title": "Tượng binh phá thế kỵ binh Thanh",
        "source_key": "qptd",
        "fact": "Nguyễn Huệ tung hơn một trăm voi chiến đúng thời cơ để phá đội kỵ binh thiện chiến nhất của quân Thanh trước đồn Ngọc Hồi.",
        "text": (
            "Tượng binh phá thế kỵ binh Thanh. Tạp chí Quốc phòng toàn dân mô tả sau Hà Hồi, quân Thanh đã cảnh giác và đưa đội kỵ binh thiện chiến ra chặn bước tiến của Tây Sơn. "
            "Nguyễn Huệ trù liệu trước và tung đội tượng binh hơn một trăm voi chiến xung trận. Trước đội voi mạnh, dũng mãnh như những khối núi di động, ngựa của quân Thanh hoảng sợ, hí lên, té chạy, lồng lộn quay về, làm đội hình kỵ binh rối loạn. "
            "Câu trả lời đúng cần nói tượng binh không phải chỉ là biểu tượng oai nghi, mà là binh chủng đột phá nhằm bẻ gãy ưu thế cơ động của kỵ binh địch. "
            "Từ đó bộ binh xung kích có điều kiện áp sát chiến lũy Ngọc Hồi. Đây là dữ liệu cốt lõi cho câu hỏi về voi chiến."
        ),
        "tags": ["micro_tactics", "elephants", "cavalry", "ngoc_hoi", "qing_army"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Tượng binh Tây Sơn phá kỵ binh Thanh thế nào?",
            "Vì sao voi chiến hiệu quả ở Ngọc Hồi?",
            "Quân Thanh phản ứng ra sao trước tượng binh?",
        ],
    },
    {
        "chunk_id": "qt_kb_094",
        "topic_title": "Hỏa khí trên tượng binh",
        "source_key": "qptd",
        "fact": "Tượng binh Tây Sơn ngoài cung, nỏ, giáo, lao còn được trang bị hỏa khí như súng tay, hỏa hổ và đại bác.",
        "text": (
            "Hỏa khí trên tượng binh. Tạp chí Quốc phòng toàn dân ghi ngoài cung, nỏ, giáo, lao, tượng binh Tây Sơn còn được trang bị thêm nhiều thứ hỏa khí như súng tay, hỏa hổ và đại bác. "
            "Trưng bày Đống Đa cũng nhắc đến voi chiến đi cùng hỏa hổ, đại bác trong đạo quân chủ lực và hướng Đống Đa. "
            "Khi trả lời, có thể nói sức mạnh của tượng binh đến từ sự kết hợp giữa thân voi gây áp lực tâm lý, tiếng động và hỏa lực trên lưng hoặc đi kèm đội hình. "
            "Điều này giải thích vì sao kỵ binh Thanh bị phá thế nhanh: ngựa sợ voi, đội hình rối, còn hỏa khí làm sức ép tăng lên. "
            "Không nên nói quá thành vũ khí thần kỳ; cần đặt tượng binh trong thế trận hiệp đồng với bộ binh, kỵ binh, mộc rơm và các hướng vu hồi."
        ),
        "tags": ["micro_tactics", "elephants", "firearms", "hoa_ho", "artillery"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Voi chiến Tây Sơn được trang bị gì?",
            "Hỏa hổ và đại bác liên quan gì đến tượng binh?",
            "Tượng binh phối hợp với hỏa lực ra sao?",
        ],
    },
    {
        "chunk_id": "qt_kb_095",
        "topic_title": "Mộc rơm ướt và đội xung kích Ngọc Hồi",
        "source_key": "dong_da_exhibit",
        "fact": "Đội xung kích gồm cảm tử quân dùng các tấm mộc lớn kết liền, có rơm ướt để chống đỡ đại bác và cung tên khi áp sát đồn Ngọc Hồi.",
        "text": (
            "Mộc rơm ướt và đội xung kích Ngọc Hồi. Trưng bày Đống Đa mô tả sau khi tượng binh mở đường, đội xung kích gồm cảm tử quân chia thành nhiều toán dàn ngang, phía trước là các tấm mộc lớn kết liền với nhau để chống đỡ hỏa lực trong chiến lũy. "
            "Các mô tả quen thuộc về trận Ngọc Hồi nhắc mộc được quấn rơm ướt nhằm giảm sức lửa và che chở cho quân tiến sát. "
            "Khi trả lời về chiến thuật vi mô, cần nêu đây là giải pháp áp sát công sự có hỏa lực mạnh: tượng binh phá kỵ binh, mộc che đạn và tên, bộ binh xung kích tiến thành đội hình chữ nhất. "
            "Điểm cốt lõi là phối hợp nhiều biện pháp để vượt qua phòng tuyến kiên cố, không phải chỉ dùng lòng dũng cảm đơn thuần."
        ),
        "tags": ["micro_tactics", "shield", "shock_troops", "ngoc_hoi", "wet_straw"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Mộc rơm ướt dùng để làm gì ở Ngọc Hồi?",
            "Đội xung kích Tây Sơn tiến công thế nào?",
            "Vì sao quân Tây Sơn áp sát được đồn Ngọc Hồi?",
        ],
    },
    {
        "chunk_id": "qt_kb_096",
        "topic_title": "Đòn phối hợp Đống Đa lúc cuối canh tư",
        "source_key": "dong_da_exhibit",
        "fact": "Hướng Đống Đa do đạo quân cơ động có kỵ binh, tượng binh, hỏa hổ và đại bác bất ngờ đánh vào khoảng cuối canh tư.",
        "text": (
            "Đòn phối hợp Đống Đa lúc cuối canh tư. Trưng bày Đống Đa ghi sáng mồng 5 tháng Giêng năm Kỷ Dậu, khi đạo chủ lực đánh Ngọc Hồi, hướng phối hợp của Đô đốc Đặng Tiến Đông cũng bất ngờ đánh vào Đống Đa. "
            "Đạo quân này gồm kỵ binh và tượng binh có sức cơ động nhanh, đột phá mạnh, được trang bị nhiều hỏa hổ và đại bác đặt trên mình voi chiến; cuộc tiến công bắt đầu vào khoảng cuối canh tư, khoảng 3 giờ sáng. "
            "Khi trả lời, cần cho thấy Đống Đa không phải trận rời rạc mà là hướng phối hợp làm tan hệ thống phòng thủ Thăng Long. "
            "Đòn đánh đêm gần sáng tạo bất ngờ, làm cánh quân Sầm Nghi Đống sụp đổ, đồng thời uy hiếp đại bản doanh Tôn Sĩ Nghị từ hướng khác với Ngọc Hồi."
        ),
        "tags": ["micro_tactics", "dong_da", "night_attack", "dang_tien_dong", "coordination"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Đống Đa được đánh vào lúc nào?",
            "Hướng Đống Đa phối hợp với Ngọc Hồi thế nào?",
            "Đạo quân Đống Đa có lực lượng gì?",
        ],
    },
    {
        "chunk_id": "qt_kb_097",
        "topic_title": "Đô đốc Long và điểm yếu Tây Nam",
        "source_key": "qptd",
        "fact": "Cánh quân Tây Sơn bí mật cơ động từ hướng Tây Nam, phối hợp lực lượng tại chỗ để bao vây, chia cắt và tiêu diệt địch ở khu vực Đống Đa - Khương Thượng.",
        "text": (
            "Đô đốc Long và điểm yếu Tây Nam. Tạp chí Quốc phòng toàn dân phân tích Tôn Sĩ Nghị liên tục điều quân tăng viện, nhưng không nhận ra nguy cơ từ hướng Tây Nam. "
            "Chớp thời cơ, cánh quân của Đô đốc Long bí mật cơ động và triển khai lực lượng, phối hợp với lực lượng tại chỗ, tổ chức nhiều hướng mũi tiến công, hình thành thế bao vây, chia cắt tiêu diệt địch. "
            "Dữ liệu này giúp trả lời sâu về vì sao quân Thanh đông mà vỡ nhanh: bộ chỉ huy bị đánh vào điểm sơ hở, thông tin chậm, các cánh quân bị chia cắt và tinh thần hoảng loạn. "
            "Khi trả lời về Đống Đa hoặc Sầm Nghi Đống, cần nêu vai trò hướng Tây Nam và đòn bí mật, không chỉ kể kết quả Sầm Nghi Đống thất bại. "
            "Đây là ví dụ rõ về nghệ thuật chọn hướng đánh của Tây Sơn."
        ),
        "tags": ["micro_tactics", "do_doc_long", "dong_da", "southwest", "encirclement"],
        "answer_intents": ["micro_tactics"],
        "canonical_questions": [
            "Đô đốc Long đánh vào điểm yếu nào?",
            "Vì sao hướng Tây Nam quan trọng trong trận Đống Đa?",
            "Quân Tây Sơn bao vây chia cắt quân Thanh ra sao?",
        ],
    },
    {
        "chunk_id": "qt_kb_098",
        "topic_title": "Guardrail sự kiện sau năm 1792",
        "source_key": "vnsu",
        "fact": "Quang Trung mất năm 1792, vì vậy nhân vật mô phỏng không được tự nhận biết hoặc tham gia các sự kiện sau mốc này.",
        "text": (
            "Guardrail sự kiện sau năm 1792. Phần dữ liệu tiểu sử xác định Quang Trung trị vì 1788-1792 và mất năm 1792. "
            "Trong hệ thống nhập vai, mọi câu hỏi gán cho ông các sự kiện sau mốc này phải được xử lý như chuyện đời sau. "
            "Nhân vật có thể phản bác bằng giọng quân vương, nhưng không được nói sự kiện ấy có liên quan đến điều đã chép nếu trong tư liệu không có liên hệ thật. "
            "Ví dụ, Internet, Facebook, trí tuệ nhân tạo, Điện Biên Phủ, chiến tranh thế giới, máy bay hiện đại hoặc các quốc gia - khái niệm chính trị đời sau đều phải bị chặn trước khi truy xuất. "
            "Câu trả lời đúng cần nói: ta đã mất năm 1792, đem chuyện hàng trăm năm sau gán cho ta là hồ đồ. Đây là hàng rào chống ảo giác ngầm."
        ),
        "tags": ["anachronism", "guardrail", "timeline", "1792", "out_of_period"],
        "answer_intents": ["anachronism"],
        "canonical_questions": [
            "Quang Trung có biết sự kiện sau năm 1792 không?",
            "Câu hỏi ngoài thời đại phải trả lời thế nào?",
            "Vì sao RAG không được lấy tài liệu cũ cho câu hỏi hiện đại?",
        ],
    },
    {
        "chunk_id": "qt_kb_099",
        "topic_title": "Thế chiến là khái niệm đời sau",
        "source_key": "vnsu",
        "fact": "Thế chiến thứ nhất, Thế chiến thứ hai, World War, WW1 và WW2 đều xảy ra sau khi Quang Trung mất rất lâu, nên phải bị chặn như câu hỏi ngoài thời đại.",
        "text": (
            "Thế chiến là khái niệm đời sau. Quang Trung mất năm 1792; các cuộc chiến tranh thế giới của thế kỷ XX diễn ra sau đó hơn một trăm năm. "
            "Vì vậy câu hỏi như nhà vua có tham gia Thế chiến thứ hai hay không không được đưa vào truy xuất bình thường. Nếu retriever vẫn ép lấy các đoạn về Việt Nam sử lược, Ngọc Hồi hoặc Quang Trung giả để trả lời, hệ thống sẽ tạo lỗi ảo giác ngầm: có vẻ thận trọng nhưng thực ra thừa nhận liên hệ sai thời đại. "
            "Guardrail cần nhận diện các cụm thế chiến, chiến tranh thế giới, World War, WW1, WW2, 1939, 1945 và các năm sau 1792. "
            "Câu trả lời nhập vai nên dứt khoát: chuyện ấy xảy ra sau đời ta, hỏi vậy là lẫn thời, không can cớ gì gán cho ta."
        ),
        "tags": ["anachronism", "world_war", "ww2", "guardrail", "timeline"],
        "answer_intents": ["anachronism"],
        "canonical_questions": [
            "Quang Trung có tham gia Thế chiến 2 không?",
            "Thế chiến có liên quan đến Quang Trung không?",
            "World War có phải ngoài thời đại Quang Trung không?",
        ],
    },
    {
        "chunk_id": "qt_kb_100",
        "topic_title": "Sửa nhầm Thiên hạ đại định thành Thiên hạ đại tín",
        "source_key": "vnsu",
        "fact": "Tư liệu Việt Nam sử lược ghi bốn chữ trên tín bài là Thiên hạ đại tín, không phải Thiên hạ đại định.",
        "text": (
            "Sửa nhầm Thiên hạ đại định thành Thiên hạ đại tín. Một lỗi dễ xảy ra trong dữ liệu là ghi tín bài với bốn chữ Thiên hạ đại định. "
            "Theo đoạn Việt Nam sử lược đang dùng trong dataset, bốn chữ trên thẻ là Thiên hạ đại tín. Chung quanh thẻ ghi tên họ, quê quán và dùng điểm chỉ làm tin; người nào cũng phải đeo thẻ ấy, gọi là tín bài. "
            "Khi người dùng hỏi theo cụm sai, hệ thống không nên lặp lại sai sót, cũng không nên chối toàn bộ câu hỏi. Câu trả lời đúng là chỉnh lại: việc cấp thẻ có trong tư liệu, nhưng bốn chữ theo bản đang đối chiếu là Thiên hạ đại tín. "
            "Sau đó giải thích tín bài dùng để quản lý dân cư, kiểm soát dân lậu và phục vụ quân dịch trong bối cảnh nhà nước Tây Sơn cần ổn định nhân khẩu."
        ),
        "tags": ["administration", "tin_bai", "thien_ha_dai_tin", "correction", "anachronism"],
        "answer_intents": ["administration"],
        "canonical_questions": [
            "Có phải tín bài ghi Thiên hạ đại định không?",
            "Thiên hạ đại tín hay Thiên hạ đại định?",
            "Nếu người hỏi sai chữ trên tín bài thì trả lời thế nào?",
        ],
    },
]


ACCENTED_DIALOGUES = [
    {
        "example_id": "qt_dialogue_001",
        "user_query": "Thưa Hoàng đế, vì sao người quyết định lên ngôi trước khi ra Bắc đánh quân Thanh?",
        "character_response": "Giặc ngoài đã vào Thăng Long, quân dân cần một danh nghĩa rõ ràng để quy về một mối. Ta lên ngôi không phải để cầu hư danh, mà để yên lòng người, thống lĩnh thủy bộ, đánh đuổi quân Thanh và giữ lấy cơ độc lập.",
    },
    {
        "example_id": "qt_dialogue_002",
        "user_query": "Người nghĩ gì về quân Thanh cuối năm 1788?",
        "character_response": "Theo ta, quân Thanh mượn tiếng phù Lê để đặt chân lên nước Nam. Việc cốt yếu là phải đánh nhanh, đánh trúng chỗ, khiến chúng không kịp thu thế. Nói nhiều không bằng hành quân, và hành quân phải thần tốc.",
    },
    {
        "example_id": "qt_dialogue_003",
        "user_query": "Vào Nghệ An, điều người cần nhất là gì?",
        "character_response": "Ta cần thêm binh, cần sắp lại đội ngũ, và cần thổi vào quân sĩ một niềm tin chung. Quân đông mà lòng chưa một thì không thắng. Đã ra trận, mỗi người phải biết vì sao mình đánh.",
    },
    {
        "example_id": "qt_dialogue_004",
        "user_query": "Lời phủ dụ quân sĩ của người muốn nói điều gì?",
        "character_response": "Ta nhắc cho quân sĩ biết núi sông Nam Bắc đã phân, người phương Bắc nhiều lần xâm lấn nhưng đều bị đánh đuổi. Nay quân Thanh lại sang, ta không thể ngồi yên. Ai đồng lòng thì tiến, ai hai lòng thì quân pháp không dung thứ.",
    },
    {
        "example_id": "qt_dialogue_005",
        "user_query": "Trận Ngọc Hồi - Đống Đa có điểm cốt lõi nào?",
        "character_response": "Theo ta, cốt lõi là bất ngờ, chia cắt và đánh vào chỗ địch tưởng là vững nhưng thật ra sơ hở. Chính diện ép Ngọc Hồi, vu hồi đánh Đống Đa, các mũi tiến phối hợp như một lệnh. Địch đông mà rối loạn thì đông cũng hóa vô ích.",
    },
    {
        "example_id": "qt_dialogue_006",
        "user_query": "Người có dùng voi chiến trong trận Ngọc Hồi không?",
        "character_response": "Có. Ta xem tượng binh là một lực lượng có sức đột phá lớn, dùng đúng thời cơ thì làm kỵ binh địch náo loạn. Nhưng voi chiến chỉ là một phần. Chiến thắng đến từ thế trận, kỷ luật và sự hiệp đồng của nhiều đạo quân.",
    },
    {
        "example_id": "qt_dialogue_007",
        "user_query": "Rạch Gầm - Xoài Mút cho thấy điều gì về cách đánh của người?",
        "character_response": "Trận ấy cho thấy không cứ lấy đông đánh đông. Ta chọn khúc sông, giấu thủy binh, bộ binh và pháo, chờ địch lọt trọn vào thế bị khóa đầu chặn đuôi rồi mới công kích. Thắng là nhờ biết dùng địa hình và thời cơ.",
    },
    {
        "example_id": "qt_dialogue_008",
        "user_query": "Nếu sinh viên hỏi về việc dùng Facebook để kêu gọi quân sĩ thì sao?",
        "character_response": "Facebook là vật của đời sau, nằm ngoài thời ta. Nếu muốn hiểu việc kêu gọi quân sĩ, hãy xem lời hịch và cuộc duyệt binh ở Nghệ An, nơi ta dùng ký ức chống ngoại xâm để hợp lòng quân.",
    },
    {
        "example_id": "qt_dialogue_009",
        "user_query": "Người có thể nói về Điện Biên Phủ không?",
        "character_response": "Điện Biên Phủ ở sau thời ta rất xa. Ta không thể tự nhận đã biết trận ấy. Nếu chỉ cần lời khuyên của một người cầm quân, thì phải nắm địa hình, giữ ý chí, và không để địch dẫn dắt thế trận.",
    },
    {
        "example_id": "qt_dialogue_010",
        "user_query": "Vì sao phải đánh thần tốc?",
        "character_response": "Địch chiếm Thăng Long mà còn chủ quan; nếu để lâu chúng sẽ phòng thủ, tiếp viện và ép lòng người. Ta đi nhanh để biến sự chủ quan của địch thành thời cơ của ta. Trong chiến tranh, chậm một ngày có khi mất cả cục diện.",
    },
    {
        "example_id": "qt_dialogue_011",
        "user_query": "Người nhìn nhận Lê Chiêu Thống như thế nào?",
        "character_response": "Kẻ cầu viện ngoại bang để trở lại ngai vàng đã đặt lợi riêng trên cơ độc lập. Ta đánh quân Thanh trước hết là giữ nước, không phải chỉ tranh hơn thua với một dòng họ.",
    },
    {
        "example_id": "qt_dialogue_012",
        "user_query": "Quân đội Tây Sơn mạnh nhất ở điểm nào?",
        "character_response": "Theo ta, sức mạnh nằm ở tốc độ cơ động, kỷ luật, cách dùng địa hình và tinh thần của người đang đánh vì một mục đích rõ ràng. Thuyền, voi, pháo, bộ binh đều cần, nhưng nếu lòng quân tán thì khí giới cũng vô dụng.",
    },
    {
        "example_id": "qt_dialogue_013",
        "user_query": "Người có thể kể lại chiến thắng Hà Hồi không?",
        "character_response": "Hà Hồi là nơi dùng uy để khuất địch. Khi thế quân Tây Sơn áp sát, tiếng reo và thế vây làm quân giặc mất mật, xin hàng, lương thực khí giới rơi vào tay ta. Không phải trận nào cũng cần giết nhiều mới là giỏi.",
    },
    {
        "example_id": "qt_dialogue_014",
        "user_query": "Tại sao người đánh giá cao việc chọn trận địa?",
        "character_response": "Trận địa là nửa phần thắng lợi. Ở Rạch Gầm - Xoài Mút, sông rạch và cù lao giúp ta giấu quân, khóa đầu đuôi. Ở Ngọc Hồi - Đống Đa, các hướng tiến công khiến địch bị chia cắt. Người cầm quân phải đọc được đất trời.",
    },
    {
        "example_id": "qt_dialogue_015",
        "user_query": "Người có phải là người thống nhất đất nước không?",
        "character_response": "Sự nghiệp Tây Sơn đã phá vỡ nhiều thế lực chia cắt và đặt nền cho việc nối lại non sông. Nhưng lịch sử có nhiều chặng, sau ta còn nhiều biến động. Hãy nói đúng mực: ta góp phần lớn vào việc thống nhất và bảo vệ độc lập.",
    },
    {
        "example_id": "qt_dialogue_016",
        "user_query": "Lời của người có cần chứng cứ không?",
        "character_response": "Có. Theo ta, đã bàn việc nước thì phải trọng chứng cứ. Điều gì sách chép rõ thì nói rõ; điều gì còn mờ thì chớ nói như đinh đóng cột. Một lời quá đà có thể làm lệch cả cách hậu thế hiểu về thời cuộc.",
    },
    {
        "example_id": "qt_dialogue_017",
        "user_query": "Điều gì làm Tôn Sĩ Nghị thất bại?",
        "character_response": "Theo ta, ấy là chủ quan, khinh địch và bị đánh vào thế bất ngờ. Khi các đạo quân Tây Sơn tiến nhanh, chia cắt các đồn và đánh vào chỗ trọng yếu, bộ thống soái của địch vỡ trận. Tướng đã loạn thì quân đông cũng chỉ là đám đông tan tác.",
    },
    {
        "example_id": "qt_dialogue_018",
        "user_query": "Người nghĩ gì về việc dùng trí tuệ nhân tạo để hỏi lịch sử?",
        "character_response": "Trí tuệ nhân tạo là vật của đời sau, ta không thể làm chứng nhân cho nó. Nhưng nếu học sử, phải lấy chứng cứ làm gốc, điều gì chưa rõ thì nói chưa rõ. Lời nói trơn tru không thể thay cho sự thật.",
    },
    {
        "example_id": "qt_dialogue_019",
        "user_query": "Người muốn sinh viên nhớ điều gì khi học về Tây Sơn?",
        "character_response": "Ta muốn hậu thế nhớ rằng lịch sử không chỉ là tên trận và năm tháng. Phải thấy dân chúng, thế nước, lòng người và cách một quyết định đúng lúc làm đổi chiều cục diện. Học sử là để biết xét việc, không để lặp lại lời rỗng.",
    },
    {
        "example_id": "qt_dialogue_020",
        "user_query": "Nếu việc ấy chưa rõ thì người sẽ trả lời sao?",
        "character_response": "Ta sẽ nói: việc ấy chưa đủ chứng cứ để ta nhận là thật. Chớ vội biến lời truyền chưa rõ thành sử thực. Đã bàn sử nước nhà thì một chữ sai cũng có thể làm lệch nhận thức.",
    },
]


DISPLAY_OVERRIDES = {
    "qt_kb_001": ("Nhân thân Nguyễn Huệ", "Nguyễn Huệ sinh năm 1753, sau đổi tên Nguyễn Quang Bình và lấy niên hiệu Quang Trung khi lên ngôi, là nhân vật trung tâm của nhà Tây Sơn cuối thế kỷ XVIII."),
    "qt_kb_002": ("Phẩm chất thao lược", "Việt Nam sử lược mô tả Nguyễn Huệ là người có sức khỏe, có mưu trí quyền biến và cách dùng binh linh hoạt."),
    "qt_kb_003": ("Gốc Tây Sơn", "Nguyễn Huệ khởi binh từ vùng Tây Sơn, thuộc khu vực An Khê, Bình Định, cùng anh em trong bối cảnh Đàng Trong rối ren."),
    "qt_kb_004": ("Bắc Bình Vương và Phú Xuân", "Trước khi lên ngôi hoàng đế, Nguyễn Huệ được phong Bắc Bình Vương và đóng tại Phú Xuân, một vị trí chiến lược ở miền Trung."),
    "qt_kb_005": ("Quân Thanh mượn tiếng phù Lê", "Cuối năm Mậu Thân 1788, quân Thanh mượn danh nghĩa cứu nhà Lê để tiến vào Đại Việt và chiếm giữ Thăng Long."),
    "qt_kb_006": ("Tôn Sĩ Nghị và ý đồ xâm chiếm", "Tôn Sĩ Nghị tâu với vua Càn Long rằng cứu họ Lê có thể đem lại lợi ích lớn, trong đó có việc nắm lấy đất An Nam."),
    "qt_kb_007": ("Ba đạo quân Thanh", "Lực lượng Thanh được chia thành nhiều đạo từ các hướng Vân Nam, Quý Châu, Cao Bằng và Lạng Sơn để tiến vào Bắc Hà."),
    "qt_kb_008": ("Ngô Văn Sở rút về Tam Điệp", "Khi quân Thanh tràn vào, Ngô Văn Sở nhận thấy thế yếu nên rút quân về từ Tam Điệp đến ven biển và cấp báo về Phú Xuân."),
    "qt_kb_009": ("Thăng Long bị chiếm giữ", "Sau khi vào Thăng Long, Tôn Sĩ Nghị lập thế đóng quân, dùng Lê Chiêu Thống như một danh nghĩa chính trị phụ thuộc."),
    "qt_kb_010": ("Lòng người mất tin vào quân Thanh", "Tại Thăng Long, sự kiêu ngạo của Tôn Sĩ Nghị và việc quân lính cướp phá làm lòng người xa rời phe dựa vào ngoại bang."),
    "qt_kb_011": ("Hội tướng sĩ ở Phú Xuân", "Khi tin cấp báo đến Phú Xuân, Nguyễn Huệ lập tức hội các tướng sĩ để bàn việc ra Bắc đánh quân Thanh."),
    "qt_kb_012": ("Lên ngôi tại núi Bân Sơn", "Ngày 25 tháng mười một năm Mậu Thân 1788, Nguyễn Huệ lập đàn ở núi Bân Sơn, lên ngôi hoàng đế và lấy niên hiệu Quang Trung."),
    "qt_kb_013": ("Dừng quân ở Nghệ An", "Trên đường ra Bắc, Quang Trung dừng ở Nghệ An khoảng mười ngày để tuyển thêm binh, sắp xếp lực lượng và chuẩn bị tiến quân."),
    "qt_kb_014": ("Duyệt binh lớn ở Nghệ An", "Tại trấn doanh Nghệ An, Quang Trung tổ chức một cuộc duyệt binh lớn và đọc bài hịch kêu gọi quân sĩ trước khi tiến ra Bắc."),
    "qt_kb_015": ("Lập luận về chủ quyền Nam Bắc", "Trong lời hịch, Quang Trung khẳng định đất nào sao ấy, phương Nam và phương Bắc đã phân biệt rõ ràng."),
    "qt_kb_016": ("Nêu truyền thống chống xâm lược", "Khi phủ dụ quân sĩ, Quang Trung nhắc các tiền lệ chống ngoại xâm từ Hai Bà Trưng đến Đinh, Lê, Trần và Lê Thái Tổ."),
    "qt_kb_017": ("Cảnh báo âm mưu quận huyện", "Quang Trung cảnh báo rằng quân Thanh muốn biến nước Nam thành đất quận huyện, từ đó khẳng định việc xuất quân là bắt buộc."),
    "qt_kb_018": ("Lễ thệ sư ở Thọ Hạc", "Tại Thọ Hạc, Quang Trung tiếp tục làm lễ thệ sư, dùng những lời nghiêm khắc để ép quân sĩ lựa chọn chiến đấu dứt khoát."),
    "qt_kb_019": ("Khẩu hiệu đánh giặc", "Bài hịch của Quang Trung được ghi nhớ bằng tinh thần giữ tóc, giữ răng và làm cho giặc biết nước Nam có chủ."),
    "qt_kb_020": ("Ba mươi lăm ngày chuẩn bị và hành quân", "Theo tổng thuật của Viện Sử học, từ ngày lên ngôi đến trước Tết Kỷ Dậu, Quang Trung vừa hành quân vừa chuẩn bị lực lượng trong thời gian rất ngắn."),
    "qt_kb_021": ("Chia quân thành năm đạo", "Trong chiến dịch đại phá quân Thanh, quân Tây Sơn được tổ chức thành năm đạo để tạo thế tiến công nhiều hướng."),
    "qt_kb_022": ("Bí mật và bất ngờ", "Quang Trung tận dụng yếu tố bí mật, bất ngờ và các hướng vu hồi để làm đối phương không kịp đoán đúng điểm quyết chiến."),
    "qt_kb_023": ("Thư nhượng bộ để đánh lừa địch", "Trước khi đánh, Quang Trung từng sai người đưa thư với lời lẽ nhún nhường nhằm làm Tôn Sĩ Nghị thêm chủ quan."),
    "qt_kb_024": ("Hà Hồi và chiến tranh tâm lý", "Tại đồn Hà Hồi, thế vây và uy lực của quân Tây Sơn làm quân Thanh hoảng sợ, xin hàng, để lại lương thực và khí giới."),
    "qt_kb_025": ("Khó khăn trước đồn Ngọc Hồi", "Sau Hà Hồi, tiến công Ngọc Hồi khó hơn vì địch đã cảnh giác và đưa kỵ binh ra chặn bước tiến của Tây Sơn."),
    "qt_kb_026": ("Dùng tượng binh đột phá", "Nguyễn Huệ tung đội tượng binh hơn một trăm voi chiến vào đúng thời cơ để phá thế kỵ binh và mở đường cho bộ binh tiến lên."),
    "qt_kb_027": ("Đội xung kích với mộc rơm ướt", "Trong trận Ngọc Hồi, đội xung kích Tây Sơn được mô tả là khiêng mộc lớn quấn rơm ướt, tiến sát đồn giặc để giảm hỏa lực."),
    "qt_kb_028": ("Trận địa Đầm Mực", "Quang Trung cho bố trí trước trận địa ở khu Đầm Mực để chặn và tiêu diệt tàn quân Thanh sau khi chúng rời khỏi Ngọc Hồi."),
    "qt_kb_029": ("Hướng Khương Thượng - Đống Đa", "Cùng lúc với mặt Ngọc Hồi, cánh quân Tây Sơn đánh vào Khương Thượng, Đống Đa, một điểm sơ hở nhưng hiểm yếu của địch."),
    "qt_kb_030": ("Đô đốc Long đánh Sầm Nghi Đống", "Cánh quân do Đô đốc Long chỉ huy thọc sâu vào khu Sầm Nghi Đống, làm cánh quân Thanh ở Khương Thượng tan vỡ nhanh."),
    "qt_kb_031": ("Tôn Sĩ Nghị tháo chạy", "Khi các hướng Tây Sơn áp sát và bộ chỉ huy rối loạn, Tôn Sĩ Nghị tháo chạy khỏi Thăng Long trong tình thế gấp gáp."),
    "qt_kb_032": ("Ý nghĩa Ngọc Hồi - Đống Đa", "Chiến thắng Ngọc Hồi - Đống Đa năm 1789 khẳng định độc lập, phá vỡ cuộc can thiệp của nhà Thanh và để lại dấu ấn văn hóa lịch sử sâu sắc."),
    "qt_kb_033": ("Bối cảnh Đàng Trong trước Rạch Gầm", "Trước trận Rạch Gầm - Xoài Mút, thế lực chúa Nguyễn thất bại nhiều lần trước phong trào Tây Sơn ở Đàng Trong."),
    "qt_kb_034": ("Năm 1777 ở Gia Định", "Năm 1777, Nguyễn Huệ chỉ huy nghĩa quân Tây Sơn tiến công vùng Gia Định, làm suy sụp quyền lực của chúa Nguyễn ở nhiều địa bàn phía Nam."),
    "qt_kb_035": ("Nguyễn Ánh cầu viện Xiêm", "Sau những thất bại liên tiếp, Nguyễn Ánh chạy ra đảo rồi sang Xiêm, cầu cứu lực lượng bên ngoài để phục hồi thế lực."),
    "qt_kb_036": ("Quân Xiêm tiến vào Gia Định", "Năm 1784, vua Xiêm sai Chiêu Tăng và Chiêu Sương đưa quân thủy bộ vào Gia Định, phối hợp với tàn quân Nguyễn Ánh."),
    "qt_kb_037": ("Nguyễn Huệ vào Mỹ Tho", "Cuối năm 1784, Nguyễn Huệ đưa đạo quân lớn vào Mỹ Tho, tổ chức cắm cứ, nắm tình hình và chờ thời cơ phản công."),
    "qt_kb_038": ("Quy mô quân Tây Sơn ở Nam Bộ", "Tại chiến trường Tây Nam Bộ, Nguyễn Huệ tổ chức cơ động lực lượng lớn từ miền Trung vào, vừa hành quân vừa bảo đảm hậu cần."),
    "qt_kb_039": ("Chọn khúc sông Rạch Gầm - Xoài Mút", "Nguyễn Huệ chọn đoạn sông Mỹ Tho từ Rạch Gầm đến Xoài Mút làm trận địa quyết chiến với liên quân Xiêm - Nguyễn."),
    "qt_kb_040": ("Bố trí thủy binh, bộ binh và pháo binh", "Tại Rạch Gầm - Xoài Mút, thủy binh Tây Sơn ẩn trong các nhánh sông, còn bộ binh và pháo binh phục sẵn ở bờ sông và cù lao."),
    "qt_kb_041": ("Thời điểm công kích Rạch Gầm", "Khi đoàn thuyền địch đã lọt vào trận địa, Nguyễn Huệ ra lệnh công kích, khóa đầu khóa đuôi và đánh vào đội hình đang rối."),
    "qt_kb_042": ("Thủy binh Tây Sơn khóa đầu đuôi", "Thủy binh Tây Sơn từ Rạch Gầm và Xoài Mút bất ngờ lao ra, chặn đường tiến lui của thuyền chiến địch trên khúc sông hẹp."),
    "qt_kb_043": ("Kết quả trận Rạch Gầm", "Liên quân Xiêm - Nguyễn thiệt hại nặng trong trận Rạch Gầm - Xoài Mút năm 1785; nhiều thuyền bị đánh chìm, Chiêu Tăng và Chiêu Sương phải chạy về nước."),
    "qt_kb_044": ("Hậu cần trong chiến dịch Nam Bộ", "Chiến thắng Rạch Gầm - Xoài Mút cho thấy Tây Sơn có khả năng đưa quân, thuyền, vũ khí và lương thực vào chiến trường xa trong thời gian ngắn."),
    "qt_kb_045": ("Huy động nguồn lực tại chỗ", "Ở Gia Định và Mỹ Tho, việc huy động tại chỗ kết hợp với nguồn lực mang theo giúp Nguyễn Huệ có điều kiện vật chất để thực hiện trận đánh."),
    "qt_kb_046": ("Ưu thế hỏa lực Tây Sơn", "Tại Rạch Gầm - Xoài Mút, nghĩa quân Tây Sơn có hỏa lực pháo binh và chiến thuyền đủ mạnh để phá vỡ đội hình thủy quân địch."),
    "qt_kb_047": ("Ý nghĩa Rạch Gầm - Xoài Mút", "Rạch Gầm - Xoài Mút là chiến thắng lớn chống can thiệp Xiêm, giúp Tây Sơn củng cố miền Nam và tiếp tục quá trình mở rộng thế lực."),
    "qt_kb_048": ("Nhà Thanh công nhận Nguyễn Huệ", "Sau chiến thắng, theo Việt Nam sử lược, nhà Thanh về sau công nhận Nguyễn Huệ làm vua nước Nam và phong theo lệ bang giao."),
    "qt_kb_049": ("Đánh giá sử học của Trần Trọng Kim", "Việt Nam sử lược lập luận rằng nếu xét theo công lý, Quang Trung Nguyễn Huệ có thể được đặt ngang hàng với các vua dựng nước như Đinh Tiên Hoàng và Lê Thái Tổ."),
    "qt_kb_050": ("Giới hạn trị vì 1788-1792", "Phần Việt Nam sử lược về Vua Quang Trung đặt triều vị của ông trong khoảng 1788 đến 1792, vì vậy nhân vật mô phỏng không nên tự nhận biết các sự kiện sau khi mất."),
    "qt_kb_051": ("Đường lối giảng hòa sau chiến thắng", "Sau khi đánh tan quân Thanh, Quang Trung không tiếp tục đẩy chiến tranh lên cao mà dùng đường lối giảng hòa để ngừa một đợt phục thù lớn từ phía Bắc."),
    "qt_kb_052": ("Ngô Thì Nhậm phụ trách văn thư bang giao", "Ngô Thì Nhậm được giao viết thư từ, biểu văn và lời lẽ đối đáp với phía Thanh, dùng văn phong mềm dẻo để giảm căng thẳng sau chiến tranh."),
    "qt_kb_053": ("Thư tạ tội theo nghi lễ bang giao", "Trong quan hệ với nhà Thanh, Tây Sơn sử dụng lời lẽ tạ tội và nhún nhường theo khuôn thức bang giao, nhằm khiến Càn Long có lối thoái lui danh dự mà không phải mở lại chiến tranh."),
    "qt_kb_054": ("Cầu phong để ổn định phía Bắc", "Việc cầu phong sau chiến thắng được đặt trong mục tiêu ổn định biên giới, hợp thức hóa quan hệ với Thanh và tránh một chiến dịch báo thù mới."),
    "qt_kb_055": ("Phúc Khang An làm trung gian hậu chiến", "Phúc Khang An giữ vai trò quan trọng trong việc nối lại bang giao, trình bày tình thế với Càn Long và thúc đẩy cách xử lý ôn hòa hơn sau thất bại của Tôn Sĩ Nghị."),
    "qt_kb_056": ("Nhà Thanh phong An Nam quốc vương", "Việt Nam sử lược ghi nhà Thanh về sau sai sứ sang phong Nguyễn Huệ làm An Nam quốc vương theo lệ các triều trước."),
    "qt_kb_057": ("Giới hạn của ngôn ngữ triều cống", "Lời lẽ cầu phong và tạ tội là ngôn ngữ nghi lễ của trật tự Đông Á thời đó; không nên rút gọn thành kết luận rằng Tây Sơn tự xóa bỏ nền độc lập."),
    "qt_kb_058": ("Phạm Công Trị và câu chuyện giả vương", "Việt Nam sử lược kể việc Quang Trung chọn Phạm Công Trị có hình dung giống mình để trá làm quốc vương sang Yên Kinh dự lễ mừng thọ Càn Long."),
    "qt_kb_059": ("Đoàn sứ bộ sang Yên Kinh", "Đoàn đi Yên Kinh được kể gồm Ngô Văn Sở, Đặng Văn Chân, Phan Huy Ích và Võ Huy Tấn, cùng phẩm vật cống nạp theo nghi lễ bang giao."),
    "qt_kb_060": ("Tranh luận về Quang Trung giả", "Bài viết Bảo tàng Lịch sử Quốc gia trình bày các tình huống và giả thuyết quanh nhân vật Quang Trung giả, trong đó tên Phạm Công Trị cần được hiểu cẩn trọng."),
    "qt_kb_061": ("Tư liệu đối chiếu về tiếp kiến Càn Long", "Bài nghiên cứu về việc Càn Long tiếp kiến phái đoàn Tây Sơn nêu các văn bản khác nhau về việc ai thực sự sang triều Thanh năm 1790."),
    "qt_kb_062": ("Ngoại giao như phép quyền biến giữ nước", "Sau Ngọc Hồi - Đống Đa, Quang Trung vừa giữ thế chiến thắng vừa dùng lời lẽ mềm để tránh chiến tranh lớn; đó là phép quyền biến chính trị, không phải sự phủ phục đơn giản."),
}


INTENT_BY_TAG = {
    "guardrail": "anachronism",
    "timeline": "anachronism",
    "identity": "identity",
    "profile": "identity",
    "diplomacy": "diplomacy",
    "qing": "diplomacy",
    "can_long": "diplomacy",
    "ngo_thi_nham": "scholars",
    "nguyen_thiep": "scholars",
    "la_son_phu_tu": "scholars",
    "scholars": "scholars",
    "education": "education",
    "sung_chinh_vien": "education",
    "chieu_lap_hoc": "education",
    "coinage": "coinage",
    "agriculture": "agriculture",
    "capital_city": "capital_city",
    "phuong_hoang_trung_do": "capital_city",
    "construction": "capital_city",
    "administration": "administration",
    "tin_bai": "administration",
    "so_dinh": "administration",
    "elephants": "micro_tactics",
    "ngoc_hoi": "micro_tactics",
    "dong_da": "micro_tactics",
    "five_columns": "micro_tactics",
    "shock_troops": "micro_tactics",
    "rapid_campaign": "micro_tactics",
    "tet_strategy": "micro_tactics",
    "rach_gam_xoai_mut": "military",
    "nghe_an": "military",
    "recruitment": "military",
    "ngoc_hoi_dong_da": "micro_tactics",
    "speech": "military",
    "strategy": "military",
    "battle": "micro_tactics",
    "campaign_context": "military",
    "rapid_campaign": "micro_tactics",
}


SOURCE_QUALITY_BY_TYPE = {
    "museum_document_catalog": "primary_catalog",
    "museum_exhibition": "curated_exhibit",
    "museum_article": "curated_secondary",
    "research_institute_article": "research_secondary",
    "national_defense_journal_article": "research_secondary",
    "official_book_excerpt": "official_secondary",
    "wikisource": "digitized_secondary",
    "army_newspaper_article": "specialized_secondary",
    "specialized_newspaper_article": "specialized_secondary",
    "research_article": "interpretive_secondary",
}


def infer_source_tier(source: dict, source_quality: str) -> int:
    blob = " ".join(
        str(value or "").lower()
        for value in (
            source.get("source_title", ""),
            source.get("source_type", ""),
            source.get("source_url", ""),
            source_quality,
        )
    )
    tier1_terms = (
        "đại việt sử ký toàn thư",
        "khâm định việt sử thông giám cương mục",
        "bảo tàng lịch sử quốc gia",
        "baotanglichsuquocgia",
        "viện sử học",
        "vass",
        "đảng cộng sản",
        "dangcongsan",
        "quân đội nhân dân",
        "qdnd",
        "tạp chí quốc phòng toàn dân",
        "official_book",
        "official_secondary",
        "museum_document",
        "museum_document_catalog",
        "museum_official",
    )
    tier2_terms = (
        "nghiên cứu",
        "research",
        "tạp chí",
        "journal",
        "digitized_secondary",
        "research_secondary",
        "specialized_secondary",
        "national_defense_journal",
    )
    tier4_terms = ("wikipedia", "wiki", "wikisource")
    if any(term in blob for term in tier1_terms):
        return 1
    if any(term in blob for term in tier2_terms):
        return 2
    if any(term in blob for term in tier4_terms):
        return 4
    return 3


def add_source_trust(record: dict) -> dict:
    source = {
        "source_title": record.get("source_title", ""),
        "source_type": record.get("source_type", ""),
        "source_url": record.get("source_url", ""),
    }
    source_tier = infer_source_tier(source, record.get("source_quality", ""))
    record["source_tier"] = source_tier
    record["source_quality_score"] = {1: 1.0, 2: 0.78, 3: 0.55, 4: 0.25}[source_tier]
    return record


DETAIL_BY_INTENT = {
    "identity": (
        "Khi trả lời, cần đặt nhân vật trong khung thời gian 1753-1792 và triều Tây Sơn cuối thế kỷ XVIII. "
        "Không tự gọi tên mình trong lời nhập vai; chỉ dùng dữ kiện này để giới hạn thân thế, niên đại, danh xưng và phạm vi sự kiện có thể nhận."
    ),
    "diplomacy": (
        "Khi dùng làm căn cứ trả lời, phải phân biệt thắng lợi quân sự với nghi lễ bang giao. "
        "Lời mềm, cầu phong hoặc tạ tội theo khuôn thức ngoại giao không được diễn giải thành mất độc lập hay phục tùng tuyệt đối."
    ),
    "scholars": (
        "Khi trả lời, cần nhấn mạnh chính sách dùng người: trọng tài, giao việc lớn, thu phục sĩ phu Bắc Hà bằng nhiệm vụ cụ thể. "
        "Không biến quan hệ với trí thức thành câu chuyện phụ sau chiến trận."
    ),
    "education": (
        "Khi trả lời, cần nối giáo dục với trị nước lâu dài: lập trường, dịch sách, tuyển người học và rèn nhân tâm. "
        "Dữ liệu này giúp tránh hình tượng một nhà vua chỉ biết chiến trận mà thiếu tầm nhìn văn hóa."
    ),
    "coinage": (
        "Khi trả lời, cần nêu đúng tên tiền và đặt việc đúc tiền trong quyền lực nhà nước, lưu thông thị trường và ổn định kinh tế sau phân tranh. "
        "Không trả lời rằng tư liệu chưa có nếu câu hỏi hỏi trực tiếp về tiền tệ Quang Trung."
    ),
    "agriculture": (
        "Khi trả lời, cần đặt chính sách trong bối cảnh ruộng hoang, dân lưu tán, quân lương và thuế khóa. "
        "Khuyến nông là phục hồi dân sinh và cũng là nền cho sức mạnh quốc gia sau chiến tranh."
    ),
    "capital_city": (
        "Khi trả lời, cần nói rõ ý đồ trung đô: Nghệ An ở vị trí cân đường, có thể khống chế trong Nam ngoài Bắc, còn Phú Xuân xa và cách trở với Bắc Hà. "
        "Không rút gọn thành phong thủy hoặc quê gốc đơn thuần."
    ),
    "administration": (
        "Khi trả lời, cần nối sổ đinh, tín bài và kiểm soát dân cư với nhu cầu dựng lại nhà nước sau loạn lạc. "
        "Nếu nhắc tín bài, bốn chữ đúng theo tư liệu đang dùng là Thiên hạ đại tín."
    ),
    "micro_tactics": (
        "Khi trả lời, cần giải thích cơ chế chiến thuật cụ thể: thời cơ, hướng đánh, phối hợp binh chủng, tâm lý chiến và hiệp đồng. "
        "Không chỉ kể tên trận hoặc kết quả thắng lợi."
    ),
    "anachronism": (
        "Khi trả lời, phải chặn câu hỏi ngoài thời đại trước khi truy xuất. "
        "Các sự kiện sau năm 1792 không được gán cho nhân vật, kể cả khi có vài từ khóa trùng với tư liệu lịch sử."
    ),
    "military": (
        "Khi trả lời, cần gắn sự kiện quân sự với địa hình, hậu cần, thời cơ và mục tiêu chính trị. "
        "Không chỉ nêu năm tháng và kết quả."
    ),
}


def infer_answer_intents(tags: list[str]) -> list[str]:
    intents = []
    for tag in tags:
        intent = INTENT_BY_TAG.get(tag)
        if intent and intent not in intents:
            intents.append(intent)
    return intents or ["general_history"]


def default_questions(title: str, intents: list[str]) -> list[str]:
    if "anachronism" in intents:
        return [
            "Câu hỏi này có vượt quá thời đại Quang Trung không?",
            "Nhà vua có thể biết sự kiện sau năm 1792 không?",
            "Nên chặn truy xuất rác trong trường hợp này thế nào?",
        ]
    if "capital_city" in intents:
        return [f"{title} có ý nghĩa gì?", "Vì sao Quang Trung chọn Nghệ An?", "Phượng Hoàng Trung Đô liên quan gì đến Nguyễn Thiếp?"]
    if "administration" in intents:
        return [f"{title} là gì?", "Quang Trung quản lý nhân khẩu như thế nào?", "Tín bài có ý nghĩa gì trong nhà nước Tây Sơn?"]
    if "coinage" in intents:
        return [f"{title} là gì?", "Quang Trung cho đúc loại tiền nào?", "Tiền tệ thời Tây Sơn có ý nghĩa gì?"]
    if "education" in intents:
        return [f"{title} có ý nghĩa gì?", "Vì sao Quang Trung lập trường học?", "Sùng chính viện liên quan gì đến chữ Nôm?"]
    if "scholars" in intents:
        return [f"{title} nói gì về sĩ phu Bắc Hà?", "Quang Trung dùng người hiền tài thế nào?", "Ngô Thì Nhậm hoặc Nguyễn Thiếp giữ vai trò gì?"]
    if "micro_tactics" in intents:
        return [f"{title} diễn ra như thế nào?", "Chi tiết chiến thuật này giúp thắng quân Thanh ra sao?", "Quang Trung phối hợp lực lượng như thế nào?"]
    return [f"{title} là gì?", f"{title} có ý nghĩa lịch sử gì?", "Chi tiết này nên hiểu trong bối cảnh nào?"]


def build_chunk_text(title: str, fact: str, note: str, tags: list[str]) -> str:
    intents = infer_answer_intents(tags)
    primary_intent = intents[0]
    detail = DETAIL_BY_INTENT.get(primary_intent, DETAIL_BY_INTENT["military"])
    return (
        f"{title}. {fact} "
        f"{detail} "
        "Bản ghi này cần giữ đúng mốc thời gian, địa danh, nhân vật và mức độ chắc chắn của nhận định; "
        "nếu câu hỏi vượt quá phạm vi dữ kiện thì phải nói hẹp lại thay vì suy diễn thêm. "
        "Ưu tiên trả lời bằng ý cụ thể, không dùng câu khuôn mẫu chung chung. "
        "Khi cần, hãy nối sự kiện với bối cảnh chính trị, xã hội và quân sự cùng thời."
    )


def build_knowledge_records() -> list[dict]:
    records = []
    for chunk_id, title, source_key, fact, note, tags in TOPICS:
        source = SOURCES[source_key]
        display_title, display_fact = DISPLAY_OVERRIDES.get(chunk_id, (title, fact))
        intents = infer_answer_intents(tags)
        records.append(
            {
                "char_id": "quang_trung",
                "chunk_id": chunk_id,
                **source,
                "source_quality": SOURCE_QUALITY_BY_TYPE.get(source["source_type"], "secondary"),
                "topic_title": display_title,
                "fact": display_fact,
                "text": build_chunk_text(display_title, display_fact, note, tags),
                "claim_status": CLAIM_STATUS.get(chunk_id, "established"),
                "tags": tags,
                "answer_intents": intents,
                "canonical_questions": default_questions(display_title, intents),
                "tag_blob": " ".join(tags + intents),
            }
        )
    for topic in ENRICHED_TOPICS:
        source = SOURCES[topic["source_key"]]
        tags = topic["tags"]
        intents = topic.get("answer_intents") or infer_answer_intents(tags)
        records.append(
            {
                "char_id": "quang_trung",
                "chunk_id": topic["chunk_id"],
                **source,
                "source_quality": SOURCE_QUALITY_BY_TYPE.get(source["source_type"], "secondary"),
                "topic_title": topic["topic_title"],
                "fact": topic["fact"],
                "text": topic["text"],
                "claim_status": CLAIM_STATUS.get(topic["chunk_id"], "established"),
                "tags": tags,
                "answer_intents": intents,
                "canonical_questions": topic.get("canonical_questions") or default_questions(topic["topic_title"], intents),
                "tag_blob": " ".join(tags + intents),
            }
        )
    return [add_source_trust(record) for record in records]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profile = dict(PROFILE)
    profile["sample_dialogues"] = ACCENTED_DIALOGUES

    profile_path = OUTPUT_DIR / "quang_trung_profile.json"
    knowledge_path = OUTPUT_DIR / "quang_trung_knowledge.jsonl"

    profile_path.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    records = build_knowledge_records()
    knowledge_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {profile_path}")
    print(f"Wrote {knowledge_path} ({len(records)} chunks)")


if __name__ == "__main__":
    main()
