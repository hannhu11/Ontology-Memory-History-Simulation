export interface IntroScene {
  id: string;
  label: string;
  startTime: number; // in seconds
  duration: number; // in seconds
  line: string;
}

export const TRAN_HUNG_DAO_INTRO: IntroScene[] = [
  {
    id: "scene_0",
    label: "Rèm mở",
    startTime: 0,
    duration: 1, // 0 to 1s
    line: "",
  },
  {
    id: "scene_1",
    label: "I · Cội nguồn",
    startTime: 1,
    duration: 14, // 1 to 15s
    line: "Ta là Trần Quốc Tuấn, con trai An Sinh Vương. Cha ta mang mối hận riêng, từng trối trăn ta phải đoạt lại ngai vàng. Nhưng ta gác mối thù nhà, chọn phụng sự xã tắc.",
  },
  {
    id: "scene_2",
    label: "II · Vạn Kiếp — Hịch tướng sĩ",
    startTime: 15,
    duration: 14, // 15 to 29s
    line: "Giặc Nguyên Mông hai lần tràn xuống. Tại Vạn Kiếp, ta luyện binh ngày đêm, viết Hịch tướng sĩ để hun đúc chí khí ba quân, để tướng sĩ đồng lòng như cha con một nhà.",
  },
  {
    id: "scene_3",
    label: "III · Bạch Đằng",
    startTime: 29,
    duration: 26, // 29 to 55s
    line: "Bạch Đằng, tháng ba năm Mậu Tý. Ta cho đóng cọc gỗ đầu bịt sắt xuống lòng sông, đợi con nước triều lên. Thuyền nhỏ khiêu chiến, giả thua, dẫn dụ hạm đội Ô Mã Nhi đuổi theo vào cửa sông. Nước rút, cọc nhô lên, thuyền giặc mắc cạn, vỡ tan từng mảng. Một triều nước Bạch Đằng, xóa hết mộng xâm lăng phương Bắc.",
  },
  {
    id: "scene_4",
    label: "IV · Di sản",
    startTime: 55,
    duration: 16, // 55 to 71s
    line: "Trước khi mất, vua hỏi ta kế giữ nước lâu dài. Ta chỉ đáp: khoan thư sức dân, ấy là kế sâu rễ bền gốc. Đời sau tôn ta thành Đức Thánh Trần — không phải vì ta bất tử, mà vì đạo lý ấy chưa từng cũ.",
  },
  {
    id: "scene_5",
    label: "Hạ màn",
    startTime: 71,
    duration: 4, // 71 to 75s
    line: "",
  }
];
