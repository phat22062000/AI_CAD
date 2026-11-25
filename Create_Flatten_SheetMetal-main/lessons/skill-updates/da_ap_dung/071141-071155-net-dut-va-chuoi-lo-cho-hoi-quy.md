CHỜ PHÁT DUYỆT, chưa sửa

# Đề xuất: nét đứt có dim giữa hai nét và chuỗi lỗ lệch đều 1 mm (chờ hồi quy)

Nguồn: 521125-01_26-071141, 521125-01_26-071155 (cùng một bản vẽ, 1 mẫu thực chất). Loại lỗi: Sai vị trí lỗ, Sai độ giãn dài. Bài học: `lessons\feedback\feedback_dim-giua-hai-net-dut-do-tu-net-buoc.md` (nét đứt: nguyên nhân xác định từ bản vẽ) và `lessons\feedback\feedback_chuoi-lo-lech-deu-1mm-khong-dong-ve-mep-phoi.md` (lỗ lệch 1 mm: nguyên nhân chỉ là suy đoán). Chưa sửa quy tắc vì chỉ 1 bản vẽ và quy tắc chân gióng/đo ngược đã có.

## (a) Script (tools\*.py)
Không đề xuất script. Đã chạy `doi_chieu_khach.py` trên 26-071141F.dxf và 26-071155F.dxf: báo "không có DXF khách" nên không so được. `dxf_check.py` trên 26-071141F (--mat SUS --t 1.2): 0 lỗi, 6 cảnh báo về đường uốn không có cặp và góc lõm không rạch Green (không liên quan lỗi này, và không bắt được vị trí nét đứt sai hay lỗ lệch 1 mm). Vị trí lỗ và nét đứt phụ thuộc dim trên bản vẽ, không đo được từ DXF.

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
KHÔNG đề xuất sửa lúc này (1 bản vẽ; lỗ lệch 1 mm chưa có nguyên nhân). Đợi Chạy hồi quy với hai mã này (đáp án T có sẵn) để biết quy tắc chân gióng (SKILL mục 2, dòng 33, 39, 46) và đo ngược hiện tại đã đủ chưa.

Ứng viên nếu hồi quy vẫn sai (chưa đề xuất): gộp vào dòng 46 (chân dim) ý "kích thước ghi giữa hai nét đứt: một đầu mũi tên có thể chạm nét đứt khác ở mức bậc, đo từ nét đó, và nét đó phải có trong DXF". Số mẫu hiện tại: 1.
