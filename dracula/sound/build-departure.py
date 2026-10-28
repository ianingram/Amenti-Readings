#!/usr/bin/env python3
"""THE DEPARTURE AND THE DAWN — the opening of Dracula, Book I (28 Oct 2026).

Ian: "start the chapter 1 train boarding with low strings, cello, some French horns as
daylight appears; more sound effects; steam and fog; it is the beginning of the book, so
we need to make this a nice scene."

  drac1-munich-3-v1.mp3   cue 3, 88 s, no voice: Munich, 1 May, 8:35 P.M. The coach and
                          its black horses pull up at the station; the hall, steam, porters,
                          the platform, the compartment door; the guard's whistle, the engine
                          whistles and draws away; the train runs on into the night. Under it,
                          low strings: cellos and violas, D minor turning to F, swelling as
                          the train starts and settling as Jonathan writes.
  score-dawn.mp3          cue 4's score, 70 s: first light. The cellos hold, then the French
                          horns rise in D major as the sun comes up over the plain; the strings
                          open out; it hands over to the journey theme at Buda-Pesth.

Recordings: BigSoundBank (CC0): #3021 steam locomotive starting, #3016/#3018 steam
locomotive, #3020 between two wagons, #0226/#0228 steam whistle and hiss, #3515 crowd,
#0979 horses in the street; the hoof engine (build-hooves-engine.py) for the coach horses;
the folder's whistle, luggage, steps, door and chair sounds.
Instruments: Versilian Studios, VSCO 2 Community Edition (CC0): cello, viola and violin
sections, F horn. Deterministic (seed 1897).
"""
import sys, numpy as np, scipy.io.wavfile as wv, scipy.signal as sg, subprocess, glob, os, re
sys.argv = [sys.argv[0], '/tmp/claude-0/dep/']
exec(open('/tmp/journey/build-journey.py').read().split('# ── the form')[0])   # load, held, BANK, reverb, put, limit …
sys.path.insert(0, '/tmp/claude-0/hb')
import engine as E

OUT = '/tmp/claude-0/dep/'
S = '/tmp/bsb/src/'; F = '/tmp/cr5/dracula/sound/'
def snd(p): return E.load(p)                      # mono float at 48 kHz
def g(d): return 10 ** (d / 20)
def env(n, keys):
    t = np.arange(n) / SR; k = sorted(keys); return np.interp(t, [a for a, b in k], [b for a, b in k]).astype(np.float32)
def norm(x, d): return x * (g(d) / (np.sqrt(np.mean(x ** 2)) + 1e-12))
def fade(x, a, b): return E.fade(x, a, b)

# the horn
def hbank():
    out = {}
    for f in sorted(glob.glob('/tmp/vsco-b/Brass/F Horn/sus/*.wav')):
        m = re.search(r'sus_([A-G]#?\d)_v(\d)', os.path.basename(f))
        if m: out.setdefault(midi_of(m.group(1)), []).append((abs(int(m.group(2)) - 2), f))
    return {k: [f for _, f in sorted(v)] for k, v in out.items()}
BANK['horn'] = hbank()

def chord(buf, inst, notes, t, dur, gain, xf=0.6):
    for m in notes: put(buf, held(inst, m, dur, xf), t, gain / max(1, len(notes)) ** 0.5)

# ═══ CUE 3 · MUNICH, 8:35 P.M. ═════════════════════════════════════════════
L3 = 88.0; N3 = int(L3 * SR)
cel = np.zeros(N3, np.float32); vla = np.zeros(N3, np.float32); vln = np.zeros(N3, np.float32)
# D minor, then the turn to F as the train starts, back to D minor for the night.  [start, chord, …]
D2, F2, A2, C3, D3, E3, F3, G3, A3, Bb2, Bb3, C4, D4 = 38, 41, 45, 48, 50, 52, 53, 55, 57, 46, 58, 60, 62
PROG = [(0, [D2, A2, D3], [F3, A3]), (10, [Bb2 - 12 + 12, F3 - 12, D3], [F3, Bb3]), (19, [F2, C3, F3 - 12 + 12], [A3, C4]),
        (29, [C3 - 12, G3 - 12, E3], [G3, C4]), (38, [D2, A2, D3], [F3, A3]),
        (48, [Bb2, F3 - 12, D3], [F3, Bb3]), (57, [F2, C3, A2], [A3, C4]), (67, [A2 - 12, E3 - 12, C3 + 1], [E3, A3]),
        (77, [D2, A2, D3], [F3, A3])]
for i, (t, low, mid) in enumerate(PROG):
    t1 = PROG[i + 1][0] if i + 1 < len(PROG) else L3
    d = t1 - t + 3.0
    chord(cel, 'vc_sus', low, t, d, 0.55)
    chord(vla, 'vla_sus', mid, t, d, 0.38)
# a cello line in the tenor, long notes, once the hall is reached
LINE = [(19, A3, 5), (24, G3, 5), (29, E3, 4), (33, F3, 5), (38, D3, 9), (48, F3, 4), (52, G3, 5), (57, A3, 5), (62, C4, 5), (67, E3 + 12 - 12, 4), (71, C3 + 13, 6)]
for t, m, d in LINE: put(cel, held('vc_sus', m, d + 0.6), t, 0.42)
# violins only for the departure swell
for t, notes, d in [(48, [D4 + 0, F3 + 12], 9), (57, [C4 + 0, A3 + 12], 10)]:
    chord(vln, 'vln_sus', notes, t, d, 0.22)
music = reverb(cel + vla * 0.9 + vln, 2.6, 0.32, seed=7, bright=4200)
music *= env(N3, [(0, 0.0), (2.5, 0.55), (18, 0.6), (40, 0.62), (47, 0.7), (52, 1.0), (64, 1.0), (68, 0.7), (78, 0.55), (85, 0.5), (88, 0.0)])
music = norm(music, -24)

fx = np.zeros((N3, 2), np.float32)
def P(x, t, d, pan=0.0): E.put(fx, x, t, d, pan)
# 0–19: the coach and the black horses pull up at the station; the evening square
sp = E.curve([(0, 2.2), (5, 2.0), (8.5, 1.0), (10.5, 0), (L3, 0)], N3)
fx += E.team(N3, sp, 'stone', 4, -3.0, seed=31) * g(-14)
fx += E.wheels(N3, sp, 32) * g(-16)
street = norm(lp(snd(S + '0979.mp3')[int(5 * SR):int(30 * SR)], 3000), -30)
P(fade(street, 2, 5), 0, 0, -0.2)
for t in (11, 14.5, 17): P(E.pitch(E.peaknorm(E.one('0496')[: int(0.3 * SR)], -10), -2), t, -14, 0.2)
P(norm(E.one('0287'), -14), 12.2, -12, -0.3); P(norm(E.one('0460'), -14), 15.5, -16, 0.4)
# the station: crowd under the iron roof, an engine standing, steam
crowd = norm(reverb(lp(hp(snd(S + '3515.mp3')[int(10 * SR):int(80 * SR)], 180), 2600), 2.8, 0.5, seed=3), -27)
crowd = crowd[:N3] if len(crowd) >= N3 else np.pad(crowd, (0, N3 - len(crowd)))
fx += E.stereo(crowd * env(N3, [(0, 0.35), (16, 0.5), (19, 1.0), (46, 1.0), (52, 0.7), (60, 0.0), (L3, 0)]))
idle = norm(lp(snd(S + '3018.mp3')[int(30 * SR):int(110 * SR)], 3500), -28)
idle = idle[:N3] if len(idle) >= N3 else np.pad(idle, (0, N3 - len(idle)))
fx += E.stereo(idle * env(N3, [(0, 0), (17, 0), (20, 0.9), (48, 1.0), (52, 0.4), (55, 0), (L3, 0)]), 0.3)
P(reverb(norm(snd(S + '0228.mp3'), -16), 2.4, 0.4), 19.6, -6, 0.4)          # a great burst of steam as he steps into the hall
P(reverb(norm(snd(S + '0227.mp3'), -16), 2.4, 0.4), 33.5, -10, 0.5)
P(norm(snd(F + 'luggage_lift.mp3'), -18), 23.5, -8, -0.3)
P(norm(snd(F + 'steps_stone.mp3'), -20), 29.5, -10, 0.0)
P(norm(snd(F + 'door_close.mp3'), -18), 40.5, -6, -0.2)
P(norm(snd(F + 'chair_creak.mp3'), -20), 43.0, -12, -0.1)
# the departure: the guard's whistle, the engine's whistle, the first chuffs; the train draws away
P(reverb(norm(snd(F + 'whistle.mp3'), -16), 2.0, 0.4), 49.0, -6, 0.3)
P(reverb(norm(snd(S + '0226.mp3'), -14), 2.6, 0.45), 51.0, -4, 0.5)
start = norm(lp(snd(S + '3021.mp3')[int(17 * SR):int(39 * SR)], 5000), -20)
P(fade(start, 0.5, 3), 51.5, -2, 0.1)
# running on into the night: inside the carriage, then outside under the stars
run_in = norm(lp(snd(S + '3020.mp3'), 1800), -26); run_in = np.tile(run_in, 3)[:N3]
fx += E.stereo(run_in * env(N3, [(0, 0), (64, 0), (70, 0.9), (77, 0.9), (80, 0.3), (L3, 0.25)]))
run_out = norm(lp(snd(S + '3016.mp3'), 3200), -24); run_out = np.pad(run_out, (0, max(0, N3 - len(run_out))))[:N3]
fx += E.stereo(np.roll(run_out, int(70 * SR)) * env(N3, [(0, 0), (75, 0), (79, 0.9), (86, 0.8), (88, 0)]))
P(reverb(lp(norm(snd(F + 'loco-whistle-far.mp3'), -18), 3000), 3.0, 0.5), 80.5, -8, -0.4)

mix3 = E.stereo(music) * 1.0 + fx
mix3 = limit(mix3 * 0.9)
mix3 *= env(N3, [(0, 1), (86.5, 1), (88, 0)])[:, None]
wv.write(OUT + 'drac1-munich-3-v1.wav', SR, mix3.astype(np.float32))

# ═══ SCORE · DAWN ═══════════════════════════════════════════════════════════
LD = 70.0; ND = int(LD * SR)
c2 = np.zeros(ND, np.float32); v2 = np.zeros(ND, np.float32); h2 = np.zeros(ND, np.float32); w2 = np.zeros(ND, np.float32)
Fs3, Fs4, B2, E4, A4 = 54, 66, 47, 64, 69
DPROG = [(0, [D2, A2], [D3, F3]), (4, [D2, A2, D3], [Fs3, A3]), (14, [G3 - 12, D3], [B2 + 12, D4 - 12 + 12]),
         (22, [D2, A2, D3], [Fs3, A3]), (30, [A2 - 12, E3], [C3 + 13, E3 + 12 - 12]), (38, [B2 - 12, Fs3 - 12], [D3, Fs3]),
         (46, [G3 - 24 + 12, D3], [B2 + 12, D4]), (54, [A2, E3], [C3 + 13, A3]), (62, [D2, A2, D3], [Fs3, A3])]
for i, (t, low, mid) in enumerate(DPROG):
    t1 = DPROG[i + 1][0] if i + 1 < len(DPROG) else LD
    chord(c2, 'vc_sus', low, t, t1 - t + 3, 0.55); chord(v2, 'vla_sus', mid, t, t1 - t + 3, 0.4)
# the horns: a call rising as the sky lightens (4 s), then the sunrise phrase
HORN = [(4.2, A2, 3.0), (7.0, D3, 3.2), (10.0, Fs3, 2.6), (12.4, A3, 5.5),
        (22.0, A3, 3), (25.0, B2 + 12, 3), (28.0, A3, 2.5), (30.5, E3, 6),
        (38.0, Fs3, 3), (41.0, A3, 3), (44.0, D4, 6), (54.0, C3 + 13, 3), (57.0, E3, 3), (60.0, D3, 8)]
for t, m, d in HORN: put(h2, held('horn', m, d + 0.5, 0.5), t, 0.5)
for t, m, d in [(12.4, D3, 5.5), (44.0, Fs3, 6), (60.0, A2, 8)]: put(h2, held('horn', m, d + 0.5, 0.5), t, 0.34)   # second horn
for t, notes, d in [(14, [D4, Fs4 - 12 + 12], 8), (22, [D4, A3 + 12], 8), (38, [Fs4, A4], 8), (46, [D4 + 12 - 12, B2 + 24], 8), (62, [Fs4, A4], 8)]:
    chord(w2, 'vln_sus', notes, t, d, 0.2)
dawn = reverb(c2 + v2 * 0.9 + h2 * 1.1 + w2, 2.8, 0.3, seed=9, bright=5200)
dawn *= env(ND, [(0, 0.0), (2, 0.45), (4, 0.5), (12, 0.9), (16, 1.0), (60, 1.0), (70, 0.95)])
dawn = norm(dawn, -18)
dawn = fold(np.concatenate([dawn, dawn[:int(3 * SR)]]), 3.0)       # it loops if a slow reader needs it
wv.write(OUT + 'score-dawn.wav', SR, limit(dawn).astype(np.float32))
for n in ('drac1-munich-3-v1', 'score-dawn'):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + n + '.wav', '-ar', '44100', '-b:a', '160k', OUT + n + '.mp3'], check=True)
print('built', L3, LD)
