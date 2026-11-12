'use strict';
window.addEventListener('error', e => { const b = document.getElementById('err'); if (b) { b.hidden = false; b.textContent = 'Lỗi giao diện: ' + e.message + ' (dòng ' + e.lineno + ')'; } });
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const LS = {get(k, d){try{const v = localStorage.getItem(k); return v == null ? d : v}catch(e){return d}},
            set(k, v){try{localStorage.setItem(k, v)}catch(e){}}};

const ST = {chua:'Chưa làm', dang:'Đang làm', xong:'Đã xong', cho:'Đang chờ khách trả lời', tay:'Tự làm', thieu:'Thiếu file'};
const RV = {cho:'Chờ check', dung:'Đúng', sai:'Sai'};
const S = {data:null, reviews:{}, oFilter:'all', oDate:(() => {const t = new Date(), p = n => String(n).padStart(2, '0'); return {d:p(t.getDate()), m:p(t.getMonth() + 1), y:String(t.getFullYear())}})(), oQ:'', sel:null, rsel:null, rOpen:new Set(), drafts:{}, plan:null, manual:null, compare:{}, packMsg:{}, oLimit:60,
           rFilter:LS.get('pw-rf','cho'), rDate:{d:'', m:'', y:''}, rQ:'', cGroup:LS.get('pw-cg','ngay')};

/* ---------- tiện ích ---------- */
const chip = (cls, txt) => `<span class="chip s-${cls}"><span class="dot"></span>${esc(txt)}</span>`;
const t = iso => iso ? new Date(iso).getTime() : null;
function dur(ms){
  if (ms == null || ms < 0) return '—';
  const m = Math.round(ms / 60000);
  if (m < 60) return m + ' phút';
  const h = Math.floor(m / 60), r = m % 60;
  if (h < 24) return h + ' giờ' + (r ? ' ' + r + ' phút' : '');
  return Math.floor(h / 24) + ' ngày ' + (h % 24) + ' giờ';
}
const ago = iso => iso ? dur(Date.now() - t(iso)) + ' trước' : '—';
const hm = iso => iso ? new Date(iso).toLocaleString('vi-VN', {hour:'2-digit', minute:'2-digit', day:'2-digit', month:'2-digit'}) : '—';
const dm = d => d ? d.slice(8, 10) + '/' + d.slice(5, 7) : '';
const month = d => d ? d.slice(0, 7) : '';
const mLabel = m => 'Tháng ' + (+m.slice(5, 7)) + '/' + m.slice(0, 4);
function toast(msg){const e = $('#toast'); e.textContent = msg; e.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => e.hidden = true, 1800)}

async function api(path, body){
  const r = await fetch(path, body ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)} : {cache:'no-store'});
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || r.status);
  return j;
}

async function load(force){
  try {
    const [d, rv, cmp] = await Promise.all([api('/api/state' + (force ? '?refresh=1' : '')), api('/api/reviews'), api('/api/compare').catch(() => ({}))]);
    S.compare = cmp || {};
    // dữ liệu agent báo có thể sai định dạng (flags là chuỗi): chuẩn hoá về mảng để giao diện không bị lỗi
    const arr = v => Array.isArray(v) ? v.map(String) : (v ? [String(v)] : []);
    (d.orders || []).forEach(o => { o.flags = arr(o.flags); o.agents = arr(o.agents); (o.codes || []).forEach(c => { c.flagsRaw = arr(c.flags); c.flags = (c.manual || c.previewOk) ? [] : c.flagsRaw; if (c.previewOk) c.flagsRaw = arr(c.flagsOrig); }); });   // mã người dùng tự làm: ẩn Flag trên giao diện (giữ flagsRaw để xem lại khi hoàn tác)
    S.data = d; S.reviews = rv;
    $('#err').hidden = true;
    $('#upd').textContent = 'Cập nhật ' + new Date().toLocaleTimeString('vi-VN', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
    render();
  } catch (e) {
    $('#err').hidden = false;
    $('#err').textContent = 'Không kết nối được server (' + e.message + '). Hãy chạy start.bat.';
  }
}

/* ---------- MỤC 1: TIẾN ĐỘ ---------- */
function orderTime(o){
  // Có dữ liệu lần chạy của agent: cộng thời gian LÀM của từng lần (lần đầu + các lần làm tiếp), bỏ khoảng chờ người dùng
  if (o.runs && o.runs.length) {
    const ms = r => (r.e ? t(r.e) : Date.now()) - t(r.s);
    const total = o.runs.reduce((a, r) => a + Math.max(0, ms(r)), 0);
    const parts = o.runs.map((r, i) => (o.runs.length > 1 ? (i ? 'Làm tiếp ' + i : 'Lần đầu') + ': ' : '') + hm(r.s) + ' đến ' + (r.e ? hm(r.e) : 'nay') + ' (' + dur(ms(r)) + ')');
    return {txt:dur(total) + (o.runs.length > 1 ? ' · ' + o.runs.length + ' lần chạy' : ''),
            tip:parts.join('; ') + '. Không tính thời gian chờ người dùng xác nhận.'};
  }
  const s = t(o.startedAt);
  if (!s) return {txt:'—'};
  if (o.state === 'xong' && o.finishedAt) return {txt:(o.timeEstimated ? '≈ ' : '') + dur(t(o.finishedAt) - s), tip:'Từ ' + hm(o.startedAt) + ' đến ' + hm(o.finishedAt) + (o.timeEstimated ? ' (ước tính theo thời gian file)' : '')};
  if (o.state === 'dang') return {txt:dur(Date.now() - s), tip:'Bắt đầu ' + hm(o.startedAt)};
  return {txt:'—', tip:o.lastFileAt ? 'File mới nhất ' + hm(o.lastFileAt) : ''};
}

// Lọc theo trạng thái (ô thống kê hoặc ô chọn): bỏ lọc ngày để hiện tất cả đơn cùng trạng thái; bấm lại ô đó hoặc "Tổng đơn" thì về như cũ
function setOFilter(v){
  v = v || 'all';
  if (v === S.oFilter && v !== 'all') v = 'all';
  if (v !== 'all' && S.oFilter === 'all') { S.oDatePrev = S.oDate; S.oDate = {d:'', m:'', y:''}; }
  else if (v === 'all' && S.oDatePrev) { S.oDate = S.oDatePrev; S.oDatePrev = null; }
  S.oFilter = v; S.oLimit = 60;
}

function renderProgress(){
  const os = S.data.orders;
  const cnt = {chua:0, dang:0, xong:0, cho:0};
  os.forEach(o => cnt[o.state]++);
  const codes = os.reduce((a, o) => a + o.total, 0);
  const dotc = {chua:'var(--idle)', dang:'var(--run)', xong:'var(--ok)', cho:'var(--warn)'};
  $('#o-stats').innerHTML =
    ['chua', 'dang', 'xong', 'cho'].map(k => `<button class="stat ${S.oFilter === k ? 'on' : ''}" data-f="${k}"><b>${cnt[k]}</b><span><i class="dot" style="background:${dotc[k]}"></i>${ST[k]}</span></button>`).join('') +
    `<button class="stat ${S.oFilter === 'all' ? 'on' : ''}" data-f="all"><b>${os.length}</b><span>Tổng đơn · ${codes} mã</span></button>`;

  // hàng đợi việc người dùng giao
  const JS = {moi:['check', 'Chờ agent nhận'], nhan:['dang', 'Agent đã nhận'], xong:['xong', 'Xong'], loi:['sai', 'Lỗi']};
  const jobs = (S.data.jobs || []).filter(j => j.status === 'moi' || j.status === 'nhan' || Date.now() - t(j.at) < 24 * 3600e3).slice(0, 8);
  jtHTML($('#jobs'), jobs.map(j => `<div class="qj">
      ${chip(...(JS[j.status] || ['chua', j.status]))}
      <span class="mono">${esc(j.order || '—')}</span>
      <span class="t2">${j.kind === 'tiep' ? 'làm tiếp ' + Object.keys(j.answers || {}).length + ' mã' : (j.plan ? Object.entries(j.plan.agents || {}).map(([a, m]) => (a === 'main' ? 'Chính' : a) + ' ' + m).join(', ') : (j.subagents ? j.subagents + ' subagent' : 'agent chính') + (j.model ? ' · ' + j.model : ''))}</span>
      <span class="p" title="${esc(j.path)}">${esc(j.result || j.path)}</span>
      <span class="mono qt">${hm(j.at)}</span>
      ${j.status !== 'nhan' ? `<button class="ib" data-deljob="${esc(j.id)}" title="Xoá khỏi hàng đợi"><svg class="i"><use href="#i-x"/></svg></button>`
        : j.by === 'auto' ? `<button class="btn btn-sec sm" data-canceljob="${esc(j.id)}" title="Dừng agent đang chạy việc này">Dừng</button>` : ''}
    </div>`).join(''));
  const rn = S.data.runner || {};
  if (!$('#job-hint').classList.contains('err') && !$('#job-hint').classList.contains('ok'))
    $('#job-hint').textContent = rn.running !== undefined && rn.cli
      ? ''
      : 'Tự chạy agent đang tắt: đơn được đưa vào hàng đợi, nói với agent "Xử lý hàng đợi" để chạy.';

  // agents: một sơ đồ cho mỗi đơn có agent chạy (hoặc xong trong 12 giờ qua)
  const runs = buildRuns();
  $('#a-n').textContent = runs.filter(r => r.status === 'RUNNING').length;
  patchRunning(runs);

  // filters
  fillDate('#o-date', os.map(o => o.date), S.oDate);
  const ost = $('#o-date .ost');      // ô lọc trạng thái đơn, dùng chung S.oFilter với 5 ô thống kê phía trên
  if (!ost.options.length) ost.innerHTML = [['all', 'Trạng thái'], ['chua', ST.chua], ['dang', ST.dang], ['xong', ST.xong], ['cho', ST.cho]].map(([v, l]) => `<option value="${v}">${l}</option>`).join('');
  ost.value = S.oFilter;

  const q = S.oQ.trim().toLowerCase();
  const list = os.filter(o => (S.oFilter === 'all' || o.state === S.oFilter) && inDate(o.date, S.oDate) &&
    (!q || o.order.includes(q) || (o.customer || '').toLowerCase().includes(q) || o.codes.some(c => c.code.includes(q))));
  // đơn đang làm / đang chờ lên đầu
  const pri = {dang:0, cho:1, chua:2, xong:3};
  list.sort((a, b) => pri[a.state] - pri[b.state] || (b.date + b.order).localeCompare(a.date + a.order));
  $('#o-n').textContent = list.length;
  const rows = list.slice(0, S.oLimit).map(orderRow).join('');
  $('#orders').innerHTML = `<div class="tr th"><span></span><span>Số đơn</span><span class="hm">Khách hàng</span><span class="hm">Vật liệu</span><span>Trạng thái</span><span class="hm">Tiến độ mã</span><span>Thời gian</span></div>` +
    (rows || `<div class="more t3">Không có đơn phù hợp.</div>`) +
    (list.length > S.oLimit ? `<div class="more"><button class="btn btn-sec" id="o-more">Xem thêm ${list.length - S.oLimit} đơn</button></div>` : '');
  renderDrawer();
}

/* ---------- sơ đồ agent (jobtree.js của dashboard mẫu) ---------- */
// Dữ liệu tiến độ (orders/agents/parts như CLAUDE.md) -> dạng "run" mà jobtree.js vẽ.
const secs = iso => iso ? Math.round(t(iso) / 1000) : null;
function buildRuns(){
  const now = Date.now(), byOrder = new Map();
  S.data.agents.forEach(a => { if (a.order) (byOrder.get(a.order) || byOrder.set(a.order, []).get(a.order)).push(a); });
  const runs = [];
  byOrder.forEach((ags, order) => {
    const live = ags.some(a => a.state === 'running' && !a.lost);
    const last = Math.max(...ags.map(a => t(a.finishedAt || a.heartbeatAt || a.startedAt) || 0));
    if (!live && now - last > 12 * 3600e3) return;
    const o = S.data.orders.find(x => x.order === order) || {order, codes:[], path:'', customer:''};
    if (!live && o.state === 'xong') return;     // đơn đã xong hoàn toàn: ẩn, chỉ hiện đơn đang chạy hoặc đang chờ
    const main = ags.find(a => a.kind === 'main') || {};
    const subs = ags.filter(a => a.kind !== 'main');
    const codes_status = o.codes.map(c => ({
      code:c.code,
      stage:'L' + Math.min(3, Math.max(0, +c.level || 0)),
      status:c.manual ? 'MANUAL' : c.previewOk ? 'PASS' : c.state === 'thieu' ? 'NOFILE' : c.pstatus === 'built' ? (c.flags.length ? 'PREVIEW' : 'PASS') : c.pstatus === 'failed' ? 'FAIL' : '',
      flags:c.flags.length,
    }));
    const wk = a => ({name:a.name || a.id, model:a.model || '', effort:a.effort || '', codes:a.codes || [],
      state:a.state === 'running' && !a.lost ? 'RUN' : a.state === 'running' ? 'WAIT' : 'DONE',
      now:a.current ? [a.current] : (a.kind === 'main' ? (o.codes.filter(c => c.pstatus === 'running').sort((x, y) => (y.startedAt || '').localeCompare(x.startedAt || ''))[0] ? [o.codes.filter(c => c.pstatus === 'running').sort((x, y) => (y.startedAt || '').localeCompare(x.startedAt || ''))[0].code] : []) : []), mood:a.mood, act:a.act || (a.kind === 'main' ? a.phase : ''), act_at:secs(a.actAt || a.heartbeatAt)});
    // Đơn có subagent mà agent chính cũng tự vẽ mã (theo phân công): hiện thêm một làn "Agent chính" cùng các subagent
    const jp = (S.data.jobs || []).filter(j => j.order === order && j.plan && j.kind !== 'tiep').sort((x, y) => (x.at || '').localeCompare(y.at || '')).pop();
    const mainCodes = jp ? Object.entries(jp.plan.codes || {}).filter(([, who]) => who === 'main').map(([c]) => c) : [];
    const mainW = subs.length && mainCodes.length ? [{...wk(main), name:'Agent chính', codes:mainCodes, isMain:true}] : [];
    const assignment = subs.length ? {mode:'SUB', workers:mainW.concat(subs.map(wk))}
      : {mode:'SUB', workers:[{...wk(main), name:'Plan'}]};
    const started = ags.map(a => a.startedAt).filter(Boolean).sort()[0];
    // đơn có mã PREVIEW (có Flag, chờ khách trả lời) hoặc đơn đang ở trạng thái 'cho' thì không phải XONG
    const waiting = !live && (o.state === 'cho' || codes_status.some(c => c.status === 'PREVIEW'));
    runs.push({id:order, job:order, kind:'RUN', status:live ? 'RUNNING' : 'DONE', waiting, user:main.user || o.user || '',
      started_at:started, ended_at:live ? null : new Date(last).toISOString(), slot:main.slot || '', usage:{model:main.model || '', effort:main.effort || ''},
      path:[o.path, o.customer, o.urgent].filter(Boolean).join('  '), codes_status, assignment, phase:main.phase || ''});
  });
  return runs.sort((a, b) => (a.status !== 'RUNNING') - (b.status !== 'RUNNING') || (b.started_at || '').localeCompare(a.started_at || ''));
}
const hhmm = ms => { if (ms == null || ms < 0) return '—'; const m = Math.floor(ms / 60000); return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); };
function runHead(r){
  const a = r.assignment, sub = a.workers[0].name !== 'Plan';
  const subW = a.workers.filter(x => !x.isMain), hasMain = a.workers.some(x => x.isMain);
  const w = subW[0] || a.workers[0];
  const model = (w.model || r.usage.model || '').replace(/^claude-/, '');
  return `<span class="jid">${esc(r.job)}</span>${r.status === 'RUNNING' ? '<span class="tag t-run">RUN</span>' : r.waiting ? '<span class="tag t-warn" title="Có mã PREVIEW: đang chờ khách trả lời, PREVIEW chuyển sang PASS thì đơn tự về Xong">ĐANG CHỜ KHÁCH TRẢ LỜI</span>' : '<span class="tag t-ok">XONG</span>'}
    ${sub ? `<span class="badge b-sub" title="Số subagent vẽ song song">${hasMain ? 'Chính + ' : ''}SUB×${subW.length}${model ? ' · ' + esc(model) : ''}</span>` : ''}
    <span class="meta">${esc(r.user || 'Agent')}</span>
    <div class="act"><button class="ib" data-copy="${esc(r.path.split('  ')[0])}" title="Copy thư mục đơn"><svg class="i"><use href="#i-folder"/></svg></button></div>`;
}
let runViews = new Map();
const folded = new Set();
function runShell(r){
  const node = document.createElement('article');
  node.className = 'job'; node.dataset.id = r.id;
  node.innerHTML = `<div class="job-h" title="Bấm để mở chi tiết đơn"><button class="ib jt-fold" data-act="fold" aria-label="Thu gọn / mở sơ đồ" title="Thu gọn / mở"><svg class="i" style="transform:rotate(90deg)"><use href="#i-chev"/></svg></button><span class="jt-dc" data-r="rb"></span><span class="jt-dc" data-r="head"></span></div>
    <div class="path" data-r="path"></div><div data-r="body"></div>`;
  const q = k => node.querySelector(`[data-r="${k}"]`);
  return {node, rb:q('rb'), head:q('head'), path:q('path'), body:q('body'), tree:null};
}
function runFill(v, r){
  jtRobot(v.rb, jtRunMood(r), 30);
  const h = runHead(r);
  if (v.head._h !== h) { jtHTML(v.head, h); tickSince(v.head); }
  jtText(v.path, r.path, true);
  const fold = folded.has(r.id);
  v.node.classList.toggle('folded', fold);
  if (fold) { if (v.tree) { jtUnmount(v.tree); v.tree = null; } jtHTML(v.body, ''); return null; }
  if (!r.codes_status.length) { jtHTML(v.body, `<div class="jt-tree"><div class="empty">${esc(r.phase || 'Đang đọc bản vẽ, chưa có danh sách mã…')}</div></div>`); return null; }
  if (v.tree && jtUpdate(v.tree, r)) return null;
  if (v.tree) jtUnmount(v.tree);
  v.body._h = null; v.body.innerHTML = '';
  v.tree = jtBuild(v.body, r); jtUpdate(v.tree, r);
  return v.tree;
}
function patchRunning(runs){
  const el = $('#running'), next = new Map(), mount = [];
  for (const r of runs) {
    const v = runViews.get(r.id) || runShell(r);
    const tr = runFill(v, r); if (tr) mount.push(tr);
    next.set(r.id, v);
  }
  runViews.forEach((v, id) => { if (!next.has(id) && v.tree) jtUnmount(v.tree); });
  runViews = next;
  if (!runs.length) {
    el.innerHTML = `<div class="empty" style="margin-bottom:8px">Không có agent nào đang chạy. Agent báo tiến độ bằng
      <code>py tools\\project_web\\report.py</code> (xem README trong tools\\project_web); trạng thái đơn bên dưới vẫn suy ra từ file trong AI_Work.</div>`;
  } else {
    const want = runs.map(r => next.get(r.id).node);
    if (want.length !== el.children.length || want.some((n, i) => el.children[i] !== n)) el.replaceChildren(...want);
  }
  mount.forEach(jtMount);
  const legend = $('#jt-legend'), show = [...next.values()].some(v => v.tree);
  legend.hidden = !show;
  if (show && !legend.innerHTML) legend.innerHTML = Object.entries(JT_MOODS).map(([m, [l, why]]) => `<div title="${esc(why)}">${robot(m, 48)}<b>${esc(l)}</b><span>${esc(why)}</span></div>`).join('');
}
function tickSince(root){
  root.querySelectorAll('[data-since]').forEach(el => {
    const s = t(el.dataset.since); if (!s) { el.textContent = '—'; return; }
    el.textContent = hhmm((el.dataset.end ? t(el.dataset.end) : Date.now()) - s);
  });
}
setInterval(() => { const r = $('#running'); if (r && !document.hidden) { jtTick(r); tickSince(r); } }, 1000);
window.addEventListener('resize', () => runViews.forEach(v => v.tree && jtRelayout(v.tree)));

function agentCard(a){
  const st = a.lost ? chip('sai', 'Mất tín hiệu') : a.state === 'running' ? chip('dang', 'Đang làm') : a.state === 'failed' ? chip('sai', 'Lỗi') : chip('xong', 'Xong');
  const total = (a.codes || []).length, done = (a.done || []).length;
  const end = a.state === 'running' ? Date.now() : t(a.finishedAt || a.heartbeatAt);
  return `<div class="agent ${a.lost ? 'lost' : ''}">
    <div class="agent-h"><svg class="i"><use href="#i-bot"/></svg><b>${esc(a.name || a.id)}</b><span class="sp"></span>${st}</div>
    <div class="row"><span>Đơn</span><span class="mono">${esc(a.order || '—')}</span></div>
    ${a.state === 'running' ? `<div class="row"><span>Đang làm mã</span><span class="cur">${esc(a.current || a.phase || '—')}</span></div>` : ''}
    ${a.kind === 'main' && a.phase ? `<div class="row"><span>Bước</span><span>${esc(a.phase)}</span></div>` : ''}
    ${total ? `<div class="pc"><div class="prog ${a.state === 'running' ? 'run' : ''}"><i style="width:${Math.round(done / total * 100)}%"></i></div><span>${done}/${total} mã</span></div>` : ''}
    <div class="row"><span>Bắt đầu</span><span>${hm(a.startedAt)}</span></div>
    <div class="row"><span>Thời gian làm</span><span class="mono">${dur(end - t(a.startedAt))}</span></div>
    <div class="row"><span>Tín hiệu cuối</span><span>${ago(a.heartbeatAt)}</span></div>
    ${a.note ? `<div class="row" style="color:var(--err-tx)">${esc(a.note)}</div>` : ''}
  </div>`;
}

function orderRow(o){
  const tm = orderTime(o);
  const pct = o.total ? Math.round(o.done / o.total * 100) : (o.hasAll ? 100 : 0);
  return `<div class="tr click ${S.sel === o.order ? 'picked' : ''}" data-o="${o.order}">
    <svg class="i chev"><use href="#i-chev"/></svg>
    <span class="mono">${o.order}</span>
    <span class="ell hm" title="${esc(o.customer)}">${esc(o.customer) || '<span class="t3">—</span>'}</span>
    <span class="ell hm t2" title="${esc(o.material)}">${esc(o.material) || '—'}</span>
    <span>${chip(o.state, ST[o.state])}</span>
    <span class="pc hm"><span class="prog ${o.state === 'dang' ? 'run' : ''}"><i style="width:${pct}%"></i></span><span>${o.done}/${o.total || '?'}</span></span>
    <span class="mono t2" title="${esc(tm.tip || '')}">${tm.txt}</span>
  </div>`;
}

/* ---------- khung chi tiết đơn (trượt ra từ bên phải khi bấm 1 đơn) ---------- */
function orderDrawer(o){
  const tm = orderTime(o);
  const pct = o.total ? Math.round(o.done / o.total * 100) : (o.hasAll ? 100 : 0);
  const job = (S.data.jobs || []).find(j => j.order === o.order && j.result);
  const dir = (S.data.workPath || S.data.work || 'AI_Work') + (o.path ? '\\' + o.path : '');
  const kv = (k, v) => `<dt>${k}</dt><dd>${v}</dd>`;
  const codes = o.codes.map(c => `<tr>
      <td class="mono">${esc(c.code)}</td>
      <td class="t2">${c.thick != null ? c.thick + 't' : '—'}</td>
      <td class="t2 mono">${esc(c.size || '—')}</td>
      <td>${chip(c.state, ST[c.state])}${c.previewOk ? ' <span class="t3">Preview OK</span> <button class="btn btn-sec sm" data-pvok="0" data-code="${esc(c.code)}" data-order="${esc(o.order)}" title="Hoàn tác Preview OK: mã quay lại trạng thái chờ">Hoàn tác</button>' : ''}${c.packed ? ' <span class="t3">đã đóng gói</span>' : ''}</td>
    </tr>`).join('');
  // Flag ghi ở dưới cùng: mỗi dòng gồm tên mã + nội dung Flag; mỗi mã có ô để bạn trả lời Flag cho agent làm tiếp
  const fu = (S.data.jobs || []).filter(j => j.kind === 'tiep' && j.order === o.order).sort((x, y) => (y.at || '').localeCompare(x.at || ''))[0];
  const busy = !!fu && (fu.status === 'moi' || fu.status === 'nhan');
  const draft = S.drafts[o.order] || {};
  const flagged = o.codes.filter(c => c.flags.length);
  const flagHtml = flagged.length
    ? flagged.map(c => `<div class="fl-c">${c.flags.map((f, i) => `<div class="fl"><b class="mono">${i ? '' : esc(c.code)}</b><span>${esc(f)}</span></div>`).join('')}
        <textarea class="fl-ans" data-c="${esc(c.code)}" rows="3" ${busy ? 'disabled' : ''} placeholder="Trả lời Flag của mã ${esc(c.code)} để agent vẽ lại (vd: mặt kegaki là mặt trên, vẽ thêm tấm D)">${esc(draft[c.code] || '')}</textarea>
        <div class="fl-ref">${(c.refs || []).map(n => `<span class="ref-chip" title="${esc(n)}"><span class="ell">${esc(n)}</span><button class="ib" data-refdel="${esc(c.code)}" data-order="${esc(o.order)}" data-name="${esc(n)}" ${busy ? 'disabled' : ''} title="Xoá file này"><svg class="i"><use href="#i-x"/></svg></button></span>`).join('')}
          <label class="btn btn-sec sm ${busy ? 'dis' : ''}" title="Nạp file PDF hoặc DXF tham khảo (tối đa 25 MB/file) để agent đọc khi làm tiếp mã này">Đính kèm PDF / DXF tham khảo<input type="file" class="ref-file" hidden multiple accept=".pdf,.dxf" data-c="${esc(c.code)}" data-order="${esc(o.order)}" ${busy ? 'disabled' : ''}></label></div>
        <div><button class="btn btn-pri sm" data-pvok="1" data-code="${esc(c.code)}" data-order="${esc(o.order)}" title="Hình dựng hiện tại đã đúng: mã tính là xong, bỏ Flag, không cần check lại">Preview OK</button></div></div>`).join('')
    : o.flags.map(f => `<div class="fl"><span>${esc(f)}</span></div>`).join('');
  const nFlag = flagged.reduce((n, c) => n + c.flags.length, 0) || o.flags.length;
  const cli = (S.data.runner || {}).cli;
  const fuMsg = !fu ? '' : fu.status === 'moi' ? `Đã gửi ${Object.keys(fu.answers || {}).length} mã, đang chờ agent nhận.`
    : fu.status === 'nhan' ? 'Agent đang làm tiếp các mã đã gửi.'
    : fu.status === 'xong' ? 'Lần làm tiếp gần nhất đã xong' + (fu.result ? ': ' + fu.result : '.')
    : 'Lần làm tiếp gần nhất bị lỗi' + (fu.result ? ': ' + fu.result : '.');
  const pm = S.packMsg[o.order];
  // đóng gói được khi có ít nhất 1 mã đã xong (không cần xong cả đơn); mã chưa xong bỏ qua, gửi khách nhiều đợt: đợt 1 vào Gui, đợt sau Gui_2, Gui_3...
  const nReady = o.packReady || 0, nPacked = o.packed || 0, nWait = o.codes.length - nReady - nPacked;
  const packOff = nReady < 1 || o.running;
  const packWhy = o.running ? 'Agent đang chạy đơn này' : nPacked && nReady < 1 ? 'Các mã đã xong đều đã được đóng gói' : 'Chưa có mã nào xong để đóng gói';
  const packHtml = `<h3>Đóng gói</h3><div class="fl-send" style="margin-top:0">
      <button class="btn btn-pri" data-pack="${esc(o.order)}" ${packOff ? 'disabled' : ''} title="${packOff ? esc(packWhy) : ''}"><svg class="i"><use href="#i-folder"/></svg>Đóng gói${nReady ? ' ' + nReady + ' mã đã xong' : ''}</button>
      <span class="t3">${packOff ? esc(packWhy) + '. Mở khi có ít nhất 1 mã đã xong.' : 'CHUYỂN DXF của ' + nReady + ' mã đã xong (không có file ALL) vào thư mục Gui' + (nPacked ? ' kế tiếp (Gui_2, Gui_3... không ghi đè đợt trước)' : '') + ' và điền file Excel 納品書 (số đơn, kích thước phôi) cho TẤT CẢ mã của đơn.' + (nWait > 0 ? ' ' + nWait + ' mã chưa xong: không chuyển DXF, trong Excel chỉ điền số thứ tự + mã và tô xanh.' : '')}</span></div>
    ${pm ? `<p class="hint ${pm.err ? 'err' : 'ok'}">${esc(pm.text)}${pm.path ? ` <button class="ib" data-copy="${esc(pm.path)}" title="Copy đường dẫn thư mục Gui"><svg class="i"><use href="#i-folder"/></svg></button>` : ''}</p>` : ''}`;
  const archHtml = (o.state === 'xong' || o.state === 'cho') ? `<h3>Phương án</h3><div class="fl-send" style="margin-top:0">
      <button class="btn btn-sec" data-arch="${esc(o.order)}">Lưu phương án và làm lại</button>
      <span class="t3">Chép Output sang AI_Work\\So_Sanh\\${esc(o.order)}\\ kèm số liệu rồi dọn đơn, để bạn Giao việc với phân công khác và so sánh.</span></div>` : '';
  const fuModel = LS.get('pw-model', 'opus');
  const fuHtml = flagged.length ? `<div class="fl-send">
      <select class="fl-model" title="Model AI vẽ lại các mã này" ${busy ? 'disabled' : ''}><option value="opus" ${fuModel === 'opus' ? 'selected' : ''}>Opus</option><option value="sonnet" ${fuModel === 'sonnet' ? 'selected' : ''}>Sonnet</option></select>
      <button class="btn btn-pri" data-fu="${esc(o.order)}" ${busy ? 'disabled' : ''}><svg class="i"><use href="#i-check"/></svg>Gửi cho agent làm tiếp</button>
      <span class="t3">${busy ? '' : (cli ? 'Agent tự chạy ngay, chỉ vẽ lại các mã bạn đã trả lời.' : 'Đưa vào hàng đợi; nói với agent "Xử lý hàng đợi" để chạy.')}</span>
    </div>${fuMsg ? `<p class="hint">${esc(fuMsg)}</p>` : ''}` : '';
  return `<div class="od-h">
      <span class="jid">${esc(o.order)}</span>${chip(o.state, ST[o.state])}${o.urgent ? `<span class="tag t-warn">${esc(o.urgent)}</span>` : ''}
      <span class="sp"></span><button class="ib" data-odclose title="Đóng (Esc)"><svg class="i"><use href="#i-x"/></svg></button>
    </div>
    <div class="od-b">
      ${job ? `<p class="od-sum">${esc(job.result)}</p>` : ''}
      <div class="pc od-prog"><span class="prog ${o.state === 'dang' ? 'run' : ''}"><i style="width:${pct}%"></i></span><span>${o.done}/${o.total || '?'} mã</span></div>
      <dl class="od-kv">
        ${kv('Thư mục', `<span class="mono">${esc(dir)}</span> <button class="ib" data-copy="${esc(dir)}" title="Copy đường dẫn"><svg class="i"><use href="#i-folder"/></svg></button>`)}
        ${kv('Khách hàng', esc(o.customer) || '—')}
        ${kv('Vật liệu', esc(o.material) || '—')}
        ${kv('Ngày đơn', o.date ? dm(o.date) + '/' + o.date.slice(0, 4) : '—')}
        ${o.user ? kv('Người chạy', esc(o.user)) : ''}
        ${kv('Agent', o.agents.length ? o.agents.map(esc).join(', ') : '—')}
        ${kv('Thời gian', `${tm.txt}${tm.tip ? ` <span class="t3">(${esc(tm.tip)})</span>` : ''}`)}
        ${kv('File', `${o.hasAll ? 'Đã có file ALL' : 'Chưa có file ALL'}${o.partFiles ? ' · ' + o.partFiles + ' file DXF riêng' : ''}${o.pdf ? ' · có PDF' : ''}`)}
        ${kv('File mới nhất', hm(o.lastFileAt))}
      </dl>
      <h3>Danh sách mã <span class="n">${o.codes.length}</span></h3>
      ${codes ? `<table class="od-t"><thead><tr><th>Mã</th><th>Dày</th><th>Kích thước</th><th>Trạng thái</th></tr></thead><tbody>${codes}</tbody></table>`
        : '<div class="empty">Không đọc được danh sách mã (thiếu file 依頼.xlsx).</div>'}
      ${nFlag ? `<h3>Flag <span class="n">${nFlag}</span></h3><div class="od-flags">${flagHtml}</div>${fuHtml}` : ''}
      ${packHtml}
      ${archHtml}
    </div>`;
}
/* khung chi tiết 1 mã bản vẽ (mục Đánh giá AI): xem thông tin + đổi Chờ check / Đúng / Sai */
function codeDrawer(x, r){
  const o = x.o, c = o.codes.find(c => c.code === r.code) || {};
  const key = o.order + '_' + r.code;
  const kv = (k, v) => `<dt>${k}</dt><dd>${v}</dd>`;
  const size = r.size && r.size !== '0.0 x 0.0' ? r.size : '';
  const fl = c.flags || [];
  return `<div class="od-h">
      <span class="jid">${esc(r.code)}</span>${chip(r.status === 'dung' ? 'xong' : r.status === 'sai' ? 'sai' : 'check', RV[r.status])}
      <span class="sp"></span><button class="ib" data-odclose title="Đóng (Esc)"><svg class="i"><use href="#i-x"/></svg></button>
    </div>
    <div class="od-b">
      <h3 style="margin-top:0">Kết quả check</h3>
      <div class="pick3 big cd-pick" data-k="${esc(key)}">
        <button data-s="cho" class="cho ${r.status === 'cho' ? 'on' : ''}">Chờ check</button>
        <button data-s="dung" class="dung ${r.status === 'dung' ? 'on' : ''}"><svg class="i"><use href="#i-check"/></svg>Đúng</button>
        <button data-s="sai" class="sai ${r.status === 'sai' ? 'on' : ''}"><svg class="i"><use href="#i-x"/></svg>Sai</button>
      </div>
      ${r.by || r.at ? `<p class="hint">Check bởi ${esc(r.by) || '—'} · ${hm(r.at)}</p>` : '<p class="hint">Chưa ai check mã này.</p>'}
      <h3>Thông tin mã</h3>
      <dl class="od-kv">
        ${kv('Số đơn', `<span class="mono">${esc(o.order)}</span> · ${dm(o.date)}/${(o.date || '').slice(0, 4)}`)}
        ${kv('Khách hàng', esc(o.customer) || '—')}
        ${kv('Vật liệu', esc(r.material || o.material) || '—')}
        ${kv('Độ dày', r.thick != null ? r.thick + ' mm' : '—')}
        ${kv('Kích thước', size ? `<span class="mono">${esc(size)}</span>` : '—')}
        ${c.blank ? kv('Phôi', `<span class="mono">${esc(c.blank)}</span>`) : ''}
        ${c.kind ? kv('Loại', esc(c.kind)) : ''}
        ${c.level != null ? kv('Mức', esc(c.level)) : ''}
        ${kv('Agent', c.agent ? esc(c.agent) : (o.agents.length ? o.agents.map(esc).join(', ') : '—'))}
        ${kv('Bắt đầu', c.startedAt ? hm(c.startedAt) : '—')}
        ${kv('Hoàn thành', c.finishedAt ? hm(c.finishedAt) : '—')}
        ${kv('Trạng thái làm', chip(c.state || 'chua', ST[c.state || 'chua']))}
        ${kv('File DXF', c.dxf
          ? `<span class="mono">${esc(c.dxf)}</span> <button class="ib" data-copy="${esc(c.dxf)}" title="Copy đường dẫn"><svg class="i"><use href="#i-folder"/></svg></button>${c.dxfKind === 'all' ? '<div class="t3" style="font-size:12px;margin-top:2px">Mã này nằm trong file ALL của đơn</div>' : ''}`
          : '<span class="t3">Chưa có file DXF</span>')}
      </dl>
      ${fl.length ? `<h3>FLAG <span class="n">${fl.length}</span></h3><div class="od-flags">${fl.map(f => '<div>⚑ ' + esc(f) + '</div>').join('')}</div>` : ''}
      <h3>Ghi chú</h3>
      <textarea class="cd-note" data-k="${esc(key)}" rows="4" placeholder="${r.status === 'sai' ? 'Sai ở đâu? (lưu khi bấm ra ngoài ô)' : 'Viết ghi chú (lưu khi bấm ra ngoài ô)'}">${esc(r.note)}</textarea>
    </div>`;
}
function renderDrawer(){
  const el = $('#od'), bg = $('#od-bg');
  let html = '', key = '';
  if (S.data && route() === 'danh-gia' && S.rsel) {
    const x = reviewOrders().find(x => x.o.order === S.rsel.o), r = x && x.rows.find(r => r.code === S.rsel.c);
    if (r) { html = codeDrawer(x, r); key = 'c' + S.rsel.o + '_' + S.rsel.c; } else S.rsel = null;
  } else if (S.data && route() === 'tien-do' && S.sel) {
    const o = S.data.orders.find(x => x.order === S.sel);
    if (o) { html = orderDrawer(o); key = 'o' + o.order; } else S.sel = null;
  }
  if (!html) { el.classList.remove('on'); bg.classList.remove('on'); document.body.classList.remove('od-open'); return; }
  const typing = el.contains(document.activeElement) && /^(TEXTAREA|INPUT)$/.test(document.activeElement.tagName) && el.dataset.o === key;
  if (el.dataset.h !== html && !typing) {
    const b = el.querySelector('.od-b'), top = b && el.dataset.o === key ? b.scrollTop : 0;
    el.innerHTML = html; el.dataset.h = html; el.dataset.o = key;
    el.querySelector('.od-b').scrollTop = top;
  }
  el.classList.add('on'); bg.classList.add('on'); document.body.classList.add('od-open');
}
function openOrder(id){ S.sel = S.sel === id ? null : id; renderProgress(); }
function openCode(o, c){ S.rsel = S.rsel && S.rsel.o === o && S.rsel.c === c ? null : {o, c}; renderReview(); }
function closeDrawer(){ S.sel = null; S.rsel = null; renderProgress(); renderReview(); }

// Bộ lọc ngày: 3 ô sổ xuống {d:'05', m:'11', y:'2026'}; ô nào để trống thì không lọc theo ô đó. Ngày dạng 'YYYY-MM-DD'.
function inDate(dt, r){
  if (!r || (!r.d && !r.m && !r.y)) return true;
  return (!r.y || dt.slice(0, 4) === r.y) && (!r.m || dt.slice(5, 7) === r.m) && (!r.d || dt.slice(8, 10) === r.d);
}
function fillDate(sel, dates, cur){
  const el = $(sel), [d, m, y] = el.querySelectorAll('select');
  const pad = n => String(n).padStart(2, '0');
  if (!d.options.length) {
    d.innerHTML = '<option value="">Ngày</option>' + Array.from({length:31}, (_, i) => `<option value="${pad(i + 1)}">${i + 1}</option>`).join('');
    m.innerHTML = '<option value="">Tháng</option>' + Array.from({length:12}, (_, i) => `<option value="${pad(i + 1)}">Tháng ${i + 1}</option>`).join('');
  }
  const years = [...new Set(dates.filter(Boolean).map(x => x.slice(0, 4)).concat(cur.y ? [cur.y] : []))].sort().reverse();
  const html = '<option value="">Năm</option>' + years.map(v => `<option value="${v}">${v}</option>`).join('');
  if (y.dataset.h !== html) { y.innerHTML = html; y.dataset.h = html; }
  d.value = cur.d; m.value = cur.m; y.value = cur.y;
  el.querySelector('.dclr').hidden = !(cur.d || cur.m || cur.y);
}

/* ---------- MỤC 2: ĐÁNH GIÁ AI ---------- */
// Một đơn đã xong: nếu đã có chấm từng mã thì dùng; nếu chưa và có file NTMF cũ thì dùng số liệu đó.
function reviewOrders(){
  return S.data.orders.filter(o => o.state === 'xong' && o.codes.length).map(o => {
    const rows = o.codes.map(c => {   // gồm cả mã người dùng tự làm (có thể AI làm sai nên mới tự làm) để tính vào đánh giá
      const r = S.reviews[o.order + '_' + c.code];
      return {code:c.code, manual:!!c.manual, thick:c.thick, material:c.material, size:c.size, status:r ? r.status : 'cho', note:r ? r.note : '', by:r ? r.by : '', at:r ? r.at : ''};
    });
    const perCode = rows.some(r => S.reviews[o.order + '_' + r.code]);
    const useLegacy = !perCode && !!o.legacy;
    const n = {cho:0, dung:0, sai:0};
    if (useLegacy) { n.dung = o.legacy.ok; n.sai = o.legacy.ng; n.cho = Math.max(0, rows.length - o.legacy.ok - o.legacy.ng); }
    else rows.forEach(r => n[r.status]++);
    return {o, rows, n, useLegacy};
  });
}

function renderReview(){
  const all = reviewOrders();
  const tot = {cho:0, dung:0, sai:0, codes:0};
  all.forEach(x => { tot.cho += x.n.cho; tot.dung += x.n.dung; tot.sai += x.n.sai; tot.codes += x.rows.length; });
  const checked = tot.dung + tot.sai;
  const pct = checked ? (tot.sai / checked * 100) : 0;
  $('#nav-cho').hidden = !tot.cho; $('#nav-cho').textContent = tot.cho;
  $('#r-stats').innerHTML = `
    <div class="stat"><b>${tot.codes}</b><span>Mã đã xong · ${all.length} đơn</span></div>
    <div class="stat"><b>${tot.cho}</b><span><i class="dot" style="background:var(--qa)"></i>Chờ check</span></div>
    <div class="stat"><b>${tot.dung}</b><span><i class="dot" style="background:var(--ok)"></i>Đúng</span></div>
    <div class="stat"><b>${tot.sai}</b><span><i class="dot" style="background:var(--err)"></i>Sai</span></div>
    <div class="stat"><b style="color:var(--err-tx)">${pct.toFixed(1)}%</b><span>Tỷ lệ mã sai (trên ${checked} mã đã check)</span></div>`;

  $('#c-group').innerHTML = [['ngay', 'Theo ngày'], ['thang', 'Theo tháng']].map(([k, l]) => `<button data-g="${k}" class="${S.cGroup === k ? 'on' : ''}">${l}</button>`).join('');
  renderChart(all);

  fillDate('#r-date', all.map(x => x.o.date), S.rDate);
  const fc = {cho:all.filter(x => x.n.cho).length, sai:all.filter(x => x.n.sai).length, all:all.length};
  $('#r-filter').innerHTML = [['cho', 'Chờ check'], ['sai', 'Có mã sai'], ['all', 'Tất cả']]
    .map(([k, l]) => `<button data-f="${k}" class="${S.rFilter === k ? 'on' : ''}">${l} <i>${fc[k]}</i></button>`).join('');

  const q = S.rQ.trim().toLowerCase();
  const list = all.filter(x => (S.rFilter === 'all' || x.n[S.rFilter]) && inDate(x.o.date, S.rDate) &&
    (!q || x.o.order.includes(q) || x.rows.some(r => r.code.includes(q))));
  renderCompare();
  $('#r-n').textContent = list.length;
  $('#reviews').innerHTML = list.slice(0, 40).map(reviewCard).join('') ||
    `<div class="empty">${S.rFilter === 'cho' ? 'Không còn mã nào chờ check.' : 'Không có đơn phù hợp.'}</div>` ;
  if (list.length > 40) $('#reviews').insertAdjacentHTML('beforeend', `<p class="hint">Đang hiện 40/${list.length} đơn, lọc theo tháng hoặc tìm số đơn để xem các đơn khác.</p>`);
  renderDrawer();
}

function reviewCard(x){
  const {o, rows, n, useLegacy} = x;
  const open = S.rOpen.has(o.order);
  const head = `<div class="rv-h ${open ? 'open' : ''}" data-rv="${esc(o.order)}" title="${open ? 'Bấm để thu gọn' : 'Bấm để xem các mã trong đơn'}">
    <svg class="i chev"><use href="#i-chev"/></svg>
    <span class="jid">${o.order}</span><span class="t2">${dm(o.date)}</span><span class="t3 ell" style="max-width:260px">${esc(o.customer)}</span>
    <span class="sp"></span>
    ${useLegacy ? `<span class="legacy">Đã chấm trước theo file ${o.legacy.ok}T${o.legacy.ng}F</span>` : ''}
    <span class="cnt">${n.cho ? chip('check', n.cho + ' Chờ') : ''}${n.dung ? chip('xong', n.dung + ' Đúng') : ''}${n.sai ? chip('sai', n.sai + ' Sai') : ''}</span>
  </div>`;
  // 3 ô trạng thái chỉ để xem (không bấm được); bấm vào cả thanh mã để mở khung chi tiết bên phải, đổi Đúng/Sai trong khung đó
  const body = rows.map(r => `<div class="rv-r ${S.rsel && S.rsel.o === o.order && S.rsel.c === r.code ? 'picked' : ''}" data-o="${o.order}" data-c="${esc(r.code)}" title="${r.by ? 'Check bởi ' + esc(r.by) + ' · ' + hm(r.at) : 'Bấm để xem chi tiết'}">
    <span class="mono">${esc(r.code)}${r.manual ? ' <span class="tag t-warn" style="margin-left:6px">TỰ LÀM</span>' : ''}</span>
    <span class="t3 ell">${[r.material, r.thick != null ? r.thick + 't' : '', r.size && r.size !== '0.0 x 0.0' ? r.size : ''].filter(Boolean).map(esc).join(' · ')}</span>
    <div class="pick3 ro" aria-label="Trạng thái check">
      ${r.status === 'dung' ? '<span class="dung on"><svg class="i"><use href="#i-check"/></svg>Đúng</span>'
        : r.status === 'sai' ? '<span class="sai on"><svg class="i"><use href="#i-x"/></svg>Sai</span>'
        : '<span class="cho on">Chờ check</span>'}
    </div>
  </div>`).join('');
  return `<div class="rv">${head}${open ? body : ''}</div>`;
}

// Biểu đồ: cột chồng Đúng / Sai của các mã ĐÃ CHECK (không tính Chờ check); % ghi ngay trong ô, đỉnh cột = tổng mã đã check
function renderChart(all){
  const key = S.cGroup === 'thang' ? (d => month(d)) : (d => d);
  const g = new Map();
  all.forEach(x => {
    const k = key(x.o.date);
    const v = g.get(k) || {dung:0, sai:0};
    v.dung += x.n.dung; v.sai += x.n.sai; g.set(k, v);
  });
  const pts = [...g.entries()].filter(([, v]) => v.dung + v.sai > 0).sort((a, b) => a[0].localeCompare(b[0])).slice(-30);
  if (!pts.length) { $('#chart').innerHTML = '<div class="empty">Chưa có mã nào được check. Biểu đồ sẽ hiện khi bạn chuyển mã sang Đúng hoặc Sai.</div>'; $('#c-note').textContent = ''; return; }
  const W = 1000, H = 300, L = 44, R = 12, T = 28, B = 34;
  const maxC = Math.max(4, Math.ceil(Math.max(...pts.map(([, v]) => v.dung + v.sai)) / 4) * 4);
  const bw = (W - L - R) / pts.length, base = H - B;
  const yC = c => T + (base - T) * (1 - c / maxC);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Kết quả check theo ${S.cGroup === 'thang' ? 'tháng' : 'ngày'}">`;
  for (let i = 0; i <= 4; i++) {
    const y = yC(maxC * i / 4);
    s += `<line class="ax" x1="${L}" x2="${W - R}" y1="${y}" y2="${y}"/><text x="${L - 6}" y="${y + 4}" text-anchor="end">${maxC * i / 4}</text>`;
  }
  pts.forEach(([k, v], i) => {
    const w = Math.min(bw * 0.64, 64), x = L + i * bw + (bw - w) / 2, cx = L + i * bw + bw / 2, t = v.dung + v.sai;
    const lbl = S.cGroup === 'thang' ? mLabel(k).replace('Tháng ', 'T') : dm(k);
    let y0 = base, seg = '';
    [['bd', v.dung], ['bs', v.sai]].forEach(([cls, n]) => {
      if (!n) return;
      const h = (base - T) * n / maxC;
      seg += `<rect class="${cls}" x="${x}" y="${y0 - h}" width="${w}" height="${h}"/>` +
        (h >= 14 ? `<text class="sv" x="${cx}" y="${y0 - h / 2 + 4}" text-anchor="middle">${Math.round(n / t * 100)}%</text>` : '');
      y0 -= h;
    });
    s += `<g><title>${lbl}: ${t} mã đã check · ${v.dung} đúng (${(v.dung / t * 100).toFixed(1)}%) · ${v.sai} sai (${(v.sai / t * 100).toFixed(1)}%)</title>
      <rect x="${L + i * bw}" y="${T}" width="${bw}" height="${base - T}" fill="transparent"/>${seg}
      <text class="v" x="${cx}" y="${y0 - 6}" text-anchor="middle">${t}</text>
      <text x="${cx}" y="${H - 14}" text-anchor="middle">${lbl}</text></g>`;
  });
  s += '</svg>';
  const lg = `<div class="c-lg"><span><i style="background:var(--ok)"></i>Đúng</span><span><i style="background:var(--err)"></i>Sai</span>` +
    `<span class="t3">% ghi trong ô, tính trên số mã đã check · số trên đầu cột = tổng mã đã check</span></div>`;
  $('#chart').innerHTML = lg + s;
  $('#c-note').textContent = 'Chỉ tính các mã đã check (Đúng + Sai), không tính Chờ check. Mỗi cột là một ' + (S.cGroup === 'thang' ? 'tháng' : 'ngày') + '; % Đúng và % Sai ghi trong từng ô. Rê chuột vào cột để xem số mã. Đơn chưa chấm từng mã nhưng có file kiểu 9T3F thì lấy số liệu file đó.';
}

async function setReview(items){
  items.forEach(it => {
    if (it.status === 'cho' && !it.note) delete S.reviews[it.key];
    else S.reviews[it.key] = {...(S.reviews[it.key] || {}), status:it.status, note:it.note ?? (S.reviews[it.key] || {}).note ?? '', by:LS.get('pw-who', '')};
  });
  renderReview();
  try { const r = await api('/api/review', {items, by:LS.get('pw-who', '')}); S.reviews = r.reviews; toast('Đã lưu'); }
  catch (e) { toast('Lỗi lưu: ' + e.message); load(); }
}

/* ---------- điều hướng & sự kiện ---------- */
function route(){ return (location.hash.match(/^#\/([\w-]+)/) || [])[1] === 'danh-gia' ? 'danh-gia' : 'tien-do'; }
function render(){
  if (!S.data) return;
  const r = route();
  document.querySelectorAll('nav a').forEach(a => a.classList.toggle('on', a.dataset.r === r));
  $('#v-tien-do').hidden = r !== 'tien-do'; $('#v-danh-gia').hidden = r !== 'danh-gia';
  if ((r !== 'tien-do' && S.sel) || (r !== 'danh-gia' && S.rsel)) { S.sel = null; S.rsel = null; renderDrawer(); }
  if (r === 'tien-do') renderProgress();
  if (r === 'danh-gia' && !document.activeElement?.classList.contains('note')) renderReview();
  else if (r === 'tien-do') { const tmp = reviewOrders().reduce((a, x) => a + x.n.cho, 0); $('#nav-cho').hidden = !tmp; $('#nav-cho').textContent = tmp; }
}
window.addEventListener('hashchange', render);

document.addEventListener('click', e => {
  const rh = e.target.closest('.rv-h[data-rv]');   // bấm tên đơn -> sổ ra / thu gọn các mã của đơn
  if (rh) { const id = rh.dataset.rv; S.rOpen.has(id) ? S.rOpen.delete(id) : S.rOpen.add(id); return renderReview(); }
  const rr = e.target.closest('.rv-r');
  if (rr && !e.target.closest('button')) return openCode(rr.dataset.o, rr.dataset.c);   // bấm thanh mã -> khung chi tiết bên phải
  const jh = e.target.closest('.job-h, .job > .path');   // bấm đầu thẻ agent đang chạy -> mở chi tiết đơn (nút thu gọn / copy giữ chức năng riêng)
  if (jh && !e.target.closest('button')) { const jb = jh.closest('.job'); if (jb && jb.dataset.id) { S.sel = jb.dataset.id; return renderProgress(); } }
  const b = e.target.closest('button, .tr.click');
  if (!b) return;
  if (b.classList.contains('dclr')) {
    const dr = b.closest('.drange'), k = dr.id === 'o-date' ? 'oDate' : 'rDate';
    S[k] = {d:'', m:'', y:''}; if (k === 'oDate') S.oDatePrev = null;
    return k === 'oDate' ? renderProgress() : renderReview();
  }
  if (b.dataset.act === 'fold') { const id = b.closest('.job').dataset.id; folded.has(id) ? folded.delete(id) : folded.add(id); return renderProgress(); }
  if (b.dataset.refdel) {
    api('/api/ref/delete', {order:b.dataset.order, code:b.dataset.refdel, name:b.dataset.name}).then(() => { toast('Đã xoá file tham khảo'); load(true); }, e2 => toast(e2.message));
    return;
  }
  if (b.dataset.canceljob) {
    if (!confirm('Dừng agent đang chạy việc này?')) return;
    api('/api/jobs/cancel', {id:b.dataset.canceljob}).then(() => { toast('Đã dừng'); load(true); }, e2 => toast(e2.message));
    return;
  }
  if (b.dataset.deljob) {
    api('/api/jobs/delete', {id:b.dataset.deljob}).then(() => { toast('Đã xoá khỏi hàng đợi'); load(true); }, e2 => toast(e2.message));
    return;
  }
  if (b.dataset.copy != null) { navigator.clipboard?.writeText(b.dataset.copy).then(() => toast('Đã copy: ' + b.dataset.copy), () => toast(b.dataset.copy)); return; }
  if (b.closest('#o-stats')) { setOFilter(b.dataset.f); return renderProgress(); }
  if (b.id === 'o-more') { S.oLimit += 60; return renderProgress(); }
  if (b.dataset.pack) {   // Đóng gói các mã đã xong: thư mục Gui (đợt 1) hoặc Gui_N (đợt sau) + file Excel
    const order = b.dataset.pack;
    b.disabled = true; S.packMsg[order] = {text: 'Đang đóng gói (điền Excel mất vài giây)...'}; renderDrawer();
    api('/api/package', {order}).then(r => {
      const x = r.result;
      S.packMsg[order] = {path: x.gui, text: 'Đợt ' + x.batch + ': đã chuyển ' + x.moved + ' file DXF và tạo file Excel trong ' + x.gui + '.' + (x.pending.length ? ' Chưa xong (tô xanh trong Excel): ' + x.pending.join(', ') + '.' : '') + (x.manual.length ? ' Mã tự làm chưa có trong Gui: ' + x.manual.join(', ') + '.' : '')};
      toast('Đã đóng gói đợt ' + x.batch); load(true);
    }, e2 => { S.packMsg[order] = {err: true, text: e2.message}; load(true); });
    return;
  }
  if (b.dataset.cdel) {   // xoá một phương án đã lưu khỏi bảng So sánh
    const dest = b.dataset.cdel, order = b.dataset.corder;
    if (!confirm('Xoá phương án này?\n\nThư mục AI_Work\\' + dest + ' (Output đã lưu và số liệu) bị xoá hẳn, không khôi phục được. Đơn và dữ liệu đang chạy không bị đụng.')) return;
    api('/api/compare/delete', {order, dest}).then(() => { toast('Đã xoá phương án'); load(true); }, e2 => toast(e2.message));
    return;
  }
  if (b.dataset.odclose != null) return closeDrawer();
  if (b.dataset.arch) {   // Lưu phương án và làm lại
    const order = b.dataset.arch;
    if (!confirm('Lưu phương án của đơn ' + order + '?\n\n- Output (DXF...) được chép sang AI_Work\\So_Sanh\\' + order + '\\ kèm số liệu.\n- Sau khi chép đủ, Output và tiến độ của đơn bị xoá, kết quả chấm Đúng/Sai của đơn được đưa về Chờ check (số liệu đã lưu trong phương án).\n- File đầu vào (PDF, xlsx, dwg) giữ nguyên.')) return;
    b.disabled = true;
    api('/api/archive', {order}).then(r => { toast('Đã lưu phương án ' + r.saved.label + ' (' + r.saved.files + ' file)'); closeDrawer(); load(true); },
      e2 => { b.disabled = false; toast(e2.message); });
    return;
  }
  if (b.dataset.fu) {   // gửi các trả lời Flag cho agent làm tiếp
    const order = b.dataset.fu, answers = {};
    Object.entries(S.drafts[order] || {}).forEach(([c, t]) => { if (t.trim()) answers[c] = t.trim(); });
    const od = S.data.orders.find(x => x.order === order);
    ((od && od.codes) || []).forEach(c => { if (c.flags.length && c.refs && c.refs.length && !(c.code in answers)) answers[c.code] = ''; });   // mã chỉ đính kèm file tham khảo, không ghi chú
    if (!Object.keys(answers).length) return toast('Chưa nhập trả lời hoặc đính kèm file cho mã nào');
    b.disabled = true;
    const model = (document.querySelector('#od .fl-model') || {}).value || 'opus';
    LS.set('pw-model', model);
    api('/api/jobs/followup', {order, answers, model}).then(() => { delete S.drafts[order]; toast('Đã gửi cho agent'); load(true); },
      e2 => { b.disabled = false; toast(e2.message); });
    return;
  }
  if (b.matches('.tr.click')) return openOrder(b.dataset.o);
  if (b.closest('#r-filter')) { S.rFilter = b.dataset.f; LS.set('pw-rf', S.rFilter); return renderReview(); }
  if (b.closest('#c-group')) { S.cGroup = b.dataset.g; LS.set('pw-cg', S.cGroup); return renderReview(); }
  if (b.closest('.cd-pick')) {   // đổi Chờ check / Đúng / Sai trong khung chi tiết mã (giữ nguyên ghi chú cũ nếu có)
    const k = b.closest('.cd-pick').dataset.k, cur = S.reviews[k];
    return setReview([{key:k, status:b.dataset.s, note:cur ? cur.note : ''}]);
  }
  if (b.id === 'reload') return load(true);
  if (b.dataset.t) { setTheme(b.dataset.t); }
});
// đóng khung chi tiết đơn: bấm nền mờ hoặc phím Esc
$('#od-bg').addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => { if (e.key === 'Escape' && (S.sel || S.rsel)) closeDrawer(); });
document.addEventListener('change', async e => {
  const el = e.target;
  if (el.classList && el.classList.contains('ref-file')) {   // nạp PDF/DXF tham khảo cho một mã (lưu vào <thư mục đơn>\Tham_Khao\<mã>)
    const files = Array.from(el.files || []), order = el.dataset.order, code = el.dataset.c;
    el.value = '';
    for (const f of files) {
      if (!/\.(pdf|dxf)$/i.test(f.name)) { toast('Bỏ qua ' + f.name + ': chỉ nhận PDF hoặc DXF'); continue; }
      if (f.size > 25 * 1024 * 1024) { toast('Bỏ qua ' + f.name + ': lớn hơn 25 MB'); continue; }
      try {
        toast('Đang nạp ' + f.name + '...');
        const data = await new Promise((ok, no) => { const rd = new FileReader(); rd.onload = () => ok(String(rd.result).split(',')[1] || ''); rd.onerror = () => no(new Error('Không đọc được file')); rd.readAsDataURL(f); });
        await api('/api/ref/upload', {order, code, name:f.name, data});
        toast('Đã nạp ' + f.name);
      } catch (err) { toast(f.name + ': ' + err.message); }
    }
    return load(true);
  }
  const dr = el.closest && el.closest('.drange');
  if (el.classList && el.classList.contains('ost')) { setOFilter(el.value); return renderProgress(); }
  if (dr) {
    const k = dr.id === 'o-date' ? 'oDate' : 'rDate', [d, m, y] = dr.querySelectorAll('select');
    S[k] = {d:d.value, m:m.value, y:y.value}; if (k === 'oDate') S.oDatePrev = null;
    return k === 'oDate' ? renderProgress() : renderReview();
  }
  if (el.classList.contains('cd-note')) {   // ghi chú của mã, lưu khi rời ô
    const k = el.dataset.k, cur = S.reviews[k];
    if ((cur ? cur.note : '') !== el.value) setReview([{key:k, status:cur ? cur.status : 'cho', note:el.value}]);
  }
});
document.addEventListener('input', e => {
  if (e.target.classList && e.target.classList.contains('fl-ans') && S.sel) { (S.drafts[S.sel] = S.drafts[S.sel] || {})[e.target.dataset.c] = e.target.value; }
  if (e.target.id === 'o-q') { S.oQ = e.target.value; S.oLimit = 60; renderProgress(); }
  if (e.target.id === 'r-q') { S.rQ = e.target.value; renderReview(); }
});

$('#job-form').addEventListener('submit', async e => {   // Giao việc / Enter -> đọc đơn rồi mở bảng phân công
  e.preventDefault();
  const hint = $('#job-hint'), btn = e.target.querySelector('button[type=submit]');
  const path = $('#job-path').value.trim();
  btn.disabled = true;
  try {
    const r = await api('/api/jobs/preview', {path});
    hint.className = 'hint'; hint.textContent = '';
    openPlan(r.preview);
  } catch (err) {
    hint.className = 'hint err'; hint.textContent = err.message;
  } finally { btn.disabled = false; }
});

/* ---------- So sánh phương án: các phương án đã lưu (AI_Work\So_Sanh\<đơn>\) + phương án hiện tại ---------- */
const mName = m => m === 'sonnet' ? 'Sonnet' : m === 'opus' ? 'Opus' : (m || '');
function planText(r){
  const p = r.plan;
  if (!p) return r.model ? 'Agent chính ' + mName(r.model) + (r.subagents ? ' + ' + r.subagents + ' subagent' : '') : 'Không có phân công (chạy trước khi có bảng phân công)';
  const cnt = a => Object.values(p.codes || {}).filter(x => x === a).length;
  return Object.entries(p.agents || {}).map(([a, m]) => paName(a) + ' ' + mName(m) + ' (' + cnt(a) + ' mã)').join(' · ');
}
function currentVariant(o){
  const jobs = (S.data.jobs || []).filter(j => j.order === o.order && (j.plan || j.model != null)).sort((a, b) => (a.at || '').localeCompare(b.at || ''));
  const last = jobs[jobs.length - 1] || {};
  const secs = (o.runs || []).reduce((a, r) => a + Math.max(0, (r.e ? t(r.e) : Date.now()) - t(r.s)), 0) / 1000;
  const rv = {dung:0, sai:0, cho:0};
  o.codes.forEach(c => { const x = S.reviews[o.order + '_' + c.code]; rv[x ? x.status : 'cho']++; });
  const us = (S.data.jobs || []).filter(j => j.order === o.order && j.usage);
  const usage = us.length ? Object.fromEntries(['costUSD', 'input', 'output', 'thinking', 'cacheRead', 'cacheWrite', 'calls_main', 'calls_sub', 'images', 'denials'].map(k => [k, us.reduce((a, j) => a + (j.usage[k] || 0), 0)])) : null;
  return {label:'Hiện tại', current:true, usage, plan:last.plan, model:last.model, subagents:last.subagents, seconds:Math.round(secs), runs:(o.runs || []).length,
          codes:o.codes.length, done:o.done, flags:o.codes.reduce((a, c) => a + c.flags.length, 0), review:rv, dest:''};
}
function renderCompare(){
  const el = $('#cmp'); if (!el) return;
  const orders = Object.keys(S.compare || {});
  if (!orders.length) { el.innerHTML = ''; return; }
  el.innerHTML = '<h2>So sánh phương án <span class="n">' + orders.length + ' đơn</span></h2>' + orders.map(order => {
    const cols = (S.compare[order] || []).slice();
    const o = S.data.orders.find(x => x.order === order);
    if (o && (o.state === 'xong' || o.state === 'cho') && o.codes.length) cols.push(currentVariant(o));
    const pct = r => (r.review.dung + r.review.sai) ? r.review.dung / (r.review.dung + r.review.sai) * 100 : null;
    const secs = cols.map(r => r.seconds).filter(x => x > 0), best = secs.length > 1 ? Math.min(...secs) : null;
    const costs = cols.filter(r => r.usage).map(r => r.usage.costUSD), bestC = costs.length > 1 ? Math.min(...costs) : null;
    const pcts = cols.map(pct).filter(x => x != null), bestP = pcts.length > 1 ? Math.max(...pcts) : null;
    const td = (r, f, cls) => `<td class="${cls ? cls(r) : ''}">${f(r)}</td>`;
    const row = (name, f, cls) => `<tr><th>${name}</th>${cols.map(r => td(r, f, cls)).join('')}</tr>`;
    return `<div class="panel cmp-p"><div class="cmp-h"><span class="jid">${esc(order)}</span><span class="t3">${cols.length} phương án</span></div>
      <div class="cmp-s"><table class="od-t cmp"><thead><tr><th></th>${cols.map(r => `<th class="${r.current ? 'cur' : ''}">${esc(r.label)}${r.savedAt ? `<div class="t3">${hm(r.savedAt)}</div>` : ''}${r.note ? `<div class="t3" style="font-weight:400;font-size:11.5px;max-width:190px">${esc(r.note)}</div>` : ''}${r.dest ? `<button class="ib" data-cdel="${esc(r.dest)}" data-corder="${esc(order)}" title="Xoá phương án này (gồm cả Output đã lưu)"><svg class="i"><use href="#i-x"/></svg></button>` : ''}</th>`).join('')}</tr></thead><tbody>
        ${row('Phân công', r => esc(planText(r)))}
        ${row('Thời gian làm', r => (r.seconds ? dur(r.seconds * 1000) : '—') + (r.runs > 1 ? ' · ' + r.runs + ' lần chạy' : ''), r => best != null && r.seconds === best ? 'best' : '')}
        ${cols.some(r => r.match) ? row('Khớp đáp án (so DXF)', r => r.match ? esc(r.match) + ' mã' : '—', r => r.match && r.match.split('/')[0] === r.match.split('/')[1] ? 'best' : '') : ''}
        ${row('Chi phí', r => r.usage ? '$' + r.usage.costUSD.toFixed(2) : '—', r => r.usage && bestC != null && r.usage.costUSD === bestC ? 'best' : '')}
        ${row('Token đọc lại (bộ nhớ đệm)', r => r.usage ? (r.usage.cacheRead / 1e6).toFixed(2) + ' triệu' : '—')}
        ${row('Token ra (gồm suy nghĩ)', r => r.usage ? (r.usage.output / 1000).toFixed(0) + ' nghìn (' + (r.usage.thinking / 1000).toFixed(0) + ' nghìn suy nghĩ)' : '—')}
        ${row('Lượt gọi công cụ', r => r.usage ? (r.usage.calls_main + r.usage.calls_sub) + ' (chính ' + r.usage.calls_main + ', phụ ' + r.usage.calls_sub + ')' : '—')}
        ${row('Ảnh đã xem · lệnh bị từ chối quyền', r => r.usage ? r.usage.images + ' · ' + r.usage.denials : '—')}
        ${row('Mã xong', r => r.done + '/' + r.codes)}
        ${row('Flag', r => String(r.flags))}
        ${row('Đúng', r => String(r.review.dung))}
        ${row('Sai', r => String(r.review.sai))}
        ${row('Chờ check', r => String(r.review.cho))}
        ${row('% Đúng', r => pct(r) == null ? '—' : pct(r).toFixed(0) + '%', r => bestP != null && pct(r) === bestP ? 'best' : '')}
        ${row('Thư mục', r => r.dest ? `<span class="mono">AI_Work\\${esc(r.dest)}</span> <button class="ib" data-copy="${esc((S.data.work || 'AI_Work') + '\\' + r.dest)}" title="Copy đường dẫn"><svg class="i"><use href="#i-folder"/></svg></button>` : '<span class="t3">Đang ở thư mục đơn</span>')}
      </tbody></table></div></div>`;
  }).join('');
}

/* ---------- mã đang chờ (Preview/Flag): người dùng chọn tự làm để hoàn tất đơn, không chờ agent ---------- */
function openManual(order, code){
  const o = S.data.orders.find(x => x.order === order), c = o && o.codes.find(x => x.code === code);
  if (!c) return;
  const dir = (S.data.workPath || S.data.work || 'AI_Work') + (o.path ? '\\' + o.path : '');
  S.manual = {order, code};
  const el = $('#pl');
  el.innerHTML = `<div class="pl-h"><span class="jid">${esc(code)}</span><span class="t2">đơn ${esc(order)}</span><span class="sp"></span>
      <button class="ib" data-mx title="Đóng (Esc)"><svg class="i"><use href="#i-x"/></svg></button></div>
    <div class="pl-b">
      ${c.manual ? '<p class="hint ok">Mã này đang được đánh dấu "Người dùng tự làm" (cũ).</p>' : ''}
      ${c.flagsRaw.length ? `<h3>Flag của agent <span class="n">${c.flagsRaw.length}</span></h3><div class="od-flags">${c.flagsRaw.map(f => `<div class="fl"><span>${esc(f)}</span></div>`).join('')}</div>` : ''}
      <p style="margin:14px 0 0;font-size:13.5px;line-height:1.6">${c.manual
        ? 'Bạn có thể hoàn tác để mã này quay lại trạng thái chờ agent.'
        : 'Nếu hình dựng hiện tại của mã <b>' + esc(code) + '</b> đã đúng, bấm <b>Preview OK</b>: mã tính là xong, bỏ Flag, không cần check lại và đóng gói được luôn.'}</p>
    </div>
    <div class="pl-f"><span class="sp"></span><button class="btn btn-sec" data-mx>Đóng</button>
      <button class="btn btn-pri" data-mgo="${c.manual ? '0' : '1'}">${c.manual ? 'Hoàn tác, chờ agent' : 'Preview OK'}</button></div>`;
  el.hidden = false; $('#pl-bg').hidden = false;
}
function closeManual(){ S.manual = null; $('#pl').hidden = true; $('#pl-bg').hidden = true; }
document.addEventListener('click', e => {
  const pv = e.target.closest('[data-pvok]');       // nút Preview OK (hoặc Hoàn tác) trong chi tiết đơn
  if (pv && !S.plan && !S.manual) {
    pv.disabled = true;
    api('/api/previewok', {order:pv.dataset.order, code:pv.dataset.code, ok:pv.dataset.pvok === '1'}).then(() => {
      toast(pv.dataset.pvok === '1' ? 'Preview OK ' + pv.dataset.code + ': mã đã xong' : 'Đã hoàn tác Preview OK ' + pv.dataset.code); load(true);
    }, e2 => { pv.disabled = false; toast(e2.message); });
    return;
  }
  const card = e.target.closest('.jt-code.s-rev, .jt-code.s-man, [data-manual]');
  if (card && !S.plan && !S.manual) {
    const code = card.dataset.code || card.dataset.manual, order = (card.closest('.job') || {dataset:{}}).dataset.id || card.dataset.order;
    if (code && order) return openManual(order, code);
  }
  if (!S.manual) return;
  const b = e.target.closest('#pl button, #pl-bg');
  if (!b) return;
  if (b.id === 'pl-bg' || b.dataset.mx != null) return closeManual();
  if (b.dataset.mgo != null) {
    const {order, code} = S.manual;
    const o0 = S.data.orders.find(x => x.order === order), c0 = (o0 && o0.codes.find(x => x.code === code)) || {};
    b.disabled = true;
    api(c0.manual ? '/api/manual' : '/api/previewok', c0.manual ? {order, code, manual:false} : {order, code, ok:true}).then(() => {
      toast(c0.manual ? 'Đã hoàn tác ' + code : 'Preview OK ' + code + ': mã đã xong'); closeManual(); load(true);
    }, e2 => { b.disabled = false; toast(e2.message); });
  }
});
document.addEventListener('keydown', e => { if (e.key === 'Escape' && S.manual) closeManual(); });

/* ---------- bảng phân công: Giao việc -> chọn agent cho từng mã, model cho từng agent ---------- */
const PA = [['main', 'Agent chính'], ['S1', 'Subagent 1'], ['S2', 'Subagent 2']];
const paName = a => (PA.find(x => x[0] === a) || [a, a])[1];
function openPlan(pv){
  const def = 'sonnet';     // Phát chốt: bảng phân công luôn mặc định Sonnet cho mọi agent
  S.plan ={...pv, agents:{main:def, S1:def, S2:def}, assign:Object.fromEntries(pv.codes.map(c => [c.code, 'main']))};
  renderPlan();
}
function closePlan(){ S.plan = null; $('#pl').hidden = true; $('#pl-bg').hidden = true; }
function renderPlan(){
  const P = S.plan, el = $('#pl');
  if (!P) return closePlan();
  const cnt = a => Object.values(P.assign).filter(x => x === a).length;
  const mSel = a => `<select class="pl-m" data-a="${a}">${['opus', 'sonnet'].map(m => `<option value="${m}" ${P.agents[a] === m ? 'selected' : ''}>${m === 'opus' ? 'Opus' : 'Sonnet'}</option>`).join('')}</select>`;
  const agents = PA.map(([a, nm]) => { const n = cnt(a); return `<div class="pl-ag ${n || a === 'main' ? '' : 'idle'}"><b>${nm}</b>${mSel(a)}<span class="t3">${n} mã</span></div>`; }).join('');
  const aSel = (c, v) => `<select class="pl-a" data-c="${esc(c)}">${PA.map(([a, nm]) => `<option value="${a}" ${v === a ? 'selected' : ''}>${nm}</option>`).join('')}</select>`;
  const rows = P.codes.map(c => `<tr><td class="mono">${esc(c.code)}</td><td class="t2">${c.thick != null ? c.thick + 't' : '—'}</td><td class="t2 mono">${esc(c.size || '—')}</td><td>${aSel(c.code, P.assign[c.code])}</td><td class="t3">${P.agents[P.assign[c.code]] === 'sonnet' ? 'Sonnet' : 'Opus'}</td></tr>`).join('');
  const used = PA.filter(([a]) => a !== 'main' && cnt(a)).length;
  el.innerHTML = `<div class="pl-h"><span class="jid">${esc(P.order || '(chưa rõ số đơn)')}</span><span class="t2">${P.codes.length} mã · ${P.pdf} PDF · ${P.xlsx} xlsx</span>
      <span class="sp"></span><button class="ib" data-plx title="Huỷ (Esc)"><svg class="i"><use href="#i-x"/></svg></button></div>
    <div class="pl-b">
      ${P.dup ? '<p class="hint err">Đơn này đang có trong hàng đợi, giao nữa sẽ bị từ chối.</p>' : ''}
      <h3>Agent và model</h3>
      <div class="pl-ags">${agents}</div>
      ${P.codes.length ? `<div class="pl-tools">
        <span class="t3">Nhanh:</span>
        <button class="btn btn-sec sm" data-plall="main">Tất cả cho Agent chính</button>
        <button class="btn btn-sec sm" data-plsplit="main,S1">Chia đều cho Agent chính và Subagent 1</button>
        <button class="btn btn-sec sm" data-plsplit="main,S1,S2">Chia đều cho Agent chính và 2 Subagent</button>
      </div>
      <h3>Mã bản vẽ <span class="n">${P.codes.length}</span></h3>
      <table class="od-t"><thead><tr><th>Mã</th><th>Dày</th><th>Kích thước</th><th>Agent</th><th>Model</th></tr></thead><tbody>${rows}</tbody></table>`
      : '<div class="empty">Không đọc được danh sách mã (thiếu file 依頼.xlsx). Agent chính sẽ tự đọc PDF và vẽ tất cả các mã với model đã chọn ở trên.</div>'}
    </div>
    <div class="pl-f"><span class="t3">${used ? 'Agent chính điều phối + ' + used + ' subagent chạy song song' : 'Agent chính tự vẽ tất cả'}</span><span class="sp"></span>
      <button class="btn btn-sec" data-plx>Huỷ</button>
      <button class="btn btn-pri" data-plgo ${P.dup ? 'disabled' : ''}><svg class="i"><use href="#i-check"/></svg>Giao việc</button></div>`;
  el.hidden = false; $('#pl-bg').hidden = false;
}
function planSplit(list){    // chia các mã thành các nhóm liền nhau, số mã gần bằng nhau, lần lượt cho từng agent trong list
  const P = S.plan, cs = P.codes.map(c => c.code), k = list.length;
  cs.forEach((c, i) => { P.assign[c] = list[Math.floor(i * k / cs.length)]; });
}
async function planGo(btn){
  const P = S.plan, hint = $('#job-hint');
  const agents = {};
  Object.values(P.assign).concat('main').forEach(a => { agents[a] = P.agents[a]; });
  btn.disabled = true;
  try {
    const r = await api('/api/jobs', {path:P.path, plan:{agents, codes:P.assign}});
    const j = r.job, ag = (j.plan || {}).agents || {};
    LS.set('pw-model', ag.main || 'opus');
    hint.className = 'hint ok';
    const auto = (S.data.runner || {}).cli && (S.data.runner || {}).running !== undefined;
    hint.textContent = `Đã giao đơn ${j.order || '(chưa rõ số đơn)'}: ${P.codes.length} mã, ` +
      Object.entries(ag).map(([a, m]) => paName(a) + ' (' + (m === 'sonnet' ? 'Sonnet' : 'Opus') + ')').join(', ') + '. ' +
      (auto ? 'Agent sẽ tự nhận trong vài giây.' : 'Nói với agent "Xử lý hàng đợi" để chạy.');
    $('#job-path').value = '';
    closePlan(); load(true);
  } catch (err) { btn.disabled = false; toast(err.message); }
}
document.addEventListener('click', e => {
  if (!S.plan) return;
  const b = e.target.closest('#pl button, #pl-bg');
  if (!b) return;
  if (b.id === 'pl-bg' || b.dataset.plx != null) return closePlan();
  if (b.dataset.plall) { Object.keys(S.plan.assign).forEach(c => { S.plan.assign[c] = b.dataset.plall; }); return renderPlan(); }
  if (b.dataset.plsplit) { planSplit(b.dataset.plsplit.split(',')); return renderPlan(); }
  if (b.dataset.plgo != null) return planGo(b);
});
document.addEventListener('change', e => {
  if (!S.plan) return;
  const t = e.target;
  if (t.classList.contains('pl-m')) { S.plan.agents[t.dataset.a] = t.value; renderPlan(); }
  if (t.classList.contains('pl-a')) { S.plan.assign[t.dataset.c] = t.value; renderPlan(); }
});
document.addEventListener('keydown', e => { if (e.key === 'Escape' && S.plan) closePlan(); });

function setTheme(v){
  document.documentElement.dataset.theme = v; LS.set('pw-theme', v);
  document.querySelectorAll('.theme button').forEach(b => b.classList.toggle('on', b.dataset.t === v));
}
setTheme(LS.get('pw-theme', 'system'));
if (!location.hash) location.hash = '#/tien-do';
load();
setInterval(() => { if (!document.hidden) load(); }, 15000);
