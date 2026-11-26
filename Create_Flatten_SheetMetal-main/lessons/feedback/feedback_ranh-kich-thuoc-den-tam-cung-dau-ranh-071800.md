---
name: feedback-ranh-kich-thuoc-den-tam-cung-dau-ranh-071800
description: Rãnh/lỗ dài có kích thước 18.5 / 43 / 48 mà gióng dừng ở đường tâm cung đầu rãnh: đó là khoảng tâm-tâm, không phải mép ngoài; vẽ theo mép ngoài thì rãnh ngắn đi 2R mỗi đầu
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-26T17:00:00+07:00
---

Đơn 521126-23, mã 26-071800 (26/11/2026, SPCC t3.2, chi tiết uốn 15°, phôi 150 x 138.515): 8 rãnh rộng 7 (R3.5), 4 rãnh ở phần phẳng đầu phôi và 4 rãnh ở phần cánh nghiêng. Bản AI (F) vẽ tâm cung ở y = 22 và 58 (đầu phẳng, tâm-tâm 36) và y = 85.52 và 126.52 (cánh nghiêng, tâm-tâm 41). Bản đúng (T): tâm cung ở y = 18.5 và 61.5 (tâm-tâm 43) và y = 82.02 và 130.02 (tâm-tâm 48). Mỗi rãnh F ngắn hơn T 7 (đúng 2R), cả 8 rãnh; khung bao, lỗ khác và biên ngoài giống nhau. `diff_tf.py`: 16 cung lệch tâm và 16 đường biên khác, khớp 38.5%, phép đặt hướng "giữ nguyên hướng".

Bằng chứng nguyên nhân (đọc DXF khách `-07.DXF`, chưa cần PDF): ở hình phẳng, mỗi rãnh là cặp thẳng x = 415.5 và 422.5 chạy từ y = 202.5 đến 245.5 (cạnh phôi y = 184), tức 18.5 và 43 tính từ cạnh phôi đến điểm đầu/cuối đoạn thẳng; hai đường gióng ngắn nằm đúng ở y = 202.5 và 245.5. Ở hình nghiêng 15°, mỗi rãnh là hai nửa elip R3.5 có TÂM đúng ở hai đầu đoạn thẳng (y = 346.26 và 392.62, cách nhau 46.36 = 48 x cos 15°). Vậy 18.5 / 43 / 48 là khoảng đến TÂM cung đầu rãnh. F lấy 18.5 là mép ngoài và 43 / 48 là tổng dài ngoài-ngoài (tâm-tâm = 43 - 7 = 36; 48 - 7 = 41) nên đẩy tâm cung vào trong 3.5 mỗi đầu.

**Why:** áp sai quy ước chân gióng rãnh dù SKILL.md (mục 4.1 dòng 33) đã có câu "chân gióng đầu rãnh/lỗ dài thường dừng ở TÂM cung R đầu rãnh, không phải mép ngoài". Agent không kiểm chân gióng/đoạn thẳng trong DXF khách trước khi chọn quy ước. Phần "agent bỏ qua dòng 33 hay không đọc DXF" là suy đoán (không có log); phần kích thước sai và quy ước đúng đã xác định bằng T và DXF khách. Khác lỗi [[feedback-ranh-tong-dai-tinh-sai-nua-dai]] (ở đó ghi chú "20X5" là tổng dài và script trừ sai; ở đây gióng là tâm-tâm và agent lại coi là tổng dài).

**How to apply:** khi rãnh/lỗ dài có kích thước dọc chiều dài, kiểm trên DXF khách: đoạn thẳng của rãnh (hai cạnh song song) kết thúc ở đâu so với kích thước ghi, và có cung/elip nào có tâm đúng ở đó không. Nếu số ghi = đầu đoạn thẳng hoặc tâm cung thì tâm-tâm = số ghi, mép ngoài = số ghi ± R. Chỉ coi là tổng dài khi có ghi "NxM" ở 長穴 hoặc gióng chạm mép ngoài cung. Dựng xong đo lại: khoảng giữa hai tâm cung phải bằng số ghi (hoặc tổng dài = số ghi + 2R).
