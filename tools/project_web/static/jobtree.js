/* Job tree of a running RUN (design approved in docs/superpowers/specs/2026-11-01-job-tree-demo.html):
   one branch per real worker (robot head + its codes, in the order it took them), or one SOLO robot over every code.
   Built once per layout, then only changed nodes are touched each poll (text, classes, lamps, robot face, lit wire);
   base wires are redrawn only when the layout changes. Moods come only from real stream events (runner.mood_of). */
'use strict';

const JT_STAGES = ['L0', 'L1', 'L2', 'L3'];
const JT_QA_STAGES = ['Đọc', 'Census', 'So', 'Ghi'];   // QA lamps on the same L0..L3: read, census, compare, its line written
const JT_FINAL = ['PASS', 'PREVIEW', 'FAIL', 'NOFILE', 'MANUAL'];
const JT_MOODS = {
  think: ['Đang suy nghĩ', 'AI trả token suy nghĩ'], look: ['Quan sát', 'Đọc ảnh / cắt ảnh bản vẽ'],
  work: ['Làm việc', 'Chạy tool'], write: ['Đang viết', 'Ghi census / spec'],
  confused: ['UNKNOWN', 'Tool trả lỗi'], question: ['Có câu hỏi', 'Mã có FLAG / câu hỏi'],
  ok: ['Xong · PASS', 'Mọi mã PASS'], review: ['Xong · cần xem', 'Có mã PREVIEW'], fail: ['Lỗi', 'Có mã FAIL / không có file'],
  sleep: ['Chờ', 'Chờ suất / chưa nhận mã / đứng im > 3 phút'],
};
const JT_PRI = ['confused', 'fail', 'question', 'sleep', 'work', 'write', 'look', 'think', 'review', 'ok'];
const JT_IDLE_S = 180;

const jtPhase = (ms) => `animation-delay:-${(performance.now() % ms / 1000).toFixed(3)}s`;   // same phase whenever drawn
let jtRbN = 0;
function robot(m, size = 40) {
  const ph = jtPhase, big = size >= 40, L = 18.5, R = 29.5, Y = 22.75, id = `rbc${++jtRbN}`;
  const dots = (r = 3.1, y = Y) => `<circle class="ff" cx="${L}" cy="${y}" r="${r}"/><circle class="ff" cx="${R}" cy="${y}" r="${r}"/>`;
  const glyph = (t) => [L, R].map((x) => `<text x="${x}" y="${Y}" text-anchor="middle" dominant-baseline="central" style="${ph(1100)}">${t}</text>`).join('');
  const wave = [L, R].map((x, i) => `<clipPath id="${id}${i}"><rect x="${x - 3.6}" y="${Y - 3.5}" width="7.2" height="7"/></clipPath>
    <g clip-path="url(#${id}${i})"><path class="f wave" style="${ph(800)}" d="M${x - 4.5} ${Y}q1.5 -2.4 3 0t3 0t3 0t3 0t3 0"/></g>`).join('');
  const eyes = {
    think: dots(3, Y - 1),
    look: `<g class="gaze" style="${ph(7000)}"><g class="lid" style="${ph(4300)}">${dots(3.4)}</g></g>`,
    work: wave,
    write: `<g class="lid" style="${ph(4300)}">${dots(2.8, Y + 1.6)}</g>`,
    // UNKNOWN: gear eyes spin, jam and shake, the screen cracks and shatters, then it starts again
    confused: [L, R].map((x, i) => `<g class="jam" style="${i ? 'animation-direction:reverse;' : ''}${ph(2400)}"><circle class="fx" cx="${x}" cy="${Y}" r="2.5" stroke-width="1.6"/>
        <path class="fx" stroke-width="1.7" d="${Array.from({length: 8}, (_, k) => { const a = k * Math.PI / 4, c = Math.cos(a), s = Math.sin(a); return `M${(x + 2.5 * c).toFixed(2)} ${(Y + 2.5 * s).toFixed(2)}L${(x + 4.1 * c).toFixed(2)} ${(Y + 4.1 * s).toFixed(2)}`; }).join('')}"/>
        <circle class="ff" cx="${x}" cy="${Y}" r=".9"/></g>`).join('')
      + `<path class="crack" style="${ph(2400)}" d="M22.6 14.2l1.7 3.4-2.4 2.8 3 2.9-2 3.2 2.3 3.4"/><path class="crack" style="${ph(2400)}" d="M33.6 31.3l-1.2-2.8 1.8-2 -1.9-2.2"/>`
      + [[21.5, 25, -2.5, 9, -60], [24.5, 22.5, 2.5, 10, 70], [26.5, 27.5, -1, 8, 35], [32.5, 26, 2, 9, -45]]
        .map(([x, y, dx, dy, r]) => `<path class="shard" style="--dx:${dx}px;--dy:${dy}px;--r:${r}deg;${ph(2400)}" d="M${x} ${y}l2.6 .5-1.5 2.2z"/>`).join(''),
    question: `<g class="bob" style="${ph(1600)}">${glyph('?')}</g>`,
    ok: `<path class="f" d="M${L - 3.5} ${Y + 1.5}q3.5 -4.5 7 0M${R - 3.5} ${Y + 1.5}q3.5 -4.5 7 0"/>`,
    review: dots(2.6),
    fail: `<path class="f" d="M${L - 2.8} ${Y - 2.8}l5.6 5.6M${L + 2.8} ${Y - 2.8}l-5.6 5.6M${R - 2.8} ${Y - 2.8}l5.6 5.6M${R + 2.8} ${Y - 2.8}l-5.6 5.6"/>`,
    sleep: `<path class="f" d="M${L - 3} ${Y + .5}h6M${R - 3} ${Y + .5}h6"/>`,
  }[m];
  const gear = (cx, cy, r, cls, ms) => `<g class="gear ${cls}" style="${ph(ms)}"><circle class="fx" cx="${cx}" cy="${cy}" r="${r}" stroke-width="2.2" stroke-dasharray="1.5 1.3"/><circle class="fx" cx="${cx}" cy="${cy}" r="${r - 1.6}"/></g>`;
  const extra = big ? ({
    think: `<g><path class="bub" d="M33 1.5h11a3 3 0 0 1 3 3v4a3 3 0 0 1-3 3h-6l-3 2.6v-2.6h-2a3 3 0 0 1-3-3v-4a3 3 0 0 1 3-3z"/>
      ${[35.6, 38.9, 42.2].map((x, i) => `<circle class="ff d${i + 1}" cx="${x}" cy="6.5" r="1.1" style="${ph(1600)}"/>`).join('')}</g>`,
    work: gear(41.5, 40.5, 4.6, '', 2400) + gear(46.6, 34.6, 2.9, 'small', 1500),
    write: `<path class="fx scrib" style="${ph(1800)}" d="M34 45q2-3 4 0t4 0t4 0"/><g class="pen" style="${ph(450)}"><path class="fx" d="M47.5 31.5l-8 8.5-1.6 3.4 3.4-1.6 8-8.5z" fill="var(--panel)"/><path class="fx" d="M45.7 33.4l1.8 1.8"/></g>`,
    sleep: '<text x="41" y="9">z</text>',
    review: '<path class="f" d="M41 14v10M41 14l5 2-5 2"/>',
  }[m] || '') : '';
  return `<svg class="rb rb-${m}" width="${size}" height="${size}" viewBox="0 0 48 48" role="img" aria-label="${JT_MOODS[m][0]}"><title>${JT_MOODS[m][0]} — ${JT_MOODS[m][1]}</title>
    <g class="all"><line class="ant" x1="24" y1="5" x2="24" y2="9.5"/><circle class="bulb" cx="24" cy="4" r="2.4"/>
    <rect class="hd" x="5" y="17" width="3" height="9" rx="1.5"/><rect class="hd" x="40" y="17" width="3" height="9" rx="1.5"/>
    <rect class="hd" x="8" y="9.5" width="32" height="27" rx="8"/><rect class="scr" x="12" y="14" width="24" height="17.5" rx="5"/>
    <g class="eyes">${eyes}</g></g>${extra}</svg>`;
}

/* ---------- model: run row -> branches ---------- */
const jtStage = (row) => Math.max(0, JT_STAGES.indexOf(row.stage || 'L0'));
const jtDone = (row) => JT_FINAL.includes(row.status);
// The code a worker is on: SUB = first open code of the group it draws now; SOLO = the open code furthest along.
function jtCurrent(codes, by, now) {
  const open = codes.filter((c) => by[c] && !jtDone(by[c]));
  if (now) return now.find((c) => open.includes(c)) || null;
  return open.reduce((best, c) => (best === null || jtStage(by[c]) > jtStage(by[best]) ? c : best), null);
}
function jtMood(w, codes, by, live) {
  if (!live || w.state === 'WAIT') return 'sleep';
  if (w.state === 'DONE') {
    return codes.every((c) => ['PASS', 'MANUAL'].includes((by[c] || {}).status)) ? 'ok' : 'review';   // as in the approved demo
  }
  if (w.act_at && Date.now() / 1000 - w.act_at > JT_IDLE_S) return 'sleep';
  return JT_MOODS[w.mood] ? w.mood : 'think';
}
function jtModel(r) {
  const rows = r.codes_status || [], by = Object.fromEntries(rows.map((x) => [x.code, x])), live = r.status === 'RUNNING';
  const a = r.assignment || {mode: 'SOLO', workers: [{name: 'SOLO', model: (r.usage && r.usage.model) || '', effort: (r.usage && r.usage.effort) || '', codes: [], state: 'RUN'}]};
  const plan = a.mode === 'SUB' && (a.workers || []).length === 1 && a.workers[0].name === 'Plan';
  const solo = a.mode !== 'SUB' || plan;
  let ws = (a.workers || []).map((w) => ({...w, codes: solo ? rows.map((x) => x.code) : (w.codes || []).filter((c) => by[c])}));
  ws = solo ? ws.slice(0, 1) : ws.filter((w) => w.codes.length);   // a slot shows up once it took a code
  const taken = new Set(ws.flatMap((w) => w.codes));
  const queue = solo ? [] : rows.map((x) => x.code).filter((c) => !taken.has(c));
  // A sonnet PREVIEW / FAIL is redone by another call (opus): the code shows under the slot redoing it ("kiểm lại")
  // and, under the slot that drew it first, points there.
  const handed = {};
  ws.forEach((w) => (w.recheck || []).forEach((c) => { handed[c] = w.name; }));
  return {solo, plan, by, live, queue, handed, sub: a.mode === 'SUB' && !plan, qa: r.kind === 'QA',
    ws: ws.map((w) => ({...w, re: new Set(w.recheck || []), cur: live && w.state !== 'DONE' ? jtCurrent(w.codes, by, solo ? null : w.now) : null, face: jtMood(w, w.codes, by, live)}))};
}
// Recheck note of one card in worker w's column: {re} = this slot redoes it, {to} = another slot took it over.
const jtRecheck = (m, w, code) => (w.re.has(code) ? {re: true} : m.handed[code] && m.handed[code] !== w.name ? {to: m.handed[code]} : {});
const jtKey = (m, fit) => [m.qa, m.solo, m.plan, m.ws.map((w) => `${w.name}:${w.codes.join()}:${[...w.re].join()}`).join('|'), m.queue.join(), m.solo ? fit : ''].join('/');

/* ---------- DOM helpers: write only what changed ---------- */
const jtText = (el, t, tip) => { if (el.textContent !== t) el.textContent = t; if (tip && el.title !== t) el.title = t; };
const jtHTML = (el, h) => { if (el._h !== h) { el._h = h; el.innerHTML = h; } };
const jtCls = (el, c) => { if (el.className !== c) el.className = c; };
const jtRobot = (el, m, size) => { if (el.dataset.m !== m) { el.dataset.m = m; el.innerHTML = robot(m, size); } };
const jtGroups = (n, max = 5) => { const k = Math.max(1, Math.ceil(n / max)); return {k, per: Math.ceil(n / k)}; };
// How many 156-px SOLO cards fit in a row (at most 5): a phone gets fewer per row, not 5+1.
const jtFits = (host) => Math.max(1, Math.min(5, Math.floor(((host.clientWidth || 900) - 32 - 22 - 4 + 12) / (156 + 12))));
const jtRO = typeof ResizeObserver === 'function' ? new ResizeObserver((es) => es.forEach((e) => e.target._wv && jtLayoutWires(e.target._wv))) : null;

function jtCard(code, lamps = JT_STAGES) {
  return `<button class="jt-code" data-code="${esc(code)}"><span class="jt-crow"><span class="jt-cno">${esc(code)}</span><span class="jt-st"></span></span>
    <span class="jt-lights">${lamps.map((s) => `<span class="jt-lt"><i class="jt-dot"></i>${s}</span>`).join('')}</span>
    <span class="jt-act"><span></span><time></time></span></button>`;
}
function jtCol(w, solo, fit, queue, lamps) {
  const n = w.codes.length, g = jtGroups(n, solo ? fit : 5);
  const head = queue ? `<div class="jt-sub"><span class="jt-mood">Chưa nhận</span><small class="mono">${n} mã chờ tác nhân rảnh</small></div>`
    : `<div class="jt-sub"><span class="jt-mood"></span><small class="mono"></small><span class="jt-dc"></span></div>`;
  return `<div class="jt-col${solo ? ' solo' : ''}${queue ? ' queue' : ''}">${head}
    <div class="jt-codes" style="${solo ? `--per:${g.per}` : `--k:${g.k};--rows:${g.per}`}">${w.codes.map((c) => jtCard(c, lamps)).join('')}</div>
    ${queue ? '' : '<svg class="jt-wires" aria-hidden="true"></svg><svg class="jt-wires" aria-hidden="true"></svg>'}</div>`;
}
const jtCards = (col) => [...col.querySelectorAll('.jt-code')].map((btn) => ({btn, code: btn.dataset.code, st: btn.querySelector('.jt-st'),
  dots: [...btn.querySelectorAll('.jt-dot')], act: btn.querySelector('.jt-act'), txt: btn.querySelector('.jt-act span'), time: btn.querySelector('.jt-act time')}));

/* Build the tree for run r into host (a fresh element); returns the view handle that jtUpdate reuses. */
function jtBuild(host, r) {
  const m = jtModel(r), fit = jtFits(host);
  const lamps = m.qa ? JT_QA_STAGES : JT_STAGES;
  host.innerHTML = `<div class="jt-tree"><div class="jt-subs">${m.ws.map((w) => jtCol(w, m.solo, fit, false, lamps)).join('')}${m.queue.length ? jtCol({codes: m.queue}, false, fit, true, lamps) : ''}</div>
    ${m.qa ? '<div class="jt-final"></div>' : ''}</div>`;
  const cols = [...host.querySelectorAll('.jt-col')];
  const v = {host, key: jtKey(m, fit), final: host.querySelector('.jt-final'), ws: cols.filter((c) => !c.classList.contains('queue')).map((col) => (col._wv = {col,
    mood: col.querySelector('.jt-mood'), meta: col.querySelector('.jt-sub small'), rb: col.querySelector('.jt-dc'), svg: col.querySelectorAll('svg.jt-wires'),
    routes: null, rkey: '', want: '', lit: null, cards: jtCards(col)})), queue: cols.filter((c) => c.classList.contains('queue')).flatMap(jtCards)};
  return v;
}
function jtCardUpdate(cv, row, on, act, actAt, confused, qa, rk = {}) {
  const done = jtDone(row), k = jtStage(row), s = row.status;
  const tone = on ? 'cur' : done ? {PASS: 'pass', PREVIEW: 'rev', MANUAL: 'man'}[s] || 'fail' : 'q';
  jtCls(cv.btn, `jt-code s-${tone}${!done && !on && (k === 0 || rk.to) ? ' q' : ''}`);
  const names = qa ? JT_QA_STAGES : JT_STAGES;
  const label = (qa ? {PASS: 'PASS · đúng', FAIL: 'FAIL · có lỗi'}
    : {PASS: 'PASS · đã giao', PREVIEW: 'PREVIEW · đã giao', FAIL: 'FAIL · đã giao', NOFILE: 'không có file', MANUAL: 'Người dùng tự làm'})[s]
    || (rk.to ? `→ kiểm lại ở ${rk.to}` : '')
    || (rk.re ? 'kiểm lại · ' : '') + (on ? `đang ${names[k]}` : k ? `dừng ở ${names[k]}` : 'chờ');
  jtText(cv.st, label + (row.flags && !done ? ` · ${row.flags} FLAG` : ''), true);
  jtCls(cv.st, `jt-st ${on ? 'run' : {PASS: 'ok', PREVIEW: 'warn', FAIL: 'err', NOFILE: 'err', MANUAL: 'man'}[s] || ''}`);
  cv.dots.forEach((d, i) => jtCls(d, `jt-dot ${done ? (i < 3 ? 'done' : {PASS: 'pass', PREVIEW: 'rev', MANUAL: 'man'}[s] || 'fail') : i < k ? 'done' : i === k && on ? 'now' : ''}`));
  const a = on ? act || '' : '';
  jtCls(cv.act, `jt-act${a ? ' on' : ''}${a && confused ? ' err' : ''}`);
  jtText(cv.txt, a, true);
  cv.time.dataset.at = a && actAt ? String(actAt) : '';
  jtText(cv.time, a && actAt ? jtSecs(actAt) : '');
}
const jtSecs = (at) => { const s = Math.max(0, Math.round(Date.now() / 1000 - at)); return s < 120 ? `${s}s` : `${Math.round(s / 60)} phút`; };

/* Update the tree in place; returns false when the layout changed (caller rebuilds with jtBuild). */
function jtUpdate(v, r) {
  const m = jtModel(r);
  if (v.key !== jtKey(m, jtFits(v.host))) return false;
  m.ws.forEach((w, i) => {
    const wv = v.ws[i];
    jtText(wv.mood, m.plan ? 'Lập kế hoạch' : JT_MOODS[w.face][0]);
    const redo = w.state === 'RUN' && (w.now || []).some((c) => w.re.has(c));
    jtText(wv.meta, [m.sub ? w.name : '', [w.model && w.model.replace(/^claude-/, ''), w.effort].filter(Boolean).join(' · '), redo ? 'kiểm lại' : ''].filter(Boolean).join(' · '));
    jtRobot(wv.rb, w.face, 64);
    wv.cards.forEach((cv, xi) => {
      const on = cv.code === w.cur;
      jtCardUpdate(cv, m.by[cv.code] || {}, on, w.act, w.act_at, w.face === 'confused', m.qa, jtRecheck(m, w, cv.code));
      if (on) wv.want = `${xi}|${jtStage(m.by[cv.code])}`;
    });
    if (!w.cur) wv.want = '';
    jtDrawLit(wv);
  });
  v.queue.forEach((cv) => jtCardUpdate(cv, m.by[cv.code] || {}, false, '', null, false, m.qa));
  if (v.final) {   // QA: each code's line is written as soon as it is checked; a failing code's DXF goes at once
    const rows = Object.values(m.by), done = rows.filter(jtDone).length, bad = rows.filter((x) => x.status === 'FAIL').map((x) => x.code);
    jtCls(v.final, `jt-final${done === rows.length && rows.length ? (bad.length ? ' bad' : ' ok') : ''}`);
    jtText(v.final, done === rows.length && rows.length ? `QA xong · ${rows.length - bad.length}/${rows.length} PASS${bad.length ? ` · lỗi: ${bad.join(', ')}` : ''}`
      : `QA từng mã · đã kiểm ${done}/${rows.length}${bad.length ? ` · đã giao ${bad.length} file lỗi` : ''} · mỗi mã ghi ngay vào AI_QA.txt`);
  }
  return true;
}
// The face of the whole run (header): the most urgent worker mood.
const jtRunMood = (r) => { const m = jtModel(r); return m.ws.map((w) => w.face).sort((a, b) => JT_PRI.indexOf(a) - JT_PRI.indexOf(b))[0] || 'sleep'; };
const jtTick = (root) => root.querySelectorAll('.jt-act time[data-at]').forEach((t) => { if (t.dataset.at) jtText(t, jtSecs(+t.dataset.at)); });
function jtMount(v) { v.ws.forEach((wv) => { jtLayoutWires(wv); if (jtRO) jtRO.observe(wv.col); }); }
function jtUnmount(v) { if (jtRO) v.ws.forEach((wv) => jtRO.unobserve(wv.col)); }
const jtRelayout = (v) => v.ws.forEach(jtLayoutWires);

/* ---------- wires: one per code from the robot's neck; robot -> current code lit ---------- */
function jtRounded(pts, rad = 6) {   // polyline with rounded corners (radius never more than half a segment)
  const p = pts.filter((q, i) => !i || Math.hypot(q[0] - pts[i - 1][0], q[1] - pts[i - 1][1]) > 0.5);
  let d = `M${p[0][0].toFixed(1)} ${p[0][1].toFixed(1)}`;
  for (let i = 1; i < p.length - 1; i++) {
    const [a, b, c] = [p[i - 1], p[i], p[i + 1]];
    const l1 = Math.hypot(b[0] - a[0], b[1] - a[1]), l2 = Math.hypot(c[0] - b[0], c[1] - b[1]), r = Math.min(rad, l1 / 2, l2 / 2);
    const s = [b[0] - (b[0] - a[0]) / l1 * r, b[1] - (b[1] - a[1]) / l1 * r], e = [b[0] + (c[0] - b[0]) / l2 * r, b[1] + (c[1] - b[1]) / l2 * r];
    d += `L${s[0].toFixed(1)} ${s[1].toFixed(1)}Q${b[0].toFixed(1)} ${b[1].toFixed(1)} ${e[0].toFixed(1)} ${e[1].toFixed(1)}`;
  }
  const z = p[p.length - 1];
  return d + `L${z[0].toFixed(1)} ${z[1].toFixed(1)}`;
}
// SOLO rows: neck -> bus above row 1 -> (other rows: gutter left of the grid, down to the row's bus) -> down into the code.
// SUB columns: neck -> bus above the columns -> along to the column's trunk -> down -> into the code's side.
function jtLayoutWires(wv) {
  const col = wv.col, head = col.querySelector('.jt-sub .rb');
  if (!head || !col.isConnected || !col.offsetWidth || !wv.cards.length) return;
  const cr = col.getBoundingClientRect(), rb = head.getBoundingClientRect(), solo = col.classList.contains('solo');
  const box = (b) => { const r = b.getBoundingClientRect(); return {x: r.left - cr.left, y: r.top - cr.top, w: r.width, h: r.height}; };
  const nx = rb.left - cr.left + rb.width / 2, ny = rb.top - cr.top + rb.height * 0.76;   // neck = bottom of the head
  const boxes = wv.cards.map((cv) => box(cv.btn)), top = Math.min(...boxes.map((r) => r.y)), bus = top - 12;
  const gx = Math.min(...boxes.map((r) => r.x)) - 11;
  const route = solo
    ? (r) => (r.y - top < 4 ? [[nx, ny], [nx, bus], [r.x + r.w / 2, bus], [r.x + r.w / 2, r.y]]
      : [[nx, ny], [nx, bus], [gx, bus], [gx, r.y - 12], [r.x + r.w / 2, r.y - 12], [r.x + r.w / 2, r.y]])
    : (r) => { const tx = r.x - 12, y = r.y + r.h / 2; return [[nx, ny], [nx, bus], [tx, bus], [tx, y], [r.x, y]]; };
  const routes = boxes.map((r) => jtRounded(route(r))), rkey = `${col.offsetWidth}x${col.offsetHeight}|${routes.join()}`;
  if (rkey === wv.rkey) return;
  wv.routes = routes; wv.rkey = rkey;
  for (const s of wv.svg) { s.setAttribute('width', col.offsetWidth); s.setAttribute('height', col.offsetHeight); }
  wv.svg[0].innerHTML = routes.map((d) => `<path class="jt-wire" d="${d}"/>`).join('');
  wv.lit = null; jtDrawLit(wv);
}
// Lit wire in its own layer: changes only when the current code or its stage changes (later stage = brighter, faster sparks).
function jtDrawLit(wv) {
  if (!wv.routes || wv.lit === wv.want) return;
  wv.lit = wv.want;
  if (!wv.want) { wv.svg[1].innerHTML = ''; return; }
  const [i, k] = wv.want.split('|').map(Number), d = wv.routes[i], dur = 900 - 150 * k;
  wv.svg[1].innerHTML = `<path class="jt-wire w-cur" style="--k:${k};${jtPhase(1200)}" d="${d}"/><path class="jt-spark" style="--k:${k};animation-duration:${dur}ms;${jtPhase(dur)}" d="${d}"/>`;
}
