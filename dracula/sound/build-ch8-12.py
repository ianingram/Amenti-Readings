#!/usr/bin/env python3
"""Dracula — Chapters VIII–XII: Lucy. New sounds — the bat at the window, the wolf through
the glass, thunder over Whitby — and a new cue, THE VIGIL: the sickroom where Lucy is
being drained night by night. A music box (glockenspiel) that keeps winding down, a
low string pedal under it, the piano barely touched. Fragile, and it gets more fragile.
Instruments VSCO 2 CE (CC0); thunder from Wikimedia Commons (stephan, PD). Seed 1897."""
import os, re, glob, json
exec(open('/tmp/qv/prod/qv_score.py').read().split('# ═══ OPULENCE')[0].replace("/tmp/qv/score/", "/tmp/dr/sound/"))
rng = np.random.default_rng(1897)
GLOCK = {midi_of(re.search(r'_([A-G]#?\d)\.wav', f).group(1)): f for f in glob.glob('/tmp/vsco/Percussion/Glock/glock_medium_*.wav')}
def glock(m, g=1.0):
    k = min(GLOCK, key=lambda q: abs(q - m)); return load16(GLOCK[k], m - k) * g
# the bat at the window: soft leathery beats against the glass, coming and going
n = int(4.0 * SR); bat = np.zeros(n, np.float32); t_ = 0.1
while t_ < 3.5:
    q = int(0.07 * SR); tq = np.arange(q) / SR
    beat = (lp(rng.standard_normal(q), 900) * np.exp(-tq * 45)).astype(np.float32)
    put(bat, beat, t_, 0.4 + 0.6 * np.sin(np.pi * t_ / 3.6)); t_ += 0.09 + 0.05 * rng.random()
    if rng.random() < 0.12: put(bat, (hp(rng.standard_normal(int(0.03 * SR)), 2500) * 0.2).astype(np.float32), t_)      # a claw on the pane
write_mp3(peak_db(reverb(bat, 1.2, 0.2), -14), 'wing-beat.mp3')
# the wolf through the window: the frame giving, glass bursting and falling across the floor
n = int(3.5 * SR); gl = np.zeros(n, np.float32)
put(gl, lp(load('/tmp/snd/w_Dull_thud.wav')[: int(0.4 * SR)], 1500) * 1.4, 0.0)
for k in range(140):
    t0 = 0.02 + (rng.random() ** 2) * 2.4; q = int((0.02 + 0.08 * rng.random()) * SR); tq = np.arange(q) / SR
    f = 2500 + 7000 * rng.random()
    shard = (np.sin(2 * np.pi * f * tq) * np.exp(-tq * (60 + 80 * rng.random())) + 0.6 * hp(rng.standard_normal(q), 3000) * np.exp(-tq * 120))
    put(gl, shard.astype(np.float32), t0, (0.5 + 0.5 * rng.random()) * (1 - t0 / 2.6))
write_mp3(peak_db(reverb(gl, 1.4, 0.22), -5), 'glass-crash.mp3')
# thunder over the North Sea
th = load('/tmp/snd/th/Storm_thunderbolts.wav')
env_ = np.array([np.sqrt(np.mean(th[i:i + 4800] ** 2)) for i in range(0, len(th) - 4800, 4800)])
pk = int(np.argmax(env_)) * 4800; seg = th[max(0, pk - int(0.6 * SR)): pk + int(6 * SR)]
write_mp3(peak_db(env(seg, [(0, 0), (0.05, 1), (len(seg) / SR - 1.2, 1), (len(seg) / SR, 0)]), -4), 'thunder.mp3')
# ═══ THE VIGIL — the sickroom: a music box winding down over a low string pedal ═══════════
BT = 60 / 52; BAR = 4 * BT; bars = 12; N = int((bars * BAR + 6) * SR)
box, pedal, pn = (np.zeros(N, np.float32) for _ in range(3))
TUNE = [76, 72, 69, 71, 72, 69, 64, 0, 76, 74, 72, 71, 69, 0, 0, 0, 74, 72, 71, 69, 68, 69, 71, 0, 72, 69, 64, 65, 64, 0, 0, 0]
t_ = 0.5; step = BT / 2
for i, m in enumerate(TUNE * 2):
    drag = 1 + 0.012 * i                                                    # the music box running down
    if m: put(box, glock(m + 12, 0.5 - 0.004 * i), t_)
    t_ += step * drag
put(pedal, sustain(CEL, 45, bars * BAR, head=0.6, kx=0.6, tail=3), 0.0, 0.6); put(pedal, sustain(VLA, 52, bars * BAR, head=0.6, kx=0.6, tail=3), 1.0, 0.4)
for b in range(0, bars, 3): put(pn, pno(45 + (0 if b % 2 == 0 else -4), 0.4), b * BAR + BT)
mix = stems((reverb(box, 3.2, 0.42, seed=31), -28), (reverb(pedal, 3.6, 0.35, seed=32), -32), (reverb(pn, 3.4, 0.38, seed=33), -36))
render('score-vigil.mp3', mix[: int((bars * BAR + 3) * SR)], 3.0, -27)
json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:20s} {v_:6.2f}s')
