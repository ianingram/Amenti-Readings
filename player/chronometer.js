/* Amenti-Readings/player/chronometer.js · 25 Oct 2026 ─────────────────────────
   THE CHRONOMETER IN THE READING. A small emblem in the lower-left corner of a
   Dracula reading; tap it and the Chronometer (dracula/dossier/chronometer.html)
   opens beside the text and turns with the voice.

   IT DOES NOT TOUCH THE VOICE PATH. It only reads what the reader already
   publishes — Amenti.reading.sheet.episode and Amenti.reading.cue.n — on a
   gentle interval, and posts {type:'amenti-cue', ep, n} to the Chronometer.

   AND IT CAN BE STEERED FROM THE DIAL. When the reader taps a chapter or a date
   on the Chronometer, it posts {type:'amenti-jump', ep, n} here:
     · a page that runs its own chapter chain (the Book pages) defines
       window.amentiChronoJump(ep, n) and keeps its cards and endings in order;
     · otherwise the same chapter seeks (Amenti.reading.seek), and another
       chapter is loaded and then sought.

   Load after reader.js:   <script src="…/player/chronometer.js"></script>
   ─────────────────────────────────────────────────────────────────────────── */
(function () {
  'use strict';
  var SRC = 'https://ianingram.github.io/Amenti-Readings/dracula/dossier/chronometer.html?embed=1';
  var R = window.Amenti && window.Amenti.reading;
  if (!R) { console.warn('chronometer.js: Amenti.reading not found — load reader.js first.'); return; }

  var css = document.createElement('style');
  css.textContent =
    '#amenti-chrono-btn{position:fixed;left:16px;bottom:16px;z-index:1950;width:48px;height:48px;border-radius:50%;'
    + 'background:rgba(7,9,12,.88);border:1px solid rgba(224,165,60,.6);cursor:pointer;display:none;align-items:center;justify-content:center;'
    + 'box-shadow:0 4px 18px rgba(0,0,0,.5);padding:0}'
    + '#amenti-chrono-btn.on{display:flex}#amenti-chrono-btn:hover{background:rgba(224,165,60,.15)}'
    + '#amenti-chrono{position:fixed;left:16px;bottom:74px;z-index:1950;width:340px;height:560px;max-width:calc(100vw - 32px);max-height:calc(100vh - 100px);'
    + 'border:1px solid rgba(224,165,60,.45);background:#07090c;box-shadow:0 12px 40px rgba(0,0,0,.6);display:none}'
    + '#amenti-chrono.on{display:block}#amenti-chrono iframe{width:100%;height:100%;border:0;display:block}';
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.id = 'amenti-chrono-btn'; btn.title = 'The Chronometer'; btn.setAttribute('aria-label', 'Open the Chronometer');
  btn.innerHTML = '<svg viewBox="0 0 44 56" width="26" height="33" aria-hidden="true"><g stroke="#e0a53c" stroke-linecap="round" fill="none">'
    + '<circle cx="22" cy="22" r="13" stroke-width="2.6"/><line x1="22" y1="4" x2="22" y2="52" stroke-width="3"/><line x1="5" y1="22" x2="39" y2="22" stroke-width="3"/></g></svg>';
  var panel = document.createElement('div'); panel.id = 'amenti-chrono';
  var frame = null, last = '';
  document.body.appendChild(btn); document.body.appendChild(panel);

  function tell(force) {
    if (!frame || !R.sheet || R.sheet.work !== 'dracula') return;
    var n = R.cue ? R.cue.n : 1, key = R.sheet.episode + ':' + n;
    if (key === last && !force) return; last = key;
    try { frame.contentWindow.postMessage({ type: 'amenti-cue', ep: R.sheet.episode, n: n }, '*'); } catch (e) {}
  }
  btn.addEventListener('click', function () {
    if (!frame) {
      frame = document.createElement('iframe'); frame.title = 'The Chronometer';
      var q = R.sheet ? '&ep=' + R.sheet.episode + '&n=' + (R.cue ? R.cue.n : 1) : '';
      frame.src = SRC + q; frame.onload = function () { tell(true); };
      panel.appendChild(frame);
    }
    panel.classList.toggle('on');
  });

  /* show the emblem only while a Dracula sheet is loaded */
  setInterval(function () {
    var on = !!(R.sheet && R.sheet.work === 'dracula');
    btn.classList.toggle('on', on);
    if (!on) panel.classList.remove('on');
    tell(false);
  }, 700);

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  window.addEventListener('message', function (ev) {
    var d = ev.data;
    if (!d || d.type !== 'amenti-jump' || !frame || ev.source !== frame.contentWindow) return;
    var ep = +d.ep, n = +d.n || 1;
    if (typeof window.amentiChronoJump === 'function' && window.amentiChronoJump(ep, n) !== false) return;
    if (R.sheet && R.sheet.episode === ep && (R.state === 'reading' || R.state === 'paused' || R.state === 'stalled')) { R.seek(n); return; }
    R.play('dracula/ep' + pad(ep) + '.json').then(function () { if (n > 1) R.seek(n); }, function (e) { console.warn('chronometer.js: ' + (e && e.message)); });
  });

  console.log('%c Amenti readings · chronometer ready ', 'background:#e0a53c;color:#000;padding:2px 6px');
})();
