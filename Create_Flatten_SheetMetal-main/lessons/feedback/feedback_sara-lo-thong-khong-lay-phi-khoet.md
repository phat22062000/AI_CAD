---
name: feedback-sara-lo-thong-khong-lay-phi-khoet
description: Lỗ cho bu lông đầu chìm (サラ): φ lớn ghi ở mặt cắt là đường kính khoét đầu vít, lỗ cắt là lỗ thông (vòng nhỏ trong DXF khách), không vẽ φ khoét
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-16T10:10:00Z
---

Đơn 521116-10, mã 26-068884 (SUS304 t1.5, bài giao 16/11/2026): PDF ghi 4-φ6.5 ở mặt cắt A, khung tên ghi 六角穴付サラ B-M3x10 4ヶ. Bài AI (F) vẽ 4 lỗ φ6.5; bài đúng (T) vẽ φ3.5. So từng entity (14 entity mỗi bản): vị trí lỗ (x = 59.75/299.75/539.75/779.75, y = 8.25), biên dạng 839.75 x 26.11, bo R1/R3 và hai đường uốn DASHED y = 17.36/20 đều giống nhau; chỉ khác đường kính 4 lỗ.

DXF khách (26-13600-236) có sẵn block ký hiệu lỗ chứa hai vòng φ3.5 và φ6.5 (lồng nhau) ở 4 vị trí, tức φ6.5 là miệng khoét, φ3.5 là lỗ thông.

**Why:** φ6.5 trên PDF là đường kính khoét đầu vít chìm, không phải lỗ cắt. SKILL dòng 85 đã nói khoét côn/khoét bậc không vẽ, nhưng AI lấy con số trên PDF và không mở block ký hiệu lỗ trong DXF khách nên không thấy vòng φ3.5; log không ghi lý do, nguyên nhân là suy đoán từ kết quả. Khách 676 ghi "PDF là chuẩn" nhưng ở đây PDF chỉ ghi φ khoét, không ghi lỗ thông.

**How to apply:** khi khung tên có bu lông đầu chìm/chìm bậc (サラ, 皿, ザグリ) và PDF có φ lớn ghi cho nhóm lỗ đó: (1) mở block/INSERT ký hiệu lỗ trong DXF khách, lấy vòng nhỏ nhất làm lỗ thông; (2) không có DXF thì tra Quy_Tac_Lo_Moi mục 2 và 3 (M3: 3.4), không vẽ φ khoét; (3) khác số PDF thì Flag 1. Phát xác nhận 17/11/2026: lỗ thông lấy theo vòng DXF khách (3.5), không theo bảng (M3 = 3.4); bảng chỉ dùng khi DXF khách không có vòng lỗ thông. Đề xuất skill: lessons\skill-updates\068884-sara-lo-thong.md.
