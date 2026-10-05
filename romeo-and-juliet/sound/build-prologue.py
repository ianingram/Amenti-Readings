#!/usr/bin/env python3
"""The Prologue, in time. Shakespeare speaks his sonnet one line to a bar, 4/4 at 76,
over a processional of tabor, viola-pizzicato bass and lute, the harmony walking the
sonnet's quatrains (Dm Bb C A · Dm Bb Gm A · F C Dm A) and its couplet home to D.
Each line is the engine's own render in his voice (Charon + his ledger style), cut at
its first and last sound and fitted to the bar with its pitch kept. Two bars in, two out."""
import os, json
exec(open('/tmp/rj/rj_assets.py').read().split('# ═══ THE FEAST')[0].replace("/tmp/rj/sound/", "/tmp/rj/sound/"))
def stretch(x, k):
    """draw speech out or in, pitch kept: overlap-add of short grains"""
    g = int(0.05 * SR); hop_out = g // 4; hop_in = max(1, int(round(hop_out / k))); w_ = np.hanning(g).astype(np.float32)
    n_out = int(len(x) * k) + g; y = np.zeros(n_out, np.float32); nrm = np.zeros(n_out, np.float32); i = o = 0
    while i + g < len(x) and o + g < n_out:
        y[o:o + g] += x[i:i + g] * w_; nrm[o:o + g] += w_; i += hop_in; o += hop_out
    return (y / np.maximum(nrm, 1e-3))[:o]
BPM = 76; BT = 60 / BPM; BAR = 4 * BT; INTRO = 2; LINES = 14; OUTRO = 2
CH = [(38, [50, 53, 57]), (34, [46, 50, 53]), (36, [48, 52, 55]), (33, [45, 49, 52]),
      (38, [50, 53, 57]), (34, [46, 50, 53]), (43, [55, 58, 62]), (33, [45, 49, 52]),
      (41, [53, 57, 60]), (36, [48, 52, 55]), (38, [50, 53, 57]), (33, [45, 49, 52]),
      (34, [46, 50, 53]), (33, [45, 49, 52])]
FIRST = (38, [50, 53, 57]); LAST = (38, [50, 54, 57])                 # in on D minor; home on D major
bars = [FIRST, FIRST] + CH + [LAST, LAST]
N = int((len(bars) * BAR + 6) * SR)
band = np.zeros(N, np.float32); voice = np.zeros(N, np.float32)
TAB = load16('/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_higher/tenorH_f_1.wav') * 0.5
TABL = load16('/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f_1.wav') * 0.6 if os.path.exists('/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f_1.wav') else TAB
for b, (root, tri) in enumerate(bars):
    t0 = b * BAR; last = b >= len(bars) - OUTRO
    if last and b == len(bars) - 1: break
    put(band, pluck(VAPZ, root - 12, 0.9), t0); put(band, pluck(VAPZ, root - 12, 0.6), t0 + 2 * BT)           # bass on 1 and 3
    for k, m in enumerate([tri[0], tri[1], tri[2], tri[1]] * 2):                                              # lute in quavers
        put(band, pluck(VPIZZ, m + 12, 0.5 if k % 2 else 0.62), t0 + k * BT / 2 + 0.004 * (k % 3))
    for t_, x, g in ((0, TABL, 0.8), (2 * BT, TAB, 0.6), (3.5 * BT, TAB, 0.3)): put(band, x, t0 + t_, g)       # the tabor: 1, 3, and the and of 4
fin = len(bars) - 1; root, tri = bars[fin]
for m in [root - 12, tri[0], tri[1], tri[2], tri[2] + 12]: put(band, pluck(VPIZZ if m > 45 else VAPZ, m, 0.7), fin * BAR + 0.01 * (m % 5))   # a last spread chord
put(band, TABL, fin * BAR, 0.9)
SP = json.load(open('/tmp/rj/pro/spans.json')); FIT = BAR * 0.93
for i in range(LINES):
    a_, b_ = SP[i]; x = load16('/tmp/rj/pro/line%02d.wav' % (i + 1))[int(max(0, a_ - 0.03) * SR): int((b_ + 0.06) * SR)]
    k = FIT / (len(x) / SR)
    if abs(k - 1) > 0.03: x = stretch(x, k)
    x = x / (np.sqrt(np.mean(x[np.abs(x) > 0.02 * np.abs(x).max()] ** 2)) + 1e-9) * 0.12
    put(voice, x, (INTRO + i) * BAR - 0.03)                            # the line lands on the downbeat
voice = reverb(hp(voice, 70), 1.4, 0.16, seed=31, bright=6000)
band = reverb(band, 1.8, 0.22, seed=32)
def at(x, db, a=INTRO * BAR, b=(INTRO + LINES) * BAR):
    s_ = x[int(a * SR): int(b * SR)]; return x * (10 ** (db / 20) / (np.sqrt(np.mean(s_ ** 2)) + 1e-12))
mix = at(voice, -17) + at(band, -25)
mix = mix[: int((len(bars) * BAR + 4) * SR)]
mix = env(mix, [(0, 0), (0.05, 1), (len(mix) / SR - 2.5, 1), (len(mix) / SR, 0)])
write_mp3(rms_db(mix, -19), 'prologue-chorus.mp3', br='192k')
print(files, round(len(bars) * BAR, 1), 's of music')
