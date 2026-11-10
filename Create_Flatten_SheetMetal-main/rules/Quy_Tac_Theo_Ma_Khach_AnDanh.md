# Khách hàng yêu cầu đặc biệt (bản gọn, tra theo mã khách)

Bản gốc: DS_khach_hang_yeu_cau_dac_biet.md. Khách không có trong danh sách này thì áp quy tắc chung (Laser R theo bảng).

## Tra nhanh theo nhóm quy tắc
- **Không bo R góc ngoài (giữ góc nhọn) nếu không chỉ định:** 325, 412, 425, 473, 768, 779, 790, 859, 979. Riêng 777: mặc định không bo, chỉ thêm R0.5 ở góc quá nhọn.
- **Bo R3 góc ngoài khi không chỉ định:** 765 (cả chỗ vát R3), 898 (không chỉ thị hoặc chỉ ghi (R) thì R3).
- **Mọi piercing = lỗ xuyên:** 407, 473, 518, 768, 810, 899.
- **Piercing/ponch/marking = lỗ trắng:** 703 (ポンチ), 764 (ピアス, マーキング), 781, 898 (punch), 908, 921, 940, 955.
- **Kegaki vị trí hàn dù không có chỉ thị:** 676 (hàn tại khách), 851, 899, 938, 957.
- **PDF là chuẩn (DXF chỉ tham khảo):** 395, 407, 544, 676, 710. **DXF/dữ liệu là chuẩn:** 240, 829, 915, 964.
- **Lưu thêm DWG:** 789, 794, 825 (khách này chỉ DWG, không DXF).

## Chi tiết từng khách
| Mã | Quy tắc |
|---|---|
| 240 | Lập theo dữ liệu gốc, coi là đúng, không kiểm tra kích thước. |
| 309 | Có hình vẽ tay thì làm theo đó. |
| 325 | Góc không chỉ dẫn: không bo R góc ngoài. |
| 390 | Đường xanh = kegaki; chữ xanh hoặc đỏ = không cần kegaki. DXF được xem là mặt (surface) chi tiết. |
| 395 | DXF khác PDF thì PDF là chuẩn. Thiếu kích thước thì tham khảo DXF. |
| 407 | Mọi piercing làm lỗ xuyên. PDF là chuẩn; lệch nhiều so DXF thì hỏi lại. |
| 412 | Không chỉ định: không bo R góc ngoài. |
| 425 | Góc không chỉ thị: không bo R góc ngoài. |
| 433 | PDF và DXF khác nhau: chỉ xác nhận khi sai khác ≥ 1 mm. |
| 473 | Mọi piercing lỗ xuyên. Không bo R. Chỗ khác màu trong DXF = kegaki. Lỗ không khoét được thì hỏi lại. |
| 512 | Tấm gân: mặt bản vẽ chỉ định là mặt có gân. PDF không hiện kích thước lỗ, xem DXF. |
| 513 | Taro và khoét côn chỉ làm đến lỗ mồi (không khoan xuyên được thì đột/piercing). |
| 514 | Không có đường tâm vẫn OK nếu đặt ở tâm; không ở tâm sẽ có chỉ thị. Tấm gân không ghi mặt: mặt trước là mặt gân; mặt sau sẽ có chỉ thị. |
| 518 | Mọi piercing làm lỗ xuyên. Repeat: sửa tất cả piercing thành lỗ xuyên. |
| 544 | Có DXF vẫn làm theo PDF. |
| 553 | Lỗ gia công cơ khí (taro, doa bậc, khoét vát…): dày ~4.5t khoan lỗ mồi; từ 6.0t trở lên đột xuyên = tạo lỗ mồi (CIRCLE đường kính lỗ mồi theo Quy_Tac_Lo_Moi.md, ví dụ M6x1 → φ5) khoét xuyên tấm. KHÔNG dùng POINT (kể cả POINT xanh). |
| 587 | Vát C: số trước dấu góc là kích thước (3x45° → C3). |
| 610 | Không chỉ thị thì chỉ vẽ biên ngoài. Chỗ có ▽▽, ▽ hoặc ※ (xem ngoài khung) vẽ +2. |
| 621 | Chỉ gia công chỗ có chỉ dẫn; không có thì chỉ biên ngoài. |
| 630 | Không gắn joint vào lỗ. Lỗ khoan/pierce ở chu vi ngoài làm bình thường. |
| 646 | Dùng bảng giãn riêng Bang_Do_Gian_AICOKU ALPHA (kể cả tự uốn tại công ty). |
| 676 | Có DXF vẫn theo PDF; chênh lớn thì hỏi lại. Hàn tại khách: tất cả cần kegaki. |
| 703 | ポンチ = lỗ trắng. Đôi khi tính uốn ×2. |
| 710 | Khác nhau (vài mm) giữa dữ liệu và bản vẽ: lấy bản vẽ làm chuẩn; DXF chỉ tham khảo. |
| 712 | Chỉ gia công chỗ có ghi "旭". Ghi "全加工" thì khoét lỗ đúng bản vẽ. Độ dày bản vẽ có thể khác đơn (vd bản vẽ t16, đơn t19). Có chỉ thị đắp thịt +2 mm (▽▽), đừng bỏ sót. マスキング và ピアス = lỗ trắng; lỗ xuyên có chỉ thị riêng. Vát C không ghi: C5 (không cần hỏi). SS19t: lỗ cách biên ≤ 5 mm thì đắp thịt rồi mới khoét. Hình dạng, có/không lỗ theo chỉ thị của kinh doanh. |
| 725 | Đôi khi khoét lỗ nhỏ hơn ½ độ dày (cần xác nhận). |
| 733 | DXF khác bản vẽ thì phải liên hệ xác nhận. |
| 745 | Lỗ không xuyên có thể làm bằng piercing. Bo R làm kích thước ngắn lại thì kiểm tra/xác nhận. |
| 760 | Mọi nét đứt là kegaki (màu hoặc loại nét có thể khác). Kiểm tra dữ liệu. |
| 764 | ピアス, マーキング = lỗ trắng (chú ý chỉ thị マーキング, cần xác nhận). Bản vẽ của khách này: taro → lỗ trắng (thiếu ghi cũng làm lỗ trắng, không cần hỏi). |
| 765 | Không chỉ định vẫn bo góc ngoài R3; chỗ vát cũng R3. |
| 768 | Không chỉ định: không bo R góc ngoài. Mọi piercing là lỗ xuyên. |
| 776 | Lỗ mồi taro và chỗ khó thấy: theo ghi chú viết tay; độ giãn khi uốn cũng ghi tay. ピアス = lỗ xuyên, ポンチ = lỗ trắng; lỗ xuyên có chỉ thị. Nội dung trong ( ): có khi cần, có khi không, cần xác nhận. |
| 777 | Kiểm tra dữ liệu. Mặc định không bo R góc ngoài; chỉ thêm R0.5 ở góc quá nhọn dễ chảy khi cắt. |
| 779 | Taro: luôn khoét lỗ mồi. Lỗ trên ống vuông (□) lấy kích thước +1 (cần xác nhận). Không bo R; không chỉ thị thì làm đúng bản vẽ. |
| 780 | Góc giao thoa do uốn: được gia công lỗ thoát không cần xác nhận. |
| 781 | Chỉ gia công lỗ Φ; taro, khoan, khoét bậc… làm bằng white pierce (lưu ý khi chỉnh NC). Đánh dấu = white pierce. |
| 789 | Bản vẽ nhiều kegaki thì lưu thêm cả DWG. |
| 790 | Không bo R (góc nhọn); có chỉ thị thì làm theo. |
| 794 | Hàng Shinto Kogyo không chỉ định vát C: dùng kích thước C ghi trong chú thích. Lỗ gần chỗ uốn có thể biến dạng: không hỏi lại, đánh dấu bằng bút sơn trắng rồi khoan lỗ. Lưu cả DWG. |
| 802 | Kích thước taro ghi tay cần kiểm tra lại theo bảng kích thước. |
| 803 | Bo R làm co ngắn thì xác nhận từng trường hợp. |
| 804 | Cần xác nhận trước khi vẽ (dữ liệu số có thể khác bản vẽ); kiểm tra dữ liệu. Đôi khi có chỉ thị vị trí piercing và micro joint (không xóa khi chỉnh dữ liệu). |
| 810 | Mọi lỗ đột là lỗ xuyên. |
| 824 | SUS, SS, AL: không gắn micro joint cho mọi lỗ (kể cả lỗ dài). Lượng giãn ghi một phía nên tính ×2. Khi uốn góc có thể dùng độ giãn chuẩn Asahi. |
| 825 | Theo quy định nội bộ, không cung cấp DXF; không nhận yêu cầu. Tạo file DWG. |
| 829 | Có dữ liệu thì không cần đối chiếu bản vẽ; lấy dữ liệu làm cơ sở chính. |
| 830 | Gia công đúng chỉ dẫn bản vẽ (kể cả bán kính R ở chu vi ngoài). |
| 843 | Chiều dài bù uốn chỉ một phía nên ×2. A5052 dày 5: bù uốn 7.72 mm. Ghi tay 片伸び x: giãn chỗ uốn = 2 × x, kể cả góc ≠ 90°. |
| 850 | Đôi khi lỗ nhỏ hơn ½ độ dày (cần xác nhận). Lỗ quá gần nhau: thêm R1 thành lỗ Daruma. Không "heso" = không có phần nối giữa các lỗ. |
| 851 | Cho phép biến dạng lỗ do uốn. Vị trí hàn cần kegaki dù không chỉ thị. Tấm hàn nghiêng có hai kích thước: dùng kích thước ngắn hơn. |
| 859 | Thép đặc chủng Nakajima (cũ). Trừ khi chỉ định, không bo R góc ngoài (giữ góc vuông). R có ký hiệu ※ có thể bỏ qua. Dày ≥ 19t cần xác nhận. Đôi khi lỗ nhỏ hơn ½ độ dày (cần xác nhận). |
| 875 | Tấm đến 9t: lỗ nhỏ hơn ½ độ dày thì không gia công (làm piercing). Tấm từ 12t: mọi lỗ nhỏ hơn độ dày đều làm lỗ trắng. |
| 879 | Cắt góc rồi uốn thì không tạo khe (slit). Cho phép biến dạng lỗ. |
| 880 | Thời gian CAD tất cả 1 phút. |
| 898 | Lỗ mồi taro và khoét bậc đầu vít: nội bộ (có J) theo quy định nội bộ; tại khách (không J) làm lỗ trắng. Không chỉ thị hoặc chỉ ghi (R): mặc định R3. Góc C không chỉ thị: C3. Uốn góc: kích thước trong + kích thước trong = tổng chiều dài. Punch = lỗ trắng. |
| 899 | Vị trí hàn phải kegaki. Đường kính lỗ taro có thể khác kích thước công ty tự gia công, cần xác nhận. Mọi piercing làm lỗ xuyên. |
| 905 | Vẽ gauge: xem sheet riêng. Tấm t1.6 mà bản vẽ và hình tạo ra khác kích thước: xác nhận có phải gauge không. Gauge: khoét tất cả lỗ, φ5 đều, không vát, không lỗ vuông, không khe cắt; vẫn bo R theo độ dày (R0.5 góc ngoài). Đến Φ50 khoét φ5 (trừ lỗ khí). Lỗ doa (リーマ) của gauge không khoét, nếu cần sẽ có chỉ thị; lỗ doa của sản phẩm hỏi lại mỗi lần. "表裏共通": khoét lỗ mặt trước và sau cùng lúc. Dấu × = lỗ trắng. |
| 907 | Hướng vân Hairline ghi ở mép bản vẽ. |
| 908 | Lỗ taro sâu nhỏ hơn chiều dày tấm: white pierce. Mọi lỗ doa dùng white pierce (chi tiết lặp cũng sửa). Laser mark = white pierce. |
| 915 | Có DXF thì dữ liệu là chuẩn. |
| 921 | Đánh dấu tâm (white pierce/đột nguội). Vật mỏng dễ cháy xém hoặc nứt nên có khi dùng white pierce. |
| 938 | Kể cả không gia công nội bộ, vị trí hàn vẫn cần kegaki. |
| 940 | Ghi chú M12: lỗ Ø10.5 (chỉ áp dụng M12?). Mark, pin hole, punch = white pierce. |
| 955 | Đã xác nhận dữ liệu. Có ký hiệu ○-point thì kẻ dấu (đánh dấu bằng white pierce). |
| 956 | Lỗ không gia công được phải chuyển sang đột (pierce): xác nhận với khách là đột hay bỏ lỗ. |
| 957 | Kể cả không gia công nội bộ, vẫn kegaki tại vị trí hàn. Chấn SUS cần xác nhận mặt trước/sau vật liệu. |
| 964 | Kích thước lấy theo dữ liệu là đúng. Chi tiết "耐震固定用金具": mặt trong của phần uốn chữ L làm mặt ngoài (mặt chuẩn). |
| 974 | Khác với dữ liệu thì xác nhận lại. Kiểm tra dữ liệu bản vẽ trong DXF sản phẩm của đợt yêu cầu báo giá. |
| 978 | Lỗ không gia công được do tấm quá dày: cho dùng pierce trắng, không cần hỏi. Uốn góc dùng độ giãn Asahi (chỉ góc uốn khác 90°). |
| 979 | Không chỉ thị: không bo R góc ngoài. |
