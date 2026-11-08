# Đơn 521102-16: thử chạy song song (cách 5) và overlay (cách 6)

Khách 393, 6 chi tiết SPCC (065389/390/393 t1.6 uốn 90°, 065392 t2.3 phẳng, 065394/395 t0.8 phẳng hình cung). File: `521102-16_ALL.dxf` (đã lưu vào thư mục đơn trên máy, dung lượng khớp 323 496 byte).

## 1. Thời gian (từ lúc nhận việc đến lúc commit file: khoảng 24 phút)
| Bước | Thời gian thực | Nếu làm tuần tự (ước tính từ tổng thời gian từng subagent) |
|---|---|---|
| Agent chính: tìm file, stage, đọc skill/Excel/PDF, lập order_context.json | khoảng 2,7 phút | như nhau |
| 5 subagent dựng spec + overlay chạy song song | 7,7 phút (chậm nhất là nhóm 065394+395: 464 s; còn lại 98 / 231 / 235 / 238 s) | khoảng 21 phút (tổng 1 266 s) |
| Gộp ALL.dxf vào Template + ezdxf audit | dưới 1 giây (script gộp viết sẵn trong lúc chờ) | như nhau |
| dxf-check: 6 subagent đọc mù PDF song song | 8,6 phút (chậm nhất 065394: 515 s) | khoảng 26 phút (tổng 1 568 s) |
| Chạy dxf_check.py, so bảng đọc mù với file, commit về máy | khoảng 7 phút | như nhau |
Subagent dùng khoảng 1,2 triệu token cho cả hai pha (dựng khoảng 640 nghìn, đọc mù khoảng 570 nghìn).

## 2. Kết quả kiểm
- ezdxf audit 0 lỗi; phần sau ENTITIES trùng Template; thứ tự hình đúng Excel; không Flag nào cần ghi.
- dxf_check.py: LỖI 0. Các cảnh báo của script đều không phải lỗi: "không có cạnh thẳng áp Ox/Oy" (065389, 065394, 065395: biên là cung, không hướng nào thoả), "cặp gương 394:395" (hai chi tiết không phải cặp gương, mình khai nhầm để thử), "nguồn không có lớp chữ" (đã có bảng đọc mù).
- So bảng đọc mù độc lập với file: kích thước phôi, vị trí lỗ, góc lỗ trên R101 (167°/106°/45°, 167°/87°), ヌキ 32x21 ở (-28; 53), đường uốn, giãn 2.64 (số tay trùng bảng Asahi t1.6) đều khớp, lệch pixel khoảng 1 mm trở xuống (lớn nhất 1,2 mm ở đầu cung R16 phải của 065395, trong sai số đo ảnh).
- Mặt vẽ 065389 (lật trái-phải so với hình đứng, tai nằm bên phải tâm sau khi lật) mình tự xác lại từ hình bằng (hình trên) và hình chiếu phải: đúng. Hướng 065393 (lỗ y = 6 và 21 tính từ mép trước) khớp hình bằng.

## 3. Cần Phát xác nhận (chưa phải lỗi)
1. 065394 và 065395: phôi 197,55 x 107 và 136,37 x 107, CAD依頼書 ghi 214 x 107 và 161 x 107 (lệch X 16,5 và 24,6 mm). Hình bản vẽ đo và overlay cho kết quả như file; chỉ có số 依頼 khác. Chưa Flag vì Flag chỉ dùng cho lệch PDF/DXF khách.
2. Cạnh vát hai đầu 065394/395 chỉ có góc (33.7°) trong ngoặc làm kích thước tham khảo (cạnh dài 11,1 tính ra, đọc mù đo 9,9 đến 10,6). Mình dùng 33.7° vì tan khớp 2/3 và overlay khớp 1 pixel. Theo mục 0 chặt thì có thể phải Flag 3; chờ Phát quyết.
3. Góc 41° của ヌキ (065394): đọc mù đo 40,0 đến 40,5, nhãn ghi 41; file theo nhãn (chênh khoảng 0,5 mm ở đầu cạnh 32).

## 4. Nhận xét ưu và nhược
Cách 5, chạy song song:
- Ưu: pha dựng giảm từ khoảng 21 xuống 7,7 phút; pha đọc mù từ khoảng 26 xuống 8,6 phút. order_context.json giữ J, giãn 2.64, quy tắc R cho cả đơn, 6 subagent không ai tự đổi. Spec JSON làm bước gộp vào Template hầu như bằng 0 giây và không sai cấu trúc file.
- Nhược: tốn token (mỗi subagent đọc lại toàn bộ skill). Thời gian bị chặn bởi chi tiết khó nhất: nhóm 394+395 (cung, ヌキ, R16) mất 7,7 phút trong khi 4 chi tiết đơn giản mất 2 đến 4 phút; nên tách 394 và 395 thành hai subagent. Đơn chỉ 6 chi tiết, 4 chi tiết đơn giản nên lợi ích thực tế chủ yếu ở hai tấm cung.
- Chỗ lệch quy tắc: khi chi tiết đối xứng (065390, 065393) mỗi subagent tự chọn hướng 0 hoặc 180 độ; kết quả đúng nhưng skill chưa có quy tắc phá thế cân bằng, agent chính phải kiểm lại.

Cách 6, overlay:
- Ưu: mỗi chi tiết có ảnh chồng để Phát nhìn nhanh; hai tấm cung (394, 395) khớp nét in, lệch tối đa 0,2 đến 0,3 mm, đây là bằng chứng hình học tốt nhất của đơn. Mất khoảng 35 đến 90 giây mỗi chi tiết.
- Nhược: cả 6 overlay không bắt được lỗi nào mới, vì kết quả đúng; overlay không kiểm được mặt vẽ (lật trái-phải), vị trí đường uốn trên phôi, hay kích thước tới 0,1 mm. Chi tiết đã uốn (389, 390, 393) chỉ chồng được từng mặt phẳng. Bản scan nghiêng 0,4 đến 0,5 độ phải xoay trước.
- Kết luận: overlay hữu ích để Phát duyệt hình cung và hình phức tạp; với tấm phẳng chữ nhật có lỗ thì giá trị thấp. Khuyên dùng bắt buộc cho chi tiết có cung, hình tay hoặc nhiều đỉnh; bỏ qua cho tấm phẳng chữ nhật có lỗ.

## 5. Thư mục
`/mnt/project-files/521102-16/`: ALL.dxf, `parts/<mã>/spec_*.json` và `note_*.md` (thời gian, bảng mục 12), `blind/blind_table_*.md`, `review/` (ảnh overlay), `merge_all.py`, `order_context.json`, `subagent_prompt.md`. Trên máy: `AI_Work\Thang-11\02-11-2026\521102-16\` (ALL.dxf và review\).
