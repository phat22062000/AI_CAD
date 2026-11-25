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

import qa

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))          # ...\AI_CAD
WORK = os.environ.get('AI_WORK', os.path.join(ROOT, 'AI_Work'))
STATIC = os.path.join(HERE, 'static')
DATA = os.path.join(HERE, 'data')
REVIEWS = os.path.join(DATA, 'reviews.json')      # Đúng/Sai của người dùng (bền vững)
LOI_SAI = os.path.join(DATA, 'loi_sai.json')      # lỗi cụ thể của mã bị chấm Sai: {"<đơn>_<mã>": {"loi": ["...", ...], "at": ...}}, agent ghi qua `report.py loi`
PROGRESS = os.path.join(DATA, 'progress.json')    # agent ghi tiến độ vào đây
CHECKS = os.path.join(DATA, 'check_results.json') # kết quả nút "Tự check": {"<đơn>": {"at", "items": [{"code", "level": "loi|canhbao", "text"}]}}, agent ghi qua `report.py check`
REPO = os.path.join(ROOT, 'Create_Flatten_SheetMetal-main')       # skill gốc + quy tắc + bài học
DA_RUT = os.path.join(REPO, 'lessons', 'feedback', '_da_rut_kinh_nghiem.json')      # mã Sai đã rút kinh nghiệm: [{"key", "file"}]
SKILL_UPD = os.path.join(REPO, 'lessons', 'skill-updates')       # đề xuất sửa skill chờ Phát duyệt
SUA_LOI = 'Sua_loi'       # <thư mục đơn>\Sua_loi\ = <mã>F.dxf (AI vẽ, web tự chép khi chấm Sai) + <mã>T.dxf (đúng, người dùng đặt vào)
QA_FROM = '2026-11-17'      # chỉ báo "Sai chưa có file T" cho đơn từ ngày này (Phát chốt 17/11/2026: bỏ qua các mã Sai cũ chưa phân tích)
HOIQUY = os.path.join(DATA, 'hoi_quy.json')        # kết quả các lần chạy hồi quy sau update skill: [{id, at, skill, loai, items}]
SKILL_LOG = os.path.join(DATA, 'skill_updates.json')   # nhật ký các lần bấm "Update Skill": [{id, at, before, after, backup, changes, skipped}]
SCRIPT_LOG = os.path.join(DATA, 'script_updates.json')   # nhật ký các lần bấm "Update Script": [{id, at, backup, changes, skipped}]
SPECIAL = ('check', 'rutkn', 'hoiquy', 'updskill', 'updscript')      # việc đặc biệt chạy bằng nút trên trang (không phải vẽ đơn): không đụng tiến độ vẽ của đơn
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
PACK_RE = re.compile(r'^Gui(?:_\d+)?[\\/]', re.I)      # DXF đã chuyển vào Gui\<đơn> (đợt 1), Gui\<đơn>(1) (đợt 2)... (bản cũ: Gui_2...)
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


def pick_refs(order, code):
    """Nút "Đính kèm PDF/DXF": mở hộp chọn file của Windows ngay tại thư mục đơn (trình duyệt không cho trang web chọn thư mục mở sẵn),
    rồi chép các file đã chọn vào <thư mục đơn>\\Tham_Khao\\<mã>\\ (chỉ chép, không đụng file gốc). Trả về danh sách tên đã chép."""
    import subprocess
    info = scan_orders().get(order or '')
    d = _ref_path(info, code)
    if not d:
        raise ValueError('Không tìm thấy thư mục đơn hoặc mã không hợp lệ.')
    if os.name != 'nt':
        raise ValueError('Chỉ mở được hộp chọn file khi web chạy trên Windows.')
    script = (
        "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$o=New-Object Windows.Forms.Form;$o.TopMost=$true;$o.ShowInTaskbar=$false;$o.StartPosition='CenterScreen';$o.Size=New-Object Drawing.Size(1,1);$o.Opacity=0;$o.Show();"
        "$f=New-Object Windows.Forms.OpenFileDialog;$f.InitialDirectory=$env:AICAD_DIR;$f.Multiselect=$true;"
        "$f.Title='Chọn file PDF/DXF của khách cho mã '+$env:AICAD_CODE;$f.Filter='PDF/DXF (*.pdf;*.dxf)|*.pdf;*.dxf';"
        "if($f.ShowDialog($o) -eq 'OK'){$f.FileNames|ForEach-Object{[Console]::Out.WriteLine($_)}};$o.Close()")
    env = dict(os.environ, AICAD_DIR=info['dir'], AICAD_CODE=code)
    p = subprocess.run(['powershell', '-NoProfile', '-STA', '-ExecutionPolicy', 'Bypass', '-Command', script],
                       capture_output=True, env=env, timeout=600)
    picked = [x.strip() for x in (p.stdout or b'').decode('utf-8', 'replace').splitlines() if x.strip()]
    if not picked:
        return []                                 # bấm Huỷ
    names = []
    for src in picked:
        n = _safe_name(os.path.basename(src))
        if not n.lower().endswith(REF_EXT) or not os.path.isfile(src):
            continue
        if os.path.getsize(src) > REF_MAX:
            raise ValueError(n + ' lớn hơn 25 MB.')
        os.makedirs(d, exist_ok=True)
        if n not in os.listdir(d) and len(os.listdir(d)) >= 10:
            raise ValueError('Mỗi mã tối đa 10 file tham khảo, hãy xoá bớt.')
        shutil.copy2(src, os.path.join(d, n))
        names.append(n)
    _cache['t'] = 0
    return names


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


def _log_usage(j):
    """Lấy token từ dòng 'result' cuối file log của một việc (khi progress chưa có usage)."""
    lg = j.get('log')
    if not lg:
        return None
    fp = os.path.join(DATA, 'logs', os.path.basename(str(lg)))
    try:
        sz = os.path.getsize(fp)
        with open(fp, 'rb') as f:
            f.seek(max(0, sz - 400000))
            tail = f.read().decode('utf-8', 'replace').splitlines()
    except OSError:
        return None
    for ln in reversed(tail):
        if '"type":"result"' not in ln.replace(' ', ''):
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        mu = (ev.get('modelUsage') or {}).values()
        return {'input': sum(v.get('inputTokens', 0) for v in mu), 'output': sum(v.get('outputTokens', 0) for v in mu),
                'cacheRead': sum(v.get('cacheReadInputTokens', 0) for v in mu), 'cacheWrite': sum(v.get('cacheCreationInputTokens', 0) for v in mu),
                'costUSD': round(float(ev.get('total_cost_usd') or 0), 4)}
    return None


_logs_cache = {'t': 0, 'v': {}}


def _order_logs():
    """{số đơn: [(tên file log, 've'|'tiep'|'check')]} từ thư mục data/logs (tên <14 số>_<đơn>[_tiep|_check].jsonl). Cache 5 giây."""
    if time.time() - _logs_cache['t'] < 5:
        return _logs_cache['v']
    out = {}
    try:
        for fn in os.listdir(os.path.join(DATA, 'logs')):
            m = re.match(r'^\d{14}_(\d{6}-\d{2})(?:_(tiep|check))?\.jsonl$', fn)
            if m:
                out.setdefault(m.group(1), []).append((fn, m.group(2) or 've'))
    except OSError:
        pass
    _logs_cache.update(t=time.time(), v=out)
    return out


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
        if not PACK_RE.match(rel) and not rel.lower().startswith(SUA_LOI.lower() + os.sep.lower()) and not rel.lower().startswith(SUA_LOI.lower() + '/'):      # Gui (các đợt) do đóng gói tạo, Sua_loi do rút kinh nghiệm: không tính là agent đang làm
            tlast = max(tlast, mt)
        stem, ext = os.path.splitext(name)
        if ext.lower() == '.pdf' and stem == order:
            pdf = rel; tin.append(mt)
        elif ext.lower() == '.xlsx' and '依頼' in name:
            xlsx = p; tin.append(mt)
        elif ext.lower() == '.dxf':
            if stem.upper() == f'{order}_ALL'.upper():
                all_dxf = (rel, mt)
            elif '_ALL' in stem.upper() or 'review' in low or 'can_check' in low or low.startswith(SUA_LOI.lower() + '\\') or low.startswith(SUA_LOI.lower() + '/'):
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
    # mã người dùng bỏ chọn ở bảng Giao việc (plan.skip của việc giao mới nhất có plan): không làm, không tính vào tổng/tiến độ đơn
    pj = sorted(((j.get('at', ''), j.get('plan') or {}) for j in prog.get('jobs', {}).values()
                 if j.get('order') == order and j.get('kind') not in ('tiep',) + SPECIAL and j.get('status') != 'loi'), key=lambda x: x[0])
    skipped = sorted(set(pj[-1][1].get('skip') or [])) if pj else []
    if skipped:
        codes = [c for c in codes if c not in skipped]
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
        elif st == 'failed':
            s = 'cho'                      # agent báo không vẽ được: chờ bổ sung/vẽ lại, không tính xong dù đã có file ALL
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
    # token đã dùng cho đơn: cộng usage của mọi việc giao cho đơn này (vẽ, làm tiếp, tự check đọc mù)
    tk = {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0, 'cost': 0.0, 'n': 0, 'by': {}, 'miss': 0}
    for j in prog.get('jobs', {}).values():
        if j.get('order') != order:
            continue
        u = j.get('usage')
        if not isinstance(u, dict) or ('costUSD' not in u and j.get('log')):
            u = _log_usage(j) or u          # việc cũ chưa ghi usage (hoặc chưa có chi phí): đọc lại từ file log
        if not isinstance(u, dict):
            if j.get('kind') in (None, '', 'tiep', 'check') and j.get('status') in ('xong', 'loi'):
                tk['miss'] += 1
            continue
        for k in ('input', 'output', 'cacheRead', 'cacheWrite'):
            tk[k] += int(u.get(k) or 0)
        tk['cost'] += float(u.get('costUSD') or 0)
        tk['n'] += 1
        kd = j.get('kind') if j.get('kind') in ('check', 'tiep') else 've'
        tk['by'][kd] = tk['by'].get(kd, 0) + 1
    # việc đã bị xoá khỏi progress.json (hoặc bản ghi cụt không có order): đọc token thẳng từ file log của đơn
    known = {os.path.basename(str(j.get('log') or (jid + '.jsonl'))) for jid, j in prog.get('jobs', {}).items() if j.get('order') == order and isinstance(j.get('usage'), dict)}
    for lg, kd in _order_logs().get(order, []):
        if lg in known:
            continue
        u = _log_usage({'log': lg})
        if not isinstance(u, dict) or not any(u.values()):
            continue                        # log lỗi đăng nhập (401) hoặc chưa kết thúc: không có token
        for k in ('input', 'output', 'cacheRead', 'cacheWrite'):
            tk[k] += int(u.get(k) or 0)
        tk['cost'] += float(u.get('costUSD') or 0)
        tk['n'] += 1
        tk['by'][kd] = tk['by'].get(kd, 0) + 1
    tk['cost'] = round(tk['cost'], 2)
    return {
        'order': order,
        'runs': runs,
        'tokens': tk if (tk['n'] or tk['miss']) else None,
        'date': order_date(order, info['dir']),
        'customer': p_order.get('customer') or meta.get('customer', ''),
        'material': p_order.get('material') or meta.get('material', ''),
        'urgent': meta.get('urgent', ''),
        'user': p_order.get('user', ''),
        'path': os.path.relpath(info['dir'], WORK).replace(os.sep, '\\') if info['dir'] != WORK else '',
        'state': state,
        'codes': code_rows,
        'skipped': skipped,
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
                if not j.get('hidden') and not (j.get('order') and j['order'] not in found and j.get('status') not in ('moi', 'nhan'))]   # việc đang chờ/đang chạy luôn hiện (thư mục đơn có thể chưa chép vào AI_Work)
        jobs.sort(key=lambda j: j.get('at', ''), reverse=True)
        rn = sys.modules.get('runner')
        data = {'orders': orders, 'agents': agents, 'jobs': jobs[:50], 'generatedAt': now_iso(),
                'runner': rn.status() if rn else {'cli': False},
                'work': os.path.basename(WORK), 'workPath': WORK, 'qaFrom': QA_FROM, 'progressFile': os.path.exists(PROGRESS)}
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
    skip = [str(c) for c in (plan.get('skip') or [])]      # mã người dùng bỏ chọn: không làm, agent không đọc PDF mã đó
    for c in skip:
        if known and c not in known:
            raise ValueError('Mã không có trong đơn: ' + c)
        if c in asg:
            raise ValueError(f'Mã {c} vừa chọn làm vừa bỏ qua.')
    miss = [c for c in known if c not in asg and c not in skip]
    if miss:
        raise ValueError('Còn mã chưa giao cho agent nào: ' + ', '.join(sorted(miss)))
    if known and not asg:
        raise ValueError('Phải chọn ít nhất một mã để làm.')
    used = {a for a in asg.values()}
    ag = {a: m for a, m in ag.items() if a == 'main' or a in used}   # bỏ subagent không nhận mã nào
    out = {'agents': ag, 'codes': asg}
    if skip:
        out['skip'] = sorted(set(skip))
    return out


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


def add_followup(order, answers, model='', redo=False):
    """Người dùng trả lời Flag trong khung chi tiết đơn -> việc 'làm tiếp': chỉ vẽ lại các mã được trả lời.
    redo=True: LÀM LẠI mã bất kỳ (kể cả mã đã xong/đã giao khách) theo thông tin bổ sung của khách; bắt buộc có thông tin bổ sung."""
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
        raise ValueError('Chưa nhập thông tin bổ sung hoặc đính kèm file của khách cho mã nào.')
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        for j in jobs.values():
            if j.get('order') == order and j.get('kind') == 'tiep' and j.get('status') in ('moi', 'nhan'):
                raise ValueError('Đơn này đã có việc làm tiếp đang chờ hoặc đang chạy.')
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + order + '_tiep'
        jobs[jid] = {'kind': 'tiep', 'path': p, 'order': order, 'subagents': 0, 'model': model, 'note': '', 'answers': answers,
                     'refs': refs, 'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        if redo:
            jobs[jid]['redo'] = True
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


def add_resume(order):
    """Nút Tiếp tục trên thẻ agent: đơn bị dừng giữa chừng -> việc 'làm tiếp' vẽ các mã chưa xong (mã đã xong giữ nguyên)."""
    o = next((x for x in snapshot(True)['orders'] if x['order'] == order), None)
    if not o:
        raise ValueError('Không thấy đơn này.')
    todo = [c['code'] for c in o['codes'] if c.get('pstatus') != 'built' and not c.get('previewOk') and not c.get('manual')]
    if not todo:
        raise ValueError('Đơn này không còn mã nào chưa vẽ xong.')
    p = os.path.join(WORK, o['path']) if o.get('path') else ''
    if not p or not os.path.isdir(p):
        raise ValueError('Không tìm thấy thư mục đơn trong AI_Work.')
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        mine = [j for j in jobs.values() if j.get('order') == order and j.get('kind') in (None, '', 'tiep')]
        if any(j.get('status') in ('moi', 'nhan') for j in mine):
            raise ValueError('Đơn này đang có việc chờ hoặc đang chạy, bấm Dừng trước nếu muốn chạy lại.')
        mine.sort(key=lambda j: j.get('at', ''))
        model = (mine[-1].get('model') if mine else '') or ''
        if model not in ('', 'opus', 'sonnet'):
            model = ''
        answers = {c: '(Tiếp tục việc vẽ bị dừng giữa chừng: vẽ mã này từ đầu theo bản vẽ gốc, không có thông tin bổ sung)' for c in todo}
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + order + '_tiep'
        jobs[jid] = {'kind': 'tiep', 'resume': True, 'path': p, 'order': order, 'subagents': 0, 'model': model, 'note': '', 'answers': answers,
                     'refs': {}, 'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
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
    """Đóng gói các mã ĐÃ XONG của đơn (không cần xong cả đơn): thư mục con của Gui: Gui/<đơn> (đợt 1), Gui/<đơn>(1), Gui/<đơn>(2)... (các đợt sau),
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


def _find_dxf_in_dir(info, fname):
    """Tìm <mã>.dxf trong thư mục đơn (không lấy Sua_loi, Tham_Khao); ưu tiên file chưa đóng gói, rồi file mới nhất."""
    base, hits = info['dir'], []
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in (REF_DIR, SUA_LOI)]
        for f in fns:
            if f.lower() == fname.lower():
                hits.append(os.path.join(dp, f))
    hits.sort(key=lambda p: (bool(PACK_RE.match(os.path.relpath(p, base))), -os.path.getmtime(p)))
    return hits[0] if hits else None


def _bring_front(hint, cls=None, wait=15.0):
    """Windows chặn chương trình chạy nền (server) đưa cửa sổ lên trước: tìm cửa sổ vừa mở theo tiêu đề (tên thư mục / tên file),
    bấm nhả phím Alt (được Windows cho phép đổi cửa sổ trước) rồi SetForegroundWindow. Chạy ở luồng riêng, lỗi thì bỏ qua."""
    if os.name != 'nt':
        return

    def run():
        try:
            import ctypes
            from ctypes import wintypes as W
            u = ctypes.windll.user32
            h_low = hint.lower()

            def find():
                res = []
                proto = ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)

                def cb(h, _l):
                    if u.IsWindowVisible(h):
                        n = u.GetWindowTextLengthW(h)
                        if n:
                            b = ctypes.create_unicode_buffer(n + 1)
                            u.GetWindowTextW(h, b, n + 1)
                            if h_low in b.value.lower():
                                if cls:
                                    c = ctypes.create_unicode_buffer(256)
                                    u.GetClassNameW(h, c, 256)
                                    if c.value != cls:
                                        return True
                                res.append(h)
                    return True
                u.EnumWindows(proto(cb), 0)
                return res[0] if res else None
            t0 = time.time()
            while time.time() - t0 < wait:
                h = find()
                if h:
                    time.sleep(0.2)
                    if u.IsIconic(h):
                        u.ShowWindow(h, 9)          # SW_RESTORE
                    u.keybd_event(0x12, 0, 0, 0)     # Alt xuống
                    u.keybd_event(0x12, 0, 2, 0)     # Alt lên
                    u.SetForegroundWindow(h)
                    u.BringWindowToTop(h)
                    return
                time.sleep(0.3)
        except Exception as e:
            print('bring_front:', e)
    threading.Thread(target=run, daemon=True).start()


def open_order_dir(order):
    """Bấm số đơn ở khung chi tiết: mở thư mục đơn bằng File Explorer (đơn để rời trong thư mục ngày thì mở thư mục ngày)."""
    if not ORDER_RE.match(order or ''):
        raise ValueError('Số đơn không hợp lệ.')
    info = scan_orders().get(order)
    if not info or not os.path.isdir(info['dir']):
        raise ValueError('Không thấy thư mục đơn ' + order + '.')
    if os.name != 'nt':
        raise ValueError('Chỉ mở được thư mục khi web chạy trên Windows: ' + info['dir'])
    os.startfile(info['dir'])
    _bring_front(os.path.basename(info['dir'].rstrip('\\/')), cls='CabinetWClass', wait=6.0)
    return info['dir']


def open_part(order, code):
    """Bấm mã trong khung chi tiết đơn: mở <mã>.dxf của đơn (file lẻ, kể cả đã đóng gói vào Gui) bằng phần mềm mặc định."""
    if not ORDER_RE.match(order or '') or not CODE_RE.match(code or ''):
        raise ValueError('Số đơn hoặc mã không hợp lệ.')
    info = scan_orders().get(order)
    if not info:
        raise ValueError('Không thấy thư mục đơn ' + order + '.')
    fp = None
    if info.get('loose'):
        p = os.path.join(info['dir'], code + '.dxf')
        fp = p if os.path.isfile(p) else None
    else:
        fp = _find_dxf_in_dir(info, code + '.dxf')
    if not fp:
        raise ValueError('Không thấy file ' + code + '.dxf (mã có thể chỉ nằm trong file ALL).')
    if os.name != 'nt':
        raise ValueError('Chỉ mở được file khi web chạy trên Windows: ' + fp)
    os.startfile(fp)
    _bring_front(os.path.splitext(os.path.basename(fp))[0])
    return fp


def _pdf_viewer():
    """Phần mềm PDF mặc định của Windows (đọc registry) để mở đúng trang bằng /A page=N; không tìm được thì None."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.pdf\UserChoice') as k:
            prog = winreg.QueryValueEx(k, 'ProgId')[0]
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, prog + r'\shell\open\command') as k:
            cmd = winreg.QueryValueEx(k, '')[0]
        m = re.match(r'\s*"([^"]+)"', cmd) or re.match(r'\s*(\S+)', cmd)
        return m.group(1) if m and os.path.isfile(m.group(1)) else None
    except Exception:
        return None


def pdf_page_of(order, code, codes, npages):
    """Trang PDF chứa mã: agent ghi `page` khi vẽ mã (parts); đơn cũ chưa có thì đoán theo thứ tự nếu số trang = số mã. Trả (trang, chắc_chắn)."""
    pp = load_json(PROGRESS, {}).get('parts', {}).get(f'{order}_{code}', {})
    try:
        pg = int(pp.get('page'))
        if 1 <= pg <= max(npages, 1):
            return pg, True
    except (TypeError, ValueError):
        pass
    if codes and npages == len(codes) and code in codes:
        return codes.index(code) + 1, False
    return 1, False


def raise_window():
    """Đơn vừa xong: đưa cửa sổ trình duyệt đang mở trang giám sát lên trên màn hình (tìm theo tiêu đề 'AI CAD')."""
    if os.name != 'nt':
        return False
    import subprocess, base64
    try:
        # Khớp theo đầu tiêu đề trang web ("AI CAD · Giám Sát ..."), KHÔNG khớp cửa sổ console "AI CAD - Quan ly Project". Truyền lệnh dạng Base64 để giữ dấu tiếng Việt.
        cmd = "(New-Object -ComObject WScript.Shell).AppActivate('AI CAD · Giám Sát') | Out-Null"
        enc = base64.b64encode(cmd.encode('utf-16-le')).decode()
        subprocess.Popen(['powershell', '-NoProfile', '-WindowStyle', 'Hidden', '-EncodedCommand', enc],
                         creationflags=0x08000000)
        return True
    except Exception:
        return False


def open_pdf(order, code):
    """Bấm biểu tượng PDF ở Lịch Sử Lỗi: mở PDF của đơn ở đúng trang chứa mã (PDF scan, không tìm theo chữ được: dùng trang agent đã ghi hoặc đoán theo thứ tự)."""
    if not ORDER_RE.match(order or '') or not CODE_RE.match(code or ''):
        raise ValueError('Số đơn hoặc mã không hợp lệ.')
    info = scan_orders().get(order)
    if not info:
        raise ValueError('Không thấy thư mục đơn ' + order + '.')
    fp = next((p for rel, p in order_files(order, info) if os.path.basename(rel).lower() == order.lower() + '.pdf'), None)
    if not fp:
        raise ValueError('Không thấy file ' + order + '.pdf của đơn.')
    o = next((x for x in snapshot()['orders'] if x['order'] == order), None)
    codes = [c['code'] for c in (o or {}).get('codes', [])]
    try:
        import pymupdf
        npages = len(pymupdf.open(fp))
    except Exception:
        npages = 0
    page, sure = pdf_page_of(order, code, codes, npages)
    if os.name != 'nt':
        raise ValueError('Chỉ mở được file khi web chạy trên Windows: ' + fp)
    import subprocess
    viewer = _pdf_viewer()
    if viewer and page > 1:
        subprocess.Popen([viewer, '/A', f'page={page}', fp])
    else:
        os.startfile(fp)
    return {'path': fp, 'page': page, 'sure': sure, 'pages': npages}


def ensure_sua_loi(order, code):
    """Mã vừa chấm Sai: tạo <thư mục đơn>\\Sua_loi\\ và chép file AI đã vẽ thành <mã>F.dxf (không ghi đè). File T (đúng) do người dùng tự đặt vào."""
    if not ORDER_RE.match(order or '') or not CODE_RE.match(code or ''):
        return {'ok': False, 'why': 'Số đơn hoặc mã không hợp lệ.'}
    info = scan_orders().get(order)
    if not info or info['loose']:
        return {'ok': False, 'why': 'Đơn chưa có thư mục riêng ' + order + ' (file đang để rời trong thư mục ngày), chưa tạo được Sua_loi.'}
    folder = os.path.join(info['dir'], SUA_LOI)
    dst = os.path.join(folder, code + 'F.dxf')
    os.makedirs(folder, exist_ok=True)
    if os.path.isfile(dst):
        return {'ok': True, 'folder': folder, 'created': False}
    src = _find_dxf_in_dir(info, code + '.dxf')
    if not src:
        return {'ok': False, 'folder': folder, 'why': 'Đã tạo folder Sua_loi nhưng không thấy file ' + code + '.dxf của đơn (mã chỉ nằm trong file ALL hoặc đã dời đi): hãy chép file AI vẽ vào thành ' + code + 'F.dxf.'}
    shutil.copy2(src, dst)
    if os.path.getsize(dst) != os.path.getsize(src):
        os.remove(dst)
        return {'ok': False, 'folder': folder, 'why': 'Chép file F lệch dung lượng, thử lại.'}
    return {'ok': True, 'folder': folder, 'created': True, 'from': os.path.relpath(src, info['dir'])}


def _rut_done():
    d = load_json(DA_RUT, [])
    return {x.get('key') for x in d if isinstance(x, dict)} if isinstance(d, list) else set()


def loi_info():
    """Mã đang chấm Sai -> lỗi cụ thể (loi_sai.json), thư mục Sua_loi chứa <mã>T.dxf (đúng) và <mã>F.dxf (AI vẽ), đã rút kinh nghiệm chưa."""
    data = load_json(LOI_SAI, {})
    done = _rut_done()
    orders = {o['order']: o for o in snapshot()['orders']}
    out = {}
    for key, v in load_json(REVIEWS, {}).items():
        if v.get('status') != 'sai' or '_' not in key:
            continue
        order, code = key.split('_', 1)
        o = orders.get(order)
        folder, files = None, []
        if o:
            folder = os.path.join(WORK, o['path'].replace('\\', os.sep), SUA_LOI)
            try:
                files = sorted(f for f in os.listdir(folder) if f.upper() in (code.upper() + 'T.DXF', code.upper() + 'F.DXF'))
            except OSError:
                folder, files = None, []        # chưa có folder Sua_loi của đơn
        up = [f.upper() for f in files]
        out[key] = {'loi': [str(x) for x in (data.get(key) or {}).get('loi', [])], 'loai': [str(x) for x in (data.get(key) or {}).get('loai', [])],
                    'nguyen_nhan': str((data.get(key) or {}).get('nguyen_nhan', '')), 'update': str((data.get(key) or {}).get('update', '')), 'nguon': str((data.get(key) or {}).get('nguon', '')), 'khop': (data.get(key) or {}).get('khop'),
                    'folder': folder, 'files': files, 'hasT': code.upper() + 'T.DXF' in up, 'hasF': code.upper() + 'F.DXF' in up,
                    'rut': key in done, 'order': order, 'code': code, 'date': (o or {}).get('date', '')}
    return out


def _scan_md(folder, applied=False, whole=False):
    """Đọc các file .md trong một thư mục (đề xuất hoặc bài học): tên, đường dẫn, dòng đầu, các mã 26-xxxxxx nêu trong file."""
    out = []
    try:
        names = [f for f in os.listdir(folder) if f.lower().endswith('.md')]
    except OSError:
        return out
    for f in names:
        fp = os.path.join(folder, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                txt = fh.read(40000)
        except OSError:
            continue
        # mã của đề xuất/bài học: lấy ở dòng "Nguồn:" (quy ước file), không có thì ở 6 dòng đầu; mã chỉ được nhắc tới trong phần thử nghiệm không tính
        src = txt if whole else next((l for l in txt.split('\n')[:20] if re.match(r'\s*\**\s*Nguồn', l, re.I)), '\n'.join(txt.split('\n')[:6]))
        out.append({'name': f, 'at': iso(os.path.getmtime(fp)), 'head': txt[:3000], 'applied': applied,
                    'codes': set(re.findall(r'(?<!\d)(26-\d{6})(?!\d)', src))})
    return out


def loi_history():
    """Tab "Lịch Sử Lỗi": mỗi mã chấm Sai -> loại lỗi, file T/F trong Sua_loi, và giải pháp đã update chưa
    (đề xuất đã áp dụng / đang chờ duyệt / chỉ có bài học / chưa rút kinh nghiệm)."""
    props = _scan_md(SKILL_UPD) + _scan_md(os.path.join(SKILL_UPD, 'da_ap_dung'), True)
    lessons = _scan_md(os.path.join(REPO, 'lessons', 'feedback'), whole=True)
    rut_file = {x.get('key'): x.get('file') for x in (load_json(DA_RUT, []) or []) if isinstance(x, dict)}     # bài học ghi lúc rút kinh nghiệm
    rows = []
    for key, v in loi_info().items():
        code = v['code']
        own = [p for p in props if p['name'].startswith(code[3:])]     # đề xuất mang tên mã (vd 068185-...) là của chính mã này
        mine = own or [p for p in props if code in p['codes']]           # không có thì lấy đề xuất gộp nêu mã ở dòng Nguồn
        done = [p for p in mine if p['applied'] or proposal_kind(p['head']) == 'xong']
        part = [p for p in mine if not p['applied'] and proposal_kind(p['head']) != 'xong' and re.search(r'ĐÃ ÁP DỤNG', p['head'].split('\n', 1)[0], re.I)]
        wait = [p for p in mine if p not in done and p not in part]
        les = list(dict.fromkeys(([rut_file[key]] if rut_file.get(key) else []) + [l['name'] for l in lessons if code in l['codes']]))
        if done and not wait and not part:
            st, txt = 'da', 'Đã update'
        elif done or part:
            st, txt = 'motphan', 'Đã update một phần'
        elif wait:
            k = proposal_kind(wait[0]['head'])
            st, txt = 'cho', {'skill': 'Chờ Update Skill', 'script': 'Chờ Update Script', 'hq': 'Chờ đóng đề xuất'}.get(k, 'Chờ duyệt')
        elif v['rut']:
            st, txt = ('baihoc', 'Đã có bài học (agent đọc trước khi vẽ), không cần sửa skill') if les else ('khong', 'Đã rút KN, không có bài học hay đề xuất')
        else:
            st, txt = 'chua', 'Chưa rút kinh nghiệm' if v['hasT'] else 'Chưa rút KN (thiếu file T)'
        les_at = {l['name']: l['at'] for l in lessons}
        up_at = max([p['at'] for p in mine] + [les_at[n] for n in les if n in les_at], default='')     # lúc giải pháp của lỗi được update gần nhất (đề xuất hoặc bài học)
        rows.append({'key': key, 'order': v['order'], 'code': code, 'date': v.get('date', ''), 'upAt': up_at,
                     'loai': list(dict.fromkeys(qa.norm_loai(x) for x in v['loai'])), 'loi': v['loi'],
                     'hasT': v['hasT'], 'hasF': v['hasF'], 'folder': v['folder'], 'st': st, 'stText': txt,
                     'hasC': (lambda c: bool(c) and not _old_auto_compare(c))(find_compare(v['folder'], code)),
                     'props': [{'name': p['name'], 'at': p['at'], 'done': p in done, 'line': next((l.strip() for l in p['head'].split('\n') if l.strip()), '')[:200]} for p in mine], 'lessons': les})
    # mặc định: lỗi CHƯA xử lý xong (chua / cho / motphan, giống bộ lọc "Chưa xử lý xong") luôn ở trên đầu, mới nhất trước theo ngày đơn;
    # bên dưới là lỗi đã xử lý (da / baihoc / khong), giải pháp được update gần nhất nằm trên
    rows.sort(key=lambda r: (r['st'] in ('chua', 'cho', 'motphan'), (r['date'] or '') if r['st'] in ('chua', 'cho', 'motphan') else (r['upAt'] or ''), r['date'] or '', r['key']), reverse=True)
    return rows


def find_compare(folder, code):
    """File Compare đã có của mã: tìm trong Sua_loi trước, rồi thư mục đơn (cha của Sua_loi) và thư mục con tối đa 2 cấp.
    Nhận tên <mã>Compare.dxf, <mã>_Compare.dxf, <mã> compare....dxf (không phân biệt hoa thường)."""
    if not folder:
        return None
    pat = re.compile(r'^' + re.escape(code) + r'[ _-]?compare[^\\/]*\.dxf$', re.I)
    try:
        hit = next((f for f in os.listdir(folder) if pat.match(f)), None)
        if hit:
            return os.path.join(folder, hit)
    except OSError:
        pass
    base = os.path.dirname(folder.rstrip('\\/'))
    for root, dns, fns in os.walk(base):
        if root[len(base):].count(os.sep) >= 2:
            dns[:] = []
        hit = next((f for f in fns if pat.match(f)), None)
        if hit:
            return os.path.join(root, hit)
    return None


def _old_auto_compare(fp):
    """File Compare do bản cũ của compare_tf.py tạo (có lớp LABEL; còn dim hoặc còn dòng chú thích): tạo lại theo bản hiện tại.
    File người dùng tự làm (không có lớp LABEL) thì giữ nguyên."""
    try:
        with open(fp, 'r', encoding='utf-8', errors='replace') as f:
            txt = f.read()
    except OSError:
        return False
    names = set(x.strip() for x in txt.splitlines())
    if 'LABEL' not in names:
        return False
    # bản cũ: còn dim (chưa có lớp KHAC_NHAU) hoặc còn dòng chú thích dưới label (Phát 18/11 chỉ giữ True / False)
    return 'KHAC_NHAU' not in names or any(k in txt for k in ('cho cùng hướng T', 'Màu hồng = khác nhau', 'Hai hình khớp nhau'))


def compare_sualoi(order, code):
    """Nút Compare (tab Lịch Sử Lỗi): chưa có <mã>Compare.dxf trong Sua_loi thì tạo bằng tools/compare_tf.py (F trái, T phải,
    dim chỗ khác nhau, label False/True), rồi mở file bằng phần mềm mặc định. Đã có thì chỉ mở."""
    import subprocess
    v = loi_info().get(f'{order}_{code}')
    if not v or not v.get('folder'):
        raise ValueError('Không thấy thư mục Sua_loi của mã này.')
    names = {f.upper(): f for f in os.listdir(v['folder'])}
    have = find_compare(v['folder'], code)          # đã có file Compare (ở Sua_loi hoặc thư mục đơn): chỉ mở, không tạo lại
    out = have or os.path.join(v['folder'], code + 'Compare.dxf')
    if have and _old_auto_compare(have):            # bản dim cũ do web tạo: tạo lại (ghi đè) theo kiểu tô màu
        have = None
    created = False
    if not have:
        if not (v['hasT'] and v['hasF']):
            raise ValueError('Cần đủ file ' + code + 'T.dxf và ' + code + 'F.dxf trong Sua_loi mới tạo được Compare.')
        t = os.path.join(v['folder'], names[(code + 'T.DXF').upper()])
        f = os.path.join(v['folder'], names[(code + 'F.DXF').upper()])
        tool = os.path.join(REPO, 'tools', 'compare_tf.py')
        if not os.path.isfile(tool):
            raise ValueError('Thiếu công cụ ' + tool)
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        p = subprocess.run([sys.executable, '-X', 'utf8', tool, t, f, out], capture_output=True, timeout=90, env=env)
        msg = (p.stdout or b'').decode('utf-8', 'replace').strip() + (p.stderr or b'').decode('utf-8', 'replace').strip()[-300:]
        if p.returncode != 0 or not os.path.isfile(out):
            raise ValueError('Tạo Compare lỗi: ' + (msg or 'mã thoát %s' % p.returncode))
        created = True
    if os.name != 'nt':
        raise ValueError(('Đã tạo ' if created else 'Đã có ') + out + ' (chỉ mở tự động được khi web chạy trên Windows).')
    os.startfile(out)
    _bring_front(os.path.splitext(os.path.basename(out))[0])
    return {'path': out, 'created': created}


def open_sualoi(order, code, kind):
    """Mở <mã>T.dxf hoặc <mã>F.dxf trong Sua_loi bằng phần mềm mặc định của máy (chỉ hai file này, không nhận đường dẫn tuỳ ý)."""
    kind = str(kind or '').upper()
    if kind not in ('T', 'F'):
        raise ValueError('Chỉ mở được file T hoặc F.')
    v = loi_info().get(f'{order}_{code}')
    if not v or not v.get('folder'):
        raise ValueError('Không thấy thư mục Sua_loi của mã này.')
    name = next((f for f in v['files'] if f.upper() == (code + kind + '.DXF').upper()), None)
    if not name:
        raise ValueError(f'Chưa có file {code}{kind}.dxf trong Sua_loi.')
    fp = os.path.join(v['folder'], name)
    if os.name != 'nt':
        raise ValueError('Chỉ mở được file khi web chạy trên Windows: ' + fp)
    os.startfile(fp)
    _bring_front(os.path.splitext(os.path.basename(fp))[0])
    return fp


def rutkn_status():
    li = loi_info()
    ready = [k for k, v in li.items() if v['hasT'] and v['hasF'] and not v['rut']]
    wait_t = [k for k, v in li.items() if not v['hasT'] and not v['rut'] and v.get('date', '') >= QA_FROM]
    return li, ready, wait_t


def proposal_pending(head):
    """Đề xuất còn chờ: dòng đầu ghi CHỜ PHÁT DUYỆT, hoặc ghi CÒN CHỜ (đã áp dụng một phần). ĐÃ ÁP DỤNG mà không còn CÒN CHỜ thì xong."""
    h = head or ''
    if re.search(r'CÒN CHỜ', h, re.I):
        return True
    return bool(re.search(r'CHỜ PHÁT DUYỆT', h, re.I)) and not re.search(r'ĐÃ ÁP DỤNG', h.split('\n', 1)[0], re.I)


def proposal_kind(head):
    """Loại đề xuất để quyết định nút nào xử lý:
    'skill'  = còn phần sửa SKILL.md/rules (nút Update Skill);
    'script' = chỉ còn phần sửa script tools\\*.py (nút Update Script);
    'hq'     = không sửa gì, chờ Chạy hồi quy rồi người dùng tự đóng;
    'xong'   = đã áp dụng hết."""
    h = head or ''
    if not proposal_pending(h):
        return 'xong'
    lines = h.split('\n')
    title = next((l for l in lines if l.startswith('# ')), '')
    if re.search(r'chờ (chạy )?hồi quy', title, re.I):
        return 'hq'
    m = re.search(r'CÒN CHỜ:?\s*([^\n]*)', lines[0])
    if m:                                                    # đã áp dụng một phần: xem phần còn chờ là gì
        rest = m.group(1)
        if re.search(r'script|\.py', rest, re.I) and not re.search(r'SKILL|rules|quy tắc', rest, re.I):
            return 'script'
        return 'skill'
    # đề xuất mới (CHỜ PHÁT DUYỆT): xem các mục "## (a) Script", "## (c) SKILL.md" có thật sự đề xuất sửa không
    secs, cur = [], None
    for l in lines[1:]:
        if l.startswith('## '):
            cur = [l, '']
            secs.append(cur)
        elif cur is not None:
            cur[1] += l + '\n'
    act = {'skill': False, 'script': False}
    for hd, body in secs:
        tg = 'script' if re.search(r'script|\.py', hd, re.I) else 'skill' if re.search(r'SKILL|rules|skill', hd, re.I) else None
        if tg and not re.search(r'không đề xuất[^.\n]{0,12}(script|sửa|SKILL|skill)', hd + '\n' + body, re.I):
            act[tg] = True
    if secs and not act['skill'] and not act['script']:
        return 'hq'
    if secs and act['script'] and not act['skill']:
        return 'script'
    return 'skill'


def close_proposal(name):
    """Nút "Đóng đề xuất": cất file đề xuất sang lessons\\skill-updates\\da_ap_dung\\ (không xoá hẳn)."""
    src = os.path.join(SKILL_UPD, os.path.basename(name or ''))
    if not os.path.isfile(src) or not src.lower().endswith('.md'):
        raise ValueError('Không thấy file đề xuất.')
    dst = os.path.join(SKILL_UPD, 'da_ap_dung')
    os.makedirs(dst, exist_ok=True)
    to = os.path.join(dst, os.path.basename(src))
    if os.path.exists(to):
        to = os.path.join(dst, datetime.now().strftime('%Y%m%d%H%M%S_') + os.path.basename(src))
    shutil.move(src, to)
    _cache['t'] = 0
    return os.path.basename(to)


def archive_applied(names):
    """Sau Update Skill: đề xuất đã ĐÃ ÁP DỤNG hết (không còn CÒN CHỜ) thì chuyển khỏi danh sách, sang lessons\\skill-updates\\da_ap_dung\\ (không xoá hẳn để còn tra lại lý do).
    Trả về tên các file đã chuyển."""
    dst = os.path.join(SKILL_UPD, 'da_ap_dung')
    moved = []
    for name in names or []:
        src = os.path.join(SKILL_UPD, os.path.basename(name))
        try:
            with open(src, 'r', encoding='utf-8') as f:
                head = f.read(12000)
        except OSError:
            continue
        if proposal_pending(head) or not re.search(r'ĐÃ ÁP DỤNG', head):
            continue
        try:
            os.makedirs(dst, exist_ok=True)
            to = os.path.join(dst, os.path.basename(src))
            if os.path.exists(to):
                to = os.path.join(dst, datetime.now().strftime('%Y%m%d%H%M%S_') + os.path.basename(src))
            shutil.move(src, to)
            moved.append(os.path.basename(src))
        except OSError:
            continue
    return moved


def list_proposals(n=12):
    """Đề xuất sửa skill (lessons\\skill-updates\\*.md) mới nhất, để Phát xem trên trang. Kèm số đơn và mã Sai nêu trong đề xuất."""
    out = []
    try:
        fs = [os.path.join(SKILL_UPD, f) for f in os.listdir(SKILL_UPD) if f.lower().endswith('.md')]
    except OSError:
        return out
    for fp in sorted(fs, key=os.path.getmtime, reverse=True)[:n]:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                head = f.read(12000)
        except OSError:
            continue
        orders = list(dict.fromkeys(re.findall(r'(?<!\d)(5\d{5}-\d{2})(?!\d)', head)))
        codes = list(dict.fromkeys(re.findall(r'(?<!\d)(26-\d{6})(?!\d)', head)))
        out.append({'name': os.path.basename(fp), 'path': fp, 'at': iso(os.path.getmtime(fp)), 'head': head,
                    'orders': orders, 'codes': codes, 'pending': proposal_pending(head), 'kind': proposal_kind(head),
                    'partial': (lambda m: m.group(1).strip()[:120] if m else '')(re.search(r'CÒN CHỜ:?\s*([^\n]*)', head.split('\n', 1)[0]))})
    return out


def _dup_job(kind, order=''):
    prog = load_json(PROGRESS, {})
    return any(j.get('kind') == kind and j.get('order', '') == order and j.get('status') in ('moi', 'nhan') for j in prog.get('jobs', {}).values())


def run_script_check(order, info, known):
    """Chạy 2 script kiểm (0 token) cho đơn, lưu vào check_results.json (giữ nguyên các mục do agent báo)."""
    res = qa.script_check(REPO, info['dir'], order, known)
    with lock:
        d = load_json(CHECKS, {})
        cur = d.get(order) or {}
        keep = [it for it in cur.get('items', []) if it.get('src', 'ai') != 'script']
        d[order] = dict(cur, items=res['items'] + keep, info=res['info'], scriptErr=res['err'], scriptRan=res['ran'], scriptAt=now_iso())
        save_json(CHECKS, d)
    return res


def add_check_job(order, codes=None):
    """Nút "Tự check": (1) chạy script dxf_check.py + doi_chieu_khach.py ngay, 0 token; (2) chỉ mã rủi ro (script có LỖI/CẢNH BÁO,
    tối đa 30% số mã) mới giao agent đọc mù theo skill dxf-check. Bấm ở một mã cụ thể thì luôn đọc mù mã đó. Chỉ báo, không sửa file."""
    o = next((x for x in snapshot(True)['orders'] if x['order'] == order), None)
    info = scan_orders().get(order or '')
    if not o or not info:
        raise ValueError('Không thấy đơn này.')
    if not (o.get('hasAll') or o.get('partFiles')):
        raise ValueError('Đơn chưa có file DXF để check.')
    if o.get('running'):
        raise ValueError('Agent đang vẽ đơn này, chờ xong rồi hãy check.')
    known = [c['code'] for c in o['codes']]
    one = [c for c in (codes or []) if c in known]
    if codes and not one:
        raise ValueError('Không có mã nào để check.')
    if _dup_job('check', order):
        raise ValueError('Đơn này đã có việc check đang chờ hoặc đang chạy.')
    res = run_script_check(order, info, known)
    if one:
        risky, why = one, 'ma'
    elif not res['ran']:
        risky, why = known, 'khong_script'          # script không chạy được: agent tự chạy script và check cả đơn như trước
    else:
        risky, why = qa.pick_risky(res['items'], known), 'rui_ro'
    out = {'script': {'ran': res['ran'], 'err': res['err'], 'loi': sum(1 for x in res['items'] if x['level'] == 'loi'),
                      'canhbao': sum(1 for x in res['items'] if x['level'] == 'canhbao')}, 'risky': risky, 'why': why, 'job': None}
    if not risky:
        return out
    hints = [{'code': x['code'], 'level': x['level'], 'text': x['text']} for x in res['items'] if x['code'] in risky][:40]
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + order + '_check'
        jobs[jid] = {'kind': 'check', 'path': info['dir'], 'order': order, 'codes': risky, 'hints': hints, 'scriptRan': res['ran'], 'subagents': 0, 'model': '', 'note': '',
                     'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        out['job'] = dict(jobs[jid], id=jid)
    return out


def hoiquy_set(loai='', n=8):
    """Bộ mã hồi quy: mã Sai đã có file T (đáp án chuẩn), thêm mã đã chấm Đúng còn file riêng (đáp án bạc) cho đủ n.
    Có loai thì chỉ lấy mã T thuộc loại lỗi đó + tối đa 2 mã Đúng cùng đơn làm đối chứng."""
    li = loi_info()
    rv = load_json(REVIEWS, {})
    found = scan_orders()
    items = []
    for k, v in sorted(li.items(), key=lambda z: (rv.get(z[0]) or {}).get('at', ''), reverse=True):
        if not v['hasT'] or not v['folder']:
            continue
        lo = [qa.norm_loai(x) for x in v['loai']]
        if loai and loai not in lo:
            continue
        items.append({'key': k, 'order': v['order'], 'code': v['code'], 'kieu': 'T', 'loai': lo,
                      'ref': os.path.join(v['folder'], v['code'] + 'T.dxf'), 'dir': (found.get(v['order']) or {}).get('dir', '')})
    items = [x for x in items if x['dir']][:n]
    want = min(n, len(items) + 2) if loai else n
    per, pref = {}, {x['order'] for x in items}
    dung = sorted(((k, v) for k, v in rv.items() if v.get('status') == 'dung' and '_' in k), key=lambda z: z[1].get('at', ''), reverse=True)
    if loai:
        dung = [z for z in dung if z[0].split('_', 1)[0] in pref]
    for k, v in dung:
        if len(items) >= want:
            break
        order, code = k.split('_', 1)
        info = found.get(order)
        if not info or per.get(order, 0) >= 2:
            continue
        fp = _find_dxf_in_dir(info, code + '.dxf')
        if not fp:
            continue
        per[order] = per.get(order, 0) + 1
        items.append({'key': k, 'order': order, 'code': code, 'kieu': 'dung', 'loai': [], 'ref': fp, 'dir': info['dir']})
    return items


def add_hoiquy_job(loai=''):
    """Nút "Chạy hồi quy" (sau khi update skill): agent vẽ lại bộ mã bằng skill hiện tại vào thư mục tạm rồi so với đáp án bằng diff_tf.py."""
    items = hoiquy_set(loai or '')
    if not items:
        raise ValueError('Chưa có mã nào làm đáp án (cần mã Sai có file T hoặc mã Đúng còn file riêng).')
    if _dup_job('hoiquy'):
        raise ValueError('Đã có việc hồi quy đang chờ hoặc đang chạy.')
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_hoiquy'
        jobs[jid] = {'kind': 'hoiquy', 'path': REPO, 'order': '', 'items': items, 'loai': loai or '', 'skill': qa.skill_version(REPO), 'subagents': 0, 'model': '', 'note': '',
                     'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


def qa_info():
    """Số liệu cho mục chất lượng ở trang Đánh Giá AI: M1-M4, bộ hồi quy, các lần hồi quy gần đây, chi phí thật của việc check/rút kinh nghiệm/hồi quy."""
    done = set(_rut_done())
    st = qa.stats(load_json(REVIEWS, {}), load_json(LOI_SAI, {}), done)
    jobs = load_json(PROGRESS, {}).get('jobs', {})
    use = {}
    for jid, j in jobs.items():
        u = j.get('usage')
        if not u:
            continue
        k = j.get('kind') if j.get('kind') in SPECIAL else 've'
        g = use.setdefault(k, {'n': 0, 'cost': 0.0, 'out': 0, 'codes': 0})
        g['n'] += 1
        g['cost'] = round(g['cost'] + float(u.get('costUSD') or 0), 4)
        g['out'] += int(u.get('output') or 0)
        g['codes'] += len(j.get('codes') or j.get('items') or [])
    try:
        hs = hoiquy_set()
    except Exception:
        hs = []
    try:        # mọi loại lỗi có mã đã đủ file T (không bị cắt theo giới hạn 8 mã của "Cả bộ"), để chọn hồi quy theo loại
        loais = sorted({qa.norm_loai(x) for v in loi_info().values() if v['hasT'] and v['folder'] for x in v['loai']})
    except Exception:
        loais = sorted({x for it in hs for x in it['loai']})
    return {'loais': loais, 'stats': st, 'usage': use, 'skill': qa.skill_version(REPO), 'hoiquy': load_json(HOIQUY, [])[-5:], 'updates': load_json(SKILL_LOG, [])[-3:], 'scripts': load_json(SCRIPT_LOG, [])[-3:],
            'set': [{'key': x['key'], 'kieu': x['kieu'], 'loai': x['loai']} for x in hs]}


def add_updskill_job(files=None):
    """Nút "Update Skill" (người dùng bấm = lệnh "update skill"): agent áp dụng các đề xuất còn chờ vào SKILL.md/rules, sao lưu trước, ghi nhật ký dòng đã đổi.
    files = tên file đề xuất muốn áp dụng; không chọn thì áp dụng mọi đề xuất còn chờ."""
    # đề xuất 'hq' (Chờ hồi quy) chỉ được áp dụng khi người dùng tick chọn rõ (Update luôn, không cần hồi quy); không chọn gì thì chỉ áp dụng đề xuất 'skill'
    pend = {p['name']: p for p in list_proposals(50) if p['pending'] and p['kind'] in ('skill', 'hq')}
    names = [f for f in (files or [n for n, p in pend.items() if p['kind'] == 'skill']) if f in pend]
    if not names:
        raise ValueError('Không có đề xuất nào còn phần sửa SKILL.md/rules để áp dụng.')
    if _dup_job('updskill') or _dup_job('updscript'):
        raise ValueError('Đã có việc update skill hoặc update script đang chờ hoặc đang chạy.')
    items = [{'name': n, 'path': pend[n]['path'], 'orders': pend[n]['orders'], 'codes': pend[n]['codes'], **({'hq': True} if pend[n]['kind'] == 'hq' else {})} for n in names]
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_updskill'
        jobs[jid] = {'kind': 'updskill', 'path': REPO, 'order': '', 'items': items, 'skillBefore': qa.skill_version(REPO), 'subagents': 0, 'model': '', 'note': '',
                     'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


def add_updscript_job(files=None):
    """Nút "Update Script": agent áp dụng phần script (tools\\*.py) của các đề xuất, sao lưu script trước, thử trước/sau trên dữ liệu thật, ghi nhật ký."""
    pend = {p['name']: p for p in list_proposals(50) if p['pending'] and p['kind'] == 'script'}
    names = [f for f in (files or list(pend)) if f in pend]
    if not names:
        raise ValueError('Không có đề xuất nào còn phần sửa script để áp dụng.')
    if _dup_job('updskill') or _dup_job('updscript'):
        raise ValueError('Đã có việc update skill hoặc update script đang chờ hoặc đang chạy.')
    items = [{'name': n, 'path': pend[n]['path'], 'orders': pend[n]['orders'], 'codes': pend[n]['codes']} for n in names]
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_updscript'
        jobs[jid] = {'kind': 'updscript', 'path': REPO, 'order': '', 'items': items, 'subagents': 0, 'model': '', 'note': '',
                     'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


def add_rutkn_job():
    """Nút "Rút kinh nghiệm": mọi mã Sai đã có đủ T và F mà chưa rút -> agent so T/F, ghi lỗi, bài học, nháp đề xuất sửa skill (KHÔNG sửa skill)."""
    li, ready, wait_t = rutkn_status()
    if not ready:
        raise ValueError('Chưa có mã Sai nào đủ file T và F để rút kinh nghiệm.' + (' Còn %d mã Sai chờ file T.' % len(wait_t) if wait_t else ''))
    if _dup_job('rutkn'):
        raise ValueError('Đã có việc rút kinh nghiệm đang chờ hoặc đang chạy.')
    items = [{'key': k, 'order': li[k]['order'], 'code': li[k]['code'], 'folder': li[k]['folder']} for k in ready]
    with lock:
        prog = load_json(PROGRESS, {})
        jobs = prog.setdefault('jobs', {})
        jid = datetime.now().strftime('%Y%m%d%H%M%S') + '_rutkn'
        jobs[jid] = {'kind': 'rutkn', 'path': REPO, 'order': '', 'items': items, 'subagents': 0, 'model': '', 'note': '',
                     'pdf': 0, 'xlsx': 0, 'status': 'moi', 'at': now_iso(), 'ui': True}
        save_json(PROGRESS, prog)
        _cache['t'] = 0
        return dict(jobs[jid], id=jid)


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
        if j.get('status') in ('xong', 'loi') and isinstance(j.get('usage'), dict):
            j['hidden'] = True              # việc đã chạy xong: chỉ ẩn khỏi hàng đợi, giữ lại để còn tính "Token đã dùng"
        else:
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
        if path == '/api/loi':
            return self.send_json(loi_info())
        if path == '/api/compare':
            return self.send_json(list_compare())
        if path == '/api/check':
            return self.send_json(load_json(CHECKS, {}))
        if path == '/api/proposals':
            return self.send_json(list_proposals())
        if path == '/api/loihistory':
            return self.send_json(loi_history())
        if path == '/api/qa':
            return self.send_json(qa_info())
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
                newly_sai = []
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
                        if st == 'sai' and old.get('status') != 'sai':
                            newly_sai.append(key)
                    save_json(REVIEWS, rv)
                sualoi = {}
                for key in newly_sai:      # mã mới chấm Sai: tự tạo Sua_loi và chép file F (AI vẽ) vào
                    try:
                        sualoi[key] = ensure_sua_loi(*key.split('_', 1))
                    except Exception as e:
                        sualoi[key] = {'ok': False, 'why': str(e)}
                return self.send_json({'ok': True, 'reviews': rv, 'sualoi': sualoi})
            if path == '/api/sualoi':      # tạo lại Sua_loi + chép F của một mã Sai (khi lần đầu chưa thấy file)
                return self.send_json({'ok': True, 'result': ensure_sua_loi(data.get('order'), data.get('code'))})
            if path == '/api/jobs/check':
                return self.send_json(dict(add_check_job(data.get('order'), data.get('codes')), ok=True))
            if path == '/api/jobs/updscript':
                return self.send_json({'ok': True, 'job': add_updscript_job(data.get('files'))})
            if path == '/api/proposal/close':
                return self.send_json({'ok': True, 'moved': close_proposal(data.get('name'))})
            if path == '/api/jobs/updskill':
                return self.send_json({'ok': True, 'job': add_updskill_job(data.get('files'))})
            if path == '/api/jobs/hoiquy':
                return self.send_json({'ok': True, 'job': add_hoiquy_job(data.get('loai') or '')})
            if path == '/api/jobs/rutkn':
                return self.send_json({'ok': True, 'job': add_rutkn_job()})
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
            if path == '/api/ref/pick':
                return self.send_json({'ok': True, 'names': pick_refs(data.get('order'), data.get('code'))})
            if path == '/api/ref/delete':
                del_ref(data.get('order'), data.get('code'), data.get('name'))
                return self.send_json({'ok': True})
            if path == '/api/jobs/followup':
                return self.send_json({'ok': True, 'job': add_followup(data.get('order'), data.get('answers'), data.get('model'), data.get('redo') is True)})
            if path == '/api/compare_tf':
                return self.send_json(dict({'ok': True}, **compare_sualoi(data.get('order'), data.get('code'))))
            if path == '/api/raise':
                return self.send_json({'ok': raise_window()})
            if path == '/api/openorder':
                return self.send_json({'ok': True, 'path': open_order_dir(data.get('order'))})
            if path == '/api/openpart':
                return self.send_json({'ok': True, 'path': open_part(data.get('order'), data.get('code'))})
            if path == '/api/openpdf':
                return self.send_json(dict({'ok': True}, **open_pdf(data.get('order'), data.get('code'))))
            if path == '/api/openfile':
                return self.send_json({'ok': True, 'path': open_sualoi(data.get('order'), data.get('code'), data.get('kind'))})
            if path == '/api/jobs/resume':
                return self.send_json({'ok': True, 'job': add_resume(data.get('order'))})
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
