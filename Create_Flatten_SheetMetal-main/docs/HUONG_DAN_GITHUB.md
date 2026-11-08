# Đẩy repo lên GitHub (làm khi đã chốt tên và chế độ private/public)

Máy đã có Git. Chưa có GitHub CLI (`gh`), nên có hai cách.

## Cách A: GitHub CLI (gọn nhất)
1. Cài: `winget install --id GitHub.cli`, mở lại terminal.
2. Đăng nhập: `gh auth login` (chọn GitHub.com, HTTPS, đăng nhập bằng trình duyệt).
3. Trong thư mục repo: `gh repo create <tên-repo> --private --source . --remote origin --push`

## Cách B: tạo repo trên web
1. Vào github.com, New repository, đặt tên, chọn Private, không tích Add README.
2. Trong thư mục repo:
```
git remote add origin https://github.com/<tài-khoản>/<tên-repo>.git
git branch -M main
git push -u origin main
```
Lần đầu Git mở cửa sổ đăng nhập GitHub; đăng nhập là xong.

## Trước khi push
- Chạy `git status` và `git ls-files` xem lại, đảm bảo không có PDF/DXF/DWG của khách.
- Đặt tên người commit nếu chưa có: `git config --global user.name "..."` và `git config --global user.email "..."`.
