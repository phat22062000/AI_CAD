# Ghi chú lỗi khi tạo DXF (để không lặp lại)

## Lỗi 13/10/2026 - đơn 521013-04: file DXF không mở được
- Triệu chứng: CAD hiện "Press ENTER to continue", màn hình đen. Template gốc mở được, file ghép hình thì không.
- Nguyên nhân: khi ghép entity vào Template.dxf, script cắt mất dòng mã nhóm `  0` đứng ngay trước `ENDSEC` của mục ENTITIES. File DXF là các cặp 2 dòng (mã, giá trị); `ENDSEC` là giá trị nên dòng trước nó là mã `0`.
- Sai: `out = L[:i+1] + entity + L[j:]`
- Đúng: `out = L[:i+1] + entity + L[j-1:]` (i = vị trí `ENTITIES`, j = vị trí `ENDSEC` sau đó).

## Kiểm tra bắt buộc trước khi giao file
1. Đọc cả file theo từng cặp 2 dòng, dòng mã luôn là số nguyên.
2. Từ `0/ENDSEC` cuối ENTITIES đến hết file phải trùng khớp từng dòng với mẫu (`mau[j-1:] == ra[l-1:]`).
3. Chỉ được khác mẫu ở EXTMAX, HANDSEED, VPORT `*Active`.
4. Không có số dạng `1e-05`, `nan`, `inf`.
5. Không tin thông báo "written" khi ghi file về máy người dùng: liệt kê thư mục để xác nhận file có mặt và đúng dung lượng. Nếu thiếu hoặc lệch, gửi file bằng SendUserFile lấy file_uuid rồi commit lại bằng fileUuid.
6. Nếu có thể, chạy thử bằng một trình đọc DXF (ví dụ ezdxf) trước khi giao; nếu không cài được thì làm đủ các bước 1-4.

## Lưu ý khác rút ra từ đơn này
- HANDSEED của Template hiện là 208 và là handle kế tiếp chưa dùng (handle lớn nhất đang dùng là 207). Entity mới bắt đầu từ đúng giá trị HANDSEED.
- Khi người dùng chỉ yêu cầu file ALL thì không tạo file riêng từng mã.
- Lỗi 13/11/2026 - đơn 521111-25, mã 26-067785 (SUS304 t3, uốn 111°): coi kích thước 34 là kích thước ngoài, thực tế đường gióng 34 bắt đầu từ góc trong chỗ uốn 1 nên phôi ngắn 4.16 mm. Phải phóng ≥ 300 dpi đầu đường gióng để xác định trong/ngoài (SKILL.md dòng 106); không chắc thì Flag 7.
