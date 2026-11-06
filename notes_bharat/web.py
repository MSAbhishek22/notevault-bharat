"""Web UI for NoteVault Bharat — stdlib only, localhost only.

A judge cannot click a CLI, so this is the demo surface. It adds no
new intelligence: every answer still goes through NotesAgent, with
the same local search, the same grounded-refusal rule, and the same
routing + budget panel. The UI is the thing that *shows* the
BharatCode call; it does not invent it.

The 3D note galaxy (canvas, perspective projection, no dependency)
is the spatial view of the vault: notes are stars, tags are
constellations. Drag to rotate, click a star to open its note. The
plain notes list below it is the always-available 2D fallback —
every galaxy action is doable from the list, keyboard included.

Run:  python3 run.py serve            (http://127.0.0.1:8769/)
      python3 run.py serve --port 8000

Binds 127.0.0.1 by default. Never pass --host 0.0.0.0 for a demo
unless you understand that your notes folder becomes reachable
on the local network. No token, key, or note body is ever logged.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .agent import NotesAgent

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NoteVault Bharat — Apne notes se poochho, apni bhasha mein</title>
<style>
:root{
  --ink:#1b2a4a; --ink-deep:#101a30; --marigold:#f0a13a; --marigold-deep:#d98200;
  --paper:#fdf6e9; --card:#fffdf6; --text:#1e2430; --muted:#5c6470;
  --line:#e5dcc4; --ok-bg:#dcefd8; --ok-text:#145214; --mock-bg:#ffe8c2; --mock-text:#7a3e00;
  --err:#b00020; --err-bg:#fff0f0; --chip-bg:#fdeecf;
}
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",sans-serif;margin:0;color:var(--text);background:var(--paper)}
.hero{background:linear-gradient(180deg,var(--ink-deep),var(--ink) 70%,#24365e);color:#fdf6e9;padding:34px 20px 26px;text-align:center}
.hero h1{font-family:Georgia,"Times New Roman",serif;font-size:2.1em;margin:0;letter-spacing:.5px}
.hero h1 .star{color:var(--marigold)}
.hero p{margin:8px auto 0;max-width:640px;line-height:1.5;color:#e8e0cc}
.hero .hindi{font-size:1.15em;color:var(--marigold)}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px 40px}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-weight:700;font-size:.85em}
.mock{background:var(--mock-bg);color:var(--mock-text)}.real{background:var(--ok-bg);color:var(--ok-text)}
.modebar{margin:16px 0 0;text-align:center;color:var(--muted)}
.galaxy-card{margin-top:18px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--ink-deep)}
.galaxy-card h2{margin:0;padding:12px 16px 0;color:#fdf6e9;font-family:Georgia,serif;font-size:1.15em}
.galaxy-card p{margin:4px 16px 0;color:#b9c2d4;font-size:.9em}
#galaxy{display:block;width:100%;height:300px;cursor:grab;touch-action:none}
#galaxy:active{cursor:grabbing}
#galaxy:focus-visible{outline:3px solid var(--marigold);outline-offset:-3px}
.grid{display:grid;grid-template-columns:1.5fr 1fr;gap:16px;margin-top:16px}
@media(max-width:820px){.grid{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:16px;padding:16px;background:var(--card)}
.card h3{margin-top:0;font-family:Georgia,serif;color:var(--ink)}
button{padding:9px 15px;border-radius:10px;border:1px solid var(--ink);background:var(--ink);color:#fff;cursor:pointer;font-weight:600;margin:2px 4px 2px 0}
button:hover{background:#263a66}
button.secondary{background:#fff;color:var(--ink)}
button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--marigold);outline-offset:2px}
input,select{width:100%;padding:10px;border:1px solid #c9c2a8;border-radius:10px;box-sizing:border-box;background:#fff;font:inherit}
label{display:block;margin:10px 0 4px;font-weight:600;color:var(--ink)}
.meter{height:14px;background:#eee3c8;border-radius:999px;overflow:hidden}.meter>div{height:100%;background:var(--marigold-deep)}
.chip{display:inline-block;background:var(--chip-bg);border:1px solid #ecd9a8;border-radius:999px;padding:2px 9px;margin:2px;font-size:.85em}
.refusal{border:2px solid var(--err);background:var(--err-bg);padding:10px;border-radius:10px}
pre{white-space:pre-wrap;word-wrap:break-word;background:#f7efdb;padding:10px;border-radius:10px;font-family:inherit}
.note-item{cursor:pointer;padding:7px 8px;border-radius:8px;border:1px solid transparent}
.note-item:hover,.note-item:focus-visible{background:var(--chip-bg);border-color:#ecd9a8;outline:none}
small{color:var(--muted)}
.kv{line-height:1.7}
footer{margin-top:24px;text-align:center;color:var(--muted);font-size:.9em}
</style></head><body>
<header class="hero">
<h1>NoteVault <span class="star">✦</span> Bharat</h1>
<p class="hindi">अपने notes से पूछो, अपनी भाषा में।</p>
<p><b>Ask your notes, in your language — answered by BharatCode.</b>
Your notes stay local. Only the few excerpts that match your question go to the
BharatCode model API — and only when you ask. Every answer shows its route, its
model, and its budget.</p>
</header>
<div class="wrap">
<div class="modebar"><span id="modebadge" class="badge mock">[mock]</span> <span id="modeline"></span></div>

<div class="galaxy-card">
<h2>✦ Your notes, as a constellation</h2>
<p>Each star is a note; stars that share a tag form a constellation. Drag to spin the sky,
click a star to read its note. The list below works the same way — no mouse needed.</p>
<canvas id="galaxy" width="1000" height="300" tabindex="0"
  aria-label="Note constellation. Use left and right arrow keys to rotate, Enter to open the highlighted note."></canvas>
</div>

<div class="grid">
<div>
<div class="card"><h3>Ask your notes</h3>
<label for="q">Question</label>
<input id="q" placeholder="What is Abhiverse for?">
<label for="lang">Answer language</label>
<select id="lang">
<option value="en">English</option>
<option value="hi">हिन्दी (Hindi)</option>
<option value="hinglish">Hinglish</option>
</select>
<label for="model">Model (BharatCode)</label>
<select id="model">
<option value="">Default (from configuration)</option>
<option value="qwen-3.8-27b">qwen-3.8-27b — default, free for students</option>
<option value="deepseek-v4.1-flash">deepseek-v4.1-flash — fallback</option>
</select>
<label for="customModel">…or a custom BharatCode model id</label>
<input id="customModel" placeholder="qwen-3.8-27b">
<br><br>
<button onclick="ask()">Ask ✦</button>
<button class="secondary" onclick="askPreset('What is Abhiverse for?')">Try: Abhiverse</button>
<button class="secondary" onclick="askPreset('quantum bananas')">Try: refusal</button>
<div id="answer" style="margin-top:14px"></div>
<h3>Organise plan <small>(plan only — no files are changed)</small></h3>
<button onclick="organise()">Show plan</button><pre id="plan"></pre></div>

<div class="card" style="margin-top:16px"><h3>Your notes</h3><div id="notes">Loading…</div>
<h3>Note preview</h3><pre id="preview">Click a note — or a star above.</pre></div>
</div>

<div>
<div class="card"><h3>Routing — via BharatCode</h3><div id="routing">Ask a question to see the route.</div>
<h3>Budget</h3><div id="budget"></div>
<p><small>BharatCode-side usage lives in your BharatCode account (students: Qwen free
up to 10M tokens a day, per bharatcode.ai) and is not visible from this app. The meter
above is the local session budget only.</small></p>
<button onclick="resetBudget()">Reset demo budget</button>
<p><small>Notes never leave this machine except the few excerpts sent to BharatCode,
and only when you ask.</small></p></div>
</div>
</div>
<footer>NoteVault Bharat · Built for the BharatCode Build League · Public repo must contain <code>BharatCode.txt</code> at its root.</footer>
</div>
<script>
let NOTES = [];
let GALAXY = [];
let rotY = 0.6, rotX = 0.15, autoSpin = true, selected = 0;
const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reduced) autoSpin = false;

async function api(path, body){
  const r = await fetch(path, {method: body ? 'POST' : 'GET',
    headers:{'Content-Type':'application/json'}, body: body ? JSON.stringify(body) : undefined});
  const j = await r.json(); if(!r.ok) throw new Error(j.error || ('HTTP '+r.status)); return j;
}
function hashStr(s){ let h=2166136261; for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619); } return h>>>0; }
function tagColor(tag){
  const palette = ['#f0a13a','#7fd1c0','#e78fb3','#a5d6a7','#90caf9','#ffcc80'];
  return palette[hashStr(tag) % palette.length];
}
function buildGalaxy(notes){
  GALAXY = notes.map(function(n, i){
    const tag = (n.tags && n.tags[0]) || 'untagged';
    const h = hashStr(n.rel_path) / 4294967295;
    const th = hashStr(tag) / 4294967295;
    const phi = th * Math.PI * 2 + (h - 0.5) * 0.9;      // tag = constellation sector
    const theta = (h * 2.2 - 0.4) + (i % 3) * 0.25;       // spread inside the sector
    const r = 150 + (hashStr(n.rel_path + 'r') % 90);
    return {note: n, tag: tag, color: tagColor(tag),
      x: r * Math.sin(theta) * Math.cos(phi), y: r * (Math.cos(theta) - 0.55) * 0.7, z: r * Math.sin(theta) * Math.sin(phi)};
  });
  drawGalaxy();
}
function drawGalaxy(){
  const cv = document.getElementById('galaxy');
  if(!cv || !cv.getContext) return;
  const ctx = cv.getContext('2d');
  const W = cv.width, H = cv.height, cx = W/2, cy = H/2, f = 420;
  ctx.fillStyle = '#101a30'; ctx.fillRect(0,0,W,H);
  // faint background stars
  ctx.fillStyle = 'rgba(253,246,233,0.35)';
  for(let i=0;i<70;i++){ const sx=(hashStr('bg'+i)%W), sy=(hashStr('bg'+i+'y')%H); ctx.fillRect(sx,sy,1.4,1.4); }
  const cosY=Math.cos(rotY), sinY=Math.sin(rotY), cosX=Math.cos(rotX), sinX=Math.sin(rotX);
  const pts = GALAXY.map(function(g, i){
    let x=g.x, y=g.y, z=g.z;
    let x1 = x*cosY + z*sinY, z1 = -x*sinY + z*cosY;
    let y1 = y*cosX - z1*sinX, z2 = y*sinX + z1*cosX;
    const s = f/(f+z2+260);
    return {i:i, g:g, sx: cx + x1*s, sy: cy + y1*s, s:s, z:z2};
  }).sort(function(a,b){ return a.z - b.z; });
  // constellation lines: same tag, projected
  const byTag = {};
  pts.forEach(function(p){ (byTag[p.g.tag] = byTag[p.g.tag] || []).push(p); });
  ctx.lineWidth = 1;
  Object.keys(byTag).forEach(function(tag){
    const arr = byTag[tag];
    if(arr.length < 2) return;
    ctx.strokeStyle = 'rgba(240,161,58,0.35)';
    ctx.beginPath();
    arr.forEach(function(p, k){ if(k===0) ctx.moveTo(p.sx,p.sy); else ctx.lineTo(p.sx,p.sy); });
    ctx.stroke();
  });
  pts.forEach(function(p){
    const rad = Math.max(3, 7 * p.s);
    ctx.beginPath(); ctx.arc(p.sx, p.sy, rad, 0, Math.PI*2);
    ctx.fillStyle = p.g.color; ctx.globalAlpha = 0.55 + 0.45 * Math.min(1, p.s);
    ctx.fill(); ctx.globalAlpha = 1;
    if(p.i === selected){
      ctx.beginPath(); ctx.arc(p.sx, p.sy, rad+5, 0, Math.PI*2);
      ctx.strokeStyle = '#fdf6e9'; ctx.lineWidth = 2; ctx.stroke();
    }
    ctx.fillStyle = '#fdf6e9'; ctx.font = '12px system-ui, sans-serif';
    ctx.fillText(p.g.note.title.slice(0, 22), p.sx + rad + 4, p.sy + 4);
  });
  const sel = GALAXY[selected];
  if(sel){ ctx.fillStyle = '#b9c2d4'; ctx.font = '13px system-ui, sans-serif';
    ctx.fillText('Selected: ' + sel.note.title + '  (#' + sel.tag + ') — Enter or click to open', 12, H - 12); }
}
function galaxyHit(mx, my){
  const cv = document.getElementById('galaxy');
  const rect = cv.getBoundingClientRect();
  const x = (mx - rect.left) * (cv.width / rect.width), y = (my - rect.top) * (cv.height / rect.height);
  let best = -1, bestD = 26;
  const cosY=Math.cos(rotY), sinY=Math.sin(rotY), cosX=Math.cos(rotX), sinX=Math.sin(rotX);
  GALAXY.forEach(function(g, i){
    let x1 = g.x*cosY + g.z*sinY, z1 = -g.x*sinY + g.z*cosY;
    let y1 = g.y*cosX - z1*sinX, z2 = g.y*sinX + z1*cosX;
    const s = 420/(420+z2+260);
    const sx = cv.width/2 + x1*s, sy = cv.height/2 + y1*s;
    const d = Math.hypot(sx - x, sy - y);
    if(d < bestD){ bestD = d; best = i; }
  });
  return best;
}
async function load(){
  const s = await api('/api/status');
  document.getElementById('modebadge').textContent = s.mode_label;
  document.getElementById('modebadge').className = 'badge ' + (s.mode === 'mock' ? 'mock' : 'real');
  document.getElementById('modeline').textContent =
    'BharatCode API: ' + s.gateway + ' · Default model: ' + s.model + (s.fallback_model ? ' · Fallback: ' + s.fallback_model : ' · No fallback configured');
  NOTES = s.notes || [];
  document.getElementById('notes').innerHTML = NOTES.map(function(n, i){
    return '<div class="note-item" tabindex="0" role="button" onclick="showNote(' + i + ')" onkeydown="if(event.key===\\'Enter\\')showNote(' + i + ')">📄 ' + n.title +
    ' <small>(' + n.word_count + ' words' + (n.tags.length ? ', #' + n.tags.join(' #') : '') + ')</small></div>';
  }).join('') || 'No notes found.';
  document.getElementById('lang').value = s.language || 'en';
  buildGalaxy(NOTES);
  renderBudget(s.budget);
  if(autoSpin && !reduced){ setInterval(function(){ rotY += 0.004; drawGalaxy(); }, 50); }
}
function renderBudget(b){
  document.getElementById('budget').innerHTML =
    '<div class="meter"><div style="width:' + b.percent_used + '%"></div></div>' +
    '<p><b>' + b.used + ' / ' + b.limit + ' calls used</b> · ' + b.remaining + ' remaining' +
    (b.exhausted ? ' · <b>Budget exhausted</b>' : '') + '</p>';
}
function renderRouting(r){
  if(r.refused_before_routing) return '<p><b>No API call made.</b><br>Refused before routing — no matching notes, so no model was called and no budget was used.</p>';
  const c = r.chosen;
  return '<p class="kv"><b>API:</b> ' + r.gateway + '<br><b>Mode:</b> ' + r.mode_label +
    '<br><b>Chosen:</b> ' + (c ? c.provider + ' / ' + c.model : '—') + '<br><b>Why:</b> ' + (c ? c.reason : '—') +
    '<br><b>Fallback chain:</b> ' + (r.fallback_chain.length ? r.fallback_chain.map(function(f){ return f.provider + ' / ' + f.model; }).join(', ') : 'none configured') +
    '<br><b>Attempted:</b> ' + (r.attempted.length ? r.attempted.join(' → ') : 'none') +
    (r.fallback_used ? '<br><b>⚠ Fallback was used</b> (primary failed)' : '') + '</p>';
}
async function askPreset(t){ document.getElementById('q').value = t; await ask(); }
async function ask(){
  const q = document.getElementById('q').value.trim();
  const lang = document.getElementById('lang').value;
  const model = document.getElementById('customModel').value.trim() || document.getElementById('model').value || null;
  if(!q){ alert('Type a question first.'); return; }
  document.getElementById('answer').innerHTML = 'Asking BharatCode…';
  try{
    const r = await api('/api/ask', {question: q, model: model, language: lang});
    const ans = document.getElementById('answer');
    ans.innerHTML = (r.refused ? '<div class="refusal"><b>Refused — no guess.</b></div>' : '') +
      '<pre>' + r.answer.replace(/</g, '&lt;') + '</pre>' +
      '<div>' + r.sources.map(function(s){ return '<span class="chip">📄 ' + s.title + '</span>'; }).join('') + '</div>' +
      '<p><span class="badge ' + (r.mode === 'mock' ? 'mock' : 'real') + '">' + (r.mode === 'mock' ? '[mock] offline stand-in' : 'real BharatCode') + '</span> ' +
      '<span class="chip">🌐 ' + (r.language || lang) + '</span></p>';
    document.getElementById('routing').innerHTML = renderRouting(r.routing);
    renderBudget(r.budget);
  }catch(e){ document.getElementById('answer').innerHTML = '<div class="refusal">Error: ' + e.message.replace(/</g, '&lt;') + '</div>'; }
}
async function organise(){ document.getElementById('plan').textContent = (await api('/api/organise', {})).plan; }
async function showNote(i){
  const n = NOTES[i]; if(!n) return;
  selected = i; drawGalaxy();
  const full = await api('/api/note?path=' + encodeURIComponent(n.rel_path));
  document.getElementById('preview').textContent = full.title + '\\n\\n' + full.body;
}
async function resetBudget(){ await api('/api/reset-budget', {}); await load(); }
(function(){
  const cv = document.getElementById('galaxy');
  let dragging = false, lastX = 0, lastY = 0;
  cv.addEventListener('pointerdown', function(e){ dragging = true; lastX = e.clientX; lastY = e.clientY; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener('pointermove', function(e){
    if(!dragging) return;
    rotY += (e.clientX - lastX) * 0.005; rotX += (e.clientY - lastY) * 0.003;
    rotX = Math.max(-0.6, Math.min(0.6, rotX));
    lastX = e.clientX; lastY = e.clientY; drawGalaxy();
  });
  cv.addEventListener('pointerup', function(e){ dragging = false; const hit = galaxyHit(e.clientX, e.clientY); if(hit >= 0) showNote(hit); });
  cv.addEventListener('keydown', function(e){
    if(e.key === 'ArrowLeft'){ rotY -= 0.12; drawGalaxy(); e.preventDefault(); }
    if(e.key === 'ArrowRight'){ rotY += 0.12; drawGalaxy(); e.preventDefault(); }
    if(e.key === 'Enter'){ showNote(selected); e.preventDefault(); }
    if(e.key === 'Tab' && e.shiftKey === false){ /* let focus move to the notes list */ }
  });
})();
load();
</script></body></html>
"""


def _json(handler: BaseHTTPRequestHandler, obj: dict, status: int = 200) -> None:
    data = json.dumps(obj).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class NoteVaultBharatHandler(BaseHTTPRequestHandler):
    agent: NotesAgent  # set on the server instance

    def log_message(self, *args) -> None:  # never log bodies / keys
        pass

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > 64_000:
            raise ValueError("Request too large")
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8")) if raw.strip() else {}

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        agent = self.server.agent  # type: ignore[attr-defined]
        if parsed.path == "/":
            data = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parsed.path == "/api/status":
            _json(self, agent.status_dict())
            return
        if parsed.path == "/api/note":
            rel = parse_qs(parsed.query).get("path", [""])[0]
            try:
                note = agent.get_note(rel)
            except (FileNotFoundError, ValueError) as exc:
                _json(self, {"error": str(exc)}, status=404)
                return
            _json(self, {"title": note.title, "rel_path": note.rel_path, "tags": note.tags, "body": note.body[:8000]})
            return
        _json(self, {"error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        agent = self.server.agent  # type: ignore[attr-defined]
        try:
            body = self._read_json()
        except (ValueError, json.JSONDecodeError) as exc:
            _json(self, {"error": str(exc)}, status=400)
            return
        try:
            if parsed.path == "/api/ask":
                question = str(body.get("question") or "").strip()
                if not question:
                    _json(self, {"error": "question is required"}, status=400)
                    return
                model = body.get("model") or None
                language = body.get("language") or None
                result = agent.ask_detailed(question, model=model, language=language)
                _json(self, result.to_dict())
                return
            if parsed.path == "/api/organise":
                _json(self, {"plan": agent.organise_plan()})
                return
            if parsed.path == "/api/reset-budget":
                agent.reset_budget()
                _json(self, {"budget": agent.budget.to_dict()})
                return
        except (ValueError, RuntimeError) as exc:
            # ValueError: bad model id / language / path. RuntimeError:
            # budget, provider failure. Never include key values: these
            # messages come from our own code, not env.
            _json(self, {"error": str(exc)}, status=400)
            return
        _json(self, {"error": "Not found"}, status=404)


def make_server(agent: NotesAgent, host: str = "127.0.0.1", port: int = 8769) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), NoteVaultBharatHandler)
    server.agent = agent  # type: ignore[attr-defined]
    return server


def serve(agent: NotesAgent, host: str = "127.0.0.1", port: int = 8769) -> int:
    server = make_server(agent, host=host, port=port)
    print(f"NoteVault Bharat web UI: http://{host}:{port}/  (localhost only unless --host is changed)")
    print("Mode:", agent.mode, "| BharatCode API:", agent.config.gateway_label, "| model:", agent.config.model)
    print("Press Ctrl-C to stop. Notes are read locally; excerpts go to BharatCode only when you ask.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0
