# Bổ sung skill dxf-sheetmetal: relief góc hộp 4 cánh (lỗi 26-063377, đơn 521027-11, 29/10/2026)

Soạn trên bản skill có mục 6 "Hộp, vách và đường rạch góc" (dòng 91-108). Ba chỗ sửa; chèn nguyên văn nội dung dưới đây vào bản đang rút gọn.

## Chỗ sửa: replace (dòng cũ 92-92, dòng mới 92-92)
Nội dung mới:
```
- Hộp mở 4 cánh: trước tiên kiểm relief góc của khách và đầu cánh vát (2 ngoại lệ bên dưới). Không có thì phôi chữ thập, khoét 4 góc. a = ngoài cánh - giãn, t = độ dày. Khoét theo X = a (2 cánh theo phương Oy giữ đủ bề rộng, không lùi); khoét theo Y = a + t (2 cánh ở hai đầu theo Ox lùi t mỗi đầu). Góc lồi bo theo Laser R, góc lõm không bo; đường uốn DASHED chạy trong phạm vi mỗi cánh.
```

## Chỗ sửa: insert (dòng cũ 102-101, dòng mới 102-108)
Nội dung mới:
```
- Ngoại lệ: hộp 4 cánh có relief góc của khách (đơn 521027-11, 26-063377, SPCC t1.2, cánh 73, giãn 2.14, a = 70.86): mỗi đỉnh hộp bị cắt một khối vuông s (ở mẫu s = 3.5, ghi "3.5 外寸" ở hình chiếu bằng, hình chiếu cạnh và hình nhìn từ dưới), cắt cả mặt chính lẫn 2 cánh; góc lõm của chỗ cắt trên từng mặt có ghi chú R (4-R1 ở mặt chính, 2×2-R1 ở mỗi cặp cánh); hình 3D chi tiết A thấy lỗ ở chỗ giao 3 mặt. KHÔNG khoét kiểu hộp thường, KHÔNG rạch Green.
  - Quy đổi s sang phôi: trên cánh, s tính từ mặt ngoài mặt chính nên cách mép tự do (ngoài cánh - s) = 73 - 3.5 = 69.5; trên mặt chính, s tính từ mặt ngoài cánh nên cách mép phôi a + s = 74.36. Ở mỗi góc, vùng khoét vuông từ 69.5 đến 74.36 theo cả X và Y, nối với phần khoét ngoài các cánh.
  - Cánh lùi: cánh nằm lọt giữa 2 cánh kia (bản vẽ ghi 内寸, ví dụ 277.6 = 280 - 2t) có mép ở a + t = 72.06; cánh che đầu cánh kia giữ đủ bề rộng (mép ở a = 70.86). Xác định cánh nào lùi theo hình chiếu (cạnh ghi 内寸, tấm nào che đầu tấm kia), không chép theo ví dụ 26-057140.
  - Góc: 3 góc lõm của chỗ khoét bo theo ghi chú (R1); 2 góc lồi (mép cánh gặp đáy chỗ khoét) bo R0.5 laser. Đường uốn DASHED chỉ chạy giữa 2 mép relief (từ a + s đến cạnh - a - s).
  - Góc dưới trái (trước khi xoay, phôi 421.72 x 206.72, cánh dưới lùi): (72.06; 0) → (72.06; 69.5) → (74.36; 69.5) → (74.36; 74.36) → (69.5; 74.36) → (69.5; 70.86) → (0; 70.86); R0.5 tại (72.06; 69.5) và (69.5; 70.86); R1 tại 3 góc còn lại.
  - Ghi chú "A部 球面状にR取り(R1) 手仕上げ" là hoàn thiện tay sau uốn, không vẽ lên phôi.
  - Lỗi đã gặp (29/10/2026): coi "3.5 外寸" là đường tiếp tuyến chỗ uốn, khoét hộp thường và rạch Green nên sai vị trí giao 4 cánh với mặt chính. Trước khi dựng hộp, phóng to góc ở mọi hình chiếu và hình 3D (hoặc DXF khách) để tìm relief góc.
```

## Chỗ sửa: replace (dòng cũ 190-190, dòng mới 197-197)
Nội dung mới:
```
- So kích thước phôi với CAD依頼書 và công thức giãn; cạnh thẳng áp cả Ox và Oy; số entity hợp lý (cung nửa tròn là 1 ARC; các cung tiếp nối cùng tâm cùng bán kính gộp làm 1); mọi góc lõm vách–tấm có rạch Green (trừ ngoại lệ ở mục 6: đầu cánh vát 135°, relief góc của khách); kiểm file theo mục 11.2 bước 8.
```
