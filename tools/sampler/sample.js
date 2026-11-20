// Base-voice sampler · 14 Nov 2026. For each line: the figure's style from the live
// engine (names.csv on Pages), the proposed base voice, rendered once with
// /speak?probe=1 (nothing cached), saved as NN.<ext>. usage: node sample.js <sheet> <outdir>
const fs = require('fs'), path = require('path'); const { chromium } = require('playwright');
const [sheetPath, out] = process.argv.slice(2); const sheet = JSON.parse(fs.readFileSync(sheetPath, 'utf8'));
const KEY = process.env.VOICE_RENDER_KEY || ''; fs.mkdirSync(out, { recursive: true });
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('https://ianingram.github.io/Amenti-Readings/dracula/?road=1', { waitUntil: 'networkidle' });
  const styles = await p.evaluate(async (names) => {
    const T = Amenti.throttle, o = {};
    for (const n of names) { const v = await T.resolveVoice(n); o[n] = { voice: v.voice, style: v.style, found: !!v.figure }; }
    return o;
  }, sheet.lines.map(l => l[1]));
  const log = [];
  for (let i = 0; i < sheet.lines.length; i++) {
    const [role, fig, voice, text] = sheet.lines[i]; const s = styles[fig];
    let ok = false, info = '';
    for (const wait of [0, 20, 60, 120]) {
      if (wait) await new Promise(r => setTimeout(r, wait * 1000));
      let r, ct, buf;   /* 19 Nov 2026: a dropped connection (ECONNRESET) used to end the whole run; now it is one more try */
      try {
        r = await fetch('https://amenti-proxy.ingram-ian.workers.dev/speak?probe=1' + (sheet.route ? '&route=' + sheet.route : ''), { method: 'POST',   /* 19 Nov: optional sheet.route (studio|vertex) for calibration probes */
          headers: { 'Content-Type': 'application/json', 'Origin': 'https://ianingram.github.io', 'x-amenti-render': KEY },
          body: JSON.stringify(Object.assign({ text, style: s.style, voice }, sheet.model ? { model: sheet.model } : {})) });
        ct = r.headers.get('content-type') || ''; buf = Buffer.from(await r.arrayBuffer());
      } catch (e) { info = 'network ' + (e.cause && e.cause.code || e.message); continue; }
      if (r.ok && !ct.includes('json')) { const ext = ct.includes('wav') ? 'wav' : ct.includes('mpeg') ? 'mp3' : ct.includes('ogg') ? 'ogg' : 'bin';
        fs.writeFileSync(path.join(out, String(i + 1).padStart(2, '0') + '.' + ext), buf); ok = true; info = ct + ' ' + buf.length + ' bytes, route ' + r.headers.get('x-amenti-route'); break; }
      info = r.status + ' ' + buf.toString().slice(0, 160);
    }
    console.log((i + 1) + '. ' + role + ' (' + fig + ', ' + voice + (s.found ? '' : ', NOT IN LEDGER') + '): ' + (ok ? 'ok' : 'FAILED') + ' ' + info);
    log.push({ n: i + 1, role, figure: fig, voice, ok, style: s.style });
  }
  fs.writeFileSync(path.join(out, 'sampler.json'), JSON.stringify(log, null, 1)); await b.close();
})();
