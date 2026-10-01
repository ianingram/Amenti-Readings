/* ===========================================================================
   AMENTI READINGS · reader.js
   ---------------------------------------------------------------------------
   Walks a cue sheet and speaks it, one cue at a time, in the voice of the
   figure cast in that role.

   ONE JOB. Fetch a cue sheet, resolve each role to a ledger name, hand the
   text to the engine that already exists, and wait for it to finish before
   starting the next cue.

   ── IT CARRIES NO VOICE OF ITS OWN ────────────────────────────────────────
   Every word spoken here goes through Amenti.throttle.speak — the same engine
   the reading room and Atlantica use, chunking at CHUNK_MAX, streaming, with
   one shared R2 cache behind it. This file contains no chunker, no style
   composition, no fetch to /speak, and must never grow one.

   ONE CHUNKER, ONE STYLE COMPOSITION, ONE CACHE.

   The reason is money, not tidiness. The cache key is
   TTS_MODEL + voice + style + text. A second chunker splits the same passage
   differently, every measure hashes to a new key, and the archive silently
   re-renders. Page2 already runs two pipelines with two cache namespaces and
   the standing instruction is to retire that condition, not reproduce it.

   PAGE 1 ONLY, for the same reason. Page1 retired its separate read-aloud
   pipeline; every voice call there is one engine. Page2 is not ready.

   ── THE INTERFACE IT USES, VERIFIED AGAINST THE LIVE FILE ─────────────────
     Amenti.throttle.speak(text, btn, figureName, onDone)
     Amenti.throttle.stop()
     Amenti.throttle.isReading() -> bool
     Amenti.throttle.resolveVoice(name) -> Promise<{voice, style, figure}>

   onDone is what makes a cue sheet possible: the next cue starts when the
   previous one has actually finished speaking, not on a timer.

   resolveVoice joins the roster on FULL NAME, lower-cased, and falls back to
   a neutral voice when a figure is absent RATHER THAN FAILING. A mistyped
   cast name is therefore silent — it still speaks, in the wrong voice. That
   is why preflight() exists and why it runs before a reading, not after.

   ── BEING LOADED IS NOT BEING USED ────────────────────────────────────────
   The Terminal ran its whole life without the conversation core because a
   defensive guard failed silently and nothing could look at it. So this file
   publishes what it is doing:

     Amenti.reading.state   idle | loading | reading | paused | done | error
     Amenti.reading.path    'throttle' when the engine is live, 'none' when not
     Amenti.reading.cue     the cue now speaking

   A probe can ask. If the engine is missing, the reader says so in the
   console in plain words and refuses to start, instead of appearing to work.
   =========================================================================== */
(function () {
  'use strict';

  var Amenti = window.Amenti = window.Amenti || {};

  var R = {
    /* where the scripts live */
    BASE: 'https://raw.githubusercontent.com/ianingram/Amenti-Readings/main/',

    state: 'idle',
    path: 'none',
    cue: null,
    sheet: null,
    cast: null,
    i: 0,
    onCue: null,     /* host page may set this: fn(cue, index, total) */
    onEnd: null,

    /* ── the engine, or an honest refusal ──────────────────────────────── */
    engine: function () {
      var t = window.Amenti && window.Amenti.throttle;
      return (t && typeof t.speak === 'function') ? t : null;
    },

    /* ── fetch ─────────────────────────────────────────────────────────── */
    _json: function (path) {
      var url = /^https?:/.test(path) ? path : R.BASE + path;
      return fetch(url, { cache: 'no-store' }).then(function (r) {
        if (!r.ok) throw new Error(path + ' -> ' + r.status);
        return r.json();
      });
    },

    /* ── load a cue sheet and its cast ─────────────────────────────────── */
    load: function (sheetPath) {
      R.state = 'loading';
      return Promise.all([R._json(sheetPath), R._json('cast.json')])
        .then(function (both) {
          R.sheet = both[0];
          R.cast = both[1];
          R.i = 0;
          R.state = 'idle';
          return R.sheet;
        })['catch'](function (e) {
          R.state = 'error';
          console.warn('Readings: cannot load ' + sheetPath + ' — ' + e.message);
          throw e;
        });
    },

    /* ── role -> ledger name ───────────────────────────────────────────────
       A cue names a ROLE. cast.json maps the role to a ledger figure. The
       engine then resolves that name to a voice. Three hops, each one a
       lookup that can miss, so each one falls back rather than throwing:
       a reading that speaks in a plain voice is far better than one that
       stops in the middle. */
    nameFor: function (cue) {
      /* a cue may name the ledger figure outright */
      if (cue.cast) return cue.cast;
      var work = (R.sheet && R.sheet.work) || '';
      var roles = R.cast && R.cast.roles && R.cast.roles[work];
      if (!roles) return '';
      /* match on the role slug, else on the printed role name */
      var slug = String(cue.role || '').toLowerCase().replace(/[^a-z0-9]+/g, '-');
      var hit = roles[slug];
      if (!hit) {
        for (var k in roles) {
          if (roles[k].role && roles[k].role.toLowerCase() === String(cue.role).toLowerCase()) {
            hit = roles[k]; break;
          }
        }
      }
      return (hit && hit.ledger_name) || '';
    },

    /* ── PREFLIGHT ─────────────────────────────────────────────────────────
       resolveVoice never fails — it returns a neutral voice for a name it
       does not know. So a mis-cast reading sounds plausible and is wrong,
       which is the worst failure available. Check before speaking, not after.

       Returns a report; it does not block. The proprietor decides. */
    preflight: function () {
      var eng = R.engine();
      if (!eng || !eng.resolveVoice) {
        return Promise.resolve({ ok: false, reason: 'no engine' });
      }
      var names = {};
      (R.sheet.cues || []).forEach(function (c) {
        var n = R.nameFor(c);
        names[n || '(unmapped: ' + c.role + ')'] = true;
      });
      var list = Object.keys(names);
      return Promise.all(list.map(function (n) {
        if (n.indexOf('(unmapped') === 0) return { name: n, found: false };
        return eng.resolveVoice(n).then(function (v) {
          return { name: n, found: !!v.figure, dialect: v.figure && v.figure.dialect };
        });
      })).then(function (rows) {
        var missing = rows.filter(function (r) { return !r.found; });
        console.log('%c Readings · preflight ', 'background:#0a2;color:#fff;padding:2px 6px');
        rows.forEach(function (r) {
          console.log('   ' + (r.found ? 'OK  ' : 'MISS') + '  ' + r.name +
                      (r.dialect ? '  —  ' + r.dialect : ''));
        });
        if (missing.length) {
          console.warn('Readings: ' + missing.length + ' name(s) will speak in a NEUTRAL ' +
                       'voice. resolveVoice falls back rather than failing, so this is ' +
                       'silent at runtime. Fix cast.json before rendering.');
        }
        return { ok: !missing.length, rows: rows, missing: missing };
      });
    },

    /* ── play ──────────────────────────────────────────────────────────── */
    play: function (sheetPath) {
      var eng = R.engine();
      if (!eng) {
        R.state = 'error'; R.path = 'none';
        console.warn('Readings: Amenti.throttle is not present. This reader does ' +
                     'not carry its own voice by design — load amenti-voice.js (or ' +
                     'amenti-throttle.js) before it. Nothing will be spoken.');
        return Promise.reject(new Error('no engine'));
      }
      R.path = 'throttle';
      var start = sheetPath ? R.load(sheetPath) : Promise.resolve(R.sheet);
      return start.then(function () {
        if (!R.sheet || !R.sheet.cues || !R.sheet.cues.length) {
          throw new Error('cue sheet has no cues');
        }
        R.i = 0;
        R.state = 'reading';
        R._next();
      });
    },

    _next: function () {
      if (R.state !== 'reading') return;
      var cues = R.sheet.cues;
      if (R.i >= cues.length) {
        R.state = 'done'; R.cue = null;
        if (typeof R.onEnd === 'function') { try { R.onEnd(R.sheet); } catch (e) {} }
        return;
      }
      var cue = cues[R.i];
      R.cue = cue;
      if (typeof R.onCue === 'function') {
        try { R.onCue(cue, R.i, cues.length); } catch (e) {}
      }
      var name = R.nameFor(cue);

      /* THE TEXT IS PASSED THROUGH UNCHANGED.
         Not trimmed, not normalised, not re-wrapped. chunkText is
         deterministic and the cache key contains the text, so touching it
         here orphans every measure this cue has ever rendered. */
      R.engine().speak(cue.text, null, name, function () {
        R.i += 1;
        R._next();
      });
    },

    pause: function () {
      if (R.state !== 'reading') return;
      R.state = 'paused';
      var e = R.engine(); if (e) e.stop();
    },

    resume: function () {
      if (R.state !== 'paused') return;
      R.state = 'reading';
      R._next();          /* re-speaks the cue it was stopped inside */
    },

    stop: function () {
      R.state = 'idle'; R.cue = null; R.i = 0;
      var e = R.engine(); if (e) e.stop();
    },

    /* jump to a cue by 1-based number */
    seek: function (n) {
      var i = Math.max(0, Math.min((R.sheet.cues || []).length - 1, (n | 0) - 1));
      var was = R.state;
      var e = R.engine(); if (e) e.stop();
      R.i = i;
      if (was === 'reading') { R.state = 'reading'; R._next(); }
    }
  };

  Amenti.reading = R;

  /* THE TELL. A probe can ask what this is doing without reading the code. */
  console.log('%c Amenti readings · reader ready ',
              'background:#d4a017;color:#000;padding:2px 6px',
              R.engine() ? '· engine: throttle' : '· NO ENGINE — nothing will speak');
})();
