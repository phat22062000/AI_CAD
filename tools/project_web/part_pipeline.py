# -*- coding: utf-8 -*-
"""part_pipeline.py - MỘT lệnh cho mỗi mã: dựng file DXF riêng từ spec, kiểm bằng dxf_check, báo tiến độ.

Dùng (agent chạy MỘT lần cho mỗi mã, sau khi đã ghi spec bằng geom.save_spec):
  py -X utf8 part_pipeline.py <spec_<mã>.json> <thư_mục_đơn> [--order 521106-24] [--report] [--keep-checking]
Việc làm:
  1. Dựng <thư_mục_đơn>\\<mã>.dxf từ spec trên Template.dxf (cùng cách ghi với merge_all.py của kit: owner 6F, handle, cp932...).
  2. Chạy dxf_check.py (py -X utf8 ... --template --tpl Template.dxf) và CHỈ in dòng LỖI / CẢNH BÁO.
  3. Có --report: ghi tiến độ status=built (blank = w x h, flags theo spec) lên trang. Có LỖI thì ghi status=running level=2 để agent sửa.
Mã thoát 1 nếu dxf_check báo LỖI (agent phải sửa spec rồi chạy lại mã đó trước khi sang mã kế).
Không sửa file nào của skill hoặc kit: chỉ đọc geom spec + Template.dxf.
"""
import json
import os
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
REPO = os.path.join(ROOT, 'Create_Flatten_SheetMetal-main')
TPL_DEFAULT = os.path.join(REPO, 'templates', 'Template.dxf')
CHECK = os.path.join(REPO, 'tools', 'dxf_check.py')
REPORT = os.path.join(HERE, 'report.py')


def f(v):
    v = round(float(v), 8)
    if abs(v) < 1e-9:
        v = 0.0
    s = ('%.8f' % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def build_lines(spec, tpl_path):
    """Trả danh sách dòng DXF của file riêng (không có chữ mã và Flag: đó là phần của file ALL)."""
    T = open(tpl_path, 'rb').read().decode('cp932').split('\r\n')
    handle = int(T[T.index('$HANDSEED') + 2], 16)
    ents = []

    def ent(kind, head, body):
        nonlocal handle
        ents.extend(['  0', kind, '  5', '%X' % handle, '330', '6F', '100', 'AcDbEntity', '  8', '0'] + head + body)
        handle += 1

    def col(e):
        return ['62', str(e['color'])] if e.get('color') else []

    for e in spec['entities']:
        t = e['t']
        if t == 'LINE':
            p, q = e['p1'], e['p2']
            h = col(e) + (['  6', 'DASHED'] if e.get('dashed') else [])
            ent('LINE', h, ['100', 'AcDbLine', ' 10', f(p[0]), ' 20', f(p[1]), ' 30', '0.0', ' 11', f(q[0]), ' 21', f(q[1]), ' 31', '0.0'])
        elif t == 'ARC':
            ent('ARC', col(e), ['100', 'AcDbCircle', ' 10', f(e['c'][0]), ' 20', f(e['c'][1]), ' 30', '0.0', ' 40', f(e['r']),
                                '100', 'AcDbArc', ' 50', f(e['a0']), ' 51', f(e['a1'])])
        elif t == 'CIRCLE':
            ent('CIRCLE', col(e), ['100', 'AcDbCircle', ' 10', f(e['c'][0]), ' 20', f(e['c'][1]), ' 30', '0.0', ' 40', f(e['r'])])
        elif t == 'POINT':
            ent('POINT', col(e), ['100', 'AcDbPoint', ' 10', f(e['p'][0]), ' 20', f(e['p'][1]), ' 30', '0.0'])
        # TEXT: chỉ có trong file ALL
    L = T[:]
    i = L.index('ENTITIES')
    j = L.index('ENDSEC', i)
    L = L[:i + 1] + ents + L[j - 1:]
    L[L.index('$HANDSEED') + 2] = '%X' % handle
    em = L.index('$EXTMAX')
    L[em + 2] = f(spec['w'])
    L[em + 4] = f(spec['h'])
    va = L.index('*Active')

    def setv(code, val):
        for m in range(va, va + 80):
            if L[m] == code:
                L[m + 1] = val
                return

    setv(' 12', f(spec['w'] / 2))
    setv(' 22', f(spec['h'] / 2))
    setv(' 40', f(1.1 * max(spec['h'], spec['w'] / 2.34)))
    for m in range(len(L)):
        if L[m] == 'Standard' and L[m - 1] == '  2' and L[m - 2] == 'AcDbTextStyleTableRecord':
            for q in range(m, m + 20):
                if L[q] == '  3':
                    L[q + 1] = 'arial.ttf'
                    break
    return L


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    spec_path, out_dir = argv[1], argv[2]
    order = argv[argv.index('--order') + 1] if '--order' in argv else ''
    tpl = argv[argv.index('--tpl') + 1] if '--tpl' in argv else TPL_DEFAULT
    spec = json.load(open(spec_path, encoding='utf-8'))
    code = spec['code']
    out = os.path.join(out_dir, code + '.dxf')
    lines = build_lines(spec, tpl)
    with open(out, 'wb') as fh:
        fh.write('\r\n'.join(lines).encode('cp932'))
    # kiểm: chỉ in LỖI / CẢNH BÁO
    r = subprocess.run([sys.executable, '-X', 'utf8', CHECK, out, '--template', '--tpl', tpl], capture_output=True, text=True, encoding='utf-8', errors='replace')
    text = (r.stdout or '') + (r.stderr or '')
    n_err = n_warn = 0
    show, cur = [], ''
    for ln in text.split('\n'):
        m = ln.strip()
        if m.startswith('[LỖI]'):
            cur = 'err'
            try:
                n_err = int(m.split(']')[1])
            except ValueError:
                n_err = 0
            continue
        if m.startswith('[CẢNH BÁO]'):
            cur = 'warn'
            try:
                n_warn = int(m.split(']')[1])
            except ValueError:
                n_warn = 0
            continue
        if m.startswith('[THÔNG TIN]'):
            cur = ''
            continue
        if cur and m.startswith('- '):
            # NGUỒN: ... không có lớp chữ: thông báo cố định của PDF scan, bỏ cho gọn
            if 'không có lớp chữ' in m or 'Không tìm thấy Template' in m:
                continue
            show.append(('LỖI ' if cur == 'err' else 'CẢNH BÁO ') + m[2:])
    flags = spec.get('flags') or []
    print(f"{code}: {spec['w']} x {spec['h']} -> {out} | dxf_check: {n_err} lỗi, {len(show) - n_err if n_err else len(show)} cảnh báo | Flag: {len(flags)}")
    for s in show:
        print('  ' + s)
    if '--report' in argv and order:
        rep = [sys.executable, '-X', 'utf8', REPORT, 'parts', f'{order}_{code}', f'order={order}', f'code={code}', f'agent={order}_main']
        if n_err:
            rep += ['status=running', 'level=2']
        else:
            rep += ['status=built', 'level=3', f"blank={f(spec['w'])} x {f(spec['h'])}", 'finishedAt=now', 'flags=' + json.dumps(flags, ensure_ascii=False)]
        subprocess.run(rep, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return 1 if n_err else 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    sys.exit(main(sys.argv))
