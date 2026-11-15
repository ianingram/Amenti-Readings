#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Second (chapters 19-30): the new rooms · 15 Nov 2026.
  funeral-mob.mp3      Roger Cly's funeral coming down Fleet Street: a jeering, bawling mob round
                       a hearse and a mourning coach, horses at a walk, wheels
  churchyard.mp3       the churchyard in the fields at night: the night air, grass and leaves, an owl
  versailles.mp3       the crowd at Versailles waiting for the King and Queen: talk, horses far off,
                       a swell of shouting now and then
  rising.mp3           Saint Antoine rising: a vast crowd seething, drums and bells far off
  bastille.mp3         the attack on the Bastille: the roar of the crowd, cannon, musketry, drums, bells
  bastille-within.mp3  inside the fortress: the storm outside heard through the stone, dull and subdued
  chateau-fire.mp3     the chateau burning: the roar of the fire, the wind it makes, timbers cracking
  village-fire.mp3     the village at its fountain watching the fire: the tocsin, people, the fire far off
  soho-night.mp3       the quiet corner in Soho on a moonlit night: insects, the city very far off
Real recordings only (BigSoundBank, CC0 — numbers in sound/SOURCES.md). Nothing in a room repeats
inside its 60 s; the seam is crossfaded. The protest recordings are French chants: they are cut
into short grains and shuffled so no words or rhythm survive.
usage: build-rooms-b2b.py <out dir> <bsb dir> [more bsb dirs …]"""
import sys, os, subprocess, numpy as np, scipy.signal as sg
OUT, DIRS = sys.argv[1], sys.argv[2:]; SR = 44100; N = 60 * SR; XF = 6 * SR; T = N + XF
R = np.random.default_rng(1789)
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
def grains(x, n, L=(0.6, 1.8), layers=3):
    """Short shuffled grains, several layers deep: a crowd with no words and no rhythm left in it."""
    out = np.zeros((n, 2), np.float32)
    for _ in range(layers):
        t = 0
        while t < n:
            l = int(R.uniform(*L) * SR); a = R.integers(0, len(x) - l - 1); s = fade(x[a:a + l], 0.15, 0.25)
            if R.random() < 0.5: s = s[:, ::-1]
            m = min(l, n - t); out[t:t + m] += s[:m] * db(R.uniform(-4, 0)); t += l - int(0.2 * SR)
    return out
def scatter(x, n, every, L, g=(-8, 0), pan=0.8, xf=(0.2, 0.6)):
    """Pieces of a recording dropped here and there."""
    out = np.zeros((n, 2), np.float32); t = R.uniform(*every) / 2
    while t < n / SR:
        l = int(R.uniform(*L) * SR); a = R.integers(0, max(1, len(x) - l))
        put(out, fade(x[a:a + l], *xf), t, db(R.uniform(*g)), R.uniform(-pan, pan)); t += R.uniform(*every)
    return out
def drop(hits, n, every, g=(-8, 0), pan=0.8, semis=(0, 0)):
    """Whole events (a cannon shot, a volley) dropped at random times."""
    out = np.zeros((n, 2), np.float32); t = R.uniform(*every) / 2
    while t < n / SR:
        h = hits[R.integers(len(hits))]
        if semis != (0, 0): h = pitch(h, R.uniform(*semis))
        put(out, h, t, db(R.uniform(*g)), R.uniform(-pan, pan)); t += R.uniform(*every)
    return out
def loop(x):
    y = x[:N].copy(); w = np.linspace(0, 1, XF)[:, None]
    y[:XF] = x[N:N + XF] * (1 - w) + y[:XF] * w; return y
def reverb(x, secs, wet, pre=0.02, bright=4000):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = R.standard_normal((n, 2)).astype(np.float32) * np.exp(-6.9 * t / secs)[:, None]
    ir = lp(ir, bright); ir[:int(pre * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
    w = np.stack([sg.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in (0, 1)], 1)
    return (x * (1 - wet) + w * wet * 3).astype(np.float32)
def env(x, w=0.02):
    m = np.abs(x).mean(1); k = int(w * SR); return np.sqrt(sg.lfilter(np.ones(k) / k, 1, m ** 2))
def onsets(m, thr=-30, gap=0.08):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, m ** 2)); d = 20 * np.log10(e / (e.max() + 1e-9) + 1e-9); on = []; last = -1e9
    for i in np.where((d[1:] > thr) & (d[:-1] <= thr))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on
def events(x, L, thr=-24, gap=0.4):
    """Each loud event in a recording, L seconds long from its onset."""
    out = []
    for o in onsets(x.mean(1), thr, gap):
        s = x[max(0, o - 200): o + int(L * SR)]
        if len(s) > 0.8 * L * SR: out.append(fade(s / (np.abs(s).max() + 1e-9), 0.003, L * 0.5))
    return out
def tame(x, over=12):
    """Hold peaks to `over` dB above the RMS (fire recordings crackle at 0 dB over a bed at -45)."""
    c = rms(x) * db(over); a = np.abs(x).max(1)
    g = np.minimum(1.0, c / (np.maximum.reduce([np.roll(a, -k) for k in range(0, int(0.004 * SR), 8)]) + 1e-9))
    g = np.minimum(g, sg.lfilter([0.002], [1, -0.998], g))           # quick to duck, slow to come back
    return (x * g[:, None]).astype(np.float32)
def save(x, name):
    x = x / max(1.0, np.abs(x).max() / db(-1))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', OUT + '/' + name],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(name, '%.1f s' % (len(x) / SR), 'rms %.1f dB' % (20 * np.log10(rms(x))))

hoof = []
for n in ('0610', '0611'):
    h = load(n); hoof += [s / (np.abs(s).max() + 1e-9) for s in events(h, 0.22, -30, 0.08)]
def walk_by(n, every, dur=(6, 10)):
    """Horses at a slow walk going by (the procession)."""
    out = np.zeros((n, 2), np.float32); t = R.uniform(0, every[0])
    while t < n / SR:
        D = R.uniform(*dur); stride = R.uniform(1.15, 1.35); p0 = R.uniform(-1, 1); k = 0.0
        while k < D:
            for ph in (0, 0.25, 0.5, 0.75):
                u = (k + ph * stride) / D; e = np.sin(np.pi * min(1, u)) ** 2
                put(out, pitch(hoof[R.integers(len(hoof))], R.uniform(-2, 1)), t + k + ph * stride + R.normal(0, 0.015), e * db(R.uniform(-5, 0)), p0 * (1 - 2 * u))
            k += stride
        t += D * R.uniform(0.5, 1.0) + R.uniform(*every)
    return out

protest = cat('2980', '2982', '3382', '0108', '2981', '2983', '3383', '3385', '3386', '3389', '3390', '3391')
crowd = cat('3515', '3516')
shouts = cat('0236', '0237')
talk = cat('2968', '2969')
night = load('0315'); leaves = load('0659'); fount = hp(texture(load('0913'), T, (5, 10), 1.5), 250)
owls = cat('0429', '1400')
rolls = [fade(load(n), 0.01, 0.6) for n in ('2402', '2405', '2408')]
bells = cat('0135', '0830', '0829')

# --- Roger Cly's funeral: the mob in Fleet Street ------------------------------------------
mob = lp(hp(grains(protest, T, (0.5, 1.4), 4), 160), 2600)
jeer = lp(scatter(shouts, T, (2, 5), (0.6, 1.5), (-10, -3), 0.9, (0.05, 0.3)), 2200)
proc = lp(walk_by(T, (1, 3)), 2200) + lp(texture(load('1316'), T, (4, 8), 1.0), 1200)
save(loop(norm(mob, -25) + norm(texture(crowd, T, (3, 6), 0.8), -29) + norm(jeer, -33) + norm(proc, -31)), 'funeral-mob.mp3')

# --- the churchyard at night ---------------------------------------------------------------
cy = norm(texture(night, T, (6, 12), 1.5), -33) + norm(lp(texture(leaves, T, (6, 12), 1.5), 2500), -38) \
   + norm(lp(scatter(owls, T, (14, 26), (2, 4), (-8, 0), 0.9, (0.3, 0.8)), 4000), -40)
save(loop(cy), 'churchyard.mp3')

# --- Versailles: the crowd waiting for the carriage of the King and Queen -------------------------
swell = lp(scatter(load('0019'), T, (14, 24), (5, 9), (-6, 0), 0.6, (2.0, 2.5)), 1800)
vs = norm(lp(texture(crowd, T, (3, 7), 0.8), 3500), -27) + norm(lp(texture(talk, T, (4, 8), 1.0), 3000), -31) \
   + norm(lp(walk_by(T, (6, 12)), 1500), -38) + norm(swell, -36)
save(loop(vs), 'versailles.mp3')

# --- Saint Antoine rising --------------------------------------------------------------------
seethe = lp(hp(grains(protest, T, (0.6, 1.8), 5), 140), 2400)
far_drum = lp(drop(rolls, T, (6, 12), (-8, 0), 0.7), 1500)
far_bell = lp(scatter(bells, T, (10, 20), (3, 6), (-8, 0), 0.8, (0.5, 1.5)), 1800)
rs = norm(seethe, -24) + norm(lp(texture(crowd, T, (3, 6), 0.8), 2500), -28) + norm(far_drum, -34) + norm(reverb(far_bell, 2.5, 0.5, 0.05, 2000), -37)
save(loop(rs), 'rising.mp3')

# --- the attack on the Bastille ----------------------------------------------------------------
boom = []
for n in ('1023', '1806', '1807', '1808'):
    x = load(n); e = env(x, 0.01); i = int(np.where(20 * np.log10(e / e.max() + 1e-9) > -20)[0][0])
    b = x[max(0, i - int(0.05 * SR)): i + int(4.5 * SR)]; boom.append(fade(lp(b, 1600), 0.02, min(2.5, len(b) / SR / 2)))
shots = []
for n in ('2853', '2854', '0397', '0532'):
    shots += events(load(n), 0.9, -20, 0.25)
print('cannon', len(boom), 'shots', len(shots))
def volleys(n, every):
    """Musketry: a ragged volley of a few to a dozen shots, then nothing for a while."""
    out = np.zeros((n, 2), np.float32); t = R.uniform(*every) / 2
    while t < n / SR:
        for k in range(R.integers(3, 12)):
            put(out, lp(shots[R.integers(len(shots))], R.uniform(2500, 4500)), t + R.uniform(0, 1.4), db(R.uniform(-12, -2)), R.uniform(-0.9, 0.9))
        t += R.uniform(*every)
    return out
roar = lp(hp(grains(protest, T, (0.4, 1.2), 7), 130), 2800)
guns = reverb(volleys(T, (2.5, 6)), 2.2, 0.45, 0.04, 3000)
cann = reverb(drop(boom, T, (4, 9), (-6, 0), 0.6, (-4, -1)), 3.5, 0.4, 0.06, 1800)
drums = lp(drop(rolls, T, (3, 7), (-6, 0), 0.8), 3000)
bs = norm(roar, -22) + norm(lp(texture(crowd, T, (2, 5), 0.6), 2600), -26) + norm(guns, -27) + norm(cann, -25) \
   + norm(drums, -31) + norm(reverb(far_bell, 2.5, 0.5, 0.05, 2000), -33)
save(loop(bs), 'bastille.mp3')

# --- within the fortress: the storm heard through stone ------------------------------------------
drips = scatter(cat('1386', '1387'), T, (1.5, 4), (0.6, 1.4), (-12, 0), 0.5, (0.05, 0.3))
inside = norm(lp(lp(bs, 380), 380), -31) + norm(reverb(lp(drips, 4000), 1.8, 0.5, 0.02, 3500), -40)
save(loop(inside), 'bastille-within.mp3')

# --- the chateau burning -------------------------------------------------------------------------
big = tame(tame(cat('0987', '0988', '0989'))); gas = tame(cat('1341', '1342')); crack = cat('2855', '2856', '2857')
pops = scatter(crack, T, (0.8, 2.5), (0.4, 1.0), (-10, 0), 0.9, (0.01, 0.2))
fire = norm(texture(big, T, (4, 8), 1.0), -25) + norm(lp(texture(gas, T, (4, 8), 1.2), 900), -26) \
     + norm(lp(texture(leaves, T, (6, 12), 1.5), 1500), -33)
fire = fire + pops / np.abs(pops).max() * np.abs(fire).max() * 0.6    # the cracks no louder than the fire's own peaks
save(loop(fire), 'chateau-fire.mp3')

# --- the village at its fountain, the tocsin ringing, the fire on the sky -------------------------
strokes = events(load('0135'), 2.5, -18, 0.3)
print('bell strokes', len(strokes))
toc = np.zeros((T, 2), np.float32); t = 0.5
while t < T / SR:                                          # rung impatiently: runs of strokes, ragged, with breaks
    for k in range(R.integers(6, 16)):
        put(toc, strokes[R.integers(len(strokes))], t, db(R.uniform(-4, 0)), -0.3); t += R.uniform(0.55, 0.95)
    t += R.uniform(1.5, 4)
vf = norm(fount, -32) + norm(lp(fire, 500), -31) + norm(reverb(lp(toc, 3500), 2.5, 0.4, 0.05, 3000), -29) \
   + norm(lp(texture(talk, T, (4, 8), 1.0), 1800), -36)
save(loop(vf), 'village-fire.mp3')

# --- the corner in Soho on a moonlit night ---------------------------------------------------------
sn = norm(texture(cat('0425', '0426'), T, (4, 8), 1.0), -40) + norm(texture(night, T, (6, 12), 1.5), -37) \
   + norm(lp(texture(leaves, T, (6, 12), 1.5), 2500), -42) + norm(lp(texture(talk, T, (5, 9), 1.0), 400), -50)
save(loop(sn), 'soho-night.mp3')
