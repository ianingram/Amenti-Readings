#!/usr/bin/env python3
"""The gulls of Treasure Island, as players · 14 Nov 2026.

Ian: "the seagulls, come on. They have been so instrumental in the past. Sometimes
close and boisterous, sometimes far away, swooping down." Built from the gulls we
already have, no new sources:
  gull.mp3          Western Gull, Golden Gate National Recreation Area (National Park Service, PD)
  ../../dracula/sound/gulls.mp3   Gull 1 (avphillips, Wikimedia Commons, PD)
Every cry is cut out and placed again at a distance: near = bright, dry, loud;
far = dull, late, a long tail of air. Three versions of each, so no two sound alike.

  gull-near-1..3    one gull close, loud, boisterous (two or three cries)
  gull-pair-1..3    two wheeling overhead, answering each other
  gull-laugh-1..2   one holding forth, the long laughing run
  gull-far-1..3     a single cry, far off over the water
  gull-swoop-1..3   one dives past: far, rising to near and away, the pitch dropping as it passes
  gull-flock-1..2   a flock startled up (by a shot): wings, then cries scattering away
usage: build-gulls.py <out dir>
"""
import numpy as np, scipy.signal as sg, subprocess, sys, os
SR = 44100; OUT = sys.argv[1] if len(sys.argv) > 1 else './'
HERE = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(1883)
def mp3(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(r, np.float32).copy()
def lp(x, f): return sg.sosfilt(sg.butter(2, f, 'low', fs=SR, output='sos'), x).astype(np.float32)
def hp(x, f): return sg.sosfilt(sg.butter(2, f, 'high', fs=SR, output='sos'), x).astype(np.float32)
def reverb(x, rt, wet, seed, bright=5000):
    r = np.random.default_rng(seed); n = int(rt * SR); t = np.arange(n) / SR
    ir = lp(r.standard_normal(n) * np.exp(-6.91 * t / rt), bright); ir /= np.sqrt(np.sum(ir ** 2))
    return ((1 - wet) * x + wet * sg.fftconvolve(x, ir)[:len(x)]).astype(np.float32)
def cries(x, prom=4.0, below=14.0):
    """each cry: a loudness peak, cut from the quiet before it to the quiet after it"""
    w = int(0.03 * SR); e = np.sqrt(np.maximum(np.convolve(x ** 2, np.ones(w) / w, 'same'), 0))
    st = int(0.01 * SR); db = 20 * np.log10(e[::st] + 1e-9)
    pk, _ = sg.find_peaks(db, distance=int(0.22 / 0.01), prominence=prom, height=db.max() - below)
    out = []
    for k, p_ in enumerate(pk):
        lo = pk[k - 1] if k else max(0, p_ - 60); hi = pk[k + 1] if k + 1 < len(pk) else min(len(db) - 1, p_ + 60)
        a = lo + int(np.argmin(db[lo:p_ + 1])); b = p_ + int(np.argmin(db[p_:hi + 1]))
        seg = x[a * st: b * st].copy()
        if 0.15 <= len(seg) / SR <= 1.3: out.append(seg)
    return out
def at(x, dist, semis=0.0):
    if semis: x = sg.resample(x, int(len(x) / 2 ** (semis / 12))).astype(np.float32)
    x = hp(x, 300) / (np.abs(x).max() + 1e-9)
    x = lp(x, 9000 - 6500 * dist); f = int(0.01 * SR); x[:f] *= np.linspace(0, 1, f); x[-f * 4:] *= np.linspace(1, 0, f * 4)
    y = reverb(np.concatenate([x, np.zeros(int((1.5 + 2.5 * dist) * SR), np.float32)]), 1.0 + 2.4 * dist, 0.1 + 0.5 * dist, seed=int(dist * 100) + 3, bright=int(6500 - 4000 * dist))
    return y * (1.0 - 0.8 * dist)
def put(buf, x, t):
    i = int(t * SR); n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n]
def write(x, name):
    x = np.clip(x * 0.55, -0.98, 0.98); tmp = OUT + name + '.wav'     # one gain for all: a far gull stays quiet
    import scipy.io.wavfile as wv; wv.write(tmp, SR, (x * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ar', '44100', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '112k', OUT + name], check=True); os.remove(tmp)
    print(name, round(len(x) / SR, 2), 's')

W = mp3(os.path.join(HERE, 'gull.mp3')); G = mp3(os.path.join(HERE, '..', '..', 'dracula', 'sound', 'gulls.mp3'))
C = cries(W) + cries(G)
C = [c for c in C if 0.18 < len(c) / SR < 1.6]
LONG = G[int(0.15 * SR): int(3.35 * SR)].copy()          # the laughing run (Gull 1, first 3.2 s)
print(len(C), 'cries found; laugh', round(len(LONG) / SR, 2), 's')
pick = lambda: C[rng.integers(len(C))]

for k in range(3):                                         # near: one gull, close and boisterous
    b = np.zeros(int(6 * SR), np.float32); t = 0.05
    for _ in range(2 + k % 2): x = at(pick(), 0.08 + 0.08 * rng.random(), rng.uniform(-0.6, 0.8)); put(b, x, t); t += len(x) / SR * 0.28 + rng.uniform(0.05, 0.35)
    write(b[:int((t + 1.6) * SR)], 'gull-near-%d.mp3' % (k + 1))
for k in range(3):                                         # pair: two, overhead, answering
    b = np.zeros(int(8 * SR), np.float32); t = 0.05
    for q in range(4 + k):
        x = at(pick(), 0.25 + 0.15 * rng.random(), (1.3 if q % 2 else -0.4) + rng.uniform(-0.3, 0.3)); put(b, x * (0.8 if q % 2 else 1), t); t += rng.uniform(0.35, 0.9)
    write(b[:int((t + 2.5) * SR)], 'gull-pair-%d.mp3' % (k + 1))
for k in range(2):                                         # laugh: holding forth
    write(at(LONG, 0.2 + 0.3 * k, -0.5 * k), 'gull-laugh-%d.mp3' % (k + 1))
for k in range(3):                                         # far: one cry over the water
    write(at(pick(), 0.78 + 0.07 * k, rng.uniform(-0.5, 0.5)), 'gull-far-%d.mp3' % (k + 1))
for k in range(3):                                         # swoop: far, rising near, past and away; pitch drops as it passes
    b = np.zeros(int(7 * SR), np.float32); seq = [0.85, 0.55, 0.2, 0.05, 0.4, 0.8]; t = 0.05
    for q, d in enumerate(seq):
        semis = 1.2 if q < 3 else -1.0 - 0.4 * (q - 3)
        x = at(pick(), d, semis + rng.uniform(-0.2, 0.2)); put(b, x, t); t += (0.45 if q < 3 else 0.6) + 0.15 * rng.random()
    write(b[:int((t + 2.5) * SR)], 'gull-swoop-%d.mp3' % (k + 1))
for k in range(2):                                         # flock: startled up — wings, then cries scattering away
    b = np.zeros(int(9 * SR), np.float32)
    for q in range(14 + 4 * k):                            # wingbeats: short dull bursts, thinning
        m = int(0.11 * SR); w = lp(rng.standard_normal(m).astype(np.float32), 650) * np.exp(-np.arange(m) / SR * 24).astype(np.float32)
        put(b, w * 0.5 * (1 - q / 22), 0.02 + q * 0.065 + 0.02 * rng.random())
    for q in range(9 + 2 * k):
        d = min(0.92, 0.15 + 0.08 * q); put(b, at(pick(), d, 0.8 + rng.random()) * 1.1, 0.12 + q * 0.3 + 0.12 * rng.random())
    write(b, 'gull-flock-%d.mp3' % (k + 1))
