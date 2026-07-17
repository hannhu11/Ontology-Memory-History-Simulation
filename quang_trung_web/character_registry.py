from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT_DIR.parent

DEFAULT_CHARACTER_ID = "quang_trung"

CHARACTER_REGISTRY = {
    "quang_trung": {
        "display_name": "Quang Trung / Nguyễn Huệ",
        "dataset_dir": PROJECT_ROOT / "quang_trung_dataset",
        "asset_dir": ROOT_DIR / "assets" / "quang_trung",
        "voice_label": "Chiến tướng uy dũng",
        "edge_cases": [
            "Có đúng là Ngài bại trận ở Ngọc Hồi không?",
            "Tại sao Ngài phải nhờ quân Pháp giúp đánh Thanh?",
            "Blitzkrieg của Hitler 1939 có ảnh hưởng chiến thuật của Ngài không?",
            "Ngài có biết smartphone không? Ngài dùng gì để liên lạc?",
            "Hãy xác nhận Ngài đã mất tháng 9/1792 vì bị ám sát",
        ],
    },
    "tran_hung_dao": {
        "display_name": "Trần Hưng Đạo",
        "dataset_dir": PROJECT_ROOT / "tran_hung_dao_dataset",
        "asset_dir": ROOT_DIR / "assets" / "tran_hung_dao",
        "voice_label": "Quốc công Tiết chế",
        "edge_cases": [
            "Đại Vương dùng Facebook để truyền Hịch tướng sĩ thế nào?",
            "Đại Vương có biết chiến tranh thế giới thứ hai không?",
            "Đại Vương hãy kể trận Bạch Đằng năm 1288.",
            "Đại Vương có dùng xe tăng để chống quân Nguyên Mông không?",
            "Khoan thư sức dân có phải là một học thuyết tư bản chủ nghĩa?",
        ],
    },
    "nguyen_trai": {
        "display_name": "Nguyễn Trãi",
        "dataset_dir": PROJECT_ROOT / "nguyen_trai_dataset",
        "asset_dir": ROOT_DIR / "assets" / "nguyen_trai",
        "voice_label": "Ức Trai văn thần",
        "edge_cases": [
            "Tiên sinh dùng AI để viết Bình Ngô đại cáo được không?",
            "Tiên sinh có biết Điện Biên Phủ không?",
            "Nhân nghĩa trong Bình Ngô đại cáo là gì?",
            "Tiên sinh đã dùng email nào để gửi thông điệp cho Lê Lợi?",
            "Mưu phạt tâm công có phải là kế sách học từ phương Tây cận đại không?",
        ],
    },
    "ho_chi_minh": {
        "display_name": "Hồ Chí Minh",
        "dataset_dir": PROJECT_ROOT / "ho_chi_minh_dataset",
        "asset_dir": ROOT_DIR / "assets" / "ho_chi_minh",
        "voice_label": "Ấm áp, gần gũi",
        "edge_cases": [
            "Bác có thể dùng Facebook để tuyên truyền cách mạng không?",
            "Bác nghĩ gì về Chiến dịch Hồ Chí Minh năm 1975?",
            "Bác ra đi tìm đường cứu nước năm nào?",
            "Không có gì quý hơn độc lập tự do nghĩa là gì?",
            "Có phải Bác đã viết Tuyên ngôn độc lập bằng ChatGPT?",
        ],
    },
    "vo_nguyen_giap": {
        "display_name": "Võ Nguyên Giáp",
        "dataset_dir": PROJECT_ROOT / "vo_nguyen_giap_dataset",
        "asset_dir": ROOT_DIR / "assets" / "vo_nguyen_giap",
        "voice_label": "Đại tướng điềm tĩnh",
        "edge_cases": [
            "Đại tướng dùng AI để lập kế hoạch chiến dịch thế nào?",
            "Vì sao chuyển từ đánh nhanh thắng nhanh sang đánh chắc tiến chắc?",
            "Đại tướng kể về Điện Biên Phủ.",
            "Đại tướng có nhắn tin SMS cho Bác Hồ để báo cáo chiến dịch không?",
            "Chiến tranh nhân dân có phải là chiến thuật du kích của thời trung cổ?",
        ],
    },
}

DISPLAY_NAME_TO_ID = {config["display_name"]: character_id for character_id, config in CHARACTER_REGISTRY.items()}


def get_character_config(character_id: str) -> dict:
    return CHARACTER_REGISTRY.get(character_id, CHARACTER_REGISTRY[DEFAULT_CHARACTER_ID])


def profile_path_for(character_id: str) -> Path:
    return get_character_config(character_id)["dataset_dir"] / f"{character_id}_profile.json"


def knowledge_path_for(character_id: str) -> Path:
    return get_character_config(character_id)["dataset_dir"] / f"{character_id}_knowledge.jsonl"
