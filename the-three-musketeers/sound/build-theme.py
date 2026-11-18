#!/usr/bin/env python3
"""The Three Musketeers: the title theme for the Amenti Studios page · 18 Nov 2026.
Writes theme-three-musketeers.mp3 and prints where each mood begins (the page's scenes follow it).
usage: build-theme.py  (run in this folder)"""
import subprocess, numpy as np
SR = 44100; X = 6.0
PARTS = [('gascony', 40), ('meung', 30), ('intrigue', 36), ('romance', 36), ('gascony', None)]
def load(n):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'score-%s.mp3' % n, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
out = np.zeros((0, 2), np.float32); x = int(X * SR); t = 0.0
for k, (n, secs) in enumerate(PARTS):
    a = load(n); a = a[: int(secs * SR)] if secs else a
    a = a / (np.sqrt((a ** 2).mean()) + 1e-9) * 10 ** (-20 / 20)          # every mood at one level
    if k: a[:x] *= np.linspace(0, 1, x)[:, None]
    if secs: a[-x:] *= np.linspace(1, 0, x)[:, None]
    else: a[-int(8 * SR):] *= np.linspace(1, 0, int(8 * SR))[:, None]
    start = len(out) - (x if k else 0); print('%-9s %6.1f s' % (n, start / SR))
    if k:
        pad = np.zeros((max(0, start + len(a) - len(out)), 2), np.float32); out = np.concatenate([out, pad]); out[start:start + len(a)] += a
    else: out = a
out[: int(3 * SR)] *= np.linspace(0, 1, int(3 * SR))[:, None]
out = out / max(1.0, np.abs(out).max() / 10 ** (-1 / 20))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', 'theme-three-musketeers.mp3'], input=out.tobytes(), check=True)
print('theme-three-musketeers.mp3 %.1f s' % (len(out) / SR))
