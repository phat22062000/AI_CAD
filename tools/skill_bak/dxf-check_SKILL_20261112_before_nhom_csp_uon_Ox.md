---
name: "dxf-check"
description: "Kiểm DXF đầu ra (26-xxxxxx.dxf, file ALL) sau dxf-sheetmetal: chỉ kiểm hình dạng, không kiểm Template; báo cáo chỉ nêu lỗi sai."
metadata:
  version: "2026.11.11-1"
---

Dùng sau bước 6 của skill `dxf-sheetmetal` (trước khi commit file về máy người dùng), hoặc khi người dùng yêu cầu kiểm một file DXF đã có. Tiêu chí lấy từ `dxf-sheetmetal` (mục 2–12), `Quy_Tac_Laser.md`, `Ghi_Chu_Loi_Tao_DXF.md` (`knowledge/Context_Laser/`). **Chỉ kiểm hình dạng, không kiểm cấu trúc Template** (file lưu từ CAD có header/owner khác Template là bình thường, không báo); muốn so Template thì thêm `--template`.
**Nguyên tắc: kiểm = so file với kỳ vọng dựng độc lập từ nguồn (PDF bản vẽ + CAD依頼書 + DXF khách trong thư mục đơn), không chỉ soi file đầu ra.** Đúng/sai chỉ nói được khi đã có nguồn; thiếu nguồn thì dừng và báo, không kết luận. Script `dxf_check.py` đo phần đo được và đối chiếu chữ PDF/DXF khách (`--src`); PDF scan không có chữ in nên số kích thước, vị trí lỗ và ghi chú tay chỉ kiểm được qua bảng đọc mù độc lập `blind_table.md` (mục 1 bước 3). Không có bảng này thì không được kết luận 'đúng' cho các mục đó.
**BẮT BUỘC (người dùng chốt 02/11/2026): LUÔN PHẢI ĐỌC BẢN VẼ ĐỘC LẬP (từ PDF/DXF khách) RỒI MỚI ĐƯỢC CHECK. TUYỆT ĐỐI KHÔNG làm lại từ bản vẽ output của skill tạo file ALL: không dùng file ALL/file riêng, `gen_*.py`/`gen_*.ps1`, `exp.csv`, bảng đọc hình, ảnh preview hay báo cáo của phiên tạo file làm nguồn kỳ vọng. Chưa đọc độc lập xong (chưa có `blind_table.md` từ nguồn) thì KHÔNG mở file đầu ra và KHÔNG được kết luận. Không đọc độc lập được (thiếu nguồn, không chạy được subagent) thì dừng và báo người dùng, không tự kiểm lại bằng chính phiên đã tạo file.**

## 1. Quy trình
1. Lấy đủ 3 thứ: (a) file cần kiểm (riêng + ALL), (b) PDF bản vẽ và CAD依頼書 của đơn, (c) DXF khách. Container hoặc stage từ máy (`device_stage_files`) cả thư mục đơn; `--src` trỏ đúng thư mục chứa PDF/DXF khách (script chỉ quét cấp đầu, bỏ qua `*_ALL.dxf` và `26-xxxxxx.dxf`). Thiếu (b) hoặc (c) mà thư mục máy có thì stage; thật sự không có thì báo người dùng và ghi rõ phần nào chưa kiểm được.
2. Script: `/mnt/project-files/tools/dxf_check.py`; không có (ngoài project) thì stage bản sao `C:\Users\DELL\Desktop\AI_CAD\AI_Work\tools\dxf_check.py`. Thiếu thư viện: `pip install ezdxf` (thêm `matplotlib` nếu cần `--png`).
3. Dựng kỳ vọng từ nguồn TRƯỚC khi mở file đầu ra, mỗi mã một dòng: phôi (DXF khách trước, đọc cả BLOCK/INSERT, rồi PDF), mặt vẽ, lỗ (n-φ, n-M, 下穴), R/C, giãn (tay > bảng), kegaki, Flag cần có. PDF: `pdftotext -layout` lấy chữ in. Phần còn lại (kích thước, lỗ, ghi chú tay, vùng khoanh đỏ) lấy từ `blind_table.md`: dùng bảng có sẵn trong thư mục đơn nếu do subagent đọc mù tạo (không thấy DXF đầu ra); chưa có thì chạy mới theo `tools/blind_read_prompt.md` (subagent chỉ có copy PDF, KHÔNG đưa file đầu ra, exp.csv hay bảng của người tạo). Từ bảng đó lập kỳ vọng từng mã: kích thước chi tiết, tọa độ lỗ tính từ mép (theo điểm đầu–cuối đã ghi), tổng chuỗi = bề rộng. Chỗ nguồn mâu thuẫn hoặc đọc không rõ ghi riêng để Flag. Rồi chuẩn bị tham số:
   - `exp.csv` (UTF-8): `code,X,Y,mat,t` mỗi mã 1 dòng; `mat` là nhóm vật liệu theo `Quy_Tac_Laser.md` mục 1: `SS` (SS400, SPHC, SPCC, SECC...), `SUS`, `AL`, `CU`. Đơn một vật liệu thì có thể dùng `--mat` `--t` thay cột.
   - `--order` các mã theo thứ tự trang PDF (trang đầu, dòng đầu trước).
   - `--mirror A:B` cho mỗi cặp 本図/対称, R/L, A-1/A-2.
   - `--single THU_MUC` nếu có file riêng 26-xxxxxx.dxf (so hình trong ALL với file riêng).
3a. Đơn nhiều chi tiết (mục 13 dxf-sheetmetal): đọc mù chạy song song theo nhóm ghi trong `order_context.json` (tấm ĐƠN GIẢN gộp 3–4 tấm một subagent, tấm PHỨC TẠP mỗi tấm một subagent, cặp gương chung một subagent),tối đa chỉ được phép chạy 3 subagent, mỗi nhóm một thư mục trống chỉ có PDF trang của nhóm. Prompt mới nhất: `/mnt/project-files/tools/sheetmetal_kit/blind_read_prompt.md`. Mức GỌN cho nhóm ĐƠN GIẢN (một lượt, đo pixel 1 lỗ mỗi hình, lượt 2 chỉ cho mục không chắc), ĐẦY ĐỦ cho PHỨC TẠP; gặp chuỗi lệch, cặp gương hoặc ghi chú tay khó đọc thì chuyển sang ĐẦY ĐỦ cho chi tiết đó. Không bỏ bước đọc mù, không gộp vào bước dựng.
3b. Đầu vào: PDF có trang ghi "DATA" (khách có gửi DXF) mà thư mục đơn không có DXF khách tương ứng (tên không khớp email đính kèm, hoặc DXF là bản vẽ khác) thì mọi mã của trang đó phải có Flag 20 (dxf-sheetmetal mục 11.4); thiếu Flag là LỖI, chỉ báo, không tự sửa.
4. Chạy: `python3 dxf_check.py <file> --expect exp.csv --src <thư mục đơn> --order 064301,064302 --mirror 064157:064158 --single <thư mục> --png preview.png`. Mã thoát 1 nếu có LỖI. Không có `--src` thì script lấy thư mục của file; không thấy PDF/DXF khách sẽ báo CẢNH BÁO 'chưa có kỳ vọng độc lập' (không được bỏ qua; chỉ bỏ khi đã có `blind_table.md` và đã so xong).
5. Xử lý kết quả:
   - Phát hiện lỗi (LỖI của script hoặc mục SAI khi so nguồn) chỉ được BÁO LẠI cho người dùng, KHÔNG tự sửa file đầu ra, script sinh (`gen_<đơn>.py`) hay file đã commit về máy, và không xuất lại. Chỉ sửa sau khi người dùng cho phép rõ ràng cho lỗi đó (người dùng chốt 30/10/2026); phép sửa lỗi này không tự áp sang lỗi khác.
   - LỖI: ghi lại vị trí, nguồn ghi gì, file có gì, đề xuất cách sửa; chờ người dùng cho phép.
   - CẢNH BÁO: xem từng mục; ngoại lệ hợp lệ thì ghi lý do trong báo cáo, nghi là lỗi thì báo như LỖI (không tự sửa).
   - THÔNG TIN: tóm tắt từng hình (kích thước, lỗ, cung R, cặp uốn và giãn, Green, kegaki, Flag) để đối chiếu với các bảng mục 12 của `dxf-sheetmetal`; không đưa vào báo cáo trừ khi phát hiện sai.
6. So từng mã với kỳ vọng bước 3 (mục 4 là danh mục phải so; kích thước phôi và tọa độ từng lỗ đo từ file rồi so với `blind_table.md`, không so với exp.csv chỉ có khung bao), mỗi mục ghi nguồn: 'DXF khách ghi X / PDF ghi Y / file có Z' → ĐÚNG hoặc SAI (chỉ ghi lại mục SAI); xem `preview.png` (Flag hiện `\U+XXXX` thô và rộng hơn thực tế, chỉ dùng để xem hình).
6a. Điểm 'không chắc' trong `blind_table.md` ảnh hưởng toạ độ/kích thước (chuỗi không cộng đủ, đường gióng sát tâm lỗ, số đo từ mép nào) KHÔNG tính là khớp. Phóng to ≥ 300 dpi đầu/cuối từng số, đo pixel vị trí từng lỗ/ô khoét của TỪNG tấm (cặp gương đo riêng từng tấm), so với file; lệch > 1 mm hoặc vẫn không chắc thì báo. Không dùng ràng buộc tổng để chốt cách đọc (lỗi 521102-23 065504: bản đọc mù và bản tạo cùng chốt 57,5 / 171,5 theo tổng 229, đúng là 60 / 174).
7. Sau khi commit về máy: `device_list_dir` kiểm file có mặt và dung lượng đúng bằng file trong container; lệch thì commit lại từ thư mục staged mới (lỗi đã gặp 521023-07, 521027-11).
8. Báo cáo chỉ nêu lỗi sai, trình bày ngắn gọn theo mã: mục sai (nguồn ghi X, file có Z, đề xuất sửa), LỖI/CẢNH BÁO còn lại kèm lý do, rồi hỏi người dùng có cho sửa không (không sửa trước). Mục đúng không báo; mã không có lỗi gộp một dòng cuối ('không phát hiện lỗi: ...'). Vẫn nêu mục chưa so được (thiếu nguồn, ảnh mờ) và chỗ cần người dùng xác nhận vì đó chưa phải 'đúng'. Ghi rõ 1 dòng: phần đã kiểm độc lập (khớp `blind_table.md`) và phần chưa (mặt ngoài, xoay/lật, kegaki, đặt hướng: đọc mù không kiểm được).

## 2. Script tự kiểm (mức báo)
| Nhóm | Nội dung | Mức |
|---|---|---|
| Cấu trúc (chỉ chạy khi có `--template`, mặc định tắt) | cp932, CRLF, cặp mã/giá trị số nguyên, `  0` trước ENDSEC (lỗi 521013-04), phần sau ENTITIES trùng mẫu, ngoài ENTITIES chỉ khác EXTMAX/HANDSEED/VPORT *Active/mã 3 Standard, `arial.ttf`, số không dạng 1e-05/nan, owner 6F, handle ≥ HANDSEED mẫu và < HANDSEED file, không trùng | LỖI |
| ezdxf | đọc được, `audit` 0 lỗi | LỖI |
| Entity | chỉ LINE/CIRCLE/ARC/POINT/TEXT, layer 0; màu: trắng, Green 3 (rạch), Đỏ 1 (kegaki), Magenta 6 (Flag); DASHED chỉ ở LINE trắng | LỖI/CẢNH BÁO |
| Biên | vòng kín, không hở đầu mút, không nét trùng, không LINE dài 0, lỗ/POINT/uốn/kegaki nằm trong phôi | LỖI |
| Góc | góc lồi ≤ 90° chưa bo khi vật liệu cần Laser R; thép ≥ 19t góc lõm phải R3; cung nhỏ hơn Laser R (hạ R) báo để nêu trong báo cáo; 2 ARC liền cùng tâm/bán kính | LỖI/THÔNG TIN |
| Lỗ | φ < lỗ nhỏ nhất theo vật liệu/độ dày (nên là POINT, trừ quy định khách như 810) | CẢNH BÁO |
| Lỗ mồi | φ trùng bảng lỗ mồi taro (M3 2.5, M4 3.3, M5 4.2, M6 5, M8 6.8...): in danh sách từng hình; ghi chú tay 下穴 trong ảnh PDF thì đọc tay (dòng 'Nguồn' bên dưới chỉ bắt 下穴 là chữ in) | THÔNG TIN |
| POINT lỗ | POINT không phải J/LJ: chỉ đúng khi lỗ gốc (kể cả lỗ mồi) < lỗ nhỏ nhất hoặc có ghi chú tay ピアス khoanh riêng quanh lỗ; tem PIERCING đầu trang không đủ; lỗ ren mồi ≥ lỗ nhỏ nhất phải là CIRCLE (lỗi 521030-12). Đối chiếu ảnh PDF từng POINT | CẢNH BÁO |
| Uốn | mỗi chỗ uốn 2 LINE DASHED song song, cách nhau = giãn; in ra giãn đo được; 2 đường cùng độ dài, cùng đầu mút, không dài hơn bề rộng chỗ uốn thật (đường kéo qua phần cánh nhô ra ngoài bề rộng này là sai) | CẢNH BÁO |
| Rạch Green | mỗi rạch 3 entity, cung R0.5; góc lõm 90° sát đường uốn chưa có rạch | CẢNH BÁO |
| Rạch Green (số đo) | LINE chéo 45°: điểm đầu cách mép khoét = Piercing ngoài theo vật liệu/độ dày (`pierce_out`) | LỖI |
| | LINE rạch thẳng: sâu t + 0.2 tính từ góc khoét | CẢNH BÁO |
| Kegaki | trùng mép phôi hoặc trùng đường uốn, nằm ngoài phôi | LỖI |
| Đặt hình | file riêng góc dưới trái (0,0); ALL: mép trái X = 0, cách nhau 200, hình cuối sát Y = 0; cạnh dài theo X; có cạnh thẳng áp cả Ox và Oy | LỖI/CẢNH BÁO |
| J/LJ | phôi Oy ≤ 100 và Ox ≥ 1000: đủ POINT + TEXT J/LJ cao 10 trên mép trên tại 30, ..., L - 30 | LỖI |
| Chữ mã (ALL) | đúng 1 TEXT 6 số mỗi hình, X = -150, Y = đáy + cao/2, cao 12, trắng, căn trái, style Standard; file riêng không có chữ mã/Flag | LỖI |
| Flag (ALL) | cao 4, Magenta, X = -150, Y = Y mã - 12 - 7k; đánh số 1., 2. liên tục, không chữ "Flag"; ≤ 30 ký tự/dòng; ký tự ngoài ASCII dạng `\U+XXXX`; nội dung bắt đầu bằng 1 trong 20 câu chuẩn; không chạm hình dưới | LỖI/CẢNH BÁO |
| 依頼 | kích thước phôi so X/Y CAD依頼書 (chỉ tham khảo), thiếu mã | CẢNH BÁO/LỖI |
| Nguồn (`--src`) | không có PDF/DXF khách; PDF không có lớp chữ (scan): phải có `blind_table.md` (bước 3) | CẢNH BÁO |
| | lỗ vẽ có φ không nằm trong PDF/DXF khách/lỗ mồi M; PDF ghi n-φ mà hình thiếu hoặc lệch số lượng; 下穴φ trong PDF mà hình không có lỗ đó; 展開 PDF khác phôi | CẢNH BÁO |
| | R trong PDF/hình không khớp nhau; khung DXF khách khác phôi; DXF khách đọc cả BLOCK | THÔNG TIN |
| Thứ tự | thứ tự hình trên xuống so `--order` | LỖI |
| Cặp gương | B là gương trái–phải/trên–dưới của A; giống hệt A mà hình không tự đối xứng là LỖI (lỗi 064157/158) | LỖI/CẢNH BÁO |
| File riêng ↔ ALL | hình trong ALL chỉ được tịnh tiến so với file riêng | LỖI |

## 3. Cảnh báo thường gặp là hợp lệ (ghi lý do, không sửa)
- Góc lõm sát đường uốn không rạch Green: hộp 4 cánh đầu vát 135° (26-063561), relief khối vuông 3.5 khách 646 (063377), mép thân nằm giữa 2 đường uốn (COVER 064036/064041).
- Góc lồi sắc: vật liệu/độ dày không bo (SS 10–16, SUS/AL ≥ 7), khách quy định không bo, góc vát C (> 90°).
- Mép trái X ≠ 0 vài mm do góc bo ở đỉnh xiên: xem lại cách đặt hình (mục 10 `dxf-sheetmetal`), nêu trong báo cáo.
- Phôi khác X/Y CAD依頼書: bản vẽ đúng hơn 依頼 (ví dụ 064175 104 x 85.5 so 104 x 84; 063955 334.36 so 274.36); phải có Flag hoặc giải thích.
- Lỗ < lỗ nhỏ nhất vẫn vẽ CIRCLE theo quy định khách (810: mọi lỗ là lỗ xuyên).

## 4. Danh mục so với kỳ vọng từ nguồn (script chỉ đối chiếu chữ in; kích thước, ghi chú tay, hình: so với `blind_table.md` và ảnh PDF)
- Mặt vẽ: loại hình chiếu (hình dưới không mặc định là hình bằng), mặt nhìn thấy, mép trước, ưu tiên kegaki > 表 > mặt ngoài uốn > hình chiếu chính (uốn ngược chiều) > hình chiếu đứng; tấm tách từ bản vẽ lắp đã lật ra mặt ngoài.
- Tấm uốn: file vẽ mặt ngoài, hình chiếu trên bản vẽ có thể nhìn từ phía đối diện. Xác định mặt vẽ trước, rồi mới báo LỖI vị trí theo hướng trên/dưới (Y). Hướng chỉ suy từ việc hai hình thẳng hàng thì ghi CẢNH BÁO, không ghi LỖI. Hình tay dưới/trên hình chiếu đứng theo 三角法 (hình dưới = nhìn từ dưới). Check tự xác định loại hình và mặt vẽ từ vị trí hình, không bỏ qua với lý do đọc mù không kiểm được mặt ngoài.
- Cặp gương: lỗ, kegaki, cánh ngắn của bản 対称 đúng là ảnh gương (script chỉ báo phép biến hình, không biết bên nào đúng).
- Biên: mỗi đoạn biên ứng với một số/nét trên bản vẽ hoặc DXF khách; không tự thêm đoạn; tấm đặt trong hộp phải dò từng đoạn mép ở hình bằng (064175 có lưỡi 84 x 1.5); số nhỏ trong chuỗi (5, 9, 10) đều đã gán.
- Kích thước: tính theo chuỗi kích thước, không giả định số tròn/giữa/đối xứng (064040, 064045); dung sai vẽ giá trị giữa (55 +0.2/0 → 55.1); số trong ngoặc chỉ tham khảo; DXF khách theo đúng tỉ lệ khung tên.
- Chuỗi không cộng đủ tổng, cặp gương: so từng tấm theo pixel, không suy tấm này từ tấm kia (065504: số 60 đo tới tâm lỗ, không phải tới mép ô khoét).
- Chỗ uốn: phải biết mỗi kích thước là trong hay ngoài (blind_table ghi); là kích thước trong mà phôi chưa đổi sang ngoài là LỖI; không xác định được thì cảnh báo.
- Tra bảng giãn: đúng khoảng chiều dài uốn của mã trước khi lấy số.
- Độ giãn: nguồn đúng (tay viết > bảng Asahi/AICOKU 646 cho 90°; góc khác 90° do người dùng cho); vị trí 2 đường uốn tính từ 2 mép; tổng phôi = ngoài + ngoài - giãn. Giãn lấy từ công thức/K/nội suy bảng 90° cho góc ≠ 90° mà không có số tay hay số người dùng cho là SAI độ giãn dài (mục 5.4). Khách có quy định riêng (ví dụ ×2 một phía) thì đối chiếu theo quy định đó.
- Màu POINT: có dấu THROUGH HOLE/đột xuyên hoặc khách quy định piercing xuyên mà POINT trắng là LỖI (Sai màu PIERCING).
- Lỗ: bảng lỗ → tấm, đếm theo từng ghi chú n-φ/n-M; lỗ taro vẽ lỗ mồi (M6 → φ5, M8 → φ6.8) trừ khi có ghi chú tay 下穴/lỗ mồi (thắng bảng): với MỖI dòng THÔNG TIN 'lỗ trùng lỗ mồi' của script, tìm ghi chú tay cạnh nhóm lỗ đó trong PDF và đối chiếu φ đã vẽ; lỗ bị gạch không vẽ; bản vẽ có chỉ thị tay phần laser thì chỉ vẽ phần được chỉ thị.
- R/C: cộng n-Rx ở mọi hình chiếu, từng cung khớp ghi chú (062832 R12 không phải R5); "n-C" lệch hình đã Flag 9.
- Góc bo cong thấy trên PDF mà không ghi số R: file phải có Flag 3 và vẽ tạm. Thiếu Flag, hoặc vẽ góc nhọn/R0.5 mà không Flag, là CẢNH BÁO. Phóng to ≥ 200 dpi từng góc biên, không chỉ đọc n-Rx.
- Kegaki: có ヨ khoanh tròn / ケガキ / khách 851 thì mọi tấm nhận hàn có kegaki; chi tiết hàn sát mép ngoài thì không kegaki (521029-08); ống tròn vạch đủ đường kính; kegaki vẽ trên đúng mặt; tấm nghi có kegaki mà không chắc phải có Flag 12.
- Rạch Green: mọi góc lõm vách–tấm, hộp đã có rạch; điểm đầu cách mép khoét = Piercing ngoài, sâu t + 0.2.
- Phôi uốn nhiều mặt: so biên dạng ngoài từng mặt với nét trên hình chiếu của mặt đó, không chỉ so kích thước tổng. Rạch Green có khi và chỉ khi mép tại góc lõm ngang bằng kích thước uốn ngoài; rạch thừa hay thiếu đều báo.
- Flag: mọi điểm thuộc 20 trường hợp đã ghi, cũng có trong báo cáo; không Flag chỉ thị riêng hay lệch số trong ngoặc/依頼.
- Thứ tự: đúng thứ tự trang PDF, mã bị gạch đã bỏ, không thiếu mã.

## 5. Các trường hợp tính là LỖI|
Sau khi so sánh bản vẽ cần check với bản vẽ kỳ vọng thì các trường hợp dưới đây tính là LỖI.
1. Sai mặt vẽ.
2. Sai kích thước và vị trí kegaki.
3. Thiếu kegaki.
4. Sai độ giẫn dài.
5. Thiếu lỗ (bao gồm cả lỗ mồi).
6. Sai kích thước lỗ (bao gồm cả lỗ mồi).
7. Sai vị trí lỗ (bao gồm cả lỗ mồi).
8. Sai kích thước biên dạng ngoài (bao gồm tất cả các kích thước ràng buộc có ảnh hưởng đến biên dạng ngoài).
9. Thiếu góc bo R theo quy định.
10. Sai kích thước bo R.
11. Thiếu vát C.
12. Sai kích thước vát C.
13. Sai màu PIERCING.

## 6. Các trường hợp CẢNH BÁO
Sau khi so sánh bản vẽ cần check với bản vẽ kỳ vọng thì các trường hợp dưới đây tính là CẢNH BÁO.
1. Kích thước, hình dạng trong PDF của khách khác với DXF của khách.
2. Độ giãn dài viết tay khác với độ giãn dài trong bảng quy định.
3. Ghi chú viết bằng tay không chắc chắn về nghĩa.
   (Ngoại lệ: chữ "J" viết tay cạnh mã vạch nghĩa là gia công nội bộ, không cảnh báo, không yêu cầu J/LJ.)
4. Chuỗi kích thước không cộng đủ tổng, hoặc điểm đầu/cuối của số kích thước không phân biệt được sau khi đã đo pixel.
5. Góc bo cong nhìn thấy trên bản vẽ nhưng không ghi số R.
 
## 7. Yêu cầu trình bày OUTPUT (BĂT BUỘC TUÂN THỦ)
- OUTPUT chỉ bao gồm LỖI (mục 5) và CẢNH BÁO (mục 6), không được phép có thêm bất cứ thông tin nào khác.Trình bày theo đúng thứ tự của bản vẽ trong file Excel CAD依頼書.
- Phần báo cáo LỖI và CẢNH BÁO phải được ghi nguyên mẫu theo đúng những trường hợp được liệt kê ở mục 5 và mục 6 để khi nhìn vào biết ngay đó là loại LỖI hay CẢNH BÁO gì rồi mới trình bày cụ thể sau.
- Phần trình bày cụ thể cần phải viết càng ngắn gọn càng tốt chỉ đúng ngay vào chỗ sai trong bản vẽ không lòng vòng.
- Cấu trúc OUTPUT:
"mã số hình vẽ" + "icon" + "trường hợp LỖI/CẢNH BÁO(mục 5,mục 6 lưu ý chỉ ghi tên lỗi không ghi số thứ tự) + "thông tin cụ thể của LỖI/CẢNH BÁO".
- Icon: ❌ cho LỖI, ⚠️ cho CẢNH BÁO. KHÔNG ghi thêm chữ "LỖI" hay "CẢNH BÁO" sau icon (người đọc biết loại qua icon).
- Màu và cỡ chữ (làm báo cáo bằng widget HTML): gửi bằng `post_widget` (widget `show_widget`), dùng biến màu theme, không dùng mã hex. Tên lỗi: đỏ đậm (`var(--text-danger)`, bold). Giá trị SAI trong file: đỏ đậm gạch chân. Giá trị ĐÚNG theo nguồn: xanh lục đậm (`var(--text-success)`, bold). Mỗi lỗi một dòng, nền `var(--surface-1)`, vạch đỏ bên trái. Tiêu đề mã 20px, nội dung 17px, ghi chú phụ (độ chắc, mã không lỗi) 15px.
- Bản không có widget (terminal): vẫn in đậm tên lỗi và các giá trị kích thước sai bằng Markdown `**...**`.

## 8. Cập nhật script
- Script ở 2 nơi: `/mnt/project-files/tools/dxf_check.py` (bản chính) và `AI_Work\tools\dxf_check.py` trên máy (bản sao). Sửa tiêu chí thì sửa bản chính, chạy lại trên vài file ALL cũ trong `/mnt/project-files/<đơn>/` để chắc không báo sai, rồi commit bản sao về máy và kiểm dung lượng.
- `--src`: PDF cần `pdftotext` (poppler-utils); PDF scan không có chữ thì script chỉ cảnh báo, phần so làm tay với `blind_table.md`. Script đoán trang PDF theo mã 6 số; PDF không ghi mã thì chỉ so mức toàn đơn.
- Quy tắc mới trong `dxf-sheetmetal` mà đo được (vị trí, màu, số lượng, khoảng cách) thì thêm vào script; quy tắc cần đọc bản vẽ thì thêm vào mục 4.