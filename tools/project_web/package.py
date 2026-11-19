# -*- coding: utf-8 -*-
"""package.py - "Đóng gói" các mã đã xong của đơn thành thư mục Gui để gửi đi (có thể gửi nhiều đợt cho cùng một đơn).

Cấu trúc đầu ra (đúng mẫu đơn 521111-01): mỗi đợt là một thư mục con trong Gui
  <thư mục đơn>\\Gui\\<đơn>\\<đơn>.xls              đợt 1: file Excel CAD作業納品書
  <thư mục đơn>\\Gui\\<đơn>\\<đơn>\\26-xxxxxx.dxf     đợt 1: chỉ DXF các mã đợt này (KHÔNG có file ALL)
  <thư mục đơn>\\Gui\\<đơn>(1)\\<đơn>.xls ...           đợt 2 (đợt 3 là <đơn>(2), ...): cùng cấu trúc, không ghi đè đợt trước
File Excel mỗi đợt liệt kê TẤT CẢ mã của đơn (cộng dồn): mã đã gửi ở đợt trước có kích thước, nền trắng; từ đợt 2 mã của đợt này
có kích thước và tô nền xanh lá; mã chưa xong chỉ có số thứ tự + mã, bỏ trống kích thước, tô nền xanh lá cả dòng.
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


def next_batch_dir(order_dir, order):
    """Đợt 1 -> Gui\\<đơn>; đợt 2 -> Gui\\<đơn>(1); đợt 3 -> Gui\\<đơn>(2)... (không bao giờ ghi đè đợt trước).
    Trả (thư mục Gui, thư mục của đợt này, số đợt)."""
    gui = os.path.join(order_dir, 'Gui')
    first = os.path.join(gui, order)
    if not os.path.exists(first):
        return gui, first, 1
    k = 1
    while os.path.exists(os.path.join(gui, '%s(%d)' % (order, k))):
        k += 1
    return gui, os.path.join(gui, '%s(%d)' % (order, k)), k + 1


def packed_size(order_dir, order, code):
    """Kích thước phôi của mã đã đóng gói ở đợt trước, đọc từ DXF trong Gui\\<đơn>, <đơn>(1)... (và Gui_2... của bản cũ). None nếu không còn file."""
    cands = []
    try:
        gui = os.path.join(order_dir, 'Gui')
        if os.path.isdir(gui):
            for d in sorted(os.listdir(gui)):
                cands.append(os.path.join(gui, d, order, code + '.dxf'))
        for d in sorted(os.listdir(order_dir)):
            if re.match(r'^Gui_\d+$', d, re.I):          # bản cũ: Gui_2\<đơn>\<đơn>\<mã>.dxf
                cands.append(os.path.join(order_dir, d, order, order, code + '.dxf'))
        for f in cands:
            if os.path.isfile(f):
                return blank_size(f)
    except (OSError, ValueError):
        pass
    return None


def package(order, order_dir, codes, all_codes=None, done=None, known=None):
    """codes = các mã ĐÃ XONG cần đóng gói đợt này (chuyển DXF vào Gui). Mã chưa có trong danh sách thì không đụng tới.
    File Excel liệt kê TẤT CẢ mã của đơn (all_codes, theo thứ tự đơn): mã đã xong điền kích thước; mã chưa xong
    (không thuộc done) chỉ điền số thứ tự và mã, để trống kích thước và tô nền xanh lá cả dòng (pending=true cho gui_fill.ps1).
    done = tập mã đã xong (đợt này + các đợt trước); known = {mã: (x, y)} kích thước đã lưu của mã đóng gói ở đợt trước.
    Ném ValueError khi thiếu file DXF của một mã trong codes."""
    gui_root, gui, batch = next_batch_dir(order_dir, order)
    files = {m.group(1): f for f in os.listdir(order_dir) if (m := CODE_FILE.match(f))}
    missing = [c for c in codes if c not in files]
    if missing:
        raise ValueError('Thiếu file DXF của mã: ' + ', '.join(missing) + ' trong thư mục đơn (có thể đã được đóng gói ở đợt trước).')
    if not os.path.isfile(TEMPLATE):
        raise ValueError('Thiếu file mẫu Excel: ' + TEMPLATE)
    sizes = {}
    for c in codes:
        sizes[c] = blank_size(os.path.join(order_dir, files[c]))
    before = set(done or ()) - set(codes)          # mã đã gửi ở các đợt trước
    done = before | set(codes)
    rows = []
    for c in list(all_codes or codes):
        if c not in done:
            rows.append({'code': c, 'x': None, 'y': None, 'pending': True, 'current': False})
            continue
        sz = sizes.get(c) or (known or {}).get(c) or packed_size(order_dir, order, c)
        rows.append({'code': c, 'x': sz[0] if sz else None, 'y': sz[1] if sz else None, 'pending': False,
                     'current': bool(before) and c in codes})      # từ đợt 2: mã của đợt này tô xanh (như mẫu 521111-01)
    tmp_root = tempfile.mkdtemp(prefix='ai_cad_gui_')
    try:
        # dựng sẵn trong thư mục tạm, xong hết mới thay vào Gui (lỗi giữa chừng không làm mất Gui cũ)
        stage = os.path.join(tmp_root, os.path.basename(gui))
        inner = os.path.join(stage, order)
        os.makedirs(inner)
        for c in codes:
            shutil.copy2(os.path.join(order_dir, files[c]), os.path.join(inner, files[c]))
        xls = os.path.join(stage, order + '.xls')
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
        os.makedirs(gui_root, exist_ok=True)
        shutil.move(stage, gui)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    # CHUYỂN (không phải chép): chỉ xoá file gốc trong thư mục đơn sau khi mọi file đã nằm đúng chỗ trong Gui, cùng dung lượng
    inner_final = os.path.join(gui, order)
    moved = 0
    for c in codes:
        src, dst = os.path.join(order_dir, files[c]), os.path.join(inner_final, files[c])
        if os.path.isfile(dst) and os.path.isfile(src) and os.path.getsize(dst) == os.path.getsize(src):
            os.remove(src)
            moved += 1
    return {'gui': gui, 'batch': batch, 'excel': os.path.join(gui, order + '.xls'), 'files': len(codes), 'moved': moved, 'rows': rows, 'sizes': sizes}
