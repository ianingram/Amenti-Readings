// Short tails: chunk every cue with the live engine (spoken text as reader.js gives it)
// and list pieces under 25 characters. usage: node tails.js <bundle> <ep dir>
const fs = require('fs'), vm = require('vm');
const win = { location: { href: 'https://ianingram.github.io/x/' }, addEventListener() {}, document: null, navigator: { userAgent: 'node' }, localStorage: { getItem() { return null; }, setItem() {} } };
const doc = { currentScript: { src: 'https://ianingram.github.io/Amenti.live/amenti-core.bundle.js' }, querySelector() { return null; }, querySelectorAll() { return []; }, addEventListener() {}, createElement() { return { style: {}, setAttribute() {}, appendChild() {}, addEventListener() {} }; }, head: { appendChild() {} }, body: { appendChild() {} } };
win.document = doc; win.window = win;
const ctx = vm.createContext({ window: win, document: doc, navigator: win.navigator, localStorage: win.localStorage, console, setTimeout, clearTimeout, fetch: () => Promise.reject('no'), Promise, URL });
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);
const T = win.Amenti && win.Amenti.throttle; if (!T || !T.chunk) { console.error('no chunk', Object.keys(win.Amenti || {})); process.exit(1); }
const out = [];
for (let ch = 1; ch <= 45; ch++) {
  const d = JSON.parse(fs.readFileSync(process.argv[3] + '/ep' + String(ch).padStart(2, '0') + '.json'));
  for (const c of d.cues) {
    const spoken = String(c.text).replace(/\s*\n+\s*/g, ' ').trim();
    const pieces = T.chunk(spoken).map(p => p.text || p);
    pieces.forEach((p, i) => { if (p.length < 25 && pieces.length > 1) out.push([ch, c.n, i, pieces.length, c.role, p]); });
  }
}
console.log(out.length, 'short pieces inside multi-piece cues');
out.forEach(o => console.log(o.join(' | ')));
