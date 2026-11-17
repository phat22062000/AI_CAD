---
name: feedback-hoc-bac-khong-xuyen-khong-cat
description: Hốc/rãnh/bậc không xuyên (hình chiếu cạnh thấy đáy ở giữa chiều dày, có dim sâu nhỏ hơn t) không phải biên cắt; laser chỉ cắt đường xuyên hết chiều dày
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-17T13:30:00+07:00
---

Đơn 521113-05, mã 26-068185 (13/11/2026, tấm phẳng dày 5, 252 x 75, 2 góc vát C50, mép cung lõm R96, 2 lỗ φ6.5 khoét bậc φ11 sâu 1.5): F chép nguyên hình chiếu bằng trong DXF khách (block JZB_0002) nên khoét thêm 2 rãnh chữ U rộng 20, đáy R10 ở hai đầu cung R96, cắt ngắn cung và thêm 6 bo R0.5 ở mép rãnh; không Flag. Đúng là (T): biên ngoài giữ cung R96 trọn từ mép tới mép, KHÔNG có 2 rãnh U, vì đó là hốc bậc sâu 2.5 trên tấm dày 5. Bằng chứng: hình chiếu cạnh (block JZB_0001) chỉ có nét bậc từ y = 2.5 đến 5 ở đúng hai khoảng x của rãnh, nét đáy nằm ngang giữa chiều dày, kèm dim 2.5. Lỗ φ6.5 (bỏ vòng khoét φ11) F đã làm đúng. Phụ: F đặt xoay 180° so với DXF khách (T giữ hướng DXF).

**Why:** hình chiếu bằng vẽ đường viền hốc bằng nét liền như biên ngoài; AI chỉ trích hình chiếu bằng, không so với hình chiếu cạnh, nên coi đường viền hốc là biên cắt xuyên. `doi_chieu_khach.py` báo "biên khớp 100%" vì so cùng đường viền đó với DXF khách, không phân biệt xuyên hay không. Việc AI không mở hình chiếu cạnh là suy đoán từ kết quả (vẽ trong 2 phút, không Flag).

**How to apply:** với tấm dày (t ≥ 3) có rãnh/khuyết/bậc trên hình chiếu bằng, trước khi lấy làm biên phải soi hình chiếu cạnh/mặt cắt (cả block JZB khác trong DXF khách): đường gióng chỉ chạy một phần chiều dày, nét đáy nằm ngang giữa chiều dày, dim sâu < t, chữ 深サ/ザグリ/段/座 = hốc không xuyên → KHÔNG cắt, giữ biên xuyên (ở đây cung R96 chạy liền). Chưa chắc là xuyên hay không thì vẽ theo biên xuyên và Flag 1 ghi rõ đặc điểm đã bỏ. Cùng họ lỗi với khoét bậc đầu vít (feedback_sara-lo-thong-khong-lay-phi-khoet.md): cái gì không xuyên hết chiều dày thì laser không vẽ.
