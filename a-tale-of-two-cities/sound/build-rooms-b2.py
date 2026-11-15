#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Second (chapters 7-18): the new rooms · 15 Nov 2026.
  fleet-street.mp3    London by day, 1780: horses at a walk passing both ways, cart and coach
                      wheels, people talking in the street, quick steps on the stones
  old-bailey.mp3      the court: a packed hall murmuring under a high ceiling
  soho-corner.mp3     the Doctor's quiet lodgings: a plane tree's leaves, birds outside, the
                      city far off through the open windows
  storm.mp3           the storm breaking over Soho: heavy rain, rolling thunder inside it
  after-rain.mp3      the night after the storm: dripping, wet quiet
  salon.mp3           Monseigneur's reception: a crowd of fine people talking in a great room,
                      glasses, the rustle of a court
  paris-fountain.mp3  the Paris street at the fountain: the street, the fountain running
  coach-dusk.mp3      the Marquis's travelling carriage at sunset: the coach, evening birds
  village-evening.mp3 the poor village: its one fountain, evening birds, voices far off
  chateau-night.mp3   the chateau courtyard at night: the stone fountain dropping, owls, insects
  chateau-dawn.mp3    the same courtyard at sunrise: the birds waking, the fountain
Real recordings only (BigSoundBank, CC0 — numbers in sound/SOURCES.md) and Book the First's
coach-night.mp3. Nothing in a room repeats inside its 60 s; the seam is crossfaded.
usage (from the Amenti-Readings root): build-rooms-b2.py <bsb dir> <out dir>"""
import sys, subprocess, numpy as np, scipy.signal as sg
SRC, OUT = sys.argv[1], sys.argv[2]; SR = 44100; N = 60 * SR; XF = 6 * SR; T = N + XF
R = np.random.default_rng(1780)
def load(f):
    f = f if '/' in f else '%s/bsb-%s.mp3' % (SRC, f)
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
def scatter(x, n, every, L, g=(-8, 0), pan=0.8, xf=(0.2, 0.6)):
    """Pieces of a recording dropped here and there (birds, owls, clinks)."""
    out = np.zeros((n, 2), np.float32); t = R.uniform(*every) / 2
    while t < n / SR:
        l = int(R.uniform(*L) * SR); a = R.integers(0, max(1, len(x) - l))
        put(out, fade(x[a:a + l], *xf), t, db(R.uniform(*g)), R.uniform(-pan, pan)); t += R.uniform(*every)
    return out
def loop(x):
    """Crossfade the tail into the head so the 60 s file loops without a seam."""
    y = x[:N].copy(); w = np.linspace(0, 1, XF)[:, None]
    y[:XF] = x[N:N + XF] * (1 - w) + y[:XF] * w; return y
def reverb(x, secs, wet, pre=0.02, bright=4000):
    """A plain room: decaying filtered noise, early slaps from the walls."""
    n = int(secs * SR); t = np.arange(n) / SR
    ir = R.standard_normal((n, 2)).astype(np.float32) * np.exp(-6.9 * t / secs)[:, None]
    ir = lp(ir, bright); ir[:int(pre * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
    w = np.stack([sg.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in (0, 1)], 1)
    return (x * (1 - wet) + w * wet * 3).astype(np.float32)
def onsets(m, thr=-30, gap=0.08):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, m ** 2)); d = 20 * np.log10(e + 1e-9); on = []; last = -1e9
    for i in np.where((d[1:] > thr) & (d[:-1] <= thr))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on
def strikes(x, L=0.22, thr=-30):
    m = x.mean(1); out = []
    for o in onsets(m, thr):
        a = max(0, o - int(0.004 * SR)); s = x[a:a + int(L * SR)]
        if len(s) > L * SR * 0.9: out.append(fade(s / (np.abs(s).max() + 1e-9), 0.002, L * 0.6))
    return out
def save(x, name):
    x = x / max(1.0, np.abs(x).max() / db(-1))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', OUT + '/' + name],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(name, '%.1f s' % (len(x) / SR), 'rms %.1f dB' % (20 * np.log10(rms(x))))

hoof = strikes(load('0610')) + strikes(load('0611'))
def passing(n, every, speed=(0.95, 1.15), dur=(5, 9)):
    """Horses at a walk going by: four-beat strikes swelling and fading as they pass."""
    out = np.zeros((n, 2), np.float32); t = R.uniform(0, every[0])
    while t < n / SR:
        D = R.uniform(*dur); stride = R.uniform(*speed); p0 = R.uniform(-1, 1); p1 = -p0; k = 0.0
        while k < D:
            for ph in (0, 0.25, 0.5, 0.75):                   # the walk: four beats a stride
                u = (k + ph * stride) / D; env = np.sin(np.pi * min(1, u)) ** 2
                put(out, pitch(hoof[R.integers(len(hoof))], R.uniform(-2, 1)), t + k + ph * stride + R.normal(0, 0.015),
                    env * db(R.uniform(-5, 0)), p0 + (p1 - p0) * u)
            k += stride
        t += D * R.uniform(0.5, 1.0) + R.uniform(*every)
    return out
wheelsrc = lp(load(SRC + '/bsb-1316.mp3'), 1400)
def wheels(n, every, dur=(4, 8)):
    out = np.zeros((n, 2), np.float32); t = R.uniform(2, every[1])
    while t < n / SR:
        D = R.uniform(*dur); L = int(D * SR); a = R.integers(0, len(wheelsrc) - L)
        env = np.sin(np.pi * np.linspace(0, 1, L)) ** 2
        put(out, wheelsrc[a:a + L] * env[:, None], t, db(R.uniform(-6, 0)), R.uniform(-0.7, 0.7)); t += D + R.uniform(*every)
    return out

# --- Fleet Street by day ---------------------------------------------------------------
talk = hp(lp(texture(load('2968'), T, (4, 8), 1.0) + texture(load('2969'), T, (4, 8), 1.0), 2600), 150)
steps = scatter(load('1318'), T, (3, 7), (1.2, 2.5), (-10, -2), 0.8)
street = (norm(lp(passing(T, (2, 6)), 2400), -29) + norm(wheels(T, (3, 9)), -32) + norm(talk, -31) + norm(lp(steps, 3000), -38))
save(loop(street), 'fleet-street.mp3')

# --- the Old Bailey --------------------------------------------------------------------
hall = texture(load('3515'), T, (4, 9), 1.2) + texture(load('3516'), T, (4, 9), 1.2)
hall = reverb(lp(hp(hall, 140), 3200), 2.4, 0.45, 0.035, 3000)
save(loop(norm(hall, -24)), 'old-bailey.mp3')

# --- the quiet corner in Soho ----------------------------------------------------------
leaves = lp(texture(load('0659'), T, (6, 12), 1.5), 3500)
birds = hp(scatter(load('1859'), T, (4, 10), (2, 5), (-8, 0), 0.9, (0.4, 0.8)), 900)
city = lp(street, 500)
save(loop(norm(leaves, -36) + norm(lp(birds, 6000), -38) + norm(city, -44)), 'soho-corner.mp3')

# --- the storm -------------------------------------------------------------------------
rain = texture(load('1019'), T, (5, 10), 1.5); pour = texture(load('0740'), T, (5, 10), 1.5)
big = load('2719'); rolls = np.zeros((T, 2), np.float32); t = R.uniform(4, 9)
m = big.mean(1); env = np.sqrt(sg.lfilter(np.ones(4410) / 4410, 1, m ** 2)); loud = np.where(20 * np.log10(env + 1e-9) > -26)[0]
while t < T / SR:                                             # thunder rolls inside the rain, from the long storm recording
    c = loud[R.integers(len(loud))]; L = int(R.uniform(5, 9) * SR); a = max(0, c - L // 3)
    put(rolls, fade(big[a:a + L], 0.8, 2.5), t, db(R.uniform(-6, 0)), R.uniform(-0.4, 0.4)); t += R.uniform(9, 16)
save(loop(norm(rain, -24) + norm(pour, -27) + norm(lp(rolls, 900), -27)), 'storm.mp3')

# --- after the rain --------------------------------------------------------------------
wet = texture(load('0555'), T, (5, 10), 1.5)
drips = scatter(np.concatenate([load('1384'), load('1385')]), T, (0.6, 2.2), (0.6, 1.6), (-12, 0), 0.9, (0.05, 0.3))
save(loop(norm(wet, -32) + norm(lp(drips, 5000), -36)), 'after-rain.mp3')

# --- Monseigneur's reception -----------------------------------------------------------
crowd = texture(load('3516'), T, (3, 7), 0.8) + texture(load('3515'), T, (3, 7), 0.8)
clink = scatter(np.concatenate([load('0472'), load('1205')]), T, (2, 6), (0.4, 1.2), (-12, -2), 0.9, (0.01, 0.2))
salon = reverb(hp(crowd, 180), 1.8, 0.35, 0.03, 5000) + reverb(norm(clink, -1) * 0.25, 1.8, 0.4)
save(loop(norm(salon, -24)), 'salon.mp3')

# --- the Paris street at the fountain ---------------------------------------------------
fount = hp(texture(load('0913'), T, (5, 10), 1.5), 250)
save(loop(norm(lp(street, 3000), -28) + norm(fount, -30)), 'paris-fountain.mp3')

# --- the travelling carriage at sunset --------------------------------------------------
coach = load('a-tale-of-two-cities/sound/coach-night.mp3'); coach = np.concatenate([coach, coach[:XF]])[:T]
eve = hp(scatter(load('1859'), T, (3, 7), (2, 5), (-8, 0), 0.9, (0.4, 0.8)), 1000)
save(loop(norm(coach, -24) + norm(lp(eve, 5000), -35)), 'coach-dusk.mp3')

# --- the village at evening -------------------------------------------------------------
vill = norm(fount, -28) + norm(lp(hp(scatter(load('1859'), T, (3, 8), (2, 5), (-8, 0), 0.9, (0.4, 0.8)), 900), 6000), -34) \
     + norm(lp(talk, 1500), -44)
save(loop(vill), 'village-evening.mp3')

# --- the chateau at night ---------------------------------------------------------------
drop = scatter(np.concatenate([load('1386'), load('1387')]), T, (0.9, 2.6), (0.8, 1.8), (-10, 0), 0.5, (0.05, 0.4))
owls = scatter(np.concatenate([load('0429'), load('1400')]), T, (12, 22), (2, 4), (-8, 0), 0.9, (0.3, 0.8))
ins = texture(np.concatenate([load('0425'), load('0426')]), T, (4, 8), 1.0)
night = texture(load('0315'), T, (6, 12), 1.5)
cn = reverb(norm(lp(drop, 5000), -32), 1.6, 0.4, 0.02, 4000) + norm(lp(owls, 4000), -38) + norm(ins, -42) + norm(night, -40)
save(loop(cn), 'chateau-night.mp3')

# --- the chateau at sunrise -------------------------------------------------------------
wake = texture(load('0222'), T, (6, 12), 1.5) + texture(load('0999'), T, (6, 12), 1.5)
save(loop(norm(wake, -29) + norm(fount, -34)), 'chateau-dawn.mp3')
