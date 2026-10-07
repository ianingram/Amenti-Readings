#!/usr/bin/env python3
"""Julius Caesar — the sound for Part 1 (Acts I–III), 7 Oct 2026.

New here (everything else is borrowed by URL from the other productions):
  beds
    storm-night.mp3   the night of portents (I.iii): wind (Dracula's pass), rain, and thunder far
                      off under it — the near strikes are one-shots placed on the stage directions
    senate.mp3        before the Capitol (III.i): the senators murmuring under a stone portico, the
                      street crowd far behind them
  one-shots
    flourish.mp3      trumpets: a short fanfare in C, Caesar's key
    sennet.mp3        trumpets and horns: the longer call that clears the stage
    clock-three.mp3   a tower bell striking three (II.i, "Peace! count the clock.")
    stabbing.mp3      the assassination: the first blow (Casca, at the neck), the struggle, the
                      blows of the others, the cloak, the fall
    bell-toll.mp3     the Forum's great bell in G, struck once: Caesar dies
    mob.mp3           the mob turned: a roar with stamping, low and ugly
Sources: VSCO 2 CE (CC0); the Dracula wind and rain and the Storm-thunderbolts recording (PD, see
Dracula's SOURCES.md); Quo Vadis's rome-street, cheer and applause (PD/CC0); synthesis. Seed 44."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jc_kit import *
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
RD = '/tmp/claude-0/-home-claude/c002dc02-d023-5c73-9437-2a1012982e23/scratchpad/rd/'
OUT = HERE + 'out1/'; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(44)
def aud(path):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                                        capture_output=True).stdout, np.float32).copy()
def env_lin(n, pts):
    xs = [p[0] * SR for p in pts]; ys = [p[1] for p in pts]
    return np.interp(np.arange(n), xs, ys).astype(np.float32)
def tile(x, n): return np.tile(x, int(np.ceil(n / len(x))) + 1)[:n]
def nh(x, pk=1.0): return (x / (np.abs(x).max() + 1e-9) * pk).astype(np.float32)
def loop60(x, xf=3.0):
    """a 60 s bed whose end crossfades into its start"""
    n = int(60 * SR); k = int(xf * SR); y = x[:n + k].copy()
    y[:k] = y[:k] * np.linspace(0, 1, k) + y[n:n + k] * np.linspace(1, 0, k)
    return y[:n]
P = V + 'Percussion/'

# ── storm-night ──
N = int(64 * SR)
wind = tile(aud(RD + 'dracula/sound/wind.mp3'), N)
rain = tile(aud(RD + 'dracula/sound/log-rain.mp3'), N)
rain = hp(rain, 300) * 0.8
th = aud(RD + 'dracula/sound/thunder.mp3')
far = np.zeros(N, np.float32)
for t, g in ((6, 0.5), (23, 0.35), (41, 0.55), (55, 0.3)):
    put(far, lp(th, 380) * g, t)                       # far off: only the roll comes through
far = reverb(far, 3.0, 0.4, seed=5)
storm = stems((wind, -26), (rain, -30), (far, -27))
write_mp3(rms_db(loop60(storm), -26), OUT + 'storm-night.mp3')

# ── senate ──
street = aud(RD + 'quo-vadis/sound/rome-street.mp3')
N = int(64 * SR)
murmur = tile(bp(street, 160, 1400), N)
far_st = tile(lp(np.roll(street, int(17 * SR)), 600), N)
senate = stems((reverb(murmur, 2.8, 0.45, seed=6), -27), (far_st, -34))
write_mp3(rms_db(loop60(senate), -29), OUT + 'senate.mp3')

# ── flourish and sennet ──
TPT = bank('Brass/Trumpet/sus/*_v3_rr1.wav', r'sus_([A-G]#?\d)_')
TPTST = bank('Brass/Trumpet/stac/*_v3_rr1.wav', r'stac_([A-G]#?\d)_')
HORN = bank('Brass/F Horn/sus/*_v2_1.wav', r'sus_([A-G]#?\d)_')
BT = 60 / 96
def fanfare(notes, inst_st, inst_sus, voices=((0, 1.0), (-5, 0.55))):
    out = np.zeros(int((sum(d for _, d in notes) * BT + 3) * SR), np.float32); t = 0
    for m, d in notes:
        for iv, g in voices:
            x = pluck(inst_st, m + iv, g) if d < 0.6 else sustain(inst_sus, m + iv, d * BT + 0.15, head=0.08, kx=0.1, tail=0.25) * g
            put(out, x, t + rng.uniform(0, 0.012))
        t += d * BT
    return out
FL = [(60, 0.33), (60, 0.33), (60, 0.34), (67, 1.0), (64, 0.5), (67, 0.5), (72, 2.0)]   # C: da-da-da DAH, da DAH, DAAAH
fl = fanfare(FL, TPTST, TPT)
write_mp3(rms_db(reverb(fl, 2.2, 0.32, seed=7), -23), OUT + 'flourish.mp3')
SE = [(55, 1.0), (60, 1.0), (64, 0.5), (62, 0.5), (60, 1.0), (67, 1.5), (60, 2.5)]
se = fanfare(SE, TPTST, TPT) + 0
hn = np.zeros_like(se)
for m, st, d in ((48, 0, 4.0), (55, 4.0, 3.5)): put(hn, sustain(HORN, m, d * BT + 0.5, head=0.2, kx=0.2, tail=0.8), st * BT, 0.5)
write_mp3(rms_db(reverb(se + hn, 2.4, 0.34, seed=8), -24), OUT + 'sennet.mp3')

# ── the bells: the great bell (from the Forum suite) and a smaller tower bell ──
ANVIL = nh(load16(P + 'Anvil_Hit1_v3_Sum.wav'))
def bell(f, secs=9.0, seed=0, clank=0.55):
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    PART = [(0.5, 1.0, 0.35), (1.0, 0.8, 0.55), (1.19, 0.6, 0.8), (1.5, 0.35, 1.2), (2.0, 0.7, 1.0),
            (2.5, 0.3, 1.8), (2.66, 0.25, 2.2), (3.0, 0.22, 2.6), (4.2, 0.15, 4.0), (5.4, 0.08, 6.0)]
    x = np.zeros(n, np.float32)
    for m, a, dec in PART:
        for det in (-0.6, 0.6):
            x += (a * 0.5 * np.sin(2 * np.pi * (f * m + det * m * 0.3) * t + r.uniform(0, 6.28)) * np.exp(-t * dec)).astype(np.float32)
    x *= np.clip(t / 0.002, 0, 1).astype(np.float32)
    c = ANVIL[:n]; x[:len(c)] += c * clank
    return nh(x)
toll = np.zeros(int(12 * SR), np.float32); put(toll, bell(98.0, 11.5, seed=3), 0.05)
write_mp3(rms_db(reverb(toll, 3.2, 0.4, seed=9), -23), OUT + 'bell-toll.mp3')
clk = np.zeros(int(9 * SR), np.float32)
for k in range(3): put(clk, bell(262.0, 4.0, seed=10 + k, clank=0.25) * 0.8, 0.1 + 1.7 * k)
write_mp3(rms_db(lp(reverb(clk, 2.0, 0.35, seed=11), 5000), -29), OUT + 'clock-three.mp3')

# ── the assassination ──
def blow(g, dark=180):
    n = int(0.22 * SR); t = np.arange(n) / SR
    thud = lp(rng.standard_normal(n).astype(np.float32), dark) * np.exp(-t * 26) * 4
    cloth = bp(rng.standard_normal(n).astype(np.float32), 900, 4000) * np.exp(-t * 40) * 0.35
    return ((thud + cloth) * g).astype(np.float32)
def scuffle(d, g):
    n = int(d * SR); x = np.zeros(n, np.float32); t = 0.0
    while t < d - 0.1:
        k = int(0.09 * SR); s = bp(rng.standard_normal(k).astype(np.float32), 150, 1600) * np.exp(-np.arange(k) / SR * 30)
        put(x, s * rng.uniform(0.2, 0.6), t); t += rng.uniform(0.06, 0.22)
    return x * g
N = int(11 * SR); st = np.zeros(N, np.float32)
put(st, blow(1.3, 240), 0.15)                                  # Casca, at the neck
put(st, scuffle(2.6, 0.8), 0.35)                               # Caesar catches his arm
ts = [1.4, 1.75, 2.0, 2.45, 2.6, 3.05, 3.3, 3.5, 3.95, 4.3, 4.5, 4.95, 5.4, 5.9]
for t in ts: put(st, blow(rng.uniform(0.7, 1.15)), t + rng.uniform(-0.03, 0.03))
put(st, scuffle(1.6, 0.5), 3.0)
n = int(1.6 * SR); swish = bp(rng.standard_normal(n).astype(np.float32), 300, 2500) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.5
put(st, swish, 6.6)                                            # he muffles his face in his mantle
fall = lp(rng.standard_normal(int(0.5 * SR)).astype(np.float32), 120) * np.exp(-np.arange(int(0.5 * SR)) / SR * 9) * 5
put(st, fall, 8.2)                                             # at the base of Pompey's statue
write_mp3(rms_db(reverb(st, 1.8, 0.3, seed=12), -23), OUT + 'stabbing.mp3')

# ── the mob ──
cheer = aud(RD + 'quo-vadis/sound/cheer.mp3'); app = aud(RD + 'quo-vadis/sound/applause.mp3')
def down(x, semis):
    r = 2 ** (semis / 12); idx = np.arange(int(len(x) / r)) * r
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)
N = int(7 * SR); mob = np.zeros(N, np.float32)
roar = down(np.concatenate([cheer, cheer[::-1]]), -4)
put(mob, roar[:N] * env_lin(min(N, len(roar)), [(0, 0), (0.25, 1), (4.5, 0.9), (6.5, 0)])[: min(N, len(roar))], 0)
put(mob, down(cheer, -2) * 0.8, 0.4)
stamp = np.zeros(N, np.float32)
for k in range(10):
    for d in range(16): put(stamp, blow(rng.uniform(0.15, 0.3), 200), 0.3 + k * 0.5 + rng.uniform(0, 0.08))
put(mob, stamp * env_lin(N, [(0, 0), (0.5, 1), (5, 1), (6.5, 0)]), 0)
mob = np.tanh(mob / (np.abs(mob).max() + 1e-9) * 2.2)
write_mp3(rms_db(lp(reverb(mob, 1.6, 0.3, seed=13), 3500), -22), OUT + 'mob.mp3')
print('built', sorted(os.listdir(OUT)))
