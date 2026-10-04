#!/usr/bin/env python3
"""Chapter 7 — the Demeter. Every score and sound asset the episode plays.

Instruments: Versilian Studios, VSCO 2 Community Edition (CC0; credit requested).
Recordings: thunder (stephan), wolf (US Fish & Wildlife Service), timber creak
(stephan) — all public domain via Wikimedia Commons. Seas synthesized here.
Deterministic (seed 1897).

LOOPS ARE WAV, NOT MP3. An MP3 carries encoder padding at both ends, and a
looped MP3 stutters by a few milliseconds every time round — fatal to a pulse
that is counting souls. Loops are written as 32 kHz mono WAV, cut to an exact
number of bars, so Web Audio's loop is sample-tight. One-shots are MP3.
"""
import numpy as np, scipy.io.wavfile as wv, scipy.signal as sg, subprocess, os, warnings, json
warnings.filterwarnings('ignore')
SR = 48000
V = '/tmp/vsco/'
OUT = '/tmp/snd/ch7/'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1897)
_c = {}

def load(rel, semis=0.0):
    k = (rel, semis)
    if k in _c: return _c[k]
    path = rel if rel.startswith('/') else V + rel
    sr, x = wv.read(path); x = x.astype(np.float32)
    if x.ndim > 1: x = x.mean(1)
    x /= (32768.0 if np.abs(x).max() > 2 else 1.0)
    ratio = SR / sr * (2 ** (-semis / 12))
    if abs(ratio - 1) > 1e-6: x = sg.resample_poly(x, int(round(ratio * 1000)), 1000).astype(np.float32)
    _c[k] = x; return x

def lp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'low', fs=SR, output='sos'), x).astype(np.float32)
def hp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'high', fs=SR, output='sos'), x).astype(np.float32)
def put(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i < 0: return
    n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n] * g
def env(x, pts):
    t = np.arange(len(x)) / SR
    return (x * np.interp(t, [p[0] for p in pts], [p[1] for p in pts])).astype(np.float32)
def reverb(x, rt=2.4, wet=0.25, seed=5, bright=4000):
    r = np.random.default_rng(seed); n = int(rt * SR); tt = np.arange(n) / SR
    ir = lp(r.standard_normal(n) * np.exp(-6.91 * tt / rt), bright); ir /= np.sqrt(np.sum(ir ** 2))
    y = sg.fftconvolve(x, ir)[:len(x)].astype(np.float32)
    return (1 - wet) * x + wet * y
def wrap_reverb(x, rt, wet, seed=5):
    """reverb a LOOP so its tail wraps round to the start — no seam at the loop point"""
    y = reverb(np.concatenate([x, x]), rt, wet, seed)
    return y[len(x):].astype(np.float32)
def peak_db(x, db): return x * (10 ** (db / 20) / (np.abs(x).max() + 1e-12))
def rms_db(x, db): return x * (10 ** (db / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12))

files = {}
def write_mp3(x, name):
    x = np.clip(x, -1, 1); tmp = OUT + name + '.tmp.wav'
    wv.write(tmp, SR, (x * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '160k', OUT + name], check=True)
    os.remove(tmp); files[name] = len(x) / SR
def write_loop(x, name):
    """32 kHz mono WAV, exact length preserved through the resample"""
    x = np.clip(x, -1, 1)
    y = sg.resample_poly(x, 2, 3).astype(np.float32)                 # 48k -> 32k, exact for whole samples
    wv.write(OUT + name, 32000, (y * 32767).astype(np.int16)); files[name] = len(y) / 32000

TIMP_HIT = lambda d, v, r=1: f'Percussion/Timpani/Timpani{d}_Hit_v{v}_rr{r}_Sum.wav'
TIMP_ROLL = lambda d, v: f'Percussion/Timpani/Rolls/Timpani{d}_Roll_v{v}_rr1_Sum.wav'
TOM_LO = lambda dyn, n: f'VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_{dyn}_{n}.wav'
TOM_HI = lambda dyn, n: f'VSCO 1 Percussion/drums/tenor/tenor_higher/tenorH_{dyn}_{n}.wav'
SN = lambda name: f'VSCO 1 Percussion/drums/snare/{name}'
BD = lambda name: f'VSCO 1 Percussion/drums/bass/{name}.wav'
TL = {'ppp': [1], 'pp': [1, 2, 3, 4], 'mp': [1], 'mf': [1, 2, 3, 4], 'f': [1, 2], 'ff': [1, 2, 3], 'fff': [1, 2, 3, 4]}
TH = {'pp': [1], 'p': [1, 2, 3], 'mp': [1, 2], 'mf': [1, 2, 3], 'f': [1, 2, 3], 'ff': [1, 2, 3, 4, 5, 6], 'fff': [1, 2, 3, 4]}

def tom(buf, t, dyn, hi=False, g=1.0, muffle=None):
    tab = TH if hi else TL
    if dyn not in tab: dyn = 'mf'
    n = tab[dyn][rng.integers(len(tab[dyn]))]
    x = load((TOM_HI if hi else TOM_LO)(dyn, n))
    if muffle: x = lp(x, muffle)
    put(buf, x, t, g)
def tom_group(buf, t, n, dyn, spread=0.11, g=1.0):
    for k in range(n): tom(buf, t + k * spread * (0.85 + 0.3 * rng.random()), dyn, hi=bool(rng.random() < .45), g=g * (0.8 + 0.3 * rng.random()))
def sustain(rel, dur, semis=0.0, xf=0.8):
    s = load(rel, semis); head = int(0.25 * SR)
    mid = s[head: max(head + int(1.0 * SR), len(s) - int(0.4 * SR))]
    out = np.zeros(int(dur * SR) + len(s), np.float32); out[:len(s)] += s
    k = int(xf * SR); step = max(int(0.5 * SR), len(mid) - k)
    pos = max(int(0.5 * SR), len(s) - len(mid) // 2 - k)
    w = np.ones(len(mid), np.float32); w[:k] = np.linspace(0, 1, k); w[-k:] = np.linspace(1, 0, k)
    while pos < int(dur * SR): out[pos:pos + len(mid)] += mid * w; pos += step
    return out[:int(dur * SR)]
def timp_roll(buf, t, drum, v, g, dur, fin=0.6, fout=1.2, cut=None):
    x = sustain(TIMP_ROLL(drum, v), dur, xf=0.6)
    if cut: x = lp(x, cut)
    d = len(x) / SR; put(buf, env(x, [(0, 0), (fin, 1), (max(fin, d - fout), 1), (d, 0)]), t, g)
def timp(buf, t, d, v, g=1.0, r=1): put(buf, load(TIMP_HIT(d, v, r)), t, g)
_m = {}
def muf(rel, f):
    if (rel, f) not in _m: _m[(rel, f)] = lp(load(rel), f, 3)
    return _m[(rel, f)]
def lub(buf, t, g, last=False):
    put(buf, muf(TIMP_HIT(4, 1), 260), t, g); put(buf, muf(BD('bdrum_muted_pp_1'), 400), t, 0.8 * g)
    if not last:
        put(buf, muf(TIMP_HIT(4, 1, 2), 220), t + 0.24, 0.6 * g); put(buf, muf(BD('bdrum_muted_ppp_1'), 350), t + 0.24, 0.5 * g)
def heart(buf, t, beats, b0, b1, g0=1.0, g1=0.25, abrupt=False):
    tk = t
    for k in range(beats):
        f = k / max(1, beats - 1)
        lub(buf, tk, g0 + (g1 - g0) * f, last=(k == beats - 1 and not abrupt))
        tk += 60.0 / (b0 + (b1 - b0) * f) * (1 + (0.18 * f * f if not abrupt else 0))
    return tk
def ruff(buf, t, g=1.0):
    put(buf, load(SN('OldSnare/snare_pp2.wav')), t - 0.07, 0.5 * g)
    put(buf, load(SN('OldSnare/snare_p.wav')), t - 0.035, 0.6 * g)
    put(buf, load(SN('OldSnare/snare_mf.wav')), t, 0.9 * g)

# ═════════════════════ THE STORM OFF WHITBY — three loops, one hit ═══════════════
def storm(level, L=40.0, seed=0):
    """level 1: far off, a hollow booming. 3: the tempest. 4: the schooner rushing in."""
    global rng; rng = np.random.default_rng(100 + seed)
    N = int(L * SR); b = np.zeros(N, np.float32); s = np.zeros(N, np.float32)
    put(s, sustain('Strings/Solo Contrabass/Trem/BKCtbss_Trem_E1_v1_rr1.wav', L + 2, semis=-2), 0, 0.5)   # D1
    if level >= 3:
        put(s, sustain('Strings/Cello Section/trem/trem_D2_v2_1.wav', L + 2), 0, 0.45)
        put(s, sustain('Strings/Cello Section/trem/trem_F2_v2_1.wav', L + 2), 0, 0.33)
    if level >= 4:
        put(s, sustain('Strings/Viola Section/trem/Violas_trem_D3_v2_rr1.wav', L + 2), 0, 0.32)
        put(s, sustain('Strings/Viola Section/trem/Violas_trem_E4_v2_rr1.wav', L + 2, semis=-1), 0, 0.24)   # Eb4, never resolving
    rolls = {1: [(2, 4, 3, .35, 9, 1500), (22, 2, 3, .3, 10, 1500)],
             3: [(0, 2, 5, .6, 14, None), (12, 4, 5, .55, 12, None), (25, 2, 5, .6, 14, None)],
             4: [(0, 2, 5, .8, 21, None), (19, 4, 5, .8, 22, None), (8, 3, 5, .5, 14, None)]}[level]
    for t0, d, v, g, dur, cut in rolls: timp_roll(b, t0, d, v, g, dur, fin=2.5, fout=3.0, cut=cut)
    t = 0.5
    gap, n_, dyn, gg = {1: (6.5, 2, 'pp', .35), 3: (1.8, 4, 'f', .7), 4: (0.9, 6, 'ff', .9)}[level]
    while t < L - 0.5:
        tom_group(b, t, int(n_ + rng.integers(0, 3)), dyn, spread=0.1, g=gg)
        t += gap * (0.7 + 0.6 * rng.random())
    x = reverb(s + b, 2.6, 0.28, seed=5)
    # skip the strings' first attack, then fold the last 4 s over the first: no seam, no re-attack
    x = x[int(1.5 * SR):]
    k = int(4.0 * SR); body = x[:-k].copy(); a = np.linspace(0, np.pi / 2, k)
    body[:k] = body[:k] * np.sin(a) + x[-k:] * np.cos(a)
    return body
for lvl, db in [(1, -24), (3, -15), (4, -11)]:
    write_loop(peak_db(storm(lvl, L=45.5, seed=lvl), db), f'storm-{lvl}.wav')

rng = np.random.default_rng(1897)
N = int(9 * SR); hit = np.zeros(N, np.float32)
for d, v, g in [(4, 4, 1.0), (2, 4, 1.0), (3, 4, .8)]: timp(hit, 0.02, d, v, g)
put(hit, load(BD('bdrum_fff_1')), 0.02, 1.2); put(hit, load(BD('bdrum3_fff_1')), 0.025, 0.9); tom(hit, 0.02, 'fff', g=0.9)
hit = env(reverb(hit, 2.8, 0.28, seed=6), [(0, 1), (6.0, 1), (9.0, 0)])
write_mp3(peak_db(hit, -1), 'wreck-hit.mp3')

# ═════════════════════ THE LOG — the ship's pulse, one beat per soul ═════════════
BPM = 65.0; beat = 60 / BPM; bar = 4 * beat; eighth = beat / 2
ORDER = [0, 4, 2, 6, 1, 5, 3, 7]                                      # the downbeat survives longest
BARS = 4
for souls in (8, 7, 6, 5, 3, 2, 1):
    rng = np.random.default_rng(700 + souls)
    L = BARS * bar; N = int(round(L * SR)); b = np.zeros(N + SR, np.float32)
    for bi in range(BARS):
        for k in sorted(ORDER[:souls]):
            tom(b, bi * bar + k * eighth, 'pp' if k == 0 else 'ppp', g=0.55 if k == 0 else 0.4, muffle=1400)
    b[:SR] += b[N:N + SR]; b = b[:N]                                   # the last stroke's ring wraps into the start
    b = wrap_reverb(b, 0.7, 0.2, seed=8)                              # the small wooden stage
    write_loop(peak_db(b, -24), f'pulse-{souls}.wav')

# each soul taken: the roll call falters, and his heart, until it is no more
rng = np.random.default_rng(31)
def loss_file(double=False):
    b = np.zeros(int(10 * SR), np.float32)
    ruff(b, 0.1); heart(b, 0.85, 6, 72, 38)
    if double: heart(b, 1.25, 5, 66, 34, 0.85, 0.22)
    return reverb(b, 0.7, 0.2, seed=8)
write_mp3(peak_db(loss_file(), -12), 'loss-heart.mp3')
write_mp3(peak_db(loss_file(True), -11), 'loss-heart-double.mp3')

# weather in the log, on kettle and toms
def weather(kind):
    global rng; rng = np.random.default_rng({'rain': 51, 'rough': 52, 'warn': 53, 'tempest': 54}[kind])
    if kind == 'rain':
        b = np.zeros(int(5 * SR), np.float32)
        for k in range(16): tom(b, 0.1 + k * 0.28 + 0.1 * rng.random(), 'pp', hi=True, g=0.35 + 0.1 * rng.random())
        return peak_db(reverb(b, 0.7, .2), -22)
    if kind == 'rough':
        b = np.zeros(int(12 * SR), np.float32); timp_roll(b, 0, 4, 3, 0.45, 10.5, fin=3, fout=4)
        t = 1.0
        while t < 9.5: tom_group(b, t, int(2 + rng.integers(0, 3)), 'mf', g=0.45); t += 1.5 + rng.random()
        return peak_db(reverb(b, 0.7, .2), -16)
    if kind == 'warn':
        b = np.zeros(int(5.5 * SR), np.float32); timp_roll(b, 0, 2, 3, 0.4, 5.0, fin=1.8, fout=2.4, cut=900)
        return peak_db(reverb(b, 0.7, .2), -24)
    b = np.zeros(int(16 * SR), np.float32)
    timp_roll(b, 0, 2, 5, 0.65, 14.5, fin=3, fout=3.5); timp_roll(b, 4, 4, 5, 0.55, 9.0, fin=2, fout=3)
    t = 1.0
    while t < 13.0:
        ph = 1 - abs((t - 7) / 6)
        tom_group(b, t, int(3 + 3 * ph + rng.integers(0, 2)), 'ff' if ph > .5 else 'f', spread=0.1, g=0.4 + 0.25 * ph)
        t += 0.9 + 0.6 * rng.random()
    timp(b, 7.2, 4, 3, 0.6)
    return peak_db(reverb(b, 0.7, .2), -11)
for k, name in [('rain', 'log-rain.mp3'), ('rough', 'log-rough-weather.mp3'), ('warn', 'log-distant-roll.mp3'), ('tempest', 'log-tempest.mp3')]:
    write_mp3(weather(k), name)

# the mate: his heart racing under a rising snare roll — ending EXACTLY at 3.6 s, on the words
rng = np.random.default_rng(61)
RISE = 3.6; b = np.zeros(int((RISE + 0.05) * SR), np.float32)
heart(b, 0.0, 9, 120, 150, 0.6, 1.0, abrupt=True)
dy = ['OldSnare/snare_pp.wav', 'OldSnare/snare_p.wav', 'OldSnare/snare_mf2.wav', 'OldSnare/snare_f.wav', 'OldSnare/snare_ff.wav']
t = 0.0
while t < RISE - 0.02:
    ph = t / RISE; put(b, load(SN(dy[min(4, int(ph * 5))])), t, 0.35 + 0.55 * ph); t += 0.075 - 0.02 * ph
b = b[:int(RISE * SR)]; b[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))   # it stops dead
write_mp3(peak_db(reverb(b, 0.7, .2), -9), 'mate-racing.mp3')

# lightning: the great kettle drums and the snares struck with a real thunderclap, which then sinks
tsr, tx = wv.read('/tmp/snd/th/Storm_thunderbolts.wav'); tx = tx.astype(np.float32); tx = (tx.mean(1) if tx.ndim > 1 else tx) / 32768
clap = (sg.resample_poly(tx, SR, tsr).astype(np.float32) if tsr != SR else tx)[int(88.30 * SR): int(100.8 * SR)]
clap = env(clap, [(0, 0), (0.02, 1), (9.0, 1), (12.5, 0)])
def depths(x, start=0.6, f0=9000.0, f1=220.0, wm=7.0, sink=55.0):
    n = len(x); t = np.arange(n) / SR; d = np.clip((t - start) / (t[-1] - start), 0, 1)
    dly = (wm * d * (np.sin(2 * np.pi * .85 * t) + .6 * np.sin(2 * np.pi * 2.3 * t + 1.1)) / 1.6 + sink * d ** 1.6) * SR / 1000
    idx = np.clip(np.arange(n) - dly - wm * SR / 1000, 0, n - 1); i0 = np.floor(idx).astype(int); fr = idx - i0
    y = x[i0] * (1 - fr) + x[np.minimum(i0 + 1, n - 1)] * fr
    f, tt, Z = sg.stft(y, SR, nperseg=2048, noverlap=1536); dd = np.clip((tt - start) / (t[-1] - start), 0, 1)
    M = 1 / (1 + (f[:, None] / (f0 * (f1 / f0) ** dd)[None, :]) ** 6); _, y = sg.istft(Z * M, SR, nperseg=2048, noverlap=1536)
    y = y[:n].astype(np.float32); r = np.random.default_rng(41)
    for _ in range(9):
        tb = start + 1 + r.random() * (t[-1] - start - 2.5); Lb = int((.05 + .07 * r.random()) * SR); tl = np.arange(Lb) / SR
        fq = (180 + 250 * r.random()) * (1 + 3 * tl / tl[-1]); bub = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.sin(np.pi * tl / tl[-1]) ** 2
        i = int(tb * SR); y[i:i + Lb] += (bub * .05 * (.5 + r.random())).astype(np.float32)[: n - i]
    return y
clap = peak_db(depths(clap), -5)
b = np.zeros(len(clap) + SR, np.float32)
dr = np.zeros(len(b), np.float32)
for d, v, g in [(2, 4, 1.6), (4, 4, 1.5), (3, 4, 1.0)]: timp(dr, 0.10, d, v, g)
put(dr, load(SN('drum1/snare1_fff_1.wav')), 0.10, 1.3); put(dr, load(SN('OldSnare/snare_ff.wav')), 0.108, 1.0); put(dr, load(BD('bdrum_fff_1')), 0.10, 1.0)
b += peak_db(reverb(dr, 0.7, .2), -8.5); put(b, clap, 0.0, 1.0)
write_mp3(peak_db(b, -2), 'lightning-depths.mp3')

# a howl out of the fog: the wolf has lost his meal
wsr, wx = wv.read('/tmp/snd/Wolf_howls.wav'); wx = wx.astype(np.float32) / 32768; wx = wx.mean(1) if wx.ndim > 1 else wx
wx = sg.resample_poly(wx, SR, wsr)[int(20.0 * SR): int(25.3 * SR)].astype(np.float32)
wx = env(sg.sosfilt(sg.butter(2, [180, 3800], 'band', fs=SR, output='sos'), wx).astype(np.float32), [(0, 0), (.3, 1), (4.3, 1), (5.3, 0)])
wx = reverb(np.concatenate([wx, np.zeros(int(2.6 * SR), np.float32)]), 2.6, 0.4, seed=31)
write_mp3(peak_db(wx, -11), 'wolf-howl.mp3')

# the captain alone: only his heart, steady (a loop), and the last beat with no answer
b = np.zeros(int(8 * 60 / 54.0 * SR), np.float32)
for k in range(8): lub(b, k * 60 / 54.0, 1.0)
b = wrap_reverb(b, 0.7, 0.2, seed=8)
write_loop(peak_db(b, -19), 'captain-heart.wav')
b = np.zeros(int(3 * SR), np.float32); lub(b, 0.05, 0.85, last=True)
write_mp3(peak_db(reverb(b, 0.7, .2), -21), 'heart-last.mp3')

# ═════════════════════ THE SEAS ════════════════════════════════════════════════
# whitby: sea on shingle — breaking waves, the drag of pebbles back. sound.js loops it three ways.
def sea(L, kind, seed):
    r = np.random.default_rng(seed); N = int(L * SR); out = np.zeros(N, np.float32)
    swell = lp(r.standard_normal(N), 180, 2); out += rms_db(swell, -34)
    t = 0.0
    while t < L:
        dur = 5.5 + 3 * r.random(); n = int(dur * SR); tt = np.arange(n) / SR
        e = (np.clip(tt / (0.35 * dur), 0, 1) ** 2) * np.exp(-np.clip(tt - 0.35 * dur, 0, None) * 1.1)
        wave = lp(r.standard_normal(n), 2600 if kind == 'shingle' else 900, 2) * e
        if kind == 'shingle':                                           # pebbles dragged back
            drag = hp(r.standard_normal(n), 2500) * np.clip((tt - 0.5 * dur) / (0.3 * dur), 0, 1) * np.exp(-np.clip(tt - 0.8 * dur, 0, None) * 2)
            wave = wave + 0.35 * drag * (r.random(n) < 0.08)
        put(out, rms_db(wave.astype(np.float32), -26) * (0.7 + 0.5 * r.random()), t)
        t += dur * (0.55 + 0.25 * r.random())
    return out
def seamless(x, xf=4.0):
    k = int(xf * SR); body = x[:-k].copy(); a = np.linspace(0, np.pi / 2, k)
    body[:k] = body[:k] * np.sin(a) + x[-k:] * np.cos(a); return body
write_mp3(rms_db(seamless(reverb(sea(68, 'shingle', 81), 1.2, .2)), -24), 'sea.mp3')
# the demeter: sea against a hull, timbers working, close
h = sea(68, 'hull', 82)
csr, cr = wv.read('/tmp/snd/w_Creaky_wooden_casket.wav'); cr = cr.astype(np.float32) / 32768; cr = cr.mean(1) if cr.ndim > 1 else cr
cr = sg.resample_poly(cr, SR, csr).astype(np.float32)
r = np.random.default_rng(83); t = 2.0
while t < 64:
    seg = cr[int(r.random() * max(1, len(cr) - SR)):][: int((0.5 + 0.8 * r.random()) * SR)]
    seg = sg.resample(seg, int(len(seg) * (1.6 + 0.8 * r.random()))).astype(np.float32)   # bigger timbers: slower, lower
    put(h, env(lp(seg, 1800), [(0, 0), (.08, 1), (len(seg) / SR - .1, 1), (len(seg) / SR, 0)]) * 0.12, t); t += 3 + 5 * r.random()
write_mp3(rms_db(seamless(reverb(h, 0.7, .2, seed=8)), -26), 'hull.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k, v in files.items(): print(f'{k:26s} {v:6.2f}s')
