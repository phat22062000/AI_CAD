# ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 33 (2026/11/20, job 20261120144238_updskill). Đề xuất sửa skill: gốc của kích thước song song là chân đường gióng thực, không phải mép tab/bậc nhô gần nhất

Nguồn: đơn 521120-15, mã 26-070723 và 26-070724 (20/11/2026, cặp gương, cùng một nguyên nhân đã xác định bằng file T/F và bản vẽ: kích thước 55 bị tính từ mép tab nhô 15 mm thay vì từ đường uốn như 125 và 120, cả bậc khoét lệch 15 mm). Số mẫu: 2 mã (cùng một đơn, một lỗi đọc). Loại lỗi: Sai biên dạng ngoài. Bài học: `feedback_goc-kich-thuoc-mep-tab-khong-phai-duong-uon.md`.

## (a) Script (đích tools\*.py)
Không đề xuất script. Lỗi không đo được từ file: khung bao, số entity, lỗ, bo R, kegaki đều đúng; bậc khoét hợp lệ về hình học, chỉ khác số đọc từ bản vẽ. `doi_chieu_khach.py` chạy thử trên F của cả hai mã: "không có DXF khách" (đơn không có DXF khách cho hai mã này) nên không bắt được; kể cả có DXF khách thì cũng chỉ bắt được khi DXF ghi sẵn biên dạng đúng.

## (c) SKILL.md (đích skills\dxf-sheetmetal\SKILL.md)
Sửa/gộp dòng 33 (cùng chủ đề "chuỗi kích thước ... một mép chuẩn"), không thêm dòng mới. Đã Grep: dòng 38 ("Chuỗi lệch nhau: đọc lại điểm đầu/cuối từng kích thước"), 39, 43, 46 liên quan nhưng chỉ chạy khi chuỗi không khớp tổng; lỗi này im lặng (không có tổng nào để bắt) nên cần quy tắc ở dòng 33; không có dòng mâu thuẫn.

Dòng cũ (dòng 33):
"  - PHẢI tính từ chuỗi kích thước ghi trên bản vẽ, tính từ một mép chuẩn. Bản vẽ lắp (lỗ ghi kích thước tới tấm khác): quy đổi qua kích thước các tấm liên quan."

Dòng mới:
"  - PHẢI tính từ chuỗi kích thước ghi trên bản vẽ, tính từ một mép chuẩn. Gốc của mỗi kích thước là chân đường gióng thực của nó: các kích thước song song có chung chân gióng thì cùng gốc, KHÔNG lấy gốc là mép tab/bậc nhỏ nằm gần cạnh cần định vị (kích thước riêng của tab là một đoạn khác). Xác định hai chân gióng trước khi tính; dựng xong đo ngược từ cạnh vừa vẽ về đúng đường gióng gốc. Bản vẽ lắp (lỗ ghi kích thước tới tấm khác): quy đổi qua kích thước các tấm liên quan."

Lý do: F tính 55 từ mép tab 15 mm (cách đường uốn 15 mm) trong khi đường gióng của 55 trùng với của 125 và 120; kết quả mọi cạnh của bậc khoét R20 lệch 15 mm, các kiểm tra khung bao/tổng đều qua.
Số mẫu: 2 (26-070723, 26-070724; cặp gương cùng đơn).
Loại lỗi: Sai biên dạng ngoài.
