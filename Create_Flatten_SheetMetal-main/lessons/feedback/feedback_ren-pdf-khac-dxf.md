---
name: feedback-ren-pdf-khac-dxf
description: Cỡ ren PDF khác ký hiệu ren trong DXF khách (5×M3 vs M2.6): dựng lỗ mồi theo DXF rồi Flag 1, không theo PDF
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-16T10:05:00Z
---

Đơn 521112-02, mã 26-067250 (bài giao 12/11/2026): PDF ghi 5×M3, DXF khách vẽ 5 cặp vòng φ2.2/φ2.6 (ký hiệu M2.6). Bài AI (F) vẽ 5 lỗ φ2.5 (mồi M3 theo PDF); bài đúng (T) vẽ φ2.2 (mồi M2.6 theo DXF). So từng entity: vị trí lỗ (x = 12/26/50/78/88, y = 15), lỗ M4 φ3.3, 3 lỗ φ6.2, biên dạng và hai đường uốn đều giống nhau. File ALL giao không có Flag nào.

**Why:** Lúc dựng (12/11) SKILL dòng 82 còn ghi "PDF khác DXF thì theo PDF"; dòng này đã đổi ngày 13/11 thành "dựng theo DXF rồi Flag 1". Dòng 85 ("ký hiệu ren trong DXF chỉ là ký hiệu: không vẽ, chỉ vẽ lỗ mồi") dễ bị hiểu là bỏ qua cỡ ren của DXF. Chữ MTEXT trong DXF cũng ghi 5×M3 nên nhìn chữ thì PDF và DXF khớp, chỉ hình học (vòng φ2.6) lệch. Nguyên nhân là suy đoán từ kết quả.

**How to apply:** Với mỗi nhóm lỗ ren, đọc đường kính cặp vòng ký hiệu ren trong DXF (vòng ngoài ≈ cỡ ren) và so với cỡ ren PDF, không chỉ so chữ. Lệch thì lấy cỡ ren theo DXF, tra lỗ mồi trong Quy_Tac_Lo_Moi (M2.6 → 2.2) và Flag 1. Nhóm khớp (M4 PDF = vòng 4.0 DXF) vẫn vẽ mồi theo bảng (φ3.3), không vẽ theo vòng trong 3.2 của DXF (bài T giữ φ3.3).
