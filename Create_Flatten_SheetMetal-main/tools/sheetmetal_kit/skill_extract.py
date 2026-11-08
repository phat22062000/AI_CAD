"""skill_extract.py - trích các mục cần thiết của dxf-sheetmetal SKILL.md theo loại chi tiết (cho subagent, đỡ tốn token).
CLI: python3 -I skill_extract.py <SKILL.md> <loại>[,<loại>...] [out.md]
Loại: phang (tấm phẳng, kể cả hình cung/đa giác), uon (có uốn: L, U, Z, mũ...), hop (hộp, vách, khoét góc, rạch Green),
      dxf (đơn có DXF khách). Ghép nhiều loại bằng dấu phẩy, ví dụ uon,dxf. Không chắc loại nào thì dùng 'all'.
Luôn có: phần mở đầu, mục 0-3, 4.1, 7-10, 11.4, 12. Không bao giờ có 11.1-11.3 (agent chính gộp file) và mục 13 (điều phối).
"""
import re, sys
ALWAYS = ['0', '1', '2', '3', '4', '4.1', '7', '8', '9', '10', '11', '11.4', '12']
EXTRA = {'phang': [], 'uon': ['4.3', '5'], 'hop': ['4.3', '5', '6'], 'dxf': ['4.2']}
def extract(text, kinds):
    if 'all' in kinds: keep = None
    else:
        keep = set(ALWAYS)
        for k in kinds: keep |= set(EXTRA[k])
    lines = text.split('\n')
    if lines and lines[0].strip() == '---':          # bỏ frontmatter
        end = lines.index('---', 1); lines = lines[end+1:]
    out, cur = [], 'intro'
    for ln in lines:
        m = re.match(r'^(#{2,3})\s+(\d+(?:\.\d+)?)[.\s]', ln)
        if m: cur = m.group(2)
        if keep is None and cur != '13' or cur == 'intro' or (keep is not None and cur in keep):
            if keep is None or cur not in ('11.1', '11.2', '11.3', '13'):
                out.append(ln)
    return '\n'.join(out)
if __name__ == '__main__':
    src, kinds = sys.argv[1], sys.argv[2].split(',')
    t = extract(open(src, encoding='utf-8').read(), kinds)
    if len(sys.argv) > 3: open(sys.argv[3], 'w', encoding='utf-8').write(t)
    else: print(t)
