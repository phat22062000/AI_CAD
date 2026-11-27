---
name: feedback-chu-L-hinh-chieu-dung-la-mat-trong-phai-lat
description: Chữ L mà hình chiếu đứng là hình nhìn thẳng vào tấm có cánh hướng về phía người nhìn (mặt trong): phải lật trái–phải ra mặt ngoài, không vẽ nguyên hướng hình chiếu đứng/DXF khách
metadata:
  node_type: memory
  type: feedback
  modified: 2026-11-27T17:00:00Z
---

Đơn 521127-15, mã 26-072887 (bản vẽ trang 7, DXF khách 4801) và 26-072888 (trang 8, DXF khách 4800), 27/11/2026: cặp chi tiết chữ L đối xứng (cánh 55 + tấm 47 có 2 rãnh 9 x 16.5, tab xiên 30° R10 ở đầu cánh 55). Bài AI (F) và bài đúng (T) khung bao giống hệt (98.56 x 95.032), 20/20 entity khớp, chỉ khác phép đặt: F là ảnh gương trái–phải của T (diff_tf: "Sai mặt vẽ (lật)"). F 26-072887 trùng đúng T 26-072888 và F 26-072888 trùng đúng T 26-072887, vì cả hai mã đều bị vẽ ở mặt đối diện (không phải đổi chỗ hai mã: log cho thấy 072887 dựng từ 4801 trang 7, 072888 từ 4800 trang 8).

- T 26-072887: tấm có rãnh ở bên phải (rãnh x 79.06–86.56, hai đường uốn x 51.56 và 55.0), tab xiên ở góc trên trái (x 7.5–34.68, y 79.34–95.03). F: tấm có rãnh bên trái (x 12–19.5, đường uốn 43.56 và 47.0), tab xiên ở góc trên phải (x 63.88–91.06).
- T 26-072888 là ảnh gương của T 26-072887 (tấm bên trái, tab bên phải); F 26-072888 ngược lại.

**Why:** Trên bản vẽ cả hai trang, hình chiếu đứng là hình nhìn thẳng vào tấm 47 (có rãnh), cánh 55 hiện ở đỉnh như một nét mỏng; hình phải (三角法) cho thấy cánh 55 chìa về phía TRƯỚC (bên trái hình phải, mục 3 dòng "Chiếu phải: mép trái = trước"), tức hình chiếu đứng nhìn vào mặt TRONG của chỗ uốn. Mặt ngoài là mặt đối diện, nên phải lật trái–phải (SKILL mục 3, thứ tự chọn mặt vẽ, ưu tiên 3). Log chạy: agent dựng từ toạ độ DXF khách (hình có tab bên trái), chỉ xoay bội 90° rồi lưu, Flag rỗng, không có dòng nào xác định mặt trong/ngoài hay bảng mặt vẽ. Phần "agent đã bỏ qua bước xác định mặt ngoài" là suy đoán từ log (không còn script gốc); phần T là mặt ngoài cũng là suy luận từ quy tắc, chưa có lời xác nhận của Phát.
Script `doi_chieu_khach.py` không bắt được lỗi này (báo "không đối chiếu được" vì DXF khách của chi tiết uốn không có hình khai triển chồng khít).

**How to apply:**
- Chữ L: trước khi dựng, đọc hình chiếu có thấy PROFILE chữ L (hình phải/trái) để biết hình chiếu đứng đang nhìn vào mặt nào: cánh uốn chìa về phía người nhìn hình chiếu đứng = hình chiếu đứng là mặt trong → lật trái–phải (không đổi chiều dọc) rồi mới đặt phôi; ghi dòng "mặt vẽ = ngoài, hình chiếu đứng = trong, lật" vào bảng mặt vẽ (mục 12).
- Chi tiết uốn có DXF khách ở dạng hình chiếu (không phải khai triển): hướng của DXF khách là hướng nhìn của hình chiếu, KHÔNG mặc định là mặt cần vẽ; vẫn áp thứ tự chọn mặt vẽ.
- Cặp đối xứng (4800/4801...): sau khi lật xong vẫn phải là ảnh gương của nhau; nếu cả hai cùng sai mặt thì cặp trông vẫn "hợp lý", nên phải kiểm riêng từng mã với profile chữ L.
- Chưa sửa SKILL: quy tắc ưu tiên 3 đã có sẵn, đề xuất "chờ hồi quy" ở `lessons\skill-updates\072887-072888-chu-L-mat-trong-cho-hoi-quy.md`.
