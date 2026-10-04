#!/usr/bin/env python3
"""Treasure Island — Part Two: the Sea-cook. Bristol docks, the Spy-glass, the
Hispaniola at anchor and under sail. Recordings from Wikimedia Commons (PD/CC0, see
SOURCES.md); the ship's horn and bell built here. Deterministic (seed 1883)."""
import os, json
src = open('/tmp/snd/ch16_assets.py').read().split('# ── the instruments')[0]
src = src.replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/ti/sound2/'")
exec(src)
os.makedirs('/tmp/ti/sound2', exist_ok=True)
S = '/tmp/ti/src/'
rng = np.random.default_rng(1883)
import subprocess as _sp
def mp3(path):
    raw = _sp.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def seg(x, a, b): return x[int(a * SR): int(b * SR)].copy()

# ── the docks: water slapping the wharf piles, moored boats working, gulls about
wharf = load(S + 'Boat_by_a_wharf_2.wav'); L = 64.0; N = int(L * SR)
docks = rms_db(hp(wharf[:N + int(5 * SR)], 50), -28)
G1 = load('/tmp/snd/src3/Gull_1.wav'); HG = load(S + 'herring.wav')
for t_, x_, g in ((4.0, seg(G1, 6.6, 7.25), .12), (17.5, seg(HG, 7.25, 7.75), .1), (31.0, seg(G1, 10.75, 11.6), .1), (46.0, seg(G1, 12.45, 13.35), .12)):
    put(docks, reverb(lp(x_, 5000), 2.2, 0.35, seed=int(t_)) * g, t_)
chains = mp3('/tmp/snd/ch16/../out/chains.mp3') if os.path.exists('/tmp/snd/out/chains.mp3') else None
if chains is not None: put(docks, reverb(lp(chains, 2500), 2.0, 0.4) * 0.08, 24.0)
write_mp3(rms_db(fold(docks, 4.0), -26), 'docks.mp3')

# ── the deck at sea: the hull working, the wind in the rigging, canvas, a block creaking
hull = mp3('/tmp/snd/ch7/hull.mp3'); hull = np.tile(hull, 2)[:N + int(5 * SR)]
wind = load('/tmp/snd/src3/Howling_wind.wav')[int(5 * SR): int(5 * SR) + N + int(5 * SR)]
deck = rms_db(hull, -28) + rms_db(lp(wind, 1600), -36)
creak = load('/tmp/snd/w_Creaky_wooden_casket.wav')
for t_ in np.arange(3.0, L, 6.5):
    x = sg.resample(creak[: int(1.1 * SR)], int(1.1 * SR * (1.8 + 0.6 * rng.random()))).astype(np.float32)
    put(deck, lp(x, 1500) * 0.07, t_ + rng.random())
for t_ in np.arange(9.0, L, 13.0):                                   # canvas filling and slatting
    n = int(2.2 * SR); y = np.zeros(n, np.float32)
    for k in range(10):
        i = int((k / 5 + 0.04 * rng.random()) * SR); m = int(0.16 * SR)
        b_ = lp(rng.standard_normal(m), 800 + 500 * rng.random()) * np.exp(-np.arange(m) / SR * 18)
        y[i:i + m] += b_[: max(0, n - i)] * (0.4 + 0.6 * rng.random())
    put(deck, y * 0.05, t_)
write_mp3(rms_db(fold(deck, 4.0), -25), 'deck.mp3')

# ── Captain Flint, the parrot
par = load(S + 'Parrots_perroquets.wav')
write_mp3(peak_db(reverb(seg(par, 25.3, 26.45), 0.9, 0.18), -9), 'parrot.mp3')
write_mp3(peak_db(reverb(seg(par, 60.85, 61.45), 0.9, 0.18), -10), 'parrot-2.mp3')

# ── the capstan: the pawls clacking round as the anchor comes up, the cable grinding
rat = load(S + 'Tools_Ratchet.wav')
clicks = seg(rat, 2.3, 5.3)
clk = sg.resample(clicks, int(len(clicks) * 1.9)).astype(np.float32)         # slower, lower: a ship's capstan, not a spanner
cap = np.zeros(int(7 * SR), np.float32); put(cap, lp(clk, 2500), 0.0, 1.0); put(cap, lp(clk, 2500), len(clk) / SR - 0.3, 0.9)
grind = lp(rng.standard_normal(len(cap)), 400) * (0.5 + 0.5 * np.sin(2 * np.pi * np.arange(len(cap)) / SR * 0.7))
cap += grind.astype(np.float32) * 0.08
write_mp3(peak_db(reverb(cap, 1.2, 0.2), -12), 'capstan.mp3')

# ── the ship's horn as she stands out of harbour (D, then down to A), and the bell
def ship_horn(midi, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = 440 * 2 ** ((midi - 69) / 12)
    y = sum(sg.sawtooth(2 * np.pi * (f + d) * t) * 0.5 for d in (0.0, 0.6))
    y = lp(y.astype(np.float32), 520, 3)
    return (y * np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 1.6).clip(0, 1)).astype(np.float32)
hn = np.zeros(int(12 * SR), np.float32); put(hn, ship_horn(38, 4.5), 0.0); put(hn, ship_horn(33, 5.0), 4.2)
write_mp3(peak_db(reverb(hn, 4.0, 0.45, bright=1800), -10), 'ship-horn.mp3')
def ship_bell(f0=880.0):
    n = int(4.5 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for ratio, a_, d in ((0.5, .35, 0.9), (1.0, 1.0, 1.1), (1.19, .18, 2.2), (1.5, .22, 1.8), (2.0, .55, 1.6), (2.66, .18, 3.0), (3.0, .12, 3.6)):
        y += a_ * np.sin(2 * np.pi * f0 * ratio * t + rng.random()) * np.exp(-t * d)
    y += 0.25 * hp(rng.standard_normal(n), 3000) * np.exp(-t * 300)
    return (y * np.minimum(1, t / 0.0015)).astype(np.float32)
bw = np.zeros(int(6 * SR), np.float32)
for k, t_ in enumerate((0.05, 0.6, 2.0, 2.55)): put(bw, ship_bell(880 * (1 + 0.001 * k)), t_, 0.8)
write_mp3(peak_db(reverb(bw, 2.6, 0.3), -12), 'bell-watch.mp3')
la = np.zeros(int(5 * SR), np.float32)                                # "Land ho!" — the bell rung hard and fast
for k in range(8): put(la, ship_bell(880 * (1 + 0.002 * (k % 2))), 0.05 + k * 0.32, 0.8)
write_mp3(peak_db(reverb(la, 2.2, 0.28), -10), 'bell-alarm.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v in files.items(): print(f'{k_:20s} {v:6.2f}s')
