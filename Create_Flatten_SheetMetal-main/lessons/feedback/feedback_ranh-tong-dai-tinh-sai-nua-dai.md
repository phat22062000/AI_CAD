---
name: feedback-ranh-tong-dai-tinh-sai-nua-dai
description: Rãnh/lỗ dài ghi "20X5" (長穴): 20 là tổng dài hai đầu bo (tâm-tâm = 20 - 5 = 15); script dựng tay lấy nửa dài tâm-tâm = 5 nên rãnh chỉ dài 15
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-19T13:00:00+07:00
---

Đơn 521116-14, mã 26-068416 và 26-068417 (bản gương của nhau, vẽ 16/11/2026, vẽ lại 19/11/2026 sau khi khách trả lời; SPCC t3.2): bảng ghi chú ghi 長穴 "20X5" (sửa tay thay "M5×20mm"). Hai rãnh ở đáy: bản AI (F) dài tổng 15 (cung R2.5, tâm cách nhau 10), bản đúng (T) dài tổng 20 (tâm cách nhau 15). Rộng 5, vị trí tâm rãnh (y = 15 và 69, cách mép 15) và mọi thứ còn lại giống nhau. `diff_tf.py`: 8 entity rãnh khác (4 cung và 4 đường), khớp 58.3% cho cả hai mã.

Bằng chứng nguyên nhân (log vẽ lại 19/11): script ghi chú "2 ranh 20x5" nhưng dựng `a, b = cx - 5.0, cx + 5.0` (tâm hai cung cách nhau 10, tổng dài 15) thay vì `cx - 7.5, cx + 7.5` (cách nhau 15, tổng dài 20). Lần vẽ đầu (16/11) dùng hàm `slot(length=20, width=5)` với `h = length/2 - r = 7.5` và ra đúng 20. Lần vẽ lại viết tay công thức mới, trừ nhầm độ rộng thay vì nửa độ rộng (20/2 - 5 thay vì 20/2 - 2.5). Không có bước nào in ra tổng dài của rãnh để đối chiếu với ghi chú.

**Why:** lỗi số học trong script dựng tay; script đã dựng rãnh đúng lần đầu nhưng lần vẽ lại bỏ hàm chuẩn. `dxf_check` không nêu kích thước rãnh, `doi_chieu_khach.py` không chạy được vì đơn không có DXF khách. Nguyên nhân đã xác định (có bằng chứng trong log), không phải suy đoán.

**How to apply:** "NxM" ở 長穴 (hoặc "N x M" kèm hình rãnh) là tổng dài ngoài-ngoài N và rộng M; tâm-tâm = N - M, nửa dài tâm-tâm = (N - M) / 2. Dùng một hàm dựng rãnh chung (tổng dài, rộng) rồi đọc lại từ DXF vừa lưu: đo khoảng từ điểm xa nhất của cung trái đến cung phải, phải ra đúng N. Vẽ lại một mã đã làm thì không viết lại công thức: dùng lại hàm của lần trước. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]].
