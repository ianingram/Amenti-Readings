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
  bars 9–10  RISE     the crowd swells, a timpani roll building under it
  bars 11–13 HORNS    French horns over slow, rhythmic drums — and the crowd settles beneath them
  bar 14     HUSH     a citizen: "Peace, ho! Let us hear him." — and the crowd falls quiet
  bars 15–16 VOICE    Antony, heard from a distance across an open-air theatre: the stone stage,
                      the tiers of seats throwing the voice back, a long natural tail; the crowd's
                      murmur stays alive beneath him and stirs again after each line
(v6, Ian, 8 Oct: "the score should fade in slowly; the first shouts of Caesar around 15 seconds" — twelve seconds
of opening, the crowd rising out of silence and the legion's drum far off, before the first stanza.)
(v4, Ian, 7 Oct: "take what we have and create a 4/4 chord progression" — a chord bed under the
whole suite, one chord to the bar, a swell on beat 1 and a pulse on 2, 3, 4; "keep the soft G
underneath" Antony; and "why not C for Caesar" — so the Forum stays in G minor, G being the chord
that leans hardest toward C, and the third stanza turns to C minor, Caesar's own key (his theme in
the score is C minor), and the coda lands there.)
(v3, Ian, 7 Oct: in the market, "a 4/4 sound from far away, loud, inside the Forum, with the stamp of
feet and the shout of voices — very military and pompous"; and "someone strikes a bell with an anvil
right before the French horns blow — loud, three strikes of a large bell, to start the speech.")
(v2, Ian, 7 Oct: "the crowd should swell, then French horns; the voice comes in after the crowd has
hushed, after the horns — heard from a distance in an open-air theatre with great natural acoustics,
blended with the crowd's dynamics.")
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
PRE = 12.0                                          # v6: a slow opening before the first stanza (Ian, 8 Oct)
END = PRE + NST * STZ * BAR + 4 * BAR                     # three stanzas and a coda of four bars
N = int((END + 6) * SR)
def at(stanza, bar, beat=0.0): return PRE + (stanza * STZ + bar - 1) * BAR + beat * BT

crowd, calls, feet, beat, chant, horns, drums, rise, speech = (np.zeros(N, np.float32) for _ in range(9))

# ── the crowd: the Roman street, looped under everything, its level drawn stanza by stanza ──
street = aud(QV + 'rome-street.mp3'); applause = aud(QV + 'applause.mp3'); cheer = aud(QV + 'cheer.mp3')
crowd[:] = np.tile(street, int(np.ceil(N / len(street))))[:N]
pulse = np.zeros(N, np.float32)                     # the murmur falling into the beat
tb = np.arange(int(BT * SR)) / SR; one = (0.55 + 0.45 * np.exp(-tb * 5)).astype(np.float32)
lvl = []
for s in range(NST):
    g = 1 + 0.18 * s
    lvl += [(at(s, 1), 0.9 * g), (at(s, 4.6), 0.9 * g), (at(s, 5), 0.85 * g), (at(s, 8.9), 1.0 * g),
            (at(s, 9), 1.0 * g), (at(s, 10.9), 1.45 * g),                       # the swell
            (at(s, 11.2), 1.1 * g), (at(s, 13.4), 0.55),                        # settling under the horns
            (at(s, 14, 1), 0.5), (at(s, 14.9), 0.13),                            # the hush
            (at(s, 16, 0), 0.15), (at(s, 16, 2.5), 0.38), (at(s, 16.95), 0.6)]   # alive under the voice, stirring after it
lvl += [(at(NST, 1), 1.2), (at(NST, 3), 1.0), (END + 4, 0.0)]
crowd *= env_lin(N, [(0, 0.0), (10.0, 0.9)] + lvl)
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
HT = [(0, 67, 2), (2, 70, 1), (3, 69, 1), (4, 67, 2), (6, 62, 2), (8, 63, 2), (10, 62, 2.6)]      # three bars, coming to rest
LOWB = [(43, [55, 58, 62]), (39, [55, 58, 63]), (38, [50, 54, 57])]
for s in range(NST):
    up = 0 if s < 2 else 5                                                        # the third stanza lifts a fourth
    for st, m, d in HT:
        put(horns, sustain(HORN, m - 12 + up, d * BT * 1.02 + 0.3, head=0.15, kx=0.2, tail=0.8), at(s, 11, st), 0.6 + 0.12 * s)
        if s > 0: put(horns, sustain(HORN, m - 24 + up + 7, d * BT * 1.02 + 0.3, head=0.15, kx=0.2, tail=0.8), at(s, 11, st), 0.3)
    for b, (root, tri) in enumerate(LOWB):
        last = b == len(LOWB) - 1
        put(horns, sustain(TUBA, root - 12 + up, BAR + (1.2 if last else 0.4), head=0.4, kx=0.4, tail=1.0 if last else 0.6), at(s, 11 + b), 0.45)
        for m in tri: put(horns, sustain(TBN, m - 12 + up, BAR + (1.2 if last else 0.3), head=0.4, kx=0.4, tail=1.0 if last else 0.6), at(s, 11 + b), 0.18)
        put(drums, TIMP[b % 2], at(s, 11 + b), 1.0 if not last else 0.8)
        if not last:
            put(drums, TIMP[2], at(s, 11 + b, 2), 0.7)
            put(drums, lp(BD, 260), at(s, 11 + b), 0.6); put(drums, lp(BD, 260), at(s, 11 + b, 3.5), 0.3)

# ── the rise, and the citizen calling for quiet ──
PEACE = ['p1', 'p2', 'p1']
for s in range(NST):
    roll = TIMPR[: int(2 * BAR * SR)]
    put(rise, roll * np.linspace(0.3, 1.2, len(roll), dtype=np.float32), at(s, 9), 0.9)
    put(rise, sustain(CEL, 43 + (5 if s == 2 else 0), 2 * BAR, head=0.5, kx=0.4, tail=0.4) * np.linspace(0.2, 1, int(2 * BAR * SR), dtype=np.float32), at(s, 9), 0.5)
    put(rise, applause[int(2 * SR): int(8 * SR)], at(s, 9, 1), 0.6 + 0.12 * s)
    put(calls, reverb(vox(PEACE[s]), 1.2, 0.3, seed=60 + s), at(s, 13, 3.2), 1.1)      # the call that hushes them

# ── the speech: the crowd and the music fall back, Antony speaks into the hush ──
def theatre(x, seed):
    """the voice as heard from the upper tiers of an open-air theatre: the distance (air takes the
    top and a little of the bottom), the stage wall and the stepped tiers of seats returning it in a
    rapid train of reflections, a long, dark natural tail — and more room than voice"""
    r = np.random.default_rng(seed); x = hp(lp(x, 4200), 140)
    n = int(3.4 * SR); ir = np.zeros(n, np.float32); ir[0] = 1.0
    for k in range(14):                                  # the tiers: each a little later, softer, darker
        d = int((0.028 + k * 0.011 + r.uniform(0, 0.004)) * SR); ir[d] += 0.5 * 0.86 ** k * (1 if k % 2 else -1)
    ir[int(0.19 * SR)] += 0.32                           # the scaenae frons behind the stage
    ir[int(0.41 * SR)] += 0.16                           # the far wall, a faint slap
    tail = r.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / SR * (6.9 / 2.9)).astype(np.float32)
    tail = lp(tail, 2600) * np.clip((np.arange(n) / SR - 0.06) / 0.12, 0, 1).astype(np.float32)
    ir += tail * 0.09
    wet = sg.fftconvolve(x, ir)[: len(x) + int(2.5 * SR)].astype(np.float32)
    dry = np.zeros_like(wet); dry[: len(x)] = x
    return dry * 0.35 + wet * 0.9
# v5 (Ian, 7 Oct: "it's all about the beat — friends.. romans... countrymen.... lend me.. your.. ears...";
# fuse the Roman sound with the English): Antony recorded for this file alone, in an English stage voice with
# Italian vowels, each phrase set to start on a beat, the open-air theatre filling the gaps. Not the ledger voice.
V5 = os.environ.get('V5', 'a')
def phrases(path):
    x = read(path); w = int(.02 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, 'same')); idx = np.where(e > 0.04 * e.max())[0]
    out = []; a = idx[0]; pv = idx[0]
    for j in idx[1:]:
        if j - pv > int(.12 * SR): out.append((a, pv)); a = j
        pv = j
    out.append((a, pv))
    return [x[max(0, a - 600): b + 2400] for a, b in out if (b - a) > 0.25 * SR]
def on_beat(segs, t0):
    t = t0; y = np.zeros(int(16 * SR), np.float32)
    for g in segs:
        put(y, g, t - t0); end = t + len(g) / SR
        t = t0 + np.ceil((end + 0.12 - t0) / BT) * BT
    return y
for s in range(NST):
    put(speech, theatre(on_beat(phrases(HERE + f'v5/{V5}{s + 1}.wav'), at(s, 15)), 70 + s), at(s, 15))
    put(crowd, np.zeros(1, np.float32), 0)

# ── the coda: a last cheer, the brass, the Forum empties ──
for i, k in enumerate(['c1', 'c3', 'c5', 'c2', 'c4', 'c6']):
    put(chant, reverb(vox(k), 1.4, 0.35, seed=80 + i), at(NST, 1) + rng.uniform(-0.05, 0.05), 0.9)
put(chant, applause, at(NST, 1, 1), 0.9)
for m in (48, 55, 60, 63, 67): put(horns, sustain(HORN if m > 50 else TBN, m, 3 * BAR, head=0.4, kx=0.4, tail=2.5), at(NST, 1, 2), 0.4)   # C minor: Caesar's key
put(horns, sustain(TUBA, 36, 3 * BAR, head=0.4, kx=0.4, tail=2.5), at(NST, 1, 2), 0.6)
put(drums, TIMP[0], at(NST, 1, 2), 1.2)

# ── v3: the legion — a column marching through the Forum in bars 1–4, heard from far off, loud, the
#    stone of the basilicas and colonnades throwing it back; bass drum on every beat, a snare cadence,
#    cymbals, hobnailed feet, soldiers barking "Caesar!" — coming nearer, landing on bar 5 ──
def nh(x, pk=1.0): return (x / (np.abs(x).max() + 1e-9) * pk).astype(np.float32)
SN = [nh(load16(P + f'Snare2-HitSN_v{v}_rr1_Sum.wav')) for v in (9, 5, 3)]
SNR = nh(load16(P + 'Snare2-rollSN_v5_rr1_Sum.wav'))
BDL = nh(load16(P + 'BDrumNewhit_v7_rr1_Sum.wav')); BDL2 = nh(load16(P + 'BDrumNewhit_v7_rr2_Sum.wav'))
CRASH = nh(load16(P + 'cymbal-crash1_ff_rr1.wav'))
def first_word(k):
    x = vox(k); e = np.convolve(np.abs(x), np.ones(960) / 960, 'same'); on = e > 0.05 * e.max()
    i = int(np.argmax(on)); j = i + int(np.argmax(~on[i:])); return x[max(0, i - 400): j + 1200]
SHOUT = [first_word(k) for k in ('c1', 'c3', 'c5', 'c2', 'c4')]
def hobnail(g):                                       # a soldier's step: the thud, and the iron nails on stone
    n = int(0.14 * SR); t = np.arange(n) / SR
    x = lp(rng.standard_normal(n).astype(np.float32), 220) * 3.5 * np.exp(-t * 28)
    x += bp(rng.standard_normal(n).astype(np.float32), 2500, 7000) * 0.5 * np.exp(-t * 90)
    return (x * g).astype(np.float32)
SNARE = [(0, 0), (2, 2), (3, 2), (4, 1), (6, 2), (8, 0), (10, 2), (11, 2)]      # sixteenths, sample (0 loud … 2 ghost)
SG = [1.0, 0.6, 0.35]
far_, near_ = np.zeros(N, np.float32), np.zeros(N, np.float32)
legion = np.zeros(N, np.float32)
for s in range(NST):
    g = 1 + 0.15 * s
    for bar in range(1, 5):
        for k in range(4):
            t = at(s, bar, k)
            put(legion, BDL if k % 2 == 0 else BDL2, t, (1.0 if k == 0 else 0.75) * g)
            for d in range(24): put(legion, hobnail(rng.uniform(0.15, 0.35)), t + rng.uniform(-0.03, 0.05), g)
        pat = SNARE if bar < 4 else SNARE[:4]
        for six, v in pat: put(legion, SN[v], at(s, bar, six / 4), SG[v] * 0.8 * g)
        if bar == 4:                                  # the roll into bar 5
            r = SNR[: int(2 * BT * SR)] * np.linspace(0.35, 1.0, int(2 * BT * SR), dtype=np.float32)
            put(legion, r, at(s, 4, 2), 0.8 * g)
    put(legion, CRASH, at(s, 1), 0.45 * g); put(legion, CRASH, at(s, 3), 0.6 * g)
    put(legion, CRASH, at(s, 5), 0.9 * g); put(legion, BDL, at(s, 5), 1.1 * g)
    for bar, bt_ in ((2, 0), (4, 2)):                # the soldiers' shout
        for i, x in enumerate(SHOUT): put(legion, x, at(s, bar, bt_) + rng.uniform(-0.04, 0.04), 1.1 * g)
def forum(x, seed, dist):
    """the Forum: a paved square walled with basilicas, temples and colonnades — hard stone close on
    every side, so a run of slaps off the façades and a long bright-ish tail; distance takes the top end"""
    r = np.random.default_rng(seed); x = hp(lp(x, 1500 + 5000 * (1 - dist)), 60)
    n = int(2.8 * SR); ir = np.zeros(n, np.float32); ir[0] = 1.0 - 0.6 * dist
    for d, a in ((0.061, 0.5), (0.094, 0.42), (0.137, 0.38), (0.19, 0.3), (0.26, 0.26), (0.33, 0.18), (0.47, 0.12)):
        ir[int((d + r.uniform(0, 0.006)) * SR)] += a * (0.6 + 0.6 * dist)
    tail = r.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / SR * (6.9 / 2.4)).astype(np.float32)
    ir += lp(tail, 3600) * np.clip((np.arange(n) / SR - 0.04) / 0.08, 0, 1).astype(np.float32) * (0.05 + 0.08 * dist)
    return sg.fftconvolve(x, ir)[: len(x)].astype(np.float32)
lg_far, lg_near = forum(legion, 95, 1.0), forum(legion, 95, 0.35)
mixw = [(0, 0.0)]
for s in range(NST):
    mixw += [(at(s, 1), 0.0), (at(s, 4, 3), 0.85), (at(s, 5, 2), 1.0), (at(s, 5, 3.9), 0.0)]
w = env_lin(N, mixw)
legion = lg_far * (1 - w) + lg_near * w
far_drum = np.zeros(N, np.float32)                   # v6: the legion's drum far off in the opening, no voices yet
t = 3.0
while t < PRE - 0.05:
    put(far_drum, BDL, t, 0.25 + 0.75 * (t / PRE) ** 2); t += BT
legion += forum(far_drum, 98, 1.0) * 0.6
lvl_l = [(0, 0.0)]
for s in range(NST):
    lvl_l += [(at(s, 1) - 0.01, 0.0), (at(s, 1, 0.01), 0.75), (at(s, 4, 3), 1.0), (at(s, 5, 2.5), 1.0), (at(s, 6), 0.0)]
legion *= env_lin(N, lvl_l)

# ── v3: the bell — a great bronze bell, struck three times with an anvil hammer on bar 10, beats 1, 2, 3;
#    the fourth beat is silence, and the horns blow on the downbeat of bar 11 ──
ANVIL = nh(load16(P + 'Anvil_Hit1_v3_Sum.wav'))
def great_bell(f, secs=9.0, seed=0):
    """a large cast-bronze bell, struck in G: the classic partials — hum, prime, minor-third tierce,
    quint, nominal and above, each with its own decay — the strike note bright and quick, the hum
    lingering longest; the iron of the hammer on the lip at the instant of the blow"""
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    PART = [(0.5, 1.0, 0.35), (1.0, 0.8, 0.55), (1.19, 0.6, 0.8), (1.5, 0.35, 1.2), (2.0, 0.7, 1.0),
            (2.5, 0.3, 1.8), (2.66, 0.25, 2.2), (3.0, 0.22, 2.6), (4.2, 0.15, 4.0), (5.4, 0.08, 6.0)]
    x = np.zeros(n, np.float32)
    for m, a, dec in PART:
        for det in (-0.6, 0.6):                       # each partial a doublet, beating slowly as real bells do
            x += (a * 0.5 * np.sin(2 * np.pi * (f * m + det * m * 0.3) * t + r.uniform(0, 6.28)) * np.exp(-t * dec)).astype(np.float32)
    x *= np.clip(t / 0.002, 0, 1).astype(np.float32)
    clank = ANVIL[: n] if len(ANVIL) < n else ANVIL[:n]
    x[: len(clank)] += clank * 0.55
    return nh(x)
bell = np.zeros(N, np.float32)
for s in range(NST):
    for b in range(3):
        put(bell, great_bell(98.0, seed=s * 3 + b), at(s, 10, b), 1.0 + 0.1 * s)
bell = forum(bell, 96, 0.55)

# ── v4: the chord bed — one chord to the bar, 4/4: a swell on 1, a pulse on 2, 3 and 4 ──
VLA = bank('Strings/Viola Section/susvib/*_v2_1.wav', r'susvib_([A-G]#?\d)_')
CH = {'Gm': (43, [50, 55, 58]), 'Eb': (39, [51, 55, 58]), 'Bb': (46, [53, 58, 62]), 'F': (41, [53, 57, 60]),
      'Cm': (36, [51, 55, 60]), 'D': (38, [50, 54, 57]), 'Fm': (41, [53, 56, 60]), 'G': (43, [50, 55, 59]),
      'Ab': (44, [51, 56, 60])}
PROG = [['Gm', 'Eb', 'Bb', 'F', 'Gm', 'Eb', 'Bb', 'F', 'Cm', 'D', 'Gm', 'Eb', 'D'],      # I
        ['Gm', 'Eb', 'Bb', 'F', 'Gm', 'Eb', 'Bb', 'F', 'Cm', 'D', 'Gm', 'Eb', 'D'],      # II
        ['Gm', 'Eb', 'Bb', 'F', 'Gm', 'Eb', 'Bb', 'F', 'Fm', 'G', 'Cm', 'Ab', 'G']]      # III turns to C, with the horns
nb = int(BAR * SR); tt = np.arange(nb + int(0.5 * SR)) / SR
PULSE = (0.72 + 0.28 * np.exp(-np.clip(tt, 0, None) / 0.9)).astype(np.float32)
for k in (1, 2, 3): PULSE += (0.13 * np.exp(-np.clip(tt - k * BT, 0, None) / 0.25) * (tt >= k * BT)).astype(np.float32)
PULSE *= np.clip(tt / 0.12, 0, 1).astype(np.float32)
chords = np.zeros(N, np.float32)
def chord(name, t, bars=1, g=1.0, brass=0, pulse=True):
    root, up_ = CH[name]; d = bars * BAR + 0.5
    x = sustain(CEL, root, d, head=0.3, kx=0.3, tail=0.5) * 0.9 + sustain(CEL, root + 12, d, head=0.3, kx=0.3, tail=0.5) * 0.45
    for m in up_: x = x + sustain(VLA, m, d, head=0.3, kx=0.3, tail=0.5) * 0.4
    if brass >= 1:
        for m in up_: x = x + sustain(TBN, m - 12 if m > 58 else m, d, head=0.3, kx=0.3, tail=0.5) * 0.16
    if brass >= 2: x = x + sustain(TUBA, root - 12 if root >= 43 else root, d, head=0.3, kx=0.3, tail=0.5) * 0.3
    if pulse:
        env = np.tile(PULSE[:nb], bars + 1)[: len(x)]; x = x * env
    put(chords, x * g, t)
for s, prog in enumerate(PROG):
    g = 0.8 + 0.12 * s
    for b, name in enumerate(prog):
        horns_bar = b >= 10                                    # bars 11–13: the horns carry the brass; strings only here
        chord(name, at(s, b + 1), 1, g, brass=0 if horns_bar else s)
    # bars 14–16: the hush and the voice — a soft G held low in the cellos, and nothing else
    ped = (sustain(CEL, 43, 3 * BAR + 0.8, head=0.4, kx=0.4, tail=1.2) * 0.8 +
           sustain(CEL, 50, 3 * BAR + 0.8, head=0.4, kx=0.4, tail=1.2) * 0.4)
    ped *= env_lin(len(ped), [(0, 0.0), (1.5, 1.0), (len(ped) / SR - 1.2, 1.0), (len(ped) / SR, 0.0)])
    put(chords, ped * 0.32, at(s, 14))
chord('Cm', at(NST, 1, 2), 3, 1.15, brass=2, pulse=False)    # the coda: Caesar's key, everything

def active(x, db):                                   # level a stem by its loudness WHILE it sounds, not averaged over silence
    w = int(0.4 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, 'same')); on = e > 0.1 * e.max()
    r = np.sqrt(np.mean(x[on] ** 2)) + 1e-12; return (x * (10 ** (db / 20) / r)).astype(np.float32)
def stems(*pairs):
    n = max(len(x) for x, _ in pairs); out = np.zeros(n, np.float32)
    for x, db in pairs: out[:len(x)] += active(x, db)
    return out
mix = stems((crowd, -27), (reverb(calls, 1.0, 0.2, seed=90), -22), (reverb(feet, 1.2, 0.25, seed=91), -27), (beat, -29),
            (chant, -22), (reverb(horns, 2.8, 0.34, seed=92), -22), (reverb(drums, 2.2, 0.3, seed=93), -24),
            (reverb(rise, 2.4, 0.3, seed=94), -24), (speech, -16.8), (legion, -16), (bell, -15), (reverb(chords, 2.6, 0.35, seed=97), -25))
mix = mix[: int((END + 4) * SR)]
n = int(8 * SR); mix[:n] *= np.linspace(0, 1, n) ** 1.5
os.makedirs(HERE + 'out', exist_ok=True)
write_mp3(rms_db(mix, -21), HERE + 'out/the-forum.mp3')
print('the forum', round(len(mix) / SR, 1), 's · voice at', [round(at(s, 14, 3.4), 1) for s in range(NST)])
