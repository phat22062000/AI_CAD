---
name: feedback-gan-lo-theo-tam-va-canh
description: Nhóm lỗ n-Mx/n-φ phải gán đúng tấm và đúng cánh: nhãn ren khác cỡ trên cùng tấm thì tách từng lỗ, ghi chú lỗ chỉ trỏ một tấm thì tấm kia trơn, chữ コ thì mỗi cánh đủ lỗ
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-17T15:40:00+07:00
---

Ba mã cùng một chủ đề "lỗ gán sai tấm / sai cánh / sai cỡ" (so T/F bằng diff_tf.py, 17/11/2026):

1. Đơn 521110-05, mã 26-066976 (tấm 220 x 25): F vẽ cả 4 lỗ φ6.8 (mồi M8) vì nhãn in "4-M8"; T vẽ 2 lỗ (x = 10, 45) φ5 (mồi M6) và 2 lỗ (x = 125, 205) φ6.8. Trên bản vẽ có thêm nhãn "4-M6" với nét tay nối xuống cùng tấm. F không Flag.
2. Đơn 521111-01, mã 26-067271 (tấm 300 x 200): F thừa 4 lỗ φ10 cách mép 30 (ghi chú "2x2-Φ10キリ M8x4で固定" nằm ở hình tấm ③ khác trên cùng trang); T là tấm trơn. `doi_chieu_khach.py` ĐÃ báo thừa lỗ φ10 và thiếu φ6 cho mã này.
3. Đơn 521111-01, mã 26-067270 (chữ コ, phôi 1194 x 688.72): F chỉ có 2 lỗ φ8 ở cánh trên (y = 673.72); T có đủ 4 lỗ φ8, thêm 2 lỗ ở cánh dưới (15; 15) và (465; 15). Bản vẽ chỉ ghi "2-φ8キリ" ở hình một cánh. F không Flag. 4 lỗ φ20 ở đáy và biên dạng giống nhau.

**Why:** (1) AI lấy nhãn gần nhất cho cả nhóm, không tách lỗ theo nhãn thứ hai và không Flag chỗ không phân biệt được. (2) hai tấm cùng cỡ trên một trang, ghi chú lỗ chỉ trỏ một tấm. (3) số "n-φx" chỉ là số lỗ trong hình đang xem, không phải tổng cho cả chi tiết chữ コ. Nguyên nhân từng mã là suy đoán từ kết quả (log không ghi lý do). Các mã (2) và (3) đã được quy tắc SKILL dòng 146 và 147 bao (thêm ngày 12/11/2026, sau khi các mã này được vẽ ngày 10-11/11); mã (1) chưa có quy tắc.

**How to apply:** lập bảng 'lỗ → tấm → cánh' trước khi dựng: mỗi tấm liệt kê MỌI nhãn n-Mx/n-φ có đường dẫn hoặc nét tay trỏ tới nó; số lỗ nhìn thấy trên tấm không khớp một nhãn (ví dụ 4 lỗ, nhãn 4-M8 và 4-M6) thì tách từng lỗ theo ký hiệu lỗ và nét nối, không phân biệt được thì Flag, không gán hết theo một nhãn. Chi tiết chữ コ/U: vẽ đủ lỗ cả hai cánh. Hai tấm cùng cỡ: ghi chú lỗ chỉ trỏ một tấm thì tấm kia trơn. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]].
