# -*- coding: utf-8 -*-
"""package.py - "Đóng gói" các mã đã xong của đơn thành thư mục Gui để gửi đi (có thể gửi nhiều đợt cho cùng một đơn).

Cấu trúc đầu ra của MỖI ĐỢT (đúng mẫu người dùng đã lưu ở 521106-24):
  <thư mục đơn>\\Gui\\<đơn>\\<đơn>.xls             file Excel CAD作業納品書 đã điền số đơn và kích thước phôi các mã của đợt này
  <thư mục đơn>\\Gui\\<đơn>\\<đơn>\\26-xxxxxx.dxf    chỉ các file DXF của các mã đợt này (KHÔNG có file ALL)
Đợt 1 vào Gui, đợt 2 vào Gui_2, đợt 3 vào Gui_3... (mỗi đợt tự đủ, không ghi đè đợt trước; file Excel chỉ liệt kê mã của đợt đó).
CHUYỂN các file DXF vào Gui (sau khi đóng gói không còn ở thư mục đơn); file chỉ bị xoá khỏi thư mục đơn khi bản trong Gui đã đủ và cùng dung lượng.
Kích thước phôi lấy từ chính file DXF (khung bao của hình), X = chiều ngang, Y = chiều cao.
File Excel điền bằng Microsoft Excel chạy ẩn (gui_fill.ps1) trên mẫu templates\\Gui_mau.xls.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, 'templates', 'Gui_mau.xls')
PS1 = os.path.join(HERE, 'gui_fill.ps1')
CODE_FILE = re.compile(r'^(26-\d{6})\.dxf$', re.I)


def _powershell():
    """Đường dẫn đầy đủ của Windows PowerShell (không phụ thuộc PATH)."""
    p = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    return p if os.path.isfile(p) else 'powershell'


def blank_size(path):
    import compare_dxf
    s = compare_dxf.signature(path)
    if not s:
        raise ValueError('Không đọc được hình trong ' + os.path.basename(path))
    return round(s['w'], 2), round(s['h'], 2)


def next_gui_dir(order_dir):
    """Đợt 1 -> Gui; các đợt sau -> Gui_2, Gui_3... (không bao giờ ghi đè đợt trước). Trả (đường dẫn, số đợt)."""
    gui = os.path.join(order_dir, 'Gui')
    if not os.path.exists(gui):
        return gui, 1
    n = 2
    while os.path.exists(os.path.join(order_dir, 'Gui_%d' % n)):
        n += 1
    return os.path.join(order_dir, 'Gui_%d' % n), n


def package(order, order_dir, codes):
    """codes = các mã ĐÃ XONG cần đóng gói đợt này, theo thứ tự Excel. Mã chưa có trong danh sách thì không đụng tới.
    Ném ValueError khi thiếu file DXF của một mã trong codes."""
    gui, batch = next_gui_dir(order_dir)
    files = {m.group(1): f for f in os.listdir(order_dir) if (m := CODE_FILE.match(f))}
    missing = [c for c in codes if c not in files]
    if missing:
        raise ValueError('Thiếu file DXF của mã: ' + ', '.join(missing) + ' trong thư mục đơn (có thể đã được đóng gói ở đợt trước).')
    if not os.path.isfile(TEMPLATE):
        raise ValueError('Thiếu file mẫu Excel: ' + TEMPLATE)
    rows = []
    for c in codes:
        x, y = blank_size(os.path.join(order_dir, files[c]))
        rows.append({'code': c, 'x': x, 'y': y})
    tmp_root = tempfile.mkdtemp(prefix='ai_cad_gui_')
    try:
        # dựng sẵn trong thư mục tạm, xong hết mới thay vào Gui (lỗi giữa chừng không làm mất Gui cũ)
        stage = os.path.join(tmp_root, 'Gui')
        inner = os.path.join(stage, order, order)
        os.makedirs(inner)
        for c in codes:
            shutil.copy2(os.path.join(order_dir, files[c]), os.path.join(inner, files[c]))
        xls = os.path.join(stage, order, order + '.xls')
        job = os.path.join(tmp_root, 'job.json')
        with open(job, 'w', encoding='utf-8') as f:
            json.dump({'template': TEMPLATE, 'out': xls, 'order': order, 'rows': rows}, f, ensure_ascii=False)
        for attempt in (1, 2):      # Excel đôi khi từ chối mở lần đầu (bảo vệ file / khởi động chậm): thử lại một lần
            r = subprocess.run([_powershell(), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', PS1, '-Job', job],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
            if r.returncode == 0 and os.path.isfile(xls):
                break
            time.sleep(3)
        if r.returncode != 0 or not os.path.isfile(xls):
            raise ValueError('Không điền được file Excel (cần Microsoft Excel): ' + (r.stderr or r.stdout or '').strip()[:300])
        if os.path.exists(gui):      # hiếm: thư mục này vừa được tạo trong lúc đang đóng gói -> dừng, không ghi đè
            raise ValueError('Thư mục ' + gui + ' vừa xuất hiện, hãy bấm Đóng gói lại.')
        shutil.move(stage, gui)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    # CHUYỂN (không phải chép): chỉ xoá file gốc trong thư mục đơn sau khi mọi file đã nằm đúng chỗ trong Gui, cùng dung lượng
    inner_final = os.path.join(gui, order, order)
    moved = 0
    for c in codes:
        src, dst = os.path.join(order_dir, files[c]), os.path.join(inner_final, files[c])
        if os.path.isfile(dst) and os.path.isfile(src) and os.path.getsize(dst) == os.path.getsize(src):
            os.remove(src)
            moved += 1
    return {'gui': gui, 'batch': batch, 'excel': os.path.join(gui, order, order + '.xls'), 'files': len(codes), 'moved': moved, 'rows': rows}
