ĐÃ ÁP DỤNG vào skills\dxf-sheetmetal\SKILL.md dòng 27 (2026/11/18, job 20261118160816_updskill)

# Đề xuất: chữ tay フライス (phay) khoanh quanh lỗ/rãnh thì không vẽ

Nguồn: đơn 521118-11 mã 26-069881 (loại: Thừa lỗ, Sai biên dạng ngoài). Bài học: lessons\feedback\feedback_chu-tay-phay-khong-ve.md. Bằng chứng: F tự Flag "chữ フライス ... chưa rõ có phải phay sau laser: vẽ theo kích thước ghi" nhưng vẫn vẽ lỗ φ4.04 và rãnh rộng 4.04; T không vẽ cả hai. Ý nghĩa "フライス = phay sau laser" suy từ T, CẦN Phát xác nhận trước khi áp dụng. Nguyên nhân khác với phần gán nhãn lỗ của cùng mã (file 069881-nhan-lo-hai-nhan-cung-so-luong.md).

## (a) Script
Không đề xuất script. Nghĩa chữ tay phải đọc từ bản vẽ, không đo được trong DXF.

## (c) SKILL.md: sửa/gộp dòng 27 (không thêm dòng mới)
Dòng 27 hiện tại: "- Lỗ/gia công bị gạch (bút đỏ, gạch chéo): không vẽ. Áp cho cả rãnh, khoét, vát: nét hình vẫn in và DXF khách vẫn có nhưng MỌI kích thước của gia công đó bị gạch bỏ thì coi là bị hủy, không vẽ, ưu tiên hơn "hình dạng theo DXF" (dòng 25, mục 4.2); liệt kê phần đã bỏ trong báo cáo."
Dòng mới: "- Lỗ/gia công bị gạch (bút đỏ, gạch chéo) hoặc có chữ tay chỉ công đoạn khác laser (フライス phay...) khoanh quanh: không vẽ. Áp cho cả rãnh, khoét, vát: nét hình vẫn in và DXF khách vẫn có nhưng MỌI kích thước của gia công đó bị gạch bỏ thì coi là bị hủy, không vẽ, ưu tiên hơn "hình dạng theo DXF" (dòng 25, mục 4.2); liệt kê phần đã bỏ trong báo cáo. Chữ tay đọc rõ nghĩa thì không cần Flag 5; dung sai của chỗ đã bỏ không cần Flag 18."
Lý do: F đọc được chữ フライス, nghi phay sau laser nhưng vẫn vẽ (do dòng 227 cấm bỏ chi tiết chỉ vì ghi chú không rõ); đáp án không vẽ. Số mẫu: 1. Loại lỗi: Thừa lỗ, Sai biên dạng ngoài.
