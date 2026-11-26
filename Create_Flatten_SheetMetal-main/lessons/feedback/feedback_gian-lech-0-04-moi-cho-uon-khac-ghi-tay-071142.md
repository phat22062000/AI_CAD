---
name: feedback-gian-lech-0-04-moi-cho-uon-khac-ghi-tay-071142
description: Mã 26-071142: T ngắn hơn F đúng 0.039 mm mỗi chỗ uốn (giãn T ≈ 4.66, F = 4.62 theo ghi tay và bảng); không có bằng chứng trong PDF cho 4.66, nguyên nhân chưa rõ, chưa đề xuất sửa
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-26T12:00:00+07:00
---

Đơn 521126-06, mã 26-071142 (chữ U SPCC 2.3t, 2 chỗ uốn, 26/11/2026; diff_tf.py: giữ nguyên hướng, khớp 59.3%, 118 entity mỗi bên): mọi khác biệt là một độ dịch dồn theo từng chỗ uốn, hình dạng không đổi. Lỗ/cung ở cánh trái giống hệt (dx = 0), ở tấm giữa F lệch +0.039 (lỗ φ4.2 tại x 196.58 so với 196.541), ở cánh phải lệch +0.078 (lỗ φ7 tại 444.099 so với 444.021); 4 đường DASHED F lệch +0.039 (179.28 / 183.9 / 329.26 / 333.88 so với 179.241 / 183.861 / 329.221 / 333.841); khoảng cách mỗi cặp DASHED vẫn 4.62 ở cả hai; phôi F 513.16 x 370.5, T 513.08 x 370.5 (chênh 0.078 = 2 x 0.039). Tức giãn T ≈ 4.659 mỗi chỗ uốn, F 4.62. Các khác biệt "thiếu/thừa cung R3, R5, R10, R25, R50, R83.5" và "lỗ sai vị trí" do diff_tf báo đều chỉ là dịch 0.039 / 0.078 này (cùng bán kính, cùng hình).

Nguồn của F: ghi tay trên bản vẽ (PDF trang 7, đọc rõ ở độ phóng đại 4x) "183.9 + 154.6 + 183.9 − (4.62 × 2) = 513.16", với 183.9 = 181.6 (内寸) + 2.3t và 154.6 = 150 (内寸) + 2 x 2.3; bảng giãn AICOKU ALPHA (SPCC 2.3t, 3R, V18) cũng cho 4.62. F khớp cả hai: SKILL mục 5 (số ghi tay là nguồn số 1) áp đúng. Con số 4.66 không có trong PDF; cũng không có trong bảng 2.3t (Asahi 3.8; AICOKU 4.44 / 4.62; 4.66 chỉ là ô t3 của bảng Asahi).

**Why:** Nguyên nhân chưa xác định. Suy đoán: người dùng dựng T bằng nguồn giãn khác (số riêng, bảng khác, hoặc đo từ mô hình) mà không ghi lên PDF; hoặc T làm tròn theo công cụ riêng. Chưa có lời của Phát, chưa thấy PDF/DXF khách nào cho 4.66, nên không kết luận F sai về quy tắc. Chênh chỉ 0.04 mm mỗi chỗ uốn (0.078 mm tổng), dưới dung sai gia công thông thường. Một mẫu.

**How to apply:** không đổi quy tắc từ mẫu này. Khi gặp lại đơn khác có ghi tay giãn khác bảng, vẫn dùng số ghi tay (Flag 10 nếu khác bảng). Nếu Phát xác nhận T dùng giãn 4.66 cho khách này thì ghi quy tắc riêng vào `rules\Quy_Tac_Theo_Ma_Khach_AnDanh.md`; hiện CHƯA đề xuất sửa skill/rules/script.
