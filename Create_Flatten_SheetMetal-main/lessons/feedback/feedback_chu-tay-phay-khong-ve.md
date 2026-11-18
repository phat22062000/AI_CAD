---
name: feedback-chu-tay-phay-khong-ve
description: Lỗ/rãnh có dung sai H (Ø4 +0.05/+0.02) và chữ tay フライス (phay) khoanh tròn là gia công phay sau, không cắt laser; T không vẽ, F đã vẽ thừa
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-18T16:10:00+07:00
---

Đơn 521118-11, mã 26-069881 (SUS316 t3, 205 x 179, 18/11/2026; so T/F bằng diff_tf.py): trên bản vẽ có hai chỗ ở cạnh trái, mỗi chỗ có chữ tay "フライス" và vòng khoanh tay: lỗ "Ø4 +0.05/+0.02" cách mép 68 (tâm y = 82.5 trong DXF) và rãnh "4 +0.05/-0.02 (R2)" ở y = 124.5 đến 126.5. F vẽ cả hai: lỗ φ4.04 tại (8; 82.5) và rãnh rộng 4.04 (hai LINE x = 5.98 / 10.02 và hai ARC R2.02). T không có hai chỗ này (T chỉ có 8 lỗ: 4 lỗ cạnh trái, 4 lỗ x = 167 / 197). Trong file ALL, F có hai Flag: "1. Kích thước có dung sai (lỗ Ø4 +0.05/+0.02 và rãnh rộng 4 +0.05/+0.02: vẽ theo giá trị giữa 4.035)" và "2. Ghi chú tay không đọc rõ (chữ フライス cạnh lỗ Ø4 và rãnh 4 có gạch chéo/khoanh tròn, chưa rõ có phải phay sau laser: vẽ theo kích thước ghi)". Tức F đã nghi là phay sau laser nhưng vẫn vẽ.

**Why:** F gặp chữ tay フライス, tự nghi "phay sau laser" nhưng chọn vẽ rồi Flag, trong khi đáp án là không vẽ (có bằng chứng: Flag trong ALL và T bỏ cả hai). SKILL dòng 227 cấm bỏ cả chi tiết chỉ vì ghi chú "không đọc rõ", nên F vẽ là hợp lệ theo quy tắc hiện tại; chữ フライス thì đọc rõ, vấn đề là chưa có quy tắc nói nghĩa của nó. Hiểu "フライス = phay, gia công sau, không phải laser" là suy luận từ ý nghĩa chữ và từ T, chưa có lời Phát; SKILL hiện chỉ có quy tắc "gạch bỏ thì không vẽ" (dòng 27) và "chỉ vẽ phần được chỉ thị" của bản lắp hàn (dòng 28), chưa có quy tắc cho ghi chú tay chỉ công đoạn phay. Một mẫu.

**How to apply:** khi quét mọi chữ tay ngoài hình (SKILL dòng 18): chữ tay chỉ công đoạn khác laser (フライス phay...) khoanh quanh lỗ/rãnh/kích thước có dung sai thì coi là gia công sau, không vẽ, liệt kê phần đã bỏ trong báo cáo (chữ đọc rõ thì không cần Flag 5; Flag 5 chỉ cho chữ thật sự không đọc ra). Dung sai chặt (+0.05/+0.02) là dấu hiệu phụ chứ không phải điều kiện riêng. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]].
