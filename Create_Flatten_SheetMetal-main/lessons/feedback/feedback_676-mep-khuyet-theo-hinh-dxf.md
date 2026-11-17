---
name: feedback-676-mep-khuyet-theo-hinh-dxf
description: Rãnh/khuyết ở mép: vị trí mép lấy theo hình trong DXF khách; con số dim PDF có thể kết thúc ở tâm cung R chứ không ở mép ngoài (48 so với 50)
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-16T10:10:00Z
---

Đơn 521116-10, mã 26-068885 (SUS304 t3, 610 x 60, bài giao 16/11/2026): so từng entity (17 entity mỗi bản). Khác biệt duy nhất đáng kể là rãnh khuyết góc dưới phải: F vẽ mép đứng rãnh tại x = 562 (rộng 48 tính từ mép ngoài 610), T vẽ x = 560.005 (rộng 50). Các vòng bo R2, lỗ φ10 / φ4.2 (y = 10 / 52), chiều cao rãnh 28.25 (= 60 - 31.75) và biên dạng còn lại giống nhau. Chênh phụ: T dùng toạ độ DXF khách (610.005; lỗ x = 85 / 305.003 / 525.005; mép phải 608.005), F làm tròn theo PDF (610; 305; 525), lệch 0.005, bỏ qua.

DXF khách (26-13600-241): mép rãnh cách mép ngoài đúng 50; DIMENSION 48 chạy từ mép rãnh tới tâm cung R2 phía phải (cách mép ngoài 2). Trên bản scan, đường gióng 48 phía phải cũng lùi vào so với đường gióng 610/85 ở mép ngoài.

**Why:** AI coi số 48 là khoảng từ mép rãnh tới mép ngoài, không đo pixel đầu mũi tên (SKILL dòng 39) và không đối chiếu hình LINE/ARC của DXF khách. F không có Flag 1 vì chữ số PDF và DXF đều là 48. Khách 676 có quy tắc "PDF là chuẩn" nhưng ở đây hình DXF và đúng chân dim cùng cho 50. Nguyên nhân là suy đoán từ kết quả.

**How to apply:** có DXF khách thì đối chiếu từng mép/rãnh/lỗ giữa hình DXF (LINE/ARC, cả trong BLOCK) với con số PDF, đo cả chân dim (mép ngoài hay tâm/tiếp điểm R); lệch thì Flag 1 kèm số cả hai. Phát chốt 17/11/2026: khách 676 đổi thành "hình DXF khác số PDF thì theo DXF và Flag 1" (đã sửa rules\Quy_Tac_Theo_Ma_Khach_AnDanh.md dòng 11 và 39).
