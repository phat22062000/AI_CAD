---
name: feedback-relief-hop-cap-canh-lui-theo-ban-ve
description: Hộp mở 4 cánh: cặp cánh nào lùi t mỗi đầu (khoét a + t) phải xác định theo bản vẽ (cánh lọt giữa, 内寸, hình chữ thập tay), không gán cố định theo trục X/Y của phôi
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-25T11:50:00+07:00
---

Đơn 521125-01, mã 26-071162 và 26-071163 (hộp mở 4 cánh, SUS304 t1.5, giãn 2.64; 25/11/2026; diff_tf.py, khung bao giống nhau, khớp 14.3% và 38.9%): F khoét 4 góc đúng công thức SKILL mục 6 (X = a, Y = a + t) nên hai cánh ở đầu trái/phải lùi t, hai cánh trên/dưới giữ đủ bề rộng. T (người dùng làm) ngược lại: khe theo x rộng a + t = 28.86, khe theo y = a = 27.36; hai cánh trên/dưới (gắn vào hai cạnh dài 360) lùi t mỗi đầu (dài 357), hai cánh trái/phải giữ đủ 200 (071162); ở 071163 khe giữa cánh nhô và cánh dưới/trên rộng 28.86 ở T, 27.36 ở F. Mọi thứ phụ thuộc relief (biên, cung R0.5, đường uốn DASHED, kegaki, rạch Green) lệch theo 1.5 mm = t. Phát hiện cùng hướng ở cả 2 mã (X-khe T = a + t, F = a).

**Why:** SKILL dòng 118 cố định hướng theo trục (X = a, Y = a + t) còn dòng 135 (relief của khách) lại yêu cầu "xác định cánh nào lùi theo hình chiếu, không chép theo ví dụ 26-057140": hai dòng không đồng bộ, F làm theo dòng 118. Hình chữ thập tay trong bản vẽ của đơn cho thấy cánh ở cạnh dài hẹp hơn tấm giữa (khớp T), nhưng lý do khách chọn cặp lùi là suy đoán; chưa thấy chữ 内寸 cho riêng mã này.

**How to apply:** trước khi khoét góc hộp, xác định cặp cánh lùi: cánh lọt giữa 2 cánh kia (ghi 内寸, hoặc hình chữ thập tay/hình 3D cho thấy cánh hẹp hơn tấm giữa) lùi t mỗi đầu (mép ở a + t); cánh che đầu giữ a. Không gán theo trục X/Y hay theo cạnh dài/ngắn; không xác định được thì Flag nêu giả định đã dùng. Dựng xong đo ngược chiều dài mỗi cánh (200 / 357 trong ví dụ) và so với số ghi trong bản vẽ. Đề xuất sửa SKILL dòng 118 để khớp dòng 135: xem lessons\skill-updates\071162-071163-relief-hop-cap-canh-lui.md. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]], [[feedback-relief-goc-vuong-bo-sot]].
