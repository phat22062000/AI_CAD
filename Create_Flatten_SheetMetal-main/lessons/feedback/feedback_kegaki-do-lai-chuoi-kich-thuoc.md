---
name: feedback-kegaki-do-lai-chuoi-kich-thuoc
description: "Kegaki phải vẽ đủ cho mọi tấm có ống/tấm hàn lên, và kích thước vết phải đo lại pixel ở ≥2 hình chiếu, đọc đủ ghi chú nhỏ như 3.2 ở đầu ống"
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-04T01:58:48.185Z
---

Đơn 521104-03 (04/11/2026, khách 851): lần đầu bỏ kegaki 065615 (tự cho là ống sát mép đầu nên không cần), rồi vẽ vết ống 30x35 sai; đúng là 30x38.2. Phát chỉ ra cả hai lỗi.

**Why:** (1) áp quy tắc "sát mép thì không kegaki" quá rộng tay, trong khi mép trên ống nằm giữa tấm; (2) trừ chuỗi 65+465-500 mà không đọc ghi chú 3.2 ở đầu ống (kích thước 500 bắt đầu từ mặt dưới thành 3.2) và không đo lại pixel ở ≥2 hình chiếu trước khi giao.
**How to apply:** khách 851 và đơn có KEGAKI: mỗi tấm bị ống/tấm khác hàn lên đều xét kegaki, chỉ bỏ khi mọi cạnh vết đều trùng mép tấm. Mọi kích thước vết suy từ chuỗi phải đo pixel kiểm ở hình đứng và hình chiếu phải (sai số ≤1 mm), lệch thì tìm ghi chú nhỏ (3.2, 9...) chưa đọc. Liên quan [[feedback-doc-ban-ve-khong-gia-dinh]].
