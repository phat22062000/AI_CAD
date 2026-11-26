ĐÃ ÁP DỤNG phần (c) vào skills\dxf-sheetmetal\SKILL.md dòng 179 (2026/11/26, job 20261126155242_updskill); ĐÃ ÁP DỤNG phần (a) script vào tools\dxf_check.py (2026/11/26, job 20261126163635_updscript)
# Đề xuất: phôi dài hẹp trên 2500 vẫn phải có J/LJ (đơn 521126-22, mã 26-071828)

Nguồn: 26-071828 (T/F, 26/11/2026). Loại lỗi: Thiếu lỗ (diff_tf báo POINT J/LJ thiếu) / thực chất thiếu J/LJ và thiếu Flag. Số mẫu: 1 mã (đã xác định bằng file T: 4 J + 1 LJ cho L = 2540).

## (a) Script (đích tools\dxf_check.py)
Chạy thử: `dxf_check.py` trên F chỉ ra CẢNH BÁO "phôi dài 2540 > 2500, quy tắc J/LJ chưa có, hỏi người dùng", không có LỖI; `doi_chieu_khach.py` trên F trả "không đối chiếu được" (DXF khách của mã này không chồng khít). Vậy script hiện có KHÔNG bắt được lỗi.
Dòng 416 (cũ): `nJ = 1 if Wd <= 1500 else 2 if Wd <= 2000 else 3 if Wd <= 2500 else None`
Dòng 416 (mới): `nJ = 1 if Wd <= 1500 else 2 if Wd <= 2000 else 3 if Wd <= 2500 else 4 if Wd <= 3000 else None`
Dòng 434 (cũ): `else: W('%s: phôi dài %s > 2500, quy tắc J/LJ chưa có, hỏi người dùng' % (name, f(Wd)))`
Dòng 434 (mới): khi `nJ is None` (L > 3000) mà không có POINT trên mép trên và không có Flag thì báo LỖI "phôi dài hẹp thiếu J/LJ và thiếu Flag"; có Flag thì bỏ qua.
Lý do: kiểm cùng công thức xs đã có (30, ..., L - 30, chia đều) sẽ báo LỖI đúng 5 điểm thiếu ở F (x = 30, 650, 1270, 1890, 2510).

## (c) SKILL.md (đích skills\dxf-sheetmetal\SKILL.md mục 10)
Dòng 179 (cũ): `... 1000 ≤ L ≤ 1500 → 1 J + 1 LJ; 1500 < L ≤ 2000 → 2 J + 1 LJ; 2000 < L ≤ 2500 → 3 J + 1 LJ.`
Dòng 179 (mới): `... 1000 ≤ L ≤ 1500 → 1 J + 1 LJ; 1500 < L ≤ 2000 → 2 J + 1 LJ; 2000 < L ≤ 2500 → 3 J + 1 LJ; 2500 < L ≤ 3000 → 4 J + 1 LJ (cứ thêm 500 thì thêm 1 J). Phôi dài hẹp ngoài các khoảng trên hoặc không chắc số J: vẫn vẽ theo quy luật gần nhất và ghi Flag, không được bỏ trống J/LJ mà không báo.`
Lý do: T của mã mẫu có đúng 4 J + 1 LJ cho L = 2540 (ngoại suy 500 mm/J, chỉ 1 mẫu nên cần xác nhận thêm); F không vẽ gì và không Flag.
Dòng cũ cần sửa/gộp: dòng 179 (không thêm dòng mới); dòng 180 giữ nguyên (công thức chia đều đã đúng với T).

## Kết quả phần script (2026/11/26)
Đã thêm vào tools\dxf_check.py: (1) nJ = 4 cho 2500 < L <= 3000 (cùng công thức xs, nên thiếu POINT/TEXT J/LJ là LỖI; khoảng này không kiểm cao chữ vì T mẫu cao 12, không phải 10); (2) L > 3000: giữ CẢNH BÁO (đổi mốc thành 3000), thêm LỖI "thiếu J/LJ và thiếu Flag" khi file ALL không có POINT trên mép trên và mã không có Flag (file riêng không có Flag nên chỉ CẢNH BÁO).
Thử trước/sau trên 119 file (47 file ALL, các file F/T trong Sua_loi): chỉ 3 file thay đổi có ý nghĩa. 26-071828F: LỖI 0 -> 6 (thiếu POINT tại x = 30, 650, 1270, 1890, 2510 và 5 TEXT), mã thoát 0 -> 1; ALL của 521126-22 (mã 071828) có LỖI mới tương ứng. 26-071828T: không có LỖI/CẢNH BÁO mới (chỉ mất cảnh báo cũ "phôi dài 2540 > 2500"). Các mã đã chấm Đúng và mọi file khác: đầu ra không đổi (hai file ALL 521120-23 và 521125-01 vốn bị ngoại lệ trong check_part, chỉ lệch số dòng traceback). Tổng thời gian 131.2 s -> 131.0 s. Thử tổng hợp phôi 3200 x 25: ALL không Flag báo LỖI, có Flag không báo LỖI. Mốc 500 mm/J mới có 1 mẫu T, cần xác nhận thêm.
