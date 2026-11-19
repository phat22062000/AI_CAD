ĐÃ ÁP DỤNG 19/11/2026 (version 2026.11.19-1): dxf-sheetmetal SKILL.md dòng 5, 103, 108, 244. Nguyên nhân thực: dòng 108 giới hạn tên khách (Asahi/AICOKU), agent chỉ áp dụng dòng 103 (giãn tay), mục 12 không có dòng kiểm hiệu chỉnh. Giả thuyết 'đổi sang góc uốn 105° rồi rơi vào nhánh danh nghĩa' bị bác: log ghi 'uốn 75°', hình ghi 75° là góc giữa hai cánh. Dòng 111 giữ nguyên. Còn chờ Chạy hồi quy mã này.

(Nội dung đề xuất cũ bên dưới, giữ để tham khảo)

# Đề xuất: chỗ uốn cánh nghiêng góc nhọn dùng kích thước danh nghĩa (chờ hồi quy)

Nguồn: 521119-09_26-069990 (1 mẫu). Loại lỗi: Sai độ giãn dài, Sai biên dạng ngoài. Bài học: `lessons\feedback\feedback_cho-uon-75-do-dung-kich-thuoc-danh-nghia.md`. Nguyên nhân là suy đoán (xem bài học), nên chưa sửa quy tắc.

## (a) Script (tools\*.py)
Không đề xuất script. Đã chạy `doi_chieu_khach.py` trên 26-069990F.dxf: báo "không đối chiếu được" (chi tiết uốn, DXF khách không có hình phẳng chồng khít), nên script hiện có không bắt được lỗi này. Tổng dài phôi đúng hay sai phụ thuộc vào số hiệu chỉnh mà chưa có công thức xác định, nên chưa thêm kiểm vào `dxf_check.py`.

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
KHÔNG đề xuất sửa lúc này (1 mẫu, nguyên nhân chỉ là suy đoán). Đợi Chạy hồi quy với mã này (đáp án T có sẵn) để biết quy tắc mục 5 hiện tại đã đủ chưa.

Ứng viên để cân nhắc nếu hồi quy vẫn ra sai (chưa đề xuất):
- Dòng 108 (nguyên văn): "- Chỗ uốn góc ≤ 85° (cánh nghiêng; Asahi và AICOKU ALPHA): không dùng kích thước danh nghĩa (ví dụ 80/150) làm kích thước ngoài."
- Dòng 111 (nguyên văn): "  - Góc > 90°: dùng kích thước danh nghĩa (kích thước ngoài + kích thước ngoài - độ giãn)."
- Hướng sửa (gộp, không thêm dòng): bỏ giới hạn tên khách ở dòng 108, ghi rõ "góc" là góc trong giữa hai cánh trên hình cạnh (uốn = 180° - góc trong), và dòng 111 chỉ áp cho cánh vuông góc hoặc tù thật sự (góc trong ≥ 90°). Số mẫu hiện tại: 1.
