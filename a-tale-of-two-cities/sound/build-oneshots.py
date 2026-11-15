#!/usr/bin/env python3
"""A Tale of Two Cities: one-shots built for Book the First · 14 Nov 2026.
  whip-crack.mp3     the coachman's whip (BigSoundBank #2949)
  horse-snort.mp3    the near leader shaking his head: two snorts (#0285, #0286)
  shoe-hammer-1/2    the shoemaker's small hammer on a last, a few light taps, in the garret (#0005, #0006)
  pocket-watch.mp3   Mr. Lorry's loud watch ticking under his waistcoat (#1372)
usage: build-oneshots.py <bsb dir> <out dir>"""
import sys, subprocess, numpy as np, scipy.signal as sg
SRC, OUT = sys.argv[1], sys.argv[2]; SR = 44100; R = np.random.default_rng(1775)
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', SRC + '/bsb-' + f + '.mp3', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def lp(x, f): return sg.sosfilt(sg.butter(2, f, 'low', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def hp(x, f): return sg.sosfilt(sg.butter(2, f, 'high', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def fade(x, a, b):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)[:, None]
    if nb: x[-nb:] *= np.linspace(1, 0, nb)[:, None]
    return x
def room(x, t60=0.45, wet=0.25):
    n = int(t60 * SR); ir = R.standard_normal(n).astype(np.float32) * np.exp(-6.9 * np.arange(n) / n)
    ir = sg.sosfilt(sg.butter(2, 3000, 'low', fs=SR, output='sos'), ir) / np.sqrt(np.sum(ir ** 2))
    y = np.stack([sg.fftconvolve(x[:, c], ir)[:len(x)] for c in (0, 1)], 1).astype(np.float32)
    return x * (1 - wet) + y * wet * 3
def onsets(m, thr=-28, gap=0.12):
    e = np.sqrt(sg.lfilter(np.ones(96) / 96, 1, m ** 2)); d = 20 * np.log10(e + 1e-9); on = []; last = -1e9
    for i in np.where((d[1:] > thr) & (d[:-1] <= thr))[0]:
        if i - last > gap * SR: on.append(i); last = i
    return on
def save(x, name, peak=-3):
    x = np.concatenate([x, np.zeros((int(0.2 * SR), 2), np.float32)])
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (peak / 20)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', OUT + '/' + name],
                   input=x.astype(np.float32).tobytes(), check=True); print(name, '%.1f s' % (len(x) / SR))

save(fade(lp(load('2949'), 9000), 0, 0.3), 'whip-crack.mp3')
a, b = load('0285'), load('0286')
save(lp(np.concatenate([a, np.zeros((int(0.35 * SR), 2), np.float32), b * 0.8]), 7000), 'horse-snort.mp3', -4)
for k, src in ((1, '0005'), (2, '0006')):
    x = load(src); m = x.mean(1); hits = [x[o:o + int(0.18 * SR)] for o in onsets(m)]
    hits = [fade(h, 0.001, 0.12) for h in hits if len(h) == int(0.18 * SR)]
    out = np.zeros((int(3.2 * SR), 2), np.float32); t = 0.05
    for i in range(int(R.integers(4, 7))):                # a few light taps, tap-tap … tap
        h = hits[R.integers(len(hits))] * R.uniform(0.6, 1.0); s = int(t * SR); out[s:s + len(h)] += h
        t += R.choice([0.28, 0.32, 0.55, 0.9])
        if t > 2.9: break
    save(room(lp(hp(out, 180), 5000)), 'shoe-hammer-%d.mp3' % k, -6)
x = load('1372')[int(5 * SR):int(13 * SR)]
save(fade(lp(hp(x, 700), 6000), 1.0, 2.0), 'pocket-watch.mp3', -8)
