---
name: feedback-chuoi-kich-thuoc-sua-tay-hoan-vi
description: Chuỗi kích thước có số sửa tay hoặc nhiều đoạn gần nhau: ghép số theo vạch gióng từng đoạn, không theo chữ nằm gần; hoán vị cùng tổng không bị kiểm tổng bắt
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-17T15:40:00+07:00
---

Đơn 521110-12, mã 26-067077 (SUS304 t3, 535 x 150, 8 lỗ φ12, FAX viết tay): theo phương 150 chuỗi sửa tay là 25.3 / 94.8 / 29.9 (94.8 thay một số gạch bỏ, 29.9 thay số gạch khác; tổng 150). F vẽ hàng lỗ thứ hai ở y = 55.2 (25.3 + 29.9), T vẽ ở y = 120.1 (150 - 29.9, cách hàng một 94.8). 4 lỗ ở hàng này lệch; hàng y = 25.3, vị trí x và biên dạng giống nhau. Chuỗi theo phương 535 (25.2 / 94.7 / 295.2 / 94.7 / 25.2) F đọc đúng.

**Why:** 26-067077: SKILL lúc vẽ chưa có quy tắc ghép số sửa tay theo đoạn (dòng 41-43 thêm ngày 12/11/2026, ví dụ trong dòng đó đúng là lỗi này: a / b' / c' chứ không phải a / c' / b'). Hoán vị cùng tổng 150 nên mọi cách kiểm tổng đều qua. Số mới nằm ở hai hàng chữ lệch nhau; khoảng giữa hai cột lỗ nằm ở dòng dim trên cùng của hình gốc (số cũ 69.5), số cuối là đoạn tới mép (số cũ 53.3). Nguyên nhân F làm gì là suy đoán từ kết quả.

**How to apply:** số gạch rồi ghi mới: ghép từng số mới với số cũ cùng đoạn dựa trên hai vạch gióng, không theo vị trí chữ; dựng xong đối chiếu lại từng khoảng lỗ–lỗ và lỗ–mép với số ghi (SKILL dòng 41-43 đã có). Không loại được cách đọc thứ hai thì Flag 14.
