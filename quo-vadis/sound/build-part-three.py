#!/usr/bin/env python3
"""Quo Vadis — Part Three. The house in the Trans-Tiber where the Christians hide Lygia and
nurse the wounded Vinicius: a small room round a hearth, Nazarius's pigeons on the sill,
the city beyond; and the fight in the dark corridor — Ursus and Croton. Seed 64."""
import os, json
exec(open('/tmp/qv/prod/qv_score.py').read().split('# ═══ OPULENCE')[0].replace("/tmp/qv/score/", "/tmp/qv/score3/"))
os.makedirs('/tmp/qv/score3', exist_ok=True)
import subprocess as _sp
def mp3(path): return np.frombuffer(_sp.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).copy()
L = 64.0; N = int(L * SR); t = np.arange(N) / SR
def tile(x, n=N): return np.tile(x, int(np.ceil(n / len(x))))[:n]
fire = tile(mp3('/tmp/snd/ch16/../out/fire.mp3') if os.path.exists('/tmp/snd/out/fire.mp3') else lp(rng.standard_normal(N).astype(np.float32), 600))
crowd = tile(load('/tmp/qv/src/360703_eguobyte_large-crowd-medium-distance-stereo_m.wav'))
coo = np.zeros(N, np.float32)
for t0 in np.arange(3.0, L - 2, 7.0):                           # pigeons on the sill: a soft three-note coo now and then
    for k, (f, d) in enumerate(((310, 0.35), (290, 0.25), (330, 0.55))):
        n = int(d * SR); tt = np.arange(n) / SR
        y = np.sin(2 * np.pi * f * (1 + 0.04 * np.sin(2 * np.pi * 7 * tt)) * tt) * np.sin(np.pi * tt / d) ** 1.5
        put(coo, (y * 0.5 + 0.2 * np.sin(4 * np.pi * f * tt) * np.sin(np.pi * tt / d)).astype(np.float32), t0 + rng.random() + k * 0.42)
ch = rms_db(fire, -36) + rms_db(lp(coo, 1200), -40) + rms_db(lp(crowd, 350), -48)
loopfile('christian-house.mp3', ch, 4.0, -32)
# the fight in the corridor: two giants locked, breath and strain, a crack, a body falling
thud = load('/tmp/snd/w_Dull_thud.wav')[: int(0.5 * SR)]
f_ = np.zeros(int(9 * SR), np.float32)
for k, t0 in enumerate((0.2, 0.9, 1.4, 2.6, 3.1, 4.4)):                              # shoving, feet scraping on stone
    put(f_, lp(thud, 500) * 0.6, t0); n = int(0.4 * SR)
    put(f_, (bp(rng.standard_normal(n), 800, 4000) * np.exp(-np.arange(n) / SR * 8)).astype(np.float32) * 0.15, t0 + 0.1)
n = int(2.2 * SR); strain = lp(rng.standard_normal(n), 300) * np.sin(np.pi * np.arange(n) / n) ** 2      # the long crush
put(f_, strain.astype(np.float32) * 0.5, 4.8)
crack = np.zeros(int(0.3 * SR), np.float32); put(crack, (hp(rng.standard_normal(int(0.02 * SR)), 1500) * 3).astype(np.float32), 0); put(crack, lp(thud, 2000) * 0.6, 0.005)
put(f_, crack, 7.0, 1.0); put(f_, lp(thud, 700) * 1.6, 7.7)                                              # the spine gives; Croton falls
write_mp3(peak_db(reverb(f_, 1.3, 0.25), -4), 'corridor-fight.mp3')
json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:22s} {v_:6.2f}s')
