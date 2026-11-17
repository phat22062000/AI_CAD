# -*- coding: utf-8 -*-
"""doi_chieu_khach.py - đối chiếu hình AI đã vẽ (file <đơn>_ALL.dxf hoặc file riêng) với DXF khách trong thư mục đơn.
Không cần AI: chạy local, 0 token. Chỉ BÁO chỗ khác, không sửa file.

Dùng:  py -X utf8 doi_chieu_khach.py <ALL.dxf | 26-xxxxxx.dxf> [--src THU_MUC_DON] [--code 068884,068885] [--json]
Mã thoát: 0 = không có cảnh báo, 1 = có cảnh báo, 2 = lỗi đọc file.

Cách làm: mở DXF khách (cả BLOCK/INSERT, POLYLINE), tìm phép đặt (8 hướng + tịnh tiến, tỉ lệ 1:1) cho hình AI chồng
khít nhất lên một hình chiếu của khách, rồi so:
  - lỗ: cùng tâm mà khác φ; AI lấy vòng ngoài của nhóm vòng đồng tâm (khoét đầu vít chìm/ザグリ, ký hiệu ren);
    lỗ mồi không đúng cỡ ren của ký hiệu ren DXF khách; lỗ lệch vị trí; lỗ khách có mà hình AI không có;
  - biên dạng: cạnh/cung của hình AI không nằm trên nét nào của DXF khách (kèm độ lệch);
  - hốc/rãnh/bậc không xuyên: hình chiếu cạnh của DXF khách (chữ nhật mỏng bằng chiều dày, cùng bề rộng hình phẳng) có nét ngang nằm giữa
    chiều dày mà hình AI vẽ cạnh/cung đúng đoạn đó -> CẢNH BÁO (phần không xuyên hết chiều dày không vẽ làm biên cắt); bỏ qua khoét đầu vít/ザグリ.
Chỗ khác mà mã đó không có Flag 1 ("Kích thước PDF và DXF khác nhau") thì báo CẢNH BÁO (thiếu Flag 1 hoặc vẽ sai).
Giới hạn: chi tiết uốn chỉ đối chiếu được cụm lỗ (hình trải không trùng hình chiếu); DXF khách vẽ khác tỉ lệ 1:1 thì bỏ qua;
không biết nét bị gạch tay trên PDF, không biết mặt ngoài/kegaki. Kết quả là gợi ý để xem lại, không phải kết luận.
"""
import argparse
import json
import math
import os
import re
import sys
import unicodedata
from collections import defaultdict

import ezdxf

TOL = 0.05            # sai số coi là trùng
CELL = 10.0
ORI = [
    ('giữ nguyên hướng', lambda x, y: (x, y)),
    ('xoay 180°', lambda x, y: (-x, -y)),
    ('xoay 90° ngược chiều kim đồng hồ', lambda x, y: (-y, x)),
    ('xoay 90° cùng chiều kim đồng hồ', lambda x, y: (y, -x)),
    ('lật trái-phải', lambda x, y: (-x, y)),
    ('lật trên-dưới', lambda x, y: (x, -y)),
    ('xoay 90° rồi lật', lambda x, y: (y, x)),
    ('xoay 270° rồi lật', lambda x, y: (-y, -x)),
]
# lỗ mồi taro theo cỡ ren (Quy_Tac_Lo_Moi.md); chỉ dùng để nhận ra ký hiệu ren, không thay bảng gốc
PILOT_D = {2: 1.6, 2.5: 2.1, 2.6: 2.2, 3: 2.5, 3.5: 2.9, 4: 3.3, 5: 4.2, 6: 5.0, 7: 6.0, 8: 6.8, 10: 8.5, 12: 10.3, 14: 12.0, 16: 14.0}
FLAG1 = 'Kích thước PDF và DXF khác nhau'
FLAG18 = 'Kích thước có dung sai'


def f(v):
    return ('%.3f' % v).rstrip('0').rstrip('.')


def decode_u(s):
    return unicodedata.normalize('NFC', re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s))


# ---------------------------------------------------------------- hình AI
def col_of(e):
    c = e.dxf.color if e.dxf.hasattr('color') else 256
    return 7 if c in (0, 7, 256) else c


def arc_pt(c, r, a):
    return (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))


def load_ai(path):
    """Trả về [(mã, [entity], [câu Flag])]. entity: ('L', p1, p2) | ('A', tâm, R, a0, quét) | ('C', tâm, R); chỉ nét cắt trắng."""
    doc = ezdxf.readfile(path)
    ents, codes, flags = [], [], []
    for e in doc.modelspace():
        t = e.dxftype()
        if t == 'TEXT':
            tx = e.dxf.text.strip()
            if re.fullmatch(r'\d{6}', tx):
                codes.append((e.dxf.insert.y, tx))
            elif col_of(e) == 6:
                flags.append((e.dxf.insert.y, decode_u(tx)))
            continue
        lt = (e.dxf.linetype if e.dxf.hasattr('linetype') else '').upper()
        if col_of(e) != 7 or lt == 'DASHED':
            if lt == 'DASHED' and t == 'LINE':
                ents.append(('B', (e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))   # đường uốn: chỉ để biết chi tiết có uốn
            continue                      # đường uốn, kegaki, rạch Green: không có trong DXF khách theo cùng nghĩa
        if t == 'LINE':
            ents.append(('L', (e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
        elif t == 'CIRCLE':
            ents.append(('C', (e.dxf.center.x, e.dxf.center.y), e.dxf.radius))
        elif t == 'ARC':
            ents.append(('A', (e.dxf.center.x, e.dxf.center.y), e.dxf.radius, e.dxf.start_angle, (e.dxf.end_angle - e.dxf.start_angle) % 360))
    if not codes:
        m = re.search(r'(\d{6})', os.path.basename(path))
        return [(m.group(1) if m else os.path.basename(path), ents, None)]      # file riêng: không có Flag để xét

    def yr(e):
        if e[0] in ('L', 'B'):
            return min(e[1][1], e[2][1]), max(e[1][1], e[2][1])
        if e[0] == 'A':
            ys = [arc_pt(e[1], e[2], e[3] + e[4] * k / 8)[1] for k in range(9)]
            return min(ys), max(ys)
        return e[1][1] - e[2], e[1][1] + e[2]
    bands = []
    for y0, y1, e in sorted(((yr(e)[0], yr(e)[1], e) for e in ents), key=lambda z: z[0]):
        if bands and y0 <= bands[-1][1] + 100:
            bands[-1][1] = max(bands[-1][1], y1)
            bands[-1][2].append(e)
        else:
            bands.append([y0, y1, [e]])
    codes.sort(reverse=True)
    out = []
    for y0, y1, es in reversed(bands):
        cd = [c for y, c in codes if y0 - 1 <= y <= y1 + 1]
        if not cd:
            continue
        cy = next(y for y, c in codes if c == cd[0])
        nxt = max([y for y, c in codes if y < cy] or [-1e18])
        fl = ' '.join(t for y, t in sorted(flags, reverse=True) if nxt < y < cy)
        out.append((cd[0], es, [x.strip() for x in re.split(r'(?:^|\s)\d+\.\s', fl) if x.strip()]))
    return out


def tf_ent(e, fn, mirror):
    if e[0] == 'L':
        return ('L', fn(*e[1]), fn(*e[2]))
    if e[0] == 'C':
        return ('C', fn(*e[1]), e[2])
    c = fn(*e[1])
    p0, p1 = fn(*arc_pt(e[1], e[2], e[3])), fn(*arc_pt(e[1], e[2], e[3] + e[4]))
    if mirror:
        p0, p1 = p1, p0
    a0 = math.degrees(math.atan2(p0[1] - c[1], p0[0] - c[0]))
    return ('A', c, e[2], a0, e[4])


# ---------------------------------------------------------------- DXF khách
class Khach:
    def __init__(self, path):
        self.path = path
        self.lines, self.circ, self.arcs = [], [], []
        self._walk(ezdxf.readfile(path).modelspace(), 0)
        self.grid = defaultdict(list)
        for i, (x1, y1, x2, y2) in enumerate(self.lines):
            n = max(1, int(math.hypot(x2 - x1, y2 - y1) / (CELL / 2)))
            seen = set()
            for k in range(n + 1):
                key = (int(math.floor((x1 + (x2 - x1) * k / n) / CELL)), int(math.floor((y1 + (y2 - y1) * k / n) / CELL)))
                if key not in seen:
                    seen.add(key)
                    self.grid[key].append(('L', i))
        for kind, lst in (('C', self.circ), ('A', self.arcs)):
            for i, it in enumerate(lst):
                cx, cy, r = it[0], it[1], it[2]
                n = max(8, int(2 * math.pi * r / (CELL / 2)))
                seen = set()
                for k in range(n):
                    a = 2 * math.pi * k / n
                    key = (int(math.floor((cx + r * math.cos(a)) / CELL)), int(math.floor((cy + r * math.sin(a)) / CELL)))
                    if key not in seen:
                        seen.add(key)
                        self.grid[key].append((kind, i))
        self.cgrid = defaultdict(list)       # tâm vòng tròn và cung nhỏ (ký hiệu ren)
        for cx, cy, r in self.circ:
            self.cgrid[(int(math.floor(cx)), int(math.floor(cy)))].append((cx, cy, r, 'C'))
        for cx, cy, r, a0, sw in self.arcs:
            if r <= 30 and sw >= 180:
                self.cgrid[(int(math.floor(cx)), int(math.floor(cy)))].append((cx, cy, r, 'A'))

    def _walk(self, ents, depth):
        for e in ents:
            t = e.dxftype()
            try:
                if t == 'INSERT' and depth < 5:
                    self._walk(e.virtual_entities(), depth + 1)
                elif t in ('LWPOLYLINE', 'POLYLINE'):
                    self._walk(e.virtual_entities(), depth + 1)
                elif t == 'LINE':
                    self.lines.append((e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y))
                elif t == 'CIRCLE':
                    flip = e.dxf.extrusion.z < 0          # BLOCK chèn lật (extrusion -Z): toạ độ đang ở OCS, đổi về WCS
                    self.circ.append((-e.dxf.center.x if flip else e.dxf.center.x, e.dxf.center.y, e.dxf.radius))
                elif t == 'ARC':
                    sw = (e.dxf.end_angle - e.dxf.start_angle) % 360
                    if e.dxf.extrusion.z < 0:
                        self.arcs.append((-e.dxf.center.x, e.dxf.center.y, e.dxf.radius, (180 - e.dxf.end_angle) % 360, sw))
                    else:
                        self.arcs.append((e.dxf.center.x, e.dxf.center.y, e.dxf.radius, e.dxf.start_angle, sw))
            except Exception:
                continue

    def dist(self, p, lim=CELL):
        """khoảng cách từ điểm tới nét gần nhất (chỉ tìm trong lim)"""
        gx, gy = int(math.floor(p[0] / CELL)), int(math.floor(p[1] / CELL))
        best = lim
        seen = set()
        for ix in (gx - 1, gx, gx + 1):
            for iy in (gy - 1, gy, gy + 1):
                for it in self.grid.get((ix, iy), ()):
                    if it in seen:
                        continue
                    seen.add(it)
                    if it[0] == 'L':
                        x1, y1, x2, y2 = self.lines[it[1]]
                        dx, dy = x2 - x1, y2 - y1
                        L2 = dx * dx + dy * dy
                        t = 0 if L2 == 0 else max(0, min(1, ((p[0] - x1) * dx + (p[1] - y1) * dy) / L2))
                        d = math.hypot(p[0] - x1 - t * dx, p[1] - y1 - t * dy)
                    elif it[0] == 'C':
                        cx, cy, r = self.circ[it[1]]
                        d = abs(math.hypot(p[0] - cx, p[1] - cy) - r)
                    else:
                        cx, cy, r, a0, sw = self.arcs[it[1]]
                        ang = (math.degrees(math.atan2(p[1] - cy, p[0] - cx)) - a0) % 360
                        if ang <= sw + 0.5 or ang >= 359.5:
                            d = abs(math.hypot(p[0] - cx, p[1] - cy) - r)
                        else:
                            d = min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in (arc_pt((cx, cy), r, a0), arc_pt((cx, cy), r, a0 + sw)))
                    if d < best:
                        best = d
        return best

    def profiles(self):
        """Hình chiếu cạnh (mặt cắt dẹt dày t) của DXF khách: chữ nhật mỏng có nét ngang nằm giữa chiều dày = bậc/hốc KHÔNG xuyên.
        Trả về [{'ax': 0|1, 'a','b' (khoảng dọc theo trục dài), 'lo','hi' (hai mặt, t = hi-lo), 'steps': [(xa, xb, depth|None, 'trên'|'dưới'|'')]}].
        ax=0: mỏng theo y (hình chiếu cạnh đặt dưới/trên hình phẳng); ax=1: mỏng theo x (đặt bên cạnh)."""
        if hasattr(self, '_prof'):
            return self._prof
        out = []
        for ax in (0, 1):
            L = [(l[0], l[1], l[2], l[3]) if ax == 0 else (l[1], l[0], l[3], l[2]) for l in self.lines]
            hor = defaultdict(list)       # y -> [(xa, xb)]
            ver = defaultdict(list)       # x -> [(ya, yb)]
            for x1, y1, x2, y2 in L:
                if abs(y1 - y2) <= 0.005 and abs(x1 - x2) >= 0.5:
                    hor[round(y1, 2)].append((min(x1, x2), max(x1, x2)))
                elif abs(x1 - x2) <= 0.005 and abs(y1 - y2) >= 0.1:
                    ver[round(x1, 2)].append((min(y1, y2), max(y1, y2)))

            def cover(lst, a, b):
                """phần trăm đoạn [a, b] được phủ bởi các đoạn trong lst"""
                tot = 0.0
                for u, v in sorted(lst):
                    u, v = max(u, a), min(v, b)
                    if v > u:
                        tot += v - u
                return tot / (b - a) if b > a else 0.0
            ys = sorted(hor)
            for i, lo in enumerate(ys):
                for hi in ys[i + 1:]:
                    t = hi - lo
                    if t > 30:
                        break
                    if t < 0.3:
                        continue
                    for (a, b) in [r for r in hor[lo] if r[1] - r[0] >= max(20.0, 4 * t)]:
                        if not any(abs(a - u) <= 0.05 and abs(b - v) <= 0.05 for u, v in hor[hi]):
                            continue
                        xa = [x for x in ver if abs(x - a) <= 0.05]
                        xb = [x for x in ver if abs(x - b) <= 0.05]
                        if not (xa and xb) or max(cover(ver[x], lo, hi) for x in xa) < 0.9 or max(cover(ver[x], lo, hi) for x in xb) < 0.9:
                            continue
                        steps = []
                        for y, segs in hor.items():
                            if y <= lo + 0.15 or y >= hi - 0.15:
                                continue
                            for u, v in sorted(segs):
                                u, v = max(u, a), min(v, b)
                                if v - u < 1.0:
                                    continue
                                if steps and steps[-1][2] == y and u <= steps[-1][1] + 0.05:
                                    steps[-1][1] = max(steps[-1][1], v)
                                else:
                                    steps.append([u, v, y])
                        res = []
                        for u, v, y in steps:
                            up = max([cover(ver[x], y, hi) for x in ver if abs(x - u) <= 0.05 or abs(x - v) <= 0.05] or [0])
                            dn = max([cover(ver[x], lo, y) for x in ver if abs(x - u) <= 0.05 or abs(x - v) <= 0.05] or [0])
                            if up >= 0.9:
                                res.append((u, v, round(hi - y, 3), 'trên'))
                            elif dn >= 0.9:
                                res.append((u, v, round(y - lo, 3), 'dưới'))
                            else:
                                res.append((u, v, None, ''))
                        if res:
                            out.append({'ax': ax, 'a': a, 'b': b, 'lo': lo, 'hi': hi, 'steps': res})
        self._prof = out
        return out

    def centers(self, p, tol=TOL):
        gx, gy = int(math.floor(p[0])), int(math.floor(p[1]))
        out = []
        for ix in (gx - 1, gx, gx + 1):
            for iy in (gy - 1, gy, gy + 1):
                for c in self.cgrid.get((ix, iy), ()):
                    if abs(c[0] - p[0]) <= tol and abs(c[1] - p[1]) <= tol:
                        out.append(c)
        return out


# ---------------------------------------------------------------- tìm phép đặt
def samples(e, n):
    if e[0] == 'L':
        return [(e[1][0] + (e[2][0] - e[1][0]) * k / (n - 1), e[1][1] + (e[2][1] - e[1][1]) * k / (n - 1)) for k in range(n)]
    if e[0] == 'A':
        return [arc_pt(e[1], e[2], e[3] + e[4] * k / (n - 1)) for k in range(n)]
    return [e[1]]


def length(e):
    if e[0] == 'L':
        return math.hypot(e[2][0] - e[1][0], e[2][1] - e[1][1])
    if e[0] == 'A':
        return math.radians(e[4]) * e[2]
    return 0.0


def is_corner(e):
    return e[0] == 'A' and e[2] <= 3.01 and e[4] < 180      # bo R laser ở góc (kể cả góc không vuông)


def score(ents, K, d, quick=False):
    """(tỉ lệ chiều dài biên nằm trên nét khách, số lỗ trùng tâm)"""
    tot = hit = 0.0
    holes = 0
    cut = [e for e in ents if e[0] != 'C' and not is_corner(e)]
    if quick:
        cut = sorted(cut, key=length, reverse=True)[:12]
    for e in cut:
        L = length(e)
        ps = samples(e, 3)
        ok = sum(1 for p in ps if K.dist((p[0] + d[0], p[1] + d[1]), 1.0) <= TOL)
        tot += L
        hit += L * ok / len(ps)
    for e in ents:
        if e[0] == 'C' and K.centers((e[1][0] + d[0], e[1][1] + d[1])):
            holes += 1
    return (hit / tot if tot else 0.0), holes


def top(votes, n):
    return [k for k, v in sorted(votes.items(), key=lambda z: -z[1])[:n]]


def best_fit(part, K):
    nh = sum(1 for e in part if e[0] == 'C')
    best = None
    for oi, (oname, fn) in enumerate(ORI):
        ents = [tf_ent(e, fn, oi >= 4) for e in part]
        cand = {}
        jv, js = defaultdict(int), {}
        for e in ents:                                   # phiếu theo tâm lỗ
            if e[0] != 'C':
                continue
            for lst in (K.circ, [a for a in K.arcs if a[2] <= 30 and a[4] >= 180]):
                for c in lst:
                    dx, dy = c[0] - e[1][0], c[1] - e[1][1]
                    k = (round(dx, 1), round(dy, 1))
                    jv[k] += 1
                    js[k] = (dx, dy)
        for k in top(jv, 8):
            if jv[k] >= min(2, nh):
                cand[k] = js[k]
        vx, vy, sx, sy = defaultdict(float), defaultdict(float), {}, {}
        for e in ents:                                   # phiếu theo cạnh ngang/dọc
            if e[0] != 'L':
                continue
            L = length(e)
            if L < 5:
                continue
            hz, vt = abs(e[1][1] - e[2][1]) < 1e-4, abs(e[1][0] - e[2][0]) < 1e-4
            if not (hz or vt):
                continue
            for x1, y1, x2, y2 in K.lines:
                if hz and abs(y1 - y2) < 1e-4 and abs(x1 - x2) >= 5:
                    k = round(y1 - e[1][1], 1)
                    vy[k] += min(L, abs(x1 - x2))
                    sy[k] = y1 - e[1][1]
                elif vt and abs(x1 - x2) < 1e-4 and abs(y1 - y2) >= 5:
                    k = round(x1 - e[1][0], 1)
                    vx[k] += min(L, abs(y1 - y2))
                    sx[k] = x1 - e[1][0]
        for kx in top(vx, 6):
            for ky in top(vy, 6):
                cand[(kx, ky)] = (sx[kx], sy[ky])
        quick = sorted(((score(ents, K, d, True), d) for d in cand.values()), key=lambda z: -(z[0][0] * 0.6 + (z[0][1] / nh if nh else 0) * 0.4))[:3]
        for _, d in quick:
            so, hh = score(ents, K, d)
            val = so * 0.6 + (hh / nh if nh else so) * 0.4
            if best is None or val > best[0] + 1e-9:
                best = (val, so, hh, oname, d, ents)
    return best


# ---------------------------------------------------------------- so chi tiết
def compare(code, part, flags, K, fit, flat):
    val, so, hh, oname, d, ents = fit
    nh = sum(1 for e in part if e[0] == 'C')
    xs = [p[0] for e in part for p in (samples(e, 3) if e[0] != 'C' else [(e[1][0] - e[2], e[1][1] - e[2]), (e[1][0] + e[2], e[1][1] + e[2])])]
    ys = [p[1] for e in part for p in (samples(e, 3) if e[0] != 'C' else [(e[1][0] - e[2], e[1][1] - e[2]), (e[1][0] + e[2], e[1][1] + e[2])])]
    ox, oy = min(xs), min(ys)
    loc = lambda p: '(%s; %s)' % (f(p[0] - ox), f(p[1] - oy))           # toạ độ trong hình AI, gốc ở góc dưới trái khung bao
    noflag = flags is None
    has1 = any(FLAG1.lower() in x.lower() for x in flags or [])
    has18 = noflag or any(FLAG18.lower() in x.lower() for x in flags or [])
    res = {'ma': code, 'file_khach': os.path.basename(K.path), 'phep_dat': oname, 'khop_bien': round(so, 3), 'lo_trung_tam': '%d/%d' % (hh, nh),
           'kieu': 'hình phẳng' if flat else 'cụm lỗ', 'flag1': has1, 'khac_biet': []}

    def add(loai, muc, mo_ta, flag_khong_lien_quan=False):
        x = {'loai': loai, 'muc': muc, 'mo_ta': mo_ta}
        if flag_khong_lien_quan:
            x['khong_xet_flag'] = True                   # cảnh báo mà Flag 1 không phải cách xử lý (vd hốc không xuyên): không kéo theo "Thiếu Flag"
        res['khac_biet'].append(x)
    grp = defaultdict(list)
    used = set()
    for e0, e in zip(part, ents):
        if e[0] != 'C':
            continue
        p = (e[1][0] + d[0], e[1][1] + d[1])
        cs = K.centers(p)
        dia = round(2 * e[2], 2)
        if not cs:
            if flat:
                near = [c for c in K.circ if abs(c[2] - e[2]) <= 0.02 and math.hypot(c[0] - p[0], c[1] - p[1]) <= 5]
                if near:
                    c = min(near, key=lambda c: math.hypot(c[0] - p[0], c[1] - p[1]))
                    grp[('Sai vị trí lỗ', 'φ%s lệch so với DXF khách (dx %s, dy %s theo hướng DXF khách)' % (f(dia), f(p[0] - c[0]), f(p[1] - c[1])))].append(e0[1])
                else:
                    grp[('Thừa lỗ', 'φ%s không có vòng tròn nào cùng tâm trong DXF khách' % f(dia))].append(e0[1])
            continue
        for c in cs:
            used.add((round(c[0], 2), round(c[1], 2)))
        full = sorted({round(2 * c[2], 2) for c in cs if c[3] == 'C'})
        allr = sorted({round(2 * c[2], 2) for c in cs})
        if any(abs(dia - x) <= 0.02 for x in allr):
            inner = [x for x in full if x < dia - 0.3]
            if inner and abs(dia - max(allr)) <= 0.02:
                grp[('Sai kích thước lỗ', 'AI vẽ φ%s là vòng NGOÀI của nhóm vòng đồng tâm trong DXF khách (%s): nếu là khoét đầu vít chìm/ザグリ hoặc ký hiệu ren thì lỗ cắt là vòng trong φ%s' % (f(dia), ', '.join('φ' + f(x) for x in allr), f(max(inner))))].append(e0[1])
            continue
        nominal = max(allr)
        pil = PILOT_D.get(nominal if nominal != int(nominal) else int(nominal))
        if pil is not None and abs(dia - pil) <= 0.02:
            continue                                     # lỗ mồi đúng cỡ ren của ký hiệu ren
        mine = [m for m, v in PILOT_D.items() if abs(v - dia) <= 0.02]
        if pil is not None and len(allr) >= 2 and mine:
            grp[('Sai kích thước lỗ', 'AI vẽ φ%s (lỗ mồi M%s) nhưng ký hiệu ren DXF khách là M%s (vòng %s): lỗ mồi theo DXF là φ%s' % (f(dia), f(mine[0]), f(nominal), ', '.join('φ' + f(x) for x in allr), f(pil)))].append(e0[1])
        else:
            grp[('Sai kích thước lỗ', 'AI vẽ φ%s, DXF khách cùng tâm là %s' % (f(dia), ', '.join('φ' + f(x) for x in allr)))].append(e0[1])
    for (loai, txt), pts in grp.items():
        soft = has1 and 'vòng NGOÀI' not in txt
        add(loai, 'thongtin' if soft else 'canhbao', '%d lỗ tại %s: %s%s' % (len(pts), ', '.join(loc(p) for p in pts[:6]) + (' …' if len(pts) > 6 else ''), txt, ' (mã đã có Flag 1: đối chiếu nội dung Flag)' if soft else ''))
    if flat:
        bad = []
        for e0, e in zip(part, ents):
            if e[0] == 'C':
                continue
            ps = samples(e, 9)
            ds = [K.dist((p[0] + d[0], p[1] + d[1]), 8.0) for p in ps]
            if is_corner(e):
                if max(ds[0], ds[-1]) <= TOL or max(ds) <= TOL:
                    continue                             # bo R laser ở góc nhọn của khách
            if max(ds) > TOL:
                bad.append((e0, max(ds), sum(1 for x in ds if x > TOL) / len(ds)))
        if any(fr >= 0.5 for _, _, fr in bad):
            bad = [b for b in bad if b[2] >= 0.2]          # bỏ đoạn lệch ngắn là hệ quả của cạnh/cung bên cạnh
        for e0, dm, fr in sorted(bad, key=lambda z: -z[1])[:8]:
            if e0[0] == 'L':
                what = 'cạnh %s-%s' % (loc(e0[1]), loc(e0[2]))
            else:
                what = 'cung R%s tâm %s' % (f(e0[2]), loc(e0[1]))
            soft = has1 or (has18 and dm <= 0.6)
            why = ' (mã đã có Flag 1: đối chiếu nội dung Flag)' if has1 else (' (lệch ≤ 0.6: có thể do lấy giữa dung sai)' if noflag else ' (mã có Flag dung sai, lệch ≤ 0.6: có thể do lấy giữa dung sai)') if soft else ''
            add('Sai biên dạng ngoài', 'thongtin' if soft else 'canhbao', '%s không nằm trên nét của DXF khách, lệch %s%s (%d%% chiều dài)%s' % (what, '≥ ' if dm >= 8 else '', f(dm), round(fr * 100), why))
        if len(bad) > 8:
            add('Sai biên dạng ngoài', 'thongtin', 'còn %d cạnh/cung khác không nằm trên nét DXF khách' % (len(bad) - 8))
        # lỗ khách có mà hình AI không có (chỉ xét trong khung bao hình AI đã đặt lên DXF khách)
        ex = [(p[0] + d[0], p[1] + d[1]) for e in ents for p in (samples(e, 3) if e[0] != 'C' else [e[1]])]
        x0, x1, y0, y1 = min(p[0] for p in ex), max(p[0] for p in ex), min(p[1] for p in ex), max(p[1] for p in ex)
        inv = {v: k for k, v in enumerate(ORI)}
        miss = defaultdict(list)
        for cx, cy, r in K.circ:
            if x0 + r <= cx <= x1 - r and y0 + r <= cy <= y1 - r and (round(cx, 2), round(cy, 2)) not in used and r <= 100:
                if not any(abs(c[0] - cx) <= TOL and abs(c[1] - cy) <= TOL for c in [(e[1][0] + d[0], e[1][1] + d[1]) for e in ents if e[0] == 'C']):
                    miss[round(2 * r, 2)].append((cx, cy))
        for dia, pts in sorted(miss.items()):
            cen = {(round(p[0], 1), round(p[1], 1)) for p in pts}
            tron = abs(dia * 10 - round(dia * 10)) < 1e-6      # φ lẻ (4.13, 67.46...) thường là ký hiệu ren hoặc vòng chú thích
            add('Thiếu lỗ', 'thongtin' if has1 or not tron else 'canhbao', 'DXF khách có %d vòng φ%s trong vùng hình mà hình AI không có lỗ cùng tâm (lỗ bị gạch/hình chiếu khác đè lên thì bỏ qua)' % (len(cen), f(dia)))
        # hốc/rãnh/bậc không xuyên: hình chiếu cạnh của DXF khách có nét ngang giữa chiều dày mà hình AI vẽ cạnh/cung đúng đoạn đó
        for pr in K.profiles():
            ax = pr['ax']
            lo_ai, hi_ai = (x0, x1) if ax == 0 else (y0, y1)
            o0, o1 = (y0, y1) if ax == 0 else (x0, x1)
            if abs(pr['a'] - lo_ai) > 0.3 or abs(pr['b'] - hi_ai) > 0.3:
                continue
            if min(o1, pr['hi']) - max(o0, pr['lo']) > 0.5 * (pr['hi'] - pr['lo']):
                continue                                        # chữ nhật mỏng này chính là hình phẳng, không phải hình chiếu cạnh
            t = pr['hi'] - pr['lo']
            for u, v, dep, side in pr['steps']:
                if any(abs((u + v) / 2 - (c[ax])) <= 0.06 and abs((v - u) / 2 - c[2]) <= 0.06 for c in K.circ):
                    continue                                    # khoét đầu vít/ザグリ: đã kiểm ở vòng đồng tâm
                hit = []
                for e0, e in zip(part, ents):
                    if e[0] == 'C' or is_corner(e) or length(e) < 1.0:
                        continue
                    ps = [(p[0] + d[0], p[1] + d[1]) for p in samples(e, 9)]
                    if all(u - 0.1 <= p[ax] <= v + 0.1 for p in ps):
                        hit.append(e0)
                if hit:
                    where = ', '.join(('%s-%s' % (loc(h[1]), loc(h[2])) if h[0] == 'L' else 'cung R%s tâm %s' % (f(h[2]), loc(h[1]))) for h in hit[:3])
                    add('Sai biên dạng ngoài', 'canhbao', 'Hình chiếu cạnh DXF khách (dày %s) có hốc/bậc KHÔNG xuyên ở đoạn %s %s đến %s (rộng %s%s) nhưng hình AI vẽ %d cạnh/cung nằm trọn trong đoạn đó (%s): phần không xuyên hết chiều dày thì không vẽ làm biên cắt; kiểm PDF xem có phải nét gạch/hốc nửa chiều dày' % (f(t), 'x' if ax == 0 else 'y', f(u), f(v), f(v - u), ', sâu %s từ mặt %s' % (f(dep), side) if dep is not None else '', len(hit), where), True)
    if any(x['muc'] == 'canhbao' and not x.get('khong_xet_flag') for x in res['khac_biet']) and not has1 and not noflag:
        add('Thiếu Flag', 'canhbao', 'Hình khác DXF khách nhưng mã không có Flag 1 ("%s")' % FLAG1)
    return res


def src_dxf(src):
    out = []
    for fn in sorted(os.listdir(src)):
        u = fn.upper()
        if u.endswith('.DXF') and not u.endswith('_ALL.DXF') and not re.match(r'26-\d{6}[TF]?\.DXF', u) and os.path.isfile(os.path.join(src, fn)):
            out.append(os.path.join(src, fn))
    return out


def run(path, src, only=None):
    parts = [(c, [e for e in es if e[0] != 'B'], fl, any(e[0] == 'B' for e in es)) for c, es, fl in load_ai(path)]
    ks, errs = [], []
    for p in src_dxf(src):
        try:
            ks.append(Khach(p))
        except Exception as ex:
            errs.append('Không đọc được DXF khách %s: %s' % (os.path.basename(p), ex))
    out = {'file': os.path.basename(path), 'dxf_khach': [os.path.basename(k.path) for k in ks], 'loi_doc': errs, 'ket_qua': []}
    for code, part, flags, bent in parts:
        if only and code not in only:
            continue
        if not ks:
            out['ket_qua'].append({'ma': code, 'kieu': 'không có DXF khách', 'khac_biet': []})
            continue
        nh = sum(1 for e in part if e[0] == 'C')
        best = None
        for K in ks:
            fit = best_fit(part, K)
            if fit and (best is None or fit[0] > best[1][0]):
                best = (K, fit)
        if best is None:
            out['ket_qua'].append({'ma': code, 'kieu': 'không đối chiếu được', 'khac_biet': []})
            continue
        K, fit = best
        so, hh = fit[1], fit[2]
        flat = so >= (0.9 if bent else 0.6)             # chi tiết uốn: hình trải hiếm khi trùng hình chiếu, chỉ so cụm lỗ
        if flat or (hh >= 2 and hh >= 0.5 * nh):
            out['ket_qua'].append(compare(code, part, flags, K, fit, flat))
        else:
            out['ket_qua'].append({'ma': code, 'kieu': 'không đối chiếu được', 'khop_bien': round(so, 3), 'lo_trung_tam': '%d/%d' % (hh, nh),
                                   'ghi_chu': 'Không hình chiếu nào của DXF khách chồng khít hình AI (chi tiết uốn, DXF khác tỉ lệ, hoặc không có DXF của mã này)', 'khac_biet': []})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--src')
    ap.add_argument('--code')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    try:
        out = run(a.file, a.src or os.path.dirname(os.path.abspath(a.file)), set(a.code.split(',')) if a.code else None)
    except Exception as ex:
        print('LỖI: %s' % ex)
        sys.exit(2)
    warn = sum(1 for r in out['ket_qua'] for x in r['khac_biet'] if x['muc'] == 'canhbao')
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print('=== doi_chieu_khach: %s, %d DXF khách ===' % (out['file'], len(out['dxf_khach'])))
        for m in out['loi_doc']:
            print(' ! ' + m)
        for r in out['ket_qua']:
            head = '%s: %s' % (r['ma'], r['kieu'])
            if r.get('file_khach'):
                head += ' | %s | %s | biên khớp %d%%, lỗ trùng tâm %s' % (r['file_khach'], r['phep_dat'], round(r['khop_bien'] * 100), r['lo_trung_tam'])
            print(head)
            if r.get('ghi_chu'):
                print('   - ' + r['ghi_chu'])
            for x in r['khac_biet']:
                print('   [%s] %s: %s' % ('CẢNH BÁO' if x['muc'] == 'canhbao' else 'THÔNG TIN', x['loai'], x['mo_ta']))
    sys.exit(1 if warn else 0)


if __name__ == '__main__':
    main()
