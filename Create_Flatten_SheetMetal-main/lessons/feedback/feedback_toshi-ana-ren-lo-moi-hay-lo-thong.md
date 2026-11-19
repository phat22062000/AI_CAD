---
name: feedback-toshi-ana-ren-lo-moi-hay-lo-thong
description: Bảng ghi 通し穴 "M3" không kèm ghi chú tay: bản đúng vẽ lỗ mồi ren φ2.5 (bảng Quy_Tac_Lo_Moi), AI vẽ lỗ thông φ3.4. 1 bản vẽ (2 mã gương), nguyên nhân suy đoán
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-19T13:00:00+07:00
---

Đơn 521116-14, mã 26-068416 và 26-068417 (bản gương của nhau, SPCC t3.2): khung ghi chú ghi 通し穴 "M3"; hình cánh nghiêng chỉ có hai vòng tròn nhỏ (dim 12, 62, 5), không có ghi chú tay nào về ren hay lỗ mồi. Bản AI (F) vẽ hai lỗ φ3.4; bản đúng (T) vẽ φ2.5. Vị trí hai lỗ giống nhau, chỉ khác đường kính. `diff_tf.py`: "Sai kích thước lỗ", 2 lỗ mỗi mã.

Bằng chứng: script vẽ lại ghi chú "lo M3 (tham xuyen phi 3.4)", tức AI đọc 通し穴 theo nghĩa đen (lỗ thông, M3 = bu lông M3 luồn qua, mục 2 bảng `Quy_Tac_Lo_Moi.md`) và lấy φ3.4. Bản đúng lấy M3 → φ2.5 của mục 1.1 (lỗ mồi ren). SKILL.md không có dòng nào nói 通し穴 + "Mx" nghĩa là gì.

**Why:** Suy đoán: bảng ghi chú của khách dùng 通し穴 để chỉ loại lỗ M3 của chi tiết (có thể là lỗ taro), SKILL.md chỉ có quy tắc "lỗ taro: lỗ mồi theo bảng" (dòng 148) và "bu lông đầu chìm: lỗ thông theo DXF/bảng mục 2-3" (dòng 85); với nhãn 通し穴 M3 không thuộc nhánh nào rõ nên AI chọn lỗ thông. Chưa biết quy ước này riêng một khách hay chung. Chỉ có 1 bản vẽ.

**How to apply:** gặp 通し穴 "Mx" không có DXF khách (không có vòng ký hiệu), không có ghi chú tay và không có chữ サラ/ザグリ: chưa chắc là lỗ thông hay lỗ mồi ren thì vẽ lỗ mồi ren theo `Quy_Tac_Lo_Moi.md` mục 1.1 (M3 → φ2.5) và Flag 1 ghi cả hai giá trị (φ2.5 và φ3.4), không âm thầm chọn φ3.4. Chưa đề xuất sửa skill: chờ thêm mẫu hoặc Phát xác nhận quy ước, và kết quả Chạy hồi quy.
