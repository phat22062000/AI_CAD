---
name: feedback-goc-kich-thuoc-mep-tab-khong-phai-duong-uon
description: Kích thước song song cùng một mép chuẩn (125, 120, 55) phải tính từ cùng gốc theo chân đường gióng; không lấy gốc là mép bậc/tab nhô gần nhất
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-20T15:00:00+07:00
---

Đơn 521120-15, mã 26-070723 và 26-070724 (cặp gương, SUS304, 340 x 202.86, mép khoét bậc R20 bên phải, 20/11/2026): bản vẽ có tab nhô 15 x 15 ở góc, ba kích thước 125 / 120 / 55 chạy song song và cùng chân đường gióng dưới ở đường uốn (đường gióng của 55 trùng với của 125 và 120, tab 15 là kích thước riêng). F tính cạnh ngang của bậc khoét cách mép tab 55 (cách vết kegaki 70), T tính cách vết kegaki 55. Kết quả cả bậc khoét (cạnh đứng x = 240, cung R20, cạnh ngang, vòng R0.5) lệch 15 mm. Lỗ, bo R10, kegaki, khung bao đều khớp (diff_tf: 75% entity khớp ở cả hai mã, khung bao giống nhau nên kiểm khung bao không bắt được).

**Why:** F lấy gốc của 55 là mép tab nhô (gần nhất về hình) thay vì chân đường gióng thực sự của kích thước (đường uốn, cùng gốc với 125 và 120). Bằng chứng: toạ độ F = mép tab + 55 chính xác; bản vẽ cắt ở 300 dpi cho thấy đường gióng dưới của 55 nằm ngang hàng với 125 và 120, không ngang hàng với mép tab. Lỗi không có tín hiệu: khung bao, chuỗi tổng và số lượng entity đều đúng.

**How to apply:** với mỗi kích thước định vị biên (bậc, khe, ô khoét), xác định hai chân đường gióng trước khi tính; các kích thước cùng hướng bắt đầu từ cùng một đường (125, 120, 55 cùng gốc) thì tính cùng gốc. Có tab/bậc nhỏ nằm giữa gốc và cạnh cần định vị thì đừng mặc định kích thước chạy từ mép tab; kích thước riêng của tab (15) là một đoạn khác. Dựng xong đo ngược: khoảng cách từ cạnh vừa vẽ tới đúng đường gióng gốc = số ghi. Cặp gương: kiểm cả hai tấm. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]], [[feedback-chuoi-kich-thuoc-sua-tay-hoan-vi]].
