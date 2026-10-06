#!/usr/bin/env python3
"""Dracula — the last two cues of the score (6 Oct 2026).

EARTH BOXES (chapters 19–20). The hunters track the Count's fifty boxes of earth across
London — Carfax, Piccadilly, Mile End, Bermondsey. Industrial halftime at 60 BPM, and THE
CRATES ARE THE PERCUSSION: the kick is a heavy box set down on boards, the backbeat (beat 3,
halftime) is a lid prised and slammed, the ticking is earth trickling and a shovel's scrape,
with a hammer on the off-beats in the second half. Under it a low D pedal and the dread's
D–E♭ lean on cellos and violas. The only driving cue before the pursuit.

PURSUIT (chapters 26–27). The chase east to the castle before sunset. The only cue with a
true pulse: 132 BPM, a galloping string ostinato in D minor (violas and cellos in short
strokes, the rhythm of hooves), timpani on the downbeats, low brass climbing a fourth every
four bars, horses at the gallop underneath, and the wolves far off in the second half.

Instruments VSCO 2 CE (CC0). Recordings: the Dracula luggage, hammering, door, chains and
gallop sounds already in this folder; Dull thud (PD). Deterministic (seed 1897)."""
import os, json, subprocess
exec(open('/tmp/qv/prod/qv_score.py').read().split('# ═══ OPULENCE')[0].replace("/tmp/qv/score/", "/tmp/dr/cues/"))
os.makedirs('/tmp/dr/cues', exist_ok=True)
rng = np.random.default_rng(1897)
D = '/tmp/rd3/dracula/sound/'
def mp3(path):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                                        capture_output=True).stdout, np.float32).copy()
def onset(x, thresh=0.25, pre=0.01):                        # trim a recording to its first strong hit
    env_ = np.abs(x); k = int(np.argmax(env_ > thresh * env_.max())); return x[max(0, k - int(pre * SR)):]
def cut(x, dur, fade=0.03):
    y = x[: int(dur * SR)].copy(); n = int(fade * SR); y[-n:] *= np.linspace(1, 0, n); return y

# ═══ EARTH BOXES — industrial halftime, 60 BPM, the crates are the drums ═══════════════════
BT = 1.0; BAR = 4 * BT; bars = 16; N = int((bars * BAR + 4) * SR)
box = cut(onset(mp3(D + 'luggage_down.mp3')), 0.9)
thud = cut(onset(load('/tmp/snd/w_Dull_thud.wav')), 0.6)
def mix2(a, b):
    n = max(len(a), len(b)); y = np.zeros(n, np.float32); y[:len(a)] += a; y[:len(b)] += b; return y
KICK = mix2(lp(box, 400) * 1.0, lp(thud, 250) * 0.8)                         # a box set down on boards
lid = cut(onset(mp3(D + 'door_heavy.mp3')), 0.7)
SLAM = hp(lid, 120)                                                      # the lid slammed
ham = mp3(D + 'hammering.mp3'); HAM = cut(onset(ham), 0.25)
chn = mp3(D + 'chains.mp3'); CHAIN = cut(onset(chn), 1.2)
def trickle(dur, g):                                                     # earth running off a shovel
    n = int(dur * SR); y = bp(rng.standard_normal(n).astype(np.float32), 2500, 9000)
    grains = (rng.random(n) < 0.02).astype(np.float32); y = y * (0.3 + grains)
    return (y * np.sin(np.pi * np.arange(n) / n) * g).astype(np.float32)
perc, low, strings = (np.zeros(N, np.float32) for _ in range(3))
for b in range(bars):
    t0 = b * BAR
    put(perc, KICK, t0, 1.0)
    if b % 2 == 1: put(perc, KICK, t0 + 2.5 * BT, 0.55)                  # the second box, off the beat
    put(perc, SLAM, t0 + 2 * BT, 0.9)                                     # halftime backbeat on 3
    for k in range(8): put(perc, trickle(0.18, 0.18 if k % 2 else 0.28), t0 + k * BT / 2)
    if b >= 8:
        for k in (1, 3): put(perc, HAM, t0 + k * BT + 0.5, 0.45)          # a hammer on the off-beats
    if b in (7, 15): put(perc, CHAIN, t0 + 3 * BT, 0.5)
    put(low, sustain(CEL, 26 + 12, BAR + 0.5, head=0.4, kx=0.4, tail=0.6), t0, 0.8)   # the D pedal
    m = [62, 63][(b // 2) % 2]                                                          # the dread's D–E♭ lean
    if b % 2 == 0: put(strings, sustain(VLA, m - 12, BAR * 2 + 0.6, head=0.8, kx=0.6, tail=1.0), t0, 0.45)
    if b >= 8 and b % 4 == 0: put(strings, sustain(CEL, 50, BAR * 4, head=1.0, kx=0.8, tail=1.5), t0, 0.35)
mix = stems((reverb(perc, 1.6, 0.32, seed=1), -24), (reverb(low, 2.2, 0.25, seed=2), -28), (reverb(strings, 2.8, 0.3, seed=3), -31))
render('score-earth-boxes.mp3', mix[: int((bars * BAR + 2) * SR)], 3.0, -24)

# ═══ PURSUIT — 132 BPM, the gallop east before sunset ═══════════════════════════════════
BPM = 132; BT = 60 / BPM; BAR = 4 * BT; bars = 32; N = int((bars * BAR + 5) * SR)
TIMP = load16('/tmp/vsco/Percussion/Timpani/Timpani1_Hit_v1_rr1_Sum.wav')
gallop = mp3(D + 'horses-gallop.mp3'); wolves = mp3(D + 'wolf-howl.mp3')
ost, low, brass, tim, fx = (np.zeros(N, np.float32) for _ in range(5))
PROG = [(38, [62, 65, 69]), (38, [62, 65, 69]), (34, [62, 65, 70]), (36, [60, 64, 67]),
        (38, [62, 65, 69]), (39, [63, 67, 70]), (36, [60, 64, 67]), (33, [61, 64, 69])] * 4
GALLOP = [0, 0.5, 0.75, 2, 2.5, 2.75]                                     # da-da-DUM, da-da-DUM: hooves
for b, (root, tri) in enumerate(PROG):
    t0 = b * BAR; lift = 0 if b < 16 else 12 * (b >= 24)
    for k, st in enumerate(GALLOP):
        m = tri[k % 3] - 12 + lift
        put(ost, sustain(VLA, m, BT * 0.22, head=0.02, kx=0.02, tail=0.04), t0 + st * BT, 0.9 if st in (0, 2) else 0.6)
        put(ost, sustain(CEL, root + 12, BT * 0.22, head=0.02, kx=0.02, tail=0.04), t0 + st * BT, 0.7 if st in (0, 2) else 0.45)
    put(low, sustain(CEL, root, BAR + 0.2, head=0.2, kx=0.3, tail=0.3), t0, 0.6)
    put(tim, TIMP, t0, 0.9); put(tim, TIMP, t0 + 2 * BT, 0.6)
    if b % 4 == 0:                                                         # low brass climbing a fourth each phrase
        step = [0, 5, 7, 12, 5, 7, 12, 17][b // 4]
        put(brass, sustain(TBN, 38 + step, BAR * 3.8, head=0.4, kx=0.4, tail=0.6), t0, 0.6)
        put(brass, sustain(HORN, 50 + step, BAR * 3.8, head=0.5, kx=0.4, tail=0.6), t0 + BT, 0.45)
gl = np.tile(gallop, int(np.ceil(N / len(gallop))))[:N]
fx += lp(gl, 1500) * 0.5
for b in (17, 23, 29): put(fx, reverb(lp(wolves, 2500), 2.2, 0.5, seed=b) * 0.45, b * BAR)   # the wolves, far off
mix = stems((reverb(ost, 1.3, 0.2, seed=11), -24), (reverb(low, 1.8, 0.22, seed=12), -29), (reverb(brass, 2.4, 0.3, seed=13), -27),
            (reverb(tim, 2.0, 0.28, seed=14), -27), (fx, -32))
render('score-pursuit.mp3', mix[: int((bars * BAR + 2) * SR)], 2.0, -22)
json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:24s} {v_:6.2f}s')
