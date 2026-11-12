# -*- coding: utf-8 -*-
"""Quản lý Project AI_CAD: tiến độ agent + đánh giá hiệu quả AI.

Chạy: py server.py  (hoặc start.bat) -> http://localhost:8780
Chỉ dùng thư viện chuẩn của Python.
"""
import json
import os
import re
import shutil
import sys
import threading
import time
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))          # ...\AI_CAD
WORK = os.environ.get('AI_WORK', os.path.join(ROOT, 'AI_Work'))
STATIC = os.path.join(HERE, 'static')
DATA = os.path.join(HERE, 'data')
REVIEWS = os.path.join(DATA, 'reviews.json')      # Đúng/Sai của người dùng (bền vững)
PROGRESS = os.path.join(DATA, 'progress.json')    # agent ghi tiến độ vào đây
PORT = int(os.environ.get('PORT', '8780'))
ACTIVE_MIN = 30          # thư mục có file mới trong 30 phút -> coi là đang làm
LOST_MIN = 10            # heartbeat cũ hơn 10 phút -> mất tín hiệu

ORDER_RE = re.compile(r'^(\d{6}-\d{2})')
DATE_RE = re.compile(r'^(\d{2})-(\d{2})-(\d{4})$')
CODE_RE = re.compile(r'^\d{2}-\d{6}$')
LEGACY_RE = re.compile(r'^(\d+)T-?(\d+)F$', re.I)
REF_DIR = 'Tham_Khao'     # <thư mục đơn>\Tham_Khao\<mã>\ = PDF/DXF tham khảo người dùng nạp cho agent làm tiếp (không phải Output, không tính vào đơn)
REF_EXT = ('.pdf', '.dxf')
REF_MAX = 25 * 1024 * 1024
PACK_RE = re.compile(r'^Gui(?:_\d+)?[\\/]', re.I)      # DXF đã chuyển vào Gui (đợt 1), Gui_2 (đợt 2)...
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
lock = threading.Lock()


# ---------- tiện ích ----------
def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if ts else None


def load_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# ---------- đọc CAD依頼書 (.xlsx) ----------
_xlsx_cache = {}


def read_request(path):
    """Trả về danh sách mã theo thứ tự + khách/vật liệu/độ dày/kích thước."""
    try:
        mt = os.path.getmtime(path)
    except OSError:
        return []
    hit = _xlsx_cache.get(path)
    if hit and hit[0] == mt:
        return hit[1]
    items = []
    try:
        z = zipfile.ZipFile(path)
        ss = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si'):
                ss.append(''.join(t.text or '' for t in si.iter(NS + 't')))
        sheet = 'xl/worksheets/sheet1.xml'
        if sheet not in z.namelist():
            sheet = next(n for n in z.namelist() if n.startswith('xl/worksheets/sheet'))
        rows = []
        for r in ET.fromstring(z.read(sheet)).iter(NS + 'row'):
            cells = {}
            for c in r.iter(NS + 'c'):
                v = c.find(NS + 'v')
                t = c.get('t')
                val = None
                if t == 's' and v is not None:
                    val = ss[int(v.text)]
                elif t == 'inlineStr':
                    val = ''.join(x.text or '' for x in c.iter(NS + 't'))
                elif v is not None:
                    val = v.text
                if val not in (None, ''):
                    cells[re.sub(r'\d', '', c.get('r', ''))] = str(val).strip()
            rows.append(cells)
        hdr = {}
        for cells in rows:
            if '作業No.' in cells.values():
                hdr = {v: k for k, v in cells.items()}
                break
        ccode = hdr.get('作業No.', 'D')
        for cells in rows:
            code = cells.get(ccode, '')
            if not CODE_RE.match(code):
                continue
            def num(col):
                try:
                    return round(float(cells.get(col, '')), 2)
                except ValueError:
                    return None
            items.append({
                'code': code,
                'customer': cells.get('H', ''),
                'urgent': cells.get('F', ''),
                'material': cells.get('J', ''),
                'thick': num('K'),
                'x': num('L'), 'y': num('M'),
            })
    except Exception:
        items = []
    _xlsx_cache[path] = (mt, items)
    return items


# ---------- quét AI_Work ----------
def scan_orders():
    """Mỗi đơn: thư mục <số đơn> hoặc các file <số đơn>* để rời trong thư mục ngày."""
    found = {}
    for dirpath, dirnames, filenames in os.walk(WORK):
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != COMPARE_DIR]   # So_Sanh = phương án đã lưu, không phải đơn
        base = os.path.basename(dirpath)
        m = ORDER_RE.match(base)
        if m and base == m.group(1):
            found.setdefault(base, {'dir': dirpath, 'loose': False})
            dirnames[:] = []           # file con (review/, Can_Check/) tính trong đơn
            continue
        if DATE_RE.match(base):
            for fn in filenames:
                mm = ORDER_RE.match(fn)
                if mm and mm.group(1) not in found:
                    found[mm.group(1)] = {'dir': dirpath, 'loose': True}
    return found


def order_date(order, d):
    for part in reversed(os.path.normpath(d).split(os.sep)):
        m = DATE_RE.match(part)
        if m:
            return f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    return f'2026-{order[2:4]}-{order[4:6]}'


def order_files(order, info):
    out = []
    if info['loose']:
        for fn in os.listdir(info['dir']):
            p = os.path.join(info['dir'], fn)
            if fn.startswith(order) and os.path.isfile(p):
                out.append((fn, p))
    else:
        for dp, dns, fns in os.walk(info['dir']):
            dns[:] = [d for d in dns if d != REF_DIR]
            for fn in fns:
                out.append((os.path.relpath(os.path.join(dp, fn), info['dir']), os.path.join(dp, fn)))
    return out


def norm_flags(f):
    """flags phải là list chuỗi; agent đôi khi gửi chuỗi '[1. ...]' (thiếu nháy JSON) -> gói lại thành 1 mục."""
    if not f:
        return []
    if isinstance(f, str):
        try:
            f = json.loads(f)
        except ValueError:
            s = f.strip()
            if s.startswith('[') and s.endswith(']'):
                s = s[1:-1].strip()
            return [s] if s else []
    if isinstance(f, list):
        return [str(x) for x in f if str(x).strip()]
    return [str(f)]


def _ref_path(info, code):
    if not info or info.get('loose') or not CODE_RE.match(code or ''):
        return None
    return os.path.join(info['dir'], REF_DIR, code)


def list_refs(info, code):
    d = _ref_path(info, code)
    try:
        return sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))) if d and os.path.isdir(d) else []
    except OSError:
        return []


def _safe_name(name):
    n = os.path.basename(str(name or '').replace('\\', '/')).strip()
    n = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', n)
    return n[:100]


def add_ref(order, code, name, b64):
    """Người dùng nạp PDF/DXF tham khảo cho một mã: lưu vào <thư mục đơn>\\Tham_Khao\\<mã>\\ (không đụng file đầu vào/Output)."""
    import base64
    import binascii
    info = scan_orders().get(order or '')
    d = _ref_path(info, code)
    if not d:
        raise ValueError('Không tìm thấy thư mục đơn hoặc mã không hợp lệ.')
    n = _safe_name(name)
    if not n.lower().endswith(REF_EXT):
        raise ValueError('Chỉ nhận file PDF hoặc DXF.')
    try:
        raw = base64.b64decode(b64 or '', validate=False)
    except (binascii.Error, ValueError):
        raise ValueError('Dữ liệu file không hợp lệ.')
    if not raw or len(raw) > REF_MAX:
        raise ValueError('File rỗng hoặc lớn hơn 25 MB.')
    os.makedirs(d, exist_ok=True)
    if n not in os.listdir(d) and len(os.listdir(d)) >= 10:
        raise ValueError('Mỗi mã tối đa 10 file tham khảo, hãy xoá bớt.')
    with open(os.path.join(d, n), 'wb') as f:
        f.write(raw)
    _cache['t'] = 0
    return n


def del_ref(order, code, name):
    info = scan_orders().get(order or '')
    d = _ref_path(info, code)
    n = _safe_name(name)
    fp = os.path.join(d, n) if d and n else None
    if not fp or not os.path.isfile(fp):
        raise ValueError('Không thấy file tham khảo này.')
    os.remove(fp)
    for dd in (d, os.path.dirname(d)):       # thư mục mã rồi thư mục Tham_Khao rỗng thì dọn luôn
        try:
            os.rmdir(dd)
        except OSError:
            break
    _cache['t'] = 0


def build_order(order, info, prog):
    files = order_files(order, info)
    pdf = xlsx = None
    all_dxf = None
    parts = []
    legacy = None
    tin, tlast = [], 0
    for rel, p in files:
        low = rel.lower()
        name = os.path.basename(rel)
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if not PACK_RE.match(rel):      # file trong Gui/Gui_N do đóng gói tạo ra, không tính là agent đang làm
            tlast = max(tlast, mt)
        stem, ext = os.path.splitext(name)
        if ext.lower() == '.pdf' and stem == order:
            pdf = rel; tin.append(mt)
        elif ext.lower() == '.xlsx' and '依頼' in name:
            xlsx = p; tin.append(mt)
        elif ext.lower() == '.dxf':
            if stem.upper() == f'{order}_ALL'.upper():
                all_dxf = (rel, mt)
            elif '_ALL' in stem.upper() or 'review' in low or 'can_check' in low:
                pass
            else:
                parts.append((rel, mt))
        elif ext.lower() == '.txt' and LEGACY_RE.match(stem):
            m = LEGACY_RE.match(stem)
            legacy = {'ok': int(m.group(1)), 'ng': int(m.group(2))}
    req = read_request(xlsx) if xlsx else []
    codes = [r['code'] for r in req]
    meta = req[0] if req else {}
    p_order = prog.get('orders', {}).get(order, {})
    p_agents = {k: v for k, v in prog.get('agents', {}).items() if v.get('order') == order}
    if not codes and p_order.get('partOrder'):
        codes = list(p_order['partOrder'])
    # tiến độ từng mã do agent báo: chuẩn hoá mã viết tắt (066376 -> 26-066376) và flags sai định dạng
    p_parts = {}
    for k, v in prog.get('parts', {}).items():
        if not k.startswith(order + '_'):
            continue
        c = k.split('_', 1)[1]
        if c not in codes:
            c = next((x for x in codes if x.endswith('-' + c)), c)
        merged = dict(p_parts.get(c, {}))
        merged.update(v)
        merged['flags'] = norm_flags(v['flags']) if 'flags' in v else norm_flags(merged.get('flags'))
        p_parts[c] = merged
    for c in p_parts:
        if c not in codes:
            codes.append(c)
    for a in p_agents.values():
        for c in a.get('codes') or []:
            if c not in codes:
                codes.append(c)
    # DXF lẻ chỉ tính là Output khi tên file chứa mã của đơn (vd 26-066286.dxf); DXF đầu vào của khách (vd 2.DXF) bỏ qua
    parts = [(rel, mt) for rel, mt in parts
             if any(c in rel or c.split('-')[-1] in os.path.basename(rel) for c in codes)]

    now = time.time()
    running = any(a.get('state') == 'running' and not lost(a, now) for a in p_agents.values())
    failed = any(a.get('state') == 'failed' for a in p_agents.values())
    flags = []
    code_rows = []
    for c in codes:
        pp = p_parts.get(c, {})
        st = pp.get('status')
        manual = bool(pp.get('manual'))
        # "Preview OK": người dùng xác nhận hình dựng hiện tại đã đúng -> mã tính là xong, bỏ Flag, không cần check lại.
        # Mất hiệu lực nếu agent dựng lại mã sau lúc bấm (finishedAt mới hơn previewOkAt).
        pok = bool(pp.get('previewOk')) and not manual and st == 'built' and (pp.get('finishedAt') or '') <= (pp.get('previewOkAt') or '')
        # file DXF của mã: DXF lẻ có tên chứa mã (đầy đủ hoặc 6 số cuối); không có thì mã nằm trong file <số đơn>_ALL.dxf
        cands = [rel for rel, _ in parts if c in rel or c.split('-')[-1] in os.path.basename(rel)]
        top = next((r for r in cands if not PACK_RE.match(r)), None)        # DXF còn ở thư mục đơn (chưa đóng gói)
        packed = any(PACK_RE.match(r) for r in cands) or bool(pp.get('packedAt'))   # đã đóng gói ít nhất một đợt (kể cả khi bạn đã dời thư mục Gui đi)
        d_rel = top or (cands[0] if cands else None)
        d_kind = 'part' if d_rel else ('all' if all_dxf else None)
        d_rel = d_rel or (all_dxf[0] if all_dxf else None)
        if manual:
            s = 'tay'                      # người dùng tự làm mã này, không chờ agent
        elif st == 'built' and not d_rel and not pp.get('packedAt'):
            s = 'thieu'                    # agent báo xong nhưng KHÔNG thấy file DXF nào trong thư mục đơn
        elif st == 'built':
            s = 'cho' if pp.get('flags') and not pok else 'xong'
        elif st == 'running':
            s = 'dang'
        elif all_dxf:
            s = 'xong'
        else:
            s = 'chua'
        if pp.get('flags') and not manual and not pok:
            flags += [f'{c}: {f}' for f in pp['flags']]
        if s == 'thieu':
            flags.append(f'{c}: không thấy file DXF trong thư mục đơn (agent đã báo xong)')
        r = next((x for x in req if x['code'] == c), {})
        code_rows.append({'code': c, 'state': s, 'pstatus': st, 'level': pp.get('level'),
                          'dxf': os.path.join(info['dir'], d_rel) if d_rel else None, 'dxfKind': d_kind,
                          'manual': manual, 'manualAt': pp.get('manualAt'),
                          'previewOk': pok, 'previewOkAt': pp.get('previewOkAt') if pok else None,
                          'packed': packed,
                          # sẵn sàng đóng gói = mã đã xong (không Flag, không tự làm) và file 26-xxxxxx.dxf đang nằm ở thư mục đơn
                          'ready': s == 'xong' and not manual and top is not None and top.lower() == (c + '.dxf').lower(),
                          'kind': pp.get('kind'), 'blank': pp.get('blank'),
                          'agent': pp.get('agent'), 'startedAt': pp.get('startedAt'),
                          'finishedAt': pp.get('finishedAt'), 'flags': [] if pok else (pp.get('flags') or []), 'flagsOrig': pp.get('flags') or [],
                          'thick': r.get('thick'), 'material': r.get('material'),
                          'size': f"{r.get('x')} x {r.get('y')}" if r.get('x') is not None else None})

    # file tham khảo người dùng đã nạp cho từng mã
    for r in code_rows:
        r['refs'] = list_refs(info, r['code'])

    # trạng thái đơn
    if running:
        state = 'dang'
    elif flags or failed:
        state = 'cho'
    elif all_dxf:
        state = 'xong'
    elif any(r['manual'] for r in code_rows) and all(r['state'] in ('xong', 'tay') for r in code_rows):
        state = 'xong'
    elif parts or p_parts:
        state = 'dang' if now - tlast < ACTIVE_MIN * 60 else 'cho'
    else:
        state = 'chua'

    started = p_order.get('receivedAt') or min((a.get('startedAt') for a in p_agents.values() if a.get('startedAt')), default=None)
    finished = p_order.get('mergedAt') or (iso(all_dxf[1]) if all_dxf else None)
    est = False        # giờ bắt đầu chỉ lấy từ lúc agent chạy (Giao việc); không ước tính theo giờ lưu file đầu vào
    n_done = sum(1 for r in code_rows if r['state'] in ('xong', 'tay'))
    if not codes and parts:
        n_done = len(parts)
    # các lần agent chính THỰC SỰ làm (lần đầu + các lần làm tiếp); khoảng chờ người dùng ở giữa không tính
    runs = []
    mainag = p_agents.get(order + '_main')
    if mainag and mainag.get('startedAt'):
        for h in mainag.get('history') or []:
            if h.get('startedAt') and h.get('finishedAt'):
                runs.append({'s': h['startedAt'], 'e': h['finishedAt']})
        live = mainag.get('state') == 'running' and not lost(mainag, now)
        runs.append({'s': mainag['startedAt'], 'e': None if live else (mainag.get('finishedAt') or mainag.get('heartbeatAt'))})
    return {
        'order': order,
        'runs': runs,
        'date': order_date(order, info['dir']),
        'customer': p_order.get('customer') or meta.get('customer', ''),
        'material': p_order.get('material') or meta.get('material', ''),
        'urgent': meta.get('urgent', ''),
        'user': p_order.get('user', ''),
        'path': os.path.relpath(info['dir'], WORK).replace(os.sep, '\\') if info['dir'] != WORK else '',
        'state': state,
        'codes': code_rows,
        'total': len(codes) or len(parts),
        'done': n_done,
        'partFiles': len(parts),
        'running': running,
        'packReady': sum(1 for r in code_rows if r['ready']),
        'packed': sum(1 for r in code_rows if r['packed']),
        'hasAll': bool(all_dxf),
        'pdf': bool(pdf),
        'startedAt': started,
        'finishedAt': finished if state == 'xong' else None,
        'lastFileAt': iso(tlast),
        'timeEstimated': est,
        'flags': flags,
        'legacy': legacy,
        'agents': sorted(p_agents.keys()),
    }


def lost(a, now=None):
    hb = a.get('heartbeatAt') or a.get('startedAt')
    if not hb:
        return True
    try:
        t = datetime.strptime(hb, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return False
    return (now or time.time()) - t > LOST_MIN * 60


_cache = {'t': 0, 'data': None}


def snapshot(force=False):
    with lock:
        if not force and _cache['data'] and time.time() - _cache['t'] < 5:
            return _cache['data']
        prog = load_json(PROGRESS, {})
        found = scan_orders()
        # đơn không còn thư mục trong AI_Work (bị xoá/chuyển đi) thì không hiện: không đơn, không thẻ agent, không thông báo cũ (dữ liệu trong progress.json giữ nguyên)
        orders = [build_order(o, i, prog) for o, i in found.items()]
        orders.sort(key=lambda x: (x['date'], x['order']), reverse=True)
        now = time.time()
        agents = []
        for k, a in prog.get('agents', {}).items():
            if a.get('demo') or (a.get('order') and a['order'] not in found):
                continue
            a = dict(a, id=k)
            if a.get('state') == 'running' and lost(a, now):
                a['lost'] = True
            agents.append(a)
        agents.sort(key=lambda a: (a.get('state') != 'running', a.get('startedAt') or ''), reverse=False)
        jobs = [dict(j, id=k) for k, j in prog.get('jobs', {}).items()
                if not (j.get('order') and j['order'] not in found and j.get('status') not in ('moi', 'nhan'))]   # việc đang chờ/đang chạy luôn hiện (thư mục đơn có thể chưa chép vào AI_Work)
        jobs.sort(key=lambda j: j.get('at', ''), reverse=True)
        rn = sys.modules.get('runner')
        data = {'orders': orders, 'agents': agents, 'jobs': jobs[:50], 'generatedAt': now_iso(),
                'runner': rn.status() if rn else {'cli': False},
                'work': os.path.basename(WORK), 'workPath': WORK, 'progressFile': os.path.exists(PROGRESS)}
        _cache.update(t=time.time(), data=data)
        return data


# ---------- ghi tiến độ (agent gọi) ----------
COMPARE_DIR = 'So_Sanh'     # AI_Work\So_Sanh\<đơn>\<A_ngày giờ>\ = Output của từng phương án đã lưu
INPUT_EXT = ('.pdf', '.xlsx', '.xls', '.dwg', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp')   # file đầu vào, không phải Output
PLAN_AGENTS = ('main', 'S1', 'S2')     # Agent chính + tối đa 2 subagent
MODELS = ('opus', 'sonnet')


def _check_order_dir(path):
    """Kiểm thư mục đơn người dùng dán -> (đường dẫn, số đơn, danh sách file, số PDF, số xlsx)."""
    p = (path or '').strip().strip('"').strip("'").strip()
    if not p:
        raise ValueError('Chưa dán đường dẫn thư mục đơn.')
    if '..' in p.replace('\\', '/').split('/'):
        raise ValueError('Đường dẫn không được chứa "..".')
    if not (re.match(r'^[A-Za-z]:[\\/]', p) or p.startswith('\\\\')):
        raise ValueError('Cần đường dẫn đầy đủ, vd C:\\...\\521106-26 hoặc \\\\may\\...\\521106-26.')
    if not os.path.isdir(p):
        raise ValueError('Không thấy thư mục này (kiểm tra lại đường dẫn hoặc ổ mạng).')
    base = os.path.basename(p.rstrip('\\/'))
    m = ORDER_RE.match(base)
    files = os.listdir(p)
    if not m:
        m = next((ORDER_RE.match(f) for f in files if ORDER_RE.match(f)), None)
    order = m.group(1) if m else ''
    npdf = sum(1 for f in files if f.lower().endswith('.pdf'))
    nxls = sum(1 for f in files if f.lower().endswith(('.xlsx', '.xls')))
    if not npdf and not nxls:
        raise ValueError('Thư mục không có file PDF hay xlsx nào.')
    return p, order, files, npdf, nxls


def _codes_in_dir(p, files):
    """Danh sách mã đọc từ file 依頼.xlsx trong thư mục đơn (rỗng nếu không có)."""
    x = next((f for f in files if f.lower().endswith('.xlsx') and '依頼' in f), None)
    out = []
    for r in (read_request(os.path.join(p, x)) if x else []):
        out.append({'code': r['code'], 'thick': r.get('thick'), 'material': r.get('material', ''),
                    'size': f"{r['x']} x {r['y']}" if r.get('x') is not None else ''})
    return out


def preview_job(path):
    """Bước 1 của Giao việc: đọc đơn để người dùng phân công mã cho agent/model trước khi giao."""
    p, order, files, npdf, nxls = _check_order_dir(path)
    prog = load_json(PROGRESS, {})
    dup = any(j.get('path') == p and j.get('status') in ('moi', 'nhan') for j in prog.get('jobs', {}).values())
    return {'path': p, 'order': order, 'pdf': npdf, 'xlsx': nxls, 'codes': _codes_in_dir(p, files), 'dup': dup}


def _check_plan(plan, codes):
    """plan = {agents: {main|S1|S2|S3: opus|sonnet}, codes: {mã: main|S1|S2|S3}} -> bản đã kiểm."""
    if not isinstance(plan, dict):
        raise ValueError('Bảng phân công không hợp lệ.')
    ag = {a: str(m).lower() for a, m in (plan.get('agents') or {}).items()}
    asg = {str(c): str(a) for c, a in (plan.get('codes') or {}).items()}
    for a, m in ag.items():
        if a not in PLAN_AGENTS or m not in MODELS:
            raise ValueError('Agent chỉ có Agent chính, Subagent 1 và Subagent 2; model chỉ có Opus hoặc Sonnet.')
    ag.setdefault('main', 'opus')
    known = {c['code'] for c in codes}
    for c, a in asg.items():
        if known and c not in known:
            raise ValueError('Mã không có trong đơn: ' + c)
        if a not in ag:
            raise ValueError(f'Mã {c} được giao cho agent chưa chọn model.')
    miss = [c for c in known if c not in asg]
    if miss:
        raise ValueError('Còn mã chưa giao cho agent nào: ' + ', '.join(sorted(miss)))
    used = {a for a in asg.values()}
    ag = {a: m for a, m in ag.items() if a == 'main' or a in used}   # bỏ subagent không nhận mã nào
    return {'agents': ag, 'codes': asg}


def add_job(path, subagents=0, note='', model='', plan=None):
    """Người dùng dán thư mục đơn (+ bảng phân công) -> việc chờ agent nhận (collection jobs)."""
    p, order, files, npdf, nxls = _check_order_dir(path)
    if plan is not None:
        plan = _check_plan(plan, _codes_in_dir(p, files))
        n = sum(1 for a in plan['agents'] if a != 'main')
        model = plan['agents']['main']
    else:
        try:
            n = int(subagents)
        except (TypeError, ValueError):
            n = 0
        if not 0 <= n <= 10:
            raise ValueError('Số subagent từ 0 (agent chính, không dùng subagent) đến 10.')
        model = (model or '').strip().lower()
        if model not in ('',) + MODELS:
            raise ValueError('Model chỉ có Opus hoặc Sonnet.')
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        for j in jobs.values():
            if j.get('path') == p and j.get('status') in ('moi', 'nhan'):
                raise ValueError('Đơn này đã có trong hàng đợi.')
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + (('_' + order) if order else '')
        jobs[jid] = {'path': p, 'order': order, 'subagents': n, 'model': model, 'note': (note or '')[:500],
                     'pdf': npdf, 'xlsx': nxls, 'status': 'moi', 'at': now_iso(), 'ui': True}
        if plan is not None:
            jobs[jid]['plan'] = plan
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


def add_followup(order, answers, model=''):
    """Người dùng trả lời Flag trong khung chi tiết đơn -> việc 'làm tiếp': chỉ vẽ lại các mã được trả lời."""
    if not isinstance(answers, dict):
        raise ValueError('Dữ liệu trả lời không hợp lệ.')
    answers = {str(c).strip(): str(t).strip()[:1000] for c, t in answers.items()}     # mã chỉ có file tham khảo (không ghi chú) vẫn giữ, lọc bên dưới
    model = (model or '').strip().lower()
    if model not in ('', 'opus', 'sonnet'):
        raise ValueError('Model chỉ có Opus hoặc Sonnet.')
    o = next((x for x in snapshot(True)['orders'] if x['order'] == order), None)
    if not o:
        raise ValueError('Không thấy đơn này.')
    codes = {c['code'] for c in o['codes']}
    bad = [c for c in answers if c not in codes]
    if bad:
        raise ValueError('Mã không thuộc đơn: ' + ', '.join(bad))
    p = os.path.join(WORK, o['path']) if o.get('path') else ''
    if not p or not os.path.isdir(p):
        raise ValueError('Không tìm thấy thư mục đơn trong AI_Work.')
    refs = {}
    for c in o['codes']:
        if c['code'] in answers and c.get('refs'):
            refs[c['code']] = [os.path.join(p, REF_DIR, c['code'], f) for f in c['refs']]
    answers = {c: (t or '(không ghi chú, chỉ có file tham khảo đính kèm)') for c, t in answers.items() if t or c in refs}
    if not answers:
        raise ValueError('Chưa nhập thông tin bổ sung cho mã nào.')
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        for j in jobs.values():
            if j.get('order') == order and j.get('kind') == 'tiep' and j.get('status') in ('moi', 'nhan'):
                raise ValueError('Đơn này đã có việc làm tiếp đang chờ hoặc đang chạy.')
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + order + '_tiep'
        jobs[jid] = {'kind': 'tiep', 'path': p, 'order': order, 'subagents': 0, 'model': model, 'note': '', 'answers': answers,
                     'refs': refs, 'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


def _ts(iso):
    try:
        return datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def archive_order(order):
    """Lưu phương án: chép Output của đơn ra AI_Work\\So_Sanh\\<đơn>\\<nhãn>\\ kèm số liệu, rồi dọn đơn để chạy phương án khác.
    Chỉ xoá file Output (không phải PDF/xlsx/dwg đầu vào) và chỉ sau khi chép xong, đúng dung lượng."""
    if not ORDER_RE.match(order or ''):
        raise ValueError('Số đơn không hợp lệ.')
    snap = snapshot(True)
    o = next((x for x in snap['orders'] if x['order'] == order), None)
    info = scan_orders().get(order)
    if not o or not info:
        raise ValueError('Không thấy đơn này.')
    if o['state'] == 'dang' or any(a.get('state') == 'running' and not a.get('lost') for a in snap['agents'] if a.get('order') == order):
        raise ValueError('Đơn đang chạy, chờ agent xong rồi hãy lưu phương án.')
    prog = load_json(PROGRESS, {})
    starts = []
    for a in prog.get('agents', {}).values():
        if a.get('order') == order:
            starts += [h.get('startedAt') for h in a.get('history') or []] + [a.get('startedAt')]
    for j in prog.get('jobs', {}).values():
        if j.get('order') == order:
            starts.append(j.get('nhanAt'))
    ts = [t for t in map(_ts, starts) if t]
    if not ts:
        raise ValueError('Đơn này chưa có lần chạy nào của agent để lưu.')
    t0 = min(ts) - 120
    outs = []
    for rel, fp in order_files(order, info):
        try:
            if not rel.lower().endswith(INPUT_EXT) and os.path.getmtime(fp) >= t0:
                outs.append((rel, fp))
        except OSError:
            pass
    if not outs:
        raise ValueError('Không có file Output nào để lưu (chưa có DXF do agent tạo).')
    root = os.path.join(WORK, COMPARE_DIR, order)
    n = len([d for d in os.listdir(root)]) if os.path.isdir(root) else 0
    label = chr(65 + n % 26) + ('' if n < 26 else str(n // 26))
    dest = os.path.join(root, f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    rv = load_json(REVIEWS, {})
    revs = {k.split('_', 1)[1]: v for k, v in rv.items() if k.startswith(order + '_')}
    jp = [j for j in prog.get('jobs', {}).values() if j.get('order') == order and (j.get('plan') or j.get('model') is not None)]
    jp.sort(key=lambda j: j.get('at', ''))
    last = jp[-1] if jp else {}
    rows = [{'code': c['code'], 'state': c['state'], 'flags': len(c['flags']),
             'review': (revs.get(c['code']) or {}).get('status', 'cho')} for c in o['codes']]
    secs = sum(max(0, (_ts(r['e']) or time.time()) - (_ts(r['s']) or 0)) for r in o.get('runs') or [] if _ts(r['s']))
    us = [j.get('usage') for j in prog.get('jobs', {}).values() if j.get('order') == order and j.get('usage') and (_ts(j.get('at')) or 0) >= t0]
    usage = {k: sum(u.get(k, 0) for u in us) for k in ('costUSD', 'input', 'output', 'thinking', 'cacheRead', 'cacheWrite', 'calls_main', 'calls_sub', 'images', 'denials')} if us else None
    rec = {'order': order, 'label': label, 'savedAt': now_iso(), 'usage': usage, 'plan': last.get('plan'), 'model': last.get('model'),
           'subagents': last.get('subagents'), 'seconds': round(secs), 'runs': len(o.get('runs') or []),
           'codes': len(o['codes']), 'done': o['done'], 'flags': sum(r['flags'] for r in rows),
           'review': {k: sum(1 for r in rows if r['review'] == k) for k in ('dung', 'sai', 'cho')},
           'rows': rows, 'files': len(outs), 'dest': os.path.relpath(dest, WORK)}
    try:
        for rel, fp in outs:
            dp = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(fp, dp)
            if os.path.getsize(dp) != os.path.getsize(fp):
                raise OSError('Chép lệch dung lượng: ' + rel)
        with open(os.path.join(dest, 'ketqua.json'), 'w', encoding='utf-8') as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
    except Exception as e:
        shutil.rmtree(dest, ignore_errors=True)          # chép lỗi: không xoá gì ở đơn
        raise ValueError('Không lưu được phương án (đơn giữ nguyên): ' + str(e))
    # đã chép đủ -> dọn đơn
    for rel, fp in outs:
        try:
            os.remove(fp)
        except OSError:
            pass
    if not info['loose']:
        for dp, dns, fns in os.walk(info['dir'], topdown=False):
            if dp != info['dir'] and not os.listdir(dp):
                os.rmdir(dp)
    with lock:
        prog = load_json(PROGRESS, {})
        for coll in ('parts', 'agents'):
            for k in [k for k, v in prog.get(coll, {}).items() if (v.get('order') == order if coll == 'agents' else k.startswith(order + '_'))]:
                prog[coll].pop(k)
        po = prog.get('orders', {}).get(order)
        if po:
            po.pop('allFile', None); po.pop('mergedAt', None)
        save_json(PROGRESS, prog)
        rv = load_json(REVIEWS, {})
        for k in [k for k in rv if k.startswith(order + '_')]:
            rv.pop(k)
        save_json(REVIEWS, rv)
        _cache['t'] = 0
    return rec


def delete_variant(order, dest):
    """Xoá một phương án đã lưu (một thư mục con của So_Sanh/<đơn>/, gồm Output đã chép và ketqua.json). Chỉ xoá đúng thư mục đó."""
    if not ORDER_RE.match(order or ''):
        raise ValueError('Số đơn không hợp lệ.')
    base = os.path.abspath(os.path.join(WORK, COMPARE_DIR, order))
    target = os.path.abspath(os.path.join(WORK, str(dest or '')))
    if os.path.dirname(target) != base or not os.path.isfile(os.path.join(target, 'ketqua.json')):
        raise ValueError('Không thấy phương án này.')
    shutil.rmtree(target)
    if os.path.isdir(base) and not os.listdir(base):
        os.rmdir(base)
    return {'deleted': os.path.relpath(target, WORK)}


def package_order(order, overwrite=False):
    """Đóng gói các mã ĐÃ XONG của đơn (không cần xong cả đơn): thư mục Gui (đợt 1) hoặc Gui_2, Gui_3... (các đợt sau),
    mỗi đợt gồm DXF các mã đã xong (không có file ALL) + file Excel 納品書 điền TẤT CẢ mã của đơn (mã chưa xong tô xanh, trống kích thước).
    Mã chưa xong/có Flag/tự làm không bị chuyển DXF."""
    o = next((x for x in snapshot(True)['orders'] if x['order'] == order), None)
    info = scan_orders().get(order)
    if not o or not info or info['loose']:
        raise ValueError('Không thấy thư mục đơn để đóng gói.')
    if o.get('running'):
        raise ValueError('Agent đang chạy đơn này. Chờ agent dừng rồi đóng gói (tránh chuyển file khi agent còn ghi/gộp ALL).')
    codes = [c['code'] for c in o['codes'] if c.get('ready')]
    if not codes:
        if o.get('packed'):
            raise ValueError('Không có mã nào mới để đóng gói: các mã đã xong đều đã được đóng gói ở đợt trước.')
        raise ValueError('Chưa có mã nào xong (không Flag) có file DXF trong thư mục đơn để đóng gói.')
    import package
    # file Excel điền TẤT CẢ mã của đơn: mã đã xong có kích thước, mã chưa xong tô xanh (kích thước mã đã gói ở đợt trước lấy từ tiến độ đã lưu)
    all_codes = [c['code'] for c in o['codes']]
    done = {c['code'] for c in o['codes'] if c.get('ready') or c.get('packed')}
    parts_prog = load_json(PROGRESS, {}).get('parts', {})
    known = {c: (pp['packedX'], pp['packedY']) for c in all_codes
             if (pp := parts_prog.get(f'{order}_{c}')) and pp.get('packedX') is not None and pp.get('packedY') is not None}
    r = package.package(order, info['dir'], codes, all_codes=all_codes, done=done, known=known)
    t = now_iso()
    for c in codes:         # nhớ mã đã đóng gói + kích thước phôi: bạn dời thư mục Gui đi (gửi khách xong) thì mã vẫn tính là xong, đợt sau vẫn điền được kích thước
        sz = r['sizes'].get(c)
        merge_progress('parts', f'{order}_{c}', {'packedAt': t, 'packedIn': os.path.basename(r['gui']),
                                                 'packedX': sz[0] if sz else None, 'packedY': sz[1] if sz else None})
    r['manual'] = [c['code'] for c in o['codes'] if c.get('manual')]
    r['pending'] = [c['code'] for c in o['codes'] if not c.get('ready') and not c.get('packed') and not c.get('manual')]
    return r


def list_compare():
    """Các phương án đã lưu: {số đơn: [bản ghi theo thời gian]}."""
    out = {}
    base = os.path.join(WORK, COMPARE_DIR)
    if not os.path.isdir(base):
        return out
    for od in sorted(os.listdir(base)):
        recs = []
        for ad in sorted(os.listdir(os.path.join(base, od))):
            fp = os.path.join(base, od, ad, 'ketqua.json')
            if os.path.isfile(fp):
                recs.append(load_json(fp, {}))
        if recs:
            out[od] = sorted(recs, key=lambda r: r.get('savedAt', ''))
    return out


def set_manual(order, code, manual=True):
    """Người dùng chọn tự làm một mã đang chờ (Preview/Flag): đơn hoàn tất không chờ mã đó; mã này không tính vào kết quả AI."""
    o = next((x for x in snapshot(True)['orders'] if x['order'] == order), None)
    if not o:
        raise ValueError('Không thấy đơn này.')
    c = next((x for x in o['codes'] if x['code'] == code), None)
    if not c:
        raise ValueError('Mã không thuộc đơn này.')
    if manual and c['state'] not in ('cho', 'tay'):
        raise ValueError('Chỉ chọn "Tự làm" cho mã đang chờ (có Flag).')
    return merge_progress('parts', f'{order}_{code}', {'manual': bool(manual), 'manualAt': now_iso() if manual else None})


def set_preview_ok(order, code, ok=True):
    """Nút "Preview OK": hình dựng hiện tại của mã đang chờ (PREVIEW/Flag) đã đúng -> mã tính là xong, bỏ Flag, không check lại."""
    o = next((x for x in snapshot(True)['orders'] if x['order'] == order), None)
    if not o:
        raise ValueError('Không thấy đơn này.')
    c = next((x for x in o['codes'] if x['code'] == code), None)
    if not c:
        raise ValueError('Mã không thuộc đơn này.')
    if ok and c['state'] != 'cho':
        raise ValueError('Chỉ bấm Preview OK cho mã đang chờ (PREVIEW/Flag).')
    return merge_progress('parts', f'{order}_{code}', {'previewOk': bool(ok), 'previewOkAt': now_iso() if ok else None})


def del_job(jid):
    with lock:
        prog = load_json(PROGRESS, {})
        j = prog.get('jobs', {}).get(jid)
        if not j:
            raise ValueError('Không có việc này.')
        if j.get('status') == 'nhan':
            raise ValueError('Agent đã nhận việc này, không xoá được.')
        del prog['jobs'][jid]
        save_json(PROGRESS, prog)
        _cache['t'] = 0


def reset_order_progress(order):
    """Bắt đầu chạy lại cả đơn: bỏ tiến độ cũ (từng mã, agent) của đơn. Không đụng kết quả chấm Đúng/Sai."""
    with lock:
        prog = load_json(PROGRESS, {})
        for k in [k for k in prog.get('parts', {}) if k.startswith(order + '_')]:
            prog['parts'].pop(k)
        for k in [k for k, v in prog.get('agents', {}).items() if v.get('order') == order]:
            prog['agents'].pop(k)
        po = prog.get('orders', {}).get(order)
        if po:
            po.pop('allFile', None); po.pop('mergedAt', None)
        save_json(PROGRESS, prog)
        _cache['t'] = 0


def merge_progress(coll, doc_id, fields):
    if coll not in ('orders', 'agents', 'parts', 'jobs'):
        raise ValueError('collection phải là orders | agents | parts | jobs')
    if not re.match(r'^[\w\-\.]+$', doc_id or ''):
        raise ValueError('id không hợp lệ')
    if coll == 'jobs':
        # chỉ nút Giao việc / Làm tiếp trên trang mới được tạo việc cho runner chạy
        if fields.get('status') == 'moi' or 'ui' in fields:
            raise ValueError('Không được tạo/đặt việc chờ chạy qua API tiến độ; chỉ nút Giao việc trên trang.')
    with lock:
        prog = load_json(PROGRESS, {})
        doc = prog.setdefault(coll, {}).setdefault(doc_id, {})
        if coll == 'agents' and doc.get('state') == 'running' and doc.get('startedAt') and 'startedAt' in fields and 'job' not in fields:
            fields = {k: v for k, v in fields.items() if k != 'startedAt'}   # đang chạy: giữ giờ bắt đầu do trang ghi, agent báo lại không tính là lần chạy mới
        # agent bắt đầu lần chạy mới (vd làm tiếp sau khi người dùng trả lời Flag): giữ lần chạy cũ vào history
        # để tính tổng thời gian LÀM (không tính lúc chờ người dùng)
        if coll == 'agents' and fields.get('startedAt') and doc.get('startedAt') and fields['startedAt'] != doc['startedAt']:
            end = doc.get('finishedAt') or doc.get('heartbeatAt')
            if end:
                doc.setdefault('history', []).append({'startedAt': doc['startedAt'], 'finishedAt': end, 'job': doc.get('job')})
            if 'finishedAt' not in fields:
                doc['finishedAt'] = None
        for k, v in fields.items():
            if k == 'done+' and isinstance(v, str):       # tiện: thêm 1 mã vào done
                doc.setdefault('done', [])
                if v not in doc['done']:
                    doc['done'].append(v)
            else:
                doc[k] = v
        if coll == 'agents':
            doc['heartbeatAt'] = fields.get('heartbeatAt', now_iso())
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return doc


# ---------- HTTP ----------
MIME = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8', '.svg': 'image/svg+xml',
        '.woff2': 'font/woff2', '.json': 'application/json; charset=utf-8'}


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self, limit=1_000_000):
        n = int(self.headers.get('Content-Length') or 0)
        if n > limit:
            raise ValueError('quá lớn')
        return json.loads(self.rfile.read(n) or b'{}')

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/state':
            return self.send_json(snapshot('refresh' in self.path))
        if path == '/api/reviews':
            return self.send_json(load_json(REVIEWS, {}))
        if path == '/api/compare':
            return self.send_json(list_compare())
        if path == '/' or path == '':
            path = '/index.html'
        fp = os.path.normpath(os.path.join(STATIC, path.lstrip('/')))
        if not fp.startswith(STATIC) or not os.path.isfile(fp):
            self.send_response(404); self.end_headers(); return
        with open(fp, 'rb') as f:
            b = f.read()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(os.path.splitext(fp)[1], 'application/octet-stream'))
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self.body(40_000_000 if path == '/api/ref/upload' else 1_000_000)     # file tham khảo gửi dạng base64
            if path == '/api/review':
                # {items:[{key:"<đơn>_<mã>", status:"dung"|"sai"|"cho", note?}], by?}
                with lock:
                    rv = load_json(REVIEWS, {})
                    for it in data.get('items', []):
                        key = it.get('key', '')
                        if not re.match(r'^\d{6}-\d{2}_.+$', key):
                            continue
                        st = it.get('status')
                        if st == 'cho' and not it.get('note'):
                            rv.pop(key, None)
                            continue
                        if st not in ('dung', 'sai', 'cho'):
                            continue
                        old = rv.get(key, {})
                        rv[key] = {'status': st, 'note': it.get('note', old.get('note', '')),
                                   'at': now_iso(), 'by': data.get('by') or old.get('by', '')}
                    save_json(REVIEWS, rv)
                return self.send_json({'ok': True, 'reviews': rv})
            if path == '/api/previewok':
                set_preview_ok(data.get('order'), data.get('code'), data.get('ok', True) is not False)
                return self.send_json({'ok': True})
            if path == '/api/manual':
                set_manual(data.get('order'), data.get('code'), data.get('manual', True) is not False)
                return self.send_json({'ok': True})
            if path == '/api/package':
                return self.send_json({'ok': True, 'result': package_order(data.get('order'), data.get('overwrite'))})
            if path == '/api/compare/delete':
                return self.send_json({'ok': True, **delete_variant(data.get('order'), data.get('dest'))})
            if path == '/api/archive':
                return self.send_json({'ok': True, 'saved': archive_order(data.get('order'))})
            if path == '/api/jobs/preview':
                return self.send_json({'ok': True, 'preview': preview_job(data.get('path'))})
            if path == '/api/jobs':
                return self.send_json({'ok': True, 'job': add_job(data.get('path'), data.get('subagents'), data.get('note'), data.get('model'), data.get('plan'))})
            if path == '/api/ref/upload':
                return self.send_json({'ok': True, 'name': add_ref(data.get('order'), data.get('code'), data.get('name'), data.get('data'))})
            if path == '/api/ref/delete':
                del_ref(data.get('order'), data.get('code'), data.get('name'))
                return self.send_json({'ok': True})
            if path == '/api/jobs/followup':
                return self.send_json({'ok': True, 'job': add_followup(data.get('order'), data.get('answers'), data.get('model'))})
            if path == '/api/jobs/cancel':
                import runner
                runner.cancel(data.get('id', ''))
                return self.send_json({'ok': True})
            if path == '/api/jobs/delete':
                del_job(data.get('id', ''))
                return self.send_json({'ok': True})
            if path == '/api/progress':
                # {collection, id, fields:{...}}  hoặc {batch:[{collection,id,fields}]}
                ops = data.get('batch') or [data]
                docs = [merge_progress(o.get('collection'), o.get('id'), o.get('fields') or {}) for o in ops]
                return self.send_json({'ok': True, 'docs': docs})
            return self.send_json({'error': 'không có'}, 404)
        except Exception as e:
            return self.send_json({'error': str(e)}, 400)


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    os.makedirs(DATA, exist_ok=True)
    if not os.path.isdir(WORK):
        print('Không thấy thư mục AI_Work:', WORK)
        sys.exit(1)
    sys.modules['server'] = sys.modules[__name__]
    import runner
    runner.start()
    srv = ThreadingHTTPServer(('0.0.0.0', PORT), H)
    print(f'Quản lý Project AI_CAD: http://localhost:{PORT}  (AI_Work: {WORK})')
    print('Nhấn Ctrl+C để dừng.')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
