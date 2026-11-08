# Quy trình rút kinh nghiệm từ mã bị chấm Sai

Mục đích: biến phản hồi của người dùng (chấm **Sai** + ghi chú trên trang Giám Sát, mục Đánh Giá AI) thành bài học mà agent đọc trước khi vẽ, để không lặp lại lỗi.

Vòng khép kín:
1. Người dùng báo mã sai: nhắn thẳng trong app (cách chính), hoặc chấm Sai + ghi chú trên trang -> lưu ở `tools\project_web\data\reviews.json`.
2. Agent trong app làm theo quy trình dưới đây, viết bài học vào `lessons\feedback\`.
3. Mỗi lần vẽ đơn mới, agent đọc `lessons\feedback\*.md` và `rules\Ghi_Chu_Loi_Tao_DXF.md` trước (đã ghi trong prompt chạy nền ở `tools\project_web\runner.py` và trong `AI_Work\CLAUDE.md` mục 5).

## Khi nào chạy
Có hai nguồn góp ý:
- **A. Nhắn thẳng trong app (cách chính).** Người dùng nhắn kiểu "Đơn 521106-07 mã 26-066279 sai: lỗ Ø5 phải cách mép 10, AI vẽ 8". Làm ngay:
  1. Ghi kết quả lên trang để biểu đồ đúng: `py tools\project_web\report.py review <số đơn>_<mã> status=sai note="<tóm tắt lỗi>"` (chạy từ thư mục AI_CAD). Mã người dùng xác nhận đúng thì `status=dung`.
  2. Làm bước 2 đến 7 dưới đây cho các mã đó (bỏ qua bước 1).
- **B. Chấm trên trang.** Người dùng chấm Sai + ghi chú ở mục Đánh Giá AI rồi nói "rút kinh nghiệm" (có thể kèm số đơn hoặc ngày). Làm đủ bước 1 đến 7; không kèm gì thì xử lý mọi mã Sai chưa rút.

## Các bước
1. **Lấy danh sách mã Sai.** Đọc `tools\project_web\data\reviews.json` (chỉ đọc, không ghi file này). Mỗi mục có khoá `<số đơn>_<mã>`, `status`, `note`, `at`. Lấy các mục `status = "sai"`, bỏ những khoá đã có trong `lessons\feedback\_da_rut_kinh_nghiem.json`.
2. **Đối chiếu từng mã.** Tìm thư mục đơn `AI_Work\Thang-MM\dd-mm-yyyy\<số đơn>\`. Mở bản vẽ PDF của mã và file DXF đã giao (DXF lẻ có tên chứa mã, không có thì `<số đơn>_ALL.dxf`). So với ghi chú của người dùng để xác định: sai ở đâu, đúng phải là gì, nguyên nhân (đọc sai kích thước / chân dim / hình chiếu, áp sai quy tắc, skill thiếu quy tắc, lỗi công cụ...).
3. **Ghi chú chưa đủ rõ thì hỏi người dùng**, không đoán. Ghi chú kiểu "sai lỗ" phải hỏi lại: lỗ nào, sai vị trí hay sai kích thước, đúng là bao nhiêu.
4. **Viết bài học** vào `lessons\feedback\feedback_<ten-ngan>.md`, theo mẫu các file đã có:
   ```
   ---
   name: feedback-<ten-ngan>
   description: <một câu: quy tắc cần nhớ>
   metadata:
     node_type: memory
     type: feedback
     modified: <thời gian ISO>
   ---

   Đơn <số đơn>, mã <mã> (<ngày>): <sai gì>. Đúng là <...>.

   **Why:** <nguyên nhân gốc>
   **How to apply:** <làm gì khác đi ở lần sau, cụ thể đến bước kiểm tra>
   ```
   Cùng loại lỗi với một bài học đã có thì bổ sung vào file đó, không tạo file trùng. Không ghi tên khách hàng (chỉ số đơn, mã).
5. **Lỗi do skill thiếu hoặc sai quy tắc, hoặc cùng lỗi lặp lại từ 2 lần:** soạn đề xuất sửa vào `lessons\skill-updates\<mã>-<ten-ngan>.md` (ghi rõ dòng cũ, dòng mới như các file đã có). Chỉ sửa skill gốc `skills\dxf-sheetmetal\SKILL.md` khi người dùng đồng ý, và báo rõ vị trí các dòng mới cập nhật.
6. **Đánh dấu đã rút:** thêm khoá `<số đơn>_<mã>` vào `lessons\feedback\_da_rut_kinh_nghiem.json` (mảng JSON) kèm tên file bài học.
7. **Báo người dùng:** các mã đã rút, bài học mới hoặc bổ sung, đề xuất sửa skill đang chờ duyệt.
