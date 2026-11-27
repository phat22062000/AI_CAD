# Đề xuất: chữ L vẽ nguyên hướng hình chiếu đứng (mặt trong) thay vì lật ra mặt ngoài, chờ hồi quy

CHỜ PHÁT DUYỆT, chưa sửa. Chưa đề xuất dòng mới: quy tắc hiện có đã nêu đúng việc cần làm, cần Chạy hồi quy để biết agent có áp dụng được không.

Nguồn: đơn 521127-15, mã 26-072887 và 26-072888 (27/11/2026). Cùng nguyên nhân (cả hai mã bị vẽ ở mặt đối diện), 2 mẫu cùng một đơn. Loại lỗi: Sai mặt vẽ.

## (a) Script
Không đề xuất script. `doi_chieu_khach.py` chạy thử trên F của cả hai mã: "không đối chiếu được" (DXF khách là hình chiếu của chi tiết uốn, không chồng khít hình AI). Mặt trong/ngoài là kết luận từ đọc bản vẽ, không đo được bằng số entity, kích thước hay vị trí.

## (c) SKILL.md
KHÔNG đề xuất sửa. Quy tắc hiện có: `skills\dxf-sheetmetal\SKILL.md` mục 3, dòng 58 (ưu tiên 3): "Chi tiết uốn: mặt ngoài của phần uốn; hình chiếu đứng cho thấy mặt trong thì lật trái–phải (không đổi chiều dọc)." và dòng 52: "Chữ L: mặt ngoài là phía góc ngoài của chỗ uốn trên hình chiếu đứng ...". Hai mã sai đúng ở việc quy tắc này yêu cầu (F là ảnh gương của T, 20/20 entity khớp sau khi lật).

Khoảng trống có thể có (chỉ xét nếu hồi quy lại cho kết quả F lật sai): dòng 52 nói "trên hình chiếu đứng" nhưng ở các bản vẽ như hai mã này profile chữ L chỉ thấy ở HÌNH PHẢI, hình chiếu đứng là hình nhìn thẳng vào tấm; agent phải suy mặt của hình chiếu đứng từ hình phải. Ý sửa nếu cần (gộp vào dòng 58, không thêm dòng): cánh chìa về phía người nhìn hình chiếu đứng thì hình chiếu đứng là mặt trong. Chưa đưa thành đề xuất vì chưa có mẫu thứ hai ở đơn khác và nguyên nhân agent bỏ qua bước này mới là suy đoán từ log.

Cách kiểm hồi quy: vẽ lại 26-072887 và 26-072888 bằng skill hiện tại, so với T bằng `diff_tf.py`; cần "giữ nguyên hướng" cho cả hai.
