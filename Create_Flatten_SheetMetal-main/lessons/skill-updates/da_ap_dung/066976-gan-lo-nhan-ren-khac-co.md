ĐÃ ÁP DỤNG phần (c) vào skills\dxf-sheetmetal\SKILL.md dòng 148 (2026/11/17, job 20261117155115_updskill); ĐÃ ÁP DỤNG phần script (a) vào tools\dxf_check.py (2026/11/17, job 20261117162639_updscript)

# Đề xuất: nhóm lỗ ren có hai nhãn khác cỡ trên cùng tấm; chi tiết chữ コ hai cánh (script)

Nguồn: đơn 521110-05 mã 26-066976 (loại: Sai kích thước lỗ, Thiếu Flag); đơn 521111-01 mã 26-067270 (Thiếu lỗ, Thiếu Flag) và 26-067271 (Thừa lỗ). Bài học: lessons\feedback\feedback_gan-lo-theo-tam-va-canh.md.

## (a) Script, ưu tiên 1: tools\dxf_check.py (thêm cảnh báo, chi tiết uốn chữ コ/U)
Chạy thử `doi_chieu_khach.py` trên F của 26-067270: "không đối chiếu được" (chi tiết uốn, DXF khách không chồng khít) → KHÔNG bắt được. Với 26-067271: ĐÃ bắt (CẢNH BÁO thừa lỗ φ10 ×4, thiếu lỗ φ6 ×4), không cần sửa. 26-066976: không có DXF khách, script không bắt được.
Đề xuất thêm kiểm (đo được): với phôi uốn có hai cặp đường uốn DASHED song song và hai vùng cánh ngoài cùng (ví dụ y 0 đến 194 và 494 đến 688 ở 26-067270), đếm lỗ trong từng vùng cánh; số lỗ hoặc φ hai cánh khác nhau thì CẢNH BÁO "hai cánh không đối xứng lỗ (n1 so n2), kiểm: chi tiết chữ コ mặc định mỗi cánh đủ lỗ (SKILL mục 10)". Chỉ cảnh báo, không sửa. Số mẫu: 1 (cộng 1 lần quy tắc dòng 146 đã có).

## (c) SKILL.md, ưu tiên sau: bổ sung dòng 148 (không thêm dòng mới)
Dòng 148 hiện tại (kết thúc): "...Trước khi vẽ, quét mọi ghi chú tay cạnh từng nhóm lỗ n-Mx/n-φ và ghi vào bảng 'lỗ → tấm' (cột φ vẽ + nguồn: bảng / ghi chú tay)."
Thêm vào cuối dòng: "Một tấm có từ hai nhãn ren khác cỡ trỏ tới (ví dụ 4-M8 và 4-M6, kể cả nét tay nối nhãn xuống tấm) mà số lỗ thấy trên tấm không khớp một nhãn: tách từng lỗ theo ký hiệu lỗ và nét nối; không phân biệt được thì Flag 5, không gán cả nhóm theo nhãn gần nhất."
Lý do: bản F gán 4 lỗ cùng M8 (φ6.8), bản đúng 2 lỗ φ5 (M6) và 2 lỗ φ6.8, F không Flag. Số mẫu: 1. Loại lỗi: Sai kích thước lỗ, Thiếu Flag.

## Không đề xuất thêm
Dòng 146 (chữ コ hai cánh) và 147 (hai tấm cùng cỡ, ghi chú lỗ chỉ trỏ một tấm) đã có từ 12/11/2026 và bao 26-067270 và 26-067271 (hai mã vẽ ngày 11/11, trước khi có quy tắc). Cần Chạy hồi quy để biết quy tắc đã đủ chưa.

## Kết quả phần script (2026/11/17)

Thêm vào tools\dxf_check.py (check_part, sau kiểm đường uốn): với phôi có từ 2 cặp đường uốn DASHED cùng hướng (song song trục X hoặc Y) mà hai cánh ngoài cùng rộng bằng nhau (lệch < 0.1 mm), so danh sách φ lỗ (kể cả POINT lỗ) trong từng cánh; khác nhau thì CẢNH BÁO "hai cánh ngoài cùng bằng nhau (...) nhưng lỗ không đối xứng (n1 so n2)". Chỉ cảnh báo, không đổi mã thoát.

Thử trước/sau trên 51 file (tất cả F/T trong Sua_loi và mọi file *_ALL.dxf hiện có): chỉ 2 file đổi: 26-067270F (0 lỗ so 2 lỗ φ8, cánh 194.36 mm) và 521111-01_ALL (mã 067270, cùng cảnh báo). Bản đúng 26-067270T và 49 file còn lại không có dòng mới, mã thoát và dòng cũ giữ nguyên; thời gian 48.8 s so 47.5 s. 26-067271 và 26-066976: không thuộc phần này (067271 đã bắt từ trước; 066976 không có DXF khách).
