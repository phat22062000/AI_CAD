# -*- coding: utf-8 -*-
"""diff_tf.py - so DXF đúng (T, do người dùng làm) với DXF AI vẽ (F), liệt kê khác biệt có phân loại.
Không cần AI: chạy local, 0 token. Dùng trong quy trình rút kinh nghiệm (docs/QUY_TRINH_RUT_KINH_NGHIEM.md).

Dùng:  py -X utf8 diff_tf.py <T.dxf> <F.dxf> [--tol 0.05] [--json]
Mã thoát: 0 = khớp (kể cả khi chỉ khác hướng đặt), 1 = có khác biệt, 2 = lỗi đọc file.

Cách so: dời khung bao về gốc, thử 8 phép đặt hướng của F (giữ, lật, xoay) lấy phép khớp nhất với T, rồi ghép từng
entity (LINE theo màu và nét đứt, CIRCLE, ARC, POINT) trong sai số --tol. Mọi toạ độ in ra ở hệ của T.
Loại lỗi (trường "loai") theo dxf-check mục 5: Sai kích thước lỗ, Sai vị trí lỗ, Thiếu lỗ, Thừa lỗ, Sai kích thước bo R,
Sai biên dạng ngoài, Sai kegaki, Sai độ giãn dài, Thiếu/Thừa rạch Green, Sai màu PIERCING, Hướng đặt khác, Sai mặt vẽ.
"""
import argparse
import json
import math
import sys

import ezdxf

TRANSFORMS = [
    ('giữ nguyên hướng', lambda x, y: (x, y)),
    ('lật trái-phải (ảnh gương qua trục dọc)', lambda x, y: (-x, y)),
    ('lật trên-dưới (ảnh gương qua trục ngang)', lambda x, y: (x, -y)),
    ('xoay 180°', lambda x, y: (-x, -y)),
    ('xoay 90° ngược chiều kim đồng hồ', lambda x, y: (-y, x)),
    ('xoay 90° cùng chiều kim đồng hồ', lambda x, y: (y, -x)),
    ('xoay 90° rồi lật', lambda x, y: (y, x)),
    ('xoay 270° rồi lật', lambda x, y: (-y, -x)),
]
MIRROR = {1, 2, 6, 7}        # các phép có lật (đổi mặt vẽ)


def col_of(e):
    c = e.dxf.color if e.dxf.hasattr('color') else 256
    return 7 if c in (0, 7, 256) else c


def load(path):
    """Trả về danh sách entity: ('L', màu, nét, p1, p2) | ('C', màu, '', tâm, R) | ('A', màu, '', tâm, R, đầu, cuối, giữa) | ('P', màu, '', pt)."""
    out = []
    for e in ezdxf.readfile(path).modelspace():
        t = e.dxftype()
        col = col_of(e)
        lt = (e.dxf.linetype if e.dxf.hasattr('linetype') else '').upper()
        if t == 'LINE':
            out.append(('L', col, 'D' if lt == 'DASHED' else '', (e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
        elif t == 'CIRCLE':
            out.append(('C', col, '', (e.dxf.center.x, e.dxf.center.y), e.dxf.radius))
        elif t == 'ARC':
            c, r, a0 = e.dxf.center, e.dxf.radius, e.dxf.start_angle
            sw = (e.dxf.end_angle - a0) % 360
            pt = lambda a: (c.x + r * math.cos(math.radians(a)), c.y + r * math.sin(math.radians(a)))
            out.append(('A', col, '', (c.x, c.y), r, pt(a0), pt(a0 + sw), pt(a0 + sw / 2)))
        elif t == 'POINT':
            out.append(('P', col, '', (e.dxf.location.x, e.dxf.location.y)))
    return out


def tf(ents, fn):
    r = []
    for e in ents:
        k = e[0]
        if k == 'L':
            r.append((k, e[1], e[2], fn(*e[3]), fn(*e[4])))
        elif k == 'C':
            r.append((k, e[1], e[2], fn(*e[3]), e[4]))
        elif k == 'A':
            r.append((k, e[1], e[2], fn(*e[3]), e[4], fn(*e[5]), fn(*e[6]), fn(*e[7])))
        else:
            r.append((k, e[1], e[2], fn(*e[3])))
    return r


def pts(e):
    k = e[0]
    if k == 'L':
        return [e[3], e[4]]
    if k == 'C':
        c, r = e[3], e[4]
        return [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)]
    if k == 'A':
        return [e[5], e[6], e[7]]
    return []


def bbox(ents):
    p = [q for e in ents if e[0] != 'P' for q in pts(e)]
    if not p:
        return (0, 0, 0, 0)
    xs, ys = [q[0] for q in p], [q[1] for q in p]
    return (min(xs), min(ys), max(xs), max(ys))


def shift(ents, bb):
    return tf(ents, lambda x, y: (x - bb[0], y - bb[1]))


def close(a, b, tol):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def eq(a, b, tol):
    if a[0] != b[0] or a[1] != b[1] or a[2] != b[2]:
        return False
    k = a[0]
    if k == 'L':
        return (close(a[3], b[3], tol) and close(a[4], b[4], tol)) or (close(a[3], b[4], tol) and close(a[4], b[3], tol))
    if k == 'C':
        return close(a[3], b[3], tol) and abs(a[4] - b[4]) <= tol
    if k == 'A':
        ends = (close(a[5], b[5], tol) and close(a[6], b[6], tol)) or (close(a[5], b[6], tol) and close(a[6], b[5], tol))
        return close(a[3], b[3], tol) and abs(a[4] - b[4]) <= tol and ends and close(a[7], b[7], tol)
    return close(a[3], b[3], tol)


def pair(A, B, tol):
    """Ghép tham lam hai danh sách entity; trả về (số cặp, A chưa ghép, B chưa ghép)."""
    used, ua = set(), []
    n = 0
    for a in A:
        hit = next((j for j, b in enumerate(B) if j not in used and eq(a, b, tol)), None)
        if hit is None:
            ua.append(a)
        else:
            used.add(hit)
            n += 1
    return n, ua, [b for j, b in enumerate(B) if j not in used]


def f2(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def P(p):
    return '(%s; %s)' % (f2(p[0]), f2(p[1]))


def near(a, b, d):
    return math.hypot(a[0] - b[0], a[1] - b[1]) <= d


def diff(T, F, tol):
    """T, F: entity đã dời về gốc và đặt cùng hướng. Trả về danh sách {loai, mo_ta}."""
    out = []
    # --- lỗ tròn: cùng tâm khác φ -> sai kích thước; cùng φ khác tâm -> sai vị trí; còn lại thiếu/thừa
    _, ct, cf = pair([e for e in T if e[0] == 'C'], [e for e in F if e[0] == 'C'], tol)
    dia = {}
    for t in list(ct):
        f = next((f for f in cf if near(t[3], f[3], 0.5) and abs(t[4] - f[4]) > tol), None)
        if f:
            ct.remove(t); cf.remove(f)
            dia.setdefault((f2(2 * f[4]), f2(2 * t[4])), []).append(t[3])
    for (fd, td), ps in dia.items():
        out.append({'loai': 'Sai kích thước lỗ', 'mo_ta': '%d lỗ: F φ%s, T φ%s, tại %s' % (len(ps), fd, td, ', '.join(map(P, ps[:8])) + (' ...' if len(ps) > 8 else ''))})
    for t in list(ct):
        f = min((f for f in cf if abs(t[4] - f[4]) <= tol), key=lambda f: math.hypot(t[3][0] - f[3][0], t[3][1] - f[3][1]), default=None)
        if f:
            ct.remove(t); cf.remove(f)
            out.append({'loai': 'Sai vị trí lỗ', 'mo_ta': 'lỗ φ%s: F tại %s, T tại %s' % (f2(2 * t[4]), P(f[3]), P(t[3]))})
    for t in ct:
        out.append({'loai': 'Thiếu lỗ', 'mo_ta': 'F thiếu lỗ φ%s tại %s (T có)' % (f2(2 * t[4]), P(t[3]))})
    for f in cf:
        out.append({'loai': 'Thừa lỗ', 'mo_ta': 'F thừa lỗ φ%s tại %s (T không có)' % (f2(2 * f[4]), P(f[3]))})
    # --- POINT (lỗ piercing): khác màu cùng vị trí = sai màu PIERCING
    _, pt_, pf = pair([e for e in T if e[0] == 'P'], [e for e in F if e[0] == 'P'], tol)
    for t in list(pt_):
        f = next((f for f in pf if close(t[3], f[3], tol)), None)
        if f:
            pt_.remove(t); pf.remove(f)
            out.append({'loai': 'Sai màu PIERCING', 'mo_ta': 'POINT tại %s: F màu %s, T màu %s' % (P(t[3]), f[1], t[1])})
    for t in pt_:
        out.append({'loai': 'Thiếu lỗ', 'mo_ta': 'F thiếu POINT tại %s (T có)' % P(t[3])})
    for f in pf:
        out.append({'loai': 'Thừa lỗ', 'mo_ta': 'F thừa POINT tại %s (T không có)' % P(f[3])})
    # --- cung: cùng tâm khác R = sai bo R; còn lại thiếu/thừa (thuộc biên dạng)
    _, at, af = pair([e for e in T if e[0] == 'A'], [e for e in F if e[0] == 'A'], tol)
    for t in list(at):
        f = next((f for f in af if near(t[3], f[3], 1.0) and abs(t[4] - f[4]) > tol), None)
        if f:
            at.remove(t); af.remove(f)
            out.append({'loai': 'Sai kích thước bo R', 'mo_ta': 'cung gần %s: F R%s, T R%s' % (P(t[3]), f2(f[4]), f2(t[4]))})
    for t in list(at):
        f = next((f for f in af if near(t[3], f[3], tol) and abs(t[4] - f[4]) <= tol), None)
        if f:
            at.remove(t); af.remove(f)
            out.append({'loai': 'Sai biên dạng ngoài', 'mo_ta': 'cung R%s tâm %s: đầu mút khác nhau (F %s-%s, T %s-%s)' % (f2(t[4]), P(t[3]), P(f[5]), P(f[6]), P(t[5]), P(t[6]))})
    for t in at:
        out.append({'loai': 'Sai biên dạng ngoài', 'mo_ta': 'F thiếu cung R%s tâm %s (T có)' % (f2(t[4]), P(t[3]))})
    for f in af:
        out.append({'loai': 'Sai biên dạng ngoài', 'mo_ta': 'F thừa cung R%s tâm %s (T không có)' % (f2(f[4]), P(f[3]))})
    # --- đường thẳng, theo nhóm: kegaki (đỏ 1), rạch Green (3), đường uốn (nét đứt), biên
    def grp(e):
        return 'kegaki' if e[1] == 1 else 'green' if e[1] == 3 else 'uon' if e[2] == 'D' else 'bien'
    names = {'kegaki': 'Sai kegaki', 'green': 'Sai rạch Green', 'uon': 'Sai độ giãn dài (đường uốn)', 'bien': 'Sai biên dạng ngoài'}
    for g in ('bien', 'uon', 'kegaki', 'green'):
        _, lt, lf = pair([e for e in T if e[0] == 'L' and grp(e) == g], [e for e in F if e[0] == 'L' and grp(e) == g], tol)
        def seg(e):
            return '%s-%s' % (P(e[3]), P(e[4]))
        if lt or lf:
            more = ' (+%d đường nữa)' % (len(lt) + len(lf) - 8) if len(lt) + len(lf) > 8 else ''
            out.append({'loai': names[g], 'mo_ta': 'đường khác nhau (%s): T có %d đường F không có [%s]; F có %d đường T không có [%s]%s'
                        % ({'bien': 'biên', 'uon': 'uốn', 'kegaki': 'kegaki', 'green': 'rạch Green'}[g], len(lt), '; '.join(map(seg, lt[:4])) or '-',
                           len(lf), '; '.join(map(seg, lf[:4])) or '-', more)})
    return out


def compare(tpath, fpath, tol=0.05):
    T0, F0 = load(tpath), load(fpath)
    if not T0 or not F0:
        raise ValueError('file không có entity')
    T = shift(T0, bbox(T0))
    scored = []
    for i in (0, 3, 4, 5, 1, 2, 6, 7):          # xoay trước, lật sau: hoà điểm thì chọn phép xoay
        name, fn = TRANSFORMS[i]
        Ft = tf(F0, fn)
        Fs = shift(Ft, bbox(Ft))
        un = 0
        for k in ('L', 'C', 'A', 'P'):
            _, a, b = pair([e for e in T if e[0] == k], [e for e in Fs if e[0] == k], tol)
            un += len(a) + len(b)
        scored.append((un, len(scored), i, name, Fs))
    scored.sort(key=lambda x: (x[0], x[1]))
    un, _, i, name, Fs = scored[0]
    tie = [x[3] for x in scored[1:] if x[0] == un]
    bt, bf = bbox(T), bbox(Fs)
    wt, ht, wf, hf = bt[2], bt[3], bf[2], bf[3]
    res = {'T': tpath, 'F': fpath, 'khung_bao_T': [round(wt, 3), round(ht, 3)], 'khung_bao_F': [round(wf, 3), round(hf, 3)],
           'phep_dat_huong': name, 'khac_biet': [], 'ghi_chu': []}
    if i:
        res['khac_biet'].append({'loai': 'Sai mặt vẽ (lật)' if i in MIRROR else 'Hướng đặt khác',
                                 'mo_ta': 'F khớp T nhất sau khi %s%s (toạ độ bên dưới ở hệ của T)' % (name, (', hoặc cũng khớp như nhau sau khi ' + ' / '.join(tie) + ' (hình đối xứng nên không phân biệt được)') if tie else '')})
    if abs(wt - wf) > tol or abs(ht - hf) > tol:
        res['khac_biet'].append({'loai': 'Sai biên dạng ngoài', 'mo_ta': 'khung bao: F %s x %s, T %s x %s' % (f2(wf), f2(hf), f2(wt), f2(ht))})
    res['khac_biet'] += diff(T, Fs, tol)
    # chênh nhỏ dưới 0.05: ghi chú, không tính lỗi
    loose = pair(T, Fs, 0.5)
    exact = pair(T, Fs, 1e-4)
    if loose[0] > exact[0] and not res['khac_biet']:
        res['ghi_chu'].append('hai file khớp trong sai số %s; còn chênh nhỏ (vd 0.005) giữa một số toạ độ, không tính là lỗi' % tol)
    res['khop'] = not [x for x in res['khac_biet'] if not x['loai'].startswith('Hướng đặt')]
    tot = len(T) + len(Fs)                      # M4: tỉ lệ entity khớp giữa F và T sau khi đặt cùng hướng
    res['so_entity_T'], res['so_entity_F'] = len(T), len(Fs)
    res['ty_le_khop'] = round(100.0 * (tot - un) / tot, 1) if tot else 0.0
    return res


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('T')
    ap.add_argument('F')
    ap.add_argument('--tol', type=float, default=0.05)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv[1:])
    try:
        r = compare(a.T, a.F, a.tol)
    except Exception as e:
        print('Lỗi đọc file:', e)
        return 2
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print('T %s x %s | F %s x %s | %s' % (f2(r['khung_bao_T'][0]), f2(r['khung_bao_T'][1]), f2(r['khung_bao_F'][0]), f2(r['khung_bao_F'][1]), r['phep_dat_huong']))
        for x in r['khac_biet']:
            print('- [%s] %s' % (x['loai'], x['mo_ta']))
        for x in r['ghi_chu']:
            print('* ' + x)
        print('Entity khớp: %s%% (T %d, F %d entity)' % (r['ty_le_khop'], r['so_entity_T'], r['so_entity_F']))
        print('KẾT LUẬN: ' + ('khớp' if r['khop'] else 'có khác biệt'))
    return 0 if r['khop'] else 1


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    sys.exit(main(sys.argv))
