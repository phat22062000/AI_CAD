# Danh sách đã loại khỏi repo

Repo được dựng bằng cách copy; file gốc ở `AI_CAD\` không bị đổi.

## Dữ liệu khách hàng và dữ liệu theo đơn (không đưa vào)
- `AI_Work\Thang-10\`, `AI_Work\Thang-11\`: toàn bộ thư mục đơn hàng (khoảng 430 file): PDF đơn (76), DXF khách và DXF thành phẩm (225), DWG (14), NC (3), phiếu CAD依頼書 xlsx (69), ảnh overlay (10), `blind_table.md`, file `.bak`.
- `AI_Work\tools\gen_521102-*.ps1`, `gen_521104-*.ps1` (8 file): script sinh DXF theo từng đơn, chứa kích thước chi tiết của khách.
- Thư viện dự án (không copy): `*_ALL.dxf`, `gen_*.py`, `parts/`, `blind/`, `review/`, `specs/`, `order_context.json`, `exp.csv` của các đơn 5210xx-5211xx.

## Đã ẩn danh
- `DS_Khach_Hang.md` thành `rules/Quy_Tac_Theo_Ma_Khach_AnDanh.md`: bỏ cột tên khách, giữ mã khách và quy tắc; thay tên công ty trong dòng mã 764 bằng "khách này".
- Báo cáo đơn 521102-16: bỏ tên khách ở dòng đầu.

## File dư hoặc cũ (không đưa vào)
- `Skills\backup\`, `Skills\dist\`, `Skills\xem\`, `Skills\skill-sync.ps1` (quy trình cũ), `sync.json(.bak)`, `last_import.txt`, `selftest_result.txt` (có đường dẫn máy cá nhân).
- Bản SKILL.md cũ trong thư viện dự án (`tools/*_SKILL.md`, `skill-updates/*/`, `skill_fix/`): skill trên app là bản gốc.
- `__pycache__/`, `*.skill` cũ, `UPGRADE-NOTES.md`.

## Còn sót, Phát cần xem trước khi push
- Tên bảng độ giãn `Bang_Do_Gian_Asahi.xlsx` và `Bang_Do_Gian_AICOKU ALPHA.xlsx`, cùng chữ "Asahi/AICOKU" trong SKILL.md: có thể là tên khách hoặc nhà cung cấp. Đang giữ nguyên vì skill tham chiếu đúng tên này.
- Mã khách (ba chữ số) trong quy tắc và ví dụ của skill.
- `templates/Template.dxf` có một đường dẫn máy khác (`C:\Users\ADMIN\...\Output_Sample.dxf`); không sửa vì phải khớp từng byte.
- Skill `dxf-check` và `sheetmetal_kit/README.md` có đường dẫn `C:\Users\DELL\Desktop\AI_CAD\...`.
