---
name: feedback-kegaki-cach-duong-uon-0-22-070499
description: Kegaki của gân trên phôi uốn Z: bản đúng lùi 0.22 khỏi đường uốn ở hai đầu vết nhưng AI vẽ chạm đường uốn (nguyên nhân chưa xác định, lệch rất nhỏ)
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-20T14:00:00+07:00
---

Đơn 521120-07, mã 26-070499 (20/11/2026, SS400 t6, phôi uốn Z 137.44 x 65, hai chỗ uốn, đường uốn x = 50.22/60 và 90.44/100.22; gân ② hàn lên tấm đáy và tấm đứng): so T/F bằng diff_tf.py, khung bao, lỗ, biên giống hệt, khớp entity 78.3%; chỉ khác kegaki.
- Vết trên tấm đáy: T đi từ x = 4 đến 50 (đường uốn ở x = 50.22), F đi từ 4 đến 50.22 (chạm đường uốn).
- Vết trên tấm đứng: T đi từ x = 60.22 đến 90.44, F đi từ 60 đến 90.44 (T lùi 0.22 khỏi đường uốn x = 60; ở đầu 90.44 T trùng đường uốn, không lùi).
- T vẽ mỗi vết thành khung kín 4 cạnh (có đường đóng đầu); F bỏ đường đóng đầu ở chỗ trùng đường uốn.

**Why:** Suy đoán, không có bằng chứng: lệch chỉ 0.22 mm, không đọc được từ bản vẽ (các kích thước gân 54, 50, (38), 101 không cho số 0.22). Có thể bản T lùi vết khỏi vùng uốn, hoặc T dựng tay làm tròn khác; hai đầu của T cũng không đối xứng (đầu 90.44 không lùi), nên chưa thể coi là quy tắc.
**How to apply:** Mới 1 mẫu, lệch cỡ dung sai vẽ, chưa đề xuất sửa skill hay script. Skill hiện đã nói "đoạn trùng đường uốn DASHED thì bỏ" (mục 9); nếu sau này gặp thêm mã uốn có kegaki mà bản đúng luôn lùi một khoảng nhỏ khỏi đường uốn thì mới xét gộp vào dòng đó. Script hiện có (doi_chieu_khach.py) không bắt được lỗi này vì đơn không có DXF khách của mã.
