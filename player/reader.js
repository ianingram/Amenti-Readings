/* Amenti-Readings/player/reader.js · 2026-10-05 15:00 UTC */
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

     Amenti.reading.state   idle | loading | reading | paused | stalled | done | error
     Amenti.reading.path    'throttle' when the engine is live, 'none' when not
     Amenti.reading.cue     the cue now speaking

   A probe can ask. If the engine is missing, the reader says so in the
   console in plain words and refuses to start, instead of appearing to work.

   ── A RECORDED CUE (5 Oct 2026) ────────────────────────────────────────────
   A cue may carry  "audio": "<url>"  — a finished performance of that cue's
   own text (the Romeo and Juliet Prologue, spoken in time over music). The
   reader plays the file instead of speaking the text, shows the text as
   always, and moves on when the file ends. It is not a second voice path: no
   chunker, no style, no fetch to /speak — the file was made beforehand from
   the engine's own renders. warmAhead skips it (nothing to warm). If the file
   will not play, the cue is spoken by the engine instead, so nothing is lost.
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
    onError: null,   /* host page may set this: fn(error) — a cue that would not render */
    error: null,     /* { cue, role, why } while state is 'stalled' */

    /* ── THE NEXT LINE IS READY BEFORE IT IS NEEDED · 3 OCT 2026 ─────────────
       The first play of episode one had 6–12 seconds of silence between every
       cue: each line was only requested once the last had finished, and a
       render takes ~7 s. Now, as a cue starts, the next WARM_AHEAD cues are
       fetched through the engine's warm(), which sends exactly what speak()
       will send — same text, same voice, same style — so the gap becomes the
       render time of nothing. The text is still passed through unchanged.

       AND A LINE THAT WILL NOT RENDER NO LONGER STOPS THE SHOW IN SILENCE.
       The engine now reports failure (onFail). The cue is retried once; if it
       fails again the reading stops, says which cue, and offers Retry / Skip.
       state is 'stalled' while that notice is up. */
    /* ── ONE SPEECH, ONE BREATH · 9 OCT 2026 (Ian: "the same character speaks in
       several different voices from one line to the next") ─────────────────
       Verse cues keep a blank line between every verse line, so the engine's
       chunker (which splits on blank lines) sent each verse line to the voice
       as its own recording; each came back with its own accent. Casca's
       storm speech in I.iii was eleven separate performances.
       The text the VOICE hears is now the speech joined into one paragraph:
       the chunker then cuts it only at sentence ends, up to its 320 limit.
       The text on the page is unchanged. This changes the cache key of every
       multi-line cue, so those cues are recorded once more, whole. */
    /* ── THE LINE'S DIRECTION · 9 OCT 2026 ─────────────────────────────────
       From the screenplay: the scene's "voice" (where it is played — a crowded
       street, a quiet orchard) and the line's parenthetical. Sent with the line
       so it is PERFORMED, not only printed. Stage directions get none. */
    direction: function (c) {
      var sp = R.play_ && R.play_.scenes && R.sheet && R.play_.scenes[String(R.sheet.episode)];
      if (!sp || !c || /^stage direction/i.test(c.role || '')) return '';
      var parts = [];
      if (sp.voice) parts.push(sp.voice);
      if (sp.paren && sp.paren[String(c.n)]) parts.push(sp.paren[String(c.n)]);
      return parts.join('; ');
    },
    spoken: function (c) { return String(c.text).replace(/\s*\n+\s*/g, ' ').trim(); },
    WARM_AHEAD: 2,
    _tries: 0,
    _warmed: {},
    _noWarmSaid: false,

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
          /* the screenplay, if the work has one: where each scene is, how each line is played */
          R.play_ = null;
          var w = R.sheet && R.sheet.work;
          return w ? R._json(w + '/screenplay.json').then(function (sp) { R.play_ = sp; }, function () {}) : null;
        }).then(function () {
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
        R._tries = 0;
        R._warmed = {};
        R.error = null;
        R._hideNotice();
        R.state = 'reading';
        R._next();
      });
    },

    _warmAhead: function () {
      var eng = R.engine(), cues = R.sheet && R.sheet.cues;
      if (!eng || !cues) return;
      if (typeof eng.warm !== 'function') {
        if (!R._noWarmSaid) {
          R._noWarmSaid = true;
          console.warn('Readings: the engine has no warm() — each cue will render only when ' +
                       'it is reached, with a render wait between lines. Update amenti-core.bundle.js.');
        }
        return;
      }
      for (var j = 1; j <= R.WARM_AHEAD; j++) {
        var k = R.i + j, c = cues[k];
        if (!c || R._warmed[k] || c.audio) continue;     /* a recorded cue has nothing to warm */
        R._warmed[k] = true;
        try { eng.warm(R.spoken(c), R.nameFor(c), R.direction(c)); } catch (e) {}
      }
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
      var at = R.i;
      if (cue.audio && !cue._audioFailed) { R._playRecorded(cue, at); R._warmAhead(); return; }
      R.engine().speak(R.spoken(cue), null, name, function () {
        if (R.i !== at) return;
        R._tries = 0;
        R.i += 1;
        R._next();
      }, function (why) {
        if (R.i !== at || R.state !== 'reading') return;
        if (R._tries < 1) {
          R._tries += 1;
          console.warn('Readings: cue ' + (at + 1) + ' did not render (' + why + ') — retrying once.');
          R._next();
          return;
        }
        R.state = 'stalled';
        R.error = { cue: at + 1, role: cue.role || name, why: why };
        console.error('Readings: cue ' + (at + 1) + ' (' + R.error.role + ') would not render twice — ' +
                      why + '. The reading is stopped here, not skipped silently.');
        R._showNotice();
        if (typeof R.onError === 'function') { try { R.onError(R.error); } catch (e) {} }
      }, R.direction(cue));
      R._warmAhead();
    },

    /* a recorded cue: play the file, advance when it ends, speak the text if it cannot play */
    _playRecorded: function (cue, at) {
      R._stopRecorded();
      var a = new Audio(cue.audio);
      a.preload = 'auto';
      R._audio = a;
      a.onended = function () {
        if (R._audio !== a) return;
        R._audio = null;
        if (R.i !== at || R.state !== 'reading') return;
        R.i += 1; R._next();
      };
      a.onerror = function () {
        if (R._audio !== a) return;
        R._audio = null;
        console.warn('Readings: recorded cue ' + (at + 1) + ' would not play — speaking it instead.');
        cue._audioFailed = true;
        if (R.i === at && R.state === 'reading') R._next();
      };
      var p = a.play();
      if (p && typeof p['catch'] === 'function') p['catch'](function () { if (a.onerror) a.onerror(); });
    },
    _stopRecorded: function () {
      var a = R._audio; R._audio = null;
      if (a) { try { a.onended = a.onerror = null; a.pause(); } catch (e) {} }
    },

    retry: function () {
      if (R.state !== 'stalled') return;
      R._hideNotice(); R.error = null; R._tries = 0;
      R.state = 'reading';
      R._next();
    },

    skip: function () {
      if (R.state !== 'stalled') return;
      R._hideNotice(); R.error = null; R._tries = 0;
      R.i += 1;
      R.state = 'reading';
      R._next();
    },

    /* the one piece of UI the reader owns: a quiet notice when a line fails */
    _showNotice: function () {
      R._hideNotice();
      if (!document.body) return;
      var d = document.createElement('div');
      d.id = 'amenti-reading-notice';
      d.setAttribute('role', 'alert');
      d.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:2147483000;' +
        'background:rgba(12,10,8,.92);color:#e9e2d0;border:1px solid rgba(212,160,23,.5);' +
        'font:14px/1.4 Georgia,serif;padding:10px 14px;border-radius:4px;display:flex;gap:12px;align-items:center;' +
        'box-shadow:0 6px 24px rgba(0,0,0,.5);max-width:90vw';
      var t = document.createElement('span');
      t.textContent = 'Line ' + R.error.cue + ' (' + R.error.role + ') did not come through.';
      d.appendChild(t);
      [['Retry', R.retry], ['Skip', R.skip]].forEach(function (b) {
        var x = document.createElement('button');
        x.type = 'button'; x.textContent = b[0];
        x.style.cssText = 'background:none;border:1px solid rgba(212,160,23,.6);color:#d4a017;' +
          'font:inherit;padding:3px 10px;border-radius:3px;cursor:pointer';
        x.onclick = b[1];
        d.appendChild(x);
      });
      document.body.appendChild(d);
    },
    _hideNotice: function () {
      var d = document.getElementById('amenti-reading-notice');
      if (d && d.parentNode) d.parentNode.removeChild(d);
    },

    pause: function () {
      if (R.state !== 'reading') return;
      R.state = 'paused';
      R._stopRecorded();
      var e = R.engine(); if (e) e.stop();
    },

    resume: function () {
      if (R.state !== 'paused') return;
      R.state = 'reading';
      R._next();          /* re-speaks the cue it was stopped inside */
    },

    stop: function () {
      R._hideNotice(); R.error = null; R._tries = 0;
      R.state = 'idle'; R.cue = null; R.i = 0;
      R._stopRecorded();
      var e = R.engine(); if (e) e.stop();
    },

    /* jump to a cue by 1-based number */
    seek: function (n) {
      var i = Math.max(0, Math.min((R.sheet.cues || []).length - 1, (n | 0) - 1));
      var was = R.state;
      R._stopRecorded();
      var e = R.engine(); if (e) e.stop();
      R._hideNotice(); R.error = null; R._tries = 0;
      R.i = i;
      if (was === 'reading' || was === 'stalled') { R.state = 'reading'; R._next(); }
    }
  };

  Amenti.reading = R;

  /* THE TELL. A probe can ask what this is doing without reading the code. */
  console.log('%c Amenti readings · reader ready ',
              'background:#d4a017;color:#000;padding:2px 6px',
              R.engine() ? '· engine: throttle' : '· NO ENGINE — nothing will speak');
})();
