/* Amenti-Readings/player/art.js · 2026-10-17 · exhibits */
/* ===========================================================================
   AMENTI READINGS · art.js — the pictures under a reading
   ---------------------------------------------------------------------------
   The illustrated-book layer. While a reading runs, the screen behind the
   transport bar shows painted scenes that change with the story, the way the
   Demeter voyage does on the Dracula landing page: each scene is a set of
   pictures, the frame drifts slowly, and the next picture crossfades in.

   LOAD ORDER: amenti-core.bundle.js · reader.js · casting.js · playbill.js ·
   sound.js · art.js. It needs Amenti.reading and nothing else.

   ── IT TOUCHES NO VOICE AND NO CUE SHEET ──────────────────────────────────
   Nothing here speaks, composes a style or edits a cue. It reads
   Amenti.reading.sheet / .i / .state four times a second (as the transport
   bar does), so seeking, pausing and stopping are followed for free and no
   reader function is wrapped. A work without an art sheet is untouched.

   ── THE ART SHEET ── <work>/art.json ─────────────────────────────────────
   { "base": "art/",
     "episodes": { "2": [ { "from": 1, "caption": "…", "cut": false,
                            "images": ["ch02-a1-2.jpg", …] }, … ] } }
   A scene starts on the cue whose "n" equals "from" and lasts until the next
   scene. A scene with no images ends the pictures (the reading carries on
   without them). "cut": true changes the picture at once instead of
   crossfading — for a hard beat.

   ── TIMING ────────────────────────────────────────────────────────────────
   Within a scene the pictures change every HOLD seconds while the reading is
   running; paused, everything holds still. There are no word timings, so a
   scene is placed on the cue where its moment begins.

   ── EXHIBITS ── maps from the Dossier, shown over the pictures ─────────────
   "exhibits": { "1": [ { "at": 4, "src": "dossier/borgo-pass.html", "legs": "0-1" }, … ] }
   When the reading arrives at cue "at", the page is opened full screen over the
   pictures (with ?embed&legs=…), plays, says "done", and fades away; the
   pictures carry on underneath. Pausing the reading pauses the map. A page
   that never says done is closed after "max" seconds of reading (default 40).

   ── VIEWER CONTROL ────────────────────────────────────────────────────────
   A small "pictures" button turns the layer off and on; the choice is
   remembered in this browser only (try/catch — it may not be available).
   =========================================================================== */
(function () {
  'use strict';
  var A = window.Amenti || {}, R = A.reading;
  if (!R) { console.warn('[art] Amenti.reading is missing — load art.js after reader.js. No pictures.'); return; }

  var ROOT = 'https://ianingram.github.io/Amenti-Readings/';
  var HOLD = 14;          /* seconds per picture within a scene */
  var FADE = 2.6;         /* crossfade, seconds */
  var still = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);

  var sheets = {};        /* work -> art sheet | null (none) | 'loading' */
  var stage = null, cap = null, tog = null;
  var cur = { key: '', scene: null, k: 0, since: 0, layer: null };
  var off = false, shown = false, lastTick = 0, flip = 0;
  var ex = null, lastN = null;   /* the open exhibit: {el, frame, at, run, paused} */
  try { off = localStorage.getItem('amenti-art-off') === '1'; } catch (e) {}

  function css() {
    if (document.getElementById('art-css')) return;
    var s = document.createElement('style'); s.id = 'art-css';
    s.textContent =
        '#amenti-art{position:fixed;inset:0;z-index:1800;background:#05070a;overflow:hidden;'
      + 'opacity:0;pointer-events:none;transition:opacity 1.6s ease;}'
      + '#amenti-art.on{opacity:1;pointer-events:auto;}'
      + '#amenti-art .art-l{position:absolute;inset:-4%;background:center 50%/cover no-repeat;opacity:0;'
      + 'transition:opacity ' + FADE + 's ease;will-change:opacity,transform;}'
      + '#amenti-art .art-l.in{opacity:1;}'
      + '#amenti-art .art-l.cut{transition:opacity .35s ease;}'
      + '#amenti-art .art-l.kb0{animation:artkb0 30s linear forwards;}'
      + '#amenti-art .art-l.kb1{animation:artkb1 30s linear forwards;}'
      + '#amenti-art.hold .art-l{animation-play-state:paused;}'
      + '@keyframes artkb0{from{transform:scale(1) translate(0,0)}to{transform:scale(1.07) translate(-1.2%,-.8%)}}'
      + '@keyframes artkb1{from{transform:scale(1.07) translate(1%,.6%)}to{transform:scale(1) translate(0,0)}}'
      + '#amenti-art .art-veil{position:absolute;inset:0;pointer-events:none;'
      + 'background:linear-gradient(180deg,rgba(5,7,10,.55) 0%,rgba(5,7,10,0) 18%,rgba(5,7,10,0) 72%,rgba(5,7,10,.6) 100%);}'
      + '#amenti-art .art-cap{position:absolute;right:clamp(16px,4vw,44px);top:72px;z-index:3;'
      + 'font:11px/1.4 Georgia,serif;letter-spacing:.24em;text-transform:uppercase;color:#e8dcc0;'
      + 'text-shadow:0 1px 14px rgba(0,0,0,.9);opacity:0;transition:opacity 1.6s ease;max-width:70vw;text-align:right;}'
      + '#amenti-art .art-cap.on{opacity:.85;}'
      + '#amenti-exhibit{position:fixed;inset:0;z-index:1850;background:#05070a;opacity:0;transition:opacity 1.2s ease;}'
      + '#amenti-exhibit.on{opacity:1;}'
      + '#amenti-exhibit iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:#05070a;}'
      + '#amenti-art-tog{position:fixed;right:16px;bottom:16px;z-index:1950;display:none;'
      + 'background:rgba(7,9,12,.55);border:1px solid rgba(212,160,23,.35);color:#d4a017;'
      + 'font:9px/1 Georgia,serif;letter-spacing:.24em;text-transform:uppercase;padding:9px 12px;cursor:pointer;}'
      + '#amenti-art-tog.on{display:block;}'
      + '#amenti-art-tog.off{color:#6a7a70;}'
      + (still ? '#amenti-art .art-l{animation:none!important;}' : '');
    document.head.appendChild(s);
  }

  function build() {
    if (stage) return;
    css();
    stage = document.createElement('div'); stage.id = 'amenti-art'; stage.setAttribute('aria-hidden', 'true');
    var veil = document.createElement('div'); veil.className = 'art-veil';
    cap = document.createElement('div'); cap.className = 'art-cap';
    stage.appendChild(veil); stage.appendChild(cap);
    document.body.appendChild(stage);
    tog = document.createElement('button'); tog.id = 'amenti-art-tog'; tog.type = 'button';
    tog.onclick = function () {
      off = !off;
      try { localStorage.setItem('amenti-art-off', off ? '1' : '0'); } catch (e) {}
      paintTog(); tick(true);
    };
    document.body.appendChild(tog);
    paintTog();
  }
  function paintTog() { if (!tog) return; tog.textContent = off ? 'pictures off' : 'pictures'; tog.classList.toggle('off', off); }

  function sheetFor(work) {
    if (!work) return null;
    if (sheets[work] === undefined) {
      sheets[work] = 'loading';
      fetch(ROOT + work + '/art.json?v=' + Math.floor(Date.now() / 6e5))
        .then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(function (j) { sheets[work] = j; console.log('[art] pictures for ' + work); })
        .catch(function () { sheets[work] = null; });
    }
    return sheets[work] === 'loading' ? null : sheets[work];
  }

  function url(work, sheet, f) { return /^https?:/.test(f) ? f : ROOT + work + '/' + (sheet.base || '') + f; }
  function preload(u) { var im = new Image(); im.src = u; }

  function sceneAt(list, n) {
    var s = null;
    for (var j = 0; j < list.length; j++) if (list[j].from <= n) s = list[j];
    return (s && s.images && s.images.length) ? s : null;
  }

  function showImage(u, cut, caption) {
    var l = document.createElement('div');
    l.className = 'art-l' + (cut ? ' cut' : '') + (still ? '' : ' kb' + (flip++ % 2));
    l.style.backgroundImage = 'url("' + u + '")';
    stage.insertBefore(l, cap.previousSibling);   /* under the veil and the caption */
    var old = cur.layer; cur.layer = l;
    void l.offsetWidth; l.classList.add('in');
    if (old) setTimeout(function () { if (old.parentNode) old.parentNode.removeChild(old); }, (cut ? 400 : FADE * 1000 + 200));
    if (caption !== undefined) {
      cap.classList.remove('on');
      if (caption) setTimeout(function () { cap.textContent = caption; cap.classList.add('on'); }, cut ? 200 : 900);
    }
  }

  function openExhibit(work, art, x, key) {
    closeExhibit(true);
    css();
    var el = document.createElement('div'); el.id = 'amenti-exhibit';
    var fr = document.createElement('iframe'); fr.title = 'Map'; fr.setAttribute('loading', 'eager');
    fr.src = url(work, { base: '' }, x.src) + (x.src.indexOf('?') < 0 ? '?' : '&') + 'embed=1' + (x.legs != null ? '&legs=' + x.legs : '');
    el.appendChild(fr); document.body.appendChild(el);
    ex = { el: el, frame: fr, key: key, at: x.at, run: 0, max: x.max || 40, paused: false };
    void el.offsetWidth; el.classList.add('on');
  }
  function closeExhibit(now) {
    if (!ex) return;
    var el = ex.el; ex = null;
    el.classList.remove('on');
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, now ? 0 : 1300);
  }
  function tellExhibit(msg) { try { ex.frame.contentWindow.postMessage({ amentiMap: msg }, '*'); } catch (e) {} }
  window.addEventListener('message', function (ev) {
    if (ex && ev.data && ev.data.amentiMap === 'done' && ev.source === ex.frame.contentWindow) closeExhibit(false);
  });

  function exhibits(work, art, sh, n, dt) {
    var xs = (art.exhibits && art.exhibits[String(sh.episode)]) || [];
    if (n !== lastN) {
      var prev = lastN; lastN = n;
      if (ex && (n < ex.at)) closeExhibit(false);                 /* sought back before it */
      for (var j = 0; j < xs.length; j++) if (xs[j].at === n) {
        openExhibit(work, art, xs[j], work + ':' + sh.episode + ':x' + n); break;
      }
    }
    if (!ex) return;
    var p = R.state !== 'reading';
    if (p !== ex.paused) { ex.paused = p; tellExhibit(p ? 'pause' : 'resume'); }
    if (!p) { ex.run += dt; if (ex.run > ex.max) closeExhibit(false); }
  }

  function hideStage() {
    if (stage && shown) { stage.classList.remove('on'); shown = false; }
    cur.key = ''; cur.scene = null;
  }

  function tick(force) {
    var live = R.state === 'reading' || R.state === 'paused' || R.state === 'stalled';
    var sh = R.sheet, work = sh && sh.work, art = live ? sheetFor(work) : null;
    var list = art && art.episodes && art.episodes[String(sh.episode)];
    if (tog) tog.classList.toggle('on', !!(live && list));
    if (!live || !list || off) { hideStage(); closeExhibit(false); lastN = null; return; }
    build();
    var cues = sh.cues || [], c = cues[Math.min(R.i, cues.length - 1)] || {};
    var n = c.n || (R.i + 1), sc = sceneAt(list, n);
    stage.classList.toggle('hold', R.state !== 'reading');
    var tnow = Date.now() / 1000;
    exhibits(work, art, sh, n, lastTick ? Math.min(1, tnow - lastTick) : 0);
    if (!sc) { hideStage(); return; }
    var now = Date.now() / 1000, key = work + ':' + sh.episode + ':' + sc.from;
    if (key !== cur.key) {
      cur.key = key; cur.scene = sc; cur.k = 0; cur.since = now;
      showImage(url(work, art, sc.images[0]), !!sc.cut && shown, sc.caption || '');
      if (!shown) { stage.classList.add('on'); shown = true; }
      sc.images.slice(1, 2).forEach(function (f) { preload(url(work, art, f)); });
      var nx = list[list.indexOf(sc) + 1];
      if (nx && nx.images && nx.images[0]) preload(url(work, art, nx.images[0]));
      return;
    }
    if (R.state !== 'reading') { cur.since += (now - (lastTick || now)); lastTick = now; return; }  /* paused: the clock holds */
    lastTick = now;
    if (sc.images.length > 1 && now - cur.since >= HOLD) {
      cur.k = (cur.k + 1) % sc.images.length; cur.since = now;
      showImage(url(work, art, sc.images[cur.k]), false);
      preload(url(work, art, sc.images[(cur.k + 1) % sc.images.length]));
    }
  }

  setInterval(function () { try { tick(false); } catch (e) { console.warn('[art]', e); } }, 250);
  A.art = { tick: tick, sheets: sheets };
  console.log('%c Amenti readings · pictures ready ', 'background:#0b0f0d;color:#d4a017');
})();
