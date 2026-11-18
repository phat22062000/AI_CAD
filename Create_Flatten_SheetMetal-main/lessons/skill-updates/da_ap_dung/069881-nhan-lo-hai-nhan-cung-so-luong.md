ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 142 (2026/11/18, job 20261118160816_updskill)

# Đề xuất: hai nhãn lỗ cùng số lượng trên một hàng 4 lỗ, gán theo đầu mũi tên rồi đối xứng

Nguồn: đơn 521118-11 mã 26-069881 (loại: Sai kích thước lỗ). Bài học: lessons\feedback\feedback_nhan-lo-hai-nhan-cung-so-luong-dau-mui-ten.md. Nguyên nhân F suy luận thế nào là suy đoán (log không ghi); bằng chứng đáp án: đầu mũi tên 2-Ø4.5 chạm lỗ cách mép trên 6, đầu mũi tên 2-M4 chạm lỗ cách mép dưới 14.5, T gán φ4.5 cho hai lỗ cách mép 6 và M4 cho hai lỗ cách mép 14.5. Phần phay (フライス) của cùng mã là nguyên nhân khác, ở file 069881-chu-tay-phay.md.

## (a) Script
Không đề xuất script. Chạy thử `doi_chieu_khach.py` trên F: "không có DXF khách" (đơn chỉ có PDF), không bắt được. Cỡ lỗ theo nhãn phải đọc mũi tên trên bản vẽ, không đo được từ DXF.

## (c) SKILL.md: sửa dòng 142 (không thêm dòng mới)
Dòng 142 hiện tại: "  - Mỗi ghi chú lỗ (n-Mx, n-φx) xác định theo ĐẦU MŨI TÊN của đường dẫn, đối chiếu ≥ 2 hình chiếu (cạnh + bằng); không gán chỉ vì lỗ nằm trong khung hình đang xem."
Dòng mới: "  - Mỗi ghi chú lỗ (n-Mx, n-φx) xác định theo ĐẦU MŨI TÊN của đường dẫn, đối chiếu ≥ 2 hình chiếu (cạnh + bằng); không gán chỉ vì lỗ nằm trong khung hình đang xem. Hai nhãn cùng số lượng trên một hàng/cạnh (ví dụ 2-Ø4.5 và 2-M4 cho 4 lỗ): mũi tên mỗi nhãn chỉ chạm một lỗ; lỗ còn lại của nhãn đó lấy từ các lỗ chưa gán có cùng khoảng cách tới mép (đối xứng) với lỗ đã chạm, KHÔNG chia theo cặp lỗ nằm gần nhãn; không chia được duy nhất thì Flag 8."
Lý do: bản F chia theo cặp trên/dưới nên đổi cỡ hai lỗ; dòng 142 chưa nói cách chia các lỗ không có mũi tên. Có thể gộp với đề xuất chờ duyệt cho dòng 148 nếu Phát muốn (đều là gán lỗ theo nhãn, nhưng nguyên nhân khác nhau nên để riêng).
Số mẫu: 1. Loại lỗi: Sai kích thước lỗ.
