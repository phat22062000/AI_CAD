"""pdfpage.py - render trang PDF scan, xoay thẳng, cắt vùng, đo px/mm (dùng chung cho dựng phôi và đọc mù).
CLI:
  python3 -I pdfpage.py split <đơn.pdf> <thư_mục_ra> <mã1,mã2,...> [--first 2]   # tách mỗi trang bản vẽ thành <mã>/<mã>.pdf
  python3 -I pdfpage.py render <file.pdf> <out.png> [--page 1] [--dpi 200] [--rot 0|90|180|270] [--deskew]
  python3 -I pdfpage.py crop <in.png> <out.png> x0 y0 x1 y1 [--zoom 2]   # toạ độ pixel; zoom phóng ảnh cắt
  python3 -I pdfpage.py small <in.png> <out.png> [--max 1200]            # thu nhỏ trước khi mở ảnh để đỡ tốn token
Python: from pdfpage import render, deskew_angle, rotate, crop, pxmm
Lưu ý tiết kiệm token: chỉ MỞ (Read) ảnh đã cắt hoặc đã thu nhỏ (cạnh dài <= 1200 px); không mở cả trang 200 dpi.
"""
import sys, math
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
def render(pdf, out, page=1, dpi=200, rot=0, deskew=False):
    import pymupdf
    doc = pymupdf.open(pdf); pg = doc[page-1]
    pix = pg.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    im = Image.frombytes('L', (pix.width, pix.height), pix.samples)
    if rot: im = im.rotate(rot, expand=True, fillcolor=255)
    ang = 0.0
    if deskew:
        ang = deskew_angle(im)
        if abs(ang) > 0.05: im = im.rotate(ang, expand=False, fillcolor=255, resample=Image.BICUBIC)
    im.save(out)
    return out, ang
def deskew_angle(im, span=2.0, step=0.05):
    """Góc (độ, ngược chiều kim đồng hồ) cần xoay để các nét ngang (khung tên, khung bản vẽ) nằm ngang."""
    if isinstance(im, str): im = Image.open(im).convert('L')
    sm = im.copy(); sm.thumbnail((1400, 1400))
    best = (0, -1)
    for i in range(int(-span/step), int(span/step)+1):
        a = i*step
        r = np.asarray(sm.rotate(a, fillcolor=255, resample=Image.BILINEAR)) < 128
        s = r.sum(axis=1).astype(float); v = (s**2).sum()
        if v > best[1]: best = (a, v)
    return best[0]
def rotate(inp, out, ang):
    Image.open(inp).rotate(ang, expand=False, fillcolor=255, resample=Image.BICUBIC).save(out); return out
def crop(inp, out, box, zoom=1.0):
    im = Image.open(inp).crop(tuple(int(v) for v in box))
    if zoom != 1: im = im.resize((int(im.width*zoom), int(im.height*zoom)), Image.LANCZOS)
    im.save(out); return out
def small(inp, out, mx=1200):
    im = Image.open(inp); im.thumbnail((mx, mx)); im.save(out); return out
def pxmm(p1, p2, mm):
    """Tỉ lệ px/mm từ 2 điểm pixel của một kích thước chắc chắn."""
    return math.dist(p1, p2) / mm
def split(pdf, outdir, codes, first=2):
    import pymupdf, os
    src = pymupdf.open(pdf)
    for i, c in enumerate(codes):
        os.makedirs(f'{outdir}/{c}', exist_ok=True)
        d = pymupdf.open(); d.insert_pdf(src, from_page=first-1+i, to_page=first-1+i); d.save(f'{outdir}/{c}/{c}.pdf')
if __name__ == '__main__':
    a = sys.argv[1:]
    def opt(name, default):
        return type(default)(a[a.index(name)+1]) if name in a else default
    if a[0] == 'split': split(a[1], a[2], a[3].split(','), opt('--first', 2))
    elif a[0] == 'render': print(render(a[1], a[2], opt('--page', 1), opt('--dpi', 200), opt('--rot', 0), '--deskew' in a))
    elif a[0] == 'crop': print(crop(a[1], a[2], [float(v) for v in a[3:7]], opt('--zoom', 1.0)))
    elif a[0] == 'small': print(small(a[1], a[2], opt('--max', 1200)))
