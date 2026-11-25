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

## Tự check và Rút kinh nghiệm (17/11/2026)

- **Tự check** (khung chi tiết đơn, và khung chi tiết mã ở Đánh Giá AI): việc `kind=check`, agent chạy skill dxf-check, kết quả (chỉ LỖI/CẢNH BÁO) lưu `data\check_results.json` qua `report.py check <đơn> "<mã>|loi|..." "<mã>|canhbao|..."`.
- **Rút kinh nghiệm** (đầu trang Đánh Giá AI): việc `kind=rutkn` cho mọi mã Sai đã đủ `<mã>T.dxf` và `<mã>F.dxf` trong `<đơn>\Sua_loi\` mà chưa có trong `lessons\feedback\_da_rut_kinh_nghiem.json`. Dùng `Create_Flatten_SheetMetal-main\tools\diff_tf.py`; lỗi lên trang qua `report.py loi <đơn>_<mã> "..." loai="..."`. Từ 25/11/2026 kết quả trên trang chỉ còn 3 mục ngắn cho mỗi mã: Sai ở chỗ nào, Nguyên nhân (`nguyen_nhan=`), Cần update (`update=`); `loai/nguon/khop` vẫn ghi cho thống kê nhưng không hiện.
- Chấm một mã Sai lần đầu: server tự tạo `Sua_loi` và chép `<mã>F.dxf` (endpoint `/api/sualoi` để tạo lại). `QA_FROM` trong server.py là ngày bắt đầu báo "Sai chưa có file T".
- Hai việc này không tạo agent/đèn mã trên sơ đồ và không đụng tiến độ vẽ của đơn. Model mặc định Sonnet (cùng model vẽ đơn), effort High; đổi riêng từng việc bằng `data\config.json` (`check_model`, `rutkn_model`). Cần khởi động lại server sau khi cập nhật (agent vẽ đang chạy không bị ảnh hưởng).
- (Bổ sung 17/11/2026) **Tự check chạy script trước**: `qa.py` gọi `Create_Flatten_SheetMetal-main\tools\dxf_check.py` và `doi_chieu_khach.py` ngay khi bấm (0 token), lưu vào `check_results.json` với `src=script`; chỉ mã rủi ro (tối đa 30%) mới thành việc `kind=check` cho agent đọc mù (`src=ai`). Máy chủ web cần Python có `ezdxf`; thiếu thì agent tự chạy script.
- **Chạy hồi quy** (mục Chất lượng theo loại lỗi): việc `kind=hoiquy`, kết quả qua `report.py hoiquy <job id> "<đơn>_<mã>|khop|<%>|" ...` lưu `data\hoi_quy.json`. Model: `hoiquy_model`, mặc định Sonnet.
- **Thống kê** `/api/qa`: lỗi trên 100 mã theo loại, lỗi lặp lại, entity khớp bài đúng, chi phí thật theo loại việc (lấy `usage` của các việc trong `progress.json`). `report.py loi` nhận thêm `nguyen_nhan=`, `nguon=`, `khop=`.
- **Update Skill** (nút ở mục Rút kinh nghiệm, 17/11/2026): người dùng bấm = lệnh "update skill" và duyệt các đề xuất đã chọn (ô chọn từng đề xuất). Việc `kind=updskill`: `runner.backup_skill` sao lưu SKILL.md của 2 skill và `rules\*.md` vào `data\skill_backup\<job id>\`, rồi agent chỉ sửa SKILL.md/rules (không sửa script), nâng version, đổi dòng đầu file đề xuất thành "ĐÃ ÁP DỤNG ..." (còn phần script thì "CÒN CHỜ"), và ghi nhật ký từng dòng cũ/mới qua `report.py updskill <job id> <file.json>` vào `data\skill_updates.json`. Trang liệt kê đề xuất còn chờ kèm số đơn và mã Sai. Khi agent chạy `report.py updskill`, web chuyển các đề xuất đã "ĐÃ ÁP DỤNG" hết (không còn "CÒN CHỜ") sang `lessons\skill-updates\da_ap_dung\` (không xoá hẳn) và trang hiện bảng thông báo "Đã update skill xong" một lần (dòng cũ/mới, mục bỏ qua, đề xuất đã chuyển, thư mục sao lưu); lỗi thì báo lỗi. Hoàn tác = chép lại file từ thư mục sao lưu (và đưa file đề xuất về từ da_ap_dung nếu cần).
- **Phân loại đề xuất** (`server.proposal_kind`, đọc dòng đầu và các mục `## (a) Script`, `## (c) SKILL.md`): `skill` (còn phần SKILL.md/rules: nút Update Skill), `script` (chỉ còn phần tools\*.py: nút Update Script), `hq` ("Chờ hồi quy": tiêu đề có cụm "chờ hồi quy" hoặc mọi mục đều ghi "Không đề xuất": không có ô chọn, không vào hai nút update), `xong`. Nút **Đóng đề xuất** (`POST /api/proposal/close`) cất file sang `lessons\skill-updates\da_ap_dung\`.
- **Update Script** (`kind=updscript`, `POST /api/jobs/updscript`): người dùng bấm = cho phép sửa script. `runner.backup_tools` sao lưu `tools\*.py` vào `data\script_backup\<job id>\tools\`; agent chỉ sửa `tools\doi_chieu_khach.py`, `dxf_check.py`, `diff_tf.py` (không sửa skill, không sửa file của trang web), chạy thử TRƯỚC và SAU trên F/T của mã nêu trong đề xuất, mọi mã đã chấm Đúng và ≥ 6 đơn; chỉ giữ thay đổi nếu có cảnh báo mới đúng ở bản F và không có LỖI/CẢNH BÁO mới ở bản T hoặc mã Đúng, không thì khôi phục bản sao lưu và ghi lý do vào "bỏ qua". Nhật ký qua `report.py updscript <job id> <file.json>` vào `data\script_updates.json` (trang hiện bảng thông báo và mục "Lần update script gần nhất").
- Khung đề xuất sửa skill: nội dung được tô nổi bật (nhãn Nguồn/Lý do, đích sửa script/SKILL.md/rules, dòng cũ đỏ và dòng mới xanh, tên file, số dòng, số đơn và mã). Trang tự làm mới mỗi 15 giây nhưng khung này giữ nguyên trạng thái mở/đóng, ô chọn, và không vẽ lại khi nội dung không đổi hoặc khi đang bôi đen chữ.
