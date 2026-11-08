# -*- coding: utf-8 -*-
"""prep.py - bước chuẩn bị dữ liệu CHẠY TRƯỚC khi bật agent (Python thuần, không tốn token).

Ghi vào thư mục tạm của đơn (%TEMP%\\ai_cad_<đơn>\\):
  README_don.md        tóm tắt đơn + đường dẫn mọi thứ đã chuẩn bị (agent đọc cái này TRƯỚC)
  order_context.json   thông tin chung cả đơn theo mẫu của sheetmetal_kit
  skill_phang.md / skill_uon.md / skill_hop.md / skill_dxf.md   SKILL.md đã trích theo loại chi tiết (skill_extract.py)
  (lệnh `prep.py khach <mã>` in riêng quy tắc của một khách)
  pages/p<n>_small.png ảnh tổng quan mỗi trang (cạnh dài <= 1200 px) - ĐƯỢC mở
  pages/p<n>_200.png   trang 200 dpi - CHỈ để cắt vùng, không mở cả ảnh
Không sửa SKILL.md và không đụng thư mục skill gốc: chỉ đọc.
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
REPO = os.path.join(ROOT, 'Create_Flatten_SheetMetal-main')
KIT = os.path.join(REPO, 'tools', 'sheetmetal_kit')
KINDS = ('phang', 'uon', 'hop', 'dxf')
GROUP_HDR = re.compile(r'^\s*-\s+\*\*')


def _skill_extracts(out):
    sys.path.insert(0, KIT)
    import skill_extract
    text = open(os.path.join(REPO, 'skills', 'dxf-sheetmetal', 'SKILL.md'), encoding='utf-8').read()
    sizes = {}
    for k in KINDS:
        body = skill_extract.extract(text, [k])
        with open(os.path.join(out, f'skill_{k}.md'), 'w', encoding='utf-8', newline='') as f:
            f.write(body)
        sizes[k] = len(body.encode('utf-8'))
    return sizes


def rules_for(cust):
    """Quy tắc riêng của một khách (mã 3 số đọc từ khung tên PDF): các dòng nhóm có nhắc mã + dòng riêng của khách."""
    src = os.path.join(REPO, 'rules', 'Quy_Tac_Theo_Ma_Khach_AnDanh.md')
    lines = open(src, encoding='utf-8').read().split('\n')
    code = re.sub(r'\D', '', str(cust or ''))[:3]
    keep, found = [], False
    for ln in lines:
        if ln.startswith('#') or ln.startswith('Bản gốc') or ln.startswith('| Mã') or ln.startswith('|---'):
            keep.append(ln)
        elif not code:
            keep.append(ln)
        elif GROUP_HDR.match(ln) and re.search(r'(?<!\d)%s(?!\d)' % code, ln):
            keep.append(ln)
            found = True
        elif ln.startswith('| ' + code + ' |'):
            keep.append(ln)
            found = True
    note = '' if not code else ('\n' + (f'Khách {code}: các dòng trên là toàn bộ quy tắc riêng.' if found else f'Khách {code} không có quy tắc riêng: áp quy tắc chung (Laser R theo bảng).'))
    return '\n'.join(keep) + note + '\n'


def _pages(pdf, out):
    """Ảnh tổng quan + ảnh 200 dpi từng trang. Trả (số trang, có lớp chữ, danh sách file)."""
    sys.path.insert(0, KIT)
    import pdfpage
    import pymupdf
    os.makedirs(os.path.join(out, 'pages'), exist_ok=True)
    doc = pymupdf.open(pdf)
    n, has_text, files = len(doc), False, []
    for i in range(n):
        if len(doc[i].get_text().strip()) > 40:
            has_text = True
        big = os.path.join(out, 'pages', f'p{i + 1}_200.png')
        small = os.path.join(out, 'pages', f'p{i + 1}_small.png')
        pdfpage.render(pdf, big, page=i + 1, dpi=200, deskew=True)
        pdfpage.small(big, small, 1200) if hasattr(pdfpage, 'small') else None
        files.append((i + 1, small if os.path.exists(small) else big))
    return n, has_text, files


def prepare(order, workdir, out):
    """Chuẩn bị mọi thứ cho đơn; trả về dict tóm tắt (cũng ghi README_don.md). Lỗi từng phần không làm hỏng cả bước."""
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, HERE)
    import server as S
    info = {'order': order, 'errors': []}
    files = os.listdir(workdir)
    req = []
    xl = next((f for f in files if f.lower().endswith('.xlsx') and '依頼' in f), None)
    if xl:
        req = S.read_request(os.path.join(workdir, xl))
    meta = req[0] if req else {}
    info['codes'] = [r['code'] for r in req]
    # skill theo loại
    try:
        info['skill_kb'] = {k: round(v / 1024, 1) for k, v in _skill_extracts(out).items()}
    except Exception as e:
        info['errors'].append('skill_extract: ' + str(e))
    # PDF
    pdfs = [f for f in files if f.lower().endswith('.pdf')]
    pages, has_text, pfiles = 0, False, []
    if pdfs:
        try:
            pages, has_text, pfiles = _pages(os.path.join(workdir, pdfs[0]), out)
        except Exception as e:
            info['errors'].append('pdf: ' + str(e))
    info.update(pages=pages, pdf_has_text=has_text)
    # DXF/DWG của khách trong thư mục đơn (không phải Output của agent)
    cust_files = [f for f in files if f.lower().endswith(('.dxf', '.dwg')) and not re.match(r'^(26-\d{6}|%s_ALL)\.dxf$' % re.escape(order), f, re.I)]
    info['customer_cad'] = cust_files
    # order_context.json theo mẫu của kit
    ctx = {'order': order, 'customer': str(meta.get('customer', '')), 'material_group': meta.get('material', ''),
           'J_rule': 'Chữ J viết tay cạnh mã vạch = gia công nội bộ -> giãn theo bảng; không J -> giãn tay viết',
           'stretch_tables': [os.path.join(REPO, 'rules', 'bang-do-gian', f) for f in sorted(os.listdir(os.path.join(REPO, 'rules', 'bang-do-gian')))] if os.path.isdir(os.path.join(REPO, 'rules', 'bang-do-gian')) else [],
           'parts': [{'code': r['code'], 't': r.get('thick'), 'xy_request': f"{r.get('x')} x {r.get('y')} (chỉ đối chiếu)", 'material': r.get('material', '')} for r in req],
           'order_of_excel': [r['code'] for r in req], 'customer_cad_files': cust_files, 'pdf_pages': pages,
           'pdf_layout': ('1 trang = 1 mã' if pages and pages == len(req) else f'bản vẽ cụm: {pages} trang cho {len(req)} mã')}
    with open(os.path.join(out, 'order_context.json'), 'w', encoding='utf-8') as f:
        json.dump(ctx, f, ensure_ascii=False, indent=1)
    info['layout'] = ctx['pdf_layout']
    # README_don.md
    kb = info.get('skill_kb', {})
    lines = [f'# Đơn {order} - đã chuẩn bị sẵn (đọc file này trước, KHÔNG làm lại những việc dưới đây)', '',
             f"- Khách: {ctx['customer'] or '(không rõ)'} | Vật liệu: {ctx['material_group'] or '(không rõ)'} | Số mã: {len(req)} | Bản vẽ: {ctx['pdf_layout']}"
             + (' | PDF scan (không có lớp chữ, phải đọc ảnh)' if pages and not has_text else ''),
             f"- Thư mục đơn (chỉ ghi file DXF Output vào đây): {workdir}", f'- Thư mục tạm của bạn (ghi file tạm ở đây): {out}', '',
             '## Mã theo thứ tự Excel (mã | dày | X x Y chỉ để đối chiếu)']
    for r in req:
        lines.append(f"- {r['code']} | {r.get('thick')}t | {r.get('x')} x {r.get('y')}")
    lines += ['', '## Đã chuẩn bị sẵn',
              '- Skill đã trích theo loại (đọc MỘT file đúng loại thay cho SKILL.md đầy đủ; chi tiết khác loại thì đọc thêm file loại đó): '
              + ', '.join(f'skill_{k}.md ({kb[k]} KB)' for k in kb) + '. Không chắc loại nào thì chạy: py -X utf8 skill_extract.py <SKILL.md> all',
              f'- Quy tắc riêng của khách: mã khách 3 số đọc ở khung tên PDF, rồi chạy `py -X utf8 "{os.path.join(HERE, "prep.py")}" khach <mã khách>` (in vài dòng, thay cho đọc cả Quy_Tac_Theo_Ma_Khach_AnDanh.md 10 KB)',
              '- Thông tin chung cả đơn: order_context.json (gồm đường dẫn 2 bảng độ giãn)']
    if pfiles:
        lines.append('- Ảnh trang PDF: ' + '; '.join(f'trang {n}: pages/p{n}_small.png (MỞ để xem tổng quan) và pages/p{n}_200.png (chỉ CẮT vùng bằng pdfpage.py crop rồi mở ảnh đã cắt, không mở nguyên ảnh)' for n, _ in pfiles))
    if cust_files:
        lines.append('- Có file CAD của khách trong thư mục đơn (dùng làm nền theo mục 4.2 skill): ' + ', '.join(cust_files))
    lines += ['', '## Công cụ và đường dẫn',
              f'- Template.dxf: {os.path.join(REPO, "templates", "Template.dxf")}',
              f'- Bộ công cụ kit: {KIT} (pdfpage.py crop/small, geom.py, specrender.py, merge_all.py, skill_extract.py)',
              f'- Kiểm DXF: py -X utf8 "{os.path.join(REPO, "tools", "dxf_check.py")}" <file.dxf> --tpl "{os.path.join(REPO, "templates", "Template.dxf")}"']
    with open(os.path.join(out, 'README_don.md'), 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines) + '\n')
    info['seconds'] = round(time.time() - t0, 1)
    return info


if __name__ == '__main__':
    import tempfile
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    if sys.argv[1] == 'khach':
        print(rules_for(sys.argv[2] if len(sys.argv) > 2 else ''))
        sys.exit(0)
    o = sys.argv[1]
    wd = sys.argv[2]
    print(json.dumps(prepare(o, wd, os.path.join(tempfile.gettempdir(), 'ai_cad_' + o + '_prep_test')), ensure_ascii=False, indent=1))
