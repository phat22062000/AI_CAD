---
name: feedback-relief-goc-vuong-bo-sot
description: Ghi chú 直角逃がし (relief góc vuông, ví dụ ø3) ở góc lõm của biên phải được vẽ, kể cả bản ghi OUTLINE ONLY
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-17T15:40:00+07:00
---

Đơn 521109-22, mã 26-066809 (SS400 t3, 279.5 x 146.4, bản vẽ ghi OUTLINE ONLY / 外周のみ): bản vẽ có chú thích "ø3 直角逃がし" tại góc lõm vuông ở (149.9; 116.4). F vẽ góc nhọn. T vẽ relief: vòng R1.5 tâm đúng đỉnh góc (cung 304.8° đến 145.2°, mở vào vật liệu), nối hai cạnh bằng hai cung R2 tiếp tuyến (tâm (147.03; 118.4) và (151.9; 113.53)); cạnh ngang kết thúc ở x = 147.03, cạnh đứng ở y = 113.53. Biên dạng còn lại giống nhau (16 trên 19 entity khớp). F không có Flag.

**Why:** bản "OUTLINE ONLY" chỉ nói không vẽ lỗ/hình trong, nhưng relief góc nằm trên biên cắt nên vẫn phải vẽ; AI bỏ sót chú thích. SKILL chưa có quy tắc nhắc 直角逃がし. Nguyên nhân là suy đoán từ kết quả. Chưa rõ vì sao mã 26-066808 (cùng đơn, cũng có chú thích 2-ø1.5 直角逃がし) trong bản đúng không có relief ở góc nào: chưa xác định, không rút quy tắc từ đó.

**How to apply:** quét chú thích 直角逃がし / 逃がし (ø hoặc R kèm số) trên cả hình chính và bản OUTLINE ONLY; tại góc lõm vuông được chỉ (đầu mũi tên) vẽ relief theo mẫu bản đúng: vòng ø tâm tại đỉnh góc, hai cạnh dừng ở tiếp điểm cung R2. Không xác định được góc nào hoặc số góc không khớp "n-" thì Flag 5, không bỏ qua im lặng.
