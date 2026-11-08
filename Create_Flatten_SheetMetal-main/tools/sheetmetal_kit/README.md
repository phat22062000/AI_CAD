# sheetmetal_kit: công cụ dùng chung cho chạy song song (mục 13 dxf-sheetmetal, dxf-check bước 3)

| File | Việc |
|---|---|
| pdfpage.py | tách trang PDF theo mã, render 200 dpi + deskew, crop/zoom, thu nhỏ ảnh trước khi xem, px/mm |
| geom.py | dựng spec: LINE/ARC/CIRCLE/POINT/TEXT, đa giác bo R/vát C, tiếp tuyến, giao điểm, bo đoạn-cung, cặp đường uốn, xoay/lật/đưa về gốc, ghi spec JSON |
| specrender.py | vẽ spec, căn 2 điểm, overlay cắt quanh phôi và thu nhỏ |
| merge_all.py | gộp spec vào Template.dxf thành file ALL (chữ mã, Flag) và tự kiểm (đuôi file, mã nhóm, số lỗi, ezdxf audit) |
| skill_extract.py | trích mục dxf-sheetmetal theo loại chi tiết (phang/uon/hop/dxf) cho subagent |
| subagent_build_prompt.md | prompt mẫu subagent dựng phôi |
| blind_read_prompt.md | prompt mẫu subagent đọc mù (mức GỌN/ĐẦY ĐỦ) |
| order_context_template.json | mẫu thông tin chung cả đơn |

Bản chính: /mnt/project-files/tools/sheetmetal_kit/. Bản sao: C:\Users\DELL\Desktop\AI_CAD\AI_Work\tools\sheetmetal_kit\.
Cần: pymupdf, pillow, numpy, ezdxf (pip install pymupdf pillow numpy ezdxf). Đã chạy thử trên đơn 521102-16: merge_all.py cho file ALL trùng từng byte với bản đã giao.

## Quy trình chạy song song chi tiết (đơn từ 4 chi tiết)
1. Agent chính làm bước 1-3 mục 1 một lần cho cả đơn, xem nhanh mọi trang (<= 60 dpi) để phân loại, ghi `order_context.json` (vật liệu, t, J/giãn, quy định khách, loại, nhóm, overlay, mức đọc mù), tách PDF theo trang (`pdfpage.py split`).
2. Phân loại: ĐƠN GIẢN = tấm phẳng chữ nhật hoặc đa giác ít đỉnh có lỗ, chữ L/U/Z có mặt cắt rõ. PHỨC TẠP = có cung (ngoài lỗ tròn), hình tay, nhiều đỉnh xiên, hộp/vách/rạch Green, bản vẽ lắp nhiều tấm, DXF khách nhiều block. Không chắc thì PHỨC TẠP.
3. Chia nhóm: ĐƠN GIẢN gộp 2-4 tấm/subagent; PHỨC TẠP mỗi tấm một subagent; cặp gương/đối xứng chung một subagent (đo riêng từng tấm); các tấm chung một bản vẽ dim lắp ghép chung một subagent (tính chuỗi qua tấm lân cận).
4. Subagent chỉ đọc skill trích bằng `skill_extract.py <SKILL.md> <phang|uon|hop|dxf|all>`; gặp chi tiết khác loại thì báo agent chính. Dựng theo `subagent_build_prompt.md`, xuất `spec_<mã>.json` và `note_<mã>.md`, không tự đổi `order_context.json`.
5. Overlay (`overlay_small`) bắt buộc cho tấm PHỨC TẠP có cung/hình tay/nhiều đỉnh; bỏ cho tấm chữ nhật có lỗ và chữ L/U đơn giản. Overlay chỉ soát hình dạng, lỗ, hướng; không kiểm được mặt vẽ và số liệu tới 0.1 mm.
6. Tiết kiệm token: chỉ mở ảnh đã cắt/thu nhỏ (cạnh dài <= 1200 px), không mở cả trang 200 dpi.
7. Agent chính gộp bằng `merge_all.py` (thứ tự Excel), kiểm lại mặt vẽ và hướng từng tấm, rồi dxf-check (đọc mù chia nhóm: GỌN cho ĐƠN GIẢN, ĐẦY ĐỦ cho PHỨC TẠP).
8. Báo cáo gộp: thời gian từng bước, Flag và điểm không chắc từng chi tiết, ảnh overlay của chi tiết có Flag.
