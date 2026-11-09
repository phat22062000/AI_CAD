# -*- coding: utf-8 -*-
"""So DXF mới với DXF đáp án (đã giao và đã chấm Đúng), từng mã: khung bao, lỗ theo đường kính, cung theo bán kính,
đường theo màu (kegaki đỏ 62=1, uốn xanh 62=3...), điểm, chữ.

Dùng:  py -X utf8 compare_dxf.py <thư mục đáp án> <thư mục mới> [--tol 0.05] [--json out.json]
Mỗi thư mục chứa các file 26-xxxxxx.dxf. Mã thoát 0 = mọi mã khớp, 1 = có mã lệch hoặc thiếu.
Khung bao so sau khi dời về gốc; kích thước trùng nhưng xoay 90 độ hoặc đảo hướng chỉ báo CẢNH BÁO (hình vẽ có thể đặt khác hướng).
"""
import glob
import json
import math
import os
import re
import sys
from collections import Counter

import ezdxf

CODE_RE = re.compile(r'(26-\d{6})\.dxf$', re.I)


def signature(path):
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    xs, ys = [], []
    circles, arcs, lines, points, texts = Counter(), Counter(), Counter(), Counter(), []

    def grow(x, y):
        xs.append(x)
        ys.append(y)

    for e in msp:
        t = e.dxftype()
        col = e.dxf.color if e.dxf.hasattr('color') else 256
        if t == 'LINE':
            a, b = e.dxf.start, e.dxf.end
            lines[(col, round(math.dist((a.x, a.y), (b.x, b.y)), 2))] += 1
            grow(a.x, a.y)
            grow(b.x, b.y)
        elif t == 'CIRCLE':
            c, r = e.dxf.center, e.dxf.radius
            circles[round(2 * r, 2)] += 1
            grow(c.x - r, c.y - r)
            grow(c.x + r, c.y + r)
        elif t == 'ARC':
            c, r = e.dxf.center, e.dxf.radius
            sweep = (e.dxf.end_angle - e.dxf.start_angle) % 360
            arcs[(round(r, 2), round(sweep))] += 1
            for k in range(0, 21):
                a = math.radians(e.dxf.start_angle + sweep * k / 20)
                grow(c.x + r * math.cos(a), c.y + r * math.sin(a))
            # điểm cực trị (0/90/180/270 độ) nằm trong cung: nếu thiếu, khung bao bị hụt khi cung đi qua đỉnh ngang/đứng
            for q in (0, 90, 180, 270):
                if (q - e.dxf.start_angle) % 360 <= sweep:
                    a = math.radians(q)
                    grow(c.x + r * math.cos(a), c.y + r * math.sin(a))
        elif t == 'POINT':
            points[col] += 1
        elif t in ('TEXT', 'MTEXT'):
            texts.append(e.dxf.text.strip() if t == 'TEXT' else e.text.strip())
    if not xs:
        return None
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    return {'w': round(w, 3), 'h': round(h, 3), 'circles': circles, 'arcs': arcs, 'lines': lines,
            'points': points, 'texts': sorted(texts)}


def line_summary(lines):
    by = Counter()
    for (col, ln), n in lines.items():
        by[col] += n
    return dict(by)


def compare(ref, new, tol):
    out = {'ok': True, 'notes': [], 'diffs': []}
    if ref is None or new is None:
        out['ok'] = False
        out['diffs'].append('không đọc được hình')
        return out
    dims_ref, dims_new = sorted((ref['w'], ref['h'])), sorted((new['w'], new['h']))
    if all(abs(a - b) <= tol for a, b in zip(dims_ref, dims_new)):
        if not (abs(ref['w'] - new['w']) <= tol and abs(ref['h'] - new['h']) <= tol):
            out['notes'].append(f"khung bao cùng kích thước nhưng khác hướng: đáp án {ref['w']} x {ref['h']}, mới {new['w']} x {new['h']}")
    else:
        out['ok'] = False
        out['diffs'].append(f"khung bao: đáp án {ref['w']} x {ref['h']}, mới {new['w']} x {new['h']}")
    for key, name in (('circles', 'lỗ (đường kính)'), ('arcs', 'cung (R, góc)'), ('points', 'điểm (màu)')):
        if ref[key] != new[key]:
            out['ok'] = False
            out['diffs'].append(f"{name}: đáp án {dict(ref[key])}, mới {dict(new[key])}")
    if line_summary(ref['lines']) != line_summary(new['lines']):
        out['ok'] = False
        out['diffs'].append(f"số đường theo màu: đáp án {line_summary(ref['lines'])}, mới {line_summary(new['lines'])}")
    elif ref['lines'] != new['lines']:
        out['notes'].append('cùng số đường theo màu nhưng độ dài từng đường khác (có thể do bo hoặc đặt hướng khác)')
    if ref['texts'] != new['texts']:
        out['ok'] = False
        out['diffs'].append(f"chữ: đáp án {ref['texts']}, mới {new['texts']}")
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    ref_dir, new_dir = argv[1], argv[2]
    tol = float(argv[argv.index('--tol') + 1]) if '--tol' in argv else 0.05
    refs = {m.group(1): p for p in glob.glob(os.path.join(ref_dir, '26-*.dxf')) if (m := CODE_RE.search(p))}
    news = {m.group(1): p for p in glob.glob(os.path.join(new_dir, '26-*.dxf')) if (m := CODE_RE.search(p))}
    result, ok_n = {}, 0
    for code in sorted(refs):
        if code not in news:
            result[code] = {'ok': False, 'notes': [], 'diffs': ['thiếu file DXF mới']}
            continue
        try:
            r = compare(signature(refs[code]), signature(news[code]), tol)
        except Exception as e:
            r = {'ok': False, 'notes': [], 'diffs': ['lỗi đọc: ' + str(e)]}
        result[code] = r
    for code in sorted(news):
        if code not in refs:
            result[code] = {'ok': True, 'notes': ['không có trong đáp án (mã thêm)'], 'diffs': []}
    for code, r in result.items():
        ok_n += r['ok']
        flag = 'KHỚP ' if r['ok'] else 'LỆCH '
        print(f"{flag} {code}" + ('' if r['ok'] and not r['notes'] else ''))
        for d in r['diffs']:
            print('   - ' + d)
        for n in r['notes']:
            print('   * ' + n)
    print(f"=== so DXF: {ok_n}/{len(result)} mã khớp đáp án ===")
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w', encoding='utf-8') as f:
            json.dump({k: v for k, v in result.items()}, f, ensure_ascii=False, indent=1)
    return 0 if ok_n == len(result) else 1


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    sys.exit(main(sys.argv))
