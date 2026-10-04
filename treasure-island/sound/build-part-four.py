#!/usr/bin/env python3
"""Treasure Island — Part Four: the Stockade. The long gun firing on the jolly-boat,
round shot whistling over and plumping into the sand, the boat going down by the stern,
and the attack on the log-house. Built from this folder's gunfire, the theme's recorded
battle voices, and the PD/CC0 sources in SOURCES.md. Deterministic (seed 1883)."""
import os, json
src = open('/tmp/snd/ch16_assets.py').read().split('# ── the instruments')[0]
src = src.replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/ti/sound4/'")
exec(src)
os.makedirs('/tmp/ti/sound4', exist_ok=True)
rng = np.random.default_rng(1883)
import subprocess as _sp
def mp3(path):
    raw = _sp.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
TI = lambda f: mp3('/tmp/ti/sound/' + f)
CANNON_N, CANNON_F, PISTOL, MUSK, MUSK_F, VOLLEY_F, CLASH = (TI(f) for f in ('cannon-near.mp3', 'cannon-far.mp3', 'pistol-near.mp3', 'musket-near.mp3', 'musket-far.mp3', 'musket-volley-far.mp3', 'cutlass-clash.mp3'))
THUD = load('/tmp/snd/w_Dull_thud.wav')[: int(0.5 * SR)]
def whistle_shot(d=1.8, near=True):
    n = int(d * SR); t = np.arange(n) / SR
    f = 1500 * np.exp(-t * (0.9 if near else 0.5)) + 380
    y = (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + bp(rng.standard_normal(n), 400, 3000) * 0.8)
    y *= (t / d) ** (2.5 if near else 1.5) * np.exp(-np.clip(t - 0.88 * d, 0, None) * 30)
    return lp(y.astype(np.float32), 6000 if near else 2500)
def sand_hit():
    n = int(1.6 * SR); t = np.arange(n) / SR
    y = lp(THUD, 700) * 1.6
    out = np.zeros(n, np.float32); put(out, y, 0)
    put(out, (bp(rng.standard_normal(n), 800, 5000) * np.exp(-t * 5)).astype(np.float32) * 0.35, 0.02)   # the sand thrown up and falling
    return out
def splash(d=2.0, big=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    y = lp(rng.standard_normal(n), 1800) * np.exp(-t * 3.5) * big + 0.4 * hp(rng.standard_normal(n), 2500) * np.exp(-t * 6)
    return y.astype(np.float32)

# the long nine fires from the ship; the shot roars over and plumps into the water
s = np.zeros(int(9 * SR), np.float32)
put(s, CANNON_F, 0.0, 0.8); put(s, reverb(whistle_shot(1.9, True), 1.2, 0.2), 1.6, 0.6); put(s, reverb(splash(2.2), 1.4, 0.25), 3.45, 0.7)
write_mp3(peak_db(s, -4), 'long-gun-splash.mp3')
# a round shot fired at the stockade: the roar, the whistle, and the sand flung up inside the fence
s = np.zeros(int(8 * SR), np.float32)
put(s, CANNON_F, 0.0, 0.7); put(s, reverb(whistle_shot(1.6, True), 1.2, 0.2), 1.3, 0.55); put(s, reverb(sand_hit(), 1.2, 0.25), 2.85, 0.8)
write_mp3(peak_db(s, -5), 'round-shot-sand.mp3')
# 'all through the evening they kept thundering away': the cannonade, far, ball after ball
s = np.zeros(int(30 * SR), np.float32); t_ = 0.2
while t_ < 26:
    put(s, CANNON_F, t_, 0.5 + 0.3 * rng.random())
    if rng.random() < 0.6: put(s, reverb(sand_hit(), 1.4, 0.3), t_ + 2.3 + rng.random(), 0.4)
    t_ += 4.5 + 3.0 * rng.random()
write_mp3(peak_db(env(s, [(0, 0), (0.3, 1), (25, 1), (30, 0)]), -9), 'cannonade.mp3')
# the overloaded jolly-boat going down by the stern in three feet of water
s = np.zeros(int(5 * SR), np.float32)
put(s, reverb(splash(3.0, 1.4), 1.0, 0.2), 0.0, 1.0)
for k in range(10):                                                      # the water pouring in, gear floating off
    q = int(0.06 * SR); tq = np.arange(q) / SR; fq = 500 + 700 * rng.random()
    put(s, (np.sin(2 * np.pi * fq * (1 + 1.5 * tq / tq[-1]) * tq) * np.exp(-tq * 40)).astype(np.float32) * 0.12, 0.6 + k * 0.25)
write_mp3(peak_db(s, -9), 'boat-sinks.mp3')
# the Union Jack run up and snapping above the log-house
n = int(4 * SR); fl = np.zeros(n, np.float32)
for k in range(14):
    i = int((0.2 + k * 0.26 + 0.05 * rng.random()) * SR); m = int(0.12 * SR)
    fl[i:i + m] += (lp(rng.standard_normal(m), 1400) * np.exp(-np.arange(m) / SR * 25)).astype(np.float32)[: max(0, n - i)] * (0.5 + 0.5 * rng.random())
write_mp3(peak_db(reverb(fl, 1.0, 0.2), -16), 'flag-snap.mp3')

# THE ATTACK — the scattering volley from every side of the enclosure, balls thudding into
# the logs, then the rush over the palisade: men shouting, cutlasses, pistols at the
# doorway, balls zipping past, until the survivors run. 40 s.
L = 40.0; N = int(L * SR); at = np.zeros(N, np.float32)
def stage(x, dist=0.3, seed=0):
    x = hp(x, 70); loud = np.abs(x) > 0.02 * np.abs(x).max(); x = x / (np.sqrt(np.mean(x[loud] ** 2)) + 1e-9) * 0.12
    return reverb(np.concatenate([x, np.zeros(int(2.0 * SR), np.float32)]), 1.4 + 1.6 * dist, 0.18 + 0.35 * dist, seed=seed)
def zip_by():
    n = int(0.28 * SR); t = np.arange(n) / SR; f = 3200 - 2200 * (t / t[-1]) ** 0.7
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + 0.5 * bp(rng.standard_normal(n), 1500, 6000)
    return (y * np.exp(-((t - 0.11) / 0.05) ** 2)).astype(np.float32)
t_ = 0.0                                                                  # 1. the volley: shot behind shot, like a string of geese
while t_ < 9.0:
    put(at, MUSK_F if rng.random() < 0.5 else MUSK, t_, 0.35 + 0.35 * rng.random())
    if rng.random() < 0.4: put(at, lp(THUD, 1500) * 0.8, t_ + 0.15 + 0.1 * rng.random())     # a ball into the logs
    t_ += 0.25 + 0.5 * rng.random()
SHOUT = ['here_they_come', 'fire', 'get_down', 'reload', 'boarding', 'hold', 'rail', 'fire2']
MEL = ['cover', 'stay_back', 'to_me', 'load_fire', 'your_left', 'heads_down']
t_ = 10.0; k = 0                                                          # 2. over the palisade: hand to hand
while t_ < 34.0:
    r = rng.random()
    if r < 0.25: put(at, CLASH, t_, 0.5 + 0.3 * rng.random())
    elif r < 0.40: put(at, PISTOL, t_, 0.55)
    elif r < 0.50: put(at, zip_by(), t_, 0.45)
    elif r < 0.58: put(at, MUSK, t_, 0.5)
    else:
        name = (SHOUT + MEL)[k % 14]; folder = 'vox4' if name in SHOUT else 'vox6'
        put(at, stage(load('/tmp/ti/%s/%s.wav' % (folder, name)), 0.2 + 0.4 * rng.random(), seed=k), t_, 0.9); k += 1
    t_ += 0.3 + 0.55 * rng.random()
put(at, MUSK_F, 35.0, 0.35); put(at, MUSK_F, 37.2, 0.25)                 # 3. the last shots after the men who ran
at = env(at, [(0, 0), (0.05, 1), (33, 1), (L, 0)])
write_mp3(peak_db(at, -3), 'stockade-attack.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v in files.items(): print(f'{k_:22s} {v:6.2f}s')
