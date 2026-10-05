#!/usr/bin/env python3
"""THE VOYAGE OF THE DEMETER — a suite, after the captain's log. Amenti Studios · Dracula, chapter VII.

4/4 at 60 BPM, so the music and the heart share one pulse: the heart beats once a beat,
muffled, boom-boom, from the first bar to the last. 96 bars; the storm is the last third.

  bars  1–14  VARNA, 6 July — loading "silver sand and boxes of earth": dockers shouting,
              crates swung aboard, footsteps, the clerk with the manifest. D MAJOR.
  bars 15–24  "At noon set sail" — orders given and answered, the capstan, the anchor, sails.
  bars 25–28  The Bosphorus — the customs officer; backsheesh.
  bars 29–32  14 July — the crew crossing themselves; the mate loses his temper and strikes
              a man. Shouting. The music turns: G minor, then B flat.
  bars 33–36  "Expected fierce quarrel, but all was quiet." Calm.
  bars 37–44  16 July — Petrofsky missing. Murmuring below decks; prayers. D minor.
  bars 45–52  The search, stem to stern, with lanterns; "men much relieved." Calm.
  bars 53–56  24–29 July — another man gone; the round robin; shouting, a quarrel.
  bars 57–60  3 August — the mate gone mad: the knife, the hammering in the hold, the scream,
              and he leaps into the sea.
  bars 61–64  4 August — calm; fog; the captain alone at the wheel.
  bars 65–88  THE STORM — the last third. Wind, rain, thunder, timpani, low brass; the heart racing.
  bar  89     THE WRECK — a hard cut. The sea; the captain's heart slowing to its last beat; a dog howls.

v3 (6 Oct 2026) — the first voice now comes at ~0:30; the opening half-minute is the harbour alone.
v2 (6 Oct 2026) — the voices, on the log's own timeline; the synthesized creak (it croaked
like a frog) replaced by real wood: the PD "Creaky wooden casket" slowed into big timbers,
a door-handle creak slowed into a rope under strain.

Voices: the Amenti voice service (Gemini prebuilt voices) — dockers, crew, a Turkish customs
officer, the Roumanian mate, the captain. Instruments: VSCO 2 Community Edition (CC0).
Recordings: the Dracula hull, wreck, hammering, steps, luggage; the Treasure Island docks,
capstan, anchor, bosun's pipe, sails, gulls, watch bell, splash; the Romeo and Juliet blade;
wind and thunder from Wikimedia Commons (CC0 / PD). Deterministic (seed 1893)."""
import os, re, glob, json, subprocess
exec(open('/tmp/qv/prod/qv_score.py').read().split('# ═══ OPULENCE')[0].replace("/tmp/qv/score/", "/tmp/dr/suite/"))
os.makedirs('/tmp/dr/suite', exist_ok=True)
rng = np.random.default_rng(1893)
def mp3(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
D = '/tmp/rd2/dracula/sound/'; T = '/tmp/rd2/treasure-island/sound/'
BPM = 60; BT = 60 / BPM; BAR = 4 * BT; BARS = 96
LEN = BARS * BAR + 22; N = int(LEN * SR)
def at(bar, beat=0.0): return (bar - 1) * BAR + beat * BT
def env_lin(n, pts):                                     # piecewise gain over the whole piece, by bar
    x = np.zeros(n, np.float32); tt = np.arange(n) / SR
    xs = [at(b) for b, _ in pts]; ys = [g for _, g in pts]
    return np.interp(tt, xs, ys).astype(np.float32)
def tile(x, n=N): return np.tile(x, int(np.ceil(n / len(x))))[:n]
WRECK = at(89); STORM = 65

# ═══ THE HEART — muffled, boom-boom on every beat; doubles in the storm; slows and stops at the end ═══
heart = np.zeros(N, np.float32)
def thump(f0, dur, g):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * (f0 + 18 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)
    return lp(y.astype(np.float32), 160) * g
LUB, DUB = thump(52, 0.34, 1.0), thump(46, 0.28, 0.62)
t_ = at(1)
while t_ < WRECK:
    racing = at(57) <= t_ < at(61) or t_ >= at(STORM)
    if racing:
        put(heart, LUB, t_, 1.1); put(heart, DUB, t_ + 0.17, 0.7); t_ += BT / 2; continue
    put(heart, LUB, t_); put(heart, DUB, t_ + 0.24); t_ += BT     # steady: one heartbeat per beat
t_ = WRECK + 2 * BT; gap = BT
for k in range(14):                                      # the captain alone: slowing, fainter, then the last beat
    g = 0.95 - k * 0.05
    put(heart, LUB, t_, g); put(heart, DUB, t_ + 0.26, g * 0.6)
    t_ += gap; gap *= 1.13
last_beat = t_
heart = reverb(heart, 0.9, 0.15, seed=1)

# ═══ THE SHIP — real timbers working as she rolls: port on beat 2, starboard on beat 4 ═══
import scipy.signal as sgl
_cas = load('/tmp/snd/w_Creaky_wooden_casket.wav'); _door = load('/tmp/snd/Door_handle_creaking.wav')
def timber(slow, g):
    a0 = int(rng.random() * max(1, len(_cas) - int(0.9 * SR))); seg = _cas[a0: a0 + int(0.9 * SR)]
    seg = sgl.resample(seg, int(len(seg) * slow)).astype(np.float32)                 # slowed: bigger, lower timbers
    seg = lp(hp(seg, 70), 1500); n = len(seg)
    return (seg * np.sin(np.pi * np.arange(n) / n) ** 0.8 * g).astype(np.float32)
def rope(g):
    a0 = int(rng.random() * max(1, len(_door) - int(1.2 * SR))); seg = _door[a0: a0 + int(1.2 * SR)]
    seg = sgl.resample(seg, int(len(seg) * 2.4)).astype(np.float32); seg = lp(hp(seg, 90), 1200); n = len(seg)
    return (seg * np.sin(np.pi * np.arange(n) / n) * g).astype(np.float32)
ship = np.zeros(N, np.float32)
for b in range(1, 89):
    sway = 1.0 if b < STORM else 1.3
    put(ship, timber(1.7 + 0.5 * rng.random(), 0.9 * sway), at(b, 1) - 0.25)          # port
    put(ship, timber(2.1 + 0.5 * rng.random(), 0.75 * sway), at(b, 3) - 0.25)         # starboard
    if b % 4 == 2: put(ship, rope(0.5 * sway), at(b, 2.5))                           # a rope under strain
ship = reverb(ship, 0.9, 0.2, seed=2) * env_lin(N, [(1, 1), (64, 1), (65, 1.2), (88.99, 1.3), (89, 0), (97, 0)])
hull = tile(mp3(D + 'hull.mp3')) * env_lin(N, [(1, 0.8), (24, 0.9), (64, 1.0), (65, 1.1), (88.99, 1.2), (89, 0.8), (97, 0.7)])

# ═══ THE HARBOUR — dock workers muffled through the timbers, gulls; fading as she shoves off ═══
docks = lp(tile(mp3(T + 'docks.mp3')), 1400) * env_lin(N, [(1, 1), (15, 1), (20, 0.5), (23, 0), (97, 0)])
crowd = lp(tile(load('/tmp/qv/src/360703_eguobyte_large-crowd-medium-distance-stereo_m.wav')), 900) * env_lin(N, [(1, 1), (15, 0.9), (20, 0.3), (23, 0), (97, 0)])
fx = np.zeros(N, np.float32)
gull = mp3(T + 'gull.mp3')
for b, g in ((2, 0.5), (6, 0.35), (10, 0.45), (13, 0.3), (17, 0.25), (21, 0.15)): put(fx, gull * g, at(b, 2.3))
lift, down = mp3(D + 'luggage_lift.mp3'), mp3(D + 'luggage_down.mp3'); steps = mp3(D + 'steps_approach.mp3')
for b in (2, 4, 6, 8, 10, 12): put(fx, lift * 0.5, at(b, 0.5)); put(fx, down * 0.6, at(b, 2.2))        # crates swung aboard
for b in (3, 7, 11, 16, 20, 46, 48): put(fx, steps * 0.35, at(b, 1))                               # men moving about
n_ = int(5 * SR); put(fx, (bp(rng.standard_normal(n_), 2500, 9000) * np.sin(np.pi * np.arange(n_) / n_) * 0.05).astype(np.float32), at(9))  # sand pouring into the hold
put(fx, mp3(T + 'bell-watch.mp3') * 0.35, at(15))                                   # the watch bell: all aboard
put(fx, mp3(T + 'bosun-pipe.mp3') * 0.4, at(16, 2))
put(fx, mp3(T + 'capstan.mp3') * 0.55, at(18))                                      # the anchor comes up
put(fx, mp3(T + 'anchor-birds.mp3') * 0.4, at(20))
for b in (22, 23, 24): put(fx, mp3(T + 'flag-snap.mp3') * 0.35, at(b, 0.5))         # sails fill
put(fx, lp(mp3(D + 'luggage_down.mp3'), 1800) * 0.9, at(31, 1.15))                  # the blow
# ═══ THE LOSSES — no storm: a muffled snare ruff and the bell, far off, every two bars ═══
SN = '/tmp/vsco/VSCO 1 Percussion/drums/snare/drum1/'
snare = [load16(SN + f) for f in ('snare1_mp_1.wav', 'snare1_mp_2.wav', 'snare1_p_1.wav')]
bell = lp(mp3(T + 'bell-watch.mp3'), 900)
losses = []
for b in (36, 52, 54, 62):
    for k in range(5): put(fx, snare[k % 3] * (0.25 + 0.12 * k), at(b, 3) - 0.3 + k * 0.06)    # the ruff, into the downbeat
    put(fx, snare[0] * 0.9, at(b + 1)); put(fx, bell * 0.32, at(b + 1, 0.05)); losses.append(b + 1)
# ═══ THE STORM — the last third ═══
wind = tile(load('/tmp/snd/src3/Howling_wind.wav')) * env_lin(N, [(1, 0), (60, 0), (64, 0.12), (66, 0.35), (78, 0.8), (88.99, 1.0), (89, 0), (97, 0)])
rain = (bp(rng.standard_normal(N).astype(np.float32), 1200, 7000) * env_lin(N, [(1, 0), (68, 0), (72, 0.5), (88.99, 0.9), (89, 0), (97, 0)]))
th = load('/tmp/snd/th/Storm_thunderbolts.wav')
envt = np.array([np.sqrt(np.mean(th[i:i + 4800] ** 2)) for i in range(0, len(th) - 4800, 4800)])
pk = int(np.argmax(envt)) * 4800; bolt = th[max(0, pk - int(0.4 * SR)): pk + int(5 * SR)]
for b, g in ((70, 0.35), (74, 0.5), (78, 0.65), (82, 0.8), (85, 0.9), (87, 1.0)): put(fx, bolt * g, at(b, 0))
put(fx, mp3(D + 'lightning-depths.mp3') * 0.8, at(84))
swish = mp3('/tmp/rd2/romeo-and-juliet/sound/sword-swish.mp3')
for bb in (58.5, 58.8, 59.15): put(fx, lp(swish, 3500) * 0.5, at(int(bb), (bb % 1) * 4))       # the knife driven into the air
put(fx, lp(mp3(D + 'hammering.mp3'), 1500) * 0.6, at(59, 2))                                     # knocking at the boxes in the hold
put(fx, mp3(T + 'body-water.mp3') * 0.8, at(61))                                                 # he throws himself into the sea
put(fx, mp3(D + 'wreck-hit.mp3') * 1.2, WRECK)                                     # she drives onto the sands at Whitby
put(fx, mp3(D + 'wolf-howl.mp3') * 0.22, last_beat + 2.5)                           # the dog that leapt ashore

# ═══ THE MUSIC ═══
C_ = lambda r, q: (r, q)          # root (bass MIDI) + triad (MIDI)
Dm_, D_, G_, Gm_, A_, Bm_, Em_, Bb_, Eb_ = (38, [62, 66, 69]), (38, [62, 66, 69]), (43, [62, 67, 71]), (43, [62, 67, 70]), (45, [61, 64, 69]), (47, [62, 66, 71]), (40, [64, 67, 71]), (46, [62, 65, 70]), (39, [63, 67, 70])
Dm_ = (38, [62, 65, 69])
PROG = ([D_, D_, G_, D_, Bm_, G_, A_, A_, D_, D_, G_, D_, Em_, A_] +          # 1–14   Varna, D major
        [D_, G_, D_, A_, D_, G_, A_, D_, G_, A_] +                               # 15–24  under way
        [D_, Bm_, G_, A_] +                                                      # 25–28  the Bosphorus
        [D_, Gm_, D_, Bb_] +                                                     # 29–32  the blow: the turn
        [Dm_, Gm_, A_, Dm_] +                                                    # 33–36  all quiet
        [Dm_, Bb_, Gm_, A_, Dm_, Eb_, Dm_, A_] +                                 # 37–44  murmuring
        [Dm_, Bb_, Gm_, A_, Dm_, A_, Dm_, Dm_] +                                 # 45–52  the search; calm
        [Dm_, Eb_, Dm_, A_] +                                                    # 53–56  shouting
        [Eb_, Dm_, Eb_, A_] +                                                    # 57–60  the mate
        [Dm_, Bb_, Gm_, A_] +                                                    # 61–64  fog
        [Dm_, Eb_, Dm_, Eb_, Bb_, A_] * 4)                                      # 65–88  the storm
assert len(PROG) == 88
strings, horns, low, flute, oboe, viol, timp = (np.zeros(N, np.float32) for _ in range(7))
for i, (root, tri) in enumerate(PROG):
    b = i + 1; t0 = at(b)
    storm = b >= STORM
    put(low, sustain(CEL, root, BAR + 0.5, head=0.4, kx=0.4, tail=0.8), t0, 0.7 if not storm else 0.9)
    for m in tri: put(strings, sustain(VLA if m < 66 else VLN, m, BAR + 0.6, head=0.5, kx=0.5, tail=1.0), t0, 0.32 if b < 33 else 0.38)
    if 15 <= b < STORM and not (29 <= b < 37) and not (57 <= b < 65):                   # under way: violas in quavers
        for k in range(8): put(viol, sustain(VLA, [tri[0], tri[2], tri[1], tri[2]][k % 4] - 12, BT / 2 * 0.85, head=0.05, kx=0.03, tail=0.05), t0 + k * BT / 2, 0.45 if b < 33 else 0.35)
    if storm:
        for m in (root + 12, tri[0] - 12, tri[2] - 12): put(horns, sustain(TBN if m < 50 else HORN, m, BAR + 0.4, head=0.3, kx=0.3, tail=0.5), t0, 0.55 + 0.02 * (b - 49))
        tr = load16(TIMPR(2 if b % 2 else 3)); n_ = min(len(tr), int(BAR * SR))
        put(timp, tr[:n_] * np.linspace(0.3, 1.0, n_).astype(np.float32), t0, 0.5 + 0.02 * (b - STORM))
# the sea tune — flute in the major, oboe once it has turned
TUNE = [(0, 69, 2), (2, 71, 1), (3, 69, 1), (4, 66, 2), (6, 64, 2), (8, 66, 3), (11, 62, 1), (12, 64, 4)]
for start in (5, 9, 17, 21):
    for st, m, d in TUNE: put(flute, sustain(FLNV, m + 12 if start >= 17 else m, d * BT * 1.02, head=0.12, kx=0.1, tail=0.2), at(start) + st * BT, 0.42)
TUNE_M = [(0, 69, 2), (2, 70, 1), (3, 69, 1), (4, 65, 2), (6, 64, 2), (8, 65, 3), (11, 62, 1), (12, 61, 4)]
for start in (37, 41, 45, 61):
    for st, m, d in TUNE_M: put(oboe, sustain(OBOE, m, d * BT * 1.02, head=0.12, kx=0.1, tail=0.2), at(start) + st * BT, 0.42)
# the end: after the wreck, one long low D under the sea and the slowing heart
put(low, sustain(CEL, 38, last_beat - WRECK, head=2.5, kx=1.0, tail=3.0), WRECK + 1.0, 0.45)
for x in (strings, horns, low, flute, oboe, viol, timp):                                # the hard cut at the wreck
    cut = int(WRECK * SR); x[cut: cut + int(0.04 * SR)] *= np.linspace(1, 0, int(0.04 * SR)); x[cut + int(0.04 * SR):] *= (x is low)
music = stems((reverb(strings, 2.6, 0.3, seed=11), -27), (reverb(low, 2.4, 0.28, seed=12), -27), (reverb(viol, 1.8, 0.22, seed=13), -31),
              (reverb(flute, 2.4, 0.32, seed=14), -29), (reverb(oboe, 2.4, 0.32, seed=15), -29), (reverb(horns, 2.8, 0.3, seed=16), -27), (reverb(timp, 2.2, 0.3, seed=17), -29))
music *= env_lin(N, [(1, 0), (2, 0.8), (3, 0.85), (14, 0.85), (15, 1), (28, 1), (29, 0.7), (33, 0.8), (37, 0.9), (52, 0.9), (53, 0.65), (61, 0.8), (64, 0.9), (65, 1.05), (88.99, 1.3), (89, 1), (97, 1)])
# ═══ THE VOICES — placed on the log's timeline; each given its place: quay, deck, below, close ═══
VX = '/tmp/dem/vox/'
def place_v(x, where):
    if where == 'quay':  return reverb(lp(x, 3800), 1.2, 0.32, seed=7) * 0.8
    if where == 'deck':  return reverb(lp(x, 6000), 0.8, 0.18, seed=8)
    if where == 'below': return reverb(lp(hp(x, 180), 1900), 1.0, 0.35, seed=9) * 0.7
    if where == 'far':   return reverb(lp(x, 2200), 1.6, 0.45, seed=10) * 0.5
    if where == 'close': return reverb(lp(x, 7000), 0.4, 0.08, seed=11) * 0.9
    return x
VO = [  # (line, bar, beat, place, gain)
 # the first half-minute is the harbour alone — ship, water, the quay, the heart; the first voice at ~0:30
 ('d4', 8, 2.0, 'quay', 1.0), ('d1', 9, 0.5, 'quay', 1.0), ('d2', 9, 3.0, 'quay', 0.9), ('d3', 10, 2.0, 'quay', 0.9),
 ('d6', 11, 0.5, 'quay', 0.8), ('d5', 11, 3.0, 'quay', 0.9), ('d4', 12, 2.0, 'far', 0.7), ('d7', 13, 0.0, 'quay', 0.9), ('d8', 13, 3.0, 'deck', 0.75),
 ('c1', 15, 0.5, 'deck', 1.0), ('a1a', 16, 0.2, 'deck', 0.9), ('a1b', 16, 0.45, 'far', 0.9),
 ('c2', 17, 0.5, 'deck', 1.0), ('a2', 18, 0.0, 'far', 0.9), ('c3', 21, 0.0, 'deck', 1.0), ('a3', 21, 3.0, 'far', 1.0),
 ('c4', 22, 2.0, 'deck', 1.0), ('a4', 23, 2.5, 'far', 0.9), ('c5', 24, 0.5, 'deck', 0.8), ('a5', 25, 0.0, 'deck', 0.7),
 ('k1', 25, 2.0, 'deck', 0.9), ('k2', 26, 1.5, 'deck', 0.85), ('k3', 27, 2.5, 'deck', 0.85),
 ('m1', 29, 0.5, 'deck', 1.0), ('m2', 30, 0.5, 'deck', 0.8), ('m3', 30, 3.0, 'deck', 1.1), ('m4', 31, 1.2, 'deck', 0.9), ('m5', 31, 2.6, 'deck', 1.0),
 ('p1', 38, 0.0, 'below', 0.8), ('p3', 39, 1.0, 'below', 0.9), ('p2', 40, 2.0, 'below', 0.7), ('p4', 41, 1.5, 'below', 0.9), ('p1', 43, 0.0, 'below', 0.6),
 ('s1', 45, 0.5, 'deck', 1.0), ('s2a', 46, 0.5, 'below', 1.0), ('s2b', 47, 0.0, 'far', 0.9), ('s3', 48, 1.0, 'below', 1.0), ('s4', 49, 0.5, 'below', 0.9),
 ('x1', 53, 0.3, 'deck', 1.1), ('x5', 53, 3.0, 'deck', 1.0), ('x2', 54, 2.0, 'deck', 1.0), ('x3', 55, 1.5, 'deck', 1.1), ('x4', 56, 1.0, 'deck', 1.1),
 ('h1', 57, 0.5, 'close', 0.9), ('h2', 58, 0.2, 'close', 1.0), ('h3', 60, 0.0, 'deck', 1.2), ('h4', 60, 2.0, 'deck', 1.0), ('h5', 60, 3.6, 'deck', 1.1),
 ('e1', 62, 1.0, 'close', 0.8),
]
voices = np.zeros(N, np.float32); missing = []
for k, b, bt, where, g in VO:
    f = VX + k + '.wav'
    if not (os.path.exists(f) and open(f, 'rb').read(4) == b'RIFF'): missing.append(k); continue
    put(voices, place_v(load(f), where) * g, at(b, bt))
mix = (music + at_rms(voices, -27) + at_rms(heart, -30) + at_rms(ship, -33) + at_rms(hull, -36) + at_rms(docks, -37) + at_rms(crowd, -42)
       + at_rms(fx, -30) + at_rms(wind, -31) + at_rms(rain, -38))
end = int((last_beat + 9) * SR); mix = mix[:end]
mix[-int(5 * SR):] *= np.linspace(1, 0, int(5 * SR))
mix = mix / (np.abs(mix).max() + 1e-9) * 10 ** (-1.5 / 20)
write_mp3(mix.astype(np.float32), 'voyage-of-the-demeter.mp3')
print('length', round(len(mix) / SR, 1), 's · wreck at', round(WRECK, 1), 's · last heartbeat', round(last_beat, 1), 's · losses at bars', losses, '· voices missing:', sorted(set(missing)))
