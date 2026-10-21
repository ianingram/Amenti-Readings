#!/usr/bin/env python3
"""Two light underscores for Dracula Book I — music that is always there, quietly, under the voice.

21 Oct 2026, Ian: "I haven't really heard any light score filling in." The big moments (dread,
the journey) rise out of these and settle back into them. Each is six minutes, through-composed
and sparse, so its loop is not heard inside a chapter: slow chords on the string sections that
change every 20–30 s with long bows, a low drone that comes and goes, a harp note now and then.

  score-under-castle.mp3  D minor, the castle chapters (II–IV) and the night drive in I.
  score-under-light.mp3   D major, the inns and the journal in I (Klausenburgh, Bistritz).

Instruments: Versilian Studios, VSCO 2 Community Edition (CC0; credit requested). Seed 1897.
"""
import numpy as np, sys, os
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else '/tmp/journey/']
exec(open('/tmp/journey/build-journey.py').read().split('# ── the form')[0])   # helpers, banks, held(), reverb …
BANK['harp'] = bank('Strings/Harp/*.wav', r'KSHarp_([A-G]#?\d)_mf')
BANK['vc_sus2'] = BANK['vc_sus']
def harp(m, dur=6.0):
    f, semis = nearest('harp', m); s = load(f, semis); n = min(len(s), int(dur * SR)); x = s[:n].copy()
    r = int(0.6 * SR); x[-r:] *= np.linspace(1, 0, r); return x

def build(name, prog, drone, seed, harp_notes, high=None):
    rs = np.random.default_rng(seed)
    L = 366.0; N = int(L * SR); t = np.arange(N) / SR
    mid = np.zeros(N, np.float32); low = np.zeros(N, np.float32); hp_ = np.zeros(N, np.float32); hi_ = np.zeros(N, np.float32)
    # chords: [(start s, [midi…])], each held into the next with an overlap
    for k, (t0, notes) in enumerate(prog):
        t1 = prog[k + 1][0] if k + 1 < len(prog) else L
        d = t1 - t0 + 6.0
        for j, m in enumerate(notes):
            inst = 'vla_sus' if m < 64 else 'vln_sus'
            x = held(inst, m, d, xf=0.8)
            a = min(int(4.0 * SR), len(x) // 3); x[:a] *= np.linspace(0, 1, a) ** 1.5          # bowed in slowly
            r = min(int(5.0 * SR), len(x) // 3); x[-r:] *= np.linspace(1, 0, r) ** 1.2
            put(mid, x, t0 + rs.uniform(0, 1.2), 0.24 if j else 0.3)
    # the drone: comes and goes on long, unrelated swells
    for m, per, ph, g in drone:
        x = held('vc_sus', m, L, xf=0.8)
        sw = np.clip(0.15 + 0.85 * (0.5 + 0.5 * np.sin(2 * np.pi * t / per + ph)), 0, 1) ** 1.6
        low += x[:N] * sw.astype(np.float32) * g
    for tt, m in harp_notes:
        put(hp_, harp(m), tt, 0.5 + 0.2 * rs.random())
    if high:
        for tt, m, d in high:
            x = held('vln_sus', m, d, xf=0.8); a = int(3 * SR); x[:a] *= np.linspace(0, 1, a); put(hi_, x, tt, 0.13)
    mix = reverb(mid + low, 3.0, 0.32, seed=seed) + reverb(hp_, 3.4, 0.4, seed=seed + 1) * 0.8 + reverb(hi_, 3.6, 0.45, seed=seed + 2)
    write_mp3(rms_db(fold(mix, 6.0), -26), name, br='96k')
    print(name, round(L - 6.0, 1), 's')

# ── the castle: D minor, never resolving far ──
Dm, Bb, Gm, Asus, A, F, Eb, C = [50, 57, 62, 65], [46, 58, 62, 65], [43, 55, 62, 67], [45, 57, 62, 64], [45, 57, 61, 64], [41, 57, 60, 65], [39, 58, 63, 67], [48, 55, 60, 64]
castle = [(0, Dm), (26, Bb), (50, Gm), (76, Asus), (98, Dm), (124, F), (150, Gm), (172, Eb), (198, Dm), (224, Bb), (246, C), (272, Asus),
          (296, A), (318, Dm), (342, Dm)]
build('score-under-castle.mp3', castle, [(38, 23, 0.0, 0.28), (45, 37, 1.9, 0.18)], 7,
      [(14, 62), (61, 69), (112, 65), (163, 70), (209, 62), (258, 72), (305, 69), (351, 62)],
      high=[(88, 81, 14), (190, 77, 12), (286, 82, 16)])

# ── the inns and the journal: D major, warm and plain ──
D_, G_, Bm, A_, Em, Fs = [50, 57, 62, 66], [43, 59, 62, 67], [47, 59, 62, 66], [45, 57, 61, 64], [40, 55, 59, 67], [42, 57, 61, 66]
light = [(0, D_), (24, G_), (46, Bm), (70, A_), (92, D_), (118, Em), (140, G_), (164, A_), (188, Bm), (212, Fs), (234, G_),
         (258, D_), (282, Em), (304, A_), (330, D_), (350, D_)]
build('score-under-light.mp3', light, [(38, 29, 0.6, 0.22)], 9,
      [(10, 74), (37, 78), (66, 71), (101, 74), (131, 76), (159, 73), (196, 78), (227, 74), (263, 81), (296, 76), (326, 74), (355, 78)],
      high=[(80, 78, 12), (200, 81, 14), (310, 76, 12)])
