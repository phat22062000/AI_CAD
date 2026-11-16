---
name: feedback-cap-guong-hinh-duoi-va-khe-canh
description: Cặp 本図/対称 vẽ từ hình nhìn từ dưới: 本図 giữ đúng như hình dưới (mặt dưới là mặt ngoài), 対称 là ảnh gương
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-16T08:10:00Z
---

Đơn 521112-15, mã 26-067451 (本図) và 26-067452 (対称), 16/11/2026: bài AI (F) đổi chỗ hình của hai mã; bài đúng (T) giữ 本図 đúng như hình dưới trên bản vẽ. F của mỗi mã chính là T của mã kia, chỉ khác điểm cuối khe (ý 2, trường hợp riêng).

1. Hướng: T 26-067451 có chân φ7 ở dưới (y 0–25.2), đường uốn y 25.2/30, dải lỗ M4 ở y 50.2, cánh 170° ở góc trên phải. F 26-067451 là ảnh gương qua trục dọc phôi: chân φ7 ở trên (y 63.2), cánh ở góc dưới phải, lỗ M4 ở y 25. 26-067452 ngược lại: T là ảnh gương, F giữ hướng hình dưới.
2. (Trường hợp riêng, Phát xác nhận 16/11 không phải quy tắc chung) Khe 1 mm tách cánh 170°: T kết thúc khe tại x = 242.83, giữa hai đường uốn DASHED (242.66 và 243.0). F kéo khe tới 242.66 (đường uốn xa, "để cánh tách hẳn"), khác DXF khách (243) và khác T.

**Why:** AI ghi "ảnh gương, giữ mặt ngoài" nhưng hình vẽ ra là mặt đối diện với hình dưới trên bản vẽ. Nhãn 本図/対称 nằm dưới hai mã vạch; hình dưới là hình nhìn từ dưới, cánh φ7 hướng lên nên mặt dưới là mặt ngoài (SKILL mục 3), phải vẽ đúng như hình dưới, không lật. Đầu khe do AI tự chọn, không có số trên bản vẽ; không rút thành quy tắc. Nguyên nhân hướng sai là suy đoán từ kết quả, log chạy không ghi lý do.

**How to apply:**
- Cặp R/L, 本図/対称: viết ra mặt đang vẽ và hình nguồn (trên/dưới) cho CẢ HAI mã trước khi dựng; 本図 lấy đúng hướng hình nguồn (khi hình nguồn là mặt ngoài), 対称 mới lật. Soát lại: mã chỉ đúng khi các đặc điểm bất đối xứng (phía cánh, chân φ7, vát C) khớp ≥ 2 hình chiếu.
- Mã vạch cạnh nhãn quyết định mã nào là 本図, mã nào là 対称; không đổi theo thứ tự trong bảng.
