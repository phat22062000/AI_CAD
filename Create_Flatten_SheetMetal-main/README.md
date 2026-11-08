# Create_Flatten_SheetMetal

Bộ skill, quy tắc và công cụ tạo bản vẽ trải phôi (DXF) kim loại tấm cho cắt laser, dùng với Claude. Repo chỉ chứa tài liệu và công cụ dùng chung; **không chứa dữ liệu khách hàng** (PDF đơn, DXF/DWG khách, DXF thành phẩm, tên khách).

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `skills/` | Skill gốc từ app Claude (SKILL.md, UTF-8 không BOM): `dxf-sheetmetal` (v2026.11.04-1) tạo DXF trải phôi; `dxf-check` (v2026.11.03-1) kiểm DXF đầu ra |
| `rules/` | Quy tắc laser (`Quy_Tac_Laser.md`: vật liệu, Laser R, piercing, joint, kegaki), lỗ mồi, quy tắc NC CamMagic LA, ghi chú lỗi DXF, quy tắc theo mã khách (đã ẩn tên khách), `bang-do-gian/` (bảng độ giãn khi uốn) |
| `templates/` | `Template.dxf`: file mẫu để ghép hình vào, giữ nguyên từng byte |
| `lessons/` | Bài học: `skill-updates/` (đề xuất sửa skill rút từ lỗi thực tế), `feedback/` (nguyên tắc làm việc), báo cáo thử nghiệm chạy song song |
| `tools/` | `dxf_check.py` (kiểm DXF), `cammagic_nc.py` (DXF sang NC), `sheetmetal_kit/` (chạy song song: render PDF, dựng spec, gộp vào Template), `prompts/`, `skill_sync/` (đồng bộ skill từ app về máy) |
| `docs/` | Quy trình, bản đồ quy tắc, danh sách file đã loại, hướng dẫn đẩy lên GitHub |

## Cách dùng nhanh

1. Cài skill: lấy `skills/<tên>/SKILL.md`, nạp vào Claude (Cài đặt, Skills). Skill trên app là bản gốc; repo này là bản lưu.
2. Đặt `rules/`, `templates/Template.dxf` vào tài liệu project của Claude (skill tham chiếu `Quy_Tac_Laser.md`, `Quy_Tac_Lo_Moi.md`, `Bang_Do_Gian_*.xlsx`, `Template.dxf`).
3. Kiểm DXF: `python3 tools/dxf_check.py FILE.dxf [--template] [--mat SS --t 3.2]` (cần Python và `ezdxf`; các tùy chọn khác ở đầu file).
4. Tạo NC: `python3 tools/cammagic_nc.py <file.dxf> <SS|SUS|AL|CU> <độ dày> [file_ra.nc]`, theo `rules/Quy_tac_NC_Cam_LA.md`.
5. Đơn từ 4 chi tiết: xem `tools/sheetmetal_kit/README.md` (cài `pymupdf pillow numpy ezdxf`).

Quy trình chi tiết: [docs/QUY_TRINH.md](docs/QUY_TRINH.md). Tìm quy tắc theo chủ đề: [docs/BAN_DO_QUY_TAC.md](docs/BAN_DO_QUY_TAC.md).

## Lưu ý

- Mọi file `.md`, `.dxf` giữ nguyên xuống dòng (xem `.gitattributes`); đừng để Git đổi CRLF.
- Dữ liệu khách hàng bị chặn bởi `.gitignore`; kiểm lại trước khi commit.
