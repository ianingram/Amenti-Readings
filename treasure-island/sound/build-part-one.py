#!/usr/bin/env python3
"""Treasure Island — Part One: the Admiral Benbow. Recordings from Wikimedia Commons
(public domain or CC0, listed in SOURCES.md); the sea, the blades and the flintlock
pan built here. Every gun comes twice: NEAR (sharp, dry, loud) and FAR (muffled,
late, long echo). Deterministic (seed 1883)."""
import os, json
src = open('/tmp/snd/ch16_assets.py').read().split('# ── the instruments')[0]
src = src.replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/ti/sound/'")
exec(src)
S = '/tmp/ti/src/'
rng = np.random.default_rng(1883)
def seg(f, a, b): return load(S + f)[int(a * SR): int(b * SR)].copy()
def place(L, items):
    out = np.zeros(int(L * SR), np.float32)
    for t, x, g in items: put(out, x, t, g)
    return out
def metal_hit(base=2000, decay=18, n=6, dur=0.6, seed=0):
    r = np.random.default_rng(seed); N = int(dur * SR); t = np.arange(N) / SR; y = np.zeros(N)
    for m in range(n):
        f = base * (1 + m * 0.71 + r.random() * 0.4)
        y += np.sin(2 * np.pi * f * t + r.random() * 6) * np.exp(-t * decay * (1 + m * 0.35)) / (1 + m)
    return (y * np.minimum(1, t / 0.0015)).astype(np.float32)
def noise(d, lo, hi, seed=0): return bp(np.random.default_rng(seed).standard_normal(int(d * SR)).astype(np.float32), lo, hi)
def far(x, cut=900, rt=3.2, wet=0.55, delay=0.25):
    y = reverb(np.concatenate([np.zeros(int(delay * SR), np.float32), lp(x, cut, 2), np.zeros(int(rt * SR), np.float32)]), rt, wet, seed=71, bright=1500)
    return y

# ── the guns ───────────────────────────────────────────────────────────────────
shot = seg('Gunshots_8.wav', 0.05, 0.55)
pan = place(0.12, [(0.0, metal_hit(3800, 60, 4, 0.08, 1), 0.5), (0.01, noise(0.1, 2000, 7000, 2) * np.exp(-np.arange(int(0.1 * SR)) / SR * 30).astype(np.float32), 0.25)])
pistol = place(1.6, [(0.0, pan, 1.0), (0.09, shot, 1.0), (0.09, lp(shot, 300) * 1.5, 0.6)])
write_mp3(peak_db(reverb(pistol, 0.9, 0.2), -3), 'pistol-near.mp3')
write_mp3(peak_db(far(pistol, 800, 3.0, 0.5, 0.2), -14), 'pistol-far.mp3')
musket = place(2.0, [(0.0, pan, 1.0), (0.12, shot, 1.0), (0.12, lp(shot, 220) * 2.0, 0.8)])
write_mp3(peak_db(reverb(musket, 1.2, 0.25), -2), 'musket-near.mp3')
write_mp3(peak_db(far(musket, 700, 3.6, 0.55, 0.35), -13), 'musket-far.mp3')
volley = np.zeros(int(4.5 * SR), np.float32)
for k in range(7): put(volley, musket, 0.05 + k * 0.11 + 0.08 * rng.random(), 0.5 + 0.4 * rng.random())
write_mp3(peak_db(far(volley, 900, 3.4, 0.5, 0.3), -10), 'musket-volley-far.mp3')
cannon = seg('01_Salute_Cannon_Reveille.wav', 0.25, 6.5)
write_mp3(peak_db(reverb(env(cannon, [(0, 1), (5.0, 1), (6.25, 0)]), 2.2, 0.25), -1), 'cannon-near.mp3')
write_mp3(peak_db(far(cannon, 500, 5.0, 0.6, 0.6), -9), 'cannon-far.mp3')

# ── blades, blows, the stick ───────────────────────────────────────────────────
clash = place(1.8, [(0.0, metal_hit(1700, 14, 7, 1.0, 3), 1.0), (0.32, metal_hit(2100, 16, 7, 1.0, 4), 0.8),
                    (0.36, noise(0.35, 2500, 8000, 5) * np.linspace(1, 0, int(0.35 * SR)).astype(np.float32), 0.25),
                    (0.95, lp(load('/tmp/snd/w_Dull_thud.wav')[:int(0.4 * SR)], 3000), 0.7)])          # the blade bites the signboard
write_mp3(peak_db(reverb(clash, 1.0, 0.2), -6), 'cutlass-clash.mp3')
rap = seg('Knocking_on_wood_or_door.wav', 4.5, 4.75)
write_mp3(peak_db(reverb(place(1.6, [(0.0, rap, 1.0), (0.38, rap, 0.9), (0.74, rap, 1.0)]), 0.9, 0.2), -8), 'stick-rap.mp3')
tap = hp(sg.resample(rap, int(len(rap) / 1.5)).astype(np.float32), 400)
taps = np.zeros(int(7.0 * SR), np.float32); t = 0.2; k = 0
while t < 6.4:
    put(taps, tap, t, 0.25 + 0.75 * (t / 6.4)); t += 0.55 + 0.06 * rng.random(); k += 1                       # tap-tap-tapping, coming nearer
write_mp3(peak_db(reverb(taps, 1.6, 0.3, bright=2500), -11), 'stick-taps.mp3')
fall = place(1.8, [(0.0, lp(load('/tmp/snd/w_Dull_thud.wav')[:int(0.5 * SR)], 900) * 2.0, 1.0),
                   (0.18, lp(load('/tmp/snd/w_Dull_thud.wav')[:int(0.4 * SR)], 1500), 0.5)])
write_mp3(peak_db(reverb(fall, 0.9, 0.2), -7), 'body-fall.mp3')
crash = place(2.4, [(0.0, lp(load('/tmp/snd/w_Dull_thud.wav')[:int(0.5 * SR)], 1200) * 2.0, 1.0),
                    (0.45, lp(load('/tmp/snd/w_Dull_thud.wav')[:int(0.5 * SR)], 1200) * 2.0, 1.0),
                    (0.48, noise(0.7, 600, 6000, 9) * np.exp(-np.arange(int(0.7 * SR)) / SR * 5).astype(np.float32), 0.5),
                    (0.6, seg('Door_handle_creaking.wav', 0.4, 1.4), 0.6)])
write_mp3(peak_db(reverb(crash, 1.0, 0.22), -4), 'door-crash.mp3')
write_mp3(peak_db(far(seg('Human_whistling.wav', 0.0, 1.47), 2500, 2.6, 0.45, 0.1), -14), 'whistle-signal.mp3')

# ── birds, and the cove itself ─────────────────────────────────────────────────
write_mp3(peak_db(reverb(seg('Western_Gull_Golden_Gate_National_Recreation_Area.wav', 0, 4.6), 1.6, 0.25), -16), 'gull.mp3')
r = np.random.default_rng(1884); L = 70.0; N = int(L * SR); sea = np.zeros(N, np.float32)
swell = lp(r.standard_normal(N), 160, 2).astype(np.float32); sea += rms_db(swell, -33)
t = 0.0
while t < L:                                           # breakers on the rocks below the cliff, then the wash back
    d = 6.5 + 4 * r.random(); n = int(d * SR); tt = np.arange(n) / SR
    e = (np.clip(tt / (0.22 * d), 0, 1) ** 1.5) * np.exp(-np.clip(tt - 0.22 * d, 0, None) * 0.9)
    wave = lp(r.standard_normal(n), 1800, 2) * e + 0.3 * hp(r.standard_normal(n), 3000) * e * np.clip((tt - 0.4 * d) / (0.3 * d), 0, 1)
    put(sea, rms_db(wave.astype(np.float32), -24) * (0.6 + 0.6 * r.random()), t); t += d * (0.5 + 0.3 * r.random())
wind = load('/tmp/snd/src3/Howling_wind.wav')[int(20 * SR): int(20 * SR) + N]
cove = reverb(sea, 1.6, 0.2) + rms_db(lp(wind, 1200), -36)
write_mp3(rms_db(fold(cove, 5.0), -25), 'cove.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v in files.items(): print(f'{k_:24s} {v:6.2f}s')
