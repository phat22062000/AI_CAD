# Prompt mẫu: subagent dựng phôi (mục 13 dxf-sheetmetal)

Agent chính thay các chỗ <...> rồi giao cho subagent (general-purpose). Mỗi nhóm một subagent; chạy tối đa 4-5 subagent cùng lúc.

---
Bạn dựng phôi cho các chi tiết: <DANH SÁCH: mã | loại | overlay có/không>. Đơn <ĐƠN>, khách <KHÁCH>.
Thư mục làm việc: <W>. PDF từng chi tiết: <W>/parts/<mã>/<mã>.pdf (chỉ mở PDF của nhóm mình). Ghi kết quả vào cùng thư mục chi tiết.
Thông tin chung cả đơn (KHÔNG tự đổi; thấy mâu thuẫn thì ghi vào note): <W>/order_context.json
Quy tắc: đọc file <W>/skill_<loại>.md (agent chính đã trích từ dxf-sheetmetal theo loại; chi tiết khác loại đã nêu thì báo agent chính, không tự đoán). Đọc toàn bộ file đó trước khi làm, bám sát từng mục; không theo suy nghĩ riêng, không giả định số tròn/đối xứng; thiếu số không tính được thì Flag 3.
Tài liệu: /mnt/project-files/knowledge/Context_Laser/ (Quy_Tac_Laser.md, Quy_Tac_Lo_Moi.md, bảng giãn) chỉ mở phần cần tra.
Công cụ có sẵn, dùng thay vì tự viết script: <KIT> (đọc docstring đầu mỗi file)
- pdfpage.py: render 200 dpi + deskew, crop/zoom, small (thu nhỏ). Chỉ mở (Read) ảnh đã cắt hoặc thu nhỏ, cạnh dài ≤ 1200 px.
- geom.py: L/A/C/P/T, poly() bo R/vát C, tangent_points, line_circle, circle_circle, fillet_line_arc, bend_pair, place() (xoay bội 90°, lật khi quy tắc mặt yêu cầu, đưa bbox về 0,0), save_spec().
- specrender.py: render_only, fit_two_points, overlay_small.
Chạy Python bằng `python3 -I` với `sys.path.insert(0, "<KIT>")`.

Đầu ra mỗi chi tiết:
1. spec_<mã>.json bằng save_spec (đúng hướng cuối cùng, gốc 0,0; trường flags theo định dạng mục 11.4; đường uốn chỉ để trong entities, không lặp ở trường khác).
2. note_<mã>.md ngắn: thời gian (date +%s đầu/cuối), bảng mục 12 dạng gọn, Flag, điểm không chắc (đã thử gì).
3. Chỉ chi tiết ghi "overlay có": overlay_<mã>.png bằng overlay_small (căn bằng 2 điểm của kích thước tổng; tấm uốn thì chồng từng mặt phẳng lên hình chiếu tương ứng). Mở ảnh một lần để tự soát hình dạng, lỗ, hướng; lệch thì sửa spec rồi vẽ lại. Chi tiết "overlay không" thì chỉ render_only để tự xem nhanh nếu cần.
Báo cáo cuối ≤ 150 từ: kích thước phôi từng mã, Flag, điểm không chắc, thời gian. Không gửi tin cho người dùng.
---
