"""Helper dùng chung: render spec hình phôi (JSON) và overlay lên ảnh PDF.
Spec JSON: {"code":"26-065xxx","entities":[...],"flags":[...],"w":..,"h":..}
Entity (toạ độ mm, gốc (0,0) = góc dưới trái bbox phôi, y hướng lên):
 {"t":"LINE","p1":[x,y],"p2":[x,y],"dashed":false,"color":null|1|3|6}
 {"t":"ARC","c":[x,y],"r":R,"a0":deg,"a1":deg}      # ngược chiều kim đồng hồ a0->a1
 {"t":"CIRCLE","c":[x,y],"r":R}
 {"t":"POINT","p":[x,y],"color":null|3}
 {"t":"TEXT","p":[x,y],"text":"J","h":10}
Màu: null=trắng/đen (biên, lỗ), 1=đỏ kegaki, 3=xanh lá (rạch/POINT xuyên), dashed=đường uốn
"""
import json, math
from PIL import Image, ImageDraw
def _pt(a,s,ox,oy): return (ox+s*a[0], oy-s*a[1])
def draw_spec(img, spec, s, ox, oy, width=2, alpha=255):
    """Vẽ spec lên ảnh PIL RGBA `img` (in place). px = ox + s*x ; py = oy - s*y (s: px/mm)."""
    d = ImageDraw.Draw(img, 'RGBA')
    col = {None:(0,0,0,alpha), 1:(255,0,0,alpha), 3:(0,160,0,alpha), 6:(200,0,200,alpha)}
    for e in spec['entities']:
        c = col.get(e.get('color'), (0,0,0,alpha))
        t = e['t']
        if t=='LINE':
            p1=_pt(e['p1'],s,ox,oy); p2=_pt(e['p2'],s,ox,oy)
            if e.get('dashed'):
                c=(0,170,0,alpha) if e.get('color') is None else c
                L=math.dist(p1,p2); n=max(1,int(L/8))
                for i in range(n):
                    if i%2==0:
                        a=(p1[0]+(p2[0]-p1[0])*i/n, p1[1]+(p2[1]-p1[1])*i/n)
                        b=(p1[0]+(p2[0]-p1[0])*(i+1)/n, p1[1]+(p2[1]-p1[1])*(i+1)/n)
                        d.line([a,b],fill=c,width=width)
            else: d.line([p1,p2],fill=(220,0,0,alpha) if e.get('color') is None else c,width=width)
        elif t=='ARC':
            a0,a1=e['a0'],e['a1']
            if a1<=a0: a1+=360
            n=max(8,int((a1-a0)/3)); pts=[]
            for i in range(n+1):
                a=math.radians(a0+(a1-a0)*i/n)
                pts.append(_pt((e['c'][0]+e['r']*math.cos(a), e['c'][1]+e['r']*math.sin(a)),s,ox,oy))
            d.line(pts,fill=(220,0,0,alpha) if e.get('color') is None else col[e['color']],width=width)
        elif t=='CIRCLE':
            cx,cy=_pt(e['c'],s,ox,oy); r=e['r']*s
            d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=(220,0,0,alpha),width=width)
        elif t=='POINT':
            cx,cy=_pt(e['p'],s,ox,oy); r=4
            d.line([(cx-r,cy),(cx+r,cy)],fill=(220,0,0,alpha),width=width); d.line([(cx,cy-r),(cx,cy+r)],fill=(220,0,0,alpha),width=width)
        elif t=='TEXT':
            d.text(_pt(e['p'],s,ox,oy),e['text'],fill=(0,0,200,alpha))
    return img
def overlay(bg_png, spec, s, ox, oy, out_png, bg_alpha=0.5, crop=None, label=None):
    """Chồng spec (nét màu) lên ảnh nền PDF mờ. crop=(l,t,r,b) theo pixel nền."""
    bg = Image.open(bg_png).convert('RGB')
    if crop: bg = bg.crop(crop); ox-=crop[0]; oy-=crop[1]
    white = Image.new('RGB', bg.size, (255,255,255))
    base = Image.blend(white, bg, bg_alpha).convert('RGBA')
    draw_spec(base, spec, s, ox, oy)
    if label: ImageDraw.Draw(base).text((8,8),label,fill=(0,0,0,255))
    base.convert('RGB').save(out_png)
def fit_two_points(mm1, px1, mm2, px2):
    """Tính (s, ox, oy) từ 2 điểm: toạ độ mm trên phôi và pixel tương ứng trên ảnh PDF (y ảnh hướng xuống).
    Dùng 2 điểm xa nhau (ví dụ 2 góc của kích thước tổng). Trả s (px/mm), ox, oy cho overlay()."""
    import math
    s = math.dist(px1, px2) / math.dist(mm1, mm2)
    ox = px1[0] - s*mm1[0]; oy = px1[1] + s*mm1[1]
    return s, ox, oy
def overlay_small(bg_png, spec, s, ox, oy, out_png, margin_mm=8, max_px=1200, bg_alpha=0.5, label=None):
    """Overlay chỉ cắt quanh phôi (+ lề) và thu nhỏ cạnh dài <= max_px để mở ảnh tốn ít token."""
    w, h = spec['w'], spec['h']
    l = ox - margin_mm*s; t = oy - (h+margin_mm)*s; r = ox + (w+margin_mm)*s; b = oy + margin_mm*s
    overlay(bg_png, spec, s, ox, oy, out_png, bg_alpha, crop=(int(l), int(t), int(r), int(b)), label=label)
    im = Image.open(out_png); im.thumbnail((max_px, max_px)); im.save(out_png)
def render_only(spec, out_png, s=6, pad=30):
    w,h = spec['w'], spec['h']
    img = Image.new('RGBA',(int(w*s+2*pad),int(h*s+2*pad)),(255,255,255,255))
    draw_spec(img, spec, s, pad, h*s+pad)
    img.convert('RGB').save(out_png)
