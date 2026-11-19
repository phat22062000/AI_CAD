---
name: feedback-cho-uon-75-do-dung-kich-thuoc-danh-nghia
description: Chỗ uốn cánh nghiêng (góc trong 75°, uốn 105°, R0.6) có giãn tay: phôi T ngắn hơn công thức 60 + 44 - giãn đúng 2.355; AI dùng kích thước danh nghĩa. 1 mẫu, nguyên nhân suy đoán
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-19T12:00:00+07:00
---

Đơn 521119-09, mã 26-069990 (19/11/2026, SPCC t3.2, bản vẽ chữ viết tay "R0.6 V18 鋭角, 伸び 4.18"): AI vẽ phôi 100 x 99.82 (= 60 + 44 - 4.18) với hai đường uốn ở y = 60 và 55.82. Bản đúng T là 100 x 97.465, hai đường uốn ở y = 58.76 và 54.58 (vẫn cách nhau 4.18). Vị trí lỗ dài, góc bo R0.5 tính từ đầu tự do đúng cả hai; chỉ tổng dài và vị trí đường uốn lệch. `diff_tf.py`: khớp 42.3%, các lỗi đều là hệ quả của một lỗi tổng dài.

Số liệu đo được (bằng chứng): từ T, "ngoài hiệu chỉnh" mỗi cánh = vị trí đường uốn tính từ mép xa: cánh đứng 58.76, cánh nghiêng 97.465 - 54.58 = 42.885; so với kích thước ngoài đo trên DXF khách (59.91 và 44.04; chữ ghi 60 và 44) thì cả hai bớt 1.15 (1.15 và 1.155). Giãn 4.18 giữ nguyên làm khoảng cách hai đường uốn. Log chạy của đơn cho thấy AI viết thẳng `A_OUT, B_OUT, GIAN = 60.0, 44.0, 4.18` và ghi "uốn 75° không dùng bảng 90°", không nhắc đến bước hiệu chỉnh.

**Why:** Suy đoán (không có bằng chứng AI đã cân nhắc nhánh nào): SKILL.md mục 5 dòng "Chỗ uốn góc ≤ 85° (cánh nghiêng; Asahi và AICOKU ALPHA)" chỉ nêu hai khách và nói "góc ≤ 85°", còn dòng kế "Góc > 90°: dùng kích thước danh nghĩa". Mã này khách khác, góc trong 75° nhưng góc uốn 105° (> 90°), nên rất có thể AI rơi vào nhánh danh nghĩa. Con số hiệu chỉnh 1.15 trùng với (R + t)·tan(góc uốn / 2) - (R + t) = 3.8 · tan 52.5° - 3.8 = 1.152 (R0.6, t3.2): trùng số, nhưng chưa chứng minh T dùng công thức này (suy đoán).

**How to apply:** khi cánh nghiêng (hình cạnh ghi góc nhọn như 75°, hoặc chữ 鋭角) và có giãn ghi tay, đừng lấy ngay tổng danh nghĩa: phân biệt góc ghi trên hình (góc trong giữa hai cánh) với góc uốn (180° - góc trong), rồi xét hiệu chỉnh kích thước ngoài theo SKILL.md mục 5 trước khi tính phôi. Chưa chắc hiệu chỉnh bao nhiêu thì Flag 16 và hỏi, đừng vẽ số danh nghĩa. Chỉ 1 mẫu: chờ thêm mẫu cùng kiểu (cánh nghiêng góc nhọn, khách ngoài Asahi/AICOKU ALPHA) hoặc kết quả Chạy hồi quy trước khi sửa skill. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]].

**Đính chính 19/11/2026:** góc 75° trên hình là góc giữa hai cánh và log ghi 'uốn 75°', nên suy đoán 'agent đổi sang 105° rồi dùng nhánh danh nghĩa' ở trên KHÔNG đúng. Nguyên nhân khả dĩ nhất: dòng 108 chỉ nêu khách Asahi/AICOKU ALPHA, agent chỉ áp dụng dòng 103 (giãn tay), mục 12 thiếu dòng kiểm. Đã update skill (dòng 5, 103, 108, 244), xem `lessons\skill-updates\069990-cho-uon-nhon-cho-hoi-quy.md`.
