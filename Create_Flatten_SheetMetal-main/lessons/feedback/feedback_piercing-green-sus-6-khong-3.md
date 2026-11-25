---
name: feedback-piercing-green-sus-6-khong-3
description: Rạch Green góc hộp inox (SUS) t ≤ 5 dùng Piercing ngoài 6, không phải 3 của bảng thép; chạy dxf_check với --mat SUS --t trước khi giao
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-25T11:50:00+07:00
---

Đơn 521125-01, mã 26-071163 (SUS304 t1.5, hộp có cánh nhô, 25/11/2026; diff_tf.py): 8 đường rạch Green của F có điểm đầu cách mép khoét 3 mm (ví dụ (114.36; 84.36) → (117.21; 87.21)); T cách 6 mm ((111.36; 81.36) → (117.21; 87.21)). Quy_Tac_Laser mục 2.2: inox ≤ 5 → Piercing ngoài thẳng dài 6 (thép ≤ 3.2 mới dài 3). Mã cùng đơn 26-071162 (cùng vật liệu, cùng t) F vẽ đúng 6. Chạy thử `dxf_check.py <F> --mat SUS --t 1.5` báo 8 LỖI đúng chỗ này, nên script hiện có đã bắt được lỗi.

**Why:** Suy đoán: dùng cột thép (SS, ≤ 3.2 → 3) cho mã này, hoặc không chạy dxf_check với --mat SUS --t; không có bằng chứng trong file T/F. Không đề xuất sửa skill hay script (script đã có kiểm này).

**How to apply:** trước khi giao mỗi mã có rạch Green, chạy `dxf_check.py <file> --mat <SS|SUS|AL|CU> --t <độ dày>` đúng vật liệu của đơn và sửa mọi LỖI "điểm đầu cách mép khoét"; với SUS t ≤ 5 điểm đầu cách mép khoét 6 theo cả hai trục. Liên quan [[feedback-relief-goc-vuong-bo-sot]].
