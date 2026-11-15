#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Second (chapters 19-30): the new one-shots · 15 Nov 2026.
  spade.mp3          a spade in churchyard earth, a few strokes                           1305
  creak.mp3          wood wrenched and creaking (the coffin forced open)                    0539
  wedding-bells.mp3  the church bells after the wedding                                    0829
  bells-drums.mp3    church bells ringing far off over Paris, military drums beating under 0994 2402 2405
  chop.mp3           a chopper on a wooden bench, behind a closed door                      0536
  cheer.mp3          a crowd shouting and cheering                                          0019 0021 0236 0237
  roar.mp3           a vast crowd roaring as one                                            BigSoundBank protest crowds
  drum-jar.mp3       a drum jarred against a counter                                        2400
  drum-beat.mp3      a drum beating in the street, a roll and the strokes after it            2402 2408
  alarm-bells.mp3    alarm-bells ringing all over the city                                  0135 0829 0830
  cannon.mp3         a cannon shot, the walls answering                                     1806
  volley.mp3         a ragged volley of muskets                                             2853 2854 0397
  blaze.mp3          a pile set alight, blazing up high and hot                              1341
  tocsin.mp3         the village bell rung impatiently                                       0135
Real recordings only (BigSoundBank, CC0).
usage: build-oneshots-b2b.py <out dir> <bsb dir> [more bsb dirs …]"""
import sys, os, subprocess, numpy as np, scipy.signal as sg
OUT, DIRS = sys.argv[1], sys.argv[2:]; SR = 44100; R = np.random.default_rng(1792)
def load(n):
    for d in DIRS:
        f = '%s/bsb-%s.mp3' % (d, n)
        if os.path.exists(f): break
    else: raise SystemExit('no bsb-%s.mp3' % n)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def cat(*ns): return np.concatenate([load(n) for n in ns])
def lp(x, f): return sg.sosfilt(sg.butter(2, f, 'low', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def hp(x, f): return sg.sosfilt(sg.butter(2, f, 'high', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def db(d): return 10 ** (d / 20)
def fade(x, a, b):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)[:, None]
    if nb: x[-nb:] *= np.linspace(1, 0, nb)[:, None]
    return x
def pitch(x, semis):
    r = 2 ** (semis / 12); n = int(len(x) / r); i = np.arange(n) * r
    return np.stack([np.interp(i, np.arange(len(x)), x[:, c]) for c in (0, 1)], 1).astype(np.float32)
def put(bus, x, t, g=1.0, pan=0.0):
    a = int(t * SR); n = min(len(x), len(bus) - a)
    if n <= 0: return
    lr = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
    bus[a:a + n] += x[:n] * g * lr
def env(x, w=0.02):
    m = np.abs(x).mean(1); k = int(w * SR); return np.sqrt(sg.lfilter(np.ones(k) / k, 1, m ** 2))
def span(x, thr=-40):
    e = env(x); i = np.where(20 * np.log10(e / e.max() + 1e-9) > thr)[0]; return x[max(0, i[0] - 200): i[-1]]
def reverb(x, secs, wet, pre=0.02, bright=4000):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = R.standard_normal((n, 2)).astype(np.float32) * np.exp(-6.9 * t / secs)[:, None]
    ir = lp(ir, bright); ir[:int(pre * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
    y = np.concatenate([x, np.zeros((n, 2), np.float32)])
    w = np.stack([sg.fftconvolve(y[:, c], ir[:, c])[:len(y)] for c in (0, 1)], 1)
    return (y * (1 - wet) + w * wet * 3).astype(np.float32)
def trim(x, thr=-55):
    e = env(x); i = np.where(20 * np.log10(e / e.max() + 1e-9) > thr)[0]; return x[: i[-1] + 1] if len(i) else x
def onsets(m, thr=-30, gap=0.12):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, m ** 2)); d = 20 * np.log10(e / e.max() + 1e-9); on = []; last = -1e9
    for i in np.where((d[1:] > thr) & (d[:-1] <= thr))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on
def events(x, L, thr=-24, gap=0.3):
    out = []
    for o in onsets(x.mean(1), thr, gap):
        s = x[max(0, o - 200): o + int(L * SR)]
        if len(s) > 0.8 * L * SR: out.append(fade(s / (np.abs(s).max() + 1e-9), 0.003, L * 0.5))
    return out
def grains(x, secs, L=(0.4, 1.2), layers=6):
    n = int(secs * SR); out = np.zeros((n, 2), np.float32)
    for _ in range(layers):
        t = 0
        while t < n:
            l = int(R.uniform(*L) * SR); a = R.integers(0, len(x) - l - 1); s = fade(x[a:a + l], 0.12, 0.2)
            m = min(l, n - t); out[t:t + m] += s[:m] * db(R.uniform(-4, 0)); t += l - int(0.15 * SR)
    return out
def swell(n, up, down):
    e = np.ones(n, np.float32); u, d = int(up * SR), int(down * SR)
    e[:u] = np.linspace(0, 1, u) ** 1.5; e[-d:] = np.linspace(1, 0, d) ** 1.2; return e[:, None]
def save(x, name, peak=-3):
    x = trim(x); x = x / np.abs(x).max() * db(peak)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', OUT + '/' + name],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(name, '%.1f s' % (len(x) / SR))

# the spade: the first strokes only
d = span(load('1305')); save(fade(lp(d[: int(7 * SR)], 5000), 0.01, 1.5), 'spade.mp3', -6)
# the coffin lid wrenched: the barn door's long creak, a little lower
c = span(load('0539')); save(fade(pitch(c[: int(4 * SR)], -2), 0.02, 1.0), 'creak.mp3', -6)
# wedding bells: the peal, softened, from the church along the street
w = span(load('0829')); save(fade(reverb(lp(w[: int(16 * SR)], 4500), 2.5, 0.35, 0.05, 3500), 0.5, 4), 'wedding-bells.mp3', -6)
# bells far over Paris, the drums in the Palace Courtyard beneath them
b = lp(span(load('0994'))[: int(18 * SR)], 1800); dr = np.concatenate([fade(load('2402'), 0.01, 0.5), fade(load('2405'), 0.01, 0.5), fade(load('2402'), 0.01, 0.5)])
mix = np.zeros((int(20 * SR), 2), np.float32); put(mix, b, 0, 1.0, 0.3)
for t in (3.0, 9.5): put(mix, reverb(lp(dr, 1500), 2.5, 0.5, 0.06, 1500), t, 0.5, -0.4)
save(fade(mix, 2, 5), 'bells-drums.mp3', -8)
# the chopper on the bench, in a closed room
ch = span(load('0536')); save(fade(reverb(lp(ch[: int(6 * SR)], 4000), 0.6, 0.3, 0.01, 4000), 0.01, 1), 'chop.mp3', -6)
# a crowd cheering: applause and young voices, rough and outdoors, swelling and dying
ap = load('0019')[: int(9 * SR)]; sh = np.concatenate([load('0236'), load('0237')])
cheer = lp(hp(ap, 200), 3500) * 0.7; put(cheer, lp(sh, 3000), 0.6, 1.0, -0.2); put(cheer, lp(pitch(sh, -3), 2800), 2.0, 0.8, 0.3)
save(cheer * swell(len(cheer), 0.6, 3.5), 'cheer.mp3', -6)
# the roar of a vast crowd, rising and falling away
pro = np.concatenate([load(n) for n in ('2980', '2982', '0108', '3383', '3385', '3389')])
r = lp(hp(grains(pro, 9, (0.3, 0.9), 8), 130), 2600); save(r * swell(len(r), 1.2, 4.5), 'roar.mp3', -4)
# the jar of a drum behind the counter
j = events(load('2400'), 0.5, -18, 0.1)[0]; save(fade(lp(j, 1800), 0.002, 0.3), 'drum-jar.mp3', -10)
# the drum beating in the street: a roll, then the strokes, echoing between the houses
roll = fade(load('2408'), 0.01, 0.4); hits = events(load('2404'), 0.35, -20, 0.08) or [roll[: int(0.3 * SR)]]
db_ = np.zeros((int(10 * SR), 2), np.float32); put(db_, roll, 0)
t = len(roll) / SR + 0.1
for k in range(10): put(db_, hits[k % len(hits)], t, 0.9 if k % 2 == 0 else 0.6); t += 0.42
save(fade(reverb(lp(db_, 5000), 1.8, 0.4, 0.03, 3500), 0.01, 2), 'drum-beat.mp3', -5)
# alarm-bells: several churches at once, all over the city
ab = np.zeros((int(16 * SR), 2), np.float32)
for k, (n, pan, t) in enumerate((('0135', -0.6, 0), ('0829', 0.5, 1.2), ('0830', 0.0, 2.5))):
    put(ab, lp(span(load(n))[: int(13 * SR)], 3000 - k * 600), t, 1.0 - k * 0.2, pan)
save(fade(reverb(ab, 3, 0.45, 0.06, 2500), 0.8, 4), 'alarm-bells.mp3', -5)
# a cannon shot from the towers, the walls answering
x = load('1806'); e = env(x, 0.01); i = int(np.where(20 * np.log10(e / e.max() + 1e-9) > -20)[0][0])
save(fade(reverb(lp(pitch(x[max(0, i - 2000): i + int(5 * SR)], -2), 1700), 3.5, 0.4, 0.07, 1500), 0.005, 2.5), 'cannon.mp3', -1)
# a ragged volley of muskets
shots = []
for n in ('2853', '2854', '0397'): shots += events(load(n), 0.9, -20, 0.25)
v = np.zeros((int(4 * SR), 2), np.float32)
for k in range(11): put(v, lp(shots[R.integers(len(shots))], R.uniform(2800, 4500)), R.uniform(0, 1.6) ** 1.3, db(R.uniform(-9, 0)), R.uniform(-0.9, 0.9))
save(fade(reverb(v, 2.4, 0.4, 0.05, 3000), 0.002, 2), 'volley.mp3', -2)
# the pile set alight: it catches and blazes up
g = span(load('1341')); save(fade(g[: int(7 * SR)], 0.05, 2.5), 'blaze.mp3', -6)
# the tocsin: one bell, rung impatiently
st = events(load('0135'), 2.5, -18, 0.3); tc = np.zeros((int(14 * SR), 2), np.float32); t = 0
while t < 11: put(tc, st[R.integers(len(st))], t, db(R.uniform(-4, 0))); t += R.uniform(0.55, 0.9)
save(fade(reverb(lp(tc, 3500), 2.5, 0.4, 0.05, 3000), 0.01, 3), 'tocsin.mp3', -6)
