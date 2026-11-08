import json, unicodedata, sys, os
"""merge_all.py - gộp các spec_<mã>.json vào Template.dxf thành <đơn>_ALL.dxf (mục 11.2-11.4 dxf-sheetmetal) và tự kiểm.
CLI: python3 -I merge_all.py <thư_mục_parts> <mã1,mã2,...theo thứ tự Excel> <out_ALL.dxf> [--template Template.dxf]
Spec tìm ở <parts>/<mã>/spec_<mã>.json hoặc <parts>/spec_<mã>.json. Flag lấy từ trường "flags" của spec.
Kiểm sau khi ghi: cặp mã nguyên, phần sau ENTITIES trùng mẫu, không 1e-/nan, ezdxf audit 0 lỗi.
"""
import os
a=sys.argv[1:]
W=a[0]; ORDER=a[1].split(','); OUT=a[2]
TPL=a[a.index('--template')+1] if '--template' in a else '/mnt/project-files/knowledge/Context_Laser/Template.dxf'
def _spec(c):
    for p in (f'{W}/{c}/spec_{c}.json', f'{W}/spec_{c}.json'):
        if os.path.exists(p): return p
    raise SystemExit('thiếu spec '+c)
def f(v):
    v=round(float(v),8)
    if abs(v)<1e-9: v=0.0
    s=('%.8f'%v).rstrip('0').rstrip('.')
    return s if s not in('','-0') else '0'
specs=[json.load(open(_spec(c))) for c in ORDER]
def esc(s):
    s=unicodedata.normalize('NFC',s)
    return ''.join(ch if ord(ch)<128 else '\\U+%04X'%ord(ch) for ch in s)
def wrap(s,n=40):
    out=[];cur=''
    for w in s.split(' '):
        if cur and len(cur)+1+len(w)>n: out.append(cur);cur=w
        else: cur=(cur+' '+w) if cur else w
    if cur: out.append(cur)
    return out
T=open(TPL,'rb').read().decode('cp932').split('\r\n')
handle=int(T[T.index('$HANDSEED')+2],16)
ents=[]
def ent(kind,head,body):
    global handle
    ents.extend(['  0',kind,'  5','%X'%handle,'330','6F','100','AcDbEntity','  8','0']+head+body); handle+=1
def col(e): return ['62',str(e['color'])] if e.get('color') else []
def emit(e,dx,dy):
    t=e['t']
    if t=='LINE':
        p,q=e['p1'],e['p2']; h=col(e)+(['  6','DASHED'] if e.get('dashed') else [])
        ent('LINE',h,['100','AcDbLine',' 10',f(p[0]+dx),' 20',f(p[1]+dy),' 30','0.0',' 11',f(q[0]+dx),' 21',f(q[1]+dy),' 31','0.0'])
    elif t=='ARC':
        ent('ARC',col(e),['100','AcDbCircle',' 10',f(e['c'][0]+dx),' 20',f(e['c'][1]+dy),' 30','0.0',' 40',f(e['r']),'100','AcDbArc',' 50',f(e['a0']),' 51',f(e['a1'])])
    elif t=='CIRCLE':
        ent('CIRCLE',col(e),['100','AcDbCircle',' 10',f(e['c'][0]+dx),' 20',f(e['c'][1]+dy),' 30','0.0',' 40',f(e['r'])])
    elif t=='POINT':
        ent('POINT',col(e),['100','AcDbPoint',' 10',f(e['p'][0]+dx),' 20',f(e['p'][1]+dy),' 30','0.0'])
    elif t=='TEXT':
        text(e['p'][0]+dx,e['p'][1]+dy,e.get('h',10),e['text'])
def text(x,y,h,s,c=None):
    ent('TEXT',['62',str(c)] if c else [],['100','AcDbText',' 10',f(x),' 20',f(y),' 30','0.0',' 40',f(h),'  1',s,'  7','Standard','100','AcDbText'])
pos=[];y=0
for sp in reversed(specs): pos.append(y); y+=sp['h']+200
pos=pos[::-1]
maxx=0;maxy=0
for sp,dy in zip(specs,pos):
    for e in sp['entities']: emit(e,0,dy)
    ty=dy+sp['h']/2
    text(-150,ty,12,sp['code'].split('-')[-1])
    k=0
    for fl in sp.get('flags',[]):
        for line in wrap(fl):
            text(-150,ty-12-7*k,5,esc(line),6); k+=1
    maxx=max(maxx,sp['w']); maxy=max(maxy,dy+sp['h'])
L=T[:]
i=L.index('ENTITIES'); j=L.index('ENDSEC',i)
L=L[:i+1]+ents+L[j-1:]
L[L.index('$HANDSEED')+2]='%X'%handle
em=L.index('$EXTMAX'); L[em+2]=f(maxx); L[em+4]=f(maxy)
va=L.index('*Active')
def setv(code,val):
    for m in range(va,va+80):
        if L[m]==code: L[m+1]=val; return
setv(' 12',f((-150+maxx)/2)); setv(' 22',f(maxy/2)); setv(' 40',f(1.1*max(maxy,(maxx+150)/2.34)))
for m in range(len(L)):
    if L[m]=='Standard' and L[m-1]=='  2' and L[m-2]=='AcDbTextStyleTableRecord':
        for q in range(m,m+20):
            if L[q]=='  3': L[q+1]='arial.ttf'; break
open(OUT,'wb').write('\r\n'.join(L).encode('cp932'))
R=open(OUT,'rb').read().decode('cp932').split('\r\n')
l=R.index('ENDSEC',R.index('ENTITIES'))
ok_tail = T[j-1:]==R[l-1:]
ok_codes = all(R[k].strip().lstrip('-').isdigit() for k in range(0,len(R)-1,2))
bad_num = [x for x in R if ('e-' in x.lower() and x.strip()[:1] in '-0123456789') or x.strip().lower() in ('nan','inf')]
try:
    import ezdxf; au=ezdxf.readfile(OUT).audit(); n_err=len(au.errors)
except Exception as ex: n_err='không đọc được: %s'%ex
print('ALL:',OUT,'| hình:',len(specs),'| EXTMAX: %.3f x %.3f'%(maxx,maxy))
print('kiểm: đuôi file trùng mẫu=%s, mã nhóm nguyên=%s, số lỗi định dạng=%d, ezdxf audit lỗi=%s'%(ok_tail,ok_codes,len(bad_num),n_err))
