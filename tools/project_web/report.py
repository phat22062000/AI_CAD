# -*- coding: utf-8 -*-
"""Agent ghi tiến độ cho trang Quản lý Project.

Cách dùng:
  py report.py <orders|agents|parts|jobs> <id> key=value [key=value ...]
  py report.py jobs          (liệt kê việc giao trên trang còn chờ)
  py report.py review <số đơn>_<mã> status=sai note="..."   (chỉ khi người dùng góp ý trong app)
  py report.py loi <số đơn>_<mã> "lỗi 1" "lỗi 2" [loai="Sai kích thước lỗ"] [nguyen_nhan="..."] [update="..."] [nguon="T/F|script|đọc mù|Phát"] [khop=87.5]   (lỗi cụ thể của mã Sai sau khi so file T/F, hiện trong popup mã; loai= là loại lỗi, có thể lặp)
  py report.py check <số đơn> "<mã>|loi|<tên lỗi>: <chi tiết>" "<mã>|canhbao|<tên cảnh báo>: <chi tiết>"   (kết quả nút Tự check; không có mục nào = không phát hiện lỗi; ghi đè phần agent báo, giữ phần script)
  py report.py updscript <job id> <file.json>   (nhật ký các thay đổi script khi bấm nút Update Script)
  py report.py updskill <job id> <file.json>   (nhật ký các dòng đã đổi khi bấm nút Update Skill)
  py report.py hoiquy <job id> "<đơn>_<mã>|khop|<% khớp>|" "<đơn>_<mã>|khac|<% khớp>|<tóm tắt>"   (kết quả chạy hồi quy sau update skill)

Giá trị được đọc như JSON nếu được (số, true/false, null, ["a","b"]), nếu không thì là chuỗi.
Giá trị "now" = thời gian hiện tại (ISO UTC). "done+=<mã>" thêm một mã vào danh sách done.

Ví dụ:
  py report.py agents 521105-04_S1 order=521105-04 kind=sub name="Subagent 1" codes='["26-065930","26-065931"]' done='[]' current=26-065930 state=running startedAt=now
  py report.py parts 521105-04_26-065930 order=521105-04 code=26-065930 kind=uon agent=521105-04_S1 status=running startedAt=now flags='[]'
  py report.py parts 521105-04_26-065930 status=built blank="232.5 x 50" finishedAt=now
  py report.py agents 521105-04_S1 done+=26-065930 current=26-065931
  py report.py agents 521105-04_S1 state=done current=null finishedAt=now
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT', '8780'))


def parse(v):
    if v == 'now':
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        return json.loads(v)
    except ValueError:
        return v


def main(argv):
    if len(argv) == 2 and argv[1] == 'jobs':
        # liệt kê việc người dùng giao trên trang còn chờ (status "moi") hoặc đang nhận ("nhan")
        import server
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
        jobs = server.load_json(server.PROGRESS, {}).get('jobs', {})
        todo = {k: v for k, v in jobs.items() if v.get('status') in ('moi', 'nhan')}
        print(json.dumps(todo, ensure_ascii=False, indent=1))
        return 0
    if len(argv) < 3:
        print(__doc__)
        return 2
    if argv[1] == 'loi':
        # Lỗi cụ thể của mã bị chấm Sai, rút ra sau khi so 2 file DXF T (đúng) và F (sai): hiện trong popup chi tiết mã (mục Đánh Giá AI)
        # py report.py loi <số đơn>_<mã> "lỗi 1" "lỗi 2" ...   (ghi đè toàn bộ danh sách lỗi của mã)
        import server
        with server.lock:
            d = server.load_json(server.LOI_SAI, {})
            rest = [a for a in argv[3:] if a.strip()]
            loai = [a[5:].strip() for a in rest if a.startswith('loai=') and a[5:].strip()]
            opt = {k: next((a[len(k) + 1:].strip() for a in rest if a.startswith(k + '=')), '') for k in ('nguyen_nhan', 'update', 'nguon', 'khop')}
            item = {'loi': [a for a in rest if not a.startswith(('loai=', 'nguyen_nhan=', 'update=', 'nguon=', 'khop='))], 'loai': loai, 'at': server.now_iso()}
            if opt['nguyen_nhan']:
                item['nguyen_nhan'] = opt['nguyen_nhan']      # nguyên nhân gốc (ghi rõ "suy đoán" nếu không có bằng chứng)
            if opt['update']:
                item['update'] = opt['update']                # nội dung update cần đổi để không tái phạm (1 câu ngắn: đích + sửa gì)
            item['nguon'] = opt['nguon'] or 'T/F'             # nguồn phát hiện: T/F | script | đọc mù | Phát
            try:
                item['khop'] = float(opt['khop'].rstrip('%'))  # tỉ lệ entity khớp T (diff_tf.py, trường ty_le_khop)
            except ValueError:
                pass
            d[argv[2]] = item
            server.save_json(server.LOI_SAI, d)
        print('OK loi', argv[2], len(d[argv[2]]['loi']), 'dòng,', len(loai), 'loại')
        return 0
    if argv[1] == 'check':
        # Kết quả nút "Tự check" của một đơn: mỗi mục "<mã>|loi|nội dung" (LỖI) hoặc "<mã>|canhbao|nội dung" (CẢNH BÁO); không mục nào = không phát hiện lỗi
        import server
        items = []
        for a in argv[3:]:
            code, _, rest = a.partition('|')
            lv, _, text = rest.partition('|')
            if code.strip() and text.strip() and lv.strip() in ('loi', 'canhbao'):
                items.append({'code': code.strip(), 'level': lv.strip(), 'text': text.strip(), 'src': 'ai'})
        with server.lock:
            d = server.load_json(server.CHECKS, {})
            cur = d.get(argv[2]) or {}
            keep = [it for it in cur.get('items', []) if it.get('src', 'ai') == 'script']      # giữ kết quả script, chỉ thay phần agent báo
            d[argv[2]] = dict(cur, items=keep + items, at=server.now_iso())
            server.save_json(server.CHECKS, d)
        print('OK check', argv[2], len(items), 'mục')
        return 0
    if argv[1] == 'updscript':
        # Nhật ký một lần Update Script: py report.py updscript <job id> <file.json>
        # file.json: {"changes": [{"proposal", "file", "lines", "old", "new", "test"}], "skipped": [{"proposal", "why"}]}
        import server
        with open(argv[3], 'r', encoding='utf-8-sig') as f:
            rec = json.load(f)
        with server.lock:
            job = server.load_json(server.PROGRESS, {}).get('jobs', {}).get(argv[2]) or {}
            log = [r for r in server.load_json(server.SCRIPT_LOG, []) if r.get('id') != argv[2]]
            archived = server.archive_applied([it.get('name') for it in job.get('items') or []])
            log.append({'id': argv[2], 'archived': archived, 'at': server.now_iso(), 'backup': job.get('backup', ''),
                        'changes': [{k: str(c.get(k, ''))[:1500] for k in ('proposal', 'file', 'lines', 'old', 'new', 'test')} for c in rec.get('changes') or []],
                        'skipped': [{k: str(c.get(k, ''))[:500] for k in ('proposal', 'why')} for c in rec.get('skipped') or []]})
            server.save_json(server.SCRIPT_LOG, log[-20:])
        print('OK updscript', argv[2], len(rec.get('changes') or []), 'thay đổi,', len(rec.get('skipped') or []), 'bỏ qua,', len(archived), 'đề xuất đã chuyển khỏi danh sách')
        return 0
    if argv[1] == 'updskill':
        # Nhật ký một lần Update Skill: py report.py updskill <job id> <file.json>
        # file.json: {"version_before", "version_after", "changes": [{"proposal", "file", "lines", "old", "new"}], "skipped": [{"proposal", "why"}]}
        import server
        with open(argv[3], 'r', encoding='utf-8-sig') as f:
            rec = json.load(f)
        with server.lock:
            job = server.load_json(server.PROGRESS, {}).get('jobs', {}).get(argv[2]) or {}
            log = [r for r in server.load_json(server.SKILL_LOG, []) if r.get('id') != argv[2]]
            archived = server.archive_applied([it.get('name') for it in job.get('items') or []])
            log.append({'id': argv[2], 'archived': archived, 'at': server.now_iso(), 'before': str(rec.get('version_before', '')), 'after': str(rec.get('version_after', '')),
                        'backup': job.get('backup', ''), 'changes': [{k: str(c.get(k, ''))[:1500] for k in ('proposal', 'file', 'lines', 'old', 'new')} for c in rec.get('changes') or []],
                        'skipped': [{k: str(c.get(k, ''))[:500] for k in ('proposal', 'why')} for c in rec.get('skipped') or []]})
            server.save_json(server.SKILL_LOG, log[-20:])
        print('OK updskill', argv[2], len(rec.get('changes') or []), 'thay đổi,', len(rec.get('skipped') or []), 'bỏ qua,', len(archived), 'đề xuất đã chuyển khỏi danh sách')
        return 0
    if argv[1] == 'hoiquy':
        # Kết quả một lần chạy hồi quy: py report.py hoiquy <job id> "<đơn>_<mã>|khop|<% khớp>|" "<đơn>_<mã>|khac|<% khớp>|<tóm tắt khác biệt>" "<đơn>_<mã>|loi|0|<lý do>"
        import server
        with server.lock:
            job = server.load_json(server.PROGRESS, {}).get('jobs', {}).get(argv[2]) or {}
            meta = {it['key']: it for it in job.get('items') or []}
            items = []
            for a in argv[3:]:
                f = a.split('|', 3)
                if len(f) >= 2 and f[0].strip() and f[1].strip() in ('khop', 'khac', 'loi'):
                    try:
                        pc = float(f[2].strip().rstrip('%')) if len(f) > 2 and f[2].strip() else None
                    except ValueError:
                        pc = None
                    m = meta.get(f[0].strip()) or {}
                    items.append({'key': f[0].strip(), 'kq': f[1].strip(), 'khop': pc, 'text': f[3].strip() if len(f) > 3 else '', 'kieu': m.get('kieu', ''), 'loai': m.get('loai', [])})
            runs = [r for r in server.load_json(server.HOIQUY, []) if r.get('id') != argv[2]]
            runs.append({'id': argv[2], 'at': server.now_iso(), 'skill': job.get('skill', ''), 'loai': job.get('loai', ''), 'items': items})
            server.save_json(server.HOIQUY, runs[-20:])
        print('OK hoiquy', argv[2], len(items), 'mã')
        return 0
    if argv[1] == 'review':
        # Chỉ dùng khi NGƯỜI DÙNG góp ý trong app: ghi kết quả chấm lên trang (mục Đánh Giá AI)
        # py report.py review <số đơn>_<mã> status=sai|dung|cho note="..."
        f = {k: v for k, _, v in (a.partition('=') for a in argv[3:])}
        item = {'key': argv[2], 'status': f.get('status', 'sai'), 'note': f.get('note', '')}
        body = json.dumps({'items': [item], 'by': f.get('by', 'app')}, ensure_ascii=False).encode('utf-8')
        try:
            req = urllib.request.Request(f'http://127.0.0.1:{PORT}/api/review', data=body,
                                         headers={'Content-Type': 'application/json; charset=utf-8'})
            with urllib.request.urlopen(req, timeout=5) as r:
                r.read()
            print('OK review', argv[2])
        except Exception:
            import server            # server chưa chạy: ghi thẳng vào data/reviews.json
            with server.lock:
                rv = server.load_json(server.REVIEWS, {})
                old = rv.get(argv[2], {})
                rv[argv[2]] = {'status': item['status'], 'note': item['note'] or old.get('note', ''),
                               'at': server.now_iso(), 'by': f.get('by', 'app')}
                server.save_json(server.REVIEWS, rv)
            print('OK (ghi file) review', argv[2])
        return 0
    coll, doc_id = argv[1], argv[2]
    fields = {}
    for a in argv[3:]:
        k, _, v = a.partition('=')
        fields[k] = parse(v)
    body = json.dumps({'collection': coll, 'id': doc_id, 'fields': fields}).encode('utf-8')
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{PORT}/api/progress', data=body,
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as r:
            r.read()
        print('OK', coll, doc_id)
        return 0
    except Exception:
        import server            # server chưa chạy: ghi thẳng vào data/progress.json
        server.merge_progress(coll, doc_id, fields)
        print('OK (ghi file)', coll, doc_id)
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
