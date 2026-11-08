"""geom.py - hàm hình học dựng spec phôi (dùng chung cho subagent dxf-sheetmetal).
Spec entity (toạ độ mm, y hướng lên, góc độ ngược chiều kim đồng hồ):
  L(p,q, dashed=False, color=None)   A(c,r,a0,a1, color=None)   C(c,d)   P(p,color=None)   T(p,text,h=10)
color: None=trắng, 1=đỏ kegaki, 3=xanh lá (rạch/POINT xuyên). dashed=True: đường uốn.
Quy trình gợi ý: dựng biên bằng poly() (có bo R / vát C) -> thêm lỗ, uốn, kegaki -> place() (xoay bội 90°, lật nếu quy tắc mặt yêu cầu, đưa bbox về (0,0)) -> save_spec().
"""
import math, json
def L(p, q, dashed=False, color=None):
    e = {'t': 'LINE', 'p1': [float(p[0]), float(p[1])], 'p2': [float(q[0]), float(q[1])]}
    if dashed: e['dashed'] = True
    if color: e['color'] = color
    return e
def A(c, r, a0, a1, color=None):
    e = {'t': 'ARC', 'c': [float(c[0]), float(c[1])], 'r': float(r), 'a0': float(a0) % 360, 'a1': float(a1) % 360}
    if color: e['color'] = color
    return e
def C(c, d): return {'t': 'CIRCLE', 'c': [float(c[0]), float(c[1])], 'r': float(d) / 2}
def P(p, color=None):
    e = {'t': 'POINT', 'p': [float(p[0]), float(p[1])]}
    if color: e['color'] = color
    return e
def T(p, text, h=10): return {'t': 'TEXT', 'p': [float(p[0]), float(p[1])], 'text': text, 'h': h}

# ---------- vector ----------
def sub(a, b): return (a[0]-b[0], a[1]-b[1])
def add(a, b): return (a[0]+b[0], a[1]+b[1])
def mul(a, s): return (a[0]*s, a[1]*s)
def norm(a): l = math.hypot(*a); return (a[0]/l, a[1]/l)
def ang(v): return math.degrees(math.atan2(v[1], v[0])) % 360
def polar(c, r, deg): return (c[0]+r*math.cos(math.radians(deg)), c[1]+r*math.sin(math.radians(deg)))
def cross(a, b): return a[0]*b[1]-a[1]*b[0]

# ---------- giao / tiếp tuyến ----------
def line_line(p1, d1, p2, d2):
    """Giao 2 đường (điểm + vector hướng)."""
    den = cross(d1, d2)
    if abs(den) < 1e-12: raise ValueError('song song')
    t = cross(sub(p2, p1), d2) / den
    return add(p1, mul(d1, t))
def line_circle(p, d, c, r):
    """Giao đường (p, hướng d) với đường tròn (c, r): trả list điểm theo thứ tự t tăng."""
    d = norm(d); f = sub(p, c)
    b = 2*(f[0]*d[0]+f[1]*d[1]); cc = f[0]**2+f[1]**2-r*r
    disc = b*b-4*cc
    if disc < -1e-9: return []
    disc = max(disc, 0); s = math.sqrt(disc)
    return [add(p, mul(d, (-b-s)/2)), add(p, mul(d, (-b+s)/2))]
def circle_circle(c1, r1, c2, r2):
    dx, dy = sub(c2, c1); dd = math.hypot(dx, dy)
    a = (r1*r1-r2*r2+dd*dd)/(2*dd); h = math.sqrt(max(r1*r1-a*a, 0))
    m = add(c1, mul((dx, dy), a/dd))
    return [(m[0]+h*dy/dd, m[1]-h*dx/dd), (m[0]-h*dy/dd, m[1]+h*dx/dd)]
def tangent_points(pt, c, r):
    """Tiếp điểm của 2 tiếp tuyến từ điểm pt tới đường tròn (c, r)."""
    d = math.dist(pt, c)
    if d <= r: raise ValueError('điểm nằm trong đường tròn')
    a = math.degrees(math.acos(r/d)); base = ang(sub(pt, c))
    return [polar(c, r, base+a), polar(c, r, base-a)]

# ---------- biên đa giác có bo / vát ----------
def poly(pts, corner=None, close=True, color=None):
    """Biên đa giác qua các đỉnh pts. corner: dict {chỉ số đỉnh: R} (R>0 bo cung tiếp tuyến; ('C', c) vát C c).
    Góc lõm vẫn bo nếu được chỉ định R. Trả list entity LINE/ARC."""
    corner = corner or {}; n = len(pts)
    cut = {}  # i -> (điểm vào, điểm ra, entity góc hoặc None)
    for i, spec in corner.items():
        p = pts[i]; a = pts[i-1]; b = pts[(i+1) % n]
        u1 = norm(sub(a, p)); u2 = norm(sub(b, p))
        if isinstance(spec, tuple) and spec[0] == 'C':
            q1 = add(p, mul(u1, spec[1])); q2 = add(p, mul(u2, spec[1]))
            cut[i] = (q1, q2, L(q1, q2, color=color)); continue
        R = float(spec)
        th = math.acos(max(-1, min(1, u1[0]*u2[0]+u1[1]*u2[1])))
        t = R/math.tan(th/2)
        q1 = add(p, mul(u1, t)); q2 = add(p, mul(u2, t))
        bis = norm(add(u1, u2)); cc = add(p, mul(bis, R/math.sin(th/2)))
        a1, a2 = ang(sub(q1, cc)), ang(sub(q2, cc))
        # cung đi ngắn nhất từ q1 tới q2
        if (a2-a1) % 360 > 180: a1, a2 = a2, a1
        cut[i] = (q1, q2, A(cc, R, a1, a2, color=color))
    ents = []
    m = n if close else n-1
    for i in range(m):
        j = (i+1) % n
        s = cut[i][1] if i in cut else pts[i]
        e = cut[j][0] if j in cut else pts[j]
        if math.dist(s, e) > 1e-9: ents.append(L(s, e, color=color))
    for i in cut: ents.append(cut[i][2])
    return ents
def fillet_line_arc(p_far, p_corner, c, r, R, side=1):
    """Bo R giữa đoạn thẳng (p_far -> p_corner) và cung tròn (c, r) gặp tại p_corner.
    Trả (điểm tiếp trên đoạn, điểm tiếp trên cung, ARC). side=±1 chọn phía tâm bo (thử cả hai, kiểm bằng render)."""
    d = norm(sub(p_corner, p_far)); nrm = (-d[1]*side, d[0]*side)
    # tâm bo cách đường R, cách tâm cung r±R
    best = None
    for rr in (r+R, r-R):
        if rr <= 0: continue
        off = add(p_far, mul(nrm, R))
        for q in line_circle(off, d, c, rr):
            dist = math.dist(q, p_corner)
            if best is None or dist < best[0]: best = (dist, q, rr)
    _, cc, rr = best
    t_line = sub(cc, mul(nrm, R))
    v = norm(sub(cc, c)); t_arc = add(c, mul(v, r)) if rr > r else add(c, mul(v, r))
    a1, a2 = ang(sub(t_line, cc)), ang(sub(t_arc, cc))
    if (a2-a1) % 360 > 180: a1, a2 = a2, a1
    return t_line, t_arc, A(cc, R, a1, a2)

# ---------- uốn ----------
def bend_pair(axis, pos_outer, giãn, lo, hi, toward=-1):
    """2 LINE DASHED của một chỗ uốn. axis='x': đường song song trục y tại x=pos_outer và x=pos_outer+toward*giãn,
    chạy y từ lo tới hi; axis='y' ngược lại."""
    p2 = pos_outer + toward*giãn
    if axis == 'x': return [L((pos_outer, lo), (pos_outer, hi), dashed=True), L((p2, lo), (p2, hi), dashed=True)]
    return [L((lo, pos_outer), (hi, pos_outer), dashed=True), L((lo, p2), (hi, p2), dashed=True)]

# ---------- biến hình ----------
def _tp(p, k, mx):
    x, y = p
    if mx: x = -x
    for _ in range(k % 4): x, y = -y, x   # xoay 90° ngược chiều kim đồng hồ
    return (x, y)
def _ta(a, k, mx):
    if mx: a = 180 - a
    return (a + 90*k) % 360
def transform(ents, k=0, mirror=False, dx=0.0, dy=0.0):
    """mirror (lật trái-phải, CHỈ khi quy tắc mặt yêu cầu) rồi xoay k*90° CCW, rồi tịnh tiến."""
    out = []
    for e in ents:
        e = dict(e); t = e['t']
        if t == 'LINE':
            p, q = _tp(e['p1'], k, mirror), _tp(e['p2'], k, mirror)
            e['p1'], e['p2'] = [p[0]+dx, p[1]+dy], [q[0]+dx, q[1]+dy]
        elif t == 'ARC':
            c = _tp(e['c'], k, mirror); e['c'] = [c[0]+dx, c[1]+dy]
            a0, a1 = _ta(e['a0'], k, mirror), _ta(e['a1'], k, mirror)
            e['a0'], e['a1'] = (a1, a0) if mirror else (a0, a1)
        elif t in ('CIRCLE',):
            c = _tp(e['c'], k, mirror); e['c'] = [c[0]+dx, c[1]+dy]
        elif t in ('POINT', 'TEXT'):
            c = _tp(e['p'], k, mirror); e['p'] = [c[0]+dx, c[1]+dy]
        out.append(e)
    return out
def _arc_pts(e):
    c, r, a0, a1 = e['c'], e['r'], e['a0'], e['a1']
    sw = (a1 - a0) % 360 or 360
    pts = [polar(c, r, a0), polar(c, r, a1)]
    for q in (0, 90, 180, 270):
        if (q - a0) % 360 <= sw: pts.append(polar(c, r, q))
    return pts
def bbox(ents, outline_only=True):
    xs, ys = [], []
    for e in ents:
        if outline_only and (e.get('dashed') or e['t'] in ('TEXT',)): continue
        if e['t'] == 'LINE': pts = [e['p1'], e['p2']]
        elif e['t'] == 'ARC': pts = _arc_pts(e)
        elif e['t'] == 'CIRCLE': c, r = e['c'], e['r']; pts = [(c[0]-r, c[1]-r), (c[0]+r, c[1]+r)]
        else: pts = [e['p']]
        for p in pts: xs.append(p[0]); ys.append(p[1])
    return min(xs), min(ys), max(xs), max(ys)
def place(ents, k=0, mirror=False):
    """Xoay/lật rồi đưa góc dưới trái bbox về (0,0). Trả (ents, w, h)."""
    e2 = transform(ents, k, mirror)
    x0, y0, x1, y1 = bbox(e2)
    return transform(e2, 0, False, -x0, -y0), x1-x0, y1-y0
def save_spec(path, code, ents, w, h, flags=None, **extra):
    d = {'code': code, 'w': round(w, 6), 'h': round(h, 6), 'entities': ents, 'flags': flags or []}
    d.update(extra)
    json.dump(d, open(path, 'w'), ensure_ascii=False, indent=1)
    return d
