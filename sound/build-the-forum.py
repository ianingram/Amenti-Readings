#!/usr/bin/env python3
"""Julius Caesar — THE FORUM, the landing page's suite (7 Oct 2026), to Ian's design:

  a bustling crowd, a market place — voices, commands, orders, shuffling feet —
  then a rhythmic murmuring, loud coordinated cheers, a 4/4 beat;
  then French horns, and drums, slow and rhythmic;
  then a rise from the crowd, and a speech: "Friends, Romans, countrymen, lend me your ears."
  And it repeats, like the stanzas of a poem.

Three stanzas of sixteen bars at 80 BPM (a bar every three seconds), each a little stronger, each
ending on the next line of Antony's speech (Shakespeare, Julius Caesar III.ii):
    I    "Friends, Romans, countrymen, lend me your ears;"
    II   "I come to bury Caesar, not to praise him."
    III  "So let it be with Caesar."
  bars 1–4   MARKET   the crowd, street calls and commands, shuffling feet
  bars 5–8   RHYTHM   the murmur falls into the beat, feet and a low drum on every beat;
                      bar 8: the cheer — "Caesar! Caesar! Caesar!" — on the beats, and applause
  bars 9–12  HORNS    French horns over slow, rhythmic drums (timpani on one and three)
  bars 13–14 RISE     the crowd swells, a timpani roll, a citizen: "Peace, ho! Let us hear him."
  bars 15–16 SPEECH   the music and the crowd fall back; Antony speaks
After the third stanza a last cheer and the brass, and the Forum empties.

Crowd: Quo Vadis's rome-street, applause and cheer (PD/CC0, see SOURCES.md). Voices: the Amenti
speech engine — Antony in Mark Antony's ledger voice (classical Latin, swaggering and generous;
warm and persuasive), the citizens and the chant in six rough Roman voices. Instruments VSCO 2 CE
(CC0). Footsteps synthesized. Seed 44."""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jc_kit import *
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
QV = '/tmp/claude-0/-home-claude/c002dc02-d023-5c73-9437-2a1012982e23/scratchpad/rd/quo-vadis/sound/'
rng = np.random.default_rng(44)
def aud(path):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                                        capture_output=True).stdout, np.float32).copy()
def vox(k):
    x = aud(HERE + 'vox/' + k + '.wav'); a = np.abs(x); thr = 0.02 * a.max()
    i = int(np.argmax(a > thr)); j = len(x) - int(np.argmax(a[::-1] > thr))
    return x[max(0, i - 800): j + 2400]
def env_lin(n, pts):
    xs = [p[0] * SR for p in pts]; ys = [p[1] for p in pts]
    return np.interp(np.arange(n), xs, ys).astype(np.float32)

HORN = bank('Brass/F Horn/sus/*_v2_1.wav', r'sus_([A-G]#?\d)_')
TBN = bank('Brass/Tenor Trombone/sus/*_v2_1.wav', r'sus_([A-G]#?\d)_')
TUBA = bank('Brass/Tuba/sus/*_v2_rr1_Mid.wav', r'sus_([A-G]#?\d)_')
CEL = bank('Strings/Cello Section/susvib/*_v1_1.wav', r'susvib_([A-G]#?\d)_')
P = V + 'Percussion/'
TIMP = [load16(P + f'Timpani/Timpani{i}_Hit_v3_rr1_Sum.wav') for i in (1, 2, 3)]
TIMPR = load16(P + 'Timpani/Rolls/Timpani1_Roll_v5_rr1_Sum.wav')
BD = load16(P + 'BDrumNewhit_v5_rr1_Sum.wav')

BPM = 80; BT = 60 / BPM; BAR = 4 * BT; STZ = 16; NST = 3
END = NST * STZ * BAR + 4 * BAR                     # three stanzas and a coda of four bars
N = int((END + 6) * SR)
def at(stanza, bar, beat=0.0): return (stanza * STZ + bar - 1) * BAR + beat * BT

crowd, calls, feet, beat, chant, horns, drums, rise, speech = (np.zeros(N, np.float32) for _ in range(9))

# ── the crowd: the Roman street, looped under everything, its level drawn stanza by stanza ──
street = aud(QV + 'rome-street.mp3'); applause = aud(QV + 'applause.mp3'); cheer = aud(QV + 'cheer.mp3')
crowd[:] = np.tile(street, int(np.ceil(N / len(street))))[:N]
pulse = np.zeros(N, np.float32)                     # the murmur falling into the beat
tb = np.arange(int(BT * SR)) / SR; one = (0.55 + 0.45 * np.exp(-tb * 5)).astype(np.float32)
lvl = []
for s in range(NST):
    g = 1 + 0.18 * s
    lvl += [(at(s, 1), 0.9 * g), (at(s, 4.6), 0.9 * g), (at(s, 5), 0.85 * g), (at(s, 8.9), 1.0 * g), (at(s, 9), 0.55 * g),
            (at(s, 12.9), 0.55 * g), (at(s, 13), 0.7 * g), (at(s, 14.8), 1.25 * g), (at(s, 15.1), 0.22), (at(s, 16.9), 0.3)]
lvl += [(at(NST, 1), 1.2), (at(NST, 3), 1.0), (END + 4, 0.0)]
crowd *= env_lin(N, [(0, 0.0), (2.5, 0.9)] + lvl)
for s in range(NST):                                 # bars 5–8: the murmur breathes on the beat
    for k in range(16):
        t0 = int(at(s, 5, k) * SR); seg = crowd[t0:t0 + len(one)]
        crowd[t0:t0 + len(seg)] = seg * one[:len(seg)]

# ── the market: calls and commands, two or three a stanza, never on top of one another ──
MARKET = [['m2', 'm1', 'm3'], ['m5', 'm4', 'm2'], ['m3', 'm6', 'm5']]
for s, ks in enumerate(MARKET):
    for i, k in enumerate(ks):
        v = vox(k); pan_t = at(s, 1, 1.5 + i * 4.3) + rng.uniform(-0.3, 0.3)
        put(calls, reverb(v, 1.2, 0.3, seed=30 + i) * (0.8 if i != 1 else 1.0), pan_t)

# ── the feet: shuffling, then marching the beat ──
def step(g, dark=1800):
    n = int(0.09 * SR); x = bp(rng.standard_normal(n).astype(np.float32), 180, dark)
    return (x * np.exp(-np.arange(n) / SR * 38) * g).astype(np.float32)
def stomp(g):
    n = int(0.16 * SR); x = lp(rng.standard_normal(n).astype(np.float32), 260) * 3 + bp(rng.standard_normal(n).astype(np.float32), 900, 2500) * 0.4
    return (x * np.exp(-np.arange(n) / SR * 24) * g).astype(np.float32)
for s in range(NST):
    t = at(s, 1)
    while t < at(s, 5): put(feet, step(rng.uniform(0.25, 0.6)), t); t += rng.uniform(0.07, 0.3)     # many feet, no order
    for k in range(16):                                                                            # then in step
        put(feet, stomp(0.8 + 0.2 * (k % 4 == 0)), at(s, 5, k))
        for d in range(5): put(feet, step(0.25), at(s, 5, k) + rng.uniform(0.0, 0.08))
        put(beat, lp(BD, 220), at(s, 5, k), 0.75 if k % 4 == 0 else 0.5)

# ── the cheer: six voices on the beat, "Caesar! Caesar! Caesar!", with applause behind ──
for s in range(NST):
    t0 = at(s, 8)
    for i, k in enumerate(['c1', 'c2', 'c3', 'c4', 'c5', 'c6']):
        put(chant, reverb(vox(k), 1.4, 0.35, seed=40 + i), t0 + rng.uniform(-0.05, 0.05), 0.7 + 0.1 * s)
    put(chant, applause[: int(6 * SR)], t0 + 0.6, 0.6 + 0.15 * s)
    put(chant, cheer, t0 + BAR * 0.75, 0.5 + 0.15 * s)

# ── the horns, over slow and rhythmic drums ──
HT = [(0, 67, 2), (2, 70, 1), (3, 69, 1), (4, 67, 2), (6, 62, 2), (8, 63, 3), (11, 65, 1), (12, 62, 4)]
LOWB = [(43, [55, 58, 62]), (39, [55, 58, 63]), (41, [53, 57, 60]), (38, [50, 54, 57])]
for s in range(NST):
    up = 0 if s < 2 else 5                                                        # the third stanza lifts a fourth
    for st, m, d in HT:
        put(horns, sustain(HORN, m - 12 + up, d * BT * 1.02 + 0.3, head=0.15, kx=0.2, tail=0.4), at(s, 9, st), 0.6 + 0.12 * s)
        if s > 0: put(horns, sustain(HORN, m - 24 + up + 7, d * BT * 1.02 + 0.3, head=0.15, kx=0.2, tail=0.4), at(s, 9, st), 0.3)
    for b, (root, tri) in enumerate(LOWB):
        put(horns, sustain(TUBA, root - 12 + up, BAR + 0.4, head=0.4, kx=0.4, tail=0.6), at(s, 9 + b), 0.45)
        for m in tri: put(horns, sustain(TBN, m - 12 + up, BAR + 0.3, head=0.4, kx=0.4, tail=0.6), at(s, 9 + b), 0.18)
        put(drums, TIMP[b % 2], at(s, 9 + b), 1.0); put(drums, TIMP[2], at(s, 9 + b, 2), 0.7)
        put(drums, lp(BD, 260), at(s, 9 + b), 0.6); put(drums, lp(BD, 260), at(s, 9 + b, 3.5), 0.3)

# ── the rise, and the citizen calling for quiet ──
PEACE = ['p1', 'p2', 'p1']
for s in range(NST):
    put(rise, TIMPR[: int(2 * BAR * SR)] * np.linspace(0.3, 1.2, int(2 * BAR * SR), dtype=np.float32)[: len(TIMPR[: int(2 * BAR * SR)])], at(s, 13), 0.9)
    put(rise, sustain(CEL, 43 + (5 if s == 2 else 0), 2 * BAR, head=0.5, kx=0.4, tail=0.4) * np.linspace(0.2, 1, int(2 * BAR * SR), dtype=np.float32), at(s, 13), 0.5)
    put(rise, applause[int(2 * SR): int(8 * SR)], at(s, 13, 1), 0.5 + 0.12 * s)
    put(calls, reverb(vox(PEACE[s]), 1.2, 0.3, seed=60 + s), at(s, 14, 1.5), 1.1)

# ── the speech: the crowd and the music fall back, Antony speaks into the hush ──
SPEECH = ['ant1', 'ant2', 'ant3']
for s in range(NST):
    put(speech, reverb(vox(SPEECH[s]), 2.4, 0.22, seed=70 + s), at(s, 15, 0.4))

# ── the coda: a last cheer, the brass, the Forum empties ──
for i, k in enumerate(['c1', 'c3', 'c5', 'c2', 'c4', 'c6']):
    put(chant, reverb(vox(k), 1.4, 0.35, seed=80 + i), at(NST, 1) + rng.uniform(-0.05, 0.05), 0.9)
put(chant, applause, at(NST, 1, 1), 0.9)
for m in (43, 50, 55, 58, 62): put(horns, sustain(HORN if m > 50 else TBN, m, 3 * BAR, head=0.4, kx=0.4, tail=2.5), at(NST, 1, 2), 0.4)
put(horns, sustain(TUBA, 31, 3 * BAR, head=0.4, kx=0.4, tail=2.5), at(NST, 1, 2), 0.6)
put(drums, TIMP[0], at(NST, 1, 2), 1.2)

def active(x, db):                                   # level a stem by its loudness WHILE it sounds, not averaged over silence
    w = int(0.4 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, 'same')); on = e > 0.1 * e.max()
    r = np.sqrt(np.mean(x[on] ** 2)) + 1e-12; return (x * (10 ** (db / 20) / r)).astype(np.float32)
def stems(*pairs):
    n = max(len(x) for x, _ in pairs); out = np.zeros(n, np.float32)
    for x, db in pairs: out[:len(x)] += active(x, db)
    return out
mix = stems((crowd, -27), (reverb(calls, 1.0, 0.2, seed=90), -22), (reverb(feet, 1.2, 0.25, seed=91), -27), (beat, -29),
            (chant, -22), (reverb(horns, 2.8, 0.34, seed=92), -22), (reverb(drums, 2.2, 0.3, seed=93), -24),
            (reverb(rise, 2.4, 0.3, seed=94), -24), (speech, -17))
mix = mix[: int((END + 4) * SR)]
n = int(2 * SR); mix[:n] *= np.linspace(0, 1, n)
os.makedirs(HERE + 'out', exist_ok=True)
write_mp3(rms_db(mix, -21), HERE + 'out/the-forum.mp3')
print('the forum', round(len(mix) / SR, 1), 's · speech at', [round(at(s, 15, 0.4), 1) for s in range(NST)])
