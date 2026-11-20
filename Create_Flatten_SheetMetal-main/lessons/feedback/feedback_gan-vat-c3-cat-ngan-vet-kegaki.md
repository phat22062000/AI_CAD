---
name: feedback-gan-vat-c3-cat-ngan-vet-kegaki
description: Gân/tấm hàn có góc vát C (ví dụ C3) ở chỗ áp vào hai tấm khác: biên gân phải vẽ vát C (không bo R mặc định) và vết kegaki trên cả hai tấm nhận phải ngắn đi đúng cạnh vát
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-20T14:00:00+07:00
---

Đơn 521120-07 (20/11/2026, SS400 t6, một bản vẽ lắp 3 tấm: tấm nền ①, tấm đứng ②, gân ③): cả ba mã so T/F bằng diff_tf.py, khung bao giống nhau, chỉ lệch ở kegaki và góc.
- Mã 26-070498 (gân ③, 50 x 35): bản vẽ ghi C3 ở góc gân nằm sát chỗ hai tấm gặp nhau (hình chiếu đáy, C3 có mũi tên). T vẽ đoạn vát (0; 3)-(3; 0); F vẽ cung R2 tâm (2; 2) tại góc đó (khớp entity 62.5%).
- Mã 26-070496 (tấm nền ①, 100 x 89): vết kegaki của gân ③ trên ①. T là khung kín 6 x 47 (y 39 đến 86), cách mép tấm đứng ② (y = 89) đúng 3; F vẽ 6 x 50 chạy tới mép (y 39 đến 89), không có đường đóng đầu (khớp 85.7%).
- Mã 26-070497 (tấm đứng ②, 55 x 50): vết kegaki của gân ③ trên ②. T là khung kín 6 x 32 (y 9 đến 41); F vẽ 6 x 35 (y 6 đến 41), tức F bắt đầu ngay trên mặt tấm nền (6 = độ dày) còn T chừa thêm 3 (6 + 3 = 9) (khớp 76.9%).

**Why:** F bỏ sót C3 của gân ③ (áp R2 mặc định của thép t6 cho góc đó) nên dựng vết kegaki theo đủ cạnh gân (50 và 35). Bằng chứng từ T: cả bốn con số khớp chính xác với việc gân bị vát 3 ở góc áp vào hai tấm (50 - 3 = 47, 89 - 3 = 86, 35 - 3 = 32, 6 + 3 = 9); đây là suy ra từ số liệu T và bản vẽ, người dùng chưa nói ra bằng lời.
**How to apply:** Gân/tấm hàn có góc vát C ở chỗ áp vào tấm nhận: (1) biên gân vẽ đoạn vát C đúng số ghi, không bo R laser (skill đã có "góc đã vát C không bo"); (2) khi lập bảng kegaki, vết trên mỗi tấm nhận chỉ tính phần tiếp xúc thật: bỏ đoạn đầu bị vát, tức dài vết = cạnh gân - số C và khung đóng đầu đó (không chạy tới mép tấm kề). Trước khi giao, đối chiếu từng góc gân với mọi ghi chú C/R trên hình chiếu (kể cả hình đáy/hình phụ) rồi mới áp R laser mặc định. Mới 1 đơn (3 mã cùng một cụm lắp), chưa thử trên đơn khác. Liên quan [[feedback-kegaki-do-lai-chuoi-kich-thuoc]].
