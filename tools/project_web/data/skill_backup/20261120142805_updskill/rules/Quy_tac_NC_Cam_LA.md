
# Quy tắc tạo NC cho CamMagic LA

Lấy theo file NC đúng do người dùng cung cấp (26-059090.nc, SPHCP t3.2). Script `claude/cammagic_nc.py` tạo ra file giống hệt từng byte với mẫu này.

## Định dạng file
- ASCII, xuống dòng CRLF, dòng cuối không có CRLF.
- Số: bỏ số 0 thừa, số nguyên vẫn có dấu chấm (`21.`, `0.`, `-3.`, `46.8`). Không có dấu cách giữa các từ lệnh (`G01G41X18.5Y46.8`).

## Cấu trúc
```
(#_)%(#_)
(<mã>.DXF / <rộng X kể cả piercing, 1 số lẻ> X <cao Y, 1 số lẻ>)
#501=106                          ; giữ cố định, không cần quan tâm
M66
G90
G92X0.Y0.
--- mỗi đường cắt ---
G00X..Y..G40                      ; điểm đục (pierce)
M98P9010                          ; mã cắt 9010 (lỗ trắng 9016, vạch dấu 9017)
G01G41X..Y..                      ; dẫn vào
... G01 / G03 ...                 ; cắt
M121
M199
--- kết thúc ---
G01G40
M30
(CUTTING_LENGTH = %8.1fMM  RAPID_LENGTH = %8.1fMM)
(TOTAL_LENGTH = %8.1fMM)
(BEAM_ON = n  KEGAKI_ON = 0  PREPIERCE_ON = 0)
(#_)%(#_)
```

## Đường chạy
- Thứ tự: **vạch dấu (kegaki) trước tiên, rồi lỗ, biên ngoài sau cùng.** Lỗ cắt theo **diện tích từ nhỏ nhất đến lớn nhất**; các lỗ cùng diện tích thì chọn lỗ gần vị trí hiện tại nhất (bắt đầu từ gốc 0,0).
- Lỗ tròn: dẫn vào điểm bên trái lỗ (cx−r, cy), cắt G03 một vòng, chỉ ghi `I` (r). Bán kính < chiều dài piercing lỗ thì đục tại tâm; ngược lại đục cách điểm bên trái đúng chiều dài piercing.
- Lỗ dài / lỗ hình (vòng kín LINE + ARC bên trong biên ngoài): cắt ngược chiều kim đồng hồ (G03 cho cung). **Xác định trục dài của lỗ (so sánh bề rộng X và chiều cao Y của khung bao lỗ):**
  - Lỗ nằm ngang (rộng ≥ cao): điểm vào = điểm **trái nhất** của lỗ (giữa nửa tròn/đoạn thẳng đứng bên trái). Điểm đục cách điểm vào theo phương **ngang**, vào trong lỗ.
  - Lỗ nằm đứng (cao > rộng): điểm vào = điểm **thấp nhất** của lỗ (giữa nửa tròn/đoạn thẳng ngang bên dưới). Điểm đục cách điểm vào theo phương **đứng**, vào trong lỗ.
  - Khoảng cách điểm đục–điểm vào: bán kính cung tại điểm vào nếu nhỏ hơn piercing lỗ (đục tại tâm cung đầu), ngược lại bằng piercing lỗ (tối đa nửa kích thước lỗ theo trục dài).
  - Xếp chung với lỗ tròn theo diện tích (lỗ dài = πr² + chiều dài thẳng × 2r).
  - Mẫu ngang: 26-057027.nc (lỗ dài 16×8, SPHCP t1.6):
    `G00X513.5Y404.72G40` / `M98P9010` / `G01G41X509.5Y404.72` / `G03X513.5Y400.72I4.` / `G01X521.5Y400.72` / `G03X521.5Y408.72J4.` / `G01X513.5Y408.72` / `G03X509.5Y404.72J-4.` / `M121` / `M199`
  - Mẫu đứng: 26-058543.nc (lỗ dài đứng R4.5, rộng9×cao10, SPHCP t6):
    `G00X28.Y7.G40` / `M98P9010` / `G01G41X28.Y2.5` / `G03X32.5Y7.J4.5` / `G01X32.5Y17.` / `G03X23.5Y17.I-4.5` / `G01X23.5Y7.` / `G03X28.Y2.5I4.5` / `M121` / `M199`
- **Vạch dấu / kegaki** (đường màu đỏ, ACI color 62 = `1`, LINE/ARC): cắt bằng `M98P9017` (thay vì `M98P9010`), **không bù G41, không đoạn dẫn vào riêng** — đục ngay tại điểm bắt đầu rồi cắt thẳng. Cắt **trước tất cả** (trước khe, lỗ, biên ngoài). Nhiều cụm vạch dấu thì xếp theo khoảng cách từ gốc tuyệt đối (0,0) đến điểm đục, tăng dần.
  - Vòng kín: đục tại đỉnh gần gốc tuyệt đối (0,0) nhất, chạy chiều kim đồng hồ (giống quy ước biên ngoài), khép kín về điểm đầu.
  - Đường hở (2 đầu tự do): mỗi đầu được kéo dài ra ngoài biên của chi tiết một đoạn `KEGAKI_OFFSET = 3.0` (giả định cố định, đã khớp 3 mẫu piercing_ngoài=6; **chưa xác nhận có tỉ lệ theo piercing ngoài hay không**), theo hướng vuông góc với cạnh biên mà đầu đó chạm tới (trái/phải/trên/dưới khung bao biên ngoài). Chọn đầu có điểm kéo dài gần gốc tuyệt đối (0,0) hơn làm điểm đục, dẫn thẳng (không bù) tới đầu đường gốc rồi chạy tới đầu tự do còn lại.
  - Điểm đục/điểm kéo dài của kegaki cũng tính vào khung bao `(<mã>.DXF / rộng X cao Y)` ở dòng tiêu đề.
  - Mẫu đường hở: 26-058543.nc: `G00X5.Y-3.G40` / `M98P9017` / `G01X5.Y0.` / `G01X5.Y16.5` / `G01X11.Y16.5` / `G01X11.Y0.` / `M121` / `M199`
  - Đã khớp byte-từng-byte với 4/5 mẫu thực tế (26-058543, 26-058544, 26-058546 trừ một lệch 0.5mm không liên quan nêu dưới, 26-058551 trừ sai số làm tròn nêu dưới). Mẫu 26-058549 **không khớp cả hình dạng lẫn kích thước khung bao** so với DXF gốc của chính nó — nghi DXF/NC mẫu bị gửi nhầm (có vẻ khớp ảnh gương của chi tiết lân cận 26-058548); cần người dùng xác nhận lại.
- Khe cắt (スリット, đường hở LINE + ARC, VD khe giảm ứng suất ở góc trong khi uốn): cắt **sau vạch dấu, trước lỗ và biên ngoài** (chi tiết vừa có khe vừa có lỗ: cắt hết khe rồi mới cắt lỗ — đã xác nhận). Đục tại đầu nằm ngoài chi tiết (phía phế liệu), **không G41, không đoạn dẫn vào**: `G00X..Y..G40` / `M98P9010` / chạy G01/G02/G03 theo đường khe tới đầu kia / `M121` / `M199`. Nhiều khe thì chọn khe có điểm đục gần vị trí hiện tại nhất (từ gốc 0,0, sau mỗi khe tính từ điểm cuối khe). Mẫu 26-057140.nc:
  `G00X116.Y117.6G40` / `M98P9010` / `G01X118.854Y120.454` / `G02X119.207Y120.6I0.354J-0.354` / `G01X120.8Y120.6` / `M121` / `M199`
- Biên ngoài: chiều kim đồng hồ, bù G41. Điểm đục nằm trên cạnh trái (cạnh thẳng dài nhất ở X nhỏ nhất, không tính phần vát/bo), cách biên ra ngoài đúng chiều dài piercing ngoài, dẫn vào ngang. Dừng trước điểm vào một đoạn bằng joint ngoài.
- Nếu DXF không có cạnh thẳng đứng tại X nhỏ nhất (VD 26-057025 ban đầu: cánh chéo chĩa sang trái) thì xoay DXF (90°/180°/270°, không lật) để cạnh thẳng nằm sát Oy và biên chạm Ox, rồi mới tạo NC. 26-057025 đã xoay 180°.
- **Phôi dài hẹp (Y ≤ 100 và X ≥ 1000) có marker J / LJ** (TEXT "J" và "LJ" + POINT, nằm trên cạnh biên; đã xác nhận bằng mẫu 26-057101.nc, SPHCP t3.2):
  - Không dùng piercing cạnh trái. Biên ngoài tách thành **2 đường cắt**, mỗi đường mở đầu tại một marker, **LJ trước, J sau**, và đều là cắt biên chiều kim đồng hồ.
  - Điểm đục = marker dịch ra ngoài theo pháp tuyến cạnh một đoạn bằng piercing ngoài (SS ≤3.2: 3 → Y102.5 khi marker ở Y99.5); dẫn vào vuông góc `G01G41` tới marker.
  - Đường 1 bắt đầu tại LJ, chạy cả biên theo chiều kim đồng hồ, **dừng cách J một đoạn bằng joint ngoài theo bảng vật liệu/độ dày** (SS ≤3.2: 0.8 → X29.2; SUS ≤8, AL ≤8, CU: 0.7; SS 4–16, SUS/AL ≥9: 1). Đường 2 bắt đầu tại J, chạy dọc cạnh tới **cách LJ một đoạn joint ngoài** (SS ≤3.2: X1168.7). Như vậy có 2 micro joint ở J và LJ, độ rộng = joint ngoài của vật liệu (không cố định 0.8). Đường 2 kết thúc bằng `G01G40` / `M30`.
  - Phôi cao thêm piercing: đầu dòng 2 ghi `1199.5 X 102.5` (tính cả điểm đục ngoài).
  - Mẫu: `G00X1169.5Y102.5G40` / `M98P9010` / `G01G41X1169.5Y99.5` / `G01X1194.5Y99.5` / `G02X1199.5Y94.5J-5.` ... `G01X29.2Y99.5` / `M121` / `M199` / `G00X30.Y102.5G40` / `M98P9010` / `G01G41X30.Y99.5` / `G01X1168.7Y99.5` / `M121` / `M199` / `G01G40` / `M30`.
  - Nếu phôi thuộc dạng này nhưng DXF không có marker J/LJ thì script cảnh báo và dùng quy tắc thường: cần hỏi lại.
- Vị trí Y của piercing ngoài theo chiều dài L của cạnh trái:
  - L ≤ 100: giữa cạnh (L/2).
  - L > 100: cách đầu dưới của cạnh 40.
- Góc bo laser R (ARC) trên biên ngoài: cung chạy theo chiều kim đồng hồ ghi `G02X..Y..I..J..`, ngược chiều ghi `G03`. `I`, `J` = tâm cung − điểm đầu cung; thành phần bằng 0 thì bỏ (VD `G02X0.5Y347.92I0.5`, `G02X1675.Y347.42J-0.5`). Mẫu: 26-059097.nc (R0.5, SPHCP t1.6). Độ dài cắt tính theo cung.
- Piercing / joint theo bảng vật liệu – độ dày trong `Quy_tac_laser_kim_loai_tam.md` (SS ≤3.2: piercing ngoài 3, joint 0.8, piercing lỗ 6).
- CUTTING_LENGTH tính cả đoạn dẫn vào; RAPID_LENGTH tính từ gốc 0,0 qua các điểm đục, không tính quay về.
- BEAM_ON = số lần M98P9010 **+ M98P9017** (kegaki cũng tính beam).

## Cách dùng script
`python3 cammagic_nc.py <file.dxf> <nhóm SS|SUS|AL|CU> <độ dày> [file_ra.nc]`

Vật liệu trong CAD依頼書 chỉ dùng để xác định nhóm (VD SPHCP → SS) và độ dày; script tự tra piercing/joint. **Luôn lấy độ dày đúng theo cột 板厚 của từng mã trong CAD依頼書 — không dùng chung một độ dày mặc định cho cả đơn** (đã từng sai ở đơn 521006-13: dùng t≤3.2 cho toàn bộ 11 mã trong khi thực tế là 4.5/6/9mm).

## Lệch nhỏ đã biết, chưa có quy tắc tổng quát (không chặn sản xuất)
- 26-058546.nc: điểm đục/tâm lỗ tròn φ19 trong file mẫu lệch Y +0.5mm so với tâm thực trong DXF (18. thay vì 17.5) — có vẻ là chỉnh tay riêng lẻ trong file mẫu, chưa rõ quy tắc, script vẫn dùng tâm DXF.
- 26-058551.nc: 1 tọa độ vạch dấu trong mẫu là `44.32` trong khi DXF có giá trị `44.319334` (làm tròn 3 chữ số ra `44.319`) — chênh ~0.0007mm, không ảnh hưởng gia công, có thể là sai số làm tròn của DXF gốc.

## Giới hạn hiện tại
- Hỗ trợ: biên ngoài LINE + ARC, lỗ tròn, lỗ dài/lỗ hình (ngang và đứng), khe cắt, phôi dài hẹp J/LJ, vạch dấu/kegaki (đường hở 2 đầu và vòng kín).
- Chưa có mẫu, không tự đoán cú pháp: lỗ trắng (9016), joint lỗ, lỗ vuông, piercing cong (≥19t). Cần xin mẫu NC tương ứng khi gặp.
