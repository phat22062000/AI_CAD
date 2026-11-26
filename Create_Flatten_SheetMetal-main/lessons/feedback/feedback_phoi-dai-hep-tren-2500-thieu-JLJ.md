---
name: feedback-phoi-dai-hep-tren-2500-thieu-JLJ
description: Phôi dài hẹp (Oy ≤ 100, Ox ≥ 1000) dài trên 2500 vẫn phải có POINT + TEXT J/LJ ở mép trên; bảng skill dừng ở 2500 nên không được bỏ qua, phải vẽ theo quy luật hoặc ghi Flag.
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-26T15:40:00
---

Đơn 521126-22, mã 26-071828 (26/11/2026): phôi phẳng 2540 x 25, 16 lỗ φ6.5, 4 ARC R0.5 ở góc. F (AI vẽ) khớp T về biên, lỗ, ARC (khớp 90.6% entity) nhưng THIẾU 5 cặp POINT + TEXT trên mép trên (y = 25): x = 30, 650, 1270, 1890 (TEXT "J") và x = 2510 (TEXT "LJ"), TEXT cao 12 trong T. Đúng là 4 J + 1 LJ, N = 5 điểm chia đều, bước (2540 - 60)/4 = 620 (cùng công thức mục 10 SKILL.md). Mã này không có Flag nào (flags rỗng) nên người dùng không được báo thiếu.

**Why:** SKILL.md mục 10 (dòng 179) chỉ liệt kê J/LJ tới L = 2500 (1 J, 2 J, 3 J); phôi 2540 nằm ngoài bảng. `dxf_check.py` cũng chỉ CẢNH BÁO "phôi dài > 2500, quy tắc J/LJ chưa có, hỏi người dùng" (không phải LỖI), nên lỗi lọt qua. Suy đoán: agent coi ngoài bảng là không cần J/LJ thay vì ngoại suy hoặc ghi Flag.
**How to apply:** Phôi Oy ≤ 100 và Ox ≥ 1000 mà dài hơn bảng thì vẫn vẽ J/LJ: số J tăng 1 cho mỗi 500 mm (2500 < L ≤ 3000 → 4 J + 1 LJ), vị trí chia đều như công thức hiện có; nếu L > 3000 hoặc không chắc số J thì ghi Flag thay vì bỏ trống. Trước khi báo built, kiểm: phôi dài hẹp mà không có POINT/TEXT J/LJ ở mép trên thì phải có Flag. Lưu ý TEXT cao 12 trong T, skill ghi cao 10: chưa rõ khác biệt, đối chiếu thêm khi gặp mẫu khác.
