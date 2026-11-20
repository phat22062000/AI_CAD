# ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 112 (2026/11/20, job 20261120154449_updskill). Đề xuất sửa skill: kích thước của tấm ở chỗ uốn tính từ đường uốn phía tấm (ngoài cánh - giãn), không từ đường phía cánh

Nguồn: đơn 521120-17, mã 26-070728 (20/11/2026). Nguyên nhân đã xác định bằng toạ độ file T/F và bản vẽ (không phải suy đoán): ô cắt góc rộng 5 thuộc chuỗi 680 của tấm nên đo từ đường uốn phía tấm (x = 7.86), F đo từ đường phía cánh (x = 10), lệch đúng giãn 2.14. Số mẫu: 1 mã. Loại lỗi: Sai biên dạng ngoài. Bài học: `feedback_kich-thuoc-tam-do-tu-duong-uon-phia-tam.md`. Đây là nguyên nhân khác với bài 070723/070724 (đã áp dụng vào dòng 33: gốc bị lấy nhầm là mép tab) nên không gộp vào đề xuất đó.

## (a) Script (đích tools\*.py)
Không đề xuất script. Chạy thử trên F: `doi_chieu_khach.py` báo "không có DXF khách" cho 070728 (đơn không có DXF khách của mã này); `dxf_check.py` cho F và T đều 0 LỖI và cùng một CẢNH BÁO "4 góc lõm 90° sát đường uốn không có rạch Green" (báo ở cả bản đúng T, chỉ khác toạ độ), nên không phân biệt được. Hai bản đều có cạnh ô cắt cách một đường uốn đúng số nguyên 5, không có tín hiệu đo được từ file nếu không có số trên PDF. Ghi chú riêng (chưa đề xuất sửa): cảnh báo góc lõm trên là báo nhầm với ô cắt ở mép cánh của bản đúng; để Phát cân nhắc sau khi có thêm mẫu.

## (c) SKILL.md (đích skills\dxf-sheetmetal\SKILL.md)
Sửa/gộp dòng 112 (cùng chủ đề "đường uốn: đường 1 / đường 2"), không thêm dòng mới. Đã Grep: dòng 33 (gốc kích thước = chân gióng thực), 105-106 (kích thước trong/ngoài), 114 (u = y + (ngoài cánh - giãn)) liên quan, không mâu thuẫn; dòng 112 hiện chỉ nói vị trí hai đường mà chưa nói đường nào là gốc của kích thước chuỗi tấm.

Dòng cũ (dòng 112):
"- Đường uốn: mỗi chỗ uốn 2 LINE DASHED (không vẽ 1 đường giữa). Đường 1 cách mép phôi bên này = ngoài cánh bên này; đường 2 cách mép bên kia = ngoài cánh bên kia; khoảng giữa = giãn. Ví dụ L 37 + 60, giãn 5.2, phôi 91.8: đường tại 37 và 31.8. Nhiều chỗ uốn (chữ U...): mỗi cặp đặt tại (vị trí giữa ± giãn/2), vị trí giữa = ngoài cánh - giãn/2 tính từ mép xa."

Dòng mới:
"- Đường uốn: mỗi chỗ uốn 2 LINE DASHED (không vẽ 1 đường giữa). Đường 1 cách mép phôi bên này = ngoài cánh bên này; đường 2 cách mép bên kia = ngoài cánh bên kia; khoảng giữa = giãn. Ví dụ L 37 + 60, giãn 5.2, phôi 91.8: đường tại 37 và 31.8. Nhiều chỗ uốn (chữ U...): mỗi cặp đặt tại (vị trí giữa ± giãn/2), vị trí giữa = ngoài cánh - giãn/2 tính từ mép xa. Mỗi chỗ uốn có hai đường nên phải chọn đúng phía làm gốc: kích thước chiều cao cánh đo từ đường phía cánh; kích thước thuộc chuỗi của tấm (bề rộng tấm, ô cắt/bậc/khe ở mép tấm, vị trí lỗ ghi từ mép ngoài của tấm) đo từ đường phía tấm (cách mép cánh = ngoài cánh - giãn), chênh nhau đúng một độ giãn. Dựng xong đo ngược về đúng đường phía tấm."

Lý do: F tính kích thước 5 của ô cắt góc từ đường phía cánh nên ô cắt lệch đúng độ giãn (2.14) mỗi bên; khung bao, đường uốn, kegaki đều đúng nên không kiểm tra nào bắt được.
Số mẫu: 1 (26-070728). Mới một mẫu: nếu Phát muốn chờ thêm mẫu thứ hai thì giữ nguyên chờ, hoặc chạy hồi quy sau khi áp dụng.
Loại lỗi: Sai biên dạng ngoài.
