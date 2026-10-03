/* Amenti-Readings/player/sound.js · 2026-10-03 07:00 UTC */
/* ===========================================================================
   AMENTI READINGS · sound.js
   ---------------------------------------------------------------------------
   The bed and the one-shots under a reading. A sibling to reader.js: it reads
   the work's sound sheet (dracula/sound.json), starts the bed for the
   chapter, fires one-shots at cue boundaries, and sits the bed down under
   the voices while a reading is running.

   LOAD ORDER: amenti-core.bundle.js · reader.js · casting.js · playbill.js ·
   sound.js. It needs Amenti.reading and Amenti.throttle.audioContext, and
   refuses to start — out loud — if either is missing.

   ── IT TOUCHES NO VOICE ───────────────────────────────────────────────────
   Nothing here calls speak, composes a style, or goes near the voice bus's
   cache path. The bed plays on the ENGINE'S AudioContext so it shares a
   clock with the voices, through its own bus to the destination. A second
   context could never be ducked and would drift.

   ── HOW IT FOLLOWS THE READER ─────────────────────────────────────────────
   It wraps Amenti.reading._next, not onCue. _next is the one place every
   cue start and the end of the sheet pass through, and a host page that
   sets onCue for itself would otherwise silently unhook the sound.

   ── WHAT IT DOES NOT DO YET ───────────────────────────────────────────────
   Chapter-level sfx lists in sound.json are NOT fired: they say what the
   chapter needs, not where. A one-shot plays only when a CUE carries it
   ("sfx": ["door_heavy"]) — step 4. It fires as the cue begins, ahead of
   the first word; to land a sound after a line, put it on the next cue.
   Ducking follows the reading, not the waveform: the bed sits down while
   cues are being read and comes back up on pause or at the end. There is no
   word timing to do better with.

   ── SOUNDS INSIDE A LINE · added 3 Oct 2026 ──────────────────────────────
   A cue's "sfx" entry is either a key (plays as the cue begins) or
   { "key": "chains", "at": "rattling chains" } — played when the narrator
   reaches those words. There are no word timings from the voice, so the
   moment is ESTIMATED: the anchor's end position in the text divided by
   the speaker's pace, counted from the cue's first sound (the engine's
   amenti:voice-started). The pace starts at 15 characters a second
   (probe20) and is re-measured after every cue, per speaker, so the
   estimate tightens as the reading goes on. "offset" (seconds) nudges one.
   Anchors that are not found in the text play at the first sound and warn.

   ── MUSIC UNDER ONE LINE · added 3 Oct 2026 ──────────────────────────────
   A cue may carry "under": "piano_far" (or "piano_near") — a looping piece (files.under)
   that rises with the line's first sound and falls away when the line ends.
   Made for letters read aloud. While it plays the chapter score steps back,
   so two pieces of music never argue. In 1.5 s, out 2.5 s.

   ── THE SCORE · added 3 Oct 2026 ──────────────────────────────────────────
   A third layer beside the bed and the one-shots: the chapter's score cue
   ("score" in sound.json chapters, file from files.score). ONE source, looped
   at its own rate — music is never rate-shifted the way the bed is, because
   that would detune it. Its own gain and its own duck, on the same bus and
   the same clock. Envelopes from sound.json: in 6 s, out 8 s, crossfade 10 s
   equal-power — always longer than the bed's, so when both change the bed
   leads and the score follows. A chapter with "score": null (chapter 12)
   gets silence, not a quieter cue.

   ── VARIATION IS SEEDED ───────────────────────────────────────────────────
   Detune ±40 cents and playbackRate ±4 %, seeded from work + episode + cue
   + sound. An episode sounds identical on every listen.
   =========================================================================== */
(function () {
  'use strict';

  var Amenti = window.Amenti = window.Amenti || {};
  var R = Amenti.reading;
  var T = Amenti.throttle;

  if (!R) {
    console.warn('Sound: load player/reader.js first. No bed will play.');
    return;
  }
  if (!T || typeof T.audioContext !== 'function') {
    console.warn('Sound: Amenti.throttle.audioContext is missing — the engine bundle ' +
                 'is older than the voice bus (check for a stale CDN copy). No bed will play.');
    return;
  }

  /* levels and envelopes, from sound.json "envelopes" where it gives them */
  var BED_LEVEL = 0.32;      /* bed against the voices, before ducking */
  var DUCK_TO   = 0.45;      /* fraction of the bed left while a cue is read */
  var SFX_LEVEL = 0.7;
  var SCORE_LEVEL = 0.26;    /* the score against the voices, before ducking */
  var SCORE_DUCK  = 0.5;     /* music sits down less than the bed: it carries the scene */
  var UNDER_LEVEL = 0.34;    /* a fill under one line: present, never over the voice */
  var PRIMES    = [37, 53, 71];
  var LAYER     = [          /* one recording, three loops: rate and start apart */
    { rate: 1.000, at: 0.00, gain: 0.60 },
    { rate: 0.965, at: 0.37, gain: 0.45 },
    { rate: 1.035, at: 0.71, gain: 0.35 }
  ];

  var S = {
    state: 'idle',           /* idle | loading | playing | paused | off */
    sheet: null,             /* sound.json */
    chapter: null,
    bed: null,               /* key now playing */
    missing: [],
    _path: null,
    _ctx: null, _bus: null, _duck: null,
    _cur: null,              /* { key, gain, srcs } */
    score: null,             /* score key now playing */
    _scoreCur: null,         /* { key, gain, src } */
    _scoreDuck: null,
    _buffers: {},
    _fired: -1,
    _pending: null,          /* { i, cue, items } waiting for the cue's first sound */
    _cueT0: null,            /* { i, t0, len, who } of the cue now sounding */
    _cps: {},                /* measured characters per second, per speaker */
    _queued: [],             /* scheduled one-shots not yet sounded */
    _underNext: null,        /* "under" key waiting for its cue's first sound */
    _under: null,            /* { key, gain, src } */

    ctx: function () {
      if (!S._ctx) {
        S._ctx = T.audioContext();
        S._bus = S._ctx.createGain();
        S._duck = S._ctx.createGain();
        S._duck.connect(S._bus);
        S._scoreDuck = S._ctx.createGain();
        S._scoreDuck.connect(S._bus);
        S._bus.connect(S._ctx.destination);
      }
      if (S._ctx.state === 'suspended') { try { S._ctx.resume(); } catch (e) {} }
      return S._ctx;
    },

    /* ── envelopes ─────────────────────────────────────────────────────────
       Every change is a ramp. Exponential for fades (it sounds even), linear
       for ducking (small move, speed matters). Exponential cannot reach 0:
       ramp to 0.0001, then set 0. */
    _hold: function (p, t) {
      if (p.cancelAndHoldAtTime) { p.cancelAndHoldAtTime(t); }
      else { var v = p.value; p.cancelScheduledValues(t); p.setValueAtTime(v, t); }
    },
    fade: function (p, to, secs) {
      var t = S.ctx().currentTime;
      S._hold(p, t);
      p.setValueAtTime(Math.max(p.value, 0.0001), t);
      p.exponentialRampToValueAtTime(Math.max(to, 0.0001), t + secs);
      if (to <= 0) p.setValueAtTime(0, t + secs + 0.01);
    },
    slide: function (p, to, secs) {
      var t = S.ctx().currentTime;
      S._hold(p, t);
      p.linearRampToValueAtTime(to, t + secs);
    },
    /* equal-power: cos out, sin in, so the sum holds through the crossing */
    curve: function (p, from, to, secs, rising) {
      var n = 64, a = new Float32Array(n), t = S.ctx().currentTime;
      for (var i = 0; i < n; i++) {
        var x = i / (n - 1) * Math.PI / 2;
        a[i] = rising ? to * Math.sin(x) : from * Math.cos(x);
      }
      a[n - 1] = rising ? to : 0;
      S._hold(p, t);
      p.setValueCurveAtTime(a, t, secs);
    },

    /* ── files ─────────────────────────────────────────────────────────── */
    url: function (kind, key) {
      var f = S.sheet && S.sheet.files;
      var name = (f && f[kind] && f[kind][key]) || (key + '.mp3');
      var base = (f && f.base) || (R.BASE + (S.sheet ? S.sheet.work : '') + '/sound/');
      return /^https?:/.test(name) ? name : base + name;
    },
    buffer: function (url) {
      if (S._buffers[url] !== undefined) return Promise.resolve(S._buffers[url]);
      return fetch(url).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.arrayBuffer();
      }).then(function (b) {
        return new Promise(function (ok, no) { S.ctx().decodeAudioData(b, ok, no); });
      }).then(function (buf) {
        S._buffers[url] = buf; return buf;
      })['catch'](function (e) {
        S._buffers[url] = null;
        S.missing.push(url);
        console.warn('Sound: cannot load ' + url + ' (' + (e && e.message) + ') — playing without it.');
        return null;
      });
    },

    /* ── the sheet and the chapter ─────────────────────────────────────── */
    prepare: function () {
      var work = R.sheet && R.sheet.work;
      if (!work) return Promise.resolve(null);
      S.state = 'loading';
      var need = [R._json(work + '/sound.json')];
      if (R.sheet.chapter == null) need.push(R._json(work + '/index.json'));
      return Promise.all(need).then(function (got) {
        S.sheet = got[0];
        var n = R.sheet.chapter;
        if (n == null && got[1]) {
          /* ch 1 and ch 2 both point at ep01.json in index.json today, so a
             scripted match wins, and an ambiguity is said out loud */
          var hits = (got[1].chapters || []).filter(function (c) { return c.file === S._path; });
          var hit = hits.filter(function (c) { return c.status === 'scripted'; })[0] || hits[0];
          if (hits.length > 1) {
            console.warn('Sound: index.json maps ' + hits.length + ' chapters to ' + S._path +
                         ' — using chapter ' + (hit && hit.n) + '. Set "chapter" on the cue sheet to settle it.');
          }
          n = hit && hit.n;
        }
        S.chapter = n == null ? null : n;
        var ch = (S.sheet.chapters || []).filter(function (c) { return c.n === S.chapter; })[0];
        if (!ch) console.warn('Sound: no chapter found for ' + S._path + ' — no bed.');
        else if (ch.sfx && ch.sfx.length) {
          console.log('Sound: chapter ' + ch.n + ' lists ' + ch.sfx.join(', ') +
                      ' — fired only where a cue carries them.');
        }
        return ch || null;
      })['catch'](function (e) {
        console.warn('Sound: no sound sheet for ' + work + ' (' + e.message + ').');
        return null;
      });
    },

    /* ── the bed ───────────────────────────────────────────────────────── */
    level: function (state) {
      var b = S.sheet && S.sheet.beds && S.sheet.beds[S.bed];
      var lv = b && b.levels && state != null ? b.levels[String(state)] : null;
      return BED_LEVEL * (typeof lv === 'number' ? lv : 1);
    },

    startBed: function (key, state) {
      if (!key) return Promise.resolve();
      if (S._cur && S._cur.key === key) { S.setState(state); return Promise.resolve(); }
      return S.buffer(S.url('beds', key)).then(function (buf) {
        if (!buf) return;
        var ctx = S.ctx(), g = ctx.createGain(), srcs = [];
        g.gain.value = 0;
        g.connect(S._duck);
        LAYER.forEach(function (L, i) {
          var src = ctx.createBufferSource(), lg = ctx.createGain();
          var len = Math.min(PRIMES[i], buf.duration);
          src.buffer = buf; src.loop = true;
          src.loopStart = 0; src.loopEnd = len;
          src.playbackRate.value = L.rate;
          lg.gain.value = L.gain;
          src.connect(lg); lg.connect(g);
          src.start(0, (buf.duration * L.at) % len);
          srcs.push(src);
        });
        var old = S._cur;
        S.bed = key;
        var to = S.level(state);
        if (old) {                          /* 8 s equal-power crossfade */
          S.curve(old.gain.gain, old.gain.gain.value, 0, 8, false);
          S.curve(g.gain, 0, to, 8, true);
          S._retire(old, 8.2);
        } else {
          g.gain.value = 0.0001;
          S.fade(g.gain, to, 4);            /* bed in: 4 s */
        }
        S._cur = { key: key, gain: g, srcs: srcs, state: state };
        console.log('Sound: bed "' + key + '"' + (state ? ' state ' + state : '') + ' on the engine context');
      });
    },

    /* state change: 11 s, between two mixes of the same material */
    setState: function (state) {
      if (!S._cur || state == null || state === S._cur.state) return;
      S._cur.state = state;
      S.fade(S._cur.gain.gain, S.level(state), 11);
    },

    _retire: function (b, after) {
      setTimeout(function () {
        b.srcs.forEach(function (s) { try { s.stop(); } catch (e) {} });
        try { b.gain.disconnect(); } catch (e) {}
      }, after * 1000);
    },

    endBed: function (secs) {
      if (!S._cur) return;
      S.fade(S._cur.gain.gain, 0, secs);
      S._retire(S._cur, secs + 0.2);
      S._cur = null; S.bed = null;
    },

    /* ── the score ─────────────────────────────────────────────────────── */
    startScore: function (key) {
      if (!key) { if (S._scoreCur) S.endScore(8); return Promise.resolve(); }
      if (S._scoreCur && S._scoreCur.key === key) return Promise.resolve();
      return S.buffer(S.url('score', key)).then(function (buf) {
        if (!buf) return;
        var ctx = S.ctx(), g = ctx.createGain(), src = ctx.createBufferSource();
        src.buffer = buf; src.loop = true;
        src.connect(g); g.connect(S._scoreDuck);
        g.gain.value = 0;
        src.start(0);
        var old = S._scoreCur;
        if (old) {                            /* 10 s equal-power crossfade */
          S.curve(old.gain.gain, old.gain.gain.value, 0, 10, false);
          S.curve(g.gain, 0, SCORE_LEVEL, 10, true);
          setTimeout(function () { try { old.src.stop(); old.gain.disconnect(); } catch (e) {} }, 10200);
        } else {
          g.gain.value = 0.0001;
          S.fade(g.gain, SCORE_LEVEL, 6);     /* score in: 6 s */
        }
        S._scoreCur = { key: key, gain: g, src: src };
        S.score = key;
        console.log('Sound: score "' + key + '"');
      });
    },

    endScore: function (secs) {
      var c = S._scoreCur;
      if (!c) return;
      S.fade(c.gain.gain, 0, secs);
      setTimeout(function () { try { c.src.stop(); c.gain.disconnect(); } catch (e) {} }, secs * 1000 + 200);
      S._scoreCur = null; S.score = null;
    },

    /* ── music under one line ─────────────────────────────────────────── */
    startUnder: function (key, cueN) {
      return S.buffer(S.url('under', key)).then(function (buf) {
        if (!buf || S.state !== 'playing') return;
        var ctx = S.ctx(), g = ctx.createGain(), src = ctx.createBufferSource();
        src.buffer = buf; src.loop = true;
        src.connect(g); g.connect(S._bus);
        g.gain.value = 0.0001;
        /* each use begins at a different, seeded point in the piece, so a
           fill heard many times in a production is never heard the same way */
        var off = seeded((R.sheet.work || '') + '|' + (R.sheet.episode || '') + '|' + cueN + '|' + key)() * buf.duration;
        src.start(0, off);
        S.fade(g.gain, UNDER_LEVEL, 1.5);
        if (S._scoreCur) S.fade(S._scoreCur.gain.gain, SCORE_LEVEL * 0.3, 2.0);   /* the score steps back */
        S._under = { key: key, gain: g, src: src };
        console.log('Sound: under "' + key + '"');
      });
    },

    endUnder: function (secs) {
      var u = S._under;
      if (!u) return;
      S._under = null;
      S.fade(u.gain.gain, 0, secs);
      setTimeout(function () { try { u.src.stop(); u.gain.disconnect(); } catch (e) {} }, secs * 1000 + 200);
      if (S._scoreCur) S.fade(S._scoreCur.gain.gain, SCORE_LEVEL, secs + 2);    /* and returns */
    },

    /* both layers sit down while a cue is read, and come back on pause/end */
    duck: function (on) {
      if (on) { S.slide(S._duck.gain, DUCK_TO, 0.25); S.slide(S._scoreDuck.gain, SCORE_DUCK, 0.25); }
      else    { S.slide(S._duck.gain, 1, 1.2);        S.slide(S._scoreDuck.gain, 1, 1.2); }
    },

    /* ── one-shots: no fade in, the attack IS the sound ────────────────── */
    fire: function (key, cueN, when, salt) {
      return S.buffer(S.url('oneshots', key)).then(function (buf) {
        if (!buf) return;
        var ctx = S.ctx(), src = ctx.createBufferSource(), g = ctx.createGain();
        var at = (when && when > ctx.currentTime) ? when : 0;
        var rnd = seeded((R.sheet.work || '') + '|' + (R.sheet.episode || '') + '|' + cueN + '|' + key + (salt ? '|' + salt : ''));
        src.buffer = buf;
        src.playbackRate.value = 1 + (rnd() * 2 - 1) * 0.04;
        if (src.detune) src.detune.value = (rnd() * 2 - 1) * 40;
        g.gain.value = SFX_LEVEL;
        src.connect(g); g.connect(S._bus);
        src.start(at);
        if (at) {
          var q = { src: src, at: at };
          S._queued.push(q);
          src.onended = function () { var k = S._queued.indexOf(q); if (k >= 0) S._queued.splice(k, 1); };
        }
      });
    },

    /* scheduled one-shots that have not sounded yet are cancelled on pause,
       stop, seek or skip — a door must not bang into a silence */
    cancelQueued: function () {
      var now = S._ctx ? S._ctx.currentTime : 0;
      S._queued.forEach(function (q) { if (q.at > now) { try { q.src.stop(); } catch (e) {} } });
      S._queued = [];
    },

    keyOf: function (e) { return typeof e === 'string' ? e : (e && e.key); },

    cps: function (who) { return S._cps[who] || (S.sheet && S.sheet.chars_per_second) || 15; },

    /* the cue has made its first sound: place its anchored one-shots */
    voiceStarted: function () {
      if (S._underNext && S.state === 'playing') { var uk = S._underNext; S._underNext = null; S.startUnder(uk, S._underCue); }
      var p = S._pending;
      if (!p || !S._ctx || S.state !== 'playing') return;
      S._pending = null;
      var t0 = S._ctx.currentTime + 0.05, text = String(p.cue.text || ''), who = p.who;
      S._cueT0 = { i: p.i, t0: t0, len: text.length, who: who };
      p.items.forEach(function (e) {
        var idx = text.indexOf(e.at), secs = 0;
        if (idx < 0) console.warn('Sound: anchor "' + e.at + '" not in cue ' + (p.i + 1) + ' — playing at its start.');
        else secs = (idx + e.at.length) / S.cps(who);
        S.fire(e.key, p.cue.n || p.i + 1, t0 + Math.max(0, secs + (e.offset || 0)), e.at);
      });
    },

    /* the cue has ended: learn this speaker's pace from how long it took */
    measure: function () {
      var c = S._cueT0;
      if (!c || !S._ctx) return;
      S._cueT0 = null;
      var d = S._ctx.currentTime - c.t0;
      if (d < 1.5 || c.len < 40) return;                 /* too short to measure honestly */
      var obs = Math.max(8, Math.min(25, c.len / d));
      S._cps[c.who] = S._cps[c.who] ? 0.6 * S._cps[c.who] + 0.4 * obs : obs;
    },

    /* ── following the reader ──────────────────────────────────────────── */
    begin: function () {
      S._fired = -1;
      S.ctx();
      S.fade(S._bus.gain, 1, 0.05);
      S.duck(true);
      return S.prepare().then(function (ch) {
        S.state = 'playing';
        /* every one-shot the sheet uses is fetched before the first cue, so
           a door on cue 1 lands ahead of the voice rather than after it */
        var pre = [];
        (R.sheet.cues || []).forEach(function (c) {
          (c.sfx || []).forEach(function (e) { var k = S.keyOf(e); if (k) pre.push(S.buffer(S.url('oneshots', k))); });
          if (c.under) pre.push(S.buffer(S.url('under', c.under)));
        });
        if (ch) pre.push(S.startBed(ch.bed, ch.state));
        if (ch) pre.push(S.startScore(ch.score || null));
        return Promise.all(pre);
      });
    },

    onCue: function (cue, i) {
      var again = (i === S._fired);         /* resume or retry re-speaks the same cue */
      S._fired = i;
      if (again) S._cueT0 = null; else { S.measure(); if (cue.state != null) S.setState(cue.state); }
      if (!again || !S._under) {
        if (S._under && S._under.key !== cue.under) S.endUnder(2.5);
        S._underNext = (cue.under && !(S._under && S._under.key === cue.under)) ? cue.under : null;
        S._underCue = cue.n || i + 1;
      }
      var now = [], later = [];
      (cue.sfx || []).forEach(function (e) {
        if (typeof e === 'string') now.push(e);
        else if (e && e.key && e.at) later.push(e);
        else if (e && e.key) now.push(e.key);
      });
      if (!again) now.forEach(function (k) { S.fire(k, cue.n || i + 1); });
      S._pending = later.length ? { i: i, cue: cue, items: later, who: cue.role || '' } : null;
    },

    off: function () {
      S.state = 'off';
      if (S._bus) S.fade(S._bus.gain, 0, 1.5);
      S.endBed(1.5);
      S.endScore(1.5);
      S.endUnder(1.5); S._underNext = null;
    }
  };

  /* deterministic: same seed, same door */
  function seeded(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return function () {
      h = (h + 0x6D2B79F5) | 0;
      var t = Math.imul(h ^ (h >>> 15), 1 | h);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ── the hooks ───────────────────────────────────────────────────────── */
  var _load = R.load, _play = R.play, _next = R._next,
      _pause = R.pause, _resume = R.resume, _stop = R.stop;

  R.load = function (path) { if (path) S._path = path; return _load.apply(R, arguments); };

  /* The sound sheet is read BEFORE the first cue, so a one-shot on cue 1
     knows where its file is. The context is resumed synchronously, inside
     the click on "Begin the reading", because a browser only allows that
     during a gesture. With no engine, the reader refuses as it always did. */
  R.play = function (path) {
    if (!R.engine()) return _play.apply(R, arguments);
    S.ctx();
    var pre = path ? R.load(path) : Promise.resolve(R.sheet);
    return pre
      .then(function () { return S.begin(); })
      ['catch'](function (e) { console.warn('Sound: ' + (e && e.message) + ' — reading without sound.'); })
      .then(function () { return _play.call(R); })
      ['catch'](function (e) { S.off(); throw e; });
  };

  R._next = function () {
    var cues = R.sheet && R.sheet.cues;
    if (R.state === 'reading' && cues && R.i < cues.length) S.onCue(cues[R.i], R.i);
    _next.apply(R, arguments);
    if (R.state === 'done') {
      S.duck(false);
      S.endUnder(2.5);
      S.endBed(6);                          /* bed out: 6 s */
      S.endScore(8);                        /* score out: 8 s — after the bed */
      S.state = 'idle';
    }
  };

  R.pause = function () {
    _pause.apply(R, arguments);
    S.cancelQueued(); S._cueT0 = null; S._underNext = null; S.endUnder(1.5);
    if (S.state === 'playing') { S.state = 'paused'; S.duck(false); }
  };

  R.resume = function () {
    if (S.state === 'paused') { S.state = 'playing'; S.duck(true); }
    _resume.apply(R, arguments);
  };

  R.stop = function () {
    S.cancelQueued(); S._pending = null; S._cueT0 = null;
    _stop.apply(R, arguments);
    if (S.state === 'playing' || S.state === 'paused') S.off();
  };

  /* a jump in the cue sheet takes the previous cue's waiting sounds with it */
  ['seek', 'skip'].forEach(function (name) {
    var orig = R[name];
    if (typeof orig !== 'function') return;
    R[name] = function () { S.cancelQueued(); S._pending = null; S._cueT0 = null; return orig.apply(R, arguments); };
  });

  /* the engine announces each line's first sound; anchored one-shots are placed from it */
  try { window.addEventListener('amenti:voice-started', function () { S.voiceStarted(); }); } catch (e) {}

  Amenti.sound = S;

  console.log('%c Amenti readings · sound ready ',
              'background:#d4a017;color:#000;padding:2px 6px',
              '· engine context · Amenti.sound.state');
})();
