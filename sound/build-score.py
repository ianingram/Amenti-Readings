#!/usr/bin/env python3
"""Julius Caesar — THE SCORE (7 Oct 2026). A modern score that tells the story, one sound world per
kind of scene (Ian's direction for the Roman productions: no reconstruction of period music).

  caesar      the Colossus — the procession at the Lupercal, Caesar in his power. C minor, 66 BPM, 4/4:
              low brass and tuba in slow chords (i–VI–III–VII), horns climbing a fourth-and-fifth
              fanfare, trumpets answering, timpani and bass drum on the strong beats. The second half
              climbs a tone, brighter and more dangerous.
  conspiracy  the storm night and the orchard, men meeting with their faces hidden. D minor, 100 BPM:
              a whispering viola spiccato ostinato, cello pizzicato pulse, a chromatic line sinking in
              the cellos; violin tremolo and a timpani heartbeat creep in for the second half.
  brutus      the noble Roman, his conscience — the quiet heart. E minor, 56 BPM: a string chorale,
              a cello melody, answered an octave up by the violins with the cello beneath.
  forum       the Forum: the crowd, the speeches, Antony turning the mob. G minor, 84 BPM: a driving
              cello spiccato, timpani rolls building, low brass swelling and the horns taking the tune.
  ghost       Caesar's spirit in Brutus's tent: no pulse — high violin tremolo in a close cluster, low
              cello tremolo, a muted brass breath.
  philippi    the battle: A minor, 120 BPM — snare and bass drum in a march, driving low strings,
              trumpet calls, brass stabs.
  overture    the landing page: the whole story in order, each world crossfading into the next.

Instruments VSCO 2 CE (CC0), every bank pitch-calibrated (jc_kit). Seed 44 (BC)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jc_kit import *
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out') + '/'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(44)

TBN = bank('Brass/Tenor Trombone/sus/*_v2_1.wav', r'sus_([A-G]#?\d)_')
HORN = bank('Brass/F Horn/sus/*_v2_1.wav', r'sus_([A-G]#?\d)_')
TPT = bank('Brass/Trumpet/sus/*_v3_rr1.wav', r'sus_([A-G]#?\d)_')
TPTST = bank('Brass/Trumpet/stac/*_v3_rr1.wav', r'stac_([A-G]#?\d)_')
TBNST = bank('Brass/Tenor Trombone/stac/*_v4_rr1.wav', r'stac_([A-G]#?\d)_')
MHORN = bank('Brass/F Horn/mute/*_v2_1.wav', r'mute_([A-G]#?\d)_')
TUBA = bank('Brass/Tuba/sus/*_v2_rr1_Mid.wav', r'sus_([A-G]#?\d)_')
CEL = bank('Strings/Cello Section/susvib/*_v1_1.wav', r'susvib_([A-G]#?\d)_')
VLA = bank('Strings/Viola Section/susvib/*_v1_1.wav', r'susvib_([A-G]#?\d)_')
VLN = bank('Strings/Violin Section/susVib/*_v1.wav', r'susVib_([A-G]#?\d)')
CSPIC = bank('Strings/Cello Section/spic/*_v2_RR1.wav', r'spic_([A-G]#?\d)_')
VLASPIC = bank('Strings/Viola Section/spic/*_v1_rr1.wav', r'spic_([A-G]#?\d)_')
CTREM = bank('Strings/Cello Section/trem/*_v1_1.wav', r'trem_([A-G]#?\d)_')
VTREM = bank('Strings/Violin Section/Trem/*_v1.wav', r'Trem_([A-G]#?\d)')
CPIZ = bank('Strings/Cello Section/pizzT/*_v2_RR1.wav', r'pizzT_([A-G]#?\d)_')
P = V + 'Percussion/'
TIMP = [load16(P + f'Timpani/Timpani{i}_Hit_v3_rr1_Sum.wav') for i in (1, 2, 3)]
TIMPR = load16(P + 'Timpani/Rolls/Timpani1_Roll_v5_rr1_Sum.wav')
BD = load16(P + 'BDrumNewhit_v5_rr1_Sum.wav')
SN = [load16(V + f'VSCO 1 Percussion/drums/snare/drum1/snare1_{d}.wav') for d in ('f_1', 'mp_1', 'f_2')]
CRASH = load16(P + 'cymbal-crash1_ff_rr1.wav')
files = {}

def render(name, mix, xf, db=-24):
    write_mp3(rms_db(fold(mix, xf), db), OUT + name)
    files[name] = round(len(fold(mix, xf)) / SR, 1)

def chord(buf, b, notes, t, d, g, head=0.3, kx=0.3, tail=0.6):
    for m in notes: put(buf, sustain(b, m, d, head=head, kx=kx, tail=tail), t, g)

# ═══ CAESAR — the Colossus ═══════════════════════════════════════════════════════════════════════
BT = 60 / 66; BAR = 4 * BT; bars = 16; N = int((bars * BAR + 5) * SR)
low, horns, tpts, perc = (np.zeros(N, np.float32) for _ in range(4))
#             root  chord (the first half in C minor; the second a tone higher, in D minor's shadow)
H1 = [(36, [48, 55, 60, 63]), (32, [44, 51, 56, 60]), (39, [51, 55, 58, 63]), (34, [46, 50, 53, 58])]
H2 = [(38, [50, 57, 62, 65]), (34, [46, 53, 58, 62]), (41, [53, 57, 60, 65]), (43, [55, 59, 62, 67])]
PROG = H1 * 2 + H2 * 2
for b, (root, tri) in enumerate(PROG):
    t0 = b * BAR
    put(low, sustain(TUBA, root, BAR + 0.4, head=0.3, kx=0.4, tail=0.5), t0, 0.9)
    chord(low, TBN, tri[:3], t0, BAR + 0.3, 0.42)
    put(perc, TIMP[b % 2], t0, 1.0); put(perc, TIMP[2], t0 + 2 * BT, 0.55)
    put(perc, lp(BD, 300), t0, 0.7)
    if b % 4 == 3:                                                           # a snare ruff into the next phrase
        for k in range(4): put(perc, SN[1] * (0.25 + 0.12 * k), t0 + 3 * BT + k * BT / 4)
FAN = [(0, 0, 1.5), (1.5, 7, 0.5), (2, 12, 2)]                               # the horns: root, fifth, octave
for b in (0, 2, 4, 6, 8, 10, 12, 14):
    root = PROG[b][0] + 24 + (12 if PROG[b][0] < 36 else 0)
    for st, iv, d in FAN:
        put(horns, sustain(HORN, root + iv, d * BT + 0.25, head=0.12, kx=0.15, tail=0.3), b * BAR + st * BT, 0.55)
for b in (5, 7, 13, 15):                                                     # the trumpets answer
    root = PROG[b][0] + 36 + (12 if PROG[b][0] < 36 else 0)
    for st, iv, d in [(0, 7, 1), (1, 12, 1), (2, 14, 1), (3, 15, 1.4)]:
        put(tpts, sustain(TPT, root + iv - 12, d * BT + 0.2, head=0.1, kx=0.1, tail=0.25), b * BAR + st * BT, 0.5)
put(perc, CRASH * 0.5, 8 * BAR)
mix = stems((reverb(low, 2.6, 0.3, seed=1), -24), (reverb(horns, 2.8, 0.35, seed=2), -27), (reverb(tpts, 2.8, 0.35, seed=3), -29),
            (reverb(perc, 2.2, 0.3, seed=4), -27))
render('score-caesar.mp3', mix[: int((bars * BAR + 3) * SR)], 3.0)

# ═══ CONSPIRACY — the storm night, the orchard ══════════════════════════════════════════════════
BT = 60 / 100; BAR = 4 * BT; bars = 16; N = int((bars * BAR + 5) * SR)
ost, puls, sink, high, heart = (np.zeros(N, np.float32) for _ in range(5))
CH = [62, 62, 65, 62, 64, 62, 60, 62]                                         # the whisper: D D F D E D C D
ROOTS = [38, 38, 34, 34, 38, 38, 33, 33] * 2
for b in range(bars):
    t0 = b * BAR; shift = 0 if b < 8 else 0
    for k, m in enumerate(CH):
        m2 = m + (ROOTS[b] - 38 if ROOTS[b] != 33 else -1)
        put(ost, pluck(VLASPIC, m2, 0.55 if k % 2 else 0.75), t0 + k * BT / 2 + rng.uniform(-0.006, 0.006))
    for k in range(4): put(puls, pluck(CPIZ, ROOTS[b], 0.8 if k == 0 else 0.45), t0 + k * BT)
SINK = [50, 49, 48, 47, 46, 45, 44, 45]                                       # a chromatic line, sinking
for i, m in enumerate(SINK * 2):
    put(sink, sustain(CEL, m, 2 * BAR + 0.4, head=0.5, kx=0.4, tail=0.8), i * BAR * 1.0, 0.35 if i < 8 else 0.45)
for b in range(8, bars):                                                      # second half: tremolo above, a heartbeat below
    put(high, sustain(VTREM, 74 + (1 if b % 4 == 3 else 0), BAR + 0.3, head=0.2, kx=0.3, tail=0.4), b * BAR, 0.3)
    for t_ in (0, 0.28): put(heart, lp(TIMP[2], 400), b * BAR + t_, 0.7 if t_ == 0 else 0.45)
mix = stems((reverb(ost, 1.6, 0.25, seed=5), -26), (reverb(puls, 1.4, 0.2, seed=6), -30), (reverb(sink, 2.4, 0.3, seed=7), -30),
            (reverb(high, 2.6, 0.35, seed=8), -35), (reverb(heart, 1.8, 0.25, seed=9), -31))
render('score-conspiracy.mp3', mix[: int((bars * BAR + 2.5) * SR)], 2.5)

# ═══ BRUTUS — the noble Roman ══════════════════════════════════════════════════════════════════
BT = 60 / 56; BAR = 4 * BT; bars = 12; N = int((bars * BAR + 6) * SR)
pad, mel, under = (np.zeros(N, np.float32) for _ in range(3))
BCH = [(40, [52, 55, 59]), (36, [52, 55, 60]), (45, [52, 57, 60]), (47, [51, 54, 59]),
       (40, [52, 55, 59]), (43, [50, 55, 59]), (45, [48, 52, 57]), (47, [51, 54, 59])] + \
      [(40, [52, 55, 59]), (36, [52, 55, 60]), (38, [50, 54, 57]), (40, [52, 55, 59])]
for b, (root, tri) in enumerate(BCH):
    put(under, sustain(CEL, root, BAR + 0.6, head=0.5, kx=0.4, tail=0.9), b * BAR, 0.5)
    chord(pad, VLA, [n for n in tri if n < 60], b * BAR, BAR + 0.6, 0.3, head=0.7, kx=0.5, tail=1.0)
    chord(pad, VLN, [n + 12 for n in tri if n + 12 >= 60], b * BAR, BAR + 0.6, 0.22, head=0.7, kx=0.5, tail=1.0)
TUNE = [(0, 64, 3), (3, 66, 1), (4, 67, 2), (6, 66, 1), (7, 64, 1), (8, 69, 3), (11, 67, 1), (12, 66, 4),
        (16, 64, 3), (19, 62, 1), (20, 67, 2), (22, 69, 1), (23, 71, 1), (24, 72, 3), (27, 71, 1), (28, 66, 4)]
for st, m, d in TUNE:                                                         # the cello sings the tune
    put(mel, sustain(CEL, m - 12, d * BT * 1.03 + 0.3, head=0.35, kx=0.3, tail=0.6), st * BT, 0.62)
for st, m, d in TUNE[:12]:                                                    # then the violins, an octave up
    put(mel, sustain(VLN, m + 12, d * BT * 1.03 + 0.3, head=0.35, kx=0.3, tail=0.6), (32 + st) * BT, 0.42)
mix = stems((reverb(pad, 3.2, 0.38, seed=10), -30), (reverb(mel, 3.0, 0.34, seed=11), -26), (reverb(under, 3.0, 0.3, seed=12), -30))
render('score-brutus.mp3', mix[: int((bars * BAR + 4) * SR)], 3.5, -26)

# ═══ FORUM — the crowd, the speeches, Antony turning the mob ══════════════════════════════════════
BT = 60 / 84; BAR = 4 * BT; bars = 16; N = int((bars * BAR + 6) * SR)
drive, brass, horns, timp = (np.zeros(N, np.float32) for _ in range(4))
FCH = [(43, [55, 58, 62]), (39, [55, 58, 63]), (41, [53, 57, 60]), (38, [50, 54, 57])] * 2 + \
      [(43, [55, 58, 62]), (36, [55, 60, 63]), (39, [51, 55, 58]), (38, [50, 54, 57])] * 2
for b, (root, tri) in enumerate(FCH):
    t0 = b * BAR; lift = min(1.0, 0.45 + b / 16)
    for k in range(8): put(drive, pluck(CSPIC, root + (12 if k % 2 else 0), lift * (0.8 if k % 2 == 0 else 0.55)), t0 + k * BT / 2)
    chord(brass, TBN, tri, t0, BAR + 0.4, 0.22 + 0.22 * b / 16, head=0.5, kx=0.4, tail=0.7)
    put(brass, sustain(TUBA, root - 12 if root > 40 else root, BAR + 0.4, head=0.4, kx=0.4, tail=0.6), t0, 0.5 + 0.4 * b / 16)
    put(timp, TIMP[b % 3], t0, 0.6 + 0.4 * b / 16)
    if b in (7, 15): put(timp, TIMPR[: int(BAR * SR)], t0, 0.8)
FTUNE = [(0, 67, 2), (2, 70, 1), (3, 69, 1), (4, 67, 2), (6, 62, 2), (8, 63, 3), (11, 65, 1), (12, 62, 4),
         (16, 67, 2), (18, 70, 1), (19, 72, 1), (20, 74, 3), (23, 72, 1), (24, 70, 2), (26, 69, 2), (28, 67, 4)]
for rep in range(2):
    for st, m, d in FTUNE:
        put(horns, sustain(HORN, m - 12, d * BT * 1.02 + 0.25, head=0.15, kx=0.2, tail=0.35), (rep * 32 + st) * BT, 0.45 + 0.2 * rep)
put(timp, CRASH * 0.45, 8 * BAR)
mix = stems((reverb(drive, 1.8, 0.24, seed=13), -26), (reverb(brass, 2.6, 0.32, seed=14), -27), (reverb(horns, 2.8, 0.35, seed=15), -27),
            (reverb(timp, 2.4, 0.3, seed=16), -28))
render('score-forum.mp3', mix[: int((bars * BAR + 3) * SR)], 3.0)

# ═══ GHOST — Caesar's spirit in the tent ══════════════════════════════════════════════════════════
L = 36.0; N = int((L + 6) * SR)
hi, lo_, breath = (np.zeros(N, np.float32) for _ in range(3))
for k, m in enumerate((83, 84, 78)):                                          # a close, cold cluster high up
    put(hi, sustain(VTREM, m, L, head=0.4, kx=0.6, tail=3), 0.4 * k, 0.28)
put(lo_, sustain(CTREM, 40, L, head=0.4, kx=0.6, tail=3), 0, 0.5)
for t_ in (6, 18, 29):
    put(breath, sustain(MHORN, 52, 4.5, head=0.4, kx=0.4, tail=1.6), t_, 0.5)
    put(breath, sustain(MHORN, 53, 4.0, head=0.4, kx=0.4, tail=1.6), t_ + 0.6, 0.35)
sw = (0.65 + 0.35 * np.sin(2 * np.pi * np.arange(N) / SR / 9.0)).astype(np.float32)   # slow swells
mix = stems((reverb(hi * sw, 4.5, 0.5, seed=17), -31), (reverb(lo_, 4.0, 0.4, seed=18), -31), (reverb(breath, 4.5, 0.5, seed=19), -33))
render('score-ghost.mp3', mix[: int((L + 3) * SR)], 3.0, -27)

# ═══ PHILIPPI — the battle ═══════════════════════════════════════════════════════════════════════
BT = 60 / 120; BAR = 4 * BT; bars = 16; N = int((bars * BAR + 5) * SR)
drums, strings, calls, stabs = (np.zeros(N, np.float32) for _ in range(4))
PCH = [45, 45, 41, 43, 45, 45, 41, 40] * 2
for b in range(bars):
    t0 = b * BAR
    for k, (st, s, g) in enumerate([(0, 0, 0.9), (1, 2, 0.5), (1.5, 2, 0.4), (2, 0, 0.8), (3, 2, 0.5), (3.25, 1, 0.35), (3.5, 2, 0.5), (3.75, 1, 0.4)]):
        put(drums, SN[s] * g, t0 + st * BT)
    put(drums, lp(BD, 260), t0, 0.9); put(drums, lp(BD, 260), t0 + 2 * BT, 0.7)
    for k in range(8): put(strings, pluck(CSPIC, PCH[b] + (7 if k in (3, 7) else 0), 0.8 if k % 2 == 0 else 0.6), t0 + k * BT / 2)
    if b % 2 == 1:
        for st in (2.5, 3):
            for m in (PCH[b] + 12, PCH[b] + 19): put(stabs, pluck(TBNST, m, 0.6), t0 + st * BT)
CALL = [(0, 69, 0.5), (0.5, 69, 0.5), (1, 76, 1), (2, 72, 0.5), (2.5, 74, 0.5), (3, 76, 2)]
for b in (2, 6, 10, 14):
    for st, m, d in CALL: put(calls, sustain(TPT, m, d * BT + 0.15, head=0.08, kx=0.08, tail=0.2), b * BAR + st * BT, 0.55)
put(stabs, CRASH * 0.5, 8 * BAR)
mix = stems((reverb(drums, 1.6, 0.22, seed=20), -26), (reverb(strings, 1.6, 0.22, seed=21), -27), (reverb(calls, 2.6, 0.35, seed=22), -28),
            (reverb(stabs, 2.0, 0.28, seed=23), -30))
render('score-philippi.mp3', mix[: int((bars * BAR + 2.5) * SR)], 2.5, -23)

# ═══ OVERTURE — the story in order, for the landing page ═══════════════════════════════════════════
def mp3(path):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                                        capture_output=True).stdout, np.float32).copy()
order = ['score-caesar.mp3', 'score-conspiracy.mp3', 'score-forum.mp3', 'score-ghost.mp3', 'score-philippi.mp3', 'score-brutus.mp3']
XF = 4.0; ov = None
for f in order:
    x = at_rms(mp3(OUT + f), -24)
    if ov is None: ov = x; continue
    n = int(XF * SR); fx = np.linspace(0, 1, n, dtype=np.float32)
    ov[-n:] = ov[-n:] * (1 - fx) + x[:n] * fx; ov = np.concatenate([ov, x[n:]])
n = int(3 * SR); ov[:n] *= np.linspace(0, 1, n); m = int(9 * SR); ov[-m:] *= np.linspace(1, 0, m)
write_mp3(rms_db(ov, -23), OUT + 'overture.mp3'); files['overture.mp3'] = round(len(ov) / SR, 1)
for k, v in files.items(): print(f'{k:24s} {v:6.1f} s')
