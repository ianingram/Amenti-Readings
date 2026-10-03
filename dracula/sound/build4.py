#!/usr/bin/env python3
"""The piano, in two distances. Synthesized; deterministic (seed 1897).

  piano-far.mp3   far away and airy: a few notes sprinkled high, long air
                  around them, the occasional soft chord. For letters, memory,
                  anything read rather than lived.
  piano-near.mp3  near and bold: close and dry, full chords when the moment
                  needs weight, single notes between them.

Both stay inside D minor's family (Dm, Bb, F, C, Gm, A) so either can sit
under the dread score without resolving it. Each is a minute long with no
regular pattern, and sound.js starts each use at a different point in it, so
a piece heard twenty times in a production is never heard the same way twice.
"""
import numpy as np
exec(open('/tmp/snd/build.py').read().split('# ── door_heavy.mp3')[0])
rng = np.random.default_rng(1897)
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)

def piano(m, vel=0.6, dur=7.0):
    """A better piano note: three detuned strings, stretched partials, a fast
    and a slow decay per partial, brightness that follows velocity, a hammer."""
    f0 = hz(m); n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    strings = 1 if m < 40 else (2 if m < 52 else 3)
    bright = 0.35 + 0.65 * vel
    for s_ in range(strings):
        det = (s_ - (strings - 1) / 2) * 0.0007
        for h in range(1, 12):
            f = f0 * h * np.sqrt(1 + 0.00035 * h * h) * (1 + det)
            if f > 9000: break
            a = (1 / h ** (1.6 - 0.7 * bright))
            fast = np.exp(-t * (1.8 + 0.9 * h)); slow = np.exp(-t * (0.25 + 0.12 * h + (m - 40) * 0.006))
            y += a * np.sin(2 * np.pi * f * t + rng.random() * 6) * (0.55 * fast + 0.45 * slow)
    y /= strings
    y += 0.05 * vel * lp(rng.standard_normal(n), 1800 + 2500 * vel) * np.exp(-t * 80)   # hammer
    y *= np.minimum(1, t / 0.004)
    y *= np.minimum(1, (dur - t) / 0.3).clip(0, 1)
    return (y * vel).astype(np.float32)

CH = {'Dm': [50, 57, 62, 65, 69], 'Bb': [46, 53, 58, 62, 65], 'F': [41, 53, 57, 60, 65],
      'C': [48, 55, 60, 64, 67], 'Gm': [43, 55, 58, 62, 67], 'A': [45, 52, 57, 61, 64]}
SCALE = [62, 64, 65, 67, 69, 70, 72, 74, 76, 77, 81]          # D minor, upper register

def render(events, L):
    out = np.zeros(int((L + 8) * SR), np.float32)
    for at, m, v, d in events:
        p = piano(m, v, d); i = int(at * SR); out[i:i + len(p)] += p[: len(out) - i]
    return out

L = 64.0
# ── far: sprinkled notes, high and soft, irregular; a soft chord every so often
ev = []; t = 1.0; prog = ['Dm', 'Bb', 'F', 'C', 'Dm', 'Gm', 'Bb', 'A']; ci = 0
while t < L - 2:
    if rng.random() < 0.18:                                    # a soft chord
        for k, m in enumerate(CH[prog[ci % 8]][1:]):
            ev.append((t + k * 0.06, m + 12, 0.22 + 0.06 * rng.random(), 8.0))
        ci += 1; t += 5.5 + 3 * rng.random()
    else:                                                      # one or two notes
        m = SCALE[rng.integers(len(SCALE))] + (12 if rng.random() < 0.35 else 0)
        ev.append((t, m, 0.25 + 0.15 * rng.random(), 6.0))
        if rng.random() < 0.3:
            ev.append((t + 0.35 + 0.3 * rng.random(), m - [3, 4, 5, 7][rng.integers(4)], 0.2, 6.0))
        t += 2.2 + 3.2 * rng.random()
far = render(ev, L)
far = lp(far, 3200, 2)                                         # distance takes the edge off
far = reverb(far, rt60=5.0, wet=0.62, pre=0.06, bright=2600, seed=17)
far = far[: int((L + 6) * SR)]
far = loop_seamless(far, 6.0)
write(norm_rms(far, -31), 'piano-far.mp3')

# ── near: close and dry; full chords with octave bass when it matters, notes between
ev = []; t = 0.5; prog = ['Dm', 'Bb', 'Gm', 'A', 'Dm', 'F', 'C', 'A']; ci = 0
while t < L - 3:
    ch = CH[prog[ci % 8]]; ci += 1
    ev.append((t, ch[0] - 12, 0.75, 8.0)); ev.append((t, ch[0], 0.6, 8.0))
    for k, m in enumerate(ch[1:]):
        ev.append((t + 0.012 * k, m, 0.55 + 0.1 * rng.random(), 7.0))
    gap = 6.0 + 2.5 * rng.random(); s = t + 1.8
    while s < t + gap - 1.0:                                   # single notes between the chords
        if rng.random() < 0.6:
            ev.append((s, ch[1 + rng.integers(4)] + 12 * (rng.random() < 0.5), 0.42 + 0.15 * rng.random(), 5.0))
        s += 0.9 + 0.8 * rng.random()
    t += gap
near = render(ev, L)
near = reverb(near, rt60=1.4, wet=0.2, pre=0.01, bright=5000, seed=19)
near = near[: int((L + 6) * SR)]
near = loop_seamless(near, 6.0)
write(norm_rms(near, -21), 'piano-near.mp3')
