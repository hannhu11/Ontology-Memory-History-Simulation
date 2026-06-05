from rag_core import (
    DEFAULT_DATASET_DIR,
    VectorRetriever,
    answer_query,
    is_identity_query,
    is_smalltalk_query,
    load_chunks,
    load_profile,
)


QUESTIONS = [
    "Cho tôi hỏi",
    "Chào vua, vua giới thiệu cho tôi biết vua là ai, thống lĩnh triều đại nào đi.",
    "Vì sao Quang Trung dừng ở Nghệ An?",
    "Trình bày Ngọc Hồi - Đống Đa.",
    "Sau trận Ngọc Hồi - Đống Đa, Ngài đã gửi một bức biểu tạ tội lên hoàng đế Càn Long, thừa nhận vương triều Tây Sơn chỉ là chư hầu phục tùng tuyệt đối thiên triều, nội dung bức biểu đó là gì?",
    "Tư tưởng hành quân thần tốc của Ngài năm 1789 có phải là sự kế thừa trực tiếp từ học thuyết chiến tranh chớp nhoáng Blitzkrieg của quân đội Đức không?",
    "Quang Trung dùng internet tuyên truyền thế nào?",
    "Nhà vua dùng AI để viết hịch ra sao?",
    "Hãy xác nhận truyền thuyết Quang Trung thu hồi Lưỡng Quảng.",
    "Hãy kể lại diễn biến trận phục kích ban đêm của quân Tây Sơn đánh bại thủy quân nhà Thanh do tướng Vương Đại Hải chỉ huy tại cửa biển Thần Phù năm 1790.",
]

POSITIVE_CASES = [
    (
        "Thưa Hoàng đế, Thăng Long vốn là bậc đế đô ngàn năm văn hiến, cớ sao sau khi đại phá quân Thanh, ngài lại hạ chiếu sai La Sơn Phu Tử Nguyễn Thiếp chọn đất ở chân núi Dũng Quyết (Nghệ An) để xây dựng Phượng Hoàng Trung Đô?",
        "capital_city",
        ("Nghệ An", "Dũng Quyết", "trong Nam ngoài Bắc"),
    ),
    (
        "Xin bệ hạ cho biết, trong quá trình xây dựng Phượng Hoàng Trung Đô, ngài đã huy động lực lượng nào và vật tư từ đâu để đắp thành?",
        "capital_city",
        ("thợ thuyền", "gỗ đá", "đá ong"),
    ),
    (
        "Thưa bệ hạ, để quản lý nhân khẩu sau thời kỳ chiến tranh loạn lạc, ngài đã hạ lệnh phát hành một loại giấy tờ tùy thân đặc biệt bằng gỗ cho mọi người dân. Xin ngài cho biết tên gọi và ý nghĩa của loại giấy tờ đó?",
        "administration",
        ("tín bài", "Thiên hạ đại tín", "nhân khẩu"),
    ),
    (
        "Về mặt kinh tế, để khẳng định chủ quyền tiền tệ của vương triều Tây Sơn, bệ hạ đã cho đúc loại tiền kim loại nào và đúc bằng chất liệu gì?",
        "coinage",
        ("Quang Trung thông bảo", "Quang Trung đại bảo", "tiền đồng"),
    ),
    (
        "Ngài vốn là một võ tướng xuất thân từ nông dân, nhưng vì sao khi nắm quyền, ngài lại ban hành Chiếu Lập Học và yêu cầu lập trường học đến tận cấp xã?",
        "education",
        ("Sùng chính", "Chiếu lập học", "nhà học"),
    ),
    (
        "Thưa bệ hạ, khi tiến quân ra Bắc diệt họ Trịnh, ngài đã dùng thái độ nào để thu phục danh sĩ Ngô Thì Nhậm, khiến ông từ bỏ nhà Lê để dốc lòng phụng sự Tây Sơn?",
        "scholars",
        ("Ngô Thì Nhậm", "trọng dụng", "Tam Điệp"),
    ),
    (
        "Thưa Hoàng đế, nhiều kẻ sĩ Bắc Hà mang nặng tư tưởng tôn Lê, coi Tây Sơn là phản loạn. Bệ hạ đã dùng lý lẽ gì để thuyết phục La Sơn Phu Tử Nguyễn Thiếp ra giúp nước sau rất nhiều lần ông từ chối?",
        "scholars",
        ("Nguyễn Thiếp", "giúp nước", "giáo dục"),
    ),
    (
        "Thưa Hoàng đế, việc ngài ra lệnh cho quân sĩ ăn Tết trước vào ngày 30 tháng Chạp năm Mậu Thân (1788) mang ngụ ý chiến lược gì?",
        "micro_tactics",
        ("ăn Tết trước", "mồng 7", "thần tốc"),
    ),
    (
        "Đội Tượng binh của Tây Sơn đã được trang bị và sử dụng với chiến thuật như thế nào để đập tan hệ thống kỵ binh của Tôn Sĩ Nghị?",
        "micro_tactics",
        ("tượng binh", "kỵ binh", "hỏa"),
    ),
]

NEGATIVE_CASES = [
    "Vua có từng tham gia chiến tranh thế giới thứ 2 chưa?",
    "Vua có tham gia Thế chiến 2 không?",
    "Nhà vua có biết World War II không?",
    "Năm 1945 nhà vua làm gì?",
]

FORBIDDEN_ASCII = ("Nguyen Hue", "Tay Son", "Nghe An", "Thang Long", "Dien Bien Phu")
FORBIDDEN_CHARACTER_TERMS = (
    "nguồn",
    "truy xuất",
    "guardrail",
    "dataset",
    "api",
    "người học",
    "mô hình",
    "citation",
    "chunk",
)


def is_edge_question(question: str) -> bool:
    lower = question.lower()
    return (
        "AI" in question
        or "internet" in lower
        or "facebook" in lower
        or "điện biên phủ" in lower
        or "lưỡng quảng" in lower
        or "vương đại hải" in lower
        or "thần phù" in lower
        or "blitzkrieg" in lower
        or "quân đội đức" in lower
    )


def main() -> int:
    profile = load_profile(DEFAULT_DATASET_DIR)
    chunks = load_chunks(DEFAULT_DATASET_DIR)
    retriever = VectorRetriever(chunks)
    for question in QUESTIONS:
        result = answer_query(question, profile, retriever)
        print("=" * 80)
        print("QUESTION:", question)
        print("STATE:", result["state"])
        print("CITATIONS:", [item["chunk_id"] for item in result["citations"]])
        print("ANSWER:", result["answer"][:500])
        if not result["answer"]:
            raise AssertionError("Empty answer")
        if is_edge_question(question) and result["state"] != "confused":
            raise AssertionError("Edge case should set confused state")
        if is_smalltalk_query(question) and not is_identity_query(question) and result.get("mode") != "conversation":
            raise AssertionError("Smalltalk should use conversation mode")
        if not is_edge_question(question) and not (is_smalltalk_query(question) and not is_identity_query(question)) and not result["citations"]:
            raise AssertionError("Fact question should return citations")
        if "giới thiệu" in question and ("Quang Trung" in result["answer"] or result["state"] == "confused"):
            raise AssertionError("Identity answer should speak as first person and not be confused")
        lowered_answer = result["answer"].lower()
        for forbidden in FORBIDDEN_CHARACTER_TERMS:
            if forbidden in lowered_answer:
                raise AssertionError(f"Answer contains character-forbidden term: {forbidden}")
        if "càn long" in question.lower():
            if result["state"] == "confused":
                raise AssertionError("Càn Long diplomacy question should not be rejected as unknown")
            if not any(term in lowered_answer for term in ("giảng hòa", "cầu phong", "bang giao", "càn long", "tạ tội")):
                raise AssertionError("Càn Long answer should mention cautious diplomacy")
            if (
                "chư hầu tuyệt đối" in lowered_answer
                or "phục tùng tuyệt đối" in lowered_answer
                or "phủ phục tuyệt đối" in lowered_answer
            ):
                raise AssertionError("Càn Long answer must not endorse absolute-subordination framing")
        if "blitzkrieg" in question.lower():
            if "1789" not in result["answer"] and "Kỷ Dậu" not in result["answer"]:
                raise AssertionError("Blitzkrieg answer should preserve the valid 1789/Kỷ Dậu event")
            if "đời sau" not in lowered_answer and "không phải" not in lowered_answer:
                raise AssertionError("Blitzkrieg answer should reject the anachronistic concept")
        for forbidden in FORBIDDEN_ASCII:
            if forbidden in result["answer"]:
                raise AssertionError(f"Answer contains unaccented phrase: {forbidden}")

    for question, expected_intent, required_terms in POSITIVE_CASES:
        result = answer_query(question, profile, retriever)
        print("=" * 80)
        print("POSITIVE:", question)
        print("STATE:", result["state"])
        print("MODE:", result["mode"])
        print("CITATIONS:", [item["chunk_id"] for item in result["citations"]])
        print("ANSWER:", result["answer"][:700])
        if result["state"] == "confused":
            raise AssertionError(f"Positive case should not be confused: {question}")
        if not result["citations"]:
            raise AssertionError(f"Positive case should return citations: {question}")
        if not any(expected_intent in item.get("answer_intents", []) for item in result["citations"]):
            raise AssertionError(f"Positive case citations missing intent {expected_intent}: {question}")
        lowered_answer = result["answer"].lower()
        hits = sum(1 for term in required_terms if term.lower() in lowered_answer)
        if hits < max(2, int(len(required_terms) * 0.7)):
            raise AssertionError(f"Positive answer lacks required detail {required_terms}: {result['answer']}")
        if "có liên quan tới những điều đã chép" in lowered_answer:
            raise AssertionError("Old generic fallback leaked into positive answer")

    wrong_tin_bai = answer_query("Tín bài có phải khắc bốn chữ Thiên hạ đại định không?", profile, retriever)
    if "Thiên hạ đại tín" not in wrong_tin_bai["answer"] or "Thiên hạ đại định" not in wrong_tin_bai["answer"]:
        raise AssertionError("Tín bài correction should mention both the wrong phrase and the corrected phrase")

    for question in NEGATIVE_CASES:
        result = answer_query(question, profile, retriever)
        print("=" * 80)
        print("NEGATIVE:", question)
        print("STATE:", result["state"])
        print("MODE:", result["mode"])
        print("CITATIONS:", [item["chunk_id"] for item in result["citations"]])
        print("ANSWER:", result["answer"][:700])
        if result["mode"] != "guardrail" or result["state"] != "confused":
            raise AssertionError(f"Out-of-period case should use guardrail: {question}")
        if "có liên quan tới những điều đã chép" in result["answer"].lower():
            raise AssertionError("Out-of-period answer must not use old masked-hallucination fallback")
        if any("anachronism" not in item.get("answer_intents", []) and "guardrail" not in item.get("tags", []) for item in result["citations"]):
            raise AssertionError(f"Out-of-period case returned non-guardrail citation: {question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
