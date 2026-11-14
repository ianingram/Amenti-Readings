/* Amenti-Readings/tools/mixer/fetch_voice.js · 13 Nov 2026
   THE OFFLINE MIXER, PART ONE: THE VOICE.
   Opens the real player page, and for every cue asks the engine for exactly
   what it would speak: the same chunker, the same voice, the same style, the
   same /speak request, so every measure comes from the R2 cache and nothing
   is re-rendered. Nothing is played. Each measure's audio is written to disk
   with its rest and rate, and the cue list goes to manifest.json for mix.py.

   usage: node fetch_voice.js <work> <NN> <outdir>
   A cue whose every measure fails is listed under "failed" — that is the
   line that would stall a live reading. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');

(async () => {
  const [work, nn, out] = process.argv.slice(2);
  const dir = path.join(out, 'voice'); fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage();
  /* [RENDER-KEY] With VOICE_RENDER_KEY set (a GitHub secret, on Ian's word),
     /speak may voice lines not yet in the cache. Without it, the cache only. */
  const KEY = process.env.VOICE_RENDER_KEY || '';
  if (KEY) await p.route(/amenti-proxy[^/]*\/speak$/, r => r.continue({ headers: { ...r.request().headers(), 'x-amenti-render': KEY } }));
  const got = {};                                      /* request body -> file */
  const cache = { hit: 0, new: 0 };                   /* X-Amenti-Cache: what was already paid for */
  p.on('response', async (r) => {
    if (!/\/speak$/.test(r.url()) || r.request().method() !== 'POST') return;
    const body = r.request().postData() || '';
    try {
      if (!r.ok()) return;
      if ((r.headers()['x-amenti-cache'] || '') === 'hit') cache.hit++; else cache.new++;
      const buf = await r.body();
      const f = crypto.createHash('sha1').update(body).digest('hex').slice(0, 16) + '.audio';
      fs.writeFileSync(path.join(dir, f), buf);
      got[body] = f;
    } catch (e) {}
  });
  p.on('console', m => { const t = m.text(); if (/warn|error/i.test(m.type())) console.log('[page] ' + t.slice(0, 200)); });
  /* every work plays on the same player; the Dracula page carries it */
  await p.goto(`https://ianingram.github.io/Amenti-Readings/dracula/?road=1`, { waitUntil: 'networkidle' });
  await p.evaluate(() => { try { localStorage.setItem('amenti-art-off', '1'); } catch (e) {} });

  const sheet = `${work}/ep${nn}.json`;
  const plan = await p.evaluate(async (sheet) => {
    const R = Amenti.reading, T = Amenti.throttle;
    await R.load(sheet);
    const cues = R.sheet.cues, rows = [];
    for (let i = 0; i < cues.length; i++) {
      const c = cues[i];
      const row = { i, n: c.n, role: c.role || '', text: c.text };
      for (const k of ['audio', 'through', 'marks', 'sfx', 'score', 'bed', 'state', 'under']) if (c[k] !== undefined) row[k] = c[k];
      if (R._sceneFor(i) && !(c.audio && c.through)) { row.kind = 'covered'; rows.push(row); continue; }
      if (c.audio) { row.kind = c.through ? 'scene' : 'recorded'; rows.push(row); continue; }
      row.kind = 'speak';
      const name = R.nameFor(c), dir = R.direction(c), spoken = R.spoken(c);
      const v = await T.resolveVoice(name).catch(() => null);
      row.cast = name; row.voice = v && v.voice; row.direction = dir || '';
      row.chunks = T.chunk(spoken).map(ch => ({ text: ch.text != null ? ch.text : String(ch), rest: ch.rest || 0, rate: ch.rate || 1 }));
      row.ok = await T.warm(spoken, name, dir);
      rows.push(row);
    }
    return { work: R.sheet.work, episode: R.sheet.episode, chapter: R.sheet.chapter, title: R.sheet.title, cues: rows };
  }, sheet);
  await p.waitForTimeout(1500);

  /* join each measure to the audio captured for it, by its exact text and voice */
  const byText = {};
  for (const body in got) { try { const j = JSON.parse(body); (byText[j.voice + '\n' + j.text] = byText[j.voice + '\n' + j.text] || []).push({ style: j.style, f: got[body] }); } catch (e) {} }
  const failed = [];
  for (const c of plan.cues) {
    if (c.kind !== 'speak') continue;
    let any = false;
    c.chunks.forEach((ch, k) => {
      const hits = byText[c.voice + '\n' + ch.text] || [];
      if (hits.length > 1 && new Set(hits.map(h => h.style)).size > 1) console.log(`cue ${c.n}: measure ${k} has ${hits.length} styles — using the first`);
      ch.file = hits.length ? hits[0].f : null;
      if (ch.file) any = true;
    });
    const miss = c.chunks.filter(ch => !ch.file).length;
    if (!any) failed.push({ n: c.n, role: c.role, why: 'every measure failed', text: c.text.slice(0, 80) });
    else if (miss) console.log(`cue ${c.n}: ${miss} of ${c.chunks.length} measures failed (skipped, as the engine does)`);
  }
  plan.failed = failed;
  fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(plan, null, 1));
  const sp = plan.cues.filter(c => c.kind === 'speak');
  console.log(`${work} ep${nn}: ${plan.cues.length} cues, ${sp.length} spoken, ${sp.reduce((a, c) => a + c.chunks.length, 0)} measures, ` +
              `${plan.cues.filter(c => c.kind === 'recorded' || c.kind === 'scene').length} recorded; failed: ${failed.length ? failed.map(f => f.n).join(', ') : 'none'}; ` +
              `voice: ${cache.hit} from the cache, ${cache.new} newly voiced`);
  plan.voice = cache;
  await b.close();
})();
