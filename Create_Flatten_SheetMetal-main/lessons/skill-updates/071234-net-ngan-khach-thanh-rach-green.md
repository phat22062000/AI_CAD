CHỜ PHÁT DUYỆT, chưa sửa

# Đề xuất: nét ngắn của khách ở góc lõm là chỗ rạch Green, không chép làm LINE biên

Nguồn: 521125-14_26-071234 (1 mẫu). Loại lỗi: Sai rạch Green, Sai biên dạng ngoài. Bài học: `lessons\feedback\feedback_net-ngan-khach-o-goc-lom-la-cho-rach-green.md`. Nguyên nhân xác định từ file: F chép nét đỏ dài 1.2 của DXF khách ở 2 góc lõm thành LINE biên, T thay bằng rạch Green 3 entity ở mỗi góc. Lý do AI không nhận ra là suy đoán.

## (a) Script (tools\*.py)
Đích 1: `tools\doi_chieu_khach.py`. Đã chạy thử trên 26-071234F.dxf (--src thư mục đơn): báo "biên khớp 100%, lỗ trùng tâm 2/2", KHÔNG bắt được lỗi. Đề xuất thêm: trong DXF khách tìm các LINE màu đỏ (màu 1) hoặc ngắn ≤ 2t có một đầu cụt ở góc lõm; mỗi nét như vậy mà F không có Green trong bán kính ≈ 1.2 quanh góc lõm thì báo LỖI "khách có nét rạch tại (x; y) nhưng F không có Green".
Đích 2: `tools\dxf_check.py`. Đã chạy thử (--mat SS --t 3.2; kết quả tương tự với SUS 1.2): 9 LỖI nhưng đều là "hở biên"/"vòng biên rời", không nêu thiếu Green; cảnh báo "góc lõm 90° không rạch Green" (dòng 364 to 365) không chạy vì các góc này có 3 đoạn chung 1 điểm nên không vào `sharp_ccv`. Đề xuất thêm kiểm: LINE ngắn ≤ 2t trong lớp biên có một đầu cụt (chạm đúng một entity) thì báo LỖI "khe cụt ở (x; y): thay bằng rạch Green 3 entity".

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
KHÔNG đề xuất sửa: chỉ có 1 mẫu và đã có script đề xuất ở trên (quy tắc rạch tại góc lõm dòng 119 đến 125 đã đủ nội dung; lỗi là bỏ sót khi chép DXF khách). Nếu gặp lại ở mã thứ hai thì cân nhắc thêm vào cuối dòng 125 (sửa dòng cũ, không thêm dòng mới): "Nét ngắn ≈ t của khách ở góc lõm là chỗ rạch, vẽ đủ 3 entity Green, không chép làm LINE biên." Số mẫu hiện tại: 1 mã.
