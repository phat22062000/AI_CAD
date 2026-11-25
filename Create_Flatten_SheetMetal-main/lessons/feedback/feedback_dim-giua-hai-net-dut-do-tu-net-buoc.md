---
name: feedback-dim-giua-hai-net-dut-do-tu-net-buoc
description: Kích thước ghi giữa hai nét đứt (ví dụ 15) đo từ nét đứt ở mức bậc/mép gập xuống nét đứt kia, không đo từ mép phôi; vẽ đủ cả hai nét đứt
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-25T11:50:00+07:00
---

KHÔNG CÒN HIỆU LỰC (Phát 25/11/2026): trong đơn 521125-01 nét đứt chỉ là đường hỗ trợ kích thước để người check theo PDF dễ nhìn, không có thì vẫn đúng. Vị trí nét đứt không phải lỗi; không dùng bài học này.

Đơn 521125-01, mã 26-071141 và 26-071155 (cùng một bản vẽ, SUS304 t1.2, phôi 436 x 180, 25/11/2026; so T/F bằng diff_tf.py, khung bao giống nhau, khớp 55.2% và 52.9%): ở cạnh dưới có hai nét đứt song song. Bản vẽ ghi 27 là chiều cao bậc (đáy tới mép bậc) và 15 là khoảng giữa hai nét đứt: mũi tên trên của 15 chạm đúng nét đứt ở mức bậc 27, mũi tên dưới chạm nét đứt thấp hơn (đã cắt ảnh 220 dpi kiểm). F chỉ vẽ MỘT đường tại y = 15 (đo 15 từ mép dưới); T vẽ HAI đường: y = 27 suốt bề rộng (15 → 421) và y = 12 (27 - 15; 15 → 349 và 399 → 421 ở mã có khuyết 50). Ba cạnh còn lại của F khớp T.

**Why:** F coi số 15 là "nét đứt cách mép 15 ở 4 phía" (Flag của F ghi đúng như vậy) mà không xét chân gióng của mũi tên 15 nằm ở đâu: nét đứt trên chính là đường ở mức bậc, bị bỏ sót. Nguyên nhân xác định từ ảnh bản vẽ và file T/F, nhưng chỉ 1 bản vẽ (2 mã dùng chung hình) nên chưa đủ mẫu để sửa skill.

**How to apply:** với mỗi nét đứt có kích thước ghi bên cạnh, xác định hai chân gióng của kích thước đó (đầu mũi tên ở nét nào) trước khi đặt vị trí; nếu một đầu chạm một nét đứt khác, vị trí = nét kia ± số ghi, và nét đứt đó phải có trong DXF. Dựng xong đếm số nét đứt theo từng cạnh và so với số nét đứt trên hình. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]], [[feedback-kegaki-do-lai-chuoi-kich-thuoc]]. Chưa đề xuất sửa skill (quy tắc chân gióng đã có ở SKILL mục 2, dòng 33, 39, 46; chờ thêm mẫu hoặc Chạy hồi quy).
