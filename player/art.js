/* Amenti-Readings/player/art.js · 2026-10-26 · pictures fill their scene; a picture can start at a phrase */
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
   An entry ending in .mp4 is a moving picture (a Midjourney clip): it plays
   silent and on a loop while it is up, freezes while the reading is paused,
   and crossfades like a painting. The narration, score and effects are
   untouched — a clip has no sound of its own here.
   A scene starts on the cue whose "n" equals "from" and lasts until the next
   scene. A scene with no images ends the pictures (the reading carries on
   without them). "cut": true changes the picture at once instead of
   crossfading — for a hard beat.

   ── TIMING · 26 Oct 2026 ─────────────────────────────────────────────────
   A scene's pictures are SPREAD ACROSS THE SCENE and each is shown once, in
   order. They used to change every 14 s and start again from the first when
   they ran out, so a long letter over four paintings showed the same four
   three times over — the first thing a reader noticed.
   Where the reading is in a scene is measured in WORDS: the words of the cues
   already read, plus how far into the current cue the voice has got. For a
   recorded cue that is the audio's own clock (currentTime / duration); for a
   spoken one it is reading time against the cue's word count, at a speaking
   rate that calibrates itself from the cues just finished. Picture k of N
   comes up when the reading is k/N of the way through the scene.
   No picture is shown for less than MIN_HOLD seconds, so a scene with more
   pictures than time runs a little late rather than flickering, and the last
   picture holds until the scene ends — it never starts the set again.
   Paused, everything holds still.

   "at": "<words from the cue>" starts a scene PART WAY THROUGH its cue, when
   the reading reaches those words — for a long paragraph whose moment comes
   at its end ("Suddenly, I became conscious…" — the castle). Until then the
   scene before it stays up. The phrase must appear in the cue's text; if it
   does not, the scene starts at the top of the cue, as before.

   ── EXHIBITS ── maps from the Dossier, shown over the pictures ─────────────
   "exhibits": { "1": [ { "at": 4, "src": "dossier/borgo-pass.html", "legs": "0-1" }, … ] }
   When the reading arrives at cue "at", the page is opened full screen over the
   pictures (with ?embed&legs=…), plays, says "done", and fades away; the
   pictures carry on underneath. Pausing the reading pauses the map. A page
   that never says done is closed after "max" seconds of reading (default 40).
   With "until": <cue n> the page stays up from "at" through that cue and is
   told each cue as the reading reaches it ({amentiMap:'cue', n}) — for a map
   that follows a long speech; it closes when the reading moves past "until".

   ── VIEWER CONTROL ────────────────────────────────────────────────────────
   A small "pictures" button turns the layer off and on; the choice is
   remembered in this browser only (try/catch — it may not be available).
   =========================================================================== */
(function () {
  'use strict';
  var A = window.Amenti || {}, R = A.reading;
  if (!R) { console.warn('[art] Amenti.reading is missing — load art.js after reader.js. No pictures.'); return; }

  var ROOT = 'https://ianingram.github.io/Amenti-Readings/';
  var MIN_HOLD = 9;       /* no picture is shown for less than this, in seconds of reading */
  var RATE0 = 2.5;        /* words per second before any cue has been timed (150 a minute) */
  var FADE = 2.6;         /* crossfade, seconds */
  var still = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);

  var sheets = {};        /* work -> art sheet | null (none) | 'loading' */
  var stage = null, cap = null, tog = null;
  var cur = { key: '', scene: null, k: 0, since: 0, layer: null };
  var off = false, shown = false, lastTick = 0, flip = 0;
  /* reading clock and speaking rate — see TIMING */
  var clock = 0, rate = RATE0;
  var cueAt = { key: '', start: 0, words: 0, spoken: false };
  var wordsCache = { sheet: null, before: null, count: null };
  var ex = null, lastN = null, exLast = 0;   /* the open exhibit: {el, frame, at, run, paused} */
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
  function preload(u) { if (/\.mp4(\?|$)/i.test(u)) { var v = document.createElement('video'); v.preload = 'auto'; v.muted = true; v.src = u; return; } var im = new Image(); im.src = u; }

  /* ── WORDS: where the reading is, counted in words ── */
  function wc(t) { var m = String(t || '').match(/\S+/g); return m ? m.length : 0; }
  function words(sh) {                     /* per sheet: words in each cue, and words before it */
    if (wordsCache.sheet === sh) return wordsCache;
    var cs = sh.cues || [], before = {}, count = {}, run = 0;
    for (var j = 0; j < cs.length; j++) { var n = cs[j].n || (j + 1), w = wc(cs[j].text); before[n] = run; count[n] = w; run += w; }
    wordsCache = { sheet: sh, before: before, count: count, total: run };
    return wordsCache;
  }
  /* how far into its cue a scene's "at" phrase falls, 0..1 — or 0 if there is none or it is not found */
  function atFrac(sh, sc) {
    if (!sc.at) return 0;
    if (sc._atFrac !== undefined) return sc._atFrac;
    var cs = sh.cues || [], c = null;
    for (var j = 0; j < cs.length; j++) if ((cs[j].n || (j + 1)) === sc.from) { c = cs[j]; break; }
    var t = c ? String(c.text).replace(/\s+/g, ' ') : '', i = t.toLowerCase().indexOf(String(sc.at).replace(/\s+/g, ' ').toLowerCase());
    if (i < 0) { console.warn('[art] scene at cue ' + sc.from + ': "' + sc.at + '" is not in the cue — starting it at the top of the cue'); sc._atFrac = 0; }
    else sc._atFrac = wc(t.slice(0, i)) / Math.max(1, wc(t));
    return sc._atFrac;
  }
  /* the word position where a scene starts */
  function startOf(sh, sc) { var W = words(sh); return (W.before[sc.from] || 0) + atFrac(sh, sc) * (W.count[sc.from] || 0); }

  /* the scene showing at cue n, `frac` of the way through it */
  function sceneAt(sh, list, n, frac) {
    var s = null;
    for (var j = 0; j < list.length; j++) {
      var e = list[j];
      if (e.from < n || (e.from === n && (!e.at || frac >= atFrac(sh, e)))) s = e;
    }
    return (s && s.images && s.images.length) ? s : null;
  }

  /* how far through the current cue the voice is, 0..1 */
  function cueFrac(c) {
    var a = R._audio;
    if (a && c.audio && !c.through && a.duration && isFinite(a.duration) && a.duration > 0) return Math.min(1, a.currentTime / a.duration);
    var est = Math.max(1, cueAt.words / rate);
    return Math.min(0.97, (clock - cueAt.start) / est);
  }

  function isVid(u) { return /\.mp4(\?|$)/i.test(u); }
  function showImage(u, cut, caption) {
    var l = document.createElement('div'), vid = isVid(u);
    l.className = 'art-l' + (cut ? ' cut' : '') + (still || vid ? '' : ' kb' + (flip++ % 2));
    if (vid) {
      var v = document.createElement('video');
      v.muted = true; v.defaultMuted = true; v.loop = true; v.playsInline = true; v.autoplay = true;
      v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.preload = 'auto'; v.src = u;
      v.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;';
      l.appendChild(v);
      try { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); } catch (e) {}
    } else l.style.backgroundImage = 'url("' + u + '")';
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
    fr.src = url(work, { base: '' }, x.src) + (x.src.indexOf('?') < 0 ? '?' : '&') + 'embed=1' + (x.legs != null ? '&legs=' + x.legs : '') + '&cue=' + x.at;
    el.appendChild(fr); document.body.appendChild(el);
    ex = { el: el, frame: fr, key: key, at: x.at, until: x.until || null, untilAt: x.untilAt || null, run: 0, max: x.max || 40, paused: false };
    void el.offsetWidth; el.classList.add('on');
  }
  function closeExhibit(now) {
    if (!ex) return;
    var el = ex.el; ex = null;
    el.classList.remove('on');
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, now ? 0 : 1300);
  }
  function tellExhibit(msg, n) { try { ex.frame.contentWindow.postMessage({ amentiMap: msg, n: n }, '*'); } catch (e) {} }
  window.addEventListener('message', function (ev) {
    if (ex && !ex.until && ev.data && ev.data.amentiMap === 'done' && ev.source === ex.frame.contentWindow) closeExhibit(false);   /* an exhibit held to a cue ("until") stays to the end of it */
  });

  function exhibits(work, art, sh, n, dt, c, frac) {
    var xs = (art.exhibits && art.exhibits[String(sh.episode)]) || [];
    if (n !== lastN) {
      var prev = lastN; lastN = n;
      if (ex && (n < ex.at || (ex.until && n > ex.until))) closeExhibit(false);   /* sought back before it, or read past it */
      else if (ex && ex.until) tellExhibit('cue', n);
      for (var j = 0; j < xs.length; j++) if (xs[j].at === n && !(ex && ex.until && ex.at === n)) {
        openExhibit(work, art, xs[j], work + ':' + sh.episode + ':x' + n); break;
      }
    }
    if (!ex) return;
    var p = R.state !== 'reading';
    if (p !== ex.paused) { ex.paused = p; tellExhibit(p ? 'pause' : 'resume'); }
    if (!p && !ex.until) { ex.run += dt; if (ex.run > ex.max) closeExhibit(false); }
    /* "untilAt": close a held exhibit a few seconds after those words in the "until" cue (31 Oct) */
    if (ex && ex.untilAt && n === ex.until && c && c.text) {
      var ua = String(c.text).replace(/\s+/g, ' '), ui = ua.indexOf(ex.untilAt);
      if (ui >= 0 && (frac || 0) * ua.length > ui + ex.untilAt.length + 70) { closeExhibit(false); return; }
    }
    /* 31 Oct: tell the map what has been read of this cue so far, so a place flashes as it is named */
    if (ex && c && c.text) {
      var hl = Math.round(String(c.text).length * Math.max(0, Math.min(1, frac || 0)));
      if (hl !== ex.heard) { ex.heard = hl; try { ex.frame.contentWindow.postMessage({ amentiMap: 'heard', n: n, text: String(c.text).slice(0, hl) }, '*'); } catch (e) {} }
    }
  }

  function hideStage() {
    if (stage && shown) { stage.classList.remove('on'); shown = false; }
    cur.key = ''; cur.scene = null;
  }

  function tick(force) {
    var live = R.state === 'reading' || R.state === 'paused' || R.state === 'stalled';
    var sh = R.sheet, work = sh && sh.work, art = live ? sheetFor(work) : null;
    var list = art && art.episodes && art.episodes[String(sh.episode)];
    var xl = art && art.exhibits && art.exhibits[String(sh.episode)];   /* a chapter may have maps and no paintings */
    if (tog) tog.classList.toggle('on', !!(live && (list || xl)));
    if (!live || !(list || xl) || off) { hideStage(); closeExhibit(false); lastN = null; return; }
    build();
    var cues = sh.cues || [], c = cues[Math.min(R.i, cues.length - 1)] || {};
    var n = c.n || (R.i + 1);
    /* the reading clock: seconds of READING, so a pause stops it */
    var tnow0 = Date.now() / 1000, dt = lastTick ? Math.min(1, tnow0 - lastTick) : 0;
    lastTick = tnow0;
    if (R.state === 'reading') clock += dt;
    var ckey = work + ':' + sh.episode + ':' + n;
    if (ckey !== cueAt.key) {
      /* a spoken cue just finished: learn the voice's rate from it (recorded cues keep their own clock) */
      var took = clock - cueAt.start;
      if (cueAt.key && cueAt.spoken && cueAt.words >= 12 && took > 3 && cueAt.key.split(':')[1] === String(sh.episode)) {
        var r = cueAt.words / took;
        if (r > 0.8 && r < 5) rate = rate * 0.6 + r * 0.4;
      }
      cueAt = { key: ckey, start: clock, words: words(sh).count[n] || wc(c.text), spoken: !c.audio };
    }
    var frac = cueFrac(c);
    var sc = list ? sceneAt(sh, list, n, frac) : null;
    stage.classList.toggle('hold', R.state !== 'reading');
    var vs = stage.getElementsByTagName('video');
    for (var vi = 0; vi < vs.length; vi++) { try { if (R.state === 'reading') { if (vs[vi].paused) { var pp = vs[vi].play(); if (pp && pp.catch) pp.catch(function () {}); } } else if (!vs[vi].paused) vs[vi].pause(); } catch (e) {} }
    var tnow = Date.now() / 1000;
    exhibits(work, art, sh, n, exLast ? Math.min(1, tnow - exLast) : 0, c, frac); exLast = tnow;
    if (!sc) { hideStage(); return; }
    var key = work + ':' + sh.episode + ':' + sc.from + (sc.at ? '@' + sc.at : '');
    if (key !== cur.key) {
      cur.key = key; cur.scene = sc; cur.k = 0; cur.since = clock;
      showImage(url(work, art, sc.images[0]), !!sc.cut && shown, sc.caption || '');
      if (!shown) { stage.classList.add('on'); shown = true; }
      sc.images.slice(1, 2).forEach(function (f) { preload(url(work, art, f)); });
      var nx = list[list.indexOf(sc) + 1];
      if (nx && nx.images && nx.images[0]) preload(url(work, art, nx.images[0]));
      return;
    }
    if (R.state !== 'reading') return;      /* paused: the clock has stopped, so the pictures hold */
    var N = sc.images.length;
    if (N < 2 || cur.k >= N - 1) return;     /* the last picture holds until the scene ends — never round again */
    /* how far through the scene the reading is, 0..1, in words */
    var W = words(sh), from = startOf(sh, sc), idx = list.indexOf(sc), nx = null;
    for (var q = idx + 1; q < list.length; q++) { nx = list[q]; break; }
    var to = nx ? startOf(sh, nx) : W.total;
    var pos = (W.before[n] || 0) + frac * (W.count[n] || 0);
    var prog = to > from ? (pos - from) / (to - from) : 0;
    var want = Math.min(N - 1, Math.floor(prog * N));
    if (want > cur.k && clock - cur.since >= MIN_HOLD) {
      cur.k += 1; cur.since = clock;         /* one step at a time: every picture is seen */
      showImage(url(work, art, sc.images[cur.k]), false);
      if (cur.k + 1 < N) preload(url(work, art, sc.images[cur.k + 1]));
    }
  }

  setInterval(function () { try { tick(false); } catch (e) { console.warn('[art]', e); } }, 250);
  A.art = { tick: tick, sheets: sheets };
  console.log('%c Amenti readings · pictures ready ', 'background:#0b0f0d;color:#d4a017');
})();
