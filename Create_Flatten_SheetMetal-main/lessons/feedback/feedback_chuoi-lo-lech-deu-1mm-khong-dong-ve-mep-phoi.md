---
name: feedback-chuoi-lo-lech-deu-1mm-khong-dong-ve-mep-phoi
description: Chuỗi kích thước lỗ không có số đầu bên trái thì phải đóng về mép phôi bên phải (tổng chuỗi + số đầu = bề rộng phôi); lệch đều 1 mm là dấu hiệu chuỗi không đóng
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-25T11:50:00+07:00
---

Đơn 521125-01, mã 26-071141 và 26-071155 (SUS304 t1.2, phôi 436 x 180, 25/11/2026; diff_tf.py): F đặt mọi lỗ (φ22, φ28, và 2 lỗ φ6 ở 071141) lệch +1 mm theo x so với T, cùng y, bước 36/50 vẫn đúng. Hàng lỗ dưới không có số kích thước từ mép trái; từ phải sang bản vẽ ghi 62 (từ φ6 tới mép phôi 436), 26, 22, rồi 8 bước 36: lỗ đầu = 436 - 62 - 26 - 22 - 8 x 36 = 38 (T x = 38). F đặt 39, nên khoảng cách φ6 tới mép phải của F chỉ 61, không khớp số 62 đã ghi.

**Why:** Suy đoán (không có bằng chứng trong log): gốc chuỗi bị lấy lệch 1 mm (đo gốc ở 437 hoặc cộng sai), không đóng chuỗi về mép phôi để kiểm. Không phân biệt được với nguyên nhân khác. Không đề xuất sửa skill (quy tắc đo ngược đã có ở SKILL mục 5 và 7).

**How to apply:** hàng lỗ không có số từ mép đối diện: tính toạ độ lỗ đầu bằng cách đóng chuỗi về mép phôi (bề rộng phôi trừ mọi số trong chuỗi) và ghi rõ phép tính; dựng xong đo ngược từ lỗ xa nhất tới mép phôi bên phải phải đúng số ghi (ở đây 62 tại φ6), lệch 1 mm là sai. Nếu hai cách đóng chuỗi cho kết quả khác nhau thì Flag, không tự chốt. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]], [[feedback-lo-canh-lech-do-day-goc-17-200-10]].
