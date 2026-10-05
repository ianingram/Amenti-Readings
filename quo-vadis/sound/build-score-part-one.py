#!/usr/bin/env python3
"""Quo Vadis — THE SCORE, Part One. Not a reconstruction of ancient music: a modern
score that tells the story, a different sound world for each kind of scene.

  opulence   the baths, Petronius's house, the luxury of the court — eastern and sensual:
             a drone on D, an ornamented reed (oboe) in the Phrygian-dominant scale
             (D Eb F# G A Bb C), an oud-like pluck, a frame drum in a slow 6/8 sway
  lygia      the girl herself — spare and modern: upright piano in slow open arpeggios,
             a high string halo, A minor turning to C
  vinicius   his passion — cinematic: a driving string ostinato in D minor, the cellos
             carrying a long rising line, timpani breathing underneath
  court      Nero, Poppæa, the power of the Palatine — heavy and unsettling: low brass in
             dark clusters, a bassoon that slides, pizzicato like dripping, a slow 4/4 tread
  faith      the Christians — warm and still: a string chorale in D major, soft piano bells,
             the only open, consonant music in the book

Later parts add the arena (martial: brass, snares, timpani) and the fire (modern, 4/4,
a relentless pulse). Instruments VSCO 2 CE (CC0). Seed 64."""
import os, re, glob, json
exec(open('/tmp/rj/rj_assets.py').read().split('# ═══ THE FEAST')[0].replace("/tmp/rj/sound/", "/tmp/qv/score/"))
os.makedirs('/tmp/qv/score', exist_ok=True)
rng = np.random.default_rng(64)
V2 = '/tmp/vsco2tree/'; V1 = '/tmp/vsco/'
OBOE = bank(V2 + 'Woodwinds/Oboe/Sus/*_v1_Main.wav', r'Sus_([A-G]#?\d)_')
BSN = bank(V2 + 'Woodwinds/Bassoon/sus/*_v1_1.wav', r'PSBassoon_([A-G]#?\d)_')
HORN = bank(V2 + 'Brass/F Horn/sus/*_v1_1.wav', r'sus_([A-G]#?\d)_')
TBN = bank(V2 + 'Brass/Tenor Trombone/sus/*_v1_1.wav', r'sus_([A-G]#?\d)_')
CTREM = bank(V2 + 'Strings/Cello Section/trem/*_v1_1.wav', r'trem_([A-G]#?\d)_')
VLN = bank(V2 + 'Strings/Violin Section/susVib/*_v1.wav', r'susVib_([A-G]#?\d)_')
VLA = bank(V2 + 'Strings/Viola Section/susvib/*_v1_1.wav', r'susvib_([A-G]#?\d)_')
CEL = bank(V1 + 'Strings/Cello Section/susvib/*_v1_1.wav', r'susvib_([A-G]#?\d)_')
TIMPR = lambda d: V1 + f'Percussion/Timpani/Rolls/Timpani{d}_Roll_v3_rr1_Sum.wav'
DRUM = load16(V1 + 'VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f_1.wav')
DRUM_H = load16(V1 + 'VSCO 1 Percussion/drums/tenor/tenor_higher/tenorH_f_1.wav')
def pno(m, g=1.0):
    try: return piano(m, 2, 3.0) * g
    except Exception: return pluck(VPIZZ, m, g)
def at_rms(x, db):
    r = np.sqrt(np.mean(x ** 2)) + 1e-12; return x * (10 ** (db / 20) / r)
def stems(*pairs):                                    # each stem levelled on its own, then summed
    n = max(len(x) for x, _ in pairs); out = np.zeros(n, np.float32)
    for x, db in pairs: out[:len(x)] += at_rms(x, db)
    return out
def render(name, mix, xf=3.0, db=-25): write_mp3(rms_db(fold(mix, xf), db), name)

# ═══ OPULENCE — eastern, sensual: drone, ornamented reed, oud, frame drum in 6/8 ═══════════
BT = 60 / 66 / 2; BAR = 6 * BT; bars = 12; L = bars * BAR + 4; N = int(L * SR)       # 6/8, slow sway
drone, reed, oud, drum = (np.zeros(N, np.float32) for _ in range(4))
put(drone, sustain(CEL, 38, L - 1, head=0.4, kx=0.5, tail=2), 0); put(drone, sustain(VLA, 45, L - 1, head=0.4, kx=0.5, tail=2), 0.3, 0.7)
SC = [62, 63, 66, 67, 69, 70, 72, 74]                                                  # D Eb F# G A Bb C D
PHR = [(0, 69, 2), (2, 70, 1), (3, 69, 1), (4, 66, 2), (6, 67, 3), (9, 66, 1), (10, 63, 1), (11, 62, 5),
       (18, 66, 2), (20, 67, 1), (21, 69, 2), (23, 70, 1), (24, 72, 3), (27, 70, 1), (28, 69, 2), (30, 67, 1), (31, 66, 1), (32, 63, 2), (34, 62, 6)]
for rep in range(2):
    for st, m, d in PHR:
        t0 = rep * 6 * BAR + st * BT
        put(reed, sustain(OBOE, m, d * BT * 1.05 + 0.15, head=0.15, kx=0.1, tail=0.2), t0, 0.5)
        if d >= 2 and rng.random() < 0.6:                                               # the ornament: a quick turn into the long notes
            for k, o in enumerate((1, 0, -1)):
                nm = SC[max(0, min(7, SC.index(m) + o))] if m in SC else m
                put(reed, sustain(OBOE, nm, 0.09, head=0.05, kx=0.02, tail=0.03), t0 - 0.27 + k * 0.09, 0.25)
for b in range(bars):
    t0 = b * BAR
    for k, (st, m) in enumerate(((0, 50), (2, 57), (3, 62), (5, 57))):                  # the oud: a low pattern, each note plucked twice fast
        put(oud, pluck(VAPZ, m, 0.8), t0 + st * BT); put(oud, pluck(VAPZ, m, 0.35), t0 + st * BT + 0.06)
    for st, g in ((0, 1.0), (2, 0.4), (3, 0.7), (5, 0.45)): put(drum, DRUM if st in (0, 3) else DRUM_H, t0 + st * BT, g)
mix = stems((reverb(drone, 3.0, 0.3, seed=1), -30), (reverb(reed, 2.6, 0.35, seed=2), -26), (reverb(oud, 1.8, 0.25, seed=3), -29), (reverb(drum, 1.6, 0.25, seed=4), -30))
render('score-opulence.mp3', mix[: int((bars * BAR + 2) * SR)])

# ═══ LYGIA — spare and modern: piano in open arpeggios, a high string halo ═══════════════
BT = 60 / 58; BAR = 4 * BT; bars = 8; N = int((bars * BAR + 6) * SR)
pn, halo = np.zeros(N, np.float32), np.zeros(N, np.float32)
LH = [(45, [57, 64, 67, 71]), (41, [53, 60, 65, 69]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])] * 2
for b, (root, up) in enumerate(LH):
    t0 = b * BAR; put(pn, pno(root, 0.7), t0)
    for k, m in enumerate(up + [up[2] + 12, up[3]]): put(pn, pno(m, 0.5 if k % 2 else 0.6), t0 + (k + 1) * BAR / 7)
    put(halo, sustain(VLN, up[3] + 12, BAR + 0.8, head=0.5, kx=0.5, tail=1.0), t0, 0.5)
mix = stems((reverb(pn, 3.2, 0.32, seed=5), -26), (reverb(halo, 3.8, 0.45, seed=6), -33))
render('score-lygia.mp3', mix[: int((bars * BAR + 3) * SR)])

# ═══ VINICIUS — cinematic: a driving string ostinato, the cellos rising, timpani breathing ══
# (16 bars: the second half climbs to F major and back, the cellos an octave higher)
BT = 60 / 92; BAR = 4 * BT; bars = 16; N = int((bars * BAR + 5) * SR)
ost, line, tim = np.zeros(N, np.float32), np.zeros(N, np.float32), np.zeros(N, np.float32)
CH = [(38, [62, 65, 69]), (34, [62, 65, 70]), (36, [60, 64, 67]), (33, [61, 64, 69])] * 2 + \
     [(41, [65, 69, 72]), (36, [64, 67, 72]), (34, [62, 65, 70]), (33, [61, 64, 69])] * 2
TR = load16(TIMPR(2))
for b, (root, tri) in enumerate(CH):
    t0 = b * BAR
    for k in range(8):
        m = [tri[0], tri[1], tri[2], tri[1]][k % 4]
        put(ost, sustain(VLA, m, BT / 2 * 0.9, head=0.05, kx=0.03, tail=0.05), t0 + k * BT / 2, 0.6 if k % 2 else 0.8)
    put(ost, sustain(CTREM, root, BAR, head=0.1, kx=0.2, tail=0.3), t0, 0.5)
    if b % 2 == 1:
        n_ = min(len(TR), int(BAR * SR)); put(tim, TR[:n_] * np.linspace(0.2, 1, n_).astype(np.float32), t0, 0.4)
RISE = [(0, 50, 4), (4, 53, 2), (6, 55, 2), (8, 57, 6), (14, 58, 2), (16, 57, 4), (20, 60, 2), (22, 62, 2), (24, 64, 4), (28, 62, 4),
        (32, 65, 4), (36, 64, 2), (38, 65, 2), (40, 67, 6), (46, 69, 2), (48, 70, 4), (52, 69, 2), (54, 67, 2), (56, 65, 4), (60, 62, 4)]
for st, m, d in RISE: put(line, sustain(CEL, m, d * BT * 1.03 + 0.3, head=0.3, kx=0.3, tail=0.5), st * BT, 0.7)
mix = stems((reverb(ost, 1.8, 0.22, seed=7), -27), (reverb(line, 2.6, 0.3, seed=8), -25), (reverb(tim, 2.2, 0.3, seed=9), -33))
render('score-vinicius.mp3', mix[: int((bars * BAR + 2) * SR)])

# ═══ THE COURT — heavy, unsettling: low brass clusters, a sliding bassoon, dripping pizzicato ═
BT = 60 / 54; BAR = 4 * BT; bars = 8; N = int((bars * BAR + 6) * SR)
br, bs, dr, tread = (np.zeros(N, np.float32) for _ in range(4))
CL = [[38, 39, 45], [37, 38, 44], [36, 39, 46], [37, 41, 44]] * 2                         # D–Eb–A, C#–D–G#: clusters that won't settle
for b, cl in enumerate(CL):
    t0 = b * BAR
    for m in cl: put(br, sustain(TBN if m < 44 else HORN, m, BAR + 0.6, head=0.4, kx=0.4, tail=0.8), t0, 0.5)
    put(tread, DRUM, t0, 0.9); put(tread, DRUM, t0 + 2 * BT, 0.5)
    for k in range(3):                                                                    # pizzicato like something dripping in a marble hall
        put(dr, pluck(VPIZZ, [74, 75, 81, 80][(b + k) % 4], 0.35), t0 + BT * (0.75 + k * 1.15 + 0.2 * rng.random()))
for st, m, d in ((2, 50, 3), (6, 49, 2), (10, 51, 3), (14, 44, 2), (18, 50, 3), (22, 49, 3), (26, 45, 4)):
    put(bs, sustain(BSN, m, d * BT, head=0.2, kx=0.2, tail=0.3), st * BT, 0.6)
mix = stems((reverb(br, 3.4, 0.35, seed=10), -26), (reverb(bs, 2.4, 0.3, seed=11), -30), (reverb(dr, 3.0, 0.45, seed=12), -33), (reverb(tread, 2.4, 0.3, seed=13), -31))
render('score-court.mp3', mix[: int((bars * BAR + 3) * SR)])

# ═══ FAITH — warm and still: a string chorale in D major, soft piano bells ════════════════
BT = 60 / 50; BAR = 4 * BT; bars = 8; N = int((bars * BAR + 6) * SR)
ch, bells = np.zeros(N, np.float32), np.zeros(N, np.float32)
CHOR = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 55, 59, 62], [45, 52, 57, 61], [50, 57, 62, 66], [43, 50, 59, 67], [45, 57, 61, 64], [50, 57, 62, 66]]
for b, chord in enumerate(CHOR):
    t0 = b * BAR
    for m in chord: put(ch, sustain(CEL if m < 55 else (VLA if m < 64 else VLN), m, BAR + 0.9, head=0.5, kx=0.5, tail=1.2), t0, 0.45)
    put(bells, pno(chord[-1] + 12, 0.5), t0 + BT * 0.5); put(bells, pno(chord[-2] + 12, 0.35), t0 + BT * 2.5)
mix = stems((reverb(ch, 4.0, 0.4, seed=14), -26), (reverb(bells, 3.5, 0.4, seed=15), -32))
render('score-faith.mp3', mix[: int((bars * BAR + 3) * SR)])

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:22s} {v_:6.2f}s')
