#!/usr/bin/env python3
"""A Tale of Two Cities: the title theme for the Amenti Studios page · 15 Nov 2026.
The book's own score as one suite, its moods in the order of the story, crossfaded 6 s:
  period (the overture, "Recalled to Life") → recalled → tender → rising (the Revolution)
  → terror → farewell (Carton's hymn, played to its end).
Writes theme-two-cities.mp3 and prints where each mood begins (the page's scenes follow it).
usage: build-theme.py  (run in this folder)"""
import subprocess, numpy as np
SR = 44100; X = 6.0
PARTS = [('period', 40), ('recalled', 36), ('tender', 36), ('rising', 40), ('terror', 36), ('farewell', None)]
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
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-b:a', '160k', 'theme-two-cities.mp3'], input=out.tobytes(), check=True)
print('theme-two-cities.mp3 %.1f s' % (len(out) / SR))
