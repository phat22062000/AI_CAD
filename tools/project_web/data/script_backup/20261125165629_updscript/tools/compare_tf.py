# -*- coding: utf-8 -*-
"""compare_tf.py - tạo file DXF so sánh T (đúng) và F (AI vẽ): F bên trái, T bên phải, cùng hướng,
tô màu hồng (lớp KHAC_NHAU, màu 6) các đối tượng khác nhau giữa hai hình, chỉ có label "False" / "True" bên dưới.

Dùng:  py -X utf8 compare_tf.py <T.dxf> <F.dxf> <out.dxf> [--tol 0.05]
Mã thoát: 0 = đã tạo file, 2 = lỗi.

Cách làm: phá polyline / block thành đường, cung, tròn, điểm; thử 8 phép đặt hướng của F (giữ, xoay, lật) lấy phép khớp T nhất
(như diff_tf.py), dời hai hình về gốc rồi ghép từng đối tượng trong sai số --tol (cùng loại, cùng màu, cùng nét, cùng vị trí và kích thước).
Đối tượng không ghép được ở hình nào thì tô màu ở hình đó. TEXT, ELLIPSE, SPLINE chỉ chép sang, không so.
"""
import math
import os
import sys

import ezdxf
from ezdxf import zoom
from ezdxf.math import Vec3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diff_tf as D      # noqa: E402


# ---------- chép hình (đổi hướng + dời), tự dựng lại cung để lật không sinh OCS ngược ----------
def _flat(doc):
    """Liệt kê entity hình học của modelspace; INSERT / polyline được phá ra entity con."""
    out = []

    def walk(e, depth=0):
        t = e.dxftype()
        if t in ('LINE', 'ARC', 'CIRCLE', 'POINT', 'TEXT', 'MTEXT'):
            out.append(e)
        elif t in ('LWPOLYLINE', 'POLYLINE', 'INSERT') and depth < 4:
            try:
                for v in e.virtual_entities():
                    walk(v, depth + 1)
            except Exception:
                pass
        elif t in ('ELLIPSE', 'SPLINE'):
            out.append(e)
    for e in doc.modelspace():
        if e.dxftype() != 'DIMENSION':
            walk(e)
    return out


def _attrs(e, src, dst):
    lay = e.dxf.get('layer', '0')
    if lay not in dst.layers:
        try:
            sl = src.layers.get(lay)
            dst.layers.add(lay, color=sl.dxf.color, linetype=sl.dxf.get('linetype', 'Continuous'))
        except Exception:
            dst.layers.add(lay)
    a = {'layer': lay}
    if e.dxf.hasattr('color'):
        a['color'] = e.dxf.color
    lt = e.dxf.get('linetype')
    if lt and lt.upper() != 'BYLAYER' and lt in dst.linetypes:      # bản mới có sẵn các nét chuẩn (DASHED...); nét lạ thì bỏ
        a['linetype'] = lt
    return a


HL_LAYER, HL_COLOR = 'KHAC_NHAU', 6


DIM_LAYER = 'Dim'
DIM_DEFAULTS = {'dimfxl': 1.0, 'dimlfac': 1.0, 'dimtfac': 1.0, 'dimdsep': 46, 'dimtmove': 0, 'dimupt': 0}


def add_dim_setup(doc):
    """Lớp Dim (màu 5, nét 0.13) và Dimstyle DIM lấy đúng từ file tham khảo ThamKhaoDimStyle.dxf của Phát (18/11/2026),
    để dùng ngay cho kích thước trên file Compare. Chỉ tạo sẵn, không tự dim."""
    if DIM_LAYER not in doc.layers:
        doc.layers.add(DIM_LAYER, color=5, lineweight=13)
    if 'DIM' not in doc.dimstyles:
        ds = doc.dimstyles.new('DIM', dxfattribs={
            'dimscale': 1.5, 'dimasz': 2.0, 'dimexo': 0.0, 'dimdli': 10.0, 'dimexe': 1.0,
            'dimtih': 0, 'dimtoh': 0, 'dimtad': 1, 'dimzin': 8, 'dimazin': 2,
            'dimtxt': 4.0, 'dimcen': 0.0, 'dimgap': 0.625, 'dimtofl': 1, 'dimtix': 1, 'dimsoxd': 1,
            'dimclrd': 5, 'dimclre': 5, 'dimclrt': 2, 'dimadec': 2, 'dimdec': 2, 'dimtdec': 2,
            'dimlwd': 25, 'dimlwe': 25, 'dimtxsty': 'Standard'})
        ds.set_arrows(blk=ezdxf.ARROWS.open, ldrblk=ezdxf.ARROWS.open)      # đầu mũi tên Open như file tham khảo
    # Dimstyle hiện hành mặc định là DIM: đặt $DIMSTYLE và chép MỌI thông số của style sang các biến dim của header.
    # Header phải trùng từng giá trị với style, lệch một biến là CAD báo "<style overrides>" thay vì DIM. File tham khảo không ghi 6 biến dưới
    # nên dùng giá trị mặc định của CAD, đặt cả ở style lẫn header.
    ds = doc.dimstyles.get('DIM')
    for k, v in DIM_DEFAULTS.items():
        ds.dxf.set(k, v)
    doc.header['$DIMSTYLE'] = 'DIM'
    doc.header['$CLAYER'] = DIM_LAYER      # layer hiện hành mặc định là Dim: vẽ gì thêm cũng nằm ở Dim
    doc.header['$ORTHOMODE'] = 1           # luôn bật Ortho (F8)
    for k, v in ds.dxf.all_existing_dxf_attribs().items():
        if k.startswith('dim'):
            try:
                doc.header['$' + k.upper()] = v
            except Exception:
                pass
    doc.header['$DIMBLK'] = '_OPEN'      # cùng tên mũi tên Open với style DIM (ezdxf tự đổi thành OPEN khi chép)
    doc.header['$DIMLDRBLK'] = '_OPEN'


def fit_view(doc, aspect=1.6, margin=1.1):
    """Zoom Extents: khung nhìn hiện hành đặt giữa toàn bộ hình (cả False lẫn True), chừa lề `margin`.
    CAD tính bề rộng nhìn thấy = chiều cao khung x tỉ lệ cửa sổ thật, nên chọn chiều cao đủ để cả bề rộng lẫn bề cao vừa khi cửa sổ có tỉ lệ >= `aspect`."""
    from ezdxf import bbox
    msp = doc.modelspace()
    bb = bbox.extents(msp)
    if not bb.has_data:
        return
    c, w, h = bb.center, bb.size.x, bb.size.y
    vp = doc.viewports.get('*Active')[0]
    vp.dxf.center = (c.x, c.y)
    vp.dxf.height = max(h * margin, w * margin / aspect, 1.0)
    vp.dxf.aspect_ratio = aspect
    doc.header['$EXTMIN'] = (bb.extmin.x, bb.extmin.y, 0)
    doc.header['$EXTMAX'] = (bb.extmax.x, bb.extmax.y, 0)
    doc.header['$LIMMIN'] = (bb.extmin.x, bb.extmin.y)
    doc.header['$LIMMAX'] = (bb.extmax.x, bb.extmax.y)


def copy_into(src, msp, fn, mirror, dx, dy, flats, hl):
    """fn: phép đặt hướng (x, y) -> (x', y'); sau đó dời (dx, dy). hl: chỉ số entity (trong flats) cần tô màu khác."""
    dst = msp.doc
    P = lambda x, y: (fn(x, y)[0] + dx, fn(x, y)[1] + dy)
    for idx, e in enumerate(flats):
        t = e.dxftype()
        a = _attrs(e, src, dst)
        if idx in hl:
            a['layer'], a['color'] = HL_LAYER, HL_COLOR
        if t == 'LINE':
            msp.add_line(P(e.dxf.start.x, e.dxf.start.y), P(e.dxf.end.x, e.dxf.end.y), dxfattribs=a)
        elif t == 'CIRCLE':
            msp.add_circle(P(e.dxf.center.x, e.dxf.center.y), e.dxf.radius, dxfattribs=a)
        elif t == 'POINT':
            msp.add_point(P(e.dxf.location.x, e.dxf.location.y), dxfattribs=a)
        elif t == 'ARC':
            c, r = e.dxf.center, e.dxf.radius
            a0, a1 = e.dxf.start_angle, e.dxf.end_angle
            if e.dxf.get('extrusion', (0, 0, 1))[2] < 0:       # cung OCS ngược: đổi về WCS
                c = Vec3(-c.x, c.y, c.z)
                a0, a1 = 180 - a1, 180 - a0
            pt = lambda ang: (c.x + r * math.cos(math.radians(ang)), c.y + r * math.sin(math.radians(ang)))
            p0, p1 = P(*pt(a0)), P(*pt(a1))
            cc = P(c.x, c.y)
            b0 = math.degrees(math.atan2(p0[1] - cc[1], p0[0] - cc[0]))
            b1 = math.degrees(math.atan2(p1[1] - cc[1], p1[0] - cc[0]))
            if mirror:                       # lật thì chiều quay đảo: đổi đầu cuối
                b0, b1 = b1, b0
            msp.add_arc(cc, r, b0 % 360, b1 % 360, dxfattribs=a)
        elif t in ('ELLIPSE', 'SPLINE'):
            try:
                ps = [P(v.x, v.y) for v in e.flattening(0.05)]
                for p, q in zip(ps, ps[1:]):
                    msp.add_line(p, q, dxfattribs=a)
            except Exception:
                pass
        elif t in ('TEXT', 'MTEXT'):
            ins = e.dxf.insert
            txt = e.dxf.text if t == 'TEXT' else e.plain_text()
            h = e.dxf.get('height', 2.5) if t == 'TEXT' else e.dxf.get('char_height', 2.5)
            te = msp.add_text(txt, height=h, dxfattribs=a)
            try:
                te.set_placement(P(ins.x, ins.y))
            except AttributeError:
                te.set_pos(P(ins.x, ins.y))


# ---------- so khớp ----------
def tup(e):
    """Entity -> dạng so của diff_tf ('L'|'C'|'A'|'P', màu, nét, ...) ở toạ độ gốc; None nếu không so."""
    t = e.dxftype()
    col = D.col_of(e)
    lt = (e.dxf.get('linetype') or '').upper()
    if t == 'LINE':
        return ('L', col, 'D' if lt == 'DASHED' else '', (e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y))
    if t == 'CIRCLE':
        return ('C', col, '', (e.dxf.center.x, e.dxf.center.y), e.dxf.radius)
    if t == 'ARC':
        c, r, a0 = e.dxf.center, e.dxf.radius, e.dxf.start_angle
        a1 = e.dxf.end_angle
        cx = c.x
        if e.dxf.get('extrusion', (0, 0, 1))[2] < 0:
            cx, a0, a1 = -c.x, 180 - a1, 180 - a0
        sw = (a1 - a0) % 360
        pt = lambda a: (cx + r * math.cos(math.radians(a)), c.y + r * math.sin(math.radians(a)))
        return ('A', col, '', (cx, c.y), r, pt(a0), pt(a0 + sw), pt(a0 + sw / 2))
    if t == 'POINT':
        return ('P', col, '', (e.dxf.location.x, e.dxf.location.y))
    return None


def prep(flats):
    idx, ts = [], []
    for i, e in enumerate(flats):
        try:
            x = tup(e)
        except Exception:
            x = None
        if x:
            idx.append(i); ts.append(x)
    return idx, ts


def _key(e):
    k = e[0]
    if k == 'L':
        return min(e[3], e[4])
    return e[3]


def unmatched(A, B, tol):
    """Ghép A với B (D.eq, tra theo lưới 1 mm cho nhanh); trả về chỉ số phần tử chưa ghép của A và của B."""
    grid = {}
    for j, b in enumerate(B):
        p = _key(b)
        grid.setdefault((b[0], int(math.floor(p[0])), int(math.floor(p[1]))), []).append(j)
    used, ua = set(), set()
    for i, a in enumerate(A):
        p = _key(a)
        cx, cy = int(math.floor(p[0])), int(math.floor(p[1]))
        hit = None
        for gx in (cx - 1, cx, cx + 1):
            for gy in (cy - 1, cy, cy + 1):
                for j in grid.get((a[0], gx, gy), ()):
                    if j not in used and D.eq(a, B[j], tol):
                        hit = j
                        break
                if hit is not None:
                    break
            if hit is not None:
                break
        if hit is None:
            ua.add(i)
        else:
            used.add(hit)
    return ua, set(range(len(B))) - used


def put_text(msp, txt, h, p, align):
    """Chữ căn giữa; chạy được cả ezdxf mới (set_placement) lẫn cũ (set_pos)."""
    t = msp.add_text(txt, height=h, dxfattribs={'layer': 'LABEL'})
    try:
        from ezdxf.enums import TextEntityAlignment
        t.set_placement(p, align=getattr(TextEntityAlignment, align))
    except Exception:
        t.set_pos(p, align=align)


def build(tpath, fpath, out, tol=0.05):
    tdoc, fdoc = ezdxf.readfile(tpath), ezdxf.readfile(fpath)
    tflat, fflat = _flat(tdoc), _flat(fdoc)
    tidx, T0 = prep(tflat)
    fidx, F0 = prep(fflat)
    if not T0 or not F0:
        raise ValueError('file không có đường, cung, lỗ để so')
    bt = D.bbox(T0)
    T = D.shift(T0, bt)
    best = None
    for i in (0, 3, 4, 5, 1, 2, 6, 7):          # xoay trước, lật sau (như diff_tf)
        name, fn = D.TRANSFORMS[i]
        Ft = D.tf(F0, fn)
        bf = D.bbox(Ft)
        Fs = D.shift(Ft, bf)
        ua, ub = unmatched(T, Fs, tol)
        if best is None or len(ua) + len(ub) < best[0]:
            best = (len(ua) + len(ub), i, name, fn, Fs, bf, ua, ub)
    _, i, name, fn, F, bf, ua, ub = best
    wt, ht = D.bbox(T)[2], D.bbox(T)[3]
    wf, hf = D.bbox(F)[2], D.bbox(F)[3]
    size = max(wt, ht, wf, hf, 1.0)
    gap = max(80.0, 0.3 * size)
    xT = wf + gap
    doc = ezdxf.new('R2010', setup=True)
    doc.header['$INSUNITS'] = 4
    doc.layers.add(HL_LAYER, color=HL_COLOR)
    add_dim_setup(doc)
    msp = doc.modelspace()
    hlF = {fidx[k] for k in ub}
    hlT = {tidx[k] for k in ua}
    copy_into(fdoc, msp, fn, i in D.MIRROR, -bf[0], -bf[1], fflat, hlF)
    copy_into(tdoc, msp, lambda x, y: (x, y), False, -bt[0] + xT, -bt[1], tflat, hlT)
    th = max(5.0, min(40.0, round(0.085 * size, 1)))
    if 'LABEL' not in doc.layers:
        doc.layers.add('LABEL', color=7)
    put_text(msp, 'False', th, (wf / 2, -3 * th), 'BOTTOM_CENTER')
    put_text(msp, 'True', th, (xT + wt / 2, -3 * th), 'BOTTOM_CENTER')
    fit_view(doc)      # mở file là thấy cả hai hình nằm giữa khung hình, như lệnh Zoom Extents (ZOOM E)
    tmp = out + '.tmp'
    doc.saveas(tmp)
    os.replace(tmp, out)
    return {'out': out, 'huong': name, 'F': len(hlF), 'T': len(hlT)}


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    tol = 0.05
    if '--tol' in argv:
        tol = float(argv[argv.index('--tol') + 1])
    try:
        r = build(argv[1], argv[2], argv[3], tol)
    except Exception as e:
        print('Lỗi:', e)
        return 2
    print('Đã tạo %s | hướng F: %s | tô màu khác nhau: F %d, T %d' % (r['out'], r['huong'], r['F'], r['T']))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    sys.exit(main(sys.argv))
