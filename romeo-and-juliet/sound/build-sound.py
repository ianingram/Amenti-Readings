#!/usr/bin/env python3
"""Romeo and Juliet — Verona. Rooms for every scene; a dance for Capulet's feast on
'lute' (solo violin pizzicato), 'recorder' (flute without vibrato) and tabor; the
lovers' theme on solo violin over a harp of viola pizzicato; the church organ for the
wedding and the dirges; the passing bell for every death. Instruments VSCO 2 CE (CC0;
organ by Simon Dalzell of Ivy Audio); recordings from Wikimedia Commons (SOURCES.md).
Deterministic (seed 1597 — the year the play was first printed)."""
import os, re, glob, json
exec(open('/tmp/ti/ti_assets5.py').read().split('# ── the coracle')[0].replace("/tmp/ti/sound5/", "/tmp/rj/sound/"))
os.makedirs('/tmp/rj/sound', exist_ok=True)
rng = np.random.default_rng(1597)
V2 = '/tmp/vsco2tree/'; S = '/tmp/rj/src/'
def bank(pattern, rx):
    b = {}
    for f in glob.glob(pattern):
        m_ = re.search(rx, os.path.basename(f))
        if m_: b.setdefault(midi_of(m_.group(1)), f)
    return b
VPIZZ = bank(V2 + 'Strings/Solo Violin/Pizz/*_f_RR1.wav', r'Pizz_([A-G]#?\d)_')
VARCO = bank(V2 + 'Strings/Solo Violin/Arco Vib/*_p.wav', r'ArcoVib_([A-G]#?\d)_')
FLNV = bank(V2 + 'Woodwinds/Flute/susNV/*_v1_1.wav', r'susNV_([A-G]#?\d)_')
VAPZ = bank(V2 + 'Strings/Viola Section/pizz/*_v1_rr1.wav', r'pizz_([A-G]#?\d)_')
ORG = {int(re.search(r'_(\d+)_rr1', f).group(1)) - 86: f for f in glob.glob(V2 + 'Keys/Organ/Quiet/NT5_Man3Quiet_*_rr1.wav') if 122 <= int(re.search(r'_(\d+)_rr1', f).group(1)) <= 179}
def pluck(b, m, g=1.0):
    k = min(b, key=lambda q: abs(q - m)); return load16(b[k], m - k) * g
def sustain(b, m, d, head=0.25, kx=0.2, tail=0.4):
    k = min(b, key=lambda q: abs(q - m)); s = load16(b[k], m - k)
    hd = int(head * SR); mid = s[hd: max(hd + int(0.8 * SR), len(s) - int(0.4 * SR))]
    n = int(d * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    k_ = int(kx * SR); step = max(int(0.3 * SR), len(mid) - k_); pos = max(int(0.3 * SR), len(s) - len(mid) // 2 - k_)
    w_ = np.ones(len(mid), np.float32); w_[:k_] = np.linspace(0, 1, k_); w_[-k_:] = np.linspace(1, 0, k_)
    while pos < n: out[pos:pos + len(mid)] += mid * w_; pos += step
    out = out[:n]; r = min(int(tail * SR), n // 3); out[-r:] *= np.linspace(1, 0, r); return out
def loopfile(name, x, xf=3.0, db=-26): write_mp3(rms_db(fold(x, xf), db), name)

# ═══ THE FEAST — a galliard in D dorian, 3/4: lute, recorder, viola bass, tabor ════════
BPM = 104; BT = 60 / BPM; BAR = 3 * BT; bars = 16
fe = np.zeros(int((bars * BAR + 4) * SR), np.float32)
CH = [(50, [62, 65, 69]), (48, [60, 64, 67]), (50, [62, 65, 69]), (45, [57, 61, 64])] * 2 + [(53, [65, 69, 72]), (48, [60, 64, 67]), (46, [58, 62, 65]), (45, [57, 61, 64])] * 2
MEL = [74, 76, 77, 76, 74, 72, 74, 69, 72, 74, 76, 74, 72, 71, 69, 69,
       77, 79, 81, 79, 77, 76, 74, 72, 70, 72, 74, 72, 69, 68, 69, 69]                 # two notes a bar, an original tune
for b in range(bars):
    root, tri = CH[b]; t0 = b * BAR
    put(fe, pluck(VAPZ, root - 12, 0.9), t0)                                           # the bass, on the beat
    for k, m in enumerate([tri[0], tri[1], tri[2], tri[1], tri[0], tri[2]]):              # the lute, broken in quavers
        put(fe, pluck(VPIZZ, m, 0.55 if k % 2 else 0.7), t0 + k * BT / 2 + 0.004 * k)
    for k in range(2):                                                                  # the recorder: long, then short (the galliard's lilt)
        m = MEL[(2 * b + k) % len(MEL)]; d = 2 * BT if k == 0 else BT
        put(fe, sustain(FLNV, m, d * 1.02 + 0.05, head=0.12, kx=0.1, tail=0.12), t0 + (0 if k == 0 else 2 * BT), 0.4)
    TAB = load16('/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_higher/tenorH_f_1.wav') * 0.5 if os.path.exists('/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_higher/tenorH_f_1.wav') else None
    if TAB is not None:
        for t_, g in ((0, 0.6), (BT * 1.5, 0.3), (2 * BT, 0.4)): put(fe, TAB, t0 + t_, g)  # the tabor
fe = reverb(fe[: int(bars * BAR * SR + 2 * SR)], 1.8, 0.25, seed=11)
loopfile('feast.mp3', fe, 2.0, -25)

# ═══ THE LOVERS' THEME — solo violin over a harp of viola pizzicato, F major / D minor ═══
BPM2 = 60; B2 = 60 / BPM2; BAR2 = 4 * B2
LH = [(41, [53, 57, 60]), (38, [50, 53, 57]), (34, [46, 50, 53]), (36, [48, 52, 55]), (41, [53, 57, 60]), (38, [50, 53, 57]), (34, [46, 50, 53]), (36, [48, 52, 58])]
TUNE = [(0, 72, 2), (2, 74, 1), (3, 72, 1), (4, 69, 3), (7, 67, 1), (8, 65, 2), (10, 69, 2), (12, 70, 3), (15, 69, 1),
        (16, 67, 4), (20, 72, 2), (22, 74, 1), (23, 76, 1), (24, 77, 3), (27, 76, 1), (28, 74, 2), (30, 72, 2)]
lv = np.zeros(int((8 * BAR2 + 6) * SR), np.float32)
for b, (root, tri) in enumerate(LH):
    for k, m in enumerate([root, tri[0], tri[1], tri[2], tri[1], tri[0], tri[1], tri[2]]):   # the harp: rolled quavers
        put(lv, pluck(VAPZ, m, 0.45 if k else 0.6), b * BAR2 + k * B2 / 2)
for st, m, d in TUNE:
    put(lv, sustain(VARCO, m, d * B2 * 1.04 + 0.3, head=0.2, kx=0.25, tail=0.5), st * B2, 0.5)
lv = reverb(lv, 2.6, 0.32, seed=12)[: int((8 * BAR2 + 3) * SR)]
loopfile('score-lovers.mp3', lv, 3.0, -27)

# ═══ THE ORGAN — a slow chorale for the wedding, and for the dirges ═══════════════════
og = np.zeros(int(36 * SR), np.float32)
CHORALE = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 53, 57, 60], [48, 55, 60, 64], [50, 57, 62, 65], [43, 55, 58, 62], [45, 52, 57, 61], [50, 57, 62, 65]]
for k, chord in enumerate(CHORALE):
    for m in chord: put(og, sustain(ORG, m, 4.6, head=0.3, kx=0.4, tail=0.9), 0.3 + k * 4.2, 0.22)
og = reverb(og, 4.5, 0.45, seed=13)[: int(34.5 * SR)]
loopfile('score-organ.mp3', og, 3.0, -26)

# ═══ THE ROOMS ═════════════════════════════════════════════════════════════════════════
L = 64.0; N = int(L * SR)
fount = load(S + 'La_fontaine_de_la_place.wav'); fount = np.tile(fount, 2)[:N]
bb1 = load(S + 'Common_blackbird_singing_denoised.wav'); bb2 = load(S + 'Turdus_merula_2.wav')
nig = load(S + 'Common_Nightingales_song_2.wav')
def birds_far(x, t, dist, g):
    return reverb(lp(x / (np.abs(x).max() + 1e-9), 8000 - 4000 * dist), 1.2 + 2 * dist, 0.15 + 0.4 * dist, seed=int(t)) * g
# Verona by day: the fountain in the piazza, a blackbird on a roof, a church bell far off
ve = rms_db(fount, -30)
for t_ in (5.0, 26.0, 47.0): put(ve, birds_far(bb2[int(2 * SR): int(9 * SR)], t_, 0.6, 0.18), t_)
cb = None
for p_ in ('/tmp/snd/out/church-bells.mp3', '/tmp/snd/ch16/church-bells.mp3'):
    if os.path.exists(p_): cb = mp3(p_); break
if cb is not None: put(ve, reverb(lp(cb[: int(12 * SR)], 1500), 3, 0.5) * 0.06, 34.0)
loopfile('verona.mp3', ve, 4.0, -27)
# the garden at night: crickets, the nightingale in the pomegranate tree, the fountain far
t = np.arange(N) / SR; cr = np.zeros(N, np.float32)
for k, (f0, rate) in enumerate(((4600, 2.3), (5100, 1.7), (4300, 2.9))):
    chirp = (np.sin(2 * np.pi * 34 * t) > 0.2) * (np.sin(2 * np.pi * rate * t + k) > 0.55)
    cr += bp(rng.standard_normal(N).astype(np.float32), f0 * 0.92, f0 * 1.08) * chirp.astype(np.float32) * (0.5 + 0.2 * k)
gn = rms_db(cr, -38) + rms_db(lp(fount, 1500), -40)
put(gn, birds_far(nig[int(10 * SR): int(40 * SR)], 3, 0.45, 0.22), 6.0)
loopfile('garden-night.mp3', gn, 4.0, -28)
# dawn: the nightingale giving way, the blackbirds starting — 'it was the lark'
da = rms_db(cr, -44)
put(da, birds_far(nig[int(60 * SR): int(80 * SR)], 4, 0.6, 0.14), 1.0)
for t_ in (12.0, 21.0, 30.0, 41.0, 52.0): put(da, birds_far(bb1, t_, 0.3, 0.25), t_ + rng.random()); put(da, birds_far(bb2[: int(8 * SR)], t_ + 3, 0.5, 0.18), t_ + 4)
loopfile('dawn.mp3', da, 4.0, -27)
# the friar's cell: stone quiet, a blackbird outside the window, a bell far off
ce = rms_db(lp(rng.standard_normal(N), 300).astype(np.float32), -50)
for t_ in (8.0, 33.0, 55.0): put(ce, birds_far(bb2[int(10 * SR): int(18 * SR)], t_, 0.7, 0.15), t_)
if cb is not None: put(ce, reverb(lp(cb[int(3 * SR): int(9 * SR)], 1200), 3, 0.5) * 0.04, 20.0)
loopfile('cell.mp3', ce, 4.0, -32)
# Juliet's chamber: a still room, the fountain far below in the courtyard
ch = rms_db(lp(rng.standard_normal(N), 250).astype(np.float32), -50) + rms_db(lp(fount, 900), -44)
loopfile('chamber.mp3', ch, 4.0, -33)
# the Capulets' monument: a cold vault, water dripping, the night wind at the door
tb = rms_db(lp(rng.standard_normal(N), 140, 2).astype(np.float32), -40)
wind = load('/tmp/snd/src3/Howling_wind.wav'); tb += rms_db(lp(np.tile(wind, 2)[:N], 700), -42)
t_ = 0.5
while t_ < L - 1:
    q = int(0.08 * SR); tq = np.arange(q) / SR; fq = 900 + 900 * rng.random()
    put(tb, reverb((np.sin(2 * np.pi * fq * (1 + 1.5 * tq / tq[-1]) * tq) * np.exp(-tq * 50)).astype(np.float32), 3.5, 0.6, seed=int(t_)) * 0.05, t_)
    t_ += 2.5 + 4 * rng.random()
loopfile('tomb.mp3', tb, 4.0, -30)

# ═══ THE PASSING BELL — one deep stroke for every death ═══════════════════════════════
n = int(9 * SR); tt = np.arange(n) / SR; f0 = 110.0; y = np.zeros(n)
for ratio, a_, d in ((0.5, .6, 0.35), (1.0, 1.0, 0.45), (1.2, .35, 0.8), (1.5, .3, 0.7), (2.0, .5, 0.6), (2.6, .2, 1.1), (3.0, .15, 1.4)):
    y += a_ * np.sin(2 * np.pi * f0 * ratio * tt + rng.random()) * np.exp(-tt * d)
y += 0.2 * hp(rng.standard_normal(n), 2000) * np.exp(-tt * 200)
write_mp3(peak_db(reverb(y.astype(np.float32), 4.0, 0.4, bright=2500), -8), 'passing-bell.mp3')
# a knock at the door
kn = np.zeros(int(1.6 * SR), np.float32); rap = load('/tmp/ti/src/Knocking_on_wood_or_door.wav')[int(4.5 * SR): int(4.75 * SR)]
for k, t_ in enumerate((0.0, 0.32, 0.64)): put(kn, lp(rap, 2500), t_, 1.0)
write_mp3(peak_db(reverb(kn, 1.0, 0.25), -9), 'knock.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:22s} {v_:6.2f}s')
