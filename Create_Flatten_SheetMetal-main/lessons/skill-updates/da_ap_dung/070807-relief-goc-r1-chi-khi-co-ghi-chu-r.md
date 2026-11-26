ĐÃ ÁP DỤNG 26/11/2026 (version 2026.11.26-1): dxf-sheetmetal dòng 5, 81, 136, 138; runner.py dòng 160, 394; dxf-check dòng 5. Không chạy hồi quy theo lời Phát. Bản cũ: skill-out/20261126/old/

# Đề xuất: bài có DXF khách phải bóc entity DXF và ghép từng mặt; cung bo trên phôi phải truy về entity ARC của DXF (relief góc 26-070807)

Nguồn: 521126-06_26-070807 (1 mẫu; đã sửa lại ngày 26/11/2026 theo Phát). Loại lỗi: Sai biên dạng ngoài (thừa 12 ARC R1 ở 4 chỗ khoét góc). Bài học: `lessons\feedback\feedback_relief-goc-r1-chi-khi-co-ghi-chu-r-tren-hinh-bang.md`.

Nguyên nhân (đã đối chiếu DXF khách RX-138514-C1-02.dxf): DXF vẽ ở tỉ lệ 1:3, chỉ có hình chiếu (không có phôi). Ở góc relief trên hình bằng DXF chỉ có LINE vuông, KHÔNG có ARC nào ở các góc lõm. ARC R1 trong DXF chỉ là R uốn (cặp cung r 0.333 và 0.733 = R1 và R1+t chia 3, ở 4 góc hộp) cộng cung R12.5, R5, và hình 3D chi tiết A. T giữ cả 12 góc lõm sắc, đúng với DXF. F bo R1 vì xem PDF (ghi chú "A部4ヶ所角は球面状にR取り(R1)" ở hình 3D và "(2-R1)(曲げR)") rồi chép mẫu SKILL dòng 136-137, không bóc entity DXF tại góc đó. (Việc F nghĩ gì là suy đoán, log không nêu nguyên văn.)

## (a) Script (tools\*.py)
Không đề xuất script. `doi_chieu_khach.py` báo "không đối chiếu được" với DXF nhiều hình chiếu; và R1 có thật trong DXF (R uốn) nên kiểm theo bán kính không phân biệt được. Cần đọc entity tại đúng góc.

## (c) SKILL.md (skills\dxf-sheetmetal\SKILL.md)
Ba chỗ, đều sửa/gộp dòng cũ, không thêm dòng.

Dòng 81, cũ (nguyên văn):
"- DXF chỉ có hình chiếu (không có phôi) vẫn phải trích số liệu (chiều dài mép tự do, chân cánh, tọa độ lỗ) từ đó."
Dòng 81, mới:
"- DXF chỉ có hình chiếu (không có phôi) vẫn phải trích số liệu (chiều dài mép tự do, chân cánh, tọa độ lỗ) từ đó: bóc từng entity (LINE/ARC/CIRCLE, kể cả trong BLOCK) của từng hình chiếu, quy về 1:1, ghép từng mặt (mặt chính, từng cánh) rồi mới dựng phôi; ở mọi chỗ có góc (relief, khe, đầu cánh) đọc entity thực tế tại đúng góc đó. Mọi cung bo trên phôi phải truy được về entity ARC của DXF khách (hoặc ghi chú n-R trỏ đúng góc trên PDF khi không có DXF); DXF cho thấy góc sắc thì để sắc. Ví dụ trong skill chỉ minh họa cách vẽ, không phải nguồn bo góc; chữ R1 ở hình 3D và (曲げR) không phải bo góc phôi. Chỉ so PDF sau khi đã dựng xong theo DXF."

Dòng 136, cũ:
"  - 3 góc lõm bo theo ghi chú (R1), 2 góc lồi bo R0.5 laser. Đường uốn DASHED chỉ chạy giữa 2 mép relief (từ a + s đến cạnh - a - s)."
Dòng 136, mới:
"  - 3 góc lõm của chỗ khoét chỉ bo khi DXF khách có ARC ở đúng các góc lõm đó (hoặc ghi chú n-R1 trỏ đúng các góc đó); không có thì để góc lõm sắc, không bo theo ví dụ ở dòng 137. 2 góc lồi bo R0.5 laser. Đường uốn DASHED chỉ chạy giữa 2 mép relief (từ a + s đến cạnh - a - s)."

Dòng 138, cũ:
"  - Ghi chú "A部 球面状にR取り(R1) 手仕上げ" là hoàn thiện tay sau uốn, không vẽ. Lỗi đã gặp (29/10/2026): coi "3.5 外寸" là tiếp tuyến chỗ uốn, khoét hộp thường + rạch Green nên sai vị trí giao 4 cánh với mặt chính."
Dòng 138, mới:
"  - Ghi chú "A部 球面状にR取り(R1)" (có hoặc không có 手仕上げ) là bo cầu 3D/hoàn thiện sau uốn và "(曲げR)" là R uốn: không vẽ, không làm căn cứ bo góc phôi. Lỗi đã gặp: (1) coi "3.5 外寸" là tiếp tuyến chỗ uốn, khoét hộp thường + rạch Green nên sai vị trí giao 4 cánh với mặt chính (1 mẫu); (2) bo R1 3 góc lõm dù DXF khách không có cung ở đó (1 mẫu)."

## (d) Logic agent trên web (tools\project_web\runner.py; chờ Phát duyệt)
- Dòng 160 (QUY TRÌNH TỪNG MÃ): thêm "Mã có DXF khách: bóc entity DXF của mã bằng ezdxf (từng hình chiếu, quy 1:1, ghép từng mặt), dựng theo DXF xong mới so PDF; mọi ARC trên phôi phải có entity gốc trong DXF hoặc ghi chú R trỏ đúng góc, không có thì để góc sắc."
- Dòng 394 (rút kinh nghiệm, bước 2): thêm "Mã có DXF khách: trước khi kết luận nguyên nhân phải bóc entity DXF khách tại đúng vị trí khác biệt (mỗi entity F thừa/thiếu có entity gốc trong DXF không); nguyên nhân ghi theo DXF trước, PDF sau; không kết luận từ PDF khi DXF đã đủ bằng chứng."

Số mẫu: 1 mã. Sau khi áp dụng nên Chạy hồi quy 26-070807 (đáp án T có sẵn; DXF khách không cung ở góc, phải để sắc) và 26-063377 (có ghi chú 4-R1 và ARC R1 trong DXF, phải vẫn bo R1 nếu DXF có cung).
