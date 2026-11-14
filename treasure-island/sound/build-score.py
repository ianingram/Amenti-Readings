#!/usr/bin/env python3
"""The score of Treasure Island · 14 Nov 2026.

Ian, on first hearing the voiced book: "there was no score. Most movies or stage
productions start with at least 30 seconds of score that repeats as motifs through
the production ... each scene should have its own score. A light meandering works
best for the stage play, emphasis on certain sequences."

THE THEME (original; Stevenson wrote no tune). 6/8, D minor, a rolling sea lilt:
  A   A4 D5 D5 E5 | F5 . E5 D5 | C5 A4 F4 A4 | E4 . A4 .        (a question, to the dominant)
  A'  A4 D5 D5 E5 | F5 . G5 A5 | A5 G5 F5 E5 | D5 . . .         (answered, home)
  B   C5 F5 F5 G5 | A5 . G5 F5 | E5 C5 D5 Bb4| A4 . . .         (the relative major: the voyage)
Every underscore below quotes its first two bars as the motif: on a cello at the inn,
an oboe in Bristol, a horn at sea, a flute on the island, a clarinet on the hunt, and
in D major, at last, going home.

FILES (each underscore 6 min, through-composed and sparse, loops unheard in a chapter)
  score-overture.mp3        60 s: timpani and drone, the horn alone, the theme, tutti, and a long settle
  score-under-inn.mp3       D minor  · Part One, the Admiral Benbow (ch 1–6)
  score-under-bristol.mp3   G major  · Bristol and the Spy-glass (ch 7–9)
  score-under-voyage.mp3    F major / D minor, 6/8 harp lilt · at sea (ch 10–12, 25)
  score-under-island.mp3    E minor  · the island, its strangeness (ch 13–15, 22)
  score-under-stockade.mp3  A minor, a slow low pulse · the stockade and the camp (ch 16–21, 26–30)
  score-under-hunt.mp3      D minor, wandering · the treasure hunt (ch 31–33)
  score-under-home.mp3      D major  · "and last" (ch 34)

Instruments: Versilian Studios, VSCO 2 Community Edition (CC0; credit requested).
Helpers (load, held, reverb, banks) from dracula/sound/build-journey.py.
usage: build-score.py <out dir>   (samples at /tmp/vsco/)
"""
import numpy as np, sys, os
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else './'
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '..', '..', 'dracula', 'sound', 'build-journey.py')).read().split('# ── the form')[0]
sys.argv = [sys.argv[0], OUTDIR if OUTDIR.endswith('/') else OUTDIR + '/']
exec(src)                                             # SR, load, put, reverb, fold, rms_db, write_mp3, bank, BANK, held, short, perc …

BANK['horn'] = bank('Brass/F Horn/sus/*.wav', r'MOHorn_sus_([A-G]#?\d)_v2')
BANK['flute'] = bank('Woodwinds/Flute/susvib/*.wav', r'LDFlute_susvib_([A-G]#?\d)_v1')
BANK['oboe'] = bank('Woodwinds/Oboe/Vib/*.wav', r'Oboe_Vib_([A-G]#?\d)_v1')
BANK['clar'] = bank('Woodwinds/Clarinet/susLong/*.wav', r'DCClar_susLong_([A-G]#?\d)_v2_rr1')
BANK['harp'] = bank('Strings/Harp/*.wav', r'KSHarp_([A-G]#?\d)_mf')
for k in ('horn', 'flute', 'oboe', 'clar', 'harp'):
    if not BANK[k]: raise SystemExit('empty bank ' + k)
TIMP_HIT = sorted(glob.glob(V + 'Percussion/Timpani/Timpani1_Hit_v3_rr*_Sum.wav'))
TIMP_ROLL = sorted(glob.glob(V + 'Percussion/Timpani/Rolls/*.wav'))

def harp(m, dur=5.0, g=1.0):
    f, semis = nearest('harp', m); s = load(f, semis); n = min(len(s), int(dur * SR)); x = s[:n].copy()
    r = int(0.5 * SR); x[-r:] *= np.linspace(1, 0, r); return x * g
def bowed(inst, m, d, att=2.5, rel=3.0):
    x = held(inst, m, d, xf=0.8)
    a = min(int(att * SR), len(x) // 3); x[:a] *= np.linspace(0, 1, a) ** 1.5
    r = min(int(rel * SR), len(x) // 3); x[-r:] *= np.linspace(1, 0, r) ** 1.2
    return x

# the theme, in eighths (midi, eighths)
TA  = [(69, 2), (74, 1), (74, 2), (76, 1), (77, 3), (76, 2), (74, 1), (72, 2), (69, 1), (65, 2), (69, 1), (64, 3), (69, 3)]
TA2 = [(69, 2), (74, 1), (74, 2), (76, 1), (77, 3), (79, 2), (81, 1), (81, 2), (79, 1), (77, 2), (76, 1), (74, 6)]
TB  = [(72, 2), (77, 1), (77, 2), (79, 1), (81, 3), (79, 2), (77, 1), (76, 2), (72, 1), (74, 2), (70, 1), (69, 6)]
MOTIF = TA[:6]                                         # the first two bars
def sing(buf, inst, notes, t0, eighth, g, oct=0, legato=1.02):
    t = t0
    for m, e in notes:
        d = e * eighth
        x = held(inst, m + oct, d * legato + 0.25, xf=0.4)
        a = min(int(0.04 * SR), len(x) // 4); x[:a] *= np.linspace(0, 1, a)
        put(buf, x, t, g); t += d
    return t
def transpose(notes, k): return [(m + k, e) for m, e in notes]
def major(notes):          # D minor -> D major: F->F#, C->C#, Bb->B
    fix = {5: 1, 0: 1, 10: 1}
    return [(m + fix.get(m % 12, 0), e) for m, e in notes]

# ── the overture ────────────────────────────────────────────────────────────
def overture():
    L = 66.0; N = int(L * SR); E8 = 0.22; BARS = 6 * E8
    mel = np.zeros(N, np.float32); strg = np.zeros(N, np.float32); low = np.zeros(N, np.float32)
    hp_ = np.zeros(N, np.float32); tp = np.zeros(N, np.float32); hn = np.zeros(N, np.float32)
    # 0–6 s: the sea before the curtain — a timpani roll on D swelling, the low drone
    if TIMP_ROLL:
        r = load(TIMP_ROLL[0], -2.0); r = r[:int(6.5 * SR)].copy(); r *= np.linspace(0.05, 1, len(r)) ** 2
        put(tp, r, 0.0, 0.5)
    put(low, bowed('vc_sus', 38, 14, att=5, rel=6), 0.0, 0.14)
    put(low, bowed('vc_sus', 45, 12, att=6, rel=5), 3.0, 0.09)
    # 4 s: the horn alone, the motif — a call across the water
    t = 4.5
    t = sing(hn, 'horn', MOTIF, t, E8 * 1.25, 0.55, oct=-12)
    # 8.5 s: the theme on the horn, strings beneath, harp rolling in sixes
    t0 = 9.0
    prog = [(0, [50, 57, 62, 65]), (1, [46, 58, 62, 65]), (2, [41, 57, 60, 65]), (3, [45, 57, 61, 64]),
            (4, [50, 57, 62, 65]), (5, [41, 57, 60, 65]), (6, [45, 55, 61, 64]), (7, [50, 57, 62, 65]),
            (8, [41, 57, 60, 65]), (9, [41, 57, 60, 65]), (10, [48, 55, 60, 64]), (11, [45, 57, 61, 64]),
            (12, [50, 57, 62, 65]), (13, [46, 58, 62, 65]), (14, [43, 58, 62, 67]), (15, [45, 57, 61, 64]),
            (16, [50, 57, 62, 65])]
    t = sing(hn, 'horn', TA, t0, E8, 0.6, oct=-12)
    t = sing(hn, 'horn', TA2, t, E8, 0.6, oct=-12)
    tB = t; t = sing(mel, 'vln_sus', TB, t, E8, 0.5)                # B: the violins take it, the voyage
    tA = t; sing(mel, 'vln_sus', TA2, tA, E8, 0.62); sing(hn, 'horn', TA2, tA, E8, 0.55, oct=-12)  # tutti
    sing(mel, 'vla_sus', TA2, tA, E8, 0.3, oct=-12)
    tEnd = tA + 24 * E8
    for b, notes in prog:
        tb = t0 + b * BARS
        if tb > tEnd + 1: break
        d = BARS + 1.2 if b < 16 else (L - tb)
        for j, m in enumerate(notes):
            inst = 'vc_sus' if m < 52 else ('vla_sus' if m < 64 else 'vln_sus')
            put(strg, bowed(inst, m, d, att=0.4 if b else 2.0, rel=0.8 if b < 16 else 10), tb, 0.16)
        for k in range(6):                                         # the harp, rolling eighths
            arp = sorted(notes)[k % 4] + (12 if k >= 3 else 0)
            put(hp_, harp(arp + 12, 1.6), tb + k * E8, 0.3)
        if b in (0, 4, 8, 12, 16) and TIMP_HIT:                    # timpani on the phrase heads
            put(tp, load(TIMP_HIT[b % len(TIMP_HIT)], 0.0), tb, 0.35 if b < 12 else 0.5)
    # the settle: a long D minor chord, the horn's motif once more, softly, and the strings breathe out
    t2 = tEnd + 3.0
    sing(hn, 'horn', MOTIF, t2, E8 * 1.5, 0.3, oct=-12)
    for tt, m in [(t2 + 4, 69), (t2 + 8, 74), (t2 + 13, 65)]: put(hp_, harp(m + 12, 5), tt, 0.35)
    mix = reverb(strg + low, 3.2, 0.34, seed=11) + reverb(mel, 3.0, 0.32, seed=12) + reverb(hn, 3.6, 0.4, seed=13) * 1.1 \
        + reverb(hp_, 3.4, 0.4, seed=14) * 0.7 + reverb(tp, 3.0, 0.35, seed=15)
    n = len(mix); f = int(8.0 * SR); mix[-f:] *= np.linspace(1, 0, f) ** 1.5
    write_mp3(rms_db(mix, -20), 'score-overture.mp3', br='128k')
    print('score-overture.mp3', round(L, 1), 's · theme at', round(t0, 1), 'B at', round(tB, 1), 'tutti at', round(tA, 1))

# ── the underscores ─────────────────────────────────────────────────────────
def under(name, prog, drone, seed, harp_notes, motifs=(), lilt=None, pulse=None, high=None):
    rs = np.random.default_rng(seed)
    L = 366.0; N = int(L * SR); t = np.arange(N) / SR
    mid = np.zeros(N, np.float32); low = np.zeros(N, np.float32); hp_ = np.zeros(N, np.float32)
    sol = np.zeros(N, np.float32); hi_ = np.zeros(N, np.float32); pz = np.zeros(N, np.float32)
    for k, (t0, notes) in enumerate(prog):
        t1 = prog[k + 1][0] if k + 1 < len(prog) else L
        for j, m in enumerate(notes):
            inst = 'vla_sus' if m < 64 else 'vln_sus'
            put(mid, bowed(inst, m, t1 - t0 + 6.0, 4.0, 5.0), t0 + rs.uniform(0, 1.2), 0.24 if j else 0.3)
        if lilt:                                                   # the sea: a harp rolling in sixes, softly
            E8 = lilt; tt = t0
            while tt < t1:
                for q in range(6):
                    m = sorted(notes)[[0, 1, 2, 3, 2, 1][q]] + 12
                    put(hp_, harp(m, 1.4), tt + q * E8, 0.16 + 0.04 * (q == 0))
                tt += 6 * E8 * (2 if rs.random() < 0.35 else 1)    # it rests now and then, as the sea does
    for m, per, ph, g in drone:
        x = held('vc_sus', m, L, xf=0.8)
        sw = np.clip(0.15 + 0.85 * (0.5 + 0.5 * np.sin(2 * np.pi * t / per + ph)), 0, 1) ** 1.6
        low += x[:N] * sw.astype(np.float32) * g
    for tt, m in harp_notes: put(hp_, harp(m), tt, 0.5 + 0.2 * rs.random())
    for tt, inst, notes, e8, g, oct in motifs: sing(sol, inst, notes, tt, e8, g, oct=oct)
    if pulse:                                                      # the stockade: a low pizzicato heartbeat
        per, m0 = pulse; tt = 2.0
        while tt < L - 8:
            seg = [p for p in prog if p[0] <= tt][-1][1]
            put(pz, short('pizz', seg[0] - 12, 1.2), tt, 0.5); tt += per * (1 if rs.random() > 0.15 else 2)
    if high:
        for tt, m, d in high: put(hi_, bowed('vln_sus', m, d, 3.0, 4.0), tt, 0.13)
    mix = reverb(mid + low, 3.0, 0.32, seed=seed) + reverb(hp_, 3.4, 0.4, seed=seed + 1) * 0.8 \
        + reverb(sol, 3.4, 0.38, seed=seed + 2) + reverb(hi_, 3.6, 0.45, seed=seed + 3) + reverb(pz, 2.2, 0.3, seed=seed + 4) * 0.7
    write_mp3(rms_db(fold(mix, 6.0), -26), name, br='96k')
    print(name, round(L - 6.0, 1), 's')

Dm, Bb, Gm, A7, F, C, Asus = [50, 57, 62, 65], [46, 58, 62, 65], [43, 55, 62, 67], [45, 55, 61, 64], [41, 57, 60, 65], [48, 55, 60, 64], [45, 57, 62, 64]
G, D, Em, Am, Cmaj, Bm, Dmaj, A_, Fs = [43, 59, 62, 67], [50, 57, 62, 66], [40, 55, 59, 67], [45, 57, 60, 64], [48, 55, 60, 64], [47, 59, 62, 66], [50, 57, 62, 66], [45, 57, 61, 64], [42, 57, 61, 66]
E_m, Cm7, B7, Esus = [40, 55, 59, 64], [48, 55, 58, 63], [47, 54, 59, 63], [40, 57, 59, 64]

def build_all():
    overture()
    # Part One — the inn: D minor, low and close; the motif on the cello, slow, three times
    under('score-under-inn.mp3',
          [(0, Dm), (28, Bb), (54, Gm), (80, Asus), (104, Dm), (130, F), (156, Gm), (180, A7), (206, Dm), (232, Bb), (256, C), (282, Asus), (306, A7), (330, Dm)],
          [(38, 23, 0.0, 0.26), (45, 37, 1.9, 0.16)], 21,
          [(16, 62), (66, 69), (118, 65), (170, 70), (222, 62), (270, 69), (322, 62)],
          motifs=[(40, 'vc_sus', MOTIF, 0.34, 0.5, -24), (190, 'vc_sus', MOTIF, 0.34, 0.45, -24), (300, 'clar', MOTIF, 0.32, 0.4, -12)])
    # Bristol: G major, brighter, the motif on the oboe in major
    under('score-under-bristol.mp3',
          [(0, G), (24, D), (48, Em), (72, Cmaj), (96, G), (120, Bm), (144, Cmaj), (168, D), (192, G), (216, Em), (240, Cmaj), (264, D), (290, G), (316, D), (340, G)],
          [(43, 29, 0.4, 0.2)], 22,
          [(10, 67), (58, 71), (104, 74), (152, 67), (200, 71), (250, 74), (298, 79), (344, 67)],
          motifs=[(30, 'oboe', transpose(major(MOTIF), 5), 0.26, 0.42, 0), (160, 'oboe', transpose(major(MOTIF), 5), 0.26, 0.4, 0),
                  (275, 'flute', transpose(major(MOTIF), 5), 0.26, 0.32, 0)],
          high=[(120, 83, 12), (230, 86, 14)])
    # At sea: F major and D minor, the harp rocking in sixes, the motif on the horn
    under('score-under-voyage.mp3',
          [(0, F), (26, Dm), (52, Bb), (78, C), (104, F), (130, Dm), (156, Gm), (180, C), (206, F), (232, Bb), (256, Dm), (282, C), (306, F), (334, Dm)],
          [(41, 31, 0.0, 0.22), (36, 47, 1.3, 0.14)], 23, [],
          motifs=[(24, 'horn', MOTIF, 0.3, 0.42, -12), (150, 'horn', transpose(TB[:6], 0), 0.3, 0.38, -12), (262, 'horn', MOTIF, 0.3, 0.42, -12)],
          lilt=0.3)
    # The island: E minor, strange and open; long silences; the motif high on the flute, far off
    under('score-under-island.mp3',
          [(0, E_m), (32, Cmaj), (62, Esus), (92, Am), (122, E_m), (152, Cm7), (182, B7), (212, E_m), (244, Cmaj), (274, Am), (304, B7), (334, E_m)],
          [(40, 41, 0.6, 0.26), (47, 29, 2.2, 0.12)], 24,
          [(20, 76), (88, 71), (160, 79), (236, 76), (312, 71)],
          motifs=[(54, 'flute', transpose(MOTIF, 2), 0.4, 0.3, 0), (200, 'flute', transpose(MOTIF, 2), 0.4, 0.28, 0), (318, 'flute', transpose(MOTIF, 2), 0.44, 0.25, 0)],
          high=[(130, 88, 16), (260, 83, 14)])
    # The stockade and the camp: A minor, a slow low pizzicato heartbeat, never settling
    under('score-under-stockade.mp3',
          [(0, Am), (26, Fs), (50, Em), (74, Am), (98, [41, 57, 60, 65]), (122, Esus), (146, Am), (170, Dm), (194, Em), (218, Am), (242, [41, 57, 60, 65]), (266, Esus), (290, Am), (314, Dm), (338, Am)],
          [(33, 27, 0.0, 0.24), (40, 43, 2.0, 0.14)], 25,
          [(44, 69), (140, 72), (236, 69), (330, 76)],
          motifs=[(100, 'vc_sus', transpose(MOTIF, -5), 0.36, 0.42, -24), (250, 'horn', transpose(MOTIF, -5), 0.36, 0.3, -12)],
          pulse=(2.6, 45))
    # The hunt: D minor wandering, the clarinet carries the motif through the trees
    under('score-under-hunt.mp3',
          [(0, Dm), (24, Gm), (48, Asus), (72, Bb), (96, Dm), (120, [43, 58, 62, 65]), (144, A7), (168, Dm), (192, F), (216, Gm), (240, C), (264, A7), (290, Dm), (316, Asus), (340, Dm)],
          [(38, 31, 0.3, 0.24)], 26,
          [(12, 69), (84, 74), (156, 65), (228, 69), (300, 74)],
          motifs=[(30, 'clar', MOTIF, 0.32, 0.42, -12), (130, 'clar', TA2[:9], 0.32, 0.4, -12), (232, 'clar', MOTIF, 0.32, 0.42, -12), (320, 'horn', MOTIF, 0.34, 0.32, -12)])
    # And last: D major, home; the theme in major on the horn, then the flute
    under('score-under-home.mp3',
          [(0, Dmaj), (26, Bm), (50, G), (76, A_), (100, Dmaj), (126, G), (150, Em), (176, A_), (200, Dmaj), (226, Bm), (250, G), (276, A_), (300, Dmaj), (330, Dmaj)],
          [(38, 37, 0.0, 0.22)], 27,
          [(14, 66), (70, 74), (130, 69), (190, 78), (250, 74), (318, 66)],
          motifs=[(30, 'horn', major(TA), 0.28, 0.42, -12), (160, 'flute', major(TA2), 0.28, 0.32, 0), (282, 'horn', major(MOTIF), 0.32, 0.36, -12)],
          high=[(106, 81, 14), (226, 86, 12)])

if __name__ == '__main__':
    build_all()
