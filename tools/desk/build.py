"""Prompt Desk: every Midjourney prompt with a Copy button that marks it copied (artifact db
collection `copied`, doc id = tag), and Claude marks arrivals (doc field `arrived`).
usage: python3 build.py prompts.json out.html"""
import json, sys, html
src, out = sys.argv[1], sys.argv[2]
D = json.load(open(src))
page = r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prompt Desk</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Spectral:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* VOICE: a quiet working desk. IDEA: a printer's job ticket rack — one slip per prompt, stamped when it is pulled.
   PICTURE: the slips themselves; the stamp is the state. COLOUR: paper, ink, a red stamp for copied, green for arrived.
   TYPE: IM Fell for heads, Spectral for prompt text, Plex Mono for tags. LAYOUT: one column of slips, batch headings, a filter bar. */
:root{color-scheme:light dark;--bg:light-dark(#f2ece0,#14110d);--slip:light-dark(#fbf8f1,#1d1914);--ink:light-dark(#22190f,#ece3d3);--dim:light-dark(#6d6253,#a2967f);
--rule:light-dark(#ddd3c2,#332c22);--red:light-dark(#a32a22,#e0685e);--green:light-dark(#2f6b3a,#7fc28c);--gold:light-dark(#8a6408,#d4a017)}
:root[data-theme=light]{color-scheme:light}:root[data-theme=dark]{color-scheme:dark}
*{box-sizing:border-box;min-width:0}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Spectral,Georgia,serif;overflow-x:clip}
.wrap{max-width:900px;margin:0 auto;padding:clamp(18px,3vw,40px) max(4vw,14px) 60px}
h1{font:400 clamp(30px,5vw,44px)/1.05 "IM Fell English",Georgia,serif;margin:0 0 4px}
.sub{color:var(--dim);margin:0 0 18px}
.bar{position:sticky;top:0;z-index:3;background:var(--bg);display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 0;border-bottom:1px solid var(--rule);margin-bottom:10px}
.bar button{font:500 13px "IBM Plex Mono",monospace;min-height:40px;padding:0 14px;border:1px solid var(--rule);background:var(--slip);color:var(--ink);border-radius:4px;cursor:pointer}
.bar button[aria-pressed=true]{border-color:var(--ink);background:var(--ink);color:var(--bg)}
.count{font:13px "IBM Plex Mono",monospace;color:var(--dim);margin-left:auto}
h2{font:400 24px/1.2 "IM Fell English",Georgia,serif;margin:28px 0 8px}
h2 small{display:block;font:13px Spectral,serif;color:var(--dim);margin-top:2px}
.slip{background:var(--slip);border:1px solid var(--rule);border-radius:6px;padding:14px 16px;margin:10px 0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 14px;align-items:start}
.slip.done{opacity:.62}
.tag{font:500 14px "IBM Plex Mono",monospace;color:var(--gold)}
.where{font-size:14px;color:var(--dim);grid-column:1/-1}
.text{grid-column:1/-1;font-size:15px;background:light-dark(#f4efe4,#16130f);border:1px dashed var(--rule);border-radius:4px;padding:10px 12px;overflow-wrap:anywhere}
.copy{font:600 14px Spectral,serif;min-height:44px;min-width:110px;padding:0 16px;border-radius:4px;border:1px solid var(--ink);background:var(--ink);color:var(--bg);cursor:pointer}
.copy:focus-visible,.bar button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.stamps{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:8px;min-height:24px}
.st{font:500 12px "IBM Plex Mono",monospace;letter-spacing:.04em;padding:3px 8px;border:2px solid;border-radius:3px;transform:rotate(-1.5deg)}
.st.c{color:var(--red);border-color:var(--red)}.st.a{color:var(--green);border-color:var(--green)}
.undo{font:12px "IBM Plex Mono",monospace;background:none;border:0;color:var(--dim);text-decoration:underline;cursor:pointer;min-height:24px}
.status{font:12px "IBM Plex Mono",monospace;color:var(--dim)}
.empty{color:var(--dim);padding:20px 0}
@media(max-width:600px){.slip{grid-template-columns:minmax(0,1fr)}.copy{width:100%}}
</style></head><body><div class="wrap">
<h1>Prompt Desk</h1>
<p class="sub">Press Copy, paste into Midjourney. The slip is stamped <b>Copied</b> with the time, on every device. Claude stamps <b>Arrived</b> when the takes reach the Door.</p>
<div class="bar"><button data-f="todo" aria-pressed="true">Not yet copied</button><button data-f="all" aria-pressed="false">All</button><button data-f="wait" aria-pressed="false">Copied, not arrived</button><span class="count" id="count"></span></div>
<div class="status" id="status">Stamps: connecting…</div>
<div id="list"></div></div>
<script>
{
const D=__DATA__;
let marks={},db=null,filt='todo';
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const when=t=>{try{const d=new Date(t);return d.toLocaleDateString([], {month:'short',day:'numeric'})+' '+d.toLocaleTimeString([], {hour:'numeric',minute:'2-digit'})}catch(e){return ''}};
function render(){
  let shown=0,total=0,copied=0;
  const html=D.batches.map(b=>{
    const rows=b.prompts.map(p=>{
      total++; const m=marks[p.tag]||{}; if(m.copied)copied++;
      if(filt==='todo'&&m.copied)return ''; if(filt==='wait'&&!(m.copied&&!m.arrived))return '';
      shown++;
      return `<div class="slip${m.copied?' done':''}"><div><div class="tag">${esc(p.tag)}</div></div>
        <button class="copy" data-tag="${esc(p.tag)}">${m.copied?'Copy again':'Copy'}</button>
        <div class="where">${esc(p.where)}</div><div class="text">${esc(p.text)}</div>
        <div class="stamps">${m.copied?`<span class="st c">COPIED · ${esc(when(m.copied))}</span><button class="undo" data-undo="${esc(p.tag)}">unmark</button>`:''}${m.arrived?`<span class="st a">ARRIVED · ${esc(when(m.arrived))}</span>`:''}</div></div>`;}).join('');
    return rows?`<h2>${esc(b.title)}<small>${esc(b.note||'')}</small></h2>${rows}`:'';}).join('');
  $('#list').innerHTML=html||`<div class="empty">${filt==='todo'?'Every prompt here has been copied.':'Nothing here.'}</div>`;
  $('#count').textContent=copied+' of '+total+' copied';
}
async function stamp(tag,on){
  const m=Object.assign({},marks[tag]||{}); if(on)m.copied=Date.now(); else delete m.copied;
  marks[tag]=m; render();
  if(db){try{await db.doc('copied/'+tag).set(m)}catch(e){$('#status').textContent='Stamp not saved — '+(e&&e.code||'error')}}
}
document.addEventListener('click',async e=>{
  const c=e.target.closest('.copy'); const u=e.target.closest('.undo');
  if(c){const p=D.batches.flatMap(b=>b.prompts).find(x=>x.tag===c.dataset.tag);
    try{await navigator.clipboard.writeText(p.text);c.textContent='Copied ✓'}catch(err){c.textContent='Select the text'}
    stamp(p.tag,true);}
  if(u)stamp(u.dataset.undo,false);
});
document.querySelectorAll('.bar button').forEach(b=>b.onclick=()=>{filt=b.dataset.f;document.querySelectorAll('.bar button').forEach(x=>x.setAttribute('aria-pressed',x===b));render();});
render();
(async()=>{try{const d=window.claude&&await window.claude.use('db');
  if(!d){$('#status').textContent='Stamps save only on the desk’s own page.';return}
  d.collection('copied').onSnapshot(s=>{const f={};s.docs.forEach(x=>f[x.id]=x.data()||{});db=d;marks=f;$('#status').textContent='Stamps save as you copy';render();},
    e=>{$('#status').textContent='Stamps could not load'});
}catch(e){$('#status').textContent='Stamps could not load'}})();
}
</script></body></html>'''
open(out, 'w').write(page.replace('__DATA__', json.dumps(D, ensure_ascii=False)))
print('wrote', out)
