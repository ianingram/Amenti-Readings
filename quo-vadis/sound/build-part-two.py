#!/usr/bin/env python3
"""Quo Vadis — Part Two. New rooms: Rome by night, the mill by the Tiber, the Ostrianum
under the stars; and a new theme for Chilo Chilonides — the sly Greek: bassoon and
pizzicato on tiptoe, a clarinet-dry oboe that sidles, never quite settling in a key.
Built from the Part One sources and VSCO 2 CE (CC0). Seed 64."""
import os, json
exec(open('/tmp/qv/prod/qv_score.py').read().split('# ═══ OPULENCE')[0].replace("/tmp/qv/score/", "/tmp/qv/score2/"))
os.makedirs('/tmp/qv/score2', exist_ok=True)
Q = '/tmp/qv/src/'; RJ = '/tmp/rj/src/'
L = 64.0; N = int(L * SR)
def tile(x, n=N): return np.tile(x, int(np.ceil(n / len(x))))[:n]
crowd = tile(load(Q + '360703_eguobyte_large-crowd-medium-distance-stereo_m.wav')); fest = tile(load(Q + 'Festival_concert_people_crowd_m.wav'))
fount = tile(load(RJ + 'La_fontaine_de_la_place.wav')); nig = load(RJ + 'Common_Nightingales_song_2.wav')
t = np.arange(N) / SR
cr = np.zeros(N, np.float32)
for k, (f0, rate) in enumerate(((4600, 2.3), (5100, 1.7), (4300, 2.9))):
    chirp = (np.sin(2 * np.pi * 34 * t) > 0.2) * (np.sin(2 * np.pi * rate * t + k) > 0.55)
    cr += bp(rng.standard_normal(N).astype(np.float32), f0 * 0.92, f0 * 1.08) * chirp.astype(np.float32) * (0.5 + 0.2 * k)
wind = tile(load('/tmp/snd/src3/Howling_wind.wav'))
# Rome by night: the city asleep, a far murmur in the Subura, a dog, the wind along the streets
rn = rms_db(lp(crowd, 300), -46) + rms_db(lp(wind, 900), -42) + rms_db(cr, -48)
loopfile('rome-night.mp3', rn, 4.0, -33)
# the mill by the Tiber at night: the river running, the millstones grinding through a wall
river = lp(rng.standard_normal(N).astype(np.float32), 900) + 0.3 * bp(rng.standard_normal(N).astype(np.float32), 1500, 4000)
grind = lp(rng.standard_normal(N).astype(np.float32), 160) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)) * (0.7 + 0.3 * np.sin(2 * np.pi * 4.3 * t))
mi = rms_db(reverb(river, 1.5, 0.2, seed=3), -34) + rms_db(grind.astype(np.float32), -38) + rms_db(cr, -46)
loopfile('mill-night.mp3', mi, 4.0, -31)
# the Ostrianum: an open place among tombs and pines at midnight, a hushed multitude, torches, the wind in the pines
torches = np.zeros(N, np.float32); k = 0
while k < N - 2000:
    m = int(rng.integers(200, 900)); torches[k:k + m] += (hp(rng.standard_normal(m).astype(np.float32), 1500) * np.exp(-np.arange(m) / m * 4) * rng.random() ** 2)
    k += int(rng.integers(800, 9000))
os_ = rms_db(lp(fest, 700), -40) + rms_db(lp(wind, 600), -40) + rms_db(cr, -44) + rms_db(torches, -46)
put(os_, reverb(lp(nig[int(30 * SR): int(50 * SR)], 5000), 3, 0.5) * 0.04, 12.0)
loopfile('ostrianum.mp3', os_, 4.0, -31)

# ═══ CHILO — the sly Greek: bassoon and pizzicato on tiptoe, an oboe that sidles ════════════
BT = 60 / 104; BAR = 4 * BT; bars = 16; N2 = int((bars * BAR + 4) * SR)          # 16 bars: the second half a fourth higher, the oboe answering itself
bs, pz, ob = (np.zeros(N2, np.float32) for _ in range(3))
BASS = [43, 0, 46, 0, 44, 0, 41, 0, 43, 0, 49, 0, 48, 0, 46, 0]                    # staccato steps, a chromatic sidle
for b in range(bars):
    t0 = b * BAR
    for k in range(8):
        m = BASS[(b * 2 + k) % 16] + (5 if b >= 8 and BASS[(b * 2 + k) % 16] else 0)
        if m: put(bs, sustain(BSN, m, BT * 0.35, head=0.05, kx=0.03, tail=0.05), t0 + k * BT / 2, 0.8)
        if k % 2 == 1: put(pz, pluck(VPIZZ, [67, 70, 68, 73][(b + k) % 4], 0.5), t0 + k * BT / 2 + 0.03)
SLY = [(2, 74, 1), (3, 73, 1), (4, 74, 2), (8, 77, 1), (9, 76, 1), (10, 73, 1), (11, 70, 1), (12, 69, 3), (18, 74, 1), (19, 75, 1), (20, 77, 2), (24, 80, 1), (25, 79, 1), (26, 77, 1), (27, 74, 1), (28, 73, 4)]
for st, m, d in SLY: put(ob, sustain(OBOE, m, d * BT * 0.8, head=0.08, kx=0.05, tail=0.1), st * BT, 0.45)
for st, m, d in SLY: put(ob, sustain(OBOE, m + 5 if st < 16 else m - 2, d * BT * 0.8, head=0.08, kx=0.05, tail=0.1), 32 * BT + st * BT, 0.42)
mix = stems((reverb(bs, 1.4, 0.2, seed=21), -28), (reverb(pz, 1.6, 0.25, seed=22), -31), (reverb(ob, 2.0, 0.28, seed=23), -29))
render('score-chilo.mp3', mix[: int((bars * BAR + 2) * SR)])
json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:20s} {v_:6.2f}s')
