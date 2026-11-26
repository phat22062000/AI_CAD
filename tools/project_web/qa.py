# -*- coding: utf-8 -*-
"""qa.py - phần tự kiểm bằng script (0 token) và thống kê chất lượng cho trang Quản lý Project.
Dùng bởi server.py. Không sửa file nào của đơn, không sửa skill.
"""
import json
import math
import os
import re
import subprocess
import sys


def _run(args, timeout=240):
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    p = subprocess.run([sys.executable, '-X', 'utf8'] + args, capture_output=True, timeout=timeout, env=env)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def _full(known, six):
    return next((c for c in known if c.endswith(six)), None)


def script_check(repo, order_dir, order, known):
    """Chạy tools\\dxf_check.py và tools\\doi_chieu_khach.py trên <đơn>_ALL.dxf.
    Trả về {'items': [{code, level, text, src: 'script', tool}], 'info': {mã: câu tóm tắt}, 'err': [..], 'ran': [tên script đã chạy]}."""
    out = {'items': [], 'info': {}, 'err': [], 'ran': []}
    all_dxf = os.path.join(order_dir, order + '_ALL.dxf')
    if not os.path.isfile(all_dxf):
        out['err'].append('Đơn chưa có file %s_ALL.dxf nên script không chạy được.' % order)
        return out
    tools = os.path.join(repo, 'tools')
    # 1. đối chiếu DXF khách
    sp = os.path.join(tools, 'doi_chieu_khach.py')
    if os.path.isfile(sp):
        try:
            rc, so, se = _run([sp, all_dxf, '--src', order_dir, '--json'])
            if rc == 2 or '{' not in so:
                out['err'].append('doi_chieu_khach.py: ' + ((so + se).strip().splitlines() or ['không có kết quả'])[-1][:300])
            else:
                d = json.loads(so[so.index('{'):])
                out['ran'].append('doi_chieu_khach')
                for m in d.get('loi_doc') or []:
                    out['err'].append(m)
                for r in d.get('ket_qua') or []:
                    code = _full(known, r.get('ma', ''))
                    if not code:
                        continue
                    if r.get('file_khach'):
                        out['info'][code] = 'Đối chiếu DXF khách %s (%s, %s): biên khớp %d%%, lỗ trùng tâm %s' % (
                            r['file_khach'], r.get('kieu', ''), r.get('phep_dat', ''), round(100 * r.get('khop_bien', 0)), r.get('lo_trung_tam', ''))
                    else:
                        out['info'][code] = 'Đối chiếu DXF khách: %s' % r.get('kieu', 'không đối chiếu được')
                    for x in r.get('khac_biet') or []:
                        if x.get('muc') == 'canhbao':
                            out['items'].append({'code': code, 'level': 'canhbao', 'text': '%s: %s' % (x['loai'], x['mo_ta']), 'src': 'script', 'tool': 'doi_chieu_khach'})
        except Exception as e:
            out['err'].append('doi_chieu_khach.py: %s' % e)
    # 2. dxf_check.py (hình dạng, quy ước, Flag)
    sp = os.path.join(tools, 'dxf_check.py')
    if os.path.isfile(sp):
        try:
            rc, so, se = _run([sp, all_dxf, '--src', order_dir])
            if '=== dxf_check' not in so and '[LỖI]' not in so:
                out['err'].append('dxf_check.py: ' + ((so + se).strip().splitlines() or ['không có kết quả'])[-1][:300])
            else:
                out['ran'].append('dxf_check')
                lv = None
                for ln in so.splitlines():
                    m = re.match(r'\[(LỖI|CẢNH BÁO|THÔNG TIN)\]', ln)
                    if m:
                        lv = {'LỖI': 'loi', 'CẢNH BÁO': 'canhbao'}.get(m.group(1))
                        continue
                    if not lv or not ln.startswith(' - '):
                        continue
                    tx = re.sub(r' \(x\d+\)$', '', ln[3:].strip())
                    m = re.match(r'(\d{6}): (.*)', tx)
                    if not m:
                        continue                 # dòng chung của cả đơn (NGUỒN...): dành cho người chạy tay
                    code = _full(known, m.group(1))
                    if code:
                        out['items'].append({'code': code, 'level': lv, 'text': m.group(2), 'src': 'script', 'tool': 'dxf_check'})
        except Exception as e:
            out['err'].append('dxf_check.py: %s' % e)
    return out


def pick_risky(items, known, cap=None):
    """Mã rủi ro để đọc mù ĐẦY ĐỦ (Phát chốt 26/11/2026): mã có LỖI hoặc CẢNH BÁO của script (dxf_check, doi_chieu_khach), tức cả mã khác DXF khách;
    nhiều điểm trước. Không giới hạn số mã (cap=None); truyền cap (vd 0.3) nếu cần giới hạn lại. Mã còn lại (script báo sạch) do add_check_job
    giao đọc lướt (skim) các hạng mục script không phủ: kích thước, vị trí lỗ, mặt ngoài, relief."""
    sc = {}
    for it in items:
        w = 10 if it.get('level') == 'loi' else 3 if it.get('tool') == 'doi_chieu_khach' else 1 if it.get('level') == 'canhbao' else 0
        if w and it.get('code') in known:
            sc[it['code']] = sc.get(it['code'], 0) + w
    out = [c for c, _ in sorted(sc.items(), key=lambda z: (-z[1], known.index(z[0])))]
    if cap:
        out = out[:max(1, int(math.ceil(cap * len(known))))]
    return out


def norm_loai(s):
    s = re.sub(r'\s*\(.*?\)\s*', ' ', str(s)).strip()
    return {'Hướng đặt khác': 'Sai hướng đặt'}.get(s, s)


def stats(reviews, loi, done_keys):
    """M2 (lỗi trên 100 mã theo loại), M3 (lỗi lặp lại sau khi đã có bài học), M4 (tỉ lệ entity khớp T trung bình)."""
    judged = {k: v for k, v in reviews.items() if v.get('status') in ('dung', 'sai')}
    sai = sorted((k for k, v in judged.items() if v.get('status') == 'sai'), key=lambda k: judged[k].get('at', ''))
    n = len(judged)
    by, order = {}, []
    for k in sai:
        for lo in dict.fromkeys(norm_loai(x) for x in (loi.get(k) or {}).get('loai') or []):
            by.setdefault(lo, []).append(k)
    lap_keys = set()
    rows = []
    for lo, keys in by.items():
        lap = 0
        for i, k in enumerate(keys):
            # lặp lại = mã bị chấm Sai SAU khi một mã cùng loại lỗi đã được rút kinh nghiệm
            if any(p in done_keys and (loi.get(p) or {}).get('at', '') and (loi.get(p) or {}).get('at', '') < judged[k].get('at', '') for p in keys[:i]):
                lap += 1
                lap_keys.add(k)
        rows.append({'loai': lo, 'n': len(keys), 'per100': round(100.0 * len(keys) / n, 1) if n else 0, 'lap': lap, 'keys': keys})
    rows.sort(key=lambda r: (-r['n'], r['loai']))
    co = [k for k in sai if (loi.get(k) or {}).get('loai')]
    kh = [float((loi.get(k) or {}).get('khop')) for k in sai if isinstance((loi.get(k) or {}).get('khop'), (int, float))]
    nguon = {}
    for k in co:
        g = (loi.get(k) or {}).get('nguon') or 'chưa ghi'
        nguon[g] = nguon.get(g, 0) + 1
    return {'n': n, 'dung': n - len(sai), 'sai': len(sai), 'm1': round(100.0 * (n - len(sai)) / n, 1) if n else None,
            'coLoai': len(co), 'chuaPhanTich': len(sai) - len(co), 'loai': rows,
            'm3': round(100.0 * len(lap_keys) / len(co), 1) if co else None, 'lap': len(lap_keys),
            'm4': round(sum(kh) / len(kh), 1) if kh else None, 'm4n': len(kh), 'nguon': nguon}


def skill_version(repo):
    try:
        with open(os.path.join(repo, 'skills', 'dxf-sheetmetal', 'SKILL.md'), 'r', encoding='utf-8') as f:
            head = f.read(1500)
        m = re.search(r'(20\d\d\.\d\d\.\d\d-\d+)', head)
        return m.group(1) if m else ''
    except OSError:
        return ''
