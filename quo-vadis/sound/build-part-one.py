#!/usr/bin/env python3
"""Quo Vadis — Part One: Rome in the reign of Nero. The rooms of the first ten
chapters — Petronius's baths, the Roman house round its impluvium, Aulus's garden,
the streets of the city, Nero's feast on the Palatine, the palace at night — and the
feast's music on lyre, aulos and frame drum. Recordings from Wikimedia Commons (PD/CC0,
SOURCES.md); instruments VSCO 2 CE (CC0). Deterministic (seed 64 — the year Rome burned)."""
import os, re, glob, json
exec(open('/tmp/rj/rj_assets.py').read().split('# ═══ THE FEAST')[0].replace("/tmp/rj/sound/", "/tmp/qv/sound/"))
os.makedirs('/tmp/qv/sound', exist_ok=True)
rng = np.random.default_rng(64)
Q = '/tmp/qv/src/'; RJ = '/tmp/rj/src/'
L = 64.0; N = int(L * SR)
def tile(x, n=N): return np.tile(x, int(np.ceil(n / len(x))))[:n]
crowd = tile(load(Q + '360703_eguobyte_large-crowd-medium-distance-stereo_m.wav'))
fest = tile(load(Q + 'Festival_concert_people_crowd_m.wav'))
fount = tile(load(RJ + 'La_fontaine_de_la_place.wav'))
bb = load(RJ + 'Turdus_merula_2.wav')
def far(x, cut): return lp(x, cut)

# the Roman house: water falling into the impluvium, the city a murmur beyond the walls
dom = rms_db(lp(fount, 2200), -32) + rms_db(far(crowd, 380), -44)
for t_ in (9.0, 37.0): put(dom, reverb(lp(bb[int(2 * SR): int(8 * SR)], 6000), 2.0, 0.4, seed=int(t_)) * 0.05, t_)
loopfile('domus.mp3', dom, 4.0, -31)
# the baths: water lapping in a marble pool, drops falling, the hall's long echo, voices far off
ba = np.zeros(N, np.float32); t_ = 0.2
while t_ < L - 1:
    n = int((0.3 + 0.3 * rng.random()) * SR); tt = np.arange(n) / SR
    ba[int(t_ * SR): int(t_ * SR) + n] += (lp(rng.standard_normal(n), 700 + 500 * rng.random()) * np.exp(-tt * 9) * (0.1 + 0.1 * rng.random()))[: N - int(t_ * SR)]
    t_ += 0.5 + 0.8 * rng.random()
t_ = 0.4
while t_ < L - 1:
    q = int(0.06 * SR); tq = np.arange(q) / SR; f = 900 + 1200 * rng.random()
    put(ba, (np.sin(2 * np.pi * f * (1 + 1.4 * tq / tq[-1]) * tq) * np.exp(-tq * 55)).astype(np.float32) * 0.05, t_); t_ += 1.0 + 3 * rng.random()
ba = reverb(ba, 3.2, 0.5, seed=5) + rms_db(far(crowd, 600), -46)
loopfile('baths.mp3', ba, 4.0, -31)
# Aulus's garden: the fountain, the blackbird, cicadas in the cypresses
t = np.arange(N) / SR; cic = np.zeros(N, np.float32)
for k, (f0, rate) in enumerate(((4300, 31), (5200, 44))):
    cic += bp(rng.standard_normal(N).astype(np.float32), f0 * 0.85, f0 * 1.15) * ((0.5 + 0.5 * np.sin(2 * np.pi * rate * t)) ** 3) * (0.55 + 0.45 * np.sin(2 * np.pi * t / (19 + 5 * k) + k))
ga = rms_db(fount, -33) + rms_db(cic, -42)
for t_ in (4.0, 22.0, 41.0, 55.0): put(ga, reverb(lp(bb[int(10 * SR): int(18 * SR)], 7000), 1.6, 0.3, seed=int(t_)) * 0.09, t_)
loopfile('garden.mp3', ga, 4.0, -30)
# the streets of Rome: a thousand voices at a distance, blurred out of any language we know
st = rms_db(lp(crowd, 2400), -28) + rms_db(lp(fest, 1600), -36)
loopfile('rome-street.mp3', st, 4.0, -28)
# the palace at night: marble quiet, the fountain far, the feast still going somewhere in the house
pn = rms_db(lp(fount, 1100), -42) + rms_db(far(fest, 450), -44)
loopfile('palace-night.mp3', pn, 4.0, -34)

# ═══ NERO'S FEAST — lyre, aulos and frame drum in D phrygian over the banquet's roar ═══
BPM = 96; BT = 60 / BPM; BAR = 4 * BT; bars = 16
fe = np.zeros(int((bars * BAR + 5) * SR), np.float32)
CH = [(50, [62, 65, 69]), (51, [63, 67, 70]), (50, [62, 65, 69]), (48, [60, 63, 67])] * 4      # D, Eb, D, C — the Phrygian lean
MEL = [74, 75, 77, 75, 74, 72, 74, 74, 77, 79, 77, 75, 74, 75, 74, 72, 70, 72, 74, 75, 77, 75, 74, 74]
DRUM = '/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f_1.wav'
TAB = load16(DRUM) * 0.5 if os.path.exists(DRUM) else None
for b in range(bars):
    root, tri = CH[b]; t0 = b * BAR
    put(fe, pluck(VAPZ, root - 12, 0.8), t0)
    for k, m in enumerate([tri[0], tri[2], tri[1], tri[2], tri[0] + 12, tri[2], tri[1], tri[2]]):       # the lyre, arpeggiated
        put(fe, pluck(VPIZZ, m, 0.45 if k % 2 else 0.6), t0 + k * BT / 2)
    for k in range(2):                                                                                  # the aulos, reedy and plain
        m = MEL[(2 * b + k) % len(MEL)]
        put(fe, sustain(FLNV, m, 2 * BT * 1.02, head=0.1, kx=0.1, tail=0.15), t0 + k * 2 * BT, 0.42)
    if TAB is not None:
        for t_, g in ((0, 0.8), (1.5 * BT, 0.4), (2 * BT, 0.6), (3 * BT, 0.4), (3.5 * BT, 0.3)): put(fe, TAB, t0 + t_, g)
fe = reverb(fe[: int(bars * BAR * SR + 2 * SR)], 2.4, 0.3, seed=11)
music = rms_db(fold(fe, 2.0), -30)
roar = rms_db(lp(tile(fest, len(music)), 3000), -31) + rms_db(lp(tile(crowd, len(music)), 1800), -38)
write_mp3(rms_db(fold(music + roar[: len(music)], 0.5), -26), 'feast.mp3')

# applause for the Divine Voice, and the cry of Rome
ap = load(Q + 'Applause_i_m.wav'); write_mp3(peak_db(reverb(ap, 2.0, 0.3), -8), 'applause.mp3')
hu = load(Q + 'Hurray_m.wav'); write_mp3(peak_db(reverb(hu, 1.6, 0.3), -9), 'cheer.mp3')
json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:20s} {v_:6.2f}s')
