---
name: feedback-goc-lom-xien-gap-go-r3-ghi-chu-chung
description: Ghi chú chung 内側R3 (mọi chỗ uốn không chỉ định đều bo trong R3) trên thép dày: kiểm các góc lõm nơi cạnh xiên gặp gờ; bản đúng bo R3, AI để nhọn (nguyên nhân chưa xác định)
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-20T12:00:00+07:00
---

Đơn 521118-06, mã 26-069742 (SS400 t12, khung 400.04 x 394, bản vẽ chi tiết A có ghi chú chung "指示の無い曲げ部分は全て、内側R3"; không có DXF khách của mã này): so T/F bằng diff_tf.py, khớp entity 48.5%, khung bao giống nhau.
- Hai góc lõm nơi cạnh xiên (168 và 122.6) gặp gờ rộng 12: T bo cung R3 (tâm (312.69; 133.9) và (330.69; 128.64)), F vẽ góc nhọn. Trên bản vẽ hai góc này vẽ nhọn, không ghi số R.
- Cụm khe cạnh gờ (khe 18.3, 17.8, cửa sổ tam giác 92.5) trong F lệch X 0.7 đến 0.9 mm so với T (gờ T x = 315.69 đến 327.69, F x = 314.96 đến 326.96). Cạnh của T còn nghiêng nhẹ khoảng 0.1 độ (ví dụ cạnh khe (327.69; 72.18) đến (327.83; 14.99)), F thẳng lý tưởng. Các kích thước cục bộ trên bản vẽ (18.3, 17.8, 12, 72°) F và T đều khớp, nên phần lệch này không suy ra được từ bản vẽ.

**Why:** Suy đoán, không có bằng chứng trực tiếp: ghi chú chung 内側R3 không được áp cho hai góc lõm xiên/gờ (F chỉ bo R3 ở góc cửa sổ và khe). Cũng không loại trừ T bo vì lý do khác (T còn để nhọn 6 góc lồi đầu gờ, nên không phải "bo mọi góc"). Độ lệch 0.7 đến 0.9 mm của cụm khe: chưa xác định, có thể do T dựng từ nguồn khác (cạnh nghiêng nhẹ).
**How to apply:** Mới 1 mẫu, chưa thành quy tắc. Khi bản vẽ thép dày có ghi chú chung kiểu 内側R3 / R chung mà chỉ một số góc được bo: liệt kê MỌI góc lõm của biên, góc nào để nhọn thì nêu rõ trong báo cáo (Flag 3 nếu không rõ có bo hay không), không tự bỏ qua im lặng. Chạy hồi quy trên mã này sau khi có thêm mẫu cùng loại rồi mới quyết định sửa skill.
