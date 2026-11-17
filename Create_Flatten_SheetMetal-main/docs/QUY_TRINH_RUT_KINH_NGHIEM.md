# Quy trình rút kinh nghiệm từ mã bị chấm Sai

Mục đích: biến phản hồi của người dùng (chấm **Sai** + ghi chú trên trang Giám Sát, mục Đánh Giá AI) thành bài học mà agent đọc trước khi vẽ, để không lặp lại lỗi.

Vòng khép kín:
1. Người dùng báo mã sai: nhắn thẳng trong app (cách chính), hoặc chấm Sai + ghi chú trên trang -> lưu ở `tools\project_web\data\reviews.json`.
2. Agent trong app làm theo quy trình dưới đây, viết bài học vào `lessons\feedback\`.
3. Mỗi lần vẽ đơn mới, agent đọc `lessons\feedback\*.md` và `rules\Ghi_Chu_Loi_Tao_DXF.md` trước (đã ghi trong prompt chạy nền ở `tools\project_web\runner.py` và trong `AI_Work\CLAUDE.md` mục 5).

## Chạy bằng nút trên web (từ 17/11/2026)
Vòng khép kín, chỉ áp cho đơn từ 17/11/2026 trở đi (các mã Sai cũ chưa có file T tạm bỏ qua):
1. Chấm mã **Sai** trên mục Đánh Giá AI: web tự tạo `<thư mục đơn>\Sua_loi\` và chép file AI đã vẽ thành `<mã>F.dxf` (không ghi đè). Không thấy file lẻ của mã thì có nút "Chép file F".
2. Người dùng tự đặt bản đúng `<mã>T.dxf` vào folder đó. Mã Sai chưa có T hiện trong mục "Mã Sai chưa có file T" (đầu trang Đánh Giá AI).
3. Bấm **Rút kinh nghiệm**: agent so T/F bằng `tools\diff_tf.py` (0 token, tự thử 8 phép đặt hướng, phân loại khác biệt), ghi lỗi + loại lỗi lên trang (`report.py loi ... loai=...`), viết bài học vào `lessons\feedback\`, nháp đề xuất vào `lessons\skill-updates\` (đầu file ghi CHỜ PHÁT DUYỆT; ưu tiên sửa script, rồi rules, cuối cùng mới skill; sửa/gộp dòng cũ thay vì thêm), đánh dấu đã rút. **Không sửa skill**; chỉ sửa khi người dùng nói "update skill", và phải nêu rõ dòng đã đổi.
4. Bấm **Tự check** ở khung chi tiết đơn: web chạy ngay hai script, 0 token: `tools\dxf_check.py` (hình dạng, quy ước, Flag) và `tools\doi_chieu_khach.py` (chồng hình AI lên DXF khách, báo lỗ khác φ, lấy vòng ngoài của nhóm đồng tâm, lỗ mồi sai cỡ ren, cạnh lệch, và thiếu Flag 1). Chỉ mã có LỖI của dxf_check hoặc có chỗ khác DXF khách (tối đa 30% số mã của đơn) mới giao agent đọc mù theo skill dxf-check; không có mã đáng ngờ thì không tốn token. Bấm ở khung chi tiết một mã thì luôn đọc mù mã đó. Chỉ báo LỖI và CẢNH BÁO, không sửa file. Lệnh "tạo" vẫn không chạy check.
5. Sau khi update skill, bấm **Chạy hồi quy** (mục Chất lượng theo loại lỗi): agent vẽ lại bộ mã hồi quy bằng skill hiện tại vào thư mục tạm rồi so với đáp án bằng `diff_tf.py`. Bộ mã = các mã Sai đã có file T (đáp án chuẩn) + vài mã đã chấm Đúng còn file riêng (đáp án bạc, chỉ để phát hiện thoái lui); chọn một loại lỗi thì chỉ chạy các mã thuộc loại đó. Tốn token như vẽ lại từng mã, nên chỉ chạy sau update skill. Một lần khớp chưa chứng minh skill tốt hơn (AI vẽ lại không cho cùng kết quả mỗi lần).
6. Mục **Chất lượng theo loại lỗi** hiện: số lỗi trên 100 mã theo loại, số mã lặp lại lỗi sau khi đã có bài học, tỉ lệ entity khớp bài đúng (từ `diff_tf.py`), chi phí thật của từng loại việc. Số liệu lấy từ `data\loi_sai.json`: mỗi mã Sai có `loi`, `loai`, `nguyen_nhan`, `nguon` (T/F, script, đọc mù, Phát), `khop`.
Update skill: bấm nút **Update Skill** ở mục Rút kinh nghiệm (hoặc nhắn "update skill"). Nút áp dụng các đề xuất đã chọn: sao lưu bản cũ vào `data\skill_backup\`, chỉ sửa SKILL.md và rules (sửa/gộp dòng cũ, quy tắc tổng quát), nâng version, ghi lại từng dòng cũ/mới lên trang. Phần đề xuất có đích là script thì không áp dụng. Sau đó đổi dòng đầu file đề xuất thành "ĐÃ ÁP DỤNG vào SKILL.md dòng ..." (còn phần chưa làm thì thêm "CÒN CHỜ: ..."): web chỉ liệt kê đề xuất còn "CHỜ PHÁT DUYỆT" hoặc "CÒN CHỜ". Khi update xong, trang hiện bảng thông báo (dòng đã đổi, mục bỏ qua) và các đề xuất đã áp dụng hết tự rời danh sách, được cất ở `lessons\skill-updates\da_ap_dung\`. Sau update nên chạy hồi quy.

Update script: đề xuất có đích là script (tools\*.py) thì dùng nút **Update Script**. Agent sao lưu tools, sửa script, chạy thử trước và sau trên file F, file T và mọi mã đã chấm Đúng; không đạt (báo giả) thì khôi phục bản cũ và ghi lý do. Đề xuất không sửa gì mà chờ hồi quy được gắn nhãn "Chờ hồi quy", không có ô chọn; chạy hồi quy xong thì bấm **Đóng đề xuất** (file cất vào `lessons\skill-updates\da_ap_dung\`).
Model: mọi công đoạn (vẽ, Tự check, Rút kinh nghiệm, Hồi quy) mặc định Sonnet 5.5, effort High (Phát chốt 17/11/2026); đổi riêng từng việc bằng `data\config.json` (`check_model`, `rutkn_model`, `hoiquy_model`).
Thứ tự ưu tiên khi sửa: lỗi đo được thì thêm kiểm vào script (`dxf_check.py`, `doi_chieu_khach.py`); quy tắc riêng một khách thì vào rules; chỉ lỗi bắt buộc đọc bản vẽ mới vào SKILL.md, và sửa/gộp dòng cũ thay vì thêm dòng.

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
   Khi có hai file DXF `<mã>T.dxf` (đúng) và `<mã>F.dxf` (sai) trong `<thư mục đơn>\Sua_loi\` (người dùng đặt vào): so sánh hai file rồi ghi lỗi cụ thể của mã lên trang (popup chi tiết mã Sai, chỉ đọc) bằng `py tools\project_web\report.py loi <số đơn>_<mã> "lỗi 1" "lỗi 2"` (mỗi lỗi một câu, ghi đè danh sách cũ). Trang tự hiện đường dẫn folder `Sua_loi`, không cần ghi đường dẫn.
7. **Báo người dùng:** các mã đã rút, bài học mới hoặc bổ sung, đề xuất sửa skill đang chờ duyệt.
