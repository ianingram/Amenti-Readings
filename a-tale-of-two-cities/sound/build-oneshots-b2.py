#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Second: the new one-shots · 15 Nov 2026.
  hand-bell.mp3      a small table bell rung once (the Marquis, Darnay at the tavern)      0292
  church-one.mp3     St Paul's striking one, far off over wet roofs                          3446
  thunder-far.mp3    a peal of thunder some way off                                          3114
  thunder-crash.mp3  the storm breaking: a crash right overhead                              3116
  rain-drops.mp3     the first large drops falling on leaves and stones, few and heavy       1384 1385
  steps-echo.mp3     the corner's echoes: footsteps hurrying, coming and going, unseen       1318 1319
  steps-rush.mp3     the same, incessant and faster, from every side                         1318 1319
  chateau-bell.mp3   the great bell of the chateau rung in alarm                             0135
  owl.mp3            an owl in the stable roof                                               0429
  horses-stable.mp3  horses rattling at their racks in the night                             0289
  coin.mp3           a gold coin ringing on the carriage floor                               0193
Real recordings only (BigSoundBank, CC0).
usage: build-oneshots-b2.py <bsb dir> <out dir>"""
import sys, subprocess, numpy as np, scipy.signal as sg
SRC, OUT = sys.argv[1], sys.argv[2]; SR = 44100; R = np.random.default_rng(1781)
def load(n):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', '%s/bsb-%s.mp3' % (SRC, n), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
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
    m = np.abs(x).mean(1); return np.sqrt(sg.lfilter(np.ones(int(w * SR)) / int(w * SR), 1, m ** 2))
def span(x, thr=-40):
    """The part of a recording that sounds: first to last sample above thr dB of its peak."""
    e = env(x); i = np.where(20 * np.log10(e / e.max() + 1e-9) > thr)[0]; return x[max(0, i[0] - 200): i[-1]]
def first(x, gap=0.6, thr=-35):
    """The first event in a recording, up to the first silence of gap seconds."""
    e = 20 * np.log10(env(x) / env(x).max() + 1e-9); on = np.where(e > thr)[0][0]; q = 0
    for i in range(on, len(e)):
        q = q + 1 if e[i] < thr else 0
        if q > gap * SR: return x[max(0, on - 200): i]
    return x[on:]
def reverb(x, secs, wet, pre=0.02, bright=4000):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = R.standard_normal((n, 2)).astype(np.float32) * np.exp(-6.9 * t / secs)[:, None]
    ir = lp(ir, bright); ir[:int(pre * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
    y = np.concatenate([x, np.zeros((n, 2), np.float32)])
    w = np.stack([sg.fftconvolve(y[:, c], ir[:, c])[:len(y)] for c in (0, 1)], 1)
    return (y * (1 - wet) + w * wet * 3).astype(np.float32)
def trim(x, thr=-55):
    e = env(x); i = np.where(20 * np.log10(e / e.max() + 1e-9) > thr)[0]; return x[: i[-1] + 1] if len(i) else x
def save(x, name, peak=-3):
    x = trim(x); x = x / np.abs(x).max() * db(peak)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', OUT + '/' + name],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(name, '%.1f s' % (len(x) / SR))
def onsets(m, thr=-30, gap=0.12):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, m ** 2)); d = 20 * np.log10(e / e.max() + 1e-9); on = []; last = -1e9
    for i in np.where((d[1:] > thr) & (d[:-1] <= thr))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on

# the table bell: the first ring only
save(fade(first(load('0292'), 0.8), 0.002, 0.6), 'hand-bell.mp3', -6)
# St Paul's: one stroke, a little lower and far off, a long tail over the city
b = first(load('3446'), 1.5, -45); b = lp(hp(pitch(b, -3), 120), 2600)
save(fade(reverb(b, 3.5, 0.5, 0.06, 2500), 0.01, 2.0), 'church-one.mp3', -6)
# thunder far and near
save(fade(lp(span(load('3114')), 1100), 0.3, 3), 'thunder-far.mp3', -6)
save(fade(span(load('3116')), 0.01, 4), 'thunder-crash.mp3', -1)
# the first heavy drops: a handful of single drops, slowly at first
dr = np.concatenate([load('1384'), load('1385')]); hits = onsets(dr.mean(1), -28)
drops = []
for o in hits:
    s = dr[max(0, o - 100): o + int(0.25 * SR)]
    if len(s) > 0.2 * SR: drops.append(fade(s, 0.001, 0.15))
out = np.zeros((int(12 * SR), 2), np.float32); t = 0.2
while t < 11 and drops:
    put(out, lp(drops[R.integers(len(drops))], 6000), t, db(R.uniform(-10, 0)), R.uniform(-0.8, 0.8)); t += R.uniform(0.35, 1.3) * (1 - t / 18)
save(fade(out, 0.01, 2.5), 'rain-drops.mp3', -6)
# the echoing corner: steps that come and go, everywhere and nowhere
st = np.concatenate([load('1318'), load('1319')]); fs = onsets(st.mean(1), -26, 0.18)
step = [fade(st[max(0, o - 100): o + int(0.2 * SR)], 0.001, 0.12) for o in fs if o + 0.2 * SR < len(st)]
print('footsteps', len(step))
def walkers(secs, n, pace, g):
    out = np.zeros((int(secs * SR), 2), np.float32)
    for k in range(n):                                     # each walker crosses the corner and is gone
        t0 = R.uniform(0, secs * 0.85); D = R.uniform(4, 9); p0 = R.uniform(-1, 1); p1 = R.uniform(-1, 1); t = t0; sp = R.uniform(*pace)
        while t < min(secs, t0 + D):
            u = (t - t0) / D; e = np.sin(np.pi * u) ** 1.5
            put(out, pitch(step[R.integers(len(step))], R.uniform(-2, 1)), t, e * db(R.uniform(-6, 0) + g), p0 + (p1 - p0) * u); t += sp * R.uniform(0.92, 1.08)
    return out
echo = walkers(24, 10, (0.42, 0.58), 0); echo = reverb(lp(hp(echo, 200), 3500), 2.2, 0.75, 0.05, 2500)
save(fade(echo, 1.5, 4), 'steps-echo.mp3', -6)
rush = walkers(26, 26, (0.28, 0.4), 0) * np.linspace(0.5, 1.0, int(26 * SR))[:, None]
rush = reverb(lp(hp(rush, 200), 3800), 2.2, 0.7, 0.05, 2600)
save(fade(rush, 2, 3), 'steps-rush.mp3', -4)
# the great bell of the chateau, rung hard and fast
save(fade(span(load('0135')), 0.01, 3), 'chateau-bell.mp3', -4)
# an owl's complaint
save(fade(first(load('0429'), 1.0), 0.05, 0.6), 'owl.mp3', -8)
# horses in the stables, rattling at their racks
save(fade(lp(span(load('0289'))[: int(9 * SR)], 3500), 0.5, 2.5), 'horses-stable.mp3', -6)
# a gold coin flung into the carriage, ringing on its floor: the first clinks of a fall of coins
c = load('0193'); o = onsets(c.mean(1), -30, 0.05)
save(fade(c[max(0, o[0] - 100): o[0] + int(0.9 * SR)], 0.001, 0.5), 'coin.mp3', -6)
