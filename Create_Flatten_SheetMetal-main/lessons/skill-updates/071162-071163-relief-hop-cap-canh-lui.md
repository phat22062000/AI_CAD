ĐÃ ÁP DỤNG 25/11/2026 (skill 2026.11.25-3, dòng 118)

# Đề xuất: hộp 4 cánh, cặp cánh lùi t xác định theo bản vẽ, không cố định theo trục X/Y

Nguồn: 521125-01_26-071162, 521125-01_26-071163 (2 mẫu, cùng đơn, hai bản vẽ khác nhau). Loại lỗi: Sai biên dạng ngoài, Sai độ giãn dài, Sai kegaki, Sai rạch Green. Bài học: `lessons\feedback\feedback_relief-hop-cap-canh-lui-theo-ban-ve.md`. Nguyên nhân xác định từ file T/F: ở cả hai mã F khoét đúng công thức dòng 118 (X = a, Y = a + t) còn T khoét X = a + t, tức cặp cánh lùi t ngược hướng; mọi biên, đường uốn, kegaki, rạch Green lệch theo đúng 1.5 mm = t. Lý do khách chọn cặp lùi là suy đoán (hình chữ thập tay trong bản vẽ cho thấy cánh ở cạnh dài hẹp hơn tấm giữa, khớp T).

## (a) Script (tools\*.py)
Không đề xuất script. Đã chạy `doi_chieu_khach.py` trên 26-071162F.dxf và 26-071163F.dxf: báo "không có DXF khách" nên không so được. `dxf_check.py` trên 26-071162F (--mat SUS --t 1.5): 0 lỗi, 0 cảnh báo, nên script hiện có không bắt được lỗi này. Cặp cánh nào lùi phụ thuộc bản vẽ, không đo được bằng script từ DXF.

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
Đích: SKILL.md mục 6, dòng 118 (sửa/gộp dòng cũ, không thêm dòng; khớp với dòng 135 đã yêu cầu "xác định cánh nào lùi theo hình chiếu").

Dòng cũ (nguyên văn, dòng 118):
"- Hộp mở 4 cánh: TRƯỚC TIÊN phóng to mỗi đỉnh hộp ở mọi hình chiếu và hình 3D (hoặc DXF khách) để kiểm relief góc của khách và đầu cánh vát (2 ngoại lệ cuối mục). Không có thì phôi chữ thập, khoét 4 góc. a = ngoài cánh - giãn, t = độ dày. Khoét theo X = a (2 cánh theo phương Oy giữ đủ bề rộng, không lùi); khoét theo Y = a + t (2 cánh ở hai đầu theo Ox lùi t mỗi đầu). Góc lồi bo theo Laser R, góc lõm không bo; đường uốn DASHED chạy trong phạm vi mỗi cánh."

Dòng mới:
"- Hộp mở 4 cánh: TRƯỚC TIÊN phóng to mỗi đỉnh hộp ở mọi hình chiếu và hình 3D (hoặc DXF khách) để kiểm relief góc của khách và đầu cánh vát (2 ngoại lệ cuối mục). Không có thì phôi chữ thập, khoét 4 góc. a = ngoài cánh - giãn, t = độ dày. Cặp cánh lùi (mép ở a + t, khoét a + t) và cặp giữ đủ bề rộng (khoét a) xác định theo bản vẽ: cánh lọt giữa 2 cánh kia (ghi 内寸, hoặc hình chữ thập tay/hình 3D cho thấy hẹp hơn tấm giữa) lùi t mỗi đầu; KHÔNG gán cố định theo trục X/Y hay theo cạnh dài/ngắn của tấm; không xác định được thì Flag và nêu giả định đã dùng. Góc lồi bo theo Laser R, góc lõm không bo; đường uốn DASHED chạy trong phạm vi mỗi cánh."

Lý do: dòng 118 gán hướng cố định theo trục, trái với dòng 135 và với T của cả hai mã (cặp cánh ở cạnh dài lùi t). Ví dụ 26-057140 ở dòng 119 có khoét X = a, Y = a + t nhưng không rõ hướng đặt cuối, nên không dùng làm quy tắc trục. Số mẫu: 2 mã (cùng đơn). Loại lỗi: Sai biên dạng ngoài, Sai độ giãn dài, Sai kegaki, Sai rạch Green. Sau khi áp dụng nên Chạy hồi quy hai mã này (đáp án T có sẵn).
