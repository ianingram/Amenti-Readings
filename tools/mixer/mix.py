#!/usr/bin/env python3
"""Amenti-Readings/tools/mixer/mix.py · 13 Nov 2026
THE OFFLINE MIXER, PART TWO: THE MIX.

Builds a chapter's road track straight from its cue sheet, without playing
it in real time. fetch_voice.js has already written every measure the engine
would speak (from the R2 cache) and manifest.json. This file replays what
reader.js, sound.js and the engine do in the browser, on a clock of its own:

  voice    measures back to back, each followed by its rest, as the engine
           schedules them; a recorded cue or scene plays its file
  bed      three loops of one recording at 37/53/71 s, rates 1, .965, 1.035,
           ducked to 0.45 while reading; 4 s in, 8 s equal-power crossfade,
           11 s state changes, 6 s out
  score    looped at its own rate, its own level (files.levels), ducked to
           0.5, breathing (files.breath); 6 s in, 10 s crossfade, phase kept
           between loops of equal length, 8 s out, "cut" stops it in 30 ms
  under    a looped fill under one line, the score stepping back to 30 %
  sfx      one-shots, seeded rate and detune, at the cue or on their words,
           placed inside the measure that holds them

Every gain change is the same Web Audio automation sound.js schedules
(setValue, linear and exponential ramps, value curves, cancel-and-hold),
evaluated here sample by sample. Seeds are the same, so a door bangs at the
same rate and pitch as in the browser.

usage: mix.py <repo-root> <manifest-dir> <out.m4a>
"""
import json, math, os, re, subprocess, sys
import numpy as np

SR = 44100
LAT = 0.12        # cue start to first word: voice lookup, shelf, decode, +0.05
GAP = 0.02        # last word ends to next cue starts (onended)
REC_LAT = 0.05    # a recorded cue's file starts after its cue
T0 = 1.0          # the first cue, after the bed and score have started
BED_LEVEL, DUCK_TO, SFX_LEVEL = 0.32, 0.45, 0.7
SCORE_LEVEL, SCORE_DUCK, UNDER_LEVEL = 0.26, 0.5, 0.34
PRIMES = [37, 53, 71]
LAYER = [(1.000, 0.00, 0.60), (0.965, 0.37, 0.45), (1.035, 0.71, 0.35)]
READINGS = 'https://ianingram.github.io/Amenti-Readings/'
RAW = 'https://raw.githubusercontent.com/ianingram/Amenti-Readings/main/'

log = lambda *a: print(*a, file=sys.stderr, flush=True)


# ── the seeded generator, bit for bit as sound.js ──────────────────────────
def i32(x):
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x & 0x80000000 else x

def imul(a, b):
    return i32((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF))

def seeded(s):
    h = i32(2166136261)
    units = s.encode('utf-16-le')
    for k in range(0, len(units), 2):
        h = i32(h ^ (units[k] | units[k + 1] << 8))
        h = imul(h, 16777619)
    st = [h]
    def rnd():
        h = i32(st[0] + 0x6D2B79F5); st[0] = h
        t = imul(h ^ ((h & 0xFFFFFFFF) >> 15), 1 | h)
        t = i32((t + imul(t ^ ((t & 0xFFFFFFFF) >> 7), 61 | t)) ^ t)
        return ((t ^ ((t & 0xFFFFFFFF) >> 14)) & 0xFFFFFFFF) / 4294967296
    return rnd

def jsstr(v):
    """what JS makes of (x || '') inside a string"""
    if v is None or v == '' or v == 0 or v is False: return ''
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)


# ── an AudioParam ─────────────────────────────────────────────────────────
class Param:
    def __init__(self, v):
        self.default = v
        self.ev = []       # (time, kind, value, extra): set | lin | exp | curve(value=array, extra=dur)

    def _segments(self):
        """events in order -> list of (t0, t1, f) where f maps times to values"""
        ev = sorted(self.ev, key=lambda e: e[0])
        segs, pt, pv = [], -1e9, self.default
        for t, kind, v, x in ev:
            if kind == 'set':
                segs.append((pt, t, ('const', pv))); pt, pv = t, v
            elif kind in ('lin', 'exp'):
                segs.append((pt, t, (kind, pt, pv, t, v))); pt, pv = t, v
            elif kind == 'curve':
                segs.append((pt, t, ('const', pv)))
                segs.append((t, t + x, ('curve', t, x, v)))
                pt, pv = t + x, float(v[-1])
        segs.append((pt, 1e12, ('const', pv)))
        return segs

    def compile(self):
        self.segs = self._segments()
        self.starts = np.array([s[0] for s in self.segs])

    def value(self, t):
        return float(self.eval(np.array([t]))[0]) if not hasattr(self, 'segs') else float(self.eval(np.array([t]))[0])

    def at(self, t):
        self.compile()
        v = float(self.eval(np.array([t]))[0])
        del self.segs
        return v

    def eval(self, ts):
        out = np.empty_like(ts)
        i0 = max(0, int(np.searchsorted(self.starts, ts[0], 'right')) - 1)
        i1 = int(np.searchsorted(self.starts, ts[-1], 'right'))
        for s0, s1, f in self.segs[i0:i1]:
            a = int(np.searchsorted(ts, s0, 'left')); b = int(np.searchsorted(ts, s1, 'left'))
            if b <= a: continue
            x = ts[a:b]
            k = f[0]
            if k == 'const': out[a:b] = f[1]
            elif k == 'lin':
                _, t0, v0, t1, v1 = f
                out[a:b] = v1 if t1 <= t0 else v0 + (v1 - v0) * (x - t0) / (t1 - t0)
            elif k == 'exp':
                _, t0, v0, t1, v1 = f
                if t1 <= t0 or v0 <= 0 or v1 <= 0 or (v0 > 0) != (v1 > 0): out[a:b] = v0
                else: out[a:b] = v0 * (v1 / v0) ** ((x - t0) / (t1 - t0))
            elif k == 'curve':
                _, t0, d, arr = f
                pos = np.clip((x - t0) / d * (len(arr) - 1), 0, len(arr) - 1)
                out[a:b] = np.interp(pos, np.arange(len(arr)), arr)
        return out

    # the calls sound.js makes
    def set(self, v, t): self.ev.append((t, 'set', v, None))
    def lin(self, v, t): self.ev.append((t, 'lin', v, None))
    def exp(self, v, t): self.ev.append((t, 'exp', v, None))
    def curve(self, arr, t, d): self.ev.append((t, 'curve', np.asarray(arr, float), d))
    def cancel(self, t):
        self.ev = [e for e in self.ev if (e[0] if e[1] != 'curve' else e[0]) < t]
    def hold(self, t):
        v = self.at(t)
        keep = []
        for e in self.ev:
            if e[1] == 'curve':
                if e[0] + e[3] <= t: keep.append(e)
            elif e[0] <= t: keep.append(e)
        self.ev = keep
        self.set(v, t)
        return v


def fade(p, to, secs, t):
    v = p.hold(t)
    p.set(max(v, 0.0001), t)
    p.exp(max(to, 0.0001), t + secs)
    if to <= 0: p.set(0, t + secs + 0.01)

def slide(p, to, secs, t):
    p.hold(t); p.lin(to, t + secs)

def eqcurve(p, frm, to, secs, rising, t):
    x = np.linspace(0, math.pi / 2, 64)
    a = to * np.sin(x) if rising else frm * np.cos(x)
    a[-1] = to if rising else 0
    p.hold(t); p.curve(a, t, secs)


# ── audio files ────────────────────────────────────────────────────────────
class Files:
    def __init__(self, root):
        self.root, self.cache = root, {}

    def path(self, url):
        for pre in (READINGS, RAW):
            if url.startswith(pre): return os.path.join(self.root, url[len(pre):])
        return url

    def load(self, url):
        if url in self.cache: return self.cache[url]
        p = self.path(url)
        buf = None
        if os.path.exists(p) or re.match(r'https?:', p):
            r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                               capture_output=True)
            if r.returncode == 0 and r.stdout:
                buf = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()
        if buf is None: log('  missing: ' + url + ' — playing without it')
        self.cache[url] = buf
        return buf


class Src:
    def __init__(self, buf, start, off=0.0, rate=1.0, loop=False, loop_end=None, gain=1.0, params=(), stop=None, breath=None):
        self.buf, self.start, self.off, self.rate = buf, start, off, rate
        self.loop, self.gain, self.params, self.breath = loop, gain, list(params), breath
        self.dur = len(buf) / SR
        self.loop_end = min(loop_end or self.dur, self.dur)
        self.stop = stop if stop is not None else (1e12 if loop else start + (self.dur - off) / rate)


# ── the chapter ────────────────────────────────────────────────────────────
class Mix:
    def __init__(self, root, man):
        self.root, self.man = root, man
        self.work = man['work']
        self.sheet = json.load(open(os.path.join(root, self.work, 'sound.json')))
        self.f = self.sheet.get('files', {})
        self.files = Files(root)
        self.srcs = []
        self.duck, self.sduck = Param(1.0), Param(1.0)
        self.bed = None; self.score = None; self.under = None
        self.pending = None; self.under_next = None; self.under_cue = None
        self.fired = -1
        b = self.f.get('breath')
        self.breath = None
        if b:
            mn = b.get('min', 0.4); P = b.get('periods', [43, 71, 113])
            W, ph = [0.5, 0.3, 0.2], [0, 1.3, 2.1]
            self.breath = lambda t: mn + (1 - mn) * (0.5 + 0.5 * sum(W[i] * np.sin(2 * np.pi * t / P[i] + ph[i]) for i in range(min(3, len(P)))))

    def url(self, kind, key):
        name = (self.f.get(kind) or {}).get(key) or key + '.mp3'
        base = self.f.get('base') or (RAW + self.work + '/sound/')
        return name if re.match(r'https?:', name) else base + name

    def buf(self, kind, key): return self.files.load(self.url(kind, key))

    # bed
    def level(self, state):
        b = (self.sheet.get('beds') or {}).get(self.bed and self.bed['key'] or '')
        lv = (b.get('levels') or {}).get(str(state)) if (b and state is not None and isinstance(b.get('levels'), dict)) else None
        return BED_LEVEL * (lv if isinstance(lv, (int, float)) and not isinstance(lv, bool) else 1)

    def start_bed(self, key, state, t):
        if not key: return
        if self.bed and self.bed['key'] == key: return self.set_state(state, t)
        buf = self.buf('beds', key)
        if buf is None: return
        g = Param(0.0); srcs = []
        d = len(buf) / SR
        for i, (rate, at, lg) in enumerate(LAYER):
            ln = min(PRIMES[i], d)
            s = Src(buf, t, (d * at) % ln, rate, True, ln, lg, [g, self.duck])
            srcs.append(s); self.srcs.append(s)
        old = self.bed
        self.bed = {'key': key, 'g': g, 'srcs': srcs, 'state': state}
        to = self.level(state)
        if old:
            eqcurve(old['g'], old['g'].at(t), 0, 8, False, t)
            eqcurve(g, 0, to, 8, True, t)
            for s in old['srcs']: s.stop = min(s.stop, t + 8.2)
        else:
            g.default = 0.0001
            fade(g, to, 4, t)

    def set_state(self, state, t):
        if not self.bed or state is None or state == self.bed['state']: return
        self.bed['state'] = state
        fade(self.bed['g'], self.level(state), 11, t)

    def end_bed(self, secs, t):
        if not self.bed: return
        fade(self.bed['g'], 0, secs, t)
        for s in self.bed['srcs']: s.stop = min(s.stop, t + secs + 0.2)
        self.bed = None

    # score
    def score_level(self, key):
        lv = self.f.get('levels') or {}
        return lv[key] if isinstance(lv.get(key), (int, float)) else SCORE_LEVEL

    def start_score(self, key, t, xfade=None, when=None, cut=False):
        if not key: return self.end_score(xfade if xfade is not None else 8, t, when, cut)
        if self.score and self.score['key'] == key: return
        buf = self.buf('score', key)
        if buf is None: return
        d = len(buf) / SR
        at = max(when or 0, t + 0.02)
        level, old, off = self.score_level(key), self.score, 0.0
        if old and abs(old['dur'] - d) < 0.003: off = (((at - old['t0']) % d) + d) % d
        g = Param(0.0001)
        s = Src(buf, at, off, 1.0, True, None, 1.0, [g, self.sduck], breath=self.breath)
        self.srcs.append(s)
        if old:
            xf = max(0.05, xfade if xfade is not None else 10)
            x = np.linspace(0, math.pi / 2, 48)
            old['g'].cancel(at); old['g'].curve(old['level'] * np.cos(x) + 0.0001, at, xf)
            g.curve(level * np.sin(x) + 0.0001, at, xf)
            old['src'].stop = min(old['src'].stop, at + xf + 0.1)
        else:
            g.set(0.0001, at)
            g.exp(level, at + max(0.05, xfade if xfade is not None else 6))
        self.score = {'key': key, 'g': g, 'src': s, 'level': level, 't0': at - off, 'dur': d}

    def end_score(self, secs, t, when=None, cut=False):
        c = self.score
        if not c: return
        at = max(when or 0, t + 0.01); p = c['g']
        p.cancel(at); p.set(c['level'], at)
        if cut: p.lin(0.0001, at + 0.03); c['src'].stop = min(c['src'].stop, at + 0.06)
        else: p.exp(0.0001, at + max(0.05, secs)); c['src'].stop = min(c['src'].stop, at + secs + 0.1)
        self.score = None

    # under
    def start_under(self, key, cue_n, t):
        buf = self.buf('under', key)
        if buf is None: return
        d = len(buf) / SR
        off = seeded(jsstr(self.work) + '|' + jsstr(self.man.get('episode')) + '|' + jsstr(cue_n) + '|' + key)() * d
        g = Param(0.0001)
        s = Src(buf, t, off, 1.0, True, None, 1.0, [g]); self.srcs.append(s)
        fade(g, UNDER_LEVEL, 1.5, t)
        if self.score: fade(self.score['g'], self.score['level'] * 0.3, 2.0, t)
        self.under = {'key': key, 'g': g, 'src': s}

    def end_under(self, secs, t):
        u = self.under
        if not u: return
        self.under = None
        fade(u['g'], 0, secs, t); u['src'].stop = min(u['src'].stop, t + secs + 0.2)
        if self.score: fade(self.score['g'], self.score['level'], secs + 2, t)

    # one-shots
    def fire(self, key, cue_n, t, when=None, salt=None):
        buf = self.buf('oneshots', key)
        if buf is None: return
        d = len(buf) / SR
        at = when if (when and when > t) else t
        into = (t - when) if (when and when < t and when > t - d) else 0.0
        rnd = seeded(jsstr(self.work) + '|' + jsstr(self.man.get('episode')) + '|' + jsstr(cue_n) + '|' + key + ('|' + salt if salt else ''))
        rate = 1 + (rnd() * 2 - 1) * 0.04
        rate *= 2 ** (((rnd() * 2 - 1) * 40) / 1200)
        sl = self.f.get('sfx_levels') or {}
        gain = sl[key] if isinstance(sl.get(key), (int, float)) else SFX_LEVEL
        self.srcs.append(Src(buf, at, into, rate, False, None, gain))

    # following the cues
    def on_cue(self, cue, i, t):
        again = (i == self.fired)
        if self.pending and self.pending['i'] != i:
            for e in self.pending['items']:
                if not e.get('_done'): log('  anchor "%s" never found in cue %s' % (e.get('at'), self.pending['n']))
        self.fired = i
        if not again:
            if cue.get('bed'): self.start_bed(cue['bed'], cue.get('state'), t)
            elif cue.get('state') is not None: self.set_state(cue['state'], t)
        if not again or not self.under:
            if self.under and self.under['key'] != cue.get('under'): self.end_under(2.5, t)
            self.under_next = cue['under'] if (cue.get('under') and not (self.under and self.under['key'] == cue['under'])) else None
            self.under_cue = cue.get('n') or i + 1
        now, later = [], []
        for e in cue.get('sfx') or []:
            if isinstance(e, str): now.append(e)
            elif e and e.get('key') and e.get('at'): later.append(dict(e))
            elif e and e.get('key'): now.append(e['key'])
        for k in now: self.fire(k, cue.get('n') or i + 1, t)
        if 'score' in cue:
            sc = cue['score'] if isinstance(cue['score'], list) else [cue['score']]
            for ev in sc:
                if ev is None or isinstance(ev, str): ev = {'key': ev}
                if ev.get('at'): e = dict(ev); e['_score'] = True; later.append(e)
                else: self.start_score(ev.get('key'), t, ev.get('xfade'), None, bool(ev.get('cut')))
        self.pending = {'i': i, 'n': cue.get('n') or i + 1, 'items': later} if later else None

    def on_measure(self, at, dur, text, now):
        p = self.pending
        if not p: return
        ws = lambda x: re.sub(r'\s+', ' ', str(x or '')).strip()
        ch = ws(text); L = len(ch) or 1; left = []
        for e in p['items']:
            if e.get('_done'): continue
            a = ws(e.get('at')); when = None
            if e.get('_carry') is not None: when = at + dur * min(1, e['_carry'] / L)
            else:
                idx = ch.find(a)
                if idx >= 0: when = at + dur * ((idx + len(a)) / L)
                else:
                    for k in range(min(len(a) - 1, len(ch)), 5, -1):
                        if ch[-k:] == a[:k]: e['_carry'] = len(a) - k; break
            if when is None: left.append(e); continue
            e['_done'] = True
            when += e.get('offset') or 0
            if e.get('_score'): self.start_score(e.get('key'), max(now, when - 0.12), e.get('xfade'), when, bool(e.get('cut')))
            else: self.fire(e['key'], p['n'], now, when, e.get('at'))
        if not left: self.pending = None

    def run(self):
        m, cues = self.man, self.man['cues']
        # begin: the duck sits down, the chapter's bed and score start
        ch = None
        n = m.get('chapter')
        if n is None:
            try:
                ix = json.load(open(os.path.join(self.root, self.work, 'index.json')))
                hits = [c for c in ix.get('chapters', []) if c.get('file') == '%s/ep%s.json' % (self.work, m['nn'])]
                hit = ([c for c in hits if c.get('status') == 'scripted'] or hits or [None])[0]
                n = hit and hit.get('n')
            except Exception: pass
        for c in self.sheet.get('chapters', []):
            if c.get('n') == n: ch = c
        if ch:
            self.start_bed(ch.get('bed'), ch.get('state'), 0.05)
            self.start_score(ch.get('score') or None, 0.05)
        else: log('  no chapter %s in sound.json — no bed' % n)
        # the curtain: a chapter's lead is seconds of score at full voice before
        # the first cue; the duck comes down over the last 2.5 s (sound.js)
        lead = float((ch or {}).get('lead') or 0)
        t_first = (0.05 + lead) if lead else T0
        if lead:
            self.duck.set(1.0, 0); self.sduck.set(1.0, 0)
            slide(self.duck, DUCK_TO, 2.5, max(0.05, t_first - 2.5)); slide(self.sduck, SCORE_DUCK, 2.5, max(0.05, t_first - 2.5))
        else:
            slide(self.duck, DUCK_TO, 0.25, 0); slide(self.sduck, SCORE_DUCK, 0.25, 0)

        t, i, voice, stalled = t_first, 0, [], []
        idx_of = {c['n']: k for k, c in enumerate(cues)}
        while i < len(cues):
            c = cues[i]
            self.on_cue(c, i, t)
            if c['kind'] in ('recorded', 'scene'):
                buf = self.files.load(c['audio'])
                if buf is not None:
                    start = 0.0
                    if c['kind'] == 'scene':
                        for mk in c.get('marks') or []:
                            if mk[0] == c['n']: start = mk[1]; break
                    s = Src(buf, t + REC_LAT, start); self.srcs.append(s)
                    t = s.stop + GAP
                    i = (idx_of.get(c['through'], i) + 1) if c['kind'] == 'scene' else i + 1
                    continue
                log('  recorded cue %s will not play — speaking it is not possible offline' % c['n'])
                i += 1; continue
            if c['kind'] == 'covered': i += 1; continue
            # spoken: measures back to back
            nxt, first, end = 0.0, None, None
            now = t + LAT - 0.05
            for k, mz in enumerate(c.get('chunks') or []):
                if not mz.get('file'): continue
                buf = self.files.load(os.path.join(self.mdir, 'voice', mz['file']))
                if buf is None: continue
                rate = mz.get('rate') or 1
                at = max(nxt, t + LAT)
                s = Src(buf, at, 0, rate); self.srcs.append(s)
                dur = s.dur / rate
                self.on_measure(at, dur, mz['text'], now)
                if first is None:
                    first = at
                    if self.under_next:
                        uk = self.under_next; self.under_next = None
                        self.start_under(uk, self.under_cue, at - 0.05)
                nxt = at + dur + (mz.get('rest') or 0)
                end = at + dur
            if first is None:
                if re.search(r'\w', c.get('text') or '', re.U) and re.search(r'[^\W_]', c.get('text') or ''):
                    stalled.append(c['n'])
                    log('  cue %s (%s) has no audio — skipped, as Skip would' % (c['n'], c.get('role')))
                t += 1.2      # a line with no words is a pause, as reader.js holds it
            else: t = end + GAP
            i += 1
        # done
        slide(self.duck, 1, 1.2, t); slide(self.sduck, 1, 1.2, t)
        self.end_under(2.5, t); self.end_bed(6, t); self.end_score(8, t)
        self.end = t
        self.length = t + 8.5
        return stalled

    def render(self, out_wav_pipe, block=1.0):
        for s in self.srcs:
            for p in s.params: p.compile()
        n = int(self.length * SR)
        bs = int(block * SR)
        srcs = sorted(self.srcs, key=lambda s: s.start)
        for b0 in range(0, n, bs):
            b1 = min(n, b0 + bs)
            ts = np.arange(b0, b1) / SR
            acc = np.zeros((b1 - b0, 2), np.float32)
            for s in srcs:
                if s.start >= ts[-1]: break
                if s.stop <= ts[0]: continue
                a = int(np.searchsorted(ts, s.start, 'left')); z = int(np.searchsorted(ts, s.stop, 'left'))
                if z <= a: continue
                x = ts[a:z]
                tau = s.off + (x - s.start) * s.rate
                if s.loop:
                    le = s.loop_end
                    over = tau >= le
                    if over.any(): tau = np.where(over, (tau - le) % le, tau) if le > 0 else tau
                else:
                    ok = tau < s.dur - 1.0 / SR
                    if not ok.all():
                        z = a + int(np.argmin(ok)) if not ok[0] else a
                        x = ts[a:z]; tau = tau[:z - a]
                        if z <= a: continue
                pos = tau * SR
                i0 = np.minimum(pos.astype(np.int64), len(s.buf) - 2)
                fr = (pos - i0).astype(np.float32)[:, None]
                y = s.buf[i0] * (1 - fr) + s.buf[i0 + 1] * fr
                g = np.full(len(x), s.gain, np.float64)
                for p in s.params: g = g * p.eval(x)
                if s.breath: g = g * s.breath(x)
                acc[a:z] += y * g[:, None].astype(np.float32)
            out_wav_pipe.write(acc.tobytes())


def main():
    root, mdir, out = sys.argv[1:4]
    man = json.load(open(os.path.join(mdir, 'manifest.json')))
    nn = re.search(r'ep(\d+)', mdir); man['nn'] = nn.group(1) if nn else ''
    mx = Mix(root, man); mx.mdir = mdir
    stalled = mx.run()
    title = man.get('title') or ''
    num = int(man['nn']) if man['nn'] else 0
    alb = {'dracula': 'Dracula', 'a-christmas-carol': 'A Christmas Carol', 'treasure-island': 'Treasure Island'}.get(mx.work, mx.work) + ' · Amenti Studios'
    log('%s ep%s: %d sources, %.1f s' % (mx.work, man['nn'], len(mx.srcs), mx.length))
    tmp = out + '.part.m4a'
    ff = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                           '-af', 'silenceremove=start_periods=1:start_threshold=-50dB,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.3,apad=pad_dur=2',
                           '-c:a', 'aac', '-b:a', '96k',
                           '-metadata', 'title=Chapter %d · %s' % (num, title), '-metadata', 'track=%d' % num,
                           '-metadata', 'album=' + alb, '-metadata', 'artist=Amenti Studios',
                           '-metadata', 'genre=Audiobook', '-movflags', '+faststart', '-f', 'mp4', tmp], stdin=subprocess.PIPE)
    mx.render(ff.stdin)
    ff.stdin.close()
    if ff.wait() != 0: sys.exit('encode failed')
    os.replace(tmp, out)
    print(json.dumps({'out': out, 'seconds': round(mx.length, 1), 'stalled': stalled}))


if __name__ == '__main__':
    main()
