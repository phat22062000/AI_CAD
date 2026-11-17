ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 156 (2026/11/17, job 20261117155115_updskill)

# Đề xuất: relief góc vuông (直角逃がし) ở biên, kể cả bản OUTLINE ONLY

Nguồn: đơn 521109-22 mã 26-066809. Loại lỗi: Sai biên dạng ngoài (thiếu relief), Thiếu Flag. Số mẫu: 1 (mã 26-066808 cùng đơn cũng có chú thích 2-ø1.5 直角逃がし nhưng bản đúng không có relief, chưa rõ lý do). Bài học: lessons\feedback\feedback_relief-goc-vuong-bo-sot.md.

## (a) Script
Không đo được từ DXF: relief chỉ có trên chữ chú thích của PDF; không có DXF khách để so (doi_chieu_khach: "không có DXF khách"). Không đề xuất script.

## (c) SKILL.md: gộp vào dòng 156 (không thêm dòng mới)
Dòng 156 hiện tại: "- R0.5 là mặc định, không tự thay. Khi góc lồi quá nhỏ (cạnh kề quá ngắn, cung R0.5 không có chỗ tiếp tuyến) Flag 19 (mục 11.4)."
Thêm vào cuối dòng: "Chú thích 直角逃がし (ø hoặc R) chỉ vào góc lõm vuông của biên (kể cả bản OUTLINE ONLY): vẽ relief tại góc đó, vòng tâm tại đỉnh góc đường kính = số ghi, hai cạnh dừng ở tiếp điểm với 2 cung R2 nối; không xác định được góc nào hoặc số góc không khớp "n-" thì Flag 5."
Lý do: bản F bỏ relief ø3 (góc nhọn), bản đúng có vòng R1.5 tâm đỉnh góc và hai cung R2 tiếp tuyến. Số mẫu: 1, cần Phát xác nhận đây có phải quy tắc chung.
