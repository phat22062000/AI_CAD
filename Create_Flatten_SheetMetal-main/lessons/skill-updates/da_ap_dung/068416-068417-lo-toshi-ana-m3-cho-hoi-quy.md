ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 148 (2026/11/19, job 20261119122109_updskill)

# Đề xuất: nhãn 通し穴 "M3" vẽ lỗ thông φ3.4 thay vì lỗ mồi φ2.5 (chờ hồi quy)

Nguồn: 521116-14_26-068416, 521116-14_26-068417 (bản gương, cùng một bản vẽ, 1 mẫu). Loại lỗi: Sai kích thước lỗ. Bài học: `lessons\feedback\feedback_toshi-ana-ren-lo-moi-hay-lo-thong.md`. Nguyên nhân là suy đoán (xem bài học), nên chưa sửa quy tắc.

## (a) Script (tools\*.py)
Không đề xuất script. Đã chạy `doi_chieu_khach.py` trên 26-068416F.dxf và 26-068417F.dxf: "không có DXF khách", nên không bắt được. Lỗi phụ thuộc cách hiểu nhãn 通し穴 trong PDF scan, không đo được từ DXF; `dxf_check.py` không có thông tin để so.

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
KHÔNG đề xuất sửa lúc này (1 bản vẽ, nguyên nhân chỉ là suy đoán, chưa rõ quy ước này riêng một khách hay chung). Đợi Chạy hồi quy với hai mã này (đáp án T có sẵn) và thêm mẫu để biết quy tắc hiện tại đủ chưa.

Ứng viên để cân nhắc nếu hồi quy vẫn ra φ3.4 (chưa đề xuất):
- Dòng 148 (đầu dòng, nguyên văn): "- Lỗ taro: vẽ lỗ mồi theo `Quy_Tac_Lo_Moi.md` (M6 → φ5, M8 → φ6.8), TRỪ KHI bản vẽ có ghi chú tay về lỗ mồi ..."
- Hướng sửa (gộp vào dòng 148, không thêm dòng): thêm "Khung ghi chú ghi 通し穴 Mx mà không có vòng ký hiệu trong DXF khách, không có ghi chú tay và không có chữ サラ/ザグリ: coi là lỗ ren, vẽ lỗ mồi mục 1.1 và Flag 1 ghi cả φ lỗ thông mục 2". Chỉ áp dụng sau khi Phát xác nhận quy ước 通し穴 + Mx. Số mẫu hiện tại: 1.
