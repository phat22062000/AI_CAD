# Quản lý Project AI_CAD (tools\project_web)

Giao diện web 2 mục, bám phong cách dashboard agent monitor:

1. **Tiến độ** (`#/tien-do`): thẻ từng agent (đơn, mã đang làm, số mã xong, thời gian làm, tín hiệu cuối) và bảng mọi đơn trong `AI_Work` với trạng thái Chưa làm / Đang làm / Đã xong / Đang chờ. Bấm một đơn để xem từng mã.
2. **Đánh giá AI** (`#/danh-gia`): mọi mã của đơn Đã xong mặc định **Chờ check**; chuyển sang Đúng hoặc Sai (kèm ghi chú). Có đồ thị % mã bị sai theo ngày/tháng.

## Chạy

Bấm đúp `start.bat` (cần Python, lệnh `py`). Trang mở ở http://localhost:8780, máy khác trong mạng LAN mở http://<IP máy này>:8780.

## Dữ liệu

| Nguồn | Dùng cho |
|---|---|
| `AI_Work\Thang-xx\dd-mm-yyyy\<số đơn>\` | danh sách đơn, ngày |
| `<số đơn>_依頼.xlsx` (cột 作業No.) | danh sách mã, khách, vật liệu, độ dày, kích thước |
| `<số đơn>_ALL.dxf` | có file này = đơn Đã xong |
| file rỗng kiểu `9T3F.txt` | kết quả chấm cũ (9 đúng, 3 sai), dùng khi đơn chưa chấm từng mã |
| `data\reviews.json` | Đúng/Sai/ghi chú bạn chấm trên trang (lưu bền vững) |
| `data\progress.json` | tiến độ agent tự báo (xem dưới) |

Quy tắc trạng thái đơn: có agent đang chạy thì **Đang làm**; có Flag hoặc agent lỗi thì **Đang chờ**; có file ALL thì **Đã xong**; có DXF lẻ mà chưa có ALL thì Đang làm nếu có file mới trong 30 phút, quá 30 phút thì Đang chờ; chưa có DXF nào thì **Chưa làm**.

Thời gian làm có dấu ≈ là ước tính từ thời gian file (PDF/xlsx đến file ALL) khi agent chưa báo giờ bắt đầu.

## Giao việc trên trang (hàng đợi)

Ở đầu mục Tiến độ: dán đường dẫn thư mục đơn (ổ máy hoặc ổ mạng `\\...`), chọn agent chính (không dùng subagent) hoặc 1, 2, 3 subagent, bấm **Giao việc**. Server kiểm thư mục có tồn tại, có PDF/xlsx, lấy số đơn từ tên thư mục, rồi đưa vào hàng đợi (`jobs` trong `data\progress.json`). Máy không có lệnh `claude` nên trang không tự bật agent: nói với agent "Xử lý hàng đợi", agent đọc `py tools\project_web\report.py jobs` và làm theo mục 5 trong `AI_Work\CLAUDE.md`. Trạng thái việc: Chờ agent nhận → Agent đã nhận → Xong / Lỗi.

## Agent báo tiến độ

Cùng cấu trúc với CLAUDE.md (orders / agents / parts), gọi từ thư mục `AI_CAD`:

```
py tools\project_web\report.py agents 521105-04_S1 order=521105-04 kind=sub name="Subagent 1" codes='["26-065930","26-065931"]' done='[]' current=26-065930 state=running startedAt=now
py tools\project_web\report.py parts 521105-04_26-065930 order=521105-04 code=26-065930 kind=uon agent=521105-04_S1 status=running startedAt=now flags='[]'
py tools\project_web\report.py parts 521105-04_26-065930 status=built blank="232.5 x 50" finishedAt=now flags='[]'
py tools\project_web\report.py agents 521105-04_S1 done+=26-065930 current=26-065931
py tools\project_web\report.py agents 521105-04_S1 state=done current=null finishedAt=now
```

### Sơ đồ agent đang chạy (giống dashboard mẫu)

Mỗi đơn có agent chạy hiện một khung: robot "Lập kế hoạch" (chỉ có agent chính) hoặc mỗi subagent một robot, dây nối tới thẻ từng mã, 4 đèn L0 đến L3, dây sáng tới mã đang làm. Các trường thêm (tuỳ chọn):

| Trường | Ở đâu | Ý nghĩa |
|---|---|---|
| `level` 0..3 | parts | bước của mã: L0 đọc bản vẽ, L1 phân tích kích thước, L2 dựng DXF, L3 tự kiểm |
| `mood` | agents | `think` suy nghĩ, `look` quan sát ảnh, `work` chạy tool, `write` ghi file, `confused` tool lỗi, `question` có câu hỏi |
| `act`, `actAt` | agents | việc đang làm hiện trên thẻ mã, vd `act="Read: 26-066398.pdf" actAt=now` |
| `model`, `effort`, `user`, `slot` | agents (main) | hiện ở dòng đầu khung |

Thẻ mã: `status:"built"` không Flag = PASS (xanh), có Flag = PREVIEW (vàng), `status:"failed"` = FAIL (đỏ). Robot tự về mặt "Chờ" khi `actAt`/`heartbeatAt` cũ hơn 3 phút.

Mỗi lần ghi vào `agents` tự cập nhật `heartbeatAt`; quá 10 phút không có tín hiệu thì thẻ agent báo "Mất tín hiệu". Server không chạy thì report.py ghi thẳng vào `data\progress.json`.
