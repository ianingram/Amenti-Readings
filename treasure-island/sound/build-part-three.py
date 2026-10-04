#!/usr/bin/env python3
"""Treasure Island — Part Three: My Shore Adventure. The island in a stagnant heat,
the marsh, the boats pulling ashore, the murder of Tom, Ben Gunn, and the cannon that
wakes every echo of the island. Recordings from Wikimedia Commons (PD/CC0, SOURCES.md)
and the voice service; the rest built here. Deterministic (seed 1883)."""
import os, json
src = open('/tmp/snd/ch16_assets.py').read().split('# ── the instruments')[0]
src = src.replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/ti/sound3/'")
exec(src)
os.makedirs('/tmp/ti/sound3', exist_ok=True)
S = '/tmp/ti/src/'
rng = np.random.default_rng(1883)
import subprocess as _sp
def mp3(path):
    raw = _sp.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def seg(x, a, b): return x[int(a * SR): int(b * SR)].copy()
G1 = load('/tmp/snd/src3/Gull_1.wav'); HG = load(S + 'herring.wav')
CRIES = [seg(G1, a, b) for a, b in ((6.6, 7.25), (7.95, 8.95), (10.75, 11.6), (12.45, 13.35))] + [seg(HG, a, b) for a, b in ((6.45, 6.85), (7.25, 7.75), (8.1, 8.6))]
def far_cry(x, dist, semis=0.0):
    if semis: x = sg.resample(x, int(len(x) / 2 ** (semis / 12))).astype(np.float32)
    x = lp(x / (np.abs(x).max() + 1e-9), 9000 - 6500 * dist)
    return reverb(np.concatenate([x, np.zeros(int(2.5 * SR), np.float32)]), 1.2 + 2.0 * dist, 0.12 + 0.45 * dist, seed=int(dist * 100)) * (1 - 0.75 * dist)

# ── the island in the heat: insects shrilling in the woods, a stagnant stillness, the
#    surf booming half a mile off, shore birds now and then
L = 64.0; N = int(L * SR); isl = np.zeros(N, np.float32); t = np.arange(N) / SR
for k, (f0, rate, g) in enumerate(((4300, 31, .5), (5200, 44, .35), (3600, 23, .3))):   # cicadas: a buzz pulsed fast, swelling slow
    carrier = bp(rng.standard_normal(N).astype(np.float32), f0 * 0.85, f0 * 1.15)
    pulse = (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)) ** 3
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / (17 + 6 * k) + k)
    isl += carrier * pulse * swell * g
isl = rms_db(isl, -36)
cove = mp3('/tmp/ti/sound/cove.mp3'); cove = np.tile(cove, 2)[:N]
isl += rms_db(lp(cove, 600), -32)                                       # the surf, far off and dull
for t_ in (6.0, 21.0, 37.0, 52.0):
    put(isl, far_cry(CRIES[rng.integers(len(CRIES))], 0.75) * 0.25, t_ + rng.random())
write_mp3(rms_db(fold(isl, 4.0), -27), 'island.mp3')

# ── the boats pulling ashore: rowlocks knocking, oars dipping and dripping, in time
oars = np.zeros(int(9 * SR), np.float32)
for k in range(6):
    t0 = 0.2 + k * 1.45
    n = int(0.1 * SR); tt = np.arange(n) / SR
    knock = (np.sin(2 * np.pi * 420 * tt) * np.exp(-tt * 60) + 0.4 * lp(rng.standard_normal(n), 2000) * np.exp(-tt * 90)).astype(np.float32)
    put(oars, knock, t0, 0.6)
    m = int(0.45 * SR); dip = lp(rng.standard_normal(m), 1500) * np.exp(-np.arange(m) / SR * 7)
    put(oars, dip.astype(np.float32), t0 + 0.08, 0.5)
    for j in range(4):
        q = int(0.04 * SR); tq = np.arange(q) / SR; fq = 1000 + 800 * rng.random()
        put(oars, (np.sin(2 * np.pi * fq * (1 + 2 * tq / tq[-1]) * tq) * np.exp(-tq * 70)).astype(np.float32) * 0.08, t0 + 0.7 + j * 0.15)
write_mp3(peak_db(reverb(oars, 1.4, 0.2), -14), 'oars.mp3')

# ── the anchor's plunge, and the birds it sends up wheeling over the woods
plunge = np.zeros(int(6 * SR), np.float32)
m = int(1.6 * SR); put(plunge, (lp(rng.standard_normal(m), 1600) * np.exp(-np.arange(m) / SR * 3)).astype(np.float32), 0.0, 0.8)
for k in range(10):                                                     # wings, then the crying
    q = int(0.12 * SR); put(plunge, (lp(rng.standard_normal(q), 700) * np.exp(-np.arange(q) / SR * 22)).astype(np.float32) * 0.3, 0.4 + k * 0.06)
for k in range(8): put(plunge, far_cry(CRIES[rng.integers(len(CRIES))], 0.4 + 0.06 * k, 0.5 * rng.random()) * 0.35, 0.6 + k * 0.38)
write_mp3(peak_db(plunge, -9), 'anchor-birds.mp3')

# ── the marsh: a cry of anger, another, then one long horrid scream that the rocks
#    of the Spy-glass echo — and the whole marsh going up in a cloud of screaming birds
scr = load('/tmp/ti/vox8/scream.wav')
scr = scr[np.argmax(np.abs(scr) > 0.05 * np.abs(scr).max()):]
far = lp(scr / (np.abs(scr).max() + 1e-9), 2200)
echo = np.zeros(len(far) + int(5 * SR), np.float32)
for d, g in ((0.0, 1.0), (0.55, 0.35), (1.15, 0.22), (1.9, 0.12)):      # 'the rocks re-echoed it a score of times'
    put(echo, lp(far, 1800 - 300 * d), d, g)
write_mp3(peak_db(reverb(echo, 3.0, 0.5, bright=1500), -14), 'scream-far.mp3')
flock = np.zeros(int(9 * SR), np.float32)
for k in range(16):
    put(flock, far_cry(CRIES[rng.integers(len(CRIES))], 0.45 + 0.3 * rng.random(), rng.random() * 1.5) * 0.35, 0.1 + k * 0.42 + 0.2 * rng.random())
write_mp3(peak_db(flock, -11), 'marsh-birds.mp3')

# ── Silver's crutch hurled through the air, and the blow; Silver's whistle
cr = np.zeros(int(2.0 * SR), np.float32); n = int(0.5 * SR); tt = np.arange(n) / SR
whoosh = bp(rng.standard_normal(n), 300, 2500) * np.sin(np.pi * tt / tt[-1]) ** 2
put(cr, whoosh.astype(np.float32), 0.0, 0.5)
put(cr, lp(load('/tmp/snd/w_Dull_thud.wav')[: int(0.5 * SR)], 1200) * 1.6, 0.48, 1.0)
write_mp3(peak_db(reverb(cr, 1.0, 0.2), -9), 'crutch-blow.mp3')
n = int(3.4 * SR); t = np.arange(n) / SR; y = np.zeros(n)
for s0, d, f in ((0.0, 0.55, 2900), (0.75, 0.3, 3300), (1.2, 0.3, 3300), (1.75, 0.9, 2700)):   # 'several modulated blasts'
    m_ = (t >= s0) & (t < s0 + d)
    y[m_] += np.sin(2 * np.pi * f * (1 + 0.03 * np.sin(2 * np.pi * 22 * t[m_])) * t[m_]) * np.minimum(1, (t[m_] - s0) / 0.02)
y += 0.05 * bp(rng.standard_normal(n), 2000, 6000)
write_mp3(peak_db(reverb(y.astype(np.float32), 2.6, 0.4, bright=4000), -15), 'silver-whistle.mp3')

# ── Ben Gunn: a spout of gravel rattling down through the trees
gv = np.zeros(int(2.4 * SR), np.float32); tq = 0.0
while tq < 2.0:
    q = int(0.03 * SR); tick = (hp(rng.standard_normal(q), 1500) * np.exp(-np.arange(q) / SR * 120)).astype(np.float32)
    put(gv, tick, tq, 0.3 + 0.7 * rng.random() * (1 - tq / 2.2)); tq += 0.02 + 0.09 * rng.random() * (1 + tq)
write_mp3(peak_db(reverb(gv, 1.2, 0.25), -15), 'gravel.mp3')

# ── the cannon, and every echo of the island bellowing back
cf = mp3('/tmp/ti/sound/cannon-far.mp3')
ec = np.zeros(len(cf) + int(7 * SR), np.float32)
for d, g in ((0.0, 1.0), (0.8, 0.5), (1.7, 0.35), (2.9, 0.22), (4.2, 0.12)):
    put(ec, lp(cf, 900 - 120 * d), d, g)
write_mp3(peak_db(reverb(ec, 3.5, 0.45, bright=1000), -6), 'cannon-island.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v in files.items(): print(f'{k_:20s} {v:6.2f}s')
