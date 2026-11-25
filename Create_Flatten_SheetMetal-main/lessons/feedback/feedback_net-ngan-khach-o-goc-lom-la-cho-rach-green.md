---
name: feedback-net-ngan-khach-o-goc-lom-la-cho-rach-green
description: Nét ngắn (dài ≈ t, màu đỏ) trong DXF khách ở góc lõm tấm–cánh là chỗ rạch Green; phải vẽ đủ 3 entity Green, không giữ nét đó làm LINE biên
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-25T17:10:00+07:00
---

Đơn 521125-14, mã 26-071234 (khách 400片研, t1.2, phôi 525.5 x 422 gồm tấm giữa, 4 cánh, 2 lỗ φ60; 25/11/2026; diff_tf.py: giữ nguyên hướng, khớp 86.7%, phôi lệch 0.007 mm nên kích thước, lỗ, cung R211/R15 đều đúng): ở 2 góc lõm nơi mép cánh trái gặp cánh trên/dưới (T: (14; 387.12) và (14; 34.88)), F chỉ có một LINE biên màu thường dài 1.2 (14; 385.92)→(14; 387.12), không có cung và không có Green. T có đủ rạch Green 3 entity ở mỗi góc: LINE chéo từ (8; 393.12) tới (13.85; 387.27) (điểm đầu cách mỗi mép khoét 6), ARC R0.5 tâm (13.5; 386.91) từ 0° đến 45°, LINE (14; 386.91)→(14; 385.92) dừng đúng đường uốn. Tổng cộng F thiếu 2 cung R0.5, 4 đường Green và thừa 2 LINE biên.

Nguồn gốc nét 1.2 của F: trong DXF khách `HP-049FB.dxf` có nét màu đỏ (màu 1) dài 1.2 đúng ở hai góc này, cùng toạ độ (14; 385.92)→(14; 387.12) sau khi quy đổi. F đã chép nét đó vào biên thay vì đổi nó thành rạch Green.

**Why:** Nguyên nhân gốc xác định từ file: AI coi nét đỏ ngắn của khách là một đoạn biên (khe cụt) thay vì dấu chỗ rạch relief. Vì sao AI không nhận ra là suy đoán (chưa thấy bản vẽ PDF ghi gì ở chỗ này; có thể do khoảng cách khe đến đường uốn bằng đúng t nên điều kiện d < t ở SKILL dòng 124 bị đọc là "không rạch"). Script chưa bắt đúng tên lỗi: `doi_chieu_khach.py` báo "biên khớp 100%" (nét 1.2 nằm trong cả hai); `dxf_check.py` chỉ báo LỖI "hở biên tại (14; 385.92)" chứ không nêu thiếu Green, và cảnh báo "góc lõm không rạch Green" không chạy vì góc có 3 đoạn chung 1 điểm nên không được tính là góc lõm.

**How to apply:** khi DXF khách có nét ngắn (dài ≈ t, hay màu đỏ) nằm ở góc lõm giữa mép cánh và mép tấm, hoặc chạy dọc mép khoét tới đường uốn: coi đó là chỗ rạch, vẽ đúng 3 entity Green (LINE chéo từ ngoài với điểm đầu cách mép = Piercing ngoài của vật liệu, ARC R0.5, LINE dọc mép tới chân nét khách) và KHÔNG giữ nét đó làm LINE biên. Sau khi dựng, mọi LINE ngắn ≤ 2t có một đầu cụt (chạm đúng một entity) trong biên là dấu hiệu sai: sửa trước khi giao. Chưa đề xuất sửa skill vì chỉ có 1 mẫu; xem đề xuất script ở `lessons\skill-updates\071234-net-ngan-khach-thanh-rach-green.md`.
