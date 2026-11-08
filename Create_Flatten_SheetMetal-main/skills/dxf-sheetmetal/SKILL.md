---
name: "dxf-sheetmetal"
description: "Tạo bản vẽ triển khai kim loại tấm từ hình vẽ trong file PDF hay dữ liệu DXF."
metadata:
  version: "2026.11.04-1"
---

Tài liệu project (`knowledge/Context_Laser/` hoặc Project docs): `Quy_Tac_Laser.md`, `DS_Khach_Hang.md`, `Quy_Tac_Lo_Moi.md`, `Bang_Do_Gian_Asahi.xlsx`, `Bang_Do_Gian_AICOKU ALPHA.xlsx`, `Template.dxf`.

## 0. QUY ĐỊNH BẮT BUỘC (nghiêm cấm vi phạm)
- BẮT BUỘC: khi tạo hình phải dựa theo kích thước được ghi trên PDF scan hoặc trong DXF khách. NGHIÊM CẤM TUYỆT ĐỐI đưa ra giả định (kể cả số tròn, "nằm giữa", "đối xứng", số đo pixel, mượn kích thước của tấm khác).
- Chỉ được tính từ chuỗi kích thước đã ghi (cộng/trừ qua các chi tiết, mục 2). Thiếu kích thước mà không tính được thì KHÔNG tự điền số: Flag 3 trong file ALL (mục 11.4).

## 1. Quy trình
1. Đọc trang CAD依頼書 (render ≤ 100 dpi): mã yêu cầu, khách, vật liệu, độ dày, X/Y phôi (X/Y chỉ để đối chiếu, mục 2).
2. Đọc toàn bộ `Quy_Tac_Laser.md`; trong `DS_Khach_Hang.md` chỉ đọc phần "Tra nhanh theo nhóm quy tắc" và dòng của đúng mã khách (tìm theo mã khách). Quy định riêng của khách thắng quy tắc chung.
3. Thư mục đơn có DXF khách (3D*.DXF...): stage về, dựng hình từ DXF TRƯỚC rồi mới đối chiếu PDF (mục 4.2).
4. Mỗi trang bản vẽ (tiết kiệm token): kiểm hướng trang trước (`pdftotext` hoặc ảnh ≤ 50 dpi); trang xoay 90° thì xoay ngay khi render, cắt vùng hình, render MỘT lần 200 dpi. Tìm ký hiệu ヨ khoanh tròn ở TỪNG trang. Xác định loại từng hình chiếu (mục 3); ghi lại mọi điểm thuộc Flag (mục 11.4) và mọi ghi chú R ở từng hình chiếu.
5. Mỗi mã: tìm đủ hình chiếu, lập các bảng ở mục 12; xác định góc uốn và độ giãn từng chỗ (mục 5). Dựng phôi trong hệ cục bộ (u dọc đường uốn, v vuông góc): biên (mục 4), uốn (5), hộp/rạch (6), lỗ (7), kegaki (9), bo góc (8, sau khi đủ biên, trước khi xoay); cuối cùng đặt hướng (mục 10).
6. Xuất file riêng + file ALL kèm Flag (mục 11), kiểm tra theo mục 12.
7. Báo cáo: danh sách file, kích thước phôi, các bảng mục 12, kích thước tính qua chuỗi (nêu vị trí nào) và kích thước thiếu, mọi chỗ lệch DXF–PDF, kegaki đã vẽ, lỗ đã bỏ, chỗ hạ R, mã thiếu bản vẽ, các Flag.
8. Đơn từ 4 chi tiết trở lên: chạy song song theo mục 13.

## 2. Nguồn số liệu và cách đọc kích thước
- Bản vẽ là chính xác. X/Y trong CAD依頼書 chỉ là khung bao tham khảo, KHÔNG phải hình dạng. Số trong ngoặc ( ) chỉ tham khảo, chỉ cần theo số không ngoặc. Có DXF khách thì hình dạng theo DXF; lệch chỉ với số trong ngoặc hoặc CAD依頼書 thì không cần hỏi.
- Chỉ thị viết tay là chỉ thị chính thức, phải theo; lỗi cần tránh là đọc nhầm chữ tay (キリ = lỗ khoan, từng đọc nhầm thành φ7). Lỗ ghi 「あける」 thì vẽ.
- Lỗ/gia công bị gạch (bút đỏ, gạch chéo): không vẽ.
- Bản vẽ lắp hàn có ghi chú tay chỉ định phần laser (「SSレーザー 9t×295×700」「曲げ(抜穴アリ)」「角穴+曲げ 抜き」 kèm hình tay): CHỈ vẽ phần được chỉ thị; không tự vẽ lỗ ren, キリ, M5/M6... của bản gốc; liệt kê lỗ đã bỏ trong báo cáo. 
- Dung sai: vẽ theo giá trị giữa khoảng dung sai, giữ chuẩn đo/đối xứng Flag 18 (mục 11.4).
- Độ chính xác: tính đủ chữ số, không làm tròn giữa chừng; kết quả giữ ≥ 2 chữ số thập phân.
- Kích thước cộng/trừ: đọc hết từng số rồi cộng, không lấy số lớn nhất.
- Chuỗi kích thước (lỗ, chi tiết hàn, mép, thanh, kegaki):
  - PHẢI tính từ chuỗi kích thước ghi trên bản vẽ, tính từ một mép chuẩn. Bản vẽ lắp (lỗ ghi kích thước tới tấm khác): quy đổi qua kích thước các tấm liên quan.
  - Kích thước thiếu: tính qua chuỗi của chi tiết lân cận (tấm khác, thanh, ống, tổng kích thước), KHÔNG giả định (kể cả số tròn, "nằm giữa", "đối xứng"); số đo pixel chỉ để kiểm tra. Không có chuỗi nào thì KHÔNG đo ảnh để vẽ: báo thiếu kích thước và Flag 3 (mục 0).
  - Bài nhiều tấm lắp ghép mà PDF chỉ có 1 bản vẽ dim chung cho tất cả: LUÔN tính mọi vị trí (lỗ, mép, kegaki) của từng tấm bằng chuỗi kích thước qua các tấm lân cận, KHÔNG được giả định. Không mượn vị trí lỗ/đường tâm của tấm khác làm kích thước.
  - Lỗ chỉ có khoảng tâm–tâm (không ghi tới đầu): tìm chuỗi qua chi tiết khác tới mép chuẩn, KHÔNG chia đều phần dư.
  - Nhóm lỗ không có kích thước theo phương vuông góc: KHÔNG suy từ hàng lỗ khác bên cạnh ; lấy tọa độ từ DXF khách (lưu ý tỉ lệ); không có thì báo thiếu kích thước và Flag 3 (mục 0), không đo ảnh để vẽ.
  - Chuỗi lệch nhau: đọc lại điểm đầu/cuối từng kích thước trước khi Flag.
  - Chuỗi cộng không bằng tổng (ví dụ 60 + 114 + 57,5 = 231,5 ≠ 229): CẤM dùng ràng buộc tổng để chốt số nào đo từ đâu. Phóng to ≥ 300 dpi đầu và cuối từng mũi tên (đường gióng dừng ở tâm lỗ, mép ô khoét hay mép tấm), đo pixel vị trí thực (px/mm từ một kích thước chắc chắn), chọn cách đọc khớp pixel (sai số ≤ 1 mm); không phân biệt được thì Flag 14 (thêm Flag 15 nếu chân dim lệch), không tự chốt.
  - Cách đọc khớp tổng chỉ cho thấy có thể đúng, không chứng minh đúng.
  - Kiểm bằng số đo ảnh ở ≥ 2 hình chiếu (sai số cho phép 0.1 mm; lệch > 0.1 mm thì xem lại chuỗi).
  - Giá trị suy từ chuỗi (vị trí đầu ống/thanh, vết kegaki, mép) phải đo pixel kiểm ở ≥ 300 dpi trên ≥ 2 hình chiếu, sai số ≤ 1 mm. Lệch > 1 mm là dấu hiệu bỏ sót ghi chú nhỏ cạnh chân dim (3.2 thành ống, 9 độ dày...): xác định kích thước tổng bắt đầu từ mặt ngoài hay mặt trong thành ống trước khi cộng/trừ. Ví dụ 26-065615: 65 + 465 − (500 + 3.2) = 26.8, không phải 30 (kích thước 500 bắt đầu từ mặt dưới thành 3.2 ở đầu ống).

## 3. Hình chiếu và mặt vẽ (BẮT BUỘC)
- Mọi hình chiếu đều được tuân theo phương pháp góc chiếu thứ ba.
- 三角法: so với hình chiếu đứng, hình TRÊN = hình bằng (nhìn từ trên); hình DƯỚI = hình nhìn từ dưới lên; hình TRÁI = chiếu trái; hình PHẢI = chiếu phải. KHÔNG mặc định hình dưới là hình bằng. Xác định lại ở TỪNG trang.
- Trước/sau: cạnh gần hình chiếu đứng là phía TRƯỚC. Hình bằng: mép dưới = trước. Hình từ dưới: mép trên = trước. Chiếu phải: mép trái = trước. Chiếu trái: mép phải = trước. Hình xoay 90° thì xoay mép theo.
- Mặt nhìn thấy: hình bằng → mặt trên; hình từ dưới → mặt dưới. Chữ L: mặt ngoài là phía góc ngoài của chỗ uốn trên hình chiếu đứng (cánh ngang trên, cánh đứng phải: mặt trên cánh ngang là mặt ngoài). Nét đứt là phía khuất (tấm B nét đứt trong hình từ dưới → B ở mặt đối diện).
- Quy mọi vị trí về 3 trục thật (x dọc cánh, y trước–sau, z cao) rồi mới chiếu sang mặt vẽ; không lấy trên/dưới của hình làm trước/sau.
- Đối chiếu chéo: mỗi đặc điểm bất đối xứng (cánh ngắn sát mép nào, phía mở rộng, vát C ở mép nào, phía nhô của tấm hàn, lỗ tính từ mép nào) phải suy từ ≥ 2 hình chiếu độc lập cùng kết luận. Mâu thuẫn thì dừng, đọc lại loại hình chiếu, chưa vẽ.
- Chọn mặt vẽ, theo thứ tự ưu tiên:
  1. Có kegaki: mặt kegaki (mục 9).
  2. Bản vẽ đánh dấu 表: vẽ mặt 表 theo hình chiếu đứng.
  3. Chi tiết uốn: mặt ngoài của phần uốn; hình chiếu đứng cho thấy mặt trong thì lật trái–phải (không đổi chiều dọc).
  4. Uốn ngược chiều (Z/Ω/mũ, 上曲げ + 下曲げ) không có mặt ngoài rõ, không có 表: vẽ theo hình chiếu chính (hình chiếu đứng) đúng như bản vẽ, không lật; trùng mặt với 展開図 của khách nếu có.
  5. Phẳng không uốn: giữ hướng hình chiếu đứng. Tấm tách từ bản vẽ lắp mà hình chiếu đứng là mặt trong thì lật trái–phải để ra mặt ngoài.
  - Không chắc mặt nào là mặt ngoài: vẫn vẽ theo mặt đã chọn và Flag 11 (ghi mặt đã chọn).
- Cặp gương (R/L, 本図/対称, A-1/A-2, hai trang cùng loại chi tiết): hình dạng và kegaki bản kia là ảnh gương; chỗ dễ lỗi nhất, kiểm kỹ hơn. Nhãn ở hình 3D → trái/phải ở hình chiếu đứng → cùng trái/phải ở hình từ dưới (chỉ đảo trước–sau). Vẽ mặt trên (mặt kegaki) từ hình từ dưới thì lật trước–sau. Ví dụ 26-064157 (A-1, trái, đế 100 x 50): mặt trên lỗ φ16 (16; 15), kegaki (70; 35), y tính từ mép trước; 064158 (A-2) là ảnh gương. Lỗi đã gặp: coi hình dưới là hình bằng nên ra ảnh gương (26-062206: cánh ngắn 35 phải sát mép trước, mở rộng 50 phía sau; 064157/158 bị đổi chỗ).
  - Mỗi tấm của cặp gương/đối xứng phải tự đọc và đo riêng điểm đầu–cuối từng kích thước và vị trí lỗ; KHÔNG chép toạ độ từ tấm kia. Chuỗi hai tấm có thể khác nhau (521102-23: 065503 lỗ X = 57,5 / 171,5, ô khoét 60 → 169; 065504 lỗ X = 60 / 174, ô khoét 62,5 → 171,5). Chỉ coi là ảnh gương khi đo từng tấm cho cùng kết quả.
- Chỉ xoay 90°/180° chọn hướng (mục 10) SAU KHI mặt đã đúng; không dùng xoay để "sửa" khi chưa chắc mặt. Lật chỉ khi quy tắc mặt yêu cầu.

## 4. Dựng biên dạng
### 4.1 Từ hình chiếu
- Dựng từ đường viền thật trên các hình chiếu. Chỉ vẽ chữ nhật khi ≥ 2 hình chiếu đều cho biên chữ nhật (không xiên, vát, bậc); chưa kiểm được thì đọc thêm, không mặc định.
- Tìm đủ hình chiếu của từng mã (đứng, bằng, cạnh, 3D), kể cả tấm hàn nhỏ (tab, gân, gusset) lẫn trong bản vẽ lắp; tấm hàn dựng đứng thường lộ biên rõ nhất ở hình chiếu cạnh.
- Bảng gán kích thước: MỌI con số gần chi tiết (kể cả số nhỏ 10, 25, 9) kèm hướng đo và đặc điểm nó xác định; không số nào chưa gán. Cùng một số có thể ở 2 hướng với 2 nghĩa (26-062153: 10 ngang = bề rộng đỉnh, 10 dọc cạnh chân = đoạn thẳng ở đáy). Số nhỏ lẫn trong chuỗi của tấm khác vẫn phải tìm ra đặc điểm của nó.
- Mỗi đoạn biên phải ứng với một số hoặc nét trên bản vẽ/DXF; không tự thêm đoạn "cho đối xứng".
- Tấm tách từ hộp/cụm hàn (đáy, nắp, vách ngăn): dò biên theo TỪNG ĐOẠN mép trên hình bằng/hình đứng (phóng to chỗ tiếp giáp cánh hồi, vách, khe hở), quy mỗi đoạn về mặt tiếp xúc thật (mặt trong vách hay mặt ngoài); không lấy kích thước trong hay hình bao làm khung chữ nhật. Dấu hiệu: mép tấm là nét liền chạy giữa các cánh hồi và thẳng hàng với mép ngoài thì mép đó kéo ra tới mặt ngoài. Ví dụ 26-064175 (đơn 521029-08, SUS2B t1.5, hộp U 11.5+87+107+87+11.5 cao 201.5, tấm đáy rời nằm trong hộp): phần chính 104 x 84 (mặt trong tấm lưng tới mặt trong cánh hồi), ở khoảng hở 84 giữa 2 cánh hồi mép trước kéo ra 1.5 bằng mặt ngoài; biên (0,0) (104,0) (104,84) (94,84) (94,85.5) (10,85.5) (10,84) (0,84), R0.5 ở 6 góc lồi, 2 góc lõm không bo. Lần đầu vẽ chữ nhật 104 x 84 theo 2 kích thước trong là sai.
- Đường xiên bên trong biên hình chiếu cạnh (đổi dần khoảng cách tới mép) là biên thon của tấm, không phải đường phụ: đọc 2 bề rộng (đáy, đỉnh), chiều cao, đoạn thẳng ở đáy, rồi kiểm bằng hình chiếu bằng.
- Đặt phôi: ghi tọa độ đỉnh trên hình chiếu (x ngang, z cao), rồi XOAY 90° bằng code (không lật, không gương) đưa cạnh thẳng dài nhất lên Ox; không vẽ tự do rồi tự chọn phía. Cạnh thẳng bên trái + đáy rộng ở dưới thì xoay ngược chiều kim đồng hồ: cạnh thẳng nằm trên Ox, đầu hẹp ở x = 0.
- Người dùng báo "vẫn thiếu/sai" sau một lần sửa: đối chiếu bản đã giao mới nhất với bảng gán kích thước; mọi số đều khớp thì KHÔNG đoán thêm, hỏi vị trí cụ thể hoặc xin file tham khảo (người dùng có thể đang mở bản cũ/.bak).

### 4.2 Từ DXF khách
- Có DXF thì LẤY DXF LÀM NỀN rồi chỉnh theo chỉ thị riêng (DXF không phải lúc nào cũng đúng). Dựng từ DXF TRƯỚC rồi mới so PDF.
- Trích hình: layer 0, đưa về tỉ lệ 1:1 (DXF vẽ theo tỉ lệ khung tên 1:2, 1:3... thì nhân hệ số), nối LINE/ARC thành vòng kín; bỏ hình chiếu khác, kích thước, đường tâm. Hình có thể nằm trong BLOCK (INSERT JZB_xxxx): đọc cả nội dung block, không chỉ modelspace. Ví dụ 100-09.dxf (26-063640/641): hình trong JZB_0003/0004/0005; cánh rộng 61 kéo tới 29 tính từ mép tự do (cung R3 tâm (58; 26)), không dừng ở đường uốn 27.34.
- DXF chỉ có hình chiếu (không có phôi) vẫn phải trích số liệu (chiều dài mép tự do, chân cánh, tọa độ lỗ) từ đó.
- Áp chỉ thị PDF lên nền DXF: ghi chú laser (062682 'laser: φ11.6' → vẽ φ11.6 thay φ12 H7 của DXF), kích thước lỗ PDF khác DXF (062725: PDF 3xφ4, DXF φ4.5 → theo PDF), độ giãn và chiều dài tay viết. Mọi chỗ lệch DXF phải có Flag (mục 11.4).
- Phôi tham khảo (展開図 参考) của khách: hiệu chỉnh chiều dài theo độ giãn tay viết / 旭金属の展開: giữ vị trí tính từ mép tự do của cánh, phần bên kia đường uốn tính từ mép đối diện (dịch cả phần đó), vẽ lại 2 đường DASHED.
- Bản vẽ phẳng có cánh uốn chỉ hiện ở hình chiếu cạnh : mở cánh ra; đầu tự do cánh = đường uốn phía cánh - (ngoài cánh - giãn). Slit chân cánh của khách nằm đúng vùng uốn là dấu hiệu đúng.
- Lỗ khoét côn/khoét bậc và ký hiệu ren trong DXF chỉ là ký hiệu: không vẽ, chỉ vẽ lỗ mồi.
- Góc lồi 90° sắc trong phôi DXF khách vẫn bo theo bảng laser (mục 8).
- Phôi chéo không có cạnh thẳng nào áp trục: chỉ xoay bội 90° để cạnh dài nằm theo X.
- Đối với trường hợp đã có bản vẽ trải phôi thì không cần rạch (Trừ khi có yêu cầu cụ thể trên PDF).

### 4.3 Suy phôi từ hình chiếu khi không có DXF phẳng
- Không thu hẹp bề rộng ngay sau đường uốn: giữ bề rộng tới khi hình chiếu bằng thực sự thu lại. Cổ hẹp chỉ là đoạn ngắn trong vùng uốn kế tiếp.
- Chỗ nối vách–tấm (cổ hẹp giữa hai tấm uốn) có khe thoát bo R1 ở các bậc, đầu vách cắt ngay trong vùng uốn ; không vẽ góc vuông đơn giản.
- Đường uốn chạy hết bề rộng phần phẳng ở cả hai bên.
- Độ tin cậy thấp: đưa thẻ xác nhận hình dạng cho người dùng trước khi giao, ghi rõ phần suy từ hình chiếu (bề rộng chân/cổ, vị trí đầu vách, khe thoát); số không có trên bản vẽ thì báo thiếu và Flag 3 (mục 0).
- Phôi uốn nhiều mặt dựng theo 3 bước: (1) bóc tách từng mặt thành hình riêng theo kích thước ngoài; (2) thêm giãn: ở mỗi mối nối, mặt sau chồng lên mặt trước một đoạn bằng giãn; (3) ghép lại, trim nét thừa bên trong cho biên liền mạch, đổi nét uốn thành DASHED.
- Ở bước (1), biên dạng ngoài của từng mặt phải dò đúng từng đoạn nét trên hình chiếu và chân dim của chính mặt đó, kể cả phần không nối với vách. Không kéo mép theo kích thước ngoài của phần có vách, không tự áp một độ lùi cố định.

## 5. Uốn: độ giãn và đường uốn
- Phôi = kích thước ngoài + kích thước ngoài - độ giãn. Độ giãn luôn dương: bản vẽ ghi "-0.48" thì hiểu là 0.48, vẫn trừ. Sau khi dựng, đối chiếu tổng dài/rộng với công thức.
- Nguồn độ giãn, theo thứ tự:
  1. Số ghi tay trên bản vẽ (ví dụ "37+60-5.2=91.8"); khác bảng vẫn dùng số tay và Flag 10.
  2. Bảng `Bang_Do_Gian_Asahi.xlsx` (khách 646 dùng `Bang_Do_Gian_AICOKU ALPHA.xlsx`) CHỈ cho chỗ uốn 90°.
  3. Góc uốn khác 90° (kể cả > 90°, ví dụ 110°): KHÔNG dùng bảng, không lấy số 90°; độ giãn do người dùng cung cấp, chưa có thì hỏi.
- Tra bảng: xác định khoảng chiều dài uốn của mã (hàng 曲げ長さ) trước, rồi mới đọc giãn ở cột tương ứng; ô độ dày không gộp có thể phủ nhiều cột.
- Kích thước ở chỗ uốn: phóng to đầu đường gióng để xác định đi qua góc trong hay ngoài. Kích thước trong phải đổi sang ngoài trước khi tính phôi (ngoài = trong + t/tan(α/2) mỗi cánh, α là góc trong giữa hai cánh); không xác định được thì Flag 7.
- Xác định góc uốn TỪNG chỗ từ hình chiếu cạnh (ví dụ ghi 70° lệch = uốn 110°). Góc ghi trên hình chưa chắc là góc uốn: góc giữa hai mặt tấm ở hình cạnh/mặt cắt là góc uốn; góc giữa hai cạnh biên của cánh ở hình bằng/hình nhìn thẳng cánh là góc biên dạng (ví dụ đầu cánh vát), không làm đổi góc uốn. Ví dụ 26-063561/62 (天板, SUS304 2B t1.5): 4 ghi chú 135° là góc đầu cánh vát, uốn 90°, giãn 2.64. Chưa chắc thì hỏi, không tự kết luận góc uốn khác 90°.
- Chỗ uốn góc ≤ 85° (cánh nghiêng; Asahi và AICOKU ALPHA): không dùng kích thước danh nghĩa (ví dụ 80/150) làm kích thước ngoài.
  - R trong: t < 6 → 0.6; t ≥ 6 → 6. Offset ra đúng t được R ngoài (t3.2: 3.8; t ≥ 6: 6 + t), đo kích thước ngoài hiệu chỉnh mỗi cánh từ hình học thực (cánh nghiêng đo dọc mặt ngoài). Giá trị hiệu chỉnh thay đổi theo bản vẽ, không phải hằng số.
  - Phôi = ngoài hiệu chỉnh + ngoài hiệu chỉnh - giãn (giãn do người dùng cung cấp theo từng yêu cầu, không tự tra theo góc). Chưa có giãn hoặc không dựng được hiệu chỉnh thì hỏi và Flag 16.
  - Góc > 90°: dùng kích thước danh nghĩa (kích thước ngoài + kích thước ngoài - độ giãn).
- Đường uốn: mỗi chỗ uốn 2 LINE DASHED (không vẽ 1 đường giữa). Đường 1 cách mép phôi bên này = ngoài cánh bên này; đường 2 cách mép bên kia = ngoài cánh bên kia; khoảng giữa = giãn. Ví dụ L 37 + 60, giãn 5.2, phôi 91.8: đường tại 37 và 31.8. Nhiều chỗ uốn (chữ U...): mỗi cặp đặt tại (vị trí giữa ± giãn/2), vị trí giữa = ngoài cánh - giãn/2 tính từ mép xa.
- Nét đứt ở hình bằng (平面図) của chi tiết uốn cách mép ngoài đúng t (KHÔNG phải giãn/2); kích thước ghi từ nét đứt tính từ đúng đường đó. Quy đổi điểm trên phần phẳng: u (trên phôi, từ mép tự do cánh đầu) = y (trên hình bằng, từ mặt ngoài cánh đầu) + (ngoài cánh - giãn). Ví dụ 26-060232 (t3.2, mũ 13 + 102 + 13, giãn 5.5): u = y + 7.5; nét đứt cánh xa ở y = 98.8. Lỗ trên cánh vẫn đo từ mép tự do cánh.

## 6. Hộp, vách và đường rạch góc (Green 62 = 3)
- Hộp mở 4 cánh: TRƯỚC TIÊN phóng to mỗi đỉnh hộp ở mọi hình chiếu và hình 3D (hoặc DXF khách) để kiểm relief góc của khách và đầu cánh vát (2 ngoại lệ cuối mục). Không có thì phôi chữ thập, khoét 4 góc. a = ngoài cánh - giãn, t = độ dày. Khoét theo X = a (2 cánh theo phương Oy giữ đủ bề rộng, không lùi); khoét theo Y = a + t (2 cánh ở hai đầu theo Ox lùi t mỗi đầu). Góc lồi bo theo Laser R, góc lõm không bo; đường uốn DASHED chạy trong phạm vi mỗi cánh.
- Đường rạch ở mỗi góc khoét, 3 entity vẽ từ ngoài vào: LINE (điểm bắt đầu → tiếp điểm), ARC R0.5, LINE (tiếp điểm → cuối). Điểm bắt đầu nằm trong phần khoét (ngoài phôi), cách mỗi mép khoét một khoảng = Piercing ngoài (`Quy_Tac_Laser.md` mục 2; thép ≤ 3.2 → 3, thép 4–9 → 6...); đi chéo 45° tới góc, bo R0.5, rạch thẳng dọc mép khoét theo Ox (mép cánh đã lùi) vào phía đáy, sâu t + 0.2 tính từ góc khoét. Ví dụ 26-057140 (SPHC-P t1.6, giãn 2.6, cánh 121.6, phôi 491.2 x 441.2): khoét 119.0 theo X, 120.6 theo Y; góc dưới trái: (116; 117.6) → (118.854; 120.454), ARC tâm (119.207; 120.1) R0.5 từ 90° đến 135°, (119.207; 120.6) → (120.8; 120.6).
- Vách bên (2 vách đối nhau uốn từ hai mép tấm, mỗi vách ngắn hơn tấm): rạch ở 4 góc nối vách–tấm, cùng cấu trúc; LINE cuối vào tấm sâu t + 0.2 theo phương ngang của mép vách. Ví dụ 26-060234 (t3.2): góc (137.7; 37.7): LINE (140.7; 34.7) → (137.846; 37.554), ARC tâm (137.493; 37.2) R0.5 từ 45° đến 90°, LINE (137.493; 37.7) → (134.3; 37.7).
- Vách đơn (1 vách uốn từ một mép, ngắn hơn tấm): cũng PHẢI rạch ở 2 góc lõm, LINE cuối dọc mép bên của vách (không nhất thiết theo Ox). Ví dụ 26-060393 (SUS t2, vách 630 trên tấm 700, cách 2 đầu 35): góc (35; 60): LINE (29; 66) → (34.854; 60.146), ARC tâm (34.5; 59.793) R0.5 từ 0° đến 45°, LINE (35; 59.793) → (35; 57.8); góc (665; 60) đối xứng gương. Mọi góc lõm vách–tấm đều phải kiểm theo điều kiện rạch bên dưới.
- Điều kiện rạch tại góc lõm giữa mép khe/khoét và mép bên của cánh uốn. Đường uốn phía cánh là đường DASHED gần mép tự do của cánh hơn; d = khoảng từ đường này tới mép khe, đo về phía tấm chính.
  - Mép khe nằm ngoài đường uốn phía cánh (về phía mép tự do) hoặc trùng đường đó: rạch.
  - Mép khe nằm trong đường uốn phía cánh với d < t: rạch. d ≥ t: không rạch.
  - Khi rạch: LINE đầu và ARC R0.5 như các ví dụ trên; LINE cuối chạy dọc mép bên khe tới điểm cách đường uốn phía cánh t + 0.2 về phía tấm chính. Điểm cuối tính từ đường uốn, không tính từ góc khe (mép khe nằm ngoài thì rạch dài thêm đúng khoảng từ mép khe tới đường uốn).
  - Đường uốn DASHED ở cánh có khe: mép khe nằm ngoài đường uốn phía cánh thì 2 đường chạy hết bề rộng, kể cả đoạn ngang khe; mép khe trùng hoặc nằm trong đường đó thì cả 2 đường ngắt trong phạm vi bề rộng khe, chỉ vẽ trên phần cánh còn lại.
- Ngoại lệ: hộp 4 cánh uốn 90° có đầu cánh vát biên dạng 135° (bản đúng 26-063561, đơn 521027-02): KHÔNG khoét kiểu hộp thường, KHÔNG rạch Green. Phôi = tấm giữa + 4 cánh hình thang, góc khoét vuông vào trong; 135° là góc giữa mép tự do và đầu cánh vát, không phải góc uốn; giãn tra bảng 90° (t1.5 SUS: 2.64).
  - Đường uốn tại a và tại ngoài cánh tính từ mép phôi (cánh 30: 27.36 và 30); DASHED chạy từ a + 5 đến (cạnh - a - 5).
  - Khoét vuông, góc lõm sắc tại (a + 5; a + 5) = (32.36; 32.36); không giữ góc tấm, không bo.
  - Đầu cánh: đoạn 45° từ mép tự do (cách mép bên a + 29.268 = 56.628) vào tới khoảng a - 2.36 (= 25) từ mép phôi, bo góc lồi chỗ chuyển hướng (mặc định R0.5; mẫu này cạnh kề chỉ 0.008 nên hạ R0.3), rồi thẳng theo x (hoặc y) = a + 5 tới góc khoét. Mép tự do ngắn hơn tấm 2 x 29.268 (1203 → 1144.46), khớp DXF khách. Góc 135° hai đầu mép tự do không bo.
  - Góc dưới trái 26-063561 (1257.72 x 907.72): LINE (0; 56.628) → (24.488; 32.14), ARC tâm (24.7; 32.352) R0.3 từ 225° đến 0°, LINE (25; 32.352) → (25; 32.36) → (32.36; 32.36) → (32.36; 25) → (32.352; 25), ARC tâm (32.352; 24.7) R0.3 từ 90° đến 225°, LINE (32.14; 24.488) → (56.628; 0). 063562 (957.72 x 657.72) giống ở các góc.
  - Lỗi đã gặp: khoét hộp thường + rạch Green, hoặc khoét 5 x 5 giữ góc bo R0.5 và đầu cánh chéo thẳng tới chân cánh: đều sai.
- Ngoại lệ: relief góc của khách (bản đúng 26-063377, khách 646, đơn 521027-11, SPCC t1.2, cánh 73, giãn 2.14, a = 70.86): mỗi đỉnh hộp bị cắt khối vuông s (ghi "3.5 外寸" ở hình bằng, hình cạnh, hình từ dưới; hình 3D thấy lỗ ở chỗ giao 3 mặt), cắt cả mặt chính và 2 cánh; góc lõm có ghi chú R (4-R1 ở mặt chính, 2×2-R1 ở cánh). KHÔNG khoét kiểu hộp thường, KHÔNG rạch Green.
  - Quy đổi s: trên cánh cách mép tự do (ngoài cánh - s) = 73 - 3.5 = 69.5; trên mặt chính cách mép phôi a + s = 74.36. Mỗi góc khoét vuông từ 69.5 đến 74.36 theo cả X và Y, nối với phần khoét ngoài các cánh.
  - Cánh lùi: cánh lọt giữa 2 cánh kia (ghi 内寸, ví dụ 277.6 = 280 - 2t) có mép ở a + t = 72.06; cánh che đầu cánh kia giữ mép ở a = 70.86. Xác định cánh nào lùi theo hình chiếu, không chép theo 26-057140.
  - 3 góc lõm bo theo ghi chú (R1), 2 góc lồi bo R0.5 laser. Đường uốn DASHED chỉ chạy giữa 2 mép relief (từ a + s đến cạnh - a - s).
  - Góc dưới trái (trước xoay, phôi 421.72 x 206.72, cánh dưới lùi): (72.06; 0) → (72.06; 69.5) → (74.36; 69.5) → (74.36; 74.36) → (69.5; 74.36) → (69.5; 70.86) → (0; 70.86); R0.5 tại (72.06; 69.5) và (69.5; 70.86), R1 tại 3 góc còn lại.
  - Ghi chú "A部 球面状にR取り(R1) 手仕上げ" là hoàn thiện tay sau uốn, không vẽ. Lỗi đã gặp (29/10/2026): coi "3.5 外寸" là tiếp tuyến chỗ uốn, khoét hộp thường + rạch Green nên sai vị trí giao 4 cánh với mặt chính.

## 7. Lỗ
- Vị trí theo chuỗi kích thước (mục 2). Lỗ trên cánh: giữ khoảng cách đo từ mép xa (mép tự do) của cánh. Lỗ trên đáy chữ U: giữ khoảng cách so với tâm đáy.
- Gán lỗ đúng tấm trong bản vẽ lắp. Trước khi vẽ, lập bảng "lỗ → tấm" cho cả bản vẽ; mỗi mã chỉ vẽ lỗ của đúng tấm.
  - Mỗi ghi chú lỗ (n-Mx, n-φx) xác định theo ĐẦU MŨI TÊN của đường dẫn, đối chiếu ≥ 2 hình chiếu (cạnh + bằng); không gán chỉ vì lỗ nằm trong khung hình đang xem.
  - Hình chiếu cạnh nhìn từ đầu tự do ống/thanh chỉ thấy mặt ngoài tấm nắp ở đầu đó (tấm đáy bị che): lỗ trong vùng chân ống thuộc tấm nắp (E), lỗ ngoài vùng chân ống thuộc tấm đáy (A).
  - Hình thoi đặc là dấu hàn, không phải lỗ. Kích thước cùng hàng với lỗ chỉ dùng cho tấm chứa lỗ đó.
  - Sau khi vẽ, đếm lỗ từng tấm, đối chiếu mọi ghi chú (không tấm nào thiếu/thừa, không lỗ nào ở 2 tấm).
- Lỗ taro: vẽ lỗ mồi theo `Quy_Tac_Lo_Moi.md` (M6 → φ5, M8 → φ6.8), TRỪ KHI bản vẽ có ghi chú tay về lỗ mồi (ví dụ 「下穴φ2.5 レーザー → 穴あけ → タップ」 khoanh quanh 4-M5: laser chỉ cắt φ2.5, không phải φ4.2): ghi chú tay thắng bảng. Trước khi vẽ, quét mọi ghi chú tay cạnh từng nhóm lỗ n-Mx/n-φ và ghi vào bảng 'lỗ → tấm' (cột φ vẽ + nguồn: bảng / ghi chú tay).
- Lỗ nhỏ: so đường kính (kể cả lỗ mồi) với "Lỗ nhỏ nhất" trong `Quy_Tac_Laser.md` mục 2 theo vật liệu và độ dày. Nhỏ hơn, hoặc lỗ có ghi chú tay ピアス khoanh riêng quanh lỗ đó, thì vẽ POINT (piercing) tại tâm lỗ, layer 0, thay CIRCLE. Tem/chữ PIERCING đầu trang KHÔNG áp cho mọi lỗ ren: lỗ ren có lỗ mồi ≥ lỗ nhỏ nhất vẫn vẽ CIRCLE lỗ mồi. Ví dụ 26-059668 (t12, 6-M6 PIERCING, mồi φ5 < 6): 6 POINT. Ví dụ 521030-12 (tem PIERCING, ghi tay chỉ khoanh M12 t16): M12 POINT; 4-M8 t12 mồi φ6.8 (≥ 6) và M6 t6 mồi φ5 (≥ 3) vẽ CIRCLE (lần đầu vẽ POINT cho mọi lỗ ren là sai). Khách có quy định riêng trong `DS_Khach_Hang.md` (ví dụ 875: lỗ nhỏ hơn độ dày làm lỗ trắng) thì theo khách; chưa rõ thì hỏi.
- Màu POINT: mặc định trắng; có dấu THROUGH HOLE/đột xuyên hoặc khách quy định piercing là lỗ xuyên (`DS_Khach_Hang.md`) thì POINT Xanh lá (`62 = 3` ngay sau layer `8`).

## 8. Góc: Laser R, vát C, đối chiếu R
- Bản vẽ ghi R thì theo bản vẽ; khách có quy định riêng (không bo, R3...) thì theo khách; còn lại PHẢI bo góc lồi ≤ 90° theo bảng `Quy_Tac_Laser.md` mục 2:
  - Thép (SS: SPHC, SPCC, SS400...): ≤ 5 → R0.5; 6–9 → R2; 10–16 → không bo; ≥ 19 → R3 cả góc trong và ngoài.
  - Inox/khác: ≤ 6 → R0.5; ≥ 7 → không bo. Nhôm: ≤ 6 → R0.5: ≥ 7 → không bo. Đồng/đồng thau: ≤ 5 → R0.5.
- R0.5 là mặc định, không tự thay. Khi góc lồi quá nhỏ (cạnh kề quá ngắn, cung R0.5 không có chỗ tiếp tuyến) Flag 19 (mục 11.4).
- Góc nhìn thấy bo cong trên hình nhưng không có số R: KHÔNG coi là góc nhọn rồi bo R0.5 như thường, KHÔNG tự điền R theo ghi chú lân cận. Zoom ≥ 200 dpi từng góc; góc bo cong mà thiếu số thì Flag 3 (nêu vị trí góc, 'bo cong, không ghi số R'), vẫn vẽ tạm R0.5 để file không hở và ghi rõ 'tạm' trong Flag; chờ người dùng cung cấp R.
- Góc đã vát C (135°) và góc lõm không bo (trừ thép ≥ 19t). Vát C vẽ thành đoạn chéo.
- Vẽ ARC tiếp tuyến 2 cạnh, cắt ngắn 2 cạnh tại tiếp điểm. Kích thước bản vẽ là kích thước chưa bo.
- Ghi chú "n-Rx" có thể ở NHIỀU hình chiếu, mỗi nơi là n góc riêng. Bắt buộc lập bảng (ghi chú | hình | số góc), cộng mọi hình chiếu, đối chiếu với số góc lồi thực tế. Góc có ghi chú bo theo bản vẽ; chỉ góc chưa có ghi chú mới áp bảng laser. Góc cùng loại với góc đã có R mà chưa gán thì tìm lại ghi chú ở hình khác trước khi áp R laser. "(n-Rx)" trong ngoặc ở hình mặt cắt thường là R uốn, không phải R góc phôi.
- Đối chiếu bán kính (BẮT BUỘC mọi mã, kể cả hình lấy từ DXF khách; khung bao đúng không chứng minh R đúng, phải đối chiếu từng cung.
  - Bảng: mỗi ghi chú R trên MỌI hình chiếu (R5, R12, n-Rx, kể cả có chữ như "R12 (リブ)") | số lần xuất hiện | cung đã gán (tâm, bán kính, góc đầu–cuối) | trạng thái. Không ghi chú nào chưa gán; không cung nào thiếu ghi chú (trừ R laser và R uốn). Ghi chú xuất hiện nhiều lần là nhiều vị trí.
  - Rib/gân hàn lên tấm chính: KHÔNG mặc định cạnh tiếp xúc đi theo bề mặt tấm chính (kể cả R trong chỗ uốn); biên rib có thể có cung tránh (relief). DXF khách có cung đúng giá trị ghi chú thì dùng cung đó.

## 9. Kegaki (vạch dấu ケガキ: LINE Đỏ 62 = 1, layer 0; `Quy_Tac_Laser.md` mục 5)
- Vẽ khi: có chỉ thị KEGAKI/ケガキ, có ký hiệu ヨ khoanh tròn (ký hiệu hàn nội bộ, thường cạnh mã vạch), hoặc khách yêu cầu vạch vị trí hàn (ví dụ khách 851,676). Tìm ヨ kỹ cạnh mã vạch và khung tên TỪNG trang; có ヨ thì mọi tấm nhận hàn đều có kegaki.
- Vẽ vết (footprint) của tấm hàn lên tấm nhận (tấm có mặt bị tấm khác hàn lên), xác định quan hệ lắp ráp từ các hình chiếu. Tấm chỉ hàn bằng cạnh vào tấm khác thì không có kegaki.
- CHỈ kegaki phần tiếp xúc thật giữa hai chi tiết. Không chắc phần nào tiếp xúc thì xem thêm hình 3D (đâu chồng lên đâu, mặt nào áp mặt nào) trước khi quyết định vẽ hay bỏ. Dấu hiệu có vùng chồng: một chi tiết ghi cùng lúc tổng dài và phần nhô ra (hiệu số là phần chồng dưới chi tiết khác).
- Chi tiết hàn chỉ được bỏ kegaki khi MỌI cạnh của vết (footprint) đều trùng mép ngoài tấm nhận (định vị được theo mép). Còn bất kỳ cạnh vết nào nằm bên trong tấm (đầu mút ống/thanh, mặt xa của ống/thanh, mép tấm hàn) thì VẼ các cạnh đó; cạnh trùng mép tấm thì bỏ. Ống/thanh vuông không cắt laser vẫn tạo vết kegaki trên tấm laser nhận hàn. Ví dụ 26-065615 (khách 851): ống 30 sát mép đầu trái tấm nhưng đầu ống nằm cách mép trên tấm 26.8, phải vẽ 2 LINE (x = 30 và y = 38.2); lần đầu bỏ kegaki là sai.
- Tấm hàn chạm mặt nhận chỉ bằng một cạnh (tấm ngang đặt lên mặt nghiêng, tựa trên tấm gia cường): vẽ ĐÚNG đường chạm thật, không suy vết từ độ dày tấm. Tấm chỉ chạm tại một cạnh thì chỉ 1 LINE (x từ đầu tới cuối tấm); tấm gia cường/gân hàn bằng cạnh dài thì khung kín bề dày x chiều dài tiếp xúc.
- Chỉ vẽ đoạn nằm trong phôi: đoạn trùng mép phôi hoặc trùng đường uốn DASHED thì bỏ.
- Ống tròn hàn lên tấm: vết phủ đủ đường kính (2 đường ở 2 mép ống), không chỉ đường tâm.
- Mặt vẽ là mặt kegaki (ưu tiên hơn quy tắc mặt ngoài/hình chiếu đứng); hình chiếu đứng cho thấy mặt đối diện thì lật trái–phải (không đổi chiều dọc). 本図/対称: hình dạng và kegaki của 対称 là ảnh gương của 本図.

## 10. Đặt hình trên phôi
- Góc dưới trái tại (0,0), cạnh dài hơn theo X. Chỉ xoay bội 90°, không lật. Chọn hướng có cạnh thẳng của biên nằm trên cả Ox và Oy (tiếp xúc bằng cạnh, không chỉ một đỉnh). Ví dụ 26-057025: khối chữ nhật sát góc dưới trái, cánh nghiêng hướng lên phải. Hai hướng (xoay 180°) đều có cạnh áp trục thì chọn hướng có cạnh áp trục dài hơn.
- Phôi dài hẹp (Oy ≤ 100 và Ox ≥ 1000): thêm POINT trên mép trên (y = Oy lớn nhất), mỗi điểm 1 TEXT cao 10 đặt đúng tại điểm (layer 0, style Standard). Theo chiều dài L (Ox): 1000 ≤ L ≤ 1500 → 1 J + 1 LJ; 1500 < L ≤ 2000 → 2 J + 1 LJ; 2000 < L ≤ 2500 → 3 J + 1 LJ.
  - J đầu cách đầu mép thẳng trên 30, LJ cách cuối mép thẳng trên 30: x_đầu và x_cuối là hai đầu đoạn thẳng của mép trên, bỏ đoạn vát C và bo R ở đầu; mép trên không vát thì x_đầu = 0, x_cuối = L. N = số J + 1 điểm chia đều, bước (x_cuối - x_đầu - 60)/(N - 1). Ví dụ 2J + LJ: x_đầu + 30, giữa, x_cuối - 30.
    - Phôi có J/LJ: xoay 180° để mép thẳng nằm trên, phần tai/cánh nhô ra nằm dưới ; vẫn là bội 90°, không lật.

## 11. File đầu ra
### 11.1 File riêng
- Tên "26-" + mã yêu cầu (6 số dưới mã vạch), ví dụ 26-059090.dxf; lưu vào thư mục chứa PDF yêu cầu. Người dùng chỉ yêu cầu file ALL thì không tạo file riêng.

### 11.2 Template.dxf (BẮT BUỘC)
- Đọc lại `Template.dxf` bản mới nhất mỗi lần (người dùng có thể cập nhật); người dùng đính kèm thì dùng bản đính kèm.
- File ra giống hệt mẫu (AC1024, ANSI_932, CLASSES, TABLES, BLOCKS, OBJECTS..., layer 0, Defpoints, DIM nếu có), CHỈ khác phần hình vẽ; không tự dựng header/tables.
1. Đọc bytes, decode `cp932`, tách `\r\n` thành cặp (mã nhóm, giá trị).
2. Xóa entity giữa `2/ENTITIES` và `0/ENDSEC` của mẫu, chèn entity mới. Ghép đúng: `L[:i+1] + entity + L[j-1:]` (i = chỉ số `ENTITIES`, j = chỉ số `ENDSEC` sau đó). Ghép sai `L[:i+1] + entity + L[j:]` làm mất mã `  0` trước `ENDSEC`, CAD báo "Press ENTER to continue" và không mở được (lỗi 13/10/2026, đơn 521013-04).
3. Font: mọi TEXT (chữ mã, J/LJ, Flag) dùng Arial. Trong bảng STYLE, bản ghi `2 Standard` đổi giá trị mã `3` từ `txt` thành `arial.ttf`, giữ các dòng khác, không thêm style mới. Áp cho mọi file (riêng và ALL).
4. Entity: LINE, CIRCLE, ARC, POINT, TEXT; layer `0`, owner `330 = 6F`, subclass `AcDbEntity` + `AcDbLine`/`AcDbCircle`/`AcDbCircle`+`AcDbArc` (góc 50/51, độ, ngược chiều kim đồng hồ)/`AcDbPoint` (chỉ 10/20/30; POINT xanh thêm `62 = 3` sau `8`)/`AcDbText` như mẫu. Đường uốn: LINE thêm `6 = DASHED`. Đường rạch (LINE/ARC): `62 = 3` ngay sau layer `8`. Kegaki (LINE): `62 = 1` ngay sau `8`. Flag: mục 11.4.
5. Handle mới bắt đầu từ `$HANDSEED` của mẫu hiện tại (bản mới nhất 25D hex, là handle kế tiếp chưa dùng), tăng dần; sau đó cập nhật `$HANDSEED` = handle kế tiếp.
6. Cập nhật `$EXTMAX` (10/20 = khung bao X/Y); VPORT `*Active`: 12/22 = tâm hình, 40 = chiều cao view (~1.1 × kích thước). EXTMIN/EXTMAX gốc của mẫu là ±1e20 nên chỉ ghi đè EXTMAX (10/20); khác mẫu ở các dòng này là bình thường.
7. Ghi lại với `\r\n`, mã hóa `cp932`.
8. Kiểm tra bắt buộc trước khi giao: (a) đọc từng cặp 2 dòng, dòng mã luôn là số nguyên; (b) từ `0/ENDSEC` cuối ENTITIES đến hết file trùng mẫu từng dòng (`mẫu[j-1:] == ra[l-1:]`); (c) ngoài ENTITIES chỉ khác mẫu ở EXTMAX, HANDSEED, VPORT và mã `3` của Standard; (d) không có số dạng `1e-05`, `nan`; (e) không tin báo "written": sau khi ghi vào thư mục người dùng phải liệt kê thư mục xác nhận file có mặt và đúng dung lượng, lệch thì SendUserFile lấy file_uuid rồi commit lại bằng fileUuid. Ghi đè file đã commit trong cùng phiên: commit từ stagedPath MỚI (thư mục khác), vì cùng đường dẫn có thể giữ nội dung cũ (đã gặp ở 521023-07, 521027-11).

### 11.3 File tổng hợp `<số đơn>_ALL.dxf`
- Ví dụ 521008-11_ALL.dxf, lưu cùng thư mục, cùng template.
- Xếp 1 cột dọc, căn trái tại X = 0, các hình cách nhau 200 theo Y. Thứ tự theo PDF / CAD依頼書 (trang đầu, dòng đầu ở trên cùng), KHÔNG theo mã; hình cuối cùng sát Y = 0.
- Giữ nguyên chiều quay, hình dạng, màu như file riêng (gồm POINT/TEXT J/LJ và kegaki), chỉ tịnh tiến.
- Mỗi hình 1 TEXT mã yêu cầu (6 số), cao 12, căn trái tại X = -150, Y = Y đáy hình + chiều cao hình/2 (đáy chữ ngang tâm hình), style Standard, layer 0 (chữ cùng layer với đường cắt là chủ ý, người dùng đã biết, không nhắc lại). Cập nhật EXTMAX theo toàn bộ hình + chữ.
- Không ghi chú/giả định vào file ALL (chỉ báo trong chat); ngoại lệ duy nhất là Flag.

### 11.4 Flag (cảnh báo trong file ALL)
- Ghi Flag tiếng Việt có dấu ngay dưới chữ mã khi gặp:
  1. Kích thước PDF và DXF khác nhau.
  2. Kích thước giữa các hình chiếu không khớp.
  3. Thiếu kích thước (chỉ khi không tính được qua chuỗi, mục 2; kể cả góc bo cong thấy trên hình mà không ghi số R, mục 8).
  4. Kích thước và hình dạng không khớp.
  5. Ghi chú tay không đọc rõ.
  6. Kích thước ghi quá mờ, không đọc rõ.
  7. Không rõ kích thước trong hay ngoài (chỗ uốn).
  8. Số lượng lỗ ghi không khớp với hình.
  9. Số lượng bo R hoặc vát C ghi không khớp với hình.
  10. Độ giãn viết tay khác bảng (vẫn dùng số tay; ghi: tay x, bảng y).
  11. Không chắc mặt nào là mặt ngoài (vẫn vẽ theo mặt đã chọn; ghi mặt đã chọn).
  12. Khi trên tấm có hàn tại cả 2 mặt mà bạn chưa biết phải kegaki trên mặt nào.
  13. Cộng thêm lượng dư gia công có thể làm thay đổi R hoặc C.
  14. Tổng các kích thước trong chuỗi Dim khác với kích thước tổng.
  15. Chân dim kích thước bị lệch.
  16. Thiếu độ giãn dài.
  17. Có bất kì lỗ tròn nào (tính cả lỗ mồi) trong tấm nhỏ hơn 1/2 độ dày của tấm đó.
  18. Kích thước có dung sai (trừ trường hợp dung sai dương và dung sai âm băng nhau).
  19. Gọc nhọn quá bé không thể laser R.
- Không Flag chỉ thị riêng (ghi chú laser, chiều dài tay viết) hay lệch số trong ngoặc/CAD依頼書. Flag không thay việc phải hỏi; ghi cả trong báo cáo; không ghi ở file riêng.
- Dạng: đánh số 1., 2., 3... theo từng hình (số cuối = số Flag), không ghi chữ "Flag": `<số thứ tự>. <câu chuẩn> (<chi tiết: vị trí, số liệu>)`, ví dụ "1. Kích thước PDF và DXF khác nhau (lỗ 3xφ4: PDF φ4, DXF φ4.5)".
- Hiển thị: TEXT cao 5, căn trái, X = X chữ mã (-150); dòng k (k = 0, 1...) tại Y = Y chữ mã - 12 - 7k; ≤ 40 ký tự/dòng, ngắt ở khoảng trắng; layer `0`, Magenta `62 = 6`. Style Standard (Arial, mục 11.2 bước 3; SHX `txt` cũ hiện "?"). Ký tự ngoài ASCII ghi `\U+XXXX` (hex hoa, NFC); file vẫn ghi cp932.
- Kiểm tra: ezdxf `audit` 0 lỗi; render: dấu đúng, không đè hình.

## 12. Bảng kiểm trước khi giao (ghi vào báo cáo)
- Mặt vẽ (từng mã, làm TRƯỚC khi xuất file): loại hình chiếu dùng; mặt nhìn thấy; mép trước nằm trên hay dưới; cánh/phần mở rộng sát mép nào; kết quả đối chiếu 2 hình; mặt vẽ cuối cùng (ngoài/trong/kegaki).
- Gán kích thước (mục 4.1): mọi con số gần chi tiết đã được gán.
- Đỉnh: bảng đỉnh của biên (sau xoay) đối chiếu từng đỉnh với hình chiếu gốc; bounding box trùng CAD依頼書 không chứng minh hình đúng.
- Lỗ → tấm (mục 7): không tấm nào thừa/thiếu lỗ.
- Lỗ mồi (mục 7): mỗi nhóm lỗ taro đã đối chiếu ghi chú tay 下穴/lỗ mồi trong PDF; ghi nguồn φ (bảng hay ghi chú tay) vào báo cáo.
- n-Rx và R ↔ cung (mục 8): đủ số góc, không ghi chú/cung nào lẻ.
- Render preview, so từng đặc điểm bất đối xứng (cánh sát mép nào, góc vát, tấm hàn nhô ra mép nào) với ≥ 2 hình chiếu gốc; cặp gương kiểm kỹ hơn.
- Chuỗi kích thước: mọi chuỗi không cộng đủ tổng đã đo pixel từng điểm đầu/cuối và ghi kết quả; cặp gương đã đo vị trí lỗ riêng từng tấm; Flag 14/15 đã ghi nếu còn lệch.
- Kegaki: lập bảng (tấm nhận × chi tiết hàn lên): vẽ/bỏ, lý do, từng cạnh vết trùng mép tấm hay nằm trong tấm, số đo pixel kiểm ≥ 2 hình (≤ 1 mm). Không tấm nào có chi tiết hàn lên mà chưa xét.
- So kích thước phôi với CAD依頼書 và công thức giãn; cạnh thẳng áp cả Ox và Oy; số entity hợp lý (cung nửa tròn là 1 ARC; các cung tiếp nối cùng tâm cùng bán kính gộp làm 1); mọi góc lõm vách–tấm đã xét điều kiện rạch Green và đường uốn ngắt/chạy hết ở cánh có khe theo mục 6 (trừ 2 ngoại lệ mục 6: đầu cánh vát 135°, relief góc của khách); kiểm file theo mục 11.2 bước 8.

## 13. Chạy song song (đơn từ 4 chi tiết)
- Đơn ≥ 4 chi tiết chạy song song (tối đa 2-3 subagent) theo `/mnt/project-files/tools/sheetmetal_kit/README.md`; đơn ≤ 3 làm tuần tự.
- Tấm ĐƠN GIẢN (phẳng/L/U có lỗ) gộp 3–4 tấm/subagent; tấm PHỨC TẠP (có cung, hình tay, nhiều đỉnh xiên, hộp, bản vẽ lắp) một tấm/subagent; cặp gương và tấm chung dim lắp chung một subagent (vẫn đo riêng, mục 2). Không chắc thì PHỨC TẠP.
- Subagent chỉ đọc skill trích bằng `skill_extract.py` theo loại; overlay chỉ bắt buộc cho tấm PHỨC TẠP.
- Agent chính gộp bằng `merge_all.py`, kiểm lại mặt vẽ và hướng (mục 3, 10), rồi chạy dxf-check (bước 3a).