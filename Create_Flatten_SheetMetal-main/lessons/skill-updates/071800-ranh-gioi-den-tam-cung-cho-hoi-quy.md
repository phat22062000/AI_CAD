CHỜ PHÁT DUYỆT, chưa sửa

# Đề xuất: rãnh có gióng dừng ở tâm cung, vẽ theo mép ngoài (chờ hồi quy)

Nguồn: 521126-23_26-071800 (1 mẫu). Loại lỗi: Sai kích thước lỗ (rãnh ngắn đi 2R mỗi rãnh, 8 rãnh). Bài học: `lessons\feedback\feedback_ranh-kich-thuoc-den-tam-cung-dau-ranh-071800.md`. Nguyên nhân đã xác định ở phần kích thước (T và DXF khách: đoạn thẳng rãnh dừng đúng ở các số 18.5 / 43 / 48, tâm cung ở đó); phần vì sao agent bỏ sót quy tắc là suy đoán.

## (a) Script (tools\*.py)
Không đề xuất script. `doi_chieu_khach.py` chạy thử trên 26-071800F.dxf: "không đối chiếu được" (chi tiết uốn, không hình chiếu DXF khách nào chồng khít hình phẳng AI) nên không bắt được. `dxf_check.py` không biết kích thước ghi của rãnh (chỉ có tuỳ chọn `--slot NxM` cho ghi chú tổng dài). Chưa có cách đo tự động khi không có ghi chú NxM; nếu muốn, có thể mở rộng `doi_chieu_khach.py` so từng cạnh thẳng rãnh với đoạn thẳng rãnh trong DXF khách theo hình phẳng ở phần chưa uốn, nhưng 1 mẫu, chưa đề xuất.

## (c) SKILL.md
KHÔNG đề xuất sửa lúc này (chờ hồi quy). SKILL.md mục 4.1 dòng 33 đã có câu "Chân gióng đầu rãnh/lỗ dài thường dừng ở TÂM cung R đầu rãnh, không phải mép ngoài: phóng ≥ 250 dpi xem gióng dừng ở mép hay tâm cung; mép ngoài = số ghi ± R; dựng xong đo ngược chiều dài rãnh." Quy tắc đã đủ nghĩa; lỗi lần này là không áp dụng (không rõ vì lỗi đọc hay bỏ sót, không có log). Chạy hồi quy mã này bằng skill hiện tại: nếu vẽ lại vẫn sai thì mới đề xuất thêm vào dòng 33 nhánh "khi có DXF khách thì bóc đoạn thẳng của rãnh và tâm cung (ARC/ELLIPSE) trước để xác định gióng dừng ở đâu, PDF chỉ để đọc số". 1 mẫu.
