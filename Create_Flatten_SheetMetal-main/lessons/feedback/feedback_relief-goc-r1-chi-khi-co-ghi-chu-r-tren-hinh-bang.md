---
name: feedback-relief-goc-r1-chi-khi-co-ghi-chu-r-tren-hinh-bang
description: Relief góc hộp của khách: góc lõm chỉ bo khi DXF khách có ARC ở đúng góc đó; chữ R1 ở hình 3D và (曲げR) không phải bo góc phôi; bài có DXF phải bóc entity DXF trước
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-26T13:00:00+07:00
---

Đơn 521126-06, mã 26-070807 (hộp mở 4 cánh SPCC t1.2, phôi 515.72 x 230.72, giãn 2.14, 26/11/2026; diff_tf.py: giữ nguyên hướng, khung bao giống nhau, khớp 77.6%): relief góc s = 3 nên 4 đỉnh hộp bị khoét vuông 3 x 3.86 (từ 72 đến 75.86). F khoét đúng vị trí nhưng bo thêm R1 ở 3 góc lõm mỗi chỗ (12 ARC R1: tâm (73; 74.86), (74.86; 74.86), (74.86; 73) ở đỉnh dưới trái và tương tự 3 đỉnh còn lại). T để cả 3 góc lõm sắc.

**Why:** Phát chỉ ra 26/11/2026 và đã kiểm lại bằng DXF khách (RX-138514-C1-02.dxf, tỉ lệ 1:3, chỉ có hình chiếu): ở góc relief DXF chỉ có LINE vuông, không ARC nào ở góc lõm. R1 trong DXF chỉ là R uốn (cung r 0.333 và 0.733 = R1 và R1+t, chia 3, ở 4 góc hộp). F không bóc entity DXF mà xem PDF (ghi chú "A部4ヶ所角は球面状にR取り(R1)" ở hình 3D, "(2-R1)(曲げR)") rồi chép mẫu SKILL dòng 136-137. Bản rút kinh nghiệm đầu chỉ dựa PDF/log và sửa điều kiện "ghi chú R", chưa đúng gốc. Một mẫu.

**How to apply:** bài có DXF khách: bóc từng entity của từng hình chiếu (quy 1:1, kể cả BLOCK), ghép từng mặt, dựng theo DXF xong mới so PDF (PDF khác DXF thì giữ DXF và Flag). Cung bo chỉ vẽ khi truy được về ARC của DXF (hoặc ghi chú n-R trỏ đúng góc khi không có DXF); DXF cho thấy góc sắc thì để sắc. Ví dụ trong skill chỉ minh họa cách vẽ. Đề xuất sửa SKILL dòng 81, 136, 138 và logic web: xem `lessons\skill-updates\070807-relief-goc-r1-chi-khi-co-ghi-chu-r.md`. Liên quan [[feedback-relief-goc-vuong-bo-sot]], [[feedback-doc-ban-ve-khong-gia-dinh]].
