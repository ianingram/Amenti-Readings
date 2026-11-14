#!/usr/bin/env python3
"""The ship, the island and the map as players · 14 Nov 2026.

Ian's list for Treasure Island: "rustling of sails, straining and twisting of ropes,
creaking of wood, distant voices, wind, the swaying of trees in the wind as opposed to
just wind ... campfires ... the unfolding and spreading out of the map", inland birds
"at various times of the day, on a tropical island", surf that never sounds repeated,
the clamour of feet on the deck. Like the gulls, each is a set of short players cut
from real recordings, so place-players.py can scatter them by script and nothing loops.

Sources: BigSoundBank (Joseph Sardin), all CC0, by number (see SOURCES.md).
usage: build-players.py <folder of bsb-NNNN.mp3> [out dir]
"""
import sys, os, subprocess, json
import numpy as np, scipy.signal as sg
from scipy.ndimage import uniform_filter1d
SRC = sys.argv[1].rstrip('/') + '/'
OUT = (sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))).rstrip('/') + '/'
SR = 44100

def load(n):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', SRC + 'bsb-%s.mp3' % n, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def band(x, lo, hi): return sg.sosfilt(sg.butter(4, [lo, hi], 'band', fs=SR, output='sos'), x).astype(np.float32)
def lp(x, f): return sg.sosfilt(sg.butter(2, f, 'low', fs=SR, output='sos'), x).astype(np.float32)
def hp(x, f): return sg.sosfilt(sg.butter(2, f, 'high', fs=SR, output='sos'), x).astype(np.float32)
def env_db(x, win=0.05):
    e = np.sqrt(uniform_filter1d((x.astype(np.float64)) ** 2, max(1, int(win * SR))) + 1e-12); return 20 * np.log10(e)
def fade(x, a=0.05, r=0.4):
    x = x.copy(); a = min(int(a * SR), len(x) // 3); r = min(int(r * SR), len(x) // 3)
    if a: x[:a] *= np.linspace(0, 1, a) ** 1.5
    if r: x[-r:] *= np.linspace(1, 0, r) ** 1.5
    return x
def reverb(x, rt, wet, seed=3):
    r = np.random.default_rng(seed); n = int(rt * SR); t = np.arange(n) / SR
    ir = lp(r.standard_normal(n).astype(np.float32) * np.exp(-6.91 * t / rt).astype(np.float32), 5000); ir /= np.sqrt(np.sum(ir ** 2))
    y = np.concatenate([x, np.zeros(n, np.float32)])
    return ((1 - wet) * y + wet * sg.fftconvolve(y, ir)[:len(y)]).astype(np.float32)
def at(x, dist, room=0.0):
    """dist 0 (close) .. 1 (far): darker, more air, quieter; room adds a wooden-hold reverb"""
    y = lp(x, 9000 - 7200 * dist) if dist > 0 else x
    if dist > 0: y = reverb(y, 0.8 + 1.6 * dist, 0.1 + 0.45 * dist, seed=int(dist * 100))
    if room: y = reverb(y, 0.5, room, seed=7)
    return y * (1 - 0.7 * dist)
def rms_db(x):
    e = env_db(x, 0.3); loud = e[e > e.max() - 20]; return float(np.mean(loud)) if len(loud) else -90
def write(x, name, target):
    """level by the loud part of the sound (not its quiet tail), so sets sit together"""
    g = 10 ** ((target - rms_db(x)) / 20); y = x * g
    pk = np.abs(y).max()
    if pk > 0.89: y *= 0.89 / pk
    raw = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', OUT + name + '.mp3'],
                   input=raw, check=True)
    MADE.append({'file': name + '.mp3', 'sec': round(len(y) / SR, 1)})
MADE = []

def events(x, lo, hi, n, pre=0.25, minl=0.6, maxl=4.0, drop=14, sep=1.5, skip=()):
    """the n strongest separate events in a band: (start, end) samples"""
    e = env_db(band(x, lo, hi), 0.04); hop = int(0.01 * SR); es = e[::hop]
    pk, pr = sg.find_peaks(es, prominence=6, distance=int(sep / 0.01))
    order = pk[np.argsort(-es[pk])]; out = []
    for p in order:
        if len(out) >= n: break
        i = p * hop; top = e[i]
        s = i
        while s > 0 and i - s < pre * 4 * SR and e[s] > top - drop: s -= hop
        s = max(0, s - int(pre * SR * 0.4))
        t = i
        while t < len(x) - hop and t - i < maxl * SR and e[t] > top - drop - 4: t += hop
        if (t - s) < minl * SR: t = min(len(x), s + int(minl * SR))
        if any(not (t < a or s > b) for a, b in out): continue
        if any(abs(i - k) < 2 * SR for k in skip): continue
        out.append((s, t))
    return sorted(out)
def windows(x, L, n, mode='peak', lo=200, hi=6000, sep=None):
    """n windows of L seconds: around the loudest swells ('peak') or the busiest ('busy')"""
    e = env_db(band(x, lo, hi), 0.5); hop = int(0.1 * SR); es = e[::hop]
    if mode == 'busy': es = np.convolve(np.abs(np.diff(es, prepend=es[0])), np.ones(20) / 20, 'same')
    sep = sep or L * 1.2; out = []
    for p in np.argsort(-es):
        c = p * hop; s = int(np.clip(c - L * SR / 2, 0, max(0, len(x) - L * SR)))
        if any(abs(s - a) < sep * SR for a in out): continue
        out.append(s)
        if len(out) >= n: break
    return [(s, s + int(L * SR)) for s in sorted(out)]

def cut(x, se, a=0.05, r=0.5): return fade(x[se[0]:se[1]], a, r)

# ── the ship ────────────────────────────────────────────────────────────────
# creaking wood: timbers and knees working in a seaway (the boat decks, the cabin, a barn door slowed)
k = 0
for n, cnt, slow in (('0694', 2, 1.0), ('0697', 2, 1.0), ('0700', 1, 1.0), ('0769', 2, 0.85), ('0539', 1, 0.8)):
    x = load(n)
    if slow != 1.0: x = sg.resample_poly(x, int(100 / slow), 100).astype(np.float32)
    for se in events(x, 250, 2500, cnt, maxl=3.5, minl=1.0):
        k += 1; y = hp(cut(x, se, 0.03, 0.6), 90)
        write(at(y, 0.15, room=0.12), 'creak-%d' % k, -27)
N_CREAK = k
# ropes straining and twisting (mooring and halyard ropes under load)
k = 0
for n, cnt in (('3417', 2), ('3418', 1), ('3419', 2), ('3426', 1)):
    x = load(n)
    for se in events(x, 300, 4000, cnt, maxl=3.0, minl=1.2):
        k += 1; write(at(hp(cut(x, se, 0.04, 0.5), 120), 0.1), 'rope-%d' % k, -29)
N_ROPE = k
# sails: canvas rustling and filling (flags in the wind, the longer gusts), and snaps
k = 0
for n, cnt in (('1632', 3), ('1633', 2)):
    x = load(n)
    for se in windows(x, 6.0, cnt, 'peak', 300, 8000):
        k += 1; write(at(cut(x, se, 1.2, 1.8), 0.2), 'sail-%d' % k, -29)
for n in ('1789', '1793', '1794'):
    k += 1; write(at(fade(load(n), 0.005, 0.3), 0.25), 'sail-%d' % k, -27)
N_SAIL = k
# the rigging singing in the wind
k = 0
for n, cnt in (('2443', 2), ('2444', 1)):
    x = load(n)
    for se in windows(x, 9.0, cnt, 'peak', 400, 6000):
        k += 1; write(cut(x, se, 2.0, 2.5), 'rigging-%d' % k, -31)
N_RIG = k
# feet on the deck: one man, or the clamour of several (layered, offset)
k = 0
steps = [load(n) for n in ('0165', '1515', '1516', '1517', '1518', '0181', '3440')]
rnd = np.random.default_rng(1883)
for i in range(3):                               # single walkers
    x = steps[i + 1]; se = windows(x, 4.0, 1, 'busy', 150, 4000)[0]
    k += 1; write(at(cut(x, se, 0.05, 0.6), 0.2, room=0.1), 'feet-%d' % k, -27)
for i in range(3):                               # the clamour: three or four men at once
    L = 5.0; mix = np.zeros(int((L + 1) * SR), np.float32)
    for j in range(3 + i % 2):
        x = steps[(i * 2 + j) % len(steps)]; ws = windows(x, L, 3, 'busy', 150, 4000, sep=2.0); se = ws[j % len(ws)]
        y = cut(x, se, 0.05, 0.8); o = int(rnd.uniform(0, 0.8) * SR); mix[o:o + len(y)] += y[:len(mix) - o] * rnd.uniform(0.6, 1.0)
    k += 1; write(at(mix, 0.25, room=0.12), 'feet-%d' % k, -25)
N_FEET = k
# distant voices: men at work, heard across the water or the yard (never words)
k = 0
for n, cnt in (('2968', 2), ('2969', 1), ('2970', 2)):
    x = load(n)
    for se in windows(x, 7.0, cnt, 'peak', 300, 3000):
        k += 1; write(at(lp(cut(x, se, 1.5, 2.0), 1100), 0.75), 'voices-far-%d' % k, -36)
N_VOICES = k

# ── the island ──────────────────────────────────────────────────────────────
# trees swaying: a gust coming through the woods, swelling and passing
k = 0
for n, cnt in (('1450', 2), ('1451', 3), ('1452', 2), ('1051', 1)):
    x = load(n)
    for se in windows(x, 10.0, cnt, 'peak', 200, 5000, sep=20):
        k += 1; write(cut(x, se, 3.0, 3.5), 'trees-%d' % k, -29)
N_TREES = k
# birds by the time of day
BIRDS = {
    'dawn': (('0222', 2), ('0999', 2), ('1906', 2)),
    'day': (('2713', 2), ('2715', 1), ('2749', 2), ('1164', 2), ('1165', 1)),
    'dusk': (('1859', 3),),
    'night': (('0315', 3), ('0429', 1), ('1400', 1)),
}
NB = {}
for tod, srcs in BIRDS.items():
    k = 0
    for n, cnt in srcs:
        x = load(n)
        for se in windows(x, 8.0, cnt, 'busy', 1500, 9000, sep=15):
            k += 1; y = cut(x, se, 1.8, 2.2)
            write(at(y, 0.3 if tod != 'night' else 0.45), 'birds-%s-%d' % (tod, k), -31 if tod != 'night' else -33)
    NB[tod] = k
# a strange cry in the trees (the screaming piha, for the island's strangeness)
write(at(fade(load('1762'), 0.005, 0.2), 0.55), 'bird-cry-1', -30)
# insects: the noon heat (cicadas), and the night
k = 0
for n in ('1779', '1780', '1781'):
    x = load(n); se = windows(x, 9.0, 1, 'peak', 2000, 12000)[0]; k += 1
    write(cut(x, se, 2.5, 3.0), 'insects-day-%d' % k, -34)
N_INS_D = k; k = 0
for n in ('0425', '0426', '0110'):
    x = load(n); se = windows(x, 9.0, 1, 'peak', 2000, 12000)[0]; k += 1
    write(cut(x, se, 2.5, 3.0), 'insects-night-%d' % k, -35)
N_INS_N = k
# surf: single waves breaking and drawing back, so no two minutes sound alike
k = 0
for n, cnt in (('1445', 2), ('1446', 2), ('1448', 2), ('2564', 1), ('2566', 1), ('2572', 1)):
    x = load(n)
    for se in events(x, 150, 3000, cnt, pre=1.0, minl=4.0, maxl=8.0, drop=16, sep=6):
        k += 1; write(at(cut(x, se, 0.8, 2.0), 0.2), 'wave-%d' % k, -27)
N_WAVE = k

# ── the map ─────────────────────────────────────────────────────────────────
# chapter VI: the paper unfolded and spread out on the table (a big road map, opened)
m = load('2799'); se = (0, len(m)); y = cut(m, se, 0.02, 0.6)
write(at(y, 0.1, room=0.15), 'map-unfold', -24)
m2 = load('2796'); write(at(cut(m2, (0, len(m2)), 0.02, 0.5), 0.1, room=0.15), 'map-fold', -25)

# ── the horses at the start of the book ─────────────────────────────────────
# Ian: "galloping and stopping and galloping away, not just galloping"
arr = load('1848'); dep = load('1849'); snort = load('0285'); breath = load('0286'); trot = load('0610')
a = fade(arr[int(3.5 * SR):], 0.8, 0.15)                         # coming up the road, drawing up
stand = np.zeros(int(1.8 * SR), np.float32); stand[int(0.2 * SR):int(0.2 * SR) + len(snort)] += snort * 0.8
stand[int(1.1 * SR):int(1.1 * SR) + len(breath[:int(0.7 * SR)])] += breath[:int(0.7 * SR)] * 0.6
write(at(np.concatenate([a, stand, fade(dep, 0.01, 2.0)]), 0.2), 'horse-come-go', -24)
two = np.zeros(len(arr) + SR, np.float32); two[:len(arr)] += arr; two[int(0.37 * SR):int(0.37 * SR) + len(arr)] += arr * 0.8
write(at(fade(two[int(2.0 * SR):], 1.0, 0.3), 0.2), 'horses-arrive', -23)  # riders drawing up at a door
tr = np.zeros(len(trot) + 2 * SR, np.float32)
for i, (o, g) in enumerate(((0, 1.0), (0.29, 0.8), (0.61, 0.7), (1.03, 0.6))):
    tr[int(o * SR):int(o * SR) + len(trot)] += trot * g
tr = tr[:int(11 * SR)]; tr *= np.linspace(1, 0.05, len(tr)) ** 1.3       # the party trotting off down the road
write(at(fade(tr, 0.3, 1.5), 0.25), 'horses-trot-away', -24)

COUNTS = dict(creak=N_CREAK, rope=N_ROPE, sail=N_SAIL, rigging=N_RIG, feet=N_FEET, voices_far=N_VOICES,
              trees=N_TREES, birds_dawn=NB['dawn'], birds_day=NB['day'], birds_dusk=NB['dusk'], birds_night=NB['night'],
              insects_day=N_INS_D, insects_night=N_INS_N, wave=N_WAVE)
json.dump({'counts': COUNTS, 'made': MADE}, open(OUT + 'players.json', 'w'), indent=1)
print(COUNTS, '·', len(MADE), 'files')
