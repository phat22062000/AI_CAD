---
name: feedback-kich-thuoc-tam-do-tu-duong-uon-phia-tam
description: Kích thước thuộc chuỗi của tấm (680, 670, 5...) ở chỗ uốn tính từ đường uốn phía tấm (cách mép cánh = ngoài cánh - giãn), không phải đường phía cánh (cách mép cánh = ngoài cánh); lệch đúng độ giãn
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-20T15:30:00+07:00
---

Đơn 521120-17, mã 26-070728 (SUS304, uốn 2 cánh 10 mm, giãn 2.14, phôi 695.72 x 460, 20/11/2026): bản vẽ ghi 680 (bề rộng tấm, ngoài-ngoài), 670 và hai ô cắt góc rộng 5 sâu 10 ở 4 góc; ghi tay 10 + 680 + 10 - (2.14 x 2) = 695.72. F đặt cạnh đứng ô cắt tại x = 15 (tức 5 tính từ đường uốn x = 10, đường phía cánh); T đặt tại x = 12.86 (5 tính từ x = 7.86, đường phía tấm). Ô cắt F rộng hơn T đúng 2.14 mỗi bên; khung bao, đường uốn, kegaki, bo R0.5 đều khớp (diff_tf: 41.7% entity khớp vì chỉ khác biên ô cắt; khung bao 695.72 x 460 giống nhau nên kiểm khung bao không bắt được).

**Why:** mỗi chỗ uốn có hai đường (mục 5 skill): đường phía cánh cách mép phôi = ngoài cánh (10) và đường phía tấm cách mép phôi = ngoài cánh - giãn (7.86). Kích thước 680 và 5 là kích thước của tấm nên chân của chúng là mép ngoài danh nghĩa phía tấm (đường 7.86), nhưng F lấy đường phía cánh (x = 10). Bằng chứng: toạ độ F = 10 + 5 chính xác, toạ độ T = 7.86 + 5 chính xác (687.86 - 7.86 = 680); ảnh cắt 300 dpi của bản vẽ cho thấy chân gióng trái của 680 là biên ngoài còn 5 đo vào từ đó. Khác bài [[feedback-goc-kich-thuoc-mep-tab-khong-phai-duong-uon]] (ở đó gốc bị lấy nhầm là mép tab nhô, ở đây gốc đúng đường uốn nhưng nhầm phía của cặp đường uốn).

**How to apply:** kích thước cạnh biên/ô cắt/bậc nằm trên phần tấm giữa hai chỗ uốn mà đi cùng chuỗi kích thước của tấm (680...) thì đo từ đường uốn phía tấm (cách mép cánh = ngoài cánh - giãn); kích thước chiều cao cánh (10) đo từ đường phía cánh. Dựng xong đo ngược: khoảng cách từ cạnh ô cắt tới đường phía tấm phải đúng số ghi (ở đây 5), cạnh đối diện đối xứng; nếu cạnh vừa vẽ cách đường phía cánh đúng số ghi thì đã lấy nhầm phía. Đối chiếu nhanh: tổng chuỗi 680 phải bằng khoảng giữa hai đường phía tấm (687.86 - 7.86). Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]].
