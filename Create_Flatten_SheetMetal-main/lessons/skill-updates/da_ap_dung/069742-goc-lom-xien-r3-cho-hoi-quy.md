ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 158 (2026/11/20, job 20261120115612_updskill)

# Đề xuất: góc lõm cạnh xiên gặp gờ trên thép dày bản vẽ có ghi chú chung 内側R3 (chờ hồi quy)

Nguồn: 521118-06_26-069742 (1 mẫu). Loại lỗi: Thiếu góc bo R, Sai vị trí lỗ (lệch cụm khe 0.7 đến 0.9 mm). Bài học: `lessons\feedback\feedback_goc-lom-xien-gap-go-r3-ghi-chu-chung.md`. Nguyên nhân là suy đoán (xem bài học), nên chưa sửa quy tắc.

## (a) Script (tools\*.py)
Không đề xuất script. Đã chạy `doi_chieu_khach.py` trên 26-069742F.dxf: báo "không đối chiếu được" (không có DXF khách của mã này), nên không bắt được lỗi. `dxf_check.py` trên F báo 6 góc lồi ≤ 90° chưa bo, nhưng chính T cũng để nhọn 6 góc đó, và không báo hai góc lõm mà T bo R3: tín hiệu hiện có không phân biệt được lỗi thật. Chưa đủ mẫu để định ra kiểm "góc lõm nào phải bo" (T không bo mọi góc), nên không thêm kiểm vào script.

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
KHÔNG đề xuất sửa lúc này (1 mẫu, nguyên nhân chỉ là suy đoán). Đợi Chạy hồi quy với mã này (đáp án T có sẵn) và thêm mẫu cùng loại để biết quy tắc hiện tại (mục 8 dòng 154 và 158: thép 10 đến 16 không bo Laser R, góc lõm không bo trừ thép ≥ 19t) có xung đột với ghi chú chung 内側R3 hay không.

Ứng viên để cân nhắc nếu hồi quy vẫn ra sai (chưa đề xuất):
- Dòng 158 (nguyên văn): "- Góc đã vát C (135°) và góc lõm không bo (trừ thép ≥ 19t). Vát C vẽ thành đoạn chéo."
- Hướng sửa (gộp, không thêm dòng): thêm ngoại lệ "bản vẽ có ghi chú chung R trong cho chỗ uốn (ví dụ 内側R3) thì góc lõm nơi cạnh xiên gặp gờ cần xét bo theo ghi chú đó, không rõ thì Flag 3". Số mẫu hiện tại: 1.
