# Quy trình tạo bản vẽ trải phôi

Tóm tắt từ `skills/dxf-sheetmetal/SKILL.md` (mục 1 và 13). Khi lệch, SKILL.md là chuẩn.

## Luồng một đơn
1. Đọc trang CAD依頼書: mã yêu cầu, khách, vật liệu, độ dày, X/Y phôi (chỉ để đối chiếu).
2. Đọc `rules/Quy_Tac_Laser.md` và dòng đúng mã khách trong `rules/Quy_Tac_Theo_Ma_Khach_AnDanh.md`. Quy định riêng của khách thắng quy tắc chung.
3. Có DXF khách thì dựng từ DXF trước, rồi đối chiếu PDF.
4. Mỗi trang: kiểm hướng, render 200 dpi một lần, xác định loại hình chiếu, ghi mọi điểm thuộc Flag và ghi chú R.
5. Mỗi mã: lập bảng mục 12, xác định góc uốn và độ giãn, dựng biên, uốn, hộp/rạch Green, lỗ, kegaki, bo góc, rồi đặt hướng.
6. Xuất file riêng và `<số đơn>_ALL.dxf` ghép vào `templates/Template.dxf`, kèm Flag.
7. Kiểm bằng skill `dxf-check` và `tools/dxf_check.py`; báo cáo theo mục 7 của skill.

## Nguyên tắc cứng (mục 0)
Chỉ dùng kích thước đã ghi trên PDF hoặc DXF khách, không giả định (kể cả "nằm giữa", "đối xứng", số tròn). Thiếu kích thước mà không tính được thì Flag 3.

## Đơn từ 4 chi tiết: chạy song song
Dùng `tools/sheetmetal_kit/` (xem README trong thư mục đó): agent chính lập `order_context.json`, tách PDF, chia nhóm; subagent dựng spec; `merge_all.py` gộp vào Template; `dxf-check` đọc mù song song. Kết quả thử: `lessons/BAO_CAO_don_521102-16_song_song_overlay.md`.

## Cập nhật skill
Skill trên app là bản gốc. Sau khi sửa trên app, bấm Save skill rồi chạy `tools/skill_sync/Dong-bo-skill.bat` để lưu bản về máy; sau đó chép `SKILL.md` mới vào `skills/` của repo.
