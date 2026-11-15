#!/usr/bin/env python3
"""A Tale of Two Cities, Book the First: the two new rooms · 14 Nov 2026.
  coach-night.mp3  the Dover mail heard from inside, at night: four horses at a trot on
                   a mud road (every strike a real recorded hoof), the wheels' rumble,
                   the body's leather and wood creaking, mist and wind outside.
  dover-beach.mp3  Dover under the chalk cliffs: surf on the shingle below a cliff,
                   small waves on the stones close by, gulls far off.
Real recordings only (BigSoundBank, CC0: 0610 0611 1316 2516 2517 2570 1445 2573) and
Dracula's wind.mp3. Nothing in a room repeats inside its 60 s; the seam is crossfaded.
usage: build-rooms.py <bsb dir> <out dir>"""
import sys, subprocess, numpy as np, scipy.signal as sg
SRC, OUT = sys.argv[1], sys.argv[2]; SR = 44100; N = 60 * SR; XF = 6 * SR
R = np.random.default_rng(1775)
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def lp(x, f): return sg.sosfilt(sg.butter(2, f, 'low', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def hp(x, f): return sg.sosfilt(sg.butter(2, f, 'high', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def db(d): return 10 ** (d / 20)
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-9)
def norm(x, d): return (x / rms(x) * db(d)).astype(np.float32)
def fade(x, a, b):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)[:, None]
    if nb: x[-nb:] *= np.linspace(1, 0, nb)[:, None]
    return x
def pitch(x, semis):
    r = 2 ** (semis / 12); n = int(len(x) / r); i = np.arange(n) * r
    return np.stack([np.interp(i, np.arange(len(x)), x[:, c]) for c in (0, 1)], 1).astype(np.float32)
def put(bus, x, t, g=1.0, pan=0.0):
    a = int(t * SR) % len(bus); n = min(len(x), len(bus) - a)
    lr = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
    bus[a:a + n] += x[:n] * g * lr; rest = len(x) - n
    if rest > 0: bus[:rest] += x[n:n + rest] * g * lr          # wraps round the loop
def texture(x, n, chunk=(2.0, 4.0), xf=0.5):
    """A long, non-repeating bed from random chunks of a recording, crossfaded."""
    out = np.zeros((n, 2), np.float32); t = 0
    while t < n:
        L = int(R.uniform(*chunk) * SR); a = R.integers(0, len(x) - L - 1)
        s = fade(x[a:a + L], xf, xf); m = min(L, n - t); out[t:t + m] += s[:m]; t += L - int(xf * SR)
    return out
def loop(x):
    """Crossfade the tail into the head so the 60 s file loops without a seam."""
    y = x[:N].copy(); w = np.linspace(0, 1, XF)[:, None]
    y[:XF] = x[N:N + XF] * (1 - w) + y[:XF] * w; return y
def onsets(m, thr=-30, gap=0.08):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, m ** 2)); d = 20 * np.log10(e + 1e-9); on = []; last = -1e9
    for i in np.where((d[1:] > thr) & (d[:-1] <= thr))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on
def strikes(x, L=0.22):
    m = x.mean(1); out = []
    for o in onsets(m):
        a = max(0, o - int(0.004 * SR)); s = x[a:a + int(L * SR)]
        if len(s) > L * SR * 0.9: out.append(fade(s / (np.abs(s).max() + 1e-9), 0.002, L * 0.6))
    return out
def save(x, name):
    x = x / max(1.0, np.abs(x).max() / db(-1))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', OUT + '/' + name],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(name, '%.1f s' % (len(x) / SR), 'rms %.1f dB' % (20 * np.log10(rms(x))))

T = N + XF
# --- the coach at night ------------------------------------------------------------
hoof = strikes(load(SRC + '/bsb-0610.mp3')) + strikes(load(SRC + '/bsb-0611.mp3'))
print('hoof strikes', len(hoof))
hooves = np.zeros((T, 2), np.float32)
for h in range(4):                                        # four horses at a slow, labouring trot
    stride = R.uniform(0.70, 0.78); t = R.uniform(0, stride); pan = [-0.5, -0.2, 0.2, 0.5][h]
    while t < T / SR:
        for ph in (0, 0.5):                               # a trot: diagonal pairs, two beats a stride
            s = hoof[R.integers(len(hoof))]
            put(hooves, pitch(s, R.uniform(-3, -1)), t + ph * stride + R.normal(0, 0.012), db(R.uniform(-4, 0)), pan)
        t += stride * R.uniform(0.97, 1.03)
hooves = lp(hp(hooves, 90), 1600)                         # mud underfoot, heard through the coach body
wheel = texture(lp(load(SRC + '/bsb-1316.mp3'), 900), T, (1.5, 3.0), 0.4)
rumble = lp(R.standard_normal((T, 2)).astype(np.float32), 110)
bump = np.repeat(1 + 0.6 * np.clip(R.standard_normal(T // 2205 + 1), 0, None), 2205)[:T][:, None]
rumble = lp(rumble * bump, 140)
creak = np.zeros((T, 2), np.float32); cr = [load(SRC + '/bsb-2516.mp3'), load(SRC + '/bsb-2517.mp3')]
t = R.uniform(1, 3)
while t < T / SR:                                         # leather springs and the body working, now and then
    c = cr[R.integers(2)]; L = int(R.uniform(0.4, 1.1) * SR); a = R.integers(0, len(c) - L)
    put(creak, fade(pitch(c[a:a + L], R.uniform(-7, -4)), 0.05, 0.2), t, db(R.uniform(-6, 0)), R.uniform(-0.6, 0.6)); t += R.uniform(2.5, 6.5)
creak = lp(creak, 2200)
wind = load('dracula/sound/wind.mp3'); wind = np.concatenate([wind] * 2)[:T]
coach = norm(hooves, -27) + norm(wheel, -31) + norm(rumble, -26) + norm(creak, -33) + norm(lp(wind, 1200), -36)
save(loop(coach), 'coach-night.mp3')

# --- Dover beach under the cliffs ----------------------------------------------------
cliff = texture(load(SRC + '/bsb-2570.mp3'), T, (6, 12), 1.5)
stones = texture(load(SRC + '/bsb-1445.mp3'), T, (6, 12), 1.5)
gull = load(SRC + '/bsb-2573.mp3'); gulls = np.zeros((T, 2), np.float32); t = R.uniform(3, 8)
while t < T / SR:
    L = int(R.uniform(1.5, 4) * SR); a = R.integers(0, len(gull) - L)
    put(gulls, fade(gull[a:a + L], 0.3, 0.8), t, db(R.uniform(-8, -2)), R.uniform(-0.8, 0.8)); t += R.uniform(8, 18)
gulls = lp(hp(gulls, 400), 4500)                          # far off
beach = norm(cliff, -24) + norm(stones, -28) + norm(gulls, -38)
save(loop(beach), 'dover-beach.mp3')
