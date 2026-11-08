# -*- coding: utf-8 -*-
"""Agent ghi tiến độ cho trang Quản lý Project.

Cách dùng:
  py report.py <orders|agents|parts|jobs> <id> key=value [key=value ...]
  py report.py jobs          (liệt kê việc giao trên trang còn chờ)
  py report.py review <số đơn>_<mã> status=sai note="..."   (chỉ khi người dùng góp ý trong app)

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
