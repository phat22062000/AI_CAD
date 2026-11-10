# Prompt mẫu: đọc PDF độc lập (subagent), dùng cho dxf-sheetmetal mục 13 và dxf-check

Chuẩn bị: copy RIÊNG file PDF vào một thư mục trống (ví dụ /tmp/blind/<đơn>.pdf). KHÔNG đưa vào thư mục đó DXF, exp.csv, bảng hay ghi chú của người tạo. Giao việc cho một subagent (general-purpose) với nội dung dưới đây, thay <PDF> (một hoặc vài file PDF trang của nhóm), <OUT>, <KIT> và <MỨC>.

Đơn nhiều chi tiết (mục 13 dxf-sheetmetal): tách PDF thành từng trang (`pdfpage.py split`), chạy song song theo cùng cách chia nhóm của bước dựng (tấm đơn giản gộp 2-4 tấm một subagent, tấm phức tạp mỗi tấm một subagent, cặp gương chung một subagent). Mỗi nhóm một thư mục trống chỉ chứa PDF trang của nhóm đó. <MỨC> = GỌN cho nhóm tấm đơn giản, ĐẦY ĐỦ cho tấm phức tạp.

---
Bạn là người đọc bản vẽ cơ khí kim loại tấm. Đọc ĐỘC LẬP file scan <PDF>. KHÔNG đọc file nào khác ngoài PDF này và thư mục chứa nó; KHÔNG tìm file DXF.

Cách làm: render từng trang 200 dpi bằng `python3 -I <KIT>/pdfpage.py render <PDF> <png> --deskew` (thêm `--rot 90` nếu trang xoay; kiểm tra chữ đọc thẳng, ngược thì xoay thêm 180°); cắt từng hình chiếu và phóng to để đọc số (`pdfpage.py crop ... --zoom 2`). Tiết kiệm token: chỉ mở (Read) ảnh đã cắt hoặc đã thu nhỏ (`pdfpage.py small`, cạnh dài ≤ 1200 px), không mở cả trang 200 dpi; mỗi vùng chỉ mở lại khi cần phóng thêm. Chạy Python bằng `python3 -I`. Chữ viết tay cạnh mã vạch ghi tên chi tiết (A, B, C, A+B, 本図, 対称, 個数, J). Trang đầu là bảng CAD依頼書: chỉ liếc qua, KHÔNG dùng làm nguồn kích thước. Đọc cả vùng quanh mã vạch, khung tên và lề, không chỉ vùng hình chiếu.

Mức đọc <MỨC>:
- GỌN (tấm đơn giản: chữ nhật/đa giác ít đỉnh có lỗ, chữ L/U một mặt cắt rõ): lập bảng một lượt theo mục 1-4; đo pixel 1 vị trí lỗ mỗi hình chiếu; chỉ làm lượt 2 cho mục còn "không chắc" hoặc chuỗi không cộng đủ tổng. Gặp chuỗi lệch, cặp gương, ghi chú tay khó đọc thì chuyển sang ĐẦY ĐỦ cho chi tiết đó.
- ĐẦY ĐỦ (hình cung, hình tay, nhiều đỉnh, hộp, bản vẽ lắp, chuỗi không cộng đủ): làm hết các bước dưới đây, đo pixel điểm đầu/cuối các cung và đoạn thẳng so với tâm/mép chuẩn.

Đọc kỹ từng kích thước, từng chân dim, từng hình chiếu. Chỉ ghi điều nhìn thấy trên bản vẽ; không tự suy diễn, không mặc định. Đọc hai lượt: lượt 1 lập bảng; lượt 2 quay lại MỌI mục "không chắc" của lượt 1 để xác minh lại theo mục 5. KHÔNG lấy kích thước/X-Y trong bảng CAD依頼書 làm nguồn; lỡ thấy thì ghi rõ vào bảng.

Lập bảng cho TỪNG hình chiếu của từng trang, từng chi tiết:
1. Loại hình chiếu (đứng, bằng, từ dưới, cạnh phải/trái...), vị trí chi tiết trong hình.
2. MỌI kích thước: hướng đo, ĐIỂM ĐẦU và ĐIỂM CUỐI của từng số (mép tấm, tâm lỗ, đường gióng nào), đặc điểm nó xác định. Với chuỗi nhiều số liền nhau: kiểm tổng các số = bề rộng/chiều dài tổng của tấm, ghi kết quả (đường gióng đầu chuỗi có thể nằm ở tâm lỗ, không phải mép tấm).
   Mỗi số: ghi chân dim chạm đâu (mép, tâm, góc trong hay ngoài, điểm tiếp tuyến) theo đúng hình vẽ, không suy theo thói quen bản vẽ. Tách rõ "nhìn thấy" (ghi trực tiếp trên bản vẽ) và "số tính được" (tính từ số khác, ghi cách tính).
   Chuỗi không cộng đủ tổng: KHÔNG dùng tổng để chốt; phóng to đầu/cuối từng mũi tên, đo pixel từng khoảng, ghi cả hai cách đọc và số đo. Cặp gương: đọc và đo riêng từng tấm.
3. Lỗ: φ hoặc ren, số lượng, vị trí tâm tính từ hai mép tấm (nêu mép nào), rãnh, vát C, bo R.
   Chỗ uốn: ghi mỗi đường gióng đi qua góc trong hay ngoài (phóng ≥ 300 dpi). Mọi dấu/tem chữ và ghi chú tay: ghi nguyên văn, vị trí, mũi tên chỉ vào đâu (lỗ, cạnh, toàn tấm) và nghĩa đọc được; không bỏ qua dấu nào dù thấy vô nghĩa. Việc diễn giải theo quy tắc để bên kiểm xử lý, không tự kết luận.
4. Ghi chú tay và ghi chú in (độ giãn, KEGAKI, J, 本図/対称, ヨ, tem PIERCING...). Liệt kê MỌI chữ tay trên trang kể cả khi không gần hình; mỗi hình tay phụ (rãnh, lỗ, vát) ghi đủ kích thước và đặc điểm.
5. Không được dừng ở "không chắc" khi còn cách xác minh. Với mỗi số chưa chắc phải làm đủ: (a) phóng ≥ 400 dpi, đổi độ tương phản nếu mờ; (b) đo pixel chân dim với tỉ lệ px/mm từ một kích thước chắc chắn trong cùng hình; (c) đối chiếu ít nhất 2 hình chiếu độc lập; (d) với chữ viết tay, thử từng cách đọc và chọn cách khớp ngữ cảnh trên bản vẽ. Chỉ sau đó mới được ghi "không chắc", kèm: đã thử gì, các cách đọc với số đo mỗi cách, cách nào khớp hơn, ảnh hưởng tới đâu. KHÔNG đoán, KHÔNG làm tròn.
Đo pixel (tỉ lệ px/mm suy từ một kích thước đã biết trong cùng hình) để kiểm tối thiểu 1 vị trí lỗ mỗi hình chiếu; ghi số đo cạnh số đọc.

Ghi kết quả đầy đủ (tiếng Việt, bảng markdown theo trang/chi tiết, cuối file là danh sách điểm không chắc) vào <OUT>/blind_table.md, rồi trả lời ngắn gọn là đã xong và nêu điểm không chắc. Không cần dựng DXF.
---

Cách dùng kết quả: so từng mục của blind_table.md với bảng của người tạo/file DXF; lệch thì xem lại ảnh gốc, không chọn bên nào theo trí nhớ. Phiên đọc mù KHÔNG kiểm được: chọn mặt ngoài, xoay/lật, kegaki, đặt hướng (các phần đó tự kiểm theo mục 3, 9, 10 dxf-sheetmetal).
