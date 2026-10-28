"""Hoof engine for Dracula ch I — four horses scored to the text, never a loop.
Every strike is a real recorded hoof (BigSoundBank, CC0) chosen at random, pitched and
placed by a gait model that follows a speed curve: 0 halt, 1 walk, 2 trot, 3 canter, 4 gallop.
"""
import numpy as np, scipy.signal as sg, sys
sys.path.insert(0, '/tmp/claude-0/hb')
from lib import load, SR, B, pieces, cue
S = '/tmp/bsb/src/'; F = '/tmp/cr5/dracula/sound/'
R = np.random.default_rng(1897)

def lp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'low', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def hp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'high', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def db(d): return 10 ** (d / 20)
def fade(x, a, b):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)[:, None] if x.ndim > 1 else np.linspace(0, 1, na)
    if nb: x[-nb:] *= np.linspace(1, 0, nb)[:, None] if x.ndim > 1 else np.linspace(1, 0, nb)
    return x
def pitch(x, semis):
    if abs(semis) < 0.01: return x
    r = 2 ** (semis / 12); n = int(len(x) / r)
    return np.interp(np.arange(n) * r, np.arange(len(x)), x).astype(np.float32)
def norm(x, d=-20):
    r = np.sqrt(np.mean(x ** 2)) + 1e-9; return (x / r * db(d)).astype(np.float32)
def peaknorm(x, d=-6): return (x / (np.abs(x).max() + 1e-9) * db(d)).astype(np.float32)

_ir = {}
def reverb(x, t60=1.2, wet=0.3, seed=0):
    k = (t60, seed)
    if k not in _ir:
        rr = np.random.default_rng(seed); n = int(t60 * SR)
        ir = rr.standard_normal(n).astype(np.float32) * np.exp(-6.9 * np.arange(n) / n)
        _ir[k] = lp(ir, 3500) / np.sqrt(np.sum(ir ** 2))
    y = sg.fftconvolve(x, _ir[k])[:len(x)].astype(np.float32)
    return x * (1 - wet) + y * wet * 3

def onsets(x, thr_db=-30, gap=0.08):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, x ** 2)); d = 20 * np.log10(e + 1e-9)
    on = []; last = -1e9
    for i in np.where((d[1:] > thr_db) & (d[:-1] <= thr_db))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on

def strikes(k, thr, length=0.22, pre=0.004):
    x = load(S + k + '.mp3'); out = []
    for o in onsets(x, thr):
        a = max(0, o - int(pre * SR)); s = x[a:a + int(length * SR)]
        if len(s) < int(length * SR) * 0.9: continue
        out.append(peaknorm(fade(s, 0.002, length * 0.6), -6))
    return out

POOL = {
    'road':  strikes('0610', -30) + strikes('0611', -30),
    'stone': strikes('0496', -32, 0.3),
    'path':  strikes('1854', -32, 0.2),
}
print('strike pool', {k: len(v) for k, v in POOL.items()})

GAITS = {  # (stride seconds, strike phases)
    1: (1.15, [0, .25, .5, .75]),
    2: (0.66, [0, .02, .5, .52]),
    3: (0.58, [0, .16, .30]),
    4: (0.44, [0, .09, .19, .30]),
}

def curve(keys, n):
    """keys: [(t, v)] -> per-sample value, linear between keys."""
    t = np.arange(n) / SR; ks = sorted(keys)
    return np.interp(t, [k[0] for k in ks], [k[1] for k in ks]).astype(np.float32)

def team(n, speed, surface='road', horses=4, semis=0.0, seed=0, snow=None, level=None):
    """Stereo hoofbeats of a team following speed (array per sample)."""
    rr = np.random.default_rng(seed); out = np.zeros((n, 2), np.float32)
    pool = POOL[surface]
    for h in range(horses):
        pan = (h - (horses - 1) / 2) / max(1, horses - 1) * 0.7
        gl, gr = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        t = rr.uniform(0, 0.4); drift = rr.uniform(0.97, 1.03); hsemi = semis + rr.uniform(-1.2, 1.2)
        while t < n / SR:
            i = int(t * SR); s = float(speed[min(i, n - 1)])
            if s < 0.5: t += 0.25; continue
            g = int(np.clip(round(s), 1, 4)); per, ph = GAITS[g]
            # stride shortens smoothly with speed inside a gait
            per = per * (1.0 - 0.12 * (s - g)) * drift * rr.uniform(0.96, 1.04)
            vel = 0.55 + 0.15 * s
            for p in ph:
                tt = t + p * per + rr.normal(0, 0.008)
                j = max(0, int(tt * SR))
                if j >= n: break
                x = pitch(pool[rr.integers(len(pool))], hsemi + rr.uniform(-0.6, 0.6)) * vel * rr.uniform(0.6, 1.0)
                m = min(len(x), n - j)
                out[j:j + m, 0] += x[:m] * gl; out[j:j + m, 1] += x[:m] * gr
            t += per
    if snow is not None:   # muffle progressively: snow is an array 0..1
        soft = lp(out, 700, 2) * 1.6
        out = out * (1 - snow[:, None]) + soft * snow[:, None]
    return out * db(5)

def texture(k, n, seg=None, rate=1.0, seed=0, chunk=(1.0, 2.5)):
    """A non-repeating bed: random chunks of a recording, cross-faded."""
    rr = np.random.default_rng(seed); x = load(S + k + '.mp3')
    if seg: x = x[int(seg[0] * SR):int(seg[1] * SR)]
    if rate != 1.0: x = pitch(x, 12 * np.log2(rate))
    out = np.zeros(n + SR * 3, np.float32); t = 0; xf = int(0.08 * SR)
    while t < n:
        L = int(rr.uniform(*chunk) * SR); a = rr.integers(0, len(x) - L - 1)
        c = x[a:a + L + xf].copy(); c[:xf] *= np.linspace(0, 1, xf); c[-xf:] *= np.linspace(1, 0, xf)
        out[t:t + len(c)] += c; t += L
    return out[:n]

def stereo(x, pan=0.0):
    return np.stack([x * np.sqrt(0.5 * (1 - pan)), x * np.sqrt(0.5 * (1 + pan))], 1).astype(np.float32)

def wheels(n, speed, seed=0):
    w = texture('1316', n, rate=0.62, seed=seed)
    w = lp(hp(w, 40), 700) * np.clip(speed / 3, 0, 1.3)
    return stereo(norm(w, -20) * np.clip(speed / 3, 0, 1.3)) * db(5)

def creaks(n, times, seed=0):
    rr = np.random.default_rng(seed); src = load(S + '2516.mp3'); out = np.zeros(n, np.float32)
    for t in times:
        a = rr.integers(0, len(src) - SR); c = src[a:a + int(rr.uniform(0.4, 0.9) * SR)]
        c = pitch(lp(hp(c, 300), 2500), rr.uniform(-9, -5)); c = fade(c, 0.05, 0.2)
        j = int(t * SR); m = min(len(c), n - j)
        if m > 0: out[j:j + m] += norm(c, -26)[:m]
    return stereo(out)

def one(k, folder=S):
    return load(folder + k + ('' if k.endswith('.mp3') else '.mp3'))

def put(bus, x, t, gain_db=0.0, pan=0.0):
    if x.ndim == 1: x = stereo(x, pan)
    j = int(t * SR)
    if j < 0: x = x[-j:]; j = 0
    m = min(len(x), len(bus) - j)
    if m > 0: bus[j:j + m] += x[:m] * db(gain_db)

# ── the voice, exactly where it sat ──────────────────────────────────────────
GAP = 0.45
def voice(n_cue):
    ps = pieces(n_cue); bs = [b for b in B if b['n'] == n_cue]
    out = []; t = 0.0; spans = []
    for p, b in zip(ps, bs):
        p = pitch_sr(p); out.append((t, p, b['text'])); spans.append((t, t + len(p) / SR, b['text'])); t += len(p) / SR + GAP
    return out, spans, t - GAP

def pitch_sr(p):   # pieces are 24 kHz; lib.load already resamples to SR
    return p

def at(spans, phrase, after=False):
    """Seconds where the phrase is spoken (by character position in its piece)."""
    ph = ' '.join(phrase.split()).lower()
    for a, b, text in spans:
        t = ' '.join(text.split()).lower(); i = t.find(ph)
        if i >= 0:
            k = i + (len(ph) if after else 0)
            return a + (b - a) * k / max(1, len(t))
    raise KeyError(phrase)
