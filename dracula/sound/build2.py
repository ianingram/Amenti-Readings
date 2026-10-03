#!/usr/bin/env python3
"""Episode one — the small sounds. Sources public domain (pdsounds.org via
Wikimedia Commons) or CC0 (SpaceJoe via Freesound/Commons); the rest
synthesized here. Deterministic (seed 1897). See SOURCES.md."""
import numpy as np
exec(open('/tmp/snd/build.py').read().split('# ── door_heavy.mp3')[0])   # shared helpers
rng = np.random.default_rng(1897)

def seg(name, a, b):
    x = load('w_' + name + '.wav'); return x[int(a * SR): int(b * SR)].copy()

def stone(x, rt=1.4, wet=0.3, seed=21): return reverb(x, rt60=rt, wet=wet, bright=3000, seed=seed)

def step(heavy=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.45 * SR); t = np.arange(n) / SR
    heel = lp(r.standard_normal(n), 1800) * np.exp(-t * 55)
    body = np.sin(2 * np.pi * (70 + 20 * r.random()) * t) * np.exp(-t * 28) * heavy
    toe = np.zeros(n); k = int((0.07 + 0.03 * r.random()) * SR)
    toe[k:] = (bp(r.standard_normal(n - k), 400, 3000) * np.exp(-np.arange(n - k) / SR * 70)) * 0.5
    grit = hp(r.standard_normal(n), 2500) * np.exp(-t * 90) * 0.15
    return (heel * 0.8 + body * 0.9 + toe + grit).astype(np.float32)

def steps(times, heavy=1.0, gains=None, seed=0):
    n = int((times[-1] + 0.6) * SR); out = np.zeros(n, np.float32)
    for j, at in enumerate(times):
        s = step(heavy, seed + j) * (gains[j] if gains else 1.0)
        i = int(at * SR); out[i:i + len(s)] += s[: n - i]
    return out

def metal_hit(n_modes=6, base=2200, decay=18, seed=0, dur=0.5):
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for m in range(n_modes):
        f = base * (1 + m * 0.71 + r.random() * 0.4)
        y += np.sin(2 * np.pi * f * t + r.random() * 6) * np.exp(-t * decay * (1 + m * 0.4)) / (1 + m)
    y[:int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
    return y.astype(np.float32)

def scrape(dur, lo, hi, seed=0, rough=30):
    r = np.random.default_rng(seed); n = int(dur * SR)
    x = bp(r.standard_normal(n), lo, hi)
    am = np.abs(lp(r.standard_normal(n), rough, 2)); am /= am.max() + 1e-9
    return (x * (0.3 + am)).astype(np.float32)

def place(n_sec, items):
    out = np.zeros(int(n_sec * SR), np.float32)
    for at, x, g in items:
        i = int(at * SR); out[i:i + len(x)] += (x * g)[: len(out) - i]
    return out

files = {}
def make(name, x, peak, rt=1.4, wet=0.3, fout=0.4):
    y = stone(x, rt, wet) if rt else x
    y = fade(y, 0.0, fout)
    write(norm_peak(y, peak), name + '.mp3'); files[name] = name + '.mp3'

# heavy steps approaching behind the great door: muffled, growing
make('steps_approach', lp(steps([0, .8, 1.6, 2.35, 3.1], 1.3, [.35, .5, .65, .8, 1.0], 3), 900), -12, 1.0, .25)
# rattling chains: a cluster of small metallic strikes
ch = np.zeros(int(2.2 * SR), np.float32)
for j in range(34):
    at = 0.05 + 1.7 * (j / 34) ** 0.8 + 0.03 * rng.random()
    h = metal_hit(5, 1800 + 2600 * rng.random(), 22 + 20 * rng.random(), 100 + j, 0.3) * (0.4 + 0.6 * rng.random())
    i = int(at * SR); ch[i:i + len(h)] += h[: len(ch) - i]
ch += scrape(2.2, 1500, 6000, 7, 40) * 0.15
make('chains', ch, -11, 1.6, .35)
# massive bolts drawn back: an iron scrape, then a clunk
bolt = place(1.8, [(0.0, scrape(0.9, 300, 2200, 5, 18), .6),
                   (0.85, lp(seg('Springlocked_cellar_door', 4.0, 4.6), 2500), 1.0),
                   (0.85, metal_hit(4, 700, 14, 9, 0.6), .5)])
make('bolts', bolt, -10, 1.6, .35)
# a key turned with the loud grating noise of long disuse
k1 = stretch_pitch(seg('342706_spacejoe_lock-3-open-lock-3', 0, .3), 1.5)
k2 = stretch_pitch(seg('342618_spacejoe_lock-1-close-lock-3', 0, .9), 1.5)
make('key_turn', place(2.0, [(0, scrape(1.1, 250, 1800, 11, 12), .5), (0.9, k1, 1.0), (1.1, k2, .8)]), -11, 1.3, .3)
# one step over the threshold
make('step_threshold', steps([0], 1.2, None, 40), -14, 1.4, .3)
# the lamp set on its bracket
make('lamp_bracket', stretch_pitch(seg('Putting_down_thin_metal_object', 0, 1.0), 1.25), -15, 1.2, .3)
# luggage taken up, and set down
thud = seg('Dull_thud', 0, .4)
creak = seg('Creaky_wooden_casket', 0, 1.3)
make('luggage_lift', place(1.6, [(0, stretch_pitch(creak, 1.3)[: int(.7 * SR)], .25), (0.15, stretch_pitch(thud, 1.6), 1.0)]), -12, 1.2, .3)
make('luggage_down', place(1.4, [(0, stretch_pitch(thud, 1.7), 1.0), (0.32, stretch_pitch(thud, 1.4), .6)]), -12, 1.2, .3)
# up a great winding stair; steps ringing on a stone floor
make('stairs', steps([0, .55, 1.1, 1.62, 2.15, 2.68, 3.2, 3.75, 4.3, 4.85], 1.0, [.6, .7, .75, .8, .8, .85, .8, .75, .7, .6], 60), -12, 2.2, .45, 1.0)
make('steps_stone', steps([0, .7, 1.4, 2.1, 2.8, 3.5], 1.2, [.9, 1, .9, 1, .85, .7], 80), -11, 3.0, .5, 1.2)
# doors inside the castle
make('door_open', place(2.6, [(0, lp(seg('Springlocked_cellar_door', 6.4, 6.9), 3000), .8),
                              (0.3, stretch_pitch(creak, 1.8), .9)]), -10, 1.8, .35, .6)
make('door_close', seg('Closing_an_old_door', 2.9, 5.5), -10, 1.6, .3, .5)
# the fire: logs flaring; a hollow roar up the chimney
fl = lp(rng.standard_normal(int(3 * SR)), 1600, 2) * np.sin(np.linspace(0, np.pi, int(3 * SR))) ** 2
for j in range(18):
    h = hp(rng.standard_normal(int(.05 * SR)), 1500) * np.exp(-np.arange(int(.05 * SR)) / SR * 120)
    i = int((0.3 + 2.2 * rng.random()) * SR); fl[i:i + len(h)] += h * (0.5 + rng.random())
make('fire_flare', fl.astype(np.float32), -16, 1.0, .2, .8)
ro = lp(rng.standard_normal(int(4.5 * SR)), 220, 3) * np.sin(np.linspace(0, np.pi, int(4.5 * SR))) ** 1.5
make('fire_roar', ro.astype(np.float32), -14, 2.0, .3, 1.0)
# the letter opened
make('letter', seg('Turning_a_page', 1.1, 2.7), -16, 1.0, .2, .3)
# the cover taken off a dish; wine poured; a glass set down
make('dish_cover', place(1.4, [(0, seg('Putting_down_thin_metal_object', 0, .9), 1.0), (0.45, seg('Cutlery_on_table', 2.0, 2.6), .5)]), -15, 1.2, .25)
make('wine', place(5.0, [(0, seg('Pouring_wine', 4.8, 9.3), 1.0), (4.0, seg('Wine_glass', 4.8, 5.8), .6)]), -16, 1.0, .2, .6)
# a chair drawn up to the fire; a cigar lit
make('chair_draw', place(1.6, [(0, scrape(0.6, 120, 900, 31, 25), .7), (0.5, seg('Creaky_wooden_swivel_chair', 3.6, 4.3), .6)]), -14, 1.4, .3)
mt = place(1.4, [(0, scrape(0.18, 1500, 7000, 41, 60), 1.0),
                 (0.16, lp(rng.standard_normal(int(.9 * SR)), 2500) * np.exp(-np.arange(int(.9 * SR)) / SR * 4), .5)])
make('match', mt, -18, .8, .15)
# a shudder — a caught breath; and the Count sits again
make('shudder', seg('Three_sighs', 10.45, 11.3), -20, 1.0, .2, .3)
make('chair_creak', stretch_pitch(creak, 1.15)[: int(1.0 * SR)], -16, 1.4, .3)
import json; print(json.dumps(files))
