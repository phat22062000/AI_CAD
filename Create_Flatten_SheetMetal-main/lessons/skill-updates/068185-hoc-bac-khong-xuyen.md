ĐÃ ÁP DỤNG phần (c) vào skills\dxf-sheetmetal\SKILL.md dòng 85 và dòng 80 (2026/11/17, job 20261117133354_updskill); ĐÃ ÁP DỤNG phần (a) vào tools\doi_chieu_khach.py (2026/11/17, Claude làm tay theo lệnh của Phát)

# Đề xuất: hốc/rãnh/bậc không xuyên không vẽ thành biên cắt

Nguồn: đơn 521113-05, mã 26-068185 (13/11/2026). Loại lỗi: Sai biên dạng ngoài (phụ: Sai hướng đặt). Số mẫu: 1 mã cho hốc không xuyên; cùng chủ đề "không xuyên thì không vẽ" với 26-068884 (khoét đầu vít) → 2 mẫu cho chủ đề chung.

## (a) Script, ưu tiên 1: tools\doi_chieu_khach.py (thêm cảnh báo)
Kết quả chạy thử trên F: `068185: hình phẳng | 300-30.dxf | xoay 180° | biên khớp 100%, lỗ trùng tâm 2/2` → script hiện tại KHÔNG bắt được (so cùng đường viền hốc với DXF khách nên khớp).
Đề xuất thêm kiểm: khi DXF khách có thêm block/hình chiếu dẹt (một chiều xấp xỉ t) cạnh hình chiếu bằng, tìm nét ngang nằm hẳn giữa chiều dày (0 < y < t) và các đường gióng đứng chỉ chạy một phần chiều dày; khoảng x của chúng trùng với đoạn biên nào của hình chiếu bằng thì báo CẢNH BÁO "đoạn biên x a-b có thể là hốc không xuyên (sâu d / t), kiểm hình chiếu cạnh, không cắt nếu đúng". Thêm: DIMENSION có giá trị < t đặt trên hình chiếu cạnh cũng là dấu hiệu. Chỉ cảnh báo, không tự sửa.
Lý do: lỗi đo được bằng hình học của DXF khách; script bắt được thì Tự check báo trước khi giao, 0 token.

## (c) SKILL.md, ưu tiên sau: gộp vào dòng 85 (không thêm dòng mới)
Dòng 85 hiện tại (nguyên văn đầu dòng): "- Lỗ khoét côn/khoét bậc và ký hiệu ren trong DXF chỉ là ký hiệu: không vẽ, chỉ vẽ lỗ mồi. Cỡ ren (đường kính vòng ký hiệu) trong DXF vẫn phải so với cỡ ren PDF, ..."
Dòng mới (chỉ đổi câu đầu, phần sau giữ nguyên): "- Chỉ cắt đường xuyên hết chiều dày. Lỗ khoét côn/khoét bậc, ký hiệu ren, và hốc/rãnh/bậc không xuyên (hình chiếu cạnh hoặc mặt cắt có đáy giữa chiều dày, dim sâu < t, chữ 深サ/段/座) trong DXF hay PDF đều không vẽ: lỗ chỉ vẽ lỗ mồi/lỗ thông, biên ngoài giữ theo mép xuyên. Rãnh/khuyết trên hình chiếu bằng của tấm dày phải soi hình chiếu cạnh (cả block khác trong DXF khách) trước khi lấy làm biên; chưa chắc thì vẽ biên xuyên và Flag 1. Cỡ ren (đường kính vòng ký hiệu) trong DXF vẫn phải so với cỡ ren PDF, ..."
Dòng liên quan, không mâu thuẫn: dòng 80 ("bỏ hình chiếu khác, kích thước, đường tâm") nói bỏ hình chiếu khác khỏi DXF xuất, không cấm đọc chúng; nếu cần có thể thêm "(vẫn đọc để biết đặc điểm xuyên hay không)" vào dòng 80 thay vì dòng mới.
Lý do: hình chiếu bằng vẽ đường viền hốc bằng nét liền như biên ngoài, chỉ hình chiếu cạnh mới phân biệt được; đây là chỗ bắt buộc đọc bản vẽ. Gộp vào dòng 85 vì cùng nguyên tắc với khoét bậc đầu vít.

## Hướng đặt (phụ)
F xoay 180° so với DXF khách, T giữ hướng DXF. Dòng 60 ("Phẳng không uốn: giữ hướng hình chiếu đứng") đã đủ; không đề xuất sửa, chỉ ghi nhận. Ghi chú: tiến độ ghi kind=uon cho mã này dù là tấm phẳng.


## Kết quả phần (a) (17/11/2026)
Đã thêm vào tools\doi_chieu_khach.py: Khach.profiles() tìm hình chiếu cạnh (chữ nhật mỏng bằng chiều dày, cùng bề rộng hình phẳng) rồi lấy các nét ngang nằm giữa chiều dày; nếu hình AI có cạnh/cung nằm trọn trong đoạn đó thì báo CẢNH BÁO "Sai biên dạng ngoài: ... hốc/bậc KHÔNG xuyên". Bỏ qua khoét đầu vít/ザグリ (có vòng tròn cùng tâm và bán kính bằng nửa bề rộng bậc). Cảnh báo này không kéo theo "Thiếu Flag" (Flag 1 không phải cách xử lý).
Chạy thử: 26-068185F báo đúng 2 rãnh R10 (x 279.5-299.5 và 434.9-454.9, sâu 2.5/5); 26-068185T không báo; 5 đơn (37 mã) và 6 file F còn lại không báo giả. Không bắt được: DXF khách không vẽ hình chiếu cạnh, hốc nửa chiều dày chỉ ghi chú bằng chữ, nét gạch tay trên PDF.
