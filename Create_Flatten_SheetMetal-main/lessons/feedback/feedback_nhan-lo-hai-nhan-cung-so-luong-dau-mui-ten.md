---
name: feedback-nhan-lo-hai-nhan-cung-so-luong-dau-mui-ten
description: Hai nhãn lỗ cùng số lượng (2-Ø4.5, 2-M4) trên một hàng 4 lỗ: mỗi đầu mũi tên chỉ xác định đúng lỗ nó chạm; lỗ còn lại của mỗi nhãn không gán theo cặp gần nhãn mà theo đối xứng/cùng khoảng cách mép, không chắc thì Flag
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-18T16:10:00+07:00
---

Đơn 521118-11, mã 26-069881 (SUS316 t3, 205 x 179, 18/11/2026; so T/F bằng diff_tf.py, khớp 87%, giữ nguyên hướng): cạnh trái có 4 lỗ ở x = 8, y = 6 / 14.5 / 164.5 / 173. Bản vẽ ghi "2-Ø4.5" (nhãn ở trên) và "2-M4" (nhãn ở dưới). Đầu mũi tên 2-Ø4.5 chạm lỗ cách mép trên 6 (y = 173); đầu mũi tên 2-M4 chạm lỗ cách mép dưới 14.5 (y = 14.5). T: φ4.5 ở y = 6 và 173 (hai lỗ ngoài cùng, cách mép 6), φ3.3 (mồi M4) ở y = 14.5 và 164.5 (hai lỗ trong, cách mép 14.5). F: φ4.5 ở y = 164.5 và 173 (cặp trên), φ3.3 ở y = 6 và 14.5 (cặp dưới), tức hai lỗ y = 6 và y = 164.5 bị đổi cỡ. F không Flag. 4 lỗ ở x = 167 / 197 (φ3.3 mỗi hàng), biên dạng ngoài và 2 ô khoét R40 giống nhau.

**Why:** mỗi nhãn "2-" có hai lỗ nhưng đầu mũi tên chỉ chạm một lỗ; lỗ thứ hai là lỗ đối xứng (cùng khoảng cách mép 6 hoặc 14.5 ở mép đối diện). F có vẻ gán theo cặp lỗ nằm gần nhãn (trên/dưới) thay vì theo đầu mũi tên rồi đối xứng; cách F suy luận là suy đoán từ kết quả (log không ghi lý do). Dòng SKILL 142 và 148 đã nói "theo đầu mũi tên" nhưng chưa nói cách chia các lỗ không có mũi tên khi hai nhãn cùng số lượng. Cùng họ với [[feedback-gan-lo-theo-tam-va-canh]] (gán lỗ theo nhãn) nhưng nguyên nhân khác (ở đó gán hết theo một nhãn / sai tấm / sai cánh), nên không gộp.

**How to apply:** lập bảng 'lỗ → nhãn' cho từng lỗ nhìn thấy trên một hàng/cạnh: ghi lỗ mà đầu mũi tên chạm trước; số lỗ còn lại của mỗi nhãn lấy từ các lỗ chưa gán có cùng khoảng cách tới mép với lỗ đã chạm (đối xứng qua tâm cạnh). Tổng số lỗ trên hàng = tổng các "n-" mà không chia được duy nhất theo cách trên thì Flag, không chia theo vị trí nhãn. Dựng xong đếm lại: mỗi nhãn đủ n lỗ và đúng cỡ.
