#!/usr/bin/env python3
"""dxf_check.py - kiểm tra DXF đầu ra của skill dxf-sheetmetal (file riêng 26-xxxxxx.dxf và file <đơn>_ALL.dxf).
Dùng: python3 dxf_check.py FILE.dxf [--template [--tpl Template.dxf]] [--mat SS|SUS|AL|CU --t 3.2]
       [--expect yeucau.csv] [--src THU_MUC_DON] [--order 064301,064302] [--mirror 064157:064158] [--single THU_MUC] [--png out.png]
expect.csv: code,X,Y[,mat,t] (X/Y của CAD依頼書). Mã thoát 1 nếu có LỖI.
Mặc định chỉ kiểm hình dạng; so cấu trúc file với Template (CRLF, header, owner 6F, handle...) chỉ chạy khi có --template."""
import sys, re, math, argparse, os, unicodedata, subprocess
from collections import defaultdict
import ezdxf

TOL = 1e-3
OUT = {'LỖI': [], 'CẢNH BÁO': [], 'THÔNG TIN': []}
CNT = defaultdict(int)
def rep(lv, msg):
    CNT[msg] += 1
    if CNT[msg] == 1: OUT[lv].append(msg)
def E(m): rep('LỖI', m)
def W(m): rep('CẢNH BÁO', m)
def I(m): rep('THÔNG TIN', m)
def f(v): return ('%.3f' % v).rstrip('0').rstrip('.')
def P(p): return '(%s; %s)' % (f(p[0]), f(p[1]))

STD_FLAGS = ['Kích thước PDF và DXF khác nhau', 'Kích thước giữa các hình chiếu không khớp', 'Thiếu kích thước',
             'Kích thước và hình dạng không khớp', 'Ghi chú tay không đọc rõ', 'Kích thước ghi quá mờ',
             'Không rõ kích thước trong hay ngoài', 'Số lượng lỗ ghi không khớp', 'Số lượng bo R hoặc vát C',
             'Độ giãn viết tay khác bảng', 'Không chắc mặt nào là mặt ngoài',
             'Không chắc trên tấm có Kegaki hay không']

PILOT = {}
for _th, _d in (('M3', 2.5), ('M3.5', 2.9), ('M4', 3.3), ('M5', 4.2), ('M6', 5), ('M7', 6), ('M8', 6.8), ('M10', 8.5), ('M12', 10.3)):
    PILOT.setdefault(round(_d, 2), []).append(_th)

# ---------- bảng laser (Quy_Tac_Laser.md mục 2) ----------
def laser_r(mat, t):
    if mat == 'SS': return 0.5 if t <= 5 else 2 if t <= 9 else None if t < 19 else 3
    if mat in ('SUS', 'AL'): return 0.5 if t <= 6 else None
    if mat == 'CU': return 0.5 if t <= 5 else None
def pierce_out(mat, t):
    # Piercing ngoai thang (Quy_Tac_Laser muc 2); None = piercing cong hoac khong ro
    if mat == 'SS': return 3 if t <= 3.2 else 6 if t <= 9 else 10 if t <= 16 else None
    if mat in ('SUS', 'AL'): return 6 if t <= 8 else 10 if t <= 16 else None
    if mat == 'CU': return 6
def min_hole(mat, t):
    if mat == 'SS': return t / 2 if t < 16 else t
    if mat == 'SUS': return t / 2 if t <= 14 else 10 if t < 20 else t
    if mat == 'AL': return 0.8 * t if t < 16 else t
    if mat == 'CU': return t / 2 if t <= 5 else t

# ---------- 1. cấu trúc file so với Template ----------
def split(path):
    raw = open(path, 'rb').read()
    try: s = raw.decode('cp932')
    except UnicodeDecodeError as e: E('Không decode được cp932: %s' % e); s = raw.decode('cp932', 'replace')
    if s.count('\n') != s.count('\r\n'):
        E('Có dòng kết thúc bằng LF, phải là CRLF (\\r\\n): file không ghi theo Template (mục 11.2 bước 7)')
        return s.replace('\r\n', '\n').split('\n')
    return s.split('\r\n')

def sec_idx(L):
    i = next(k for k in range(1, len(L)) if L[k] == 'ENTITIES' and L[k - 1].strip() == '2')
    return i, L.index('ENDSEC', i)

def check_structure(path, tpl):
    L, T = split(path), split(tpl)
    for k in range(0, len(L) - 1, 2):
        if not re.fullmatch(r'-?\d+', L[k].strip()):
            E('Dòng %d không phải mã nhóm số nguyên: %r (lệch cặp mã/giá trị)' % (k + 1, L[k])); break
    try: i, j = sec_idx(L); ti, tj = sec_idx(T)
    except (StopIteration, ValueError): E('Không tìm thấy mục ENTITIES/ENDSEC'); return None
    if L[j - 1].strip() != '0': E("Thiếu mã '  0' trước ENDSEC của ENTITIES (lỗi ghép L[j:] thay vì L[j-1:])")
    if L[j - 1:] != T[tj - 1:]:
        d = next((k for k, (a, b) in enumerate(zip(L[j - 1:], T[tj - 1:])) if a != b), None)
        E('Phần từ ENDSEC của ENTITIES đến hết file khác Template (dòng lệch đầu tiên ~%s)' % (j + d if d is not None else 'độ dài'))
    H, TH = L[:i + 1], T[:ti + 1]
    if len(H) != len(TH):
        E('Phần trước ENTITIES khác số dòng so với Template (%d / %d): có thêm/bớt header, bảng hoặc style' % (len(H), len(TH)))
    else:
        ok = set()
        def blk(name, n):
            k = H.index(name); ok.update(range(k, k + n))
        blk('$EXTMAX', 7); blk('$HANDSEED', 3)
        k = H.index('*Active'); m = k
        while H[m] != '  0' or m == k: m += 1
        ok.update(range(k - 30, m))
        k = H.index('Standard', H.index('AcDbTextStyleTableRecord')); m = k
        while H[m] != '  0': m += 1
        ok.update(range(k, m))
        bad = [k for k in range(len(H)) if H[k] != TH[k] and k not in ok]
        if bad: E('Ngoài ENTITIES khác Template ở dòng %s (chỉ được khác EXTMAX, HANDSEED, VPORT *Active, mã 3 của Standard)' % ', '.join(str(b + 1) for b in bad[:8]))
    k = H.index('Standard', H.index('AcDbTextStyleTableRecord')); m = k
    while H[m] != '  3': m += 1
    if H[m + 1].lower() != 'arial.ttf': E("Style Standard mã 3 = %r, phải là 'arial.ttf' (SHX txt hiện '?' thay dấu)" % H[m + 1])
    ent = L[i + 1:j - 1]; hs = []
    for k in range(0, len(ent) - 1, 2):
        c, v = int(ent[k]), ent[k + 1]
        if 10 <= c <= 59 and not re.fullmatch(r'-?\d+(\.\d+)?', v.strip()): E('Số sai định dạng trong ENTITIES: mã %d = %r (không dùng 1e-05, nan, inf)' % (c, v))
        if c == 5: hs.append(int(v, 16))
        if c == 330 and v != '6F': E('Entity có owner 330 = %s, phải là 6F' % v)
        if c == 1 and any(ord(ch) > 127 for ch in v): E('TEXT có ký tự ngoài ASCII %r: phải ghi dạng \\U+XXXX' % v[:30])
    seed = lambda X: int(X[X.index('$HANDSEED') + 2], 16)
    if len(set(hs)) != len(hs): E('Trùng handle entity')
    if hs:
        if min(hs) < seed(T): E('Handle entity %X nhỏ hơn HANDSEED của Template (%X): có thể trùng handle mẫu' % (min(hs), seed(T)))
        if seed(L) <= max(hs): E('$HANDSEED (%X) phải lớn hơn handle lớn nhất (%X)' % (seed(L), max(hs)))
    ex = L.index('$EXTMAX')
    return float(L[ex + 2]), float(L[ex + 4])

# ---------- 2. hình học ----------
def arc_pts(c, r, a0, a1):
    a1 = a1 if a1 > a0 else a1 + 360
    p = lambda a: (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
    return p(a0), p(a1), [p(a) for a in range(int(a0 // 90 + 1) * 90, int(a1) + 1, 90) if a0 < a < a1]

class Seg:
    def __init__(s, e):
        s.e, s.t = e, e.dxftype()
        if s.t == 'LINE':
            s.p, s.q = tuple(e.dxf.start)[:2], tuple(e.dxf.end)[:2]; s.ext = []
        else:
            s.c, s.r = tuple(e.dxf.center)[:2], e.dxf.radius
            s.a0, s.a1 = e.dxf.start_angle % 360, e.dxf.end_angle % 360
            s.p, s.q, s.ext = arc_pts(s.c, s.r, s.a0, s.a1)
    def pts(s): return [s.p, s.q] + s.ext
    def trav(s, at_q):
        """hướng đi p→q tại p hoặc q"""
        if s.t == 'LINE': d = (s.q[0] - s.p[0], s.q[1] - s.p[1])
        else: a = math.radians(s.a1 if at_q else s.a0); d = (-math.sin(a), math.cos(a))
        n = math.hypot(*d) or 1
        return (d[0] / n, d[1] / n)
    def poly(s, n=8):
        if s.t == 'LINE': return [s.p, s.q]
        a1 = s.a1 if s.a1 > s.a0 else s.a1 + 360
        return [(s.c[0] + s.r * math.cos(math.radians(s.a0 + (a1 - s.a0) * k / n)), s.c[1] + s.r * math.sin(math.radians(s.a0 + (a1 - s.a0) * k / n))) for k in range(n + 1)]

def near(a, b, t=TOL * 2): return abs(a[0] - b[0]) < t and abs(a[1] - b[1]) < t

def loops(segs, where):
    reps, node, gap = [], defaultdict(list), []
    def kk(p):
        for r in reps:
            d = math.hypot(p[0] - r[0], p[1] - r[1])
            if d < 0.01:
                if d > 1e-6: gap.append((p, d))
                return r
        reps.append(p); return p
    for s in segs: node[kk(s.p)].append((s, True)); node[kk(s.q)].append((s, False))
    for p, d in gap[:3]: W('%s: đầu mút lệch %s mm tại %s (nối được nhưng nên làm khớp tuyệt đối)' % (where, f(d), P(p)))
    for k, v in node.items():
        if len(v) == 1: E('%s: hở biên tại %s (đầu mút LINE/ARC không nối)' % (where, P(k)))
        elif len(v) > 2: W('%s: %d đoạn chung 1 điểm %s (trùng/chồng nét)' % (where, len(v), P(k)))
    used, out = set(), []
    for s0 in segs:
        if id(s0) in used: continue
        lp, s, fwd = [], s0, True
        while s is not None and id(s) not in used:
            used.add(id(s)); lp.append((s, fwd))
            end = s.q if fwd else s.p
            nx = [(t, fp) for t, fp in node[kk(end)] if id(t) not in used]
            s, fwd = (nx[0][0], nx[0][1]) if nx else (None, True)
        out.append(lp)
    return out

def lpoly(lp):
    pts = []
    for s, fw in lp:
        q = s.poly(); pts += q if fw else q[::-1]
    return pts
def area(pts): return sum(pts[k - 1][0] * pts[k][1] - pts[k][0] * pts[k - 1][1] for k in range(len(pts))) / 2
def inside(pt, poly):
    x, y, c = pt[0], pt[1], False
    for k in range(len(poly)):
        (x1, y1), (x2, y2) = poly[k - 1], poly[k]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def dseg(pt, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]; L2 = vx * vx + vy * vy or 1e-12
    u = max(0, min(1, ((pt[0] - a[0]) * vx + (pt[1] - a[1]) * vy) / L2))
    return math.hypot(a[0] + u * vx - pt[0], a[1] + u * vy - pt[1])
def on_poly(pt, poly, t=0.01): return any(dseg(pt, poly[k - 1], poly[k]) < t for k in range(len(poly)))
def overlap(a, b, c, d, t=0.01):
    """2 đoạn thẳng thẳng hàng và chồng lên nhau một khoảng > t"""
    if dseg(c, a, b) > t and dseg(d, a, b) > t: return False
    ux, uy = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uy) or 1
    if abs(((d[0] - c[0]) * uy - (d[1] - c[1]) * ux) / L) > t: return False
    pr = sorted([((c[0] - a[0]) * ux + (c[1] - a[1]) * uy) / L, ((d[0] - a[0]) * ux + (d[1] - a[1]) * uy) / L])
    return min(L, pr[1]) - max(0, pr[0]) > t

def classify(e):
    t, col, lt = e.dxftype(), e.dxf.color, e.dxf.linetype.upper()
    if e.dxf.layer != '0': W('%s handle %s ở layer %r, phải là layer 0' % (t, e.dxf.handle, e.dxf.layer))
    if t == 'TEXT': return 'text'
    if t == 'POINT': return 'point'
    if t not in ('LINE', 'ARC', 'CIRCLE'): E('Entity %s (handle %s) không thuộc LINE/CIRCLE/ARC/POINT/TEXT' % (t, e.dxf.handle)); return None
    if lt == 'DASHED':
        if t != 'LINE' or col not in (256, 7): W('Nét DASHED trên %s màu %s: đường uốn chỉ là LINE trắng' % (t, col))
        return 'bend'
    if lt not in ('BYLAYER', 'CONTINUOUS'): W('%s handle %s dùng linetype %s' % (t, e.dxf.handle, lt))
    if col in (256, 7, 0): return 'hole' if t == 'CIRCLE' else 'cut'
    if col == 3: return 'green'
    if col == 1: return 'keg'
    E('%s handle %s màu %d không đúng quy ước (trắng, Green 3, Đỏ 1)' % (t, e.dxf.handle, col)); return None

def bbox(items):
    xs, ys = [], []
    for c, e in items:
        if c in ('cut', 'green', 'bend', 'keg') and e.dxftype() in ('LINE', 'ARC'):
            for p in Seg(e).pts(): xs.append(p[0]); ys.append(p[1])
        elif e.dxftype() == 'CIRCLE':
            x, y, r = e.dxf.center.x, e.dxf.center.y, e.dxf.radius; xs += [x - r, x + r]; ys += [y - r, y + r]
        elif c == 'point': xs.append(e.dxf.location.x); ys.append(e.dxf.location.y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None

def sig(items, x0, y0, tf=lambda p: p):
    """chữ ký hình học (để so file riêng/ALL và cặp gương); tf: phép biến hình trên tọa độ đã chuẩn hóa"""
    S = []
    for c, e in items:
        if c == 'text': continue
        t = e.dxftype(); g = lambda p: tuple(round(v, 2) + 0.0 for v in tf((p[0] - x0, p[1] - y0)))
        if t == 'LINE': S.append((c, 'L') + tuple(sorted([g(e.dxf.start), g(e.dxf.end)])))
        elif t == 'CIRCLE': S.append((c, 'C', g(e.dxf.center), round(e.dxf.radius, 3)))
        elif t == 'ARC':
            s = Seg(e); S.append((c, 'A', g(s.c), round(s.r, 3)) + tuple(sorted([g(s.p), g(s.q)])))
        elif t == 'POINT': S.append((c, 'P', g(e.dxf.location)))
    return sorted(S)

def decode_u(s): return unicodedata.normalize('NFC', re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s))

# ---------- 3. kiểm từng hình ----------
def check_part(name, items, mat, t, is_all):
    segs = [Seg(e) for c, e in items if c == 'cut']
    if not segs:
        cs = sorted([e for c, e in items if c == 'hole'], key=lambda e: -e.dxf.radius)
        if not cs: E('%s: không có biên cắt' % name); return None
        o = cs[0]; items = [(('cut' if e is o else c), e) for c, e in items]
        x, y, r = o.dxf.center.x, o.dxf.center.y, o.dxf.radius
        if abs(x - r) > TOL: E('%s: phôi tròn φ%s, mép trái ở X = %s' % (name, f(2 * r), f(x - r)))
        I('%s: phôi tròn φ%s; lỗ %s; kegaki %d' % (name, f(2 * r), ', '.join('φ%s' % f(2 * e.dxf.radius) for e in cs[1:]) or '0', sum(1 for c, _ in items if c == 'keg')))
        return (x - r, y - r, x + r, y + r), 2 * r, 2 * r
    bb = bbox([(c, e) for c, e in items if c == 'cut'])
    Wd, Hd = bb[2] - bb[0], bb[3] - bb[1]
    lps = loops(segs, name)
    polys = [(lp, lpoly(lp)) for lp in lps]
    polys.sort(key=lambda x: -abs(area(x[1])))
    outer_lp, outer = polys[0]
    for lp, pg in polys[1:]:
        if not inside(pg[0], outer) and not on_poly(pg[0], outer): E('%s: vòng biên rời nằm ngoài biên ngoài tại %s (2 phôi trong 1 hình?)' % (name, P(pg[0])))
    ori = 1 if area(outer) > 0 else -1
    # góc trên biên ngoài
    sharp_cvx, sharp_ccv, radii = [], [], defaultdict(int)
    for k in range(len(outer_lp)):
        (a, fa), (b, fb) = outer_lp[k - 1], outer_lp[k]
        da = a.trav(True) if fa else tuple(-v for v in a.trav(False))
        db = b.trav(False) if fb else tuple(-v for v in b.trav(True))
        cr = da[0] * db[1] - da[1] * db[0]; dot = da[0] * db[0] + da[1] * db[1]
        turn = math.degrees(math.atan2(cr, dot))
        if abs(turn) < 1: continue
        inner = 180 - abs(turn); pt = b.p if fb else b.q
        if turn * ori > 0 and inner <= 91: sharp_cvx.append((pt, inner))
        elif turn * ori < 0: sharp_ccv.append((pt, 180 + abs(turn)))
        if a.t == 'ARC' and b.t == 'ARC' and near(a.c, b.c) and abs(a.r - b.r) < TOL: W('%s: 2 ARC liền nhau cùng tâm/bán kính tại %s, gộp thành 1' % (name, P(pt)))
    for lp, _ in polys:
        for s, _f in lp:
            if s.t == 'ARC': radii[round(s.r, 3)] += 1
    rexp = laser_r(mat, t) if mat else None
    if sharp_cvx:
        lst = ', '.join('%s %s°' % (P(p), f(a)) for p, a in sharp_cvx[:6])
        if mat and rexp is None: I('%s: %d góc lồi sắc (đúng vì %s t%s không bo): %s' % (name, len(sharp_cvx), mat, f(t), lst))
        else: E('%s: %d góc lồi ≤ 90° chưa bo%s: %s (trừ khi khách quy định không bo)' % (name, len(sharp_cvx), ' R%s' % f(rexp) if rexp else ' (thiếu --mat/--t)', lst))
    if mat == 'SS' and t >= 19 and sharp_ccv: E('%s: thép ≥19t phải bo R3 cả góc lõm, còn %d góc lõm sắc' % (name, len(sharp_ccv)))
    small = [r for r in radii if rexp and r < rexp - TOL]
    if small: I('%s: có cung R%s nhỏ hơn Laser R%s (hạ R vì góc quá nhỏ? phải nêu trong báo cáo)' % (name, '/R'.join(f(r) for r in small), f(rexp)))
    if mat and rexp is None and rexp != 3 and radii.get(0.5): W('%s: vật liệu %s t%s không bo laser nhưng có %d cung R0.5' % (name, mat, f(t), radii[0.5]))
    # lỗ
    holes = defaultdict(int); dmin = min_hole(mat, t) if mat else None
    pts_hole = []
    for c, e in items:
        if c == 'hole':
            ctr = (e.dxf.center.x, e.dxf.center.y); d = 2 * e.dxf.radius; holes[round(d, 3)] += 1
            if not inside(ctr, outer): E('%s: lỗ φ%s tâm %s nằm ngoài biên phôi' % (name, f(d), P(ctr)))
            if dmin and d < dmin - TOL: W('%s: lỗ φ%s < lỗ nhỏ nhất %s (%s t%s): phải là POINT, trừ quy định khách (vd 810)' % (name, f(d), f(dmin), mat, f(t)))
        if c == 'point':
            pt = (e.dxf.location.x, e.dxf.location.y)
            if not inside(pt, outer) and not on_poly(pt, outer): E('%s: POINT %s nằm ngoài phôi' % (name, P(pt)))
            jl = [(x.dxf.insert.x, x.dxf.insert.y) for k, x in items if k == 'text' and x.dxf.text in ('J', 'LJ')]
            if not any(abs(pt[0] - a) < 0.01 and abs(pt[1] - b) < 0.01 for a, b in jl): pts_hole.append(pt)
    if pts_hole and dmin:
        W('%s: %d POINT lỗ (%s): chỉ đúng khi lỗ gốc (kể cả lỗ mồi) < lỗ nhỏ nhất %s (%s t%s) hoặc ghi chú tay ピアス khoanh riêng quanh lỗ đó (tem PIERCING đầu trang không đủ); lỗ ren có lỗ mồi ≥ %s phải vẽ CIRCLE (lỗi 521030-12)' % (name, len(pts_hole), ', '.join(P(p) for p in pts_hole[:4]), f(dmin), mat, f(t), f(dmin)))
    # đường uốn
    bends = [Seg(e) for c, e in items if c == 'bend']
    cand = []
    for x in range(len(bends)):
        for y in range(x + 1, len(bends)):
            A, B = bends[x], bends[y]
            u = (A.q[0] - A.p[0], A.q[1] - A.p[1]); L = math.hypot(*u) or 1; v = (B.q[0] - B.p[0], B.q[1] - B.p[1])
            if abs(u[0] * v[1] - u[1] * v[0]) / (L * (math.hypot(*v) or 1)) > 1e-4: continue
            dist = abs((B.p[0] - A.p[0]) * u[1] - (B.p[1] - A.p[1]) * u[0]) / L
            pr = sorted([((B.p[0] - A.p[0]) * u[0] + (B.p[1] - A.p[1]) * u[1]) / L, ((B.q[0] - A.p[0]) * u[0] + (B.q[1] - A.p[1]) * u[1]) / L])
            if 0.05 < dist < 30 and min(L, pr[1]) - max(0, pr[0]) > 0.5 * min(L, pr[1] - pr[0]): cand.append((dist, x, y))
    paired, pairs = set(), []
    for dist, x, y in sorted(cand):
        if x not in paired and y not in paired: paired.update((x, y)); pairs.append((bends[x], bends[y], dist))
    for k, s in enumerate(bends):
        if k not in paired: W('%s: đường uốn %s→%s không có cặp (mỗi chỗ uốn 2 LINE DASHED cách nhau = độ giãn)' % (name, P(s.p), P(s.q)))
        mid = ((s.p[0] + s.q[0]) / 2, (s.p[1] + s.q[1]) / 2)
        if not inside(mid, outer): E('%s: đường uốn %s→%s nằm ngoài phôi' % (name, P(s.p), P(s.q)))
    # rạch Green
    gs = [Seg(e) for c, e in items if c == 'green']
    for s in gs:
        if s.t == 'ARC' and abs(s.r - 0.5) > TOL: W('%s: cung rạch Green R%s, chuẩn là R0.5' % (name, f(s.r)))
    pexp = pierce_out(mat, t) if mat else None
    for s in gs:
        if s.t != 'LINE': continue
        dx, dy = s.q[0] - s.p[0], s.q[1] - s.p[1]; Ls = math.hypot(dx, dy)
        if Ls < 1e-6: continue
        if abs(abs(dx) - abs(dy)) < 1e-3 * Ls:
            # LINE cheo 45: dai = (Piercing - 0.146) x sqrt2 (diem dau cach moi mep khoet = Piercing ngoai)
            pc = Ls / math.sqrt(2) + 0.5 - 0.5 / math.sqrt(2)
            if pexp and abs(pc - pexp) > 0.05:
                E('%s: rạch Green %s→%s: điểm đầu cách mép khoét %s, chuẩn = Piercing ngoài %s (%s t%s)' % (name, P(s.p), P(s.q), f(pc), f(pexp), mat, f(t)))
        elif t and (abs(dx) < 1e-6 or abs(dy) < 1e-6):
            dep = Ls + 0.5 * (math.sqrt(2) - 1)
            if abs(dep - (t + 0.2)) > 0.05:
                W('%s: rạch Green %s→%s sâu %s tính từ góc khoét, chuẩn t + 0.2 = %s' % (name, P(s.p), P(s.q), f(dep), f(t + 0.2)))
    ng = len(gs)
    if ng % 3: W('%s: %d entity Green, mỗi đường rạch chuẩn gồm 3 (LINE, ARC R0.5, LINE)' % (name, ng))
    nearb = lambda p: any(dseg(p, b.p, b.q) < 6 for b in bends)
    nog = [p for p, a in sharp_ccv if abs(a - 270) < 1 and nearb(p) and not any(min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in s.pts()) < 1.2 for s in gs)]
    if nog: W('%s: %d góc lõm 90° sát đường uốn không có rạch Green: %s (vách–tấm/hộp phải rạch; ngoại lệ: hộp vát 135°, khoét relief, mép thân nằm giữa 2 đường uốn)' % (name, len(nog), ', '.join(P(p) for p in nog[:6])))
    # kegaki
    obl = [(s.p, s.q) for s in segs if s.t == 'LINE']; bl = [(s.p, s.q) for s in bends]
    nk = 0
    for c, e in items:
        if c != 'keg': continue
        nk += 1
        if e.dxftype() == 'LINE':
            p, q = tuple(e.dxf.start)[:2], tuple(e.dxf.end)[:2]
            mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if not inside(mid, outer) and not on_poly(mid, outer): E('%s: kegaki %s→%s nằm ngoài phôi' % (name, P(p), P(q)))
            if any(overlap(a, b, p, q) for a, b in obl): E('%s: kegaki %s→%s trùng mép phôi (phải bỏ)' % (name, P(p), P(q)))
            if any(overlap(a, b, p, q) for a, b in bl): E('%s: kegaki %s→%s trùng đường uốn (phải bỏ)' % (name, P(p), P(q)))
        elif e.dxftype() == 'ARC':
            # cung kegaki lớn (tâm có thể ở ngoài phôi): kiểm điểm đầu, giữa, cuối cung
            a0, a1 = e.dxf.start_angle, e.dxf.end_angle
            sw = (a1 - a0) % 360
            cx, cy, r = e.dxf.center.x, e.dxf.center.y, e.dxf.radius
            for k in (0.02, 0.5, 0.98):
                a = math.radians(a0 + sw * k); pt = (cx + r * math.cos(a), cy + r * math.sin(a))
                if not inside(pt, outer) and not on_poly(pt, outer):
                    E('%s: kegaki ARC nằm ngoài phôi' % name); break
        elif not inside((e.dxf.center.x, e.dxf.center.y), outer): E('%s: kegaki %s nằm ngoài phôi' % (name, e.dxftype()))
    # trùng nét, nét 0
    seen = set()
    for c, e in items:
        if c == 'text': continue
        s = tuple(sig([(c, e)], 0, 0))
        if s in seen: E('%s: entity trùng lặp %s' % (name, s[0][:3]))
        seen.add(s)
        if e.dxftype() == 'LINE' and near(e.dxf.start, e.dxf.end): E('%s: LINE dài 0 tại %s' % (name, P(e.dxf.start)))
    # áp trục, chiều dài theo X
    ax = any(s.t == 'LINE' and abs(s.p[1] - bb[1]) < TOL and abs(s.q[1] - bb[1]) < TOL for s in segs)
    ay = any(s.t == 'LINE' and abs(s.p[0] - bb[0]) < TOL and abs(s.q[0] - bb[0]) < TOL for s in segs)
    if not (ax and ay): W('%s: không có cạnh thẳng áp %s (chọn hướng có cạnh trên cả Ox và Oy, mục 10)' % (name, ' và '.join(n for n, ok in (('Ox', ax), ('Oy', ay)) if not ok)))
    if Hd > Wd + TOL: W('%s: cạnh dài hơn nằm theo Y (%s x %s), quy tắc: cạnh dài theo X' % (name, f(Wd), f(Hd)))
    # J/LJ phôi dài hẹp
    pts = [(e.dxf.location.x, e.dxf.location.y) for c, e in items if c == 'point' and abs(e.dxf.location.y - bb[3]) < TOL]
    if Hd <= 100 and Wd >= 1000:
        nJ = 1 if Wd <= 1500 else 2 if Wd <= 2000 else 3 if Wd <= 2500 else None
        if nJ:
            # đầu mép trên vát C (LINE chéo nối vào): tính 30 từ đầu đoạn thẳng (30/10/2026, 521030-09); đầu bo R giữ theo khung
            top = [q for q in segs if q.t == 'LINE' and abs(q.p[1] - bb[3]) < TOL and abs(q.q[1] - bb[3]) < TOL]
            x0, x1 = bb[0], bb[2]
            if top:
                tl, tr = min(min(q.p[0], q.q[0]) for q in top), max(max(q.p[0], q.q[0]) for q in top)
                def chamfer(xe):
                    return any(q.t == 'LINE' and abs(q.p[0] - q.q[0]) > TOL and abs(q.p[1] - q.q[1]) > TOL and (near(q.p, (xe, bb[3]), TOL) or near(q.q, (xe, bb[3]), TOL)) for q in segs)
                if chamfer(tl): x0 = tl
                if chamfer(tr): x1 = tr
            xs = [x0 + 30 + (x1 - x0 - 60) * k / nJ for k in range(nJ + 1)]
            miss = [x for x in xs if not any(abs(p[0] - x) < 0.01 for p in pts)]
            if miss: E('%s: phôi dài hẹp %s x %s cần %d J + 1 LJ trên mép trên, thiếu POINT tại x = %s' % (name, f(Wd), f(Hd), nJ, ', '.join(f(x - bb[0]) for x in miss)))
            tx = [(e.dxf.text, (e.dxf.insert.x, e.dxf.insert.y), e.dxf.height) for c, e in items if c == 'text' and e.dxf.text in ('J', 'LJ')]
            for k, x in enumerate(xs):
                want = 'LJ' if k == nJ else 'J'
                if not any(tt == want and near(p, (x, bb[3]), 0.01) and abs(h - 10) < TOL for tt, p, h in tx): E('%s: thiếu TEXT %s cao 10 tại %s' % (name, want, P((x, bb[3]))))
        else: W('%s: phôi dài %s > 2500, quy tắc J/LJ chưa có, hỏi người dùng' % (name, f(Wd)))
    elif pts and Hd > 100: W('%s: có POINT trên mép trên nhưng phôi không thuộc loại dài hẹp' % name)
    pil = ['%dxφ%s (%s)' % (n, f(d), '/'.join(PILOT[round(d, 2)])) for d, n in sorted(holes.items()) if round(d, 2) in PILOT]
    if pil: I('%s: lỗ trùng lỗ mồi taro theo bảng: %s; đối chiếu ghi chú tay 下穴 / lỗ mồi trong PDF (ghi chú tay thắng bảng, mục 7 dxf-sheetmetal)' % (name, ', '.join(pil)))
    I('%s: %s x %s | %d vòng biên, lỗ %s, cung %s, uốn %d cặp (giãn %s), Green %d, kegaki %d' % (
        name, f(Wd), f(Hd), len(lps), ', '.join('%dxφ%s' % (n, f(d)) for d, n in sorted(holes.items())) or '0',
        ', '.join('%dxR%s' % (n, f(r)) for r, n in sorted(radii.items())) or '0', len(pairs),
        '/'.join(sorted({f(d) for _, _, d in pairs})) or '-', ng, nk))
    return bb, Wd, Hd

# ---------- 4. chương trình chính ----------
# ---------- 4. đối chiếu nguồn: PDF bản vẽ + DXF khách (kỳ vọng dựng độc lập với file đang kiểm) ----------
NUM = r'(\d+(?:\.\d+)?)'
PILOT_D = {3: 2.5, 3.5: 2.9, 4: 3.3, 5: 4.2, 6: 5, 7: 6, 8: 6.8, 10: 8.5, 12: 10.3}
def norm_txt(s): return unicodedata.normalize('NFKC', s).translate({ord(c): 'φ' for c in 'ΦϕØø⌀∅Ф'})

def src_files(src):
    pdfs, dxfs = [], []
    for fn in sorted(os.listdir(src)):
        p, u = os.path.join(src, fn), fn.upper()
        if not os.path.isfile(p): continue
        if u.endswith('.PDF'): pdfs.append(p)
        elif u.endswith('.DXF') and not u.endswith('_ALL.DXF') and not re.match(r'26-\d{6}\.DXF', u): dxfs.append(p)
    return pdfs, dxfs

def pdf_pages(p):
    try: out = subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
    except (OSError, subprocess.SubprocessError): return None
    return [norm_txt(x) for x in out.split('\f')[:-1]] or [norm_txt(out)]

def notes(txt):
    """ghi chú đọc được từ chữ PDF: n-φ, φ rời, taro M, 下穴, R, 展開, mã 6 số"""
    return {'hole': [(int(a), round(float(b), 2)) for a, b in re.findall(r'(\d+)\s*[-ー–]\s*φ\s*' + NUM, txt)],
            'phi': {round(float(x), 2) for x in re.findall(r'φ\s*' + NUM, txt)},
            'tap': {float(x) for x in re.findall(r'(?<![A-Za-z])M\s*' + NUM, txt)},
            'pilot': {round(float(x), 2) for x in re.findall(r'下穴\s*φ?\s*' + NUM, txt) + re.findall(r'(?<![A-Za-z\d.])' + NUM + r'\s*下穴', txt)},
            'R': {round(float(x), 2) for x in re.findall(r'(?<![A-Za-z])R\s*' + NUM, txt)},
            'dev': {round(float(x), 2) for x in re.findall(r'展開(?:長|寸法)?\s*[:：=]?\s*' + NUM, txt)},
            'codes': set(re.findall(r'(?<!\d)(0\d{5})(?!\d)', txt))}

def dxf_khach(p):
    """CIRCLE/ARC/khung bao của DXF khách (mở cả BLOCK/INSERT)"""
    circ, arcs, xs, ys = [], [], [], []
    def walk(ents, depth=0):
        for e in ents:
            t = e.dxftype()
            if t == 'INSERT' and depth < 4:
                try: walk(e.virtual_entities(), depth + 1)
                except Exception: pass
            elif t == 'CIRCLE':
                circ.append(round(2 * e.dxf.radius, 2)); r = e.dxf.radius
                xs.extend([e.dxf.center.x - r, e.dxf.center.x + r]); ys.extend([e.dxf.center.y - r, e.dxf.center.y + r])
            elif t == 'ARC': arcs.append(round(e.dxf.radius, 2))
            elif t == 'LINE': xs.extend([e.dxf.start.x, e.dxf.end.x]); ys.extend([e.dxf.start.y, e.dxf.end.y])
    walk(ezdxf.readfile(p).modelspace())
    return circ, arcs, ((max(xs) - min(xs), max(ys) - min(ys)) if xs else None)

def union(sets): return set().union(*sets) if sets else set()

def check_source(src, parts, mat_of):
    """parts: [y0, y1, items, tên, items, Wd, Hd]; mat_of(tên) -> (mat, t)"""
    pdfs, dxfs = src_files(src)
    if not pdfs and not dxfs:
        W('NGUỒN: không có PDF/DXF khách trong %s: chưa có kỳ vọng độc lập nên CHƯA kết luận được đúng/sai; stage thư mục đơn rồi chạy lại với --src' % src); return
    I('NGUỒN: %d PDF, %d DXF khách trong %s' % (len(pdfs), len(dxfs), src))
    pn = []   # (nơi, notes)
    for p in pdfs:
        pg = pdf_pages(p)
        if pg is None: W('NGUỒN: không chạy được pdftotext cho %s (cài poppler-utils); đọc PDF bằng tay' % os.path.basename(p)); continue
        scan = []
        for k, tx in enumerate(pg):
            if len(tx.strip()) < 20: scan.append(k + 1)
            else: pn.append(notes(tx))
        if scan: W('NGUỒN: %s trang %s không có lớp chữ (bản scan): đọc ảnh (pdftoppm -r 200) rồi tự dựng kỳ vọng: phôi, lỗ, 下穴, R, giãn, kegaki' % (os.path.basename(p), ','.join(map(str, scan))))
    dx = {}
    for p in dxfs:
        try: dx[p] = dxf_khach(p)
        except Exception as ex: W('NGUỒN: không đọc được DXF khách %s: %s' % (os.path.basename(p), ex)); continue
        c, a, bb = dx[p]
        I('NGUỒN: DXF khách %s: %d CIRCLE (φ %s), %d ARC, khung %s' % (os.path.basename(p), len(c), ', '.join(f(x) for x in sorted(set(c))[:12]) or '-', len(a), ('%s x %s' % (f(bb[0]), f(bb[1]))) if bb else '-'))
    drawn_all = set()
    for pt in parts:
        if len(pt) < 7: continue
        name, its, Wd, Hd = pt[3], pt[4], pt[5], pt[6]
        dr = defaultdict(int)
        for c, e in its:
            if c == 'hole': dr[round(2 * e.dxf.radius, 2)] += 1
        drawn_all |= set(dr)
        mine = [n for n in pn if name in n['codes']]
        mydx = [v for p, v in dx.items() if name in os.path.basename(p)]
        if pn and not mine: I('%s: không trang PDF nào có chữ mã này: chỉ so ở mức toàn đơn, tự đối chiếu theo hình' % name)
        pool = mine or pn
        pil, tap = union([n['pilot'] for n in pool]), union([n['tap'] for n in pool])
        pil_known = pil if mine else set()   # 下穴 chỉ áp lên hình khi trang PDF có đúng mã đó
        known = union([n['phi'] for n in pool]) | {round(PILOT_D[m], 2) for m in tap if m in PILOT_D} | pil
        for c, a, bb in (mydx or list(dx.values())): known |= set(c)
        for d, k in sorted(dr.items()):
            if d not in known: (W if mine or mydx else I)('%s: %d lỗ φ%s không có trong nguồn (PDF%s/DXF khách): sai φ hoặc lỗ thừa' % (name, k, f(d), '' if mine else ', toàn đơn - PDF không ghi mã nên chỉ để tham khảo'))
        for d in sorted(pil_known):
            if d not in dr: W('%s: PDF ghi 下穴φ%s nhưng hình không có lỗ φ%s (lỗi 064171: vẽ theo bảng lỗ mồi)' % (name, f(d), f(d)))
            else: I('%s: 下穴φ%s trong PDF khớp lỗ đã vẽ' % (name, f(d)))
        if pil_known:
            for d, k in dr.items():
                if d in PILOT and d not in pil: W('%s: %d lỗ φ%s (= lỗ mồi %s theo bảng) trong khi PDF có 下穴φ%s: ghi chú tay thắng bảng, đối chiếu từng nhóm' % (name, k, f(d), '/'.join(PILOT[d]), '/'.join(f(x) for x in sorted(pil))))
        if len(mine) == 1 and len(mine[0]['codes']) == 1:   # trang chỉ có 1 mã: đếm được
            tot = defaultdict(int)
            for k, d in mine[0]['hole']: tot[d] += k
            for d, k in sorted(tot.items()):
                if d not in pil and dr.get(d, 0) != k: W('%s: PDF ghi tổng %d-φ%s, hình có %d lỗ φ%s (đếm lại từng ghi chú; lỗ bị gạch thì bỏ qua)' % (name, k, f(d), dr.get(d, 0), f(d)))
        for x in sorted(union([n['dev'] for n in mine])):
            if not (abs(Wd - x) < 0.05 or abs(Hd - x) < 0.05): W('%s: PDF ghi 展開 %s, phôi %s x %s' % (name, f(x), f(Wd), f(Hd)))
        if mine:
            mt, t = mat_of(name); lr = laser_r(mt, t) if mt and t else None
            pr = union([n['R'] for n in mine]); arcs = {round(Seg(e).r, 2) for c, e in its if c == 'cut' and e.dxftype() == 'ARC'}
            miss = sorted(x for x in pr if x not in arcs and x != lr); extra = sorted(x for x in arcs if x not in pr and x != lr)
            if miss: I('%s: R trong PDF mà hình không có cung R đó: %s (R ở hình chiếu khác thì bỏ qua)' % (name, ', '.join(f(x) for x in miss)))
            if extra: I('%s: cung R trong hình mà PDF không ghi: %s (R lấy từ DXF khách/hạ R thì bỏ qua)' % (name, ', '.join(f(x) for x in extra)))
        for c, a, bb in mydx:
            if bb and not ((abs(Wd - bb[0]) < 0.1 and abs(Hd - bb[1]) < 0.1) or (abs(Wd - bb[1]) < 0.1 and abs(Hd - bb[0]) < 0.1)):
                I('%s: khung DXF khách %s x %s khác phôi %s x %s (phôi uốn/DXF nhiều hình thì bình thường; đối chiếu tay)' % (name, f(bb[0]), f(bb[1]), f(Wd), f(Hd)))
    want = {d for n in pn for k, d in n['hole'] if d not in union([x['pilot'] for x in pn])}
    for d in sorted(want - drawn_all): W('NGUỒN: PDF ghi n-φ%s nhưng không hình nào vẽ lỗ φ%s (lỗ gạch/lỗ ren thì bỏ qua, còn lại là thiếu lỗ)' % (f(d), f(d)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file'); ap.add_argument('--tpl', default='/mnt/project-files/knowledge/Context_Laser/Template.dxf')
    ap.add_argument('--template', action='store_true', help='bật so cấu trúc file với Template (mặc định tắt, chỉ kiểm hình dạng)')
    ap.add_argument('--mat', choices=['SS', 'SUS', 'AL', 'CU']); ap.add_argument('--t', type=float)
    ap.add_argument('--expect'); ap.add_argument('--order'); ap.add_argument('--mirror', action='append', default=[])
    ap.add_argument('--single'); ap.add_argument('--png')
    ap.add_argument('--src', help='thư mục đơn chứa PDF bản vẽ/依頼 và DXF khách (mặc định: thư mục của FILE); đối chiếu kỳ vọng từ nguồn')
    a = ap.parse_args()
    is_all = a.file.upper().endswith('_ALL.DXF')
    exp = {}
    if a.expect:
        for ln in open(a.expect, encoding='utf-8-sig'):
            r = [x.strip() for x in ln.split(',')]
            if len(r) >= 3 and re.fullmatch(r'\d{6}', r[0]):
                exp[r[0]] = (float(r[1]), float(r[2]), r[3] if len(r) > 3 and r[3] else None, float(r[4]) if len(r) > 4 and r[4] else None)
    ext = None
    if a.template:
        if os.path.exists(a.tpl): ext = check_structure(a.file, a.tpl)
        else: W('Không tìm thấy Template %s: bỏ qua so cấu trúc' % a.tpl)
    try: doc = ezdxf.readfile(a.file)
    except Exception as ex:
        E('ezdxf không đọc được file: %s' % ex); doc = None
    if doc is None:
        for lv in ('LỖI', 'CẢNH BÁO'):
            for m in OUT[lv]: print('[%s] %s' % (lv, m))
        sys.exit(1)
    au = doc.audit()
    if au.errors: E('ezdxf audit: %d lỗi (%s)' % (len(au.errors), '; '.join(str(x.message) for x in au.errors[:3])))
    if au.fixes: W('ezdxf audit: %d chỗ tự sửa' % len(au.fixes))
    msp = doc.modelspace()
    items = [(c, e) for e in msp for c in [classify(e)] if c]
    geo = [(c, e) for c, e in items if c != 'text']
    # tách hình theo khoảng Y
    iv = sorted((((bbox([x])[1], bbox([x])[3]), x) for x in geo), key=lambda z: z[0])
    parts = []
    for (y0, y1), x in iv:
        if parts and y0 <= parts[-1][1] + 100: parts[-1][1] = max(parts[-1][1], y1); parts[-1][2].append(x)
        else: parts.append([y0, y1, [x]])
    parts.reverse()  # trên xuống dưới
    texts = [e for c, e in items if c == 'text']
    codes = [e for e in texts if re.fullmatch(r'\d{6}', e.dxf.text)]
    flags = [e for e in texts if e.dxf.color == 6]
    jl = [e for e in texts if e.dxf.text in ('J', 'LJ')]
    other = [e for e in texts if e not in codes and e not in flags and e not in jl]
    for e in other: W('TEXT lạ %r tại %s' % (decode_u(e.dxf.text)[:30], P(e.dxf.insert)))
    for e in texts:
        if e.dxf.style != 'Standard': E('TEXT %r dùng style %s, phải là Standard' % (e.dxf.text[:20], e.dxf.style))
    if not is_all and (codes or flags): E('File riêng không được có chữ mã / Flag (chỉ file ALL)')
    allbb, names, prev = [], [], None
    for k, (y0, y1, its) in enumerate(parts):
        its = its + [(c, e) for c, e in items if c == 'text' and e.dxf.text in ('J', 'LJ') and y0 - 1 <= e.dxf.insert.y <= y1 + 1]
        cd = [e for e in codes if y0 - 1 <= e.dxf.insert.y <= y1 + 1]
        name = cd[0].dxf.text if cd else ('hình %d' % (k + 1) if is_all else os.path.basename(a.file))
        if is_all and len(cd) != 1: E('%s (Y %s..%s): có %d chữ mã, cần đúng 1' % (name, f(y0), f(y1), len(cd)))
        mat, t = a.mat, a.t
        if name in exp and exp[name][2]: mat, t = exp[name][2], exp[name][3]
        r = check_part(name, its, mat, t, is_all)
        if not r: continue
        bb, Wd, Hd = r; allbb.append(bb); names.append(name)
        if abs(bb[0]) > TOL: (W if abs(bb[0]) < 5 else E)('%s: mép trái ở X = %s, phải là 0 (nếu do góc bo/vát: góc ảo trước khi bo đang ở 0?)' % (name, f(bb[0])))
        if not is_all and abs(bb[1]) > TOL: E('%s: góc dưới trái ở %s, phải là (0; 0)' % (name, P(bb[:2])))
        if is_all and cd:
            e = cd[0]; ym = bb[1] + Hd / 2
            if abs(e.dxf.insert.x + 150) > TOL: E('%s: chữ mã ở X = %s, phải là -150' % (name, f(e.dxf.insert.x)))
            if abs(e.dxf.insert.y - ym) > 0.05: W('%s: chữ mã ở Y = %s, phải = đáy + cao/2 = %s' % (name, f(e.dxf.insert.y), f(ym)))
            if abs(e.dxf.height - 12) > TOL: E('%s: chữ mã cao %s, phải là 12' % (name, f(e.dxf.height)))
            if e.dxf.color not in (256, 7): E('%s: chữ mã có màu %d' % (name, e.dxf.color))
            if e.dxf.halign or e.dxf.valign: E('%s: chữ mã không căn trái (halign/valign khác 0)' % name)
            # Flag
            fl = sorted([x for x in flags if abs(x.dxf.insert.x + 150) < 1 and x.dxf.insert.y < e.dxf.insert.y and x.dxf.insert.y > e.dxf.insert.y - 12 - 7 * 60], key=lambda x: -x.dxf.insert.y)
            fl = [x for x in fl if not any(c2 is not e and x.dxf.insert.y < c2.dxf.insert.y < e.dxf.insert.y for c2 in codes)]
            num, items_txt = 0, []
            for kk, x in enumerate(fl):
                if abs(x.dxf.insert.y - (e.dxf.insert.y - 12 - 7 * kk)) > 0.05: E('%s: dòng Flag %d ở Y = %s, phải = %s' % (name, kk + 1, f(x.dxf.insert.y), f(e.dxf.insert.y - 12 - 7 * kk)))
                if abs(x.dxf.height - 4) > TOL: E('%s: dòng Flag cao %s, phải là 4' % (name, f(x.dxf.height)))
                s = decode_u(x.dxf.text)
                if len(s) > 30: W('%s: dòng Flag dài %d ký tự (> 30): %r' % (name, len(s), s))
                if -150 + len(s) * 4 * 0.6 > -2: W('%s: dòng Flag có thể đè lên hình' % name)
                m = re.match(r'(\d+)\. ', s)
                if m:
                    num += 1
                    if int(m.group(1)) != num: E('%s: Flag đánh số %s, phải là %d' % (name, m.group(1), num))
                    items_txt.append(s[m.end():])
                elif not items_txt: E('%s: dòng Flag đầu không bắt đầu bằng "1. "' % name)
                else: items_txt[-1] += ' ' + s
                if s.lower().startswith('flag'): E('%s: không ghi chữ "Flag"' % name)
            for s in items_txt:
                if not any(s.startswith(x) for x in STD_FLAGS): W('%s: Flag %r không khớp câu chuẩn nào trong 12 trường hợp' % (name, s[:40]))
            if fl and k + 1 < len(parts) and fl[-1].dxf.insert.y - 4 < parts[k + 1][1] + 5: W('%s: Flag kéo xuống chạm hình bên dưới' % name)
            if fl: I('%s: %d Flag: %s' % (name, num, ' | '.join(items_txt)))
        if name in exp:
            X, Y = exp[name][:2]
            if not ((abs(Wd - X) < 0.05 and abs(Hd - Y) < 0.05) or (abs(Wd - Y) < 0.05 and abs(Hd - X) < 0.05)):
                W('%s: phôi %s x %s khác CAD依頼書 %s x %s (依頼 chỉ tham khảo: kiểm lại công thức giãn/chuỗi kích thước, Flag nếu đúng là lệch)' % (name, f(Wd), f(Hd), f(X), f(Y)))
            else: I('%s: khớp CAD依頼書 %s x %s' % (name, f(X), f(Y)))
        if prev is not None and is_all:
            gap = prev[1] - bb[3]
            if abs(gap - 200) > 0.01: W('%s: cách hình trên %s, chuẩn 200' % (name, f(gap)))
        prev = bb
        parts[k].append(name); parts[k].append(its); parts[k].extend([Wd, Hd])
    if is_all and allbb and abs(allbb[-1][1]) > TOL: E('Hình cuối không sát Y = 0 (đáy ở %s)' % f(allbb[-1][1]))
    if exp and is_all:
        miss = set(exp) - set(names)
        if miss: E('Thiếu mã so với danh sách 依頼: %s' % ', '.join(sorted(miss)))
    if a.order:
        want = [x.strip() for x in a.order.split(',')]
        if [n for n in names if n in want] != [n for n in want if n in names]: E('Thứ tự hình (trên xuống) %s khác thứ tự trang PDF %s' % (names, want))
    if ext and allbb:
        allx = [b[2] for b in allbb]; ally = [b[3] for b in allbb]
        if ext[0] < max(allx) - 0.01 or ext[1] < max(ally) - 0.01: W('$EXTMAX (%s; %s) nhỏ hơn khung bao hình (%s; %s)' % (f(ext[0]), f(ext[1]), f(max(allx)), f(max(ally))))
    byname = {p[3]: p for p in parts if len(p) > 4}
    def nsig(p, tf=lambda q: q):
        bb = bbox(p[4]); return sig(p[4], bb[0], bb[1], tf)
    for m in a.mirror:
        A, B = m.split(':')
        if A not in byname or B not in byname: E('Cặp gương %s: không thấy mã trong file' % m); continue
        pa, pb = byname[A], byname[B]; ba = bbox(pa[4]); w, h = ba[2] - ba[0], ba[3] - ba[1]
        sb = nsig(pb)
        tfs = {'giống hệt': lambda q: q, 'gương trái–phải': lambda q: (w - q[0], q[1]), 'gương trên–dưới': lambda q: (q[0], h - q[1]), 'xoay 180°': lambda q: (w - q[0], h - q[1])}
        hit = [k for k, tf in tfs.items() if sorted(nsig(pa, tf)) == sb]
        sym = sorted(nsig(pa, tfs['gương trái–phải'])) == nsig(pa) or sorted(nsig(pa, tfs['gương trên–dưới'])) == nsig(pa)
        if not hit: W('Cặp %s: %s không phải ảnh gương/xoay của %s, kiểm tay từng chi tiết (lỗ, kegaki, cánh)' % (m, B, A))
        elif any('gương' in x for x in hit): I('Cặp %s: %s là %s của %s' % (m, B, ' / '.join(hit), A))
        elif sym: I('Cặp %s: hình tự đối xứng nên bản 対称 giống bản 本図 (hợp lệ)' % m)
        else: E('Cặp %s: %s %s %s, KHÔNG phải ảnh gương (lỗi đã gặp 064157/158)' % (m, B, ' / '.join(hit), A))
    check_source(a.src or os.path.dirname(os.path.abspath(a.file)), parts, lambda n: (exp[n][2], exp[n][3]) if n in exp and exp[n][2] else (a.mat, a.t))
    if a.single and is_all:
        for n, p in byname.items():
            fp = os.path.join(a.single, '26-%s.dxf' % n)
            if not os.path.exists(fp): W('Không thấy file riêng %s' % fp); continue
            d2 = ezdxf.readfile(fp); its = [(c, e) for e in d2.modelspace() for c in [classify(e)] if c]
            b2 = bbox(its)
            if sig(its, b2[0], b2[1]) != nsig(p): E('%s: hình trong ALL khác file riêng 26-%s.dxf (ALL chỉ được tịnh tiến)' % (n, n))
            else: I('%s: khớp file riêng' % n)
    if a.png:
        try:
            import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
            from ezdxf.addons.drawing import RenderContext, Frontend
            from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
            fig = plt.figure(figsize=(10, max(6, len(parts) * 3))); ax = fig.add_axes([0, 0, 1, 1])
            Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(msp); fig.savefig(a.png, dpi=110, facecolor='black')
            I('Ảnh xem trước: %s' % a.png)
        except ImportError: W('Thiếu matplotlib (pip install matplotlib) để xuất --png')
    print('=== dxf_check: %s (%s, %d hình) ===' % (os.path.basename(a.file), 'file ALL' if is_all else 'file riêng', len(names)))
    for lv in ('LỖI', 'CẢNH BÁO', 'THÔNG TIN'):
        print('\n[%s] %d' % (lv, len(OUT[lv])))
        for m in OUT[lv]: print(' - ' + m + (' (x%d)' % CNT[m] if CNT[m] > 1 else ''))
    sys.exit(1 if OUT['LỖI'] else 0)

if __name__ == '__main__': main()
