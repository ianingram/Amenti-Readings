#!/usr/bin/env python3
"""Build the first-pass sound files for Dracula episode one.

Sources (all public domain, verified on Wikimedia Commons, 3 Oct 2026):
  Wolf_howls.ogg                       US Fish & Wildlife Service (PD-USGov-FWS)
  Dry_grass_burning_in_open_fireplace  pdsounds.org / ezwa (PD)
  Door_handle_creaking.ogg             pdsounds.org / stephan (PD)
  Rusty_metal_door_clasp_02.ogg        pdsounds.org / stephan (PD)
Synthesized here (owned outright): stone room tone, low boom, the reverb,
and the whole of the score.
"""
import numpy as np, scipy.io.wavfile as wav, scipy.signal as sg, subprocess, os

SR = 48000
rng = np.random.default_rng(1897)          # Dracula's year; the build is deterministic
D = '/tmp/snd/'
OUT = '/tmp/snd/out/'
os.makedirs(OUT, exist_ok=True)

def load(name):
    sr, x = wav.read(D + name)
    x = x.astype(np.float32) / 32768.0
    if sr != SR:
        x = sg.resample_poly(x, SR, sr)
    return x

def db(x): return 10 ** (x / 20)
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-12)
def lp(x, f, o=4): return sg.sosfilt(sg.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sg.sosfilt(sg.butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)

def fade(x, fin=0.0, fout=0.0):
    x = x.copy(); n = len(x)
    if fin:
        k = int(fin * SR); x[:k] *= np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    if fout:
        k = int(fout * SR); x[n - k:] *= np.cos(np.linspace(0, np.pi / 2, k)) ** 2
    return x

def stretch_pitch(x, factor):
    """Resample by factor: >1 = slower AND lower (tape-style). 2.0 = an octave down, twice as long."""
    n = int(len(x) * factor)
    return sg.resample(x, n).astype(np.float32)

def reverb(x, rt60=2.4, wet=0.35, pre=0.02, bright=3500, seed=7):
    """Stone hall: exponentially decaying filtered noise impulse response, convolved."""
    r = np.random.default_rng(seed)
    n = int(rt60 * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-6.91 * t / rt60)
    ir = lp(ir, bright)
    ir[:int(pre * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    y = sg.fftconvolve(x, ir)
    dry = np.concatenate([x, np.zeros(len(y) - len(x))])
    return (1 - wet) * dry + wet * y * 0.9

def norm_peak(x, peak_db=-3.0): return x * (db(peak_db) / (np.abs(x).max() + 1e-12))
def norm_rms(x, rms_db): return x * (db(rms_db) / rms(x))

def loop_seamless(x, xfade=4.0):
    """Return a loop whose end runs into its start with an equal-power crossfade."""
    k = int(xfade * SR)
    body, tail = x[:-k].copy(), x[-k:]
    a = np.linspace(0, np.pi / 2, k)
    body[:k] = body[:k] * np.sin(a) + tail * np.cos(a)
    return body

def limit(x, ceiling_db=-1.0, knee_db=-6.0):
    """Soft limiter: transparent below the knee, tanh above it, never past the ceiling."""
    c, k = db(ceiling_db), db(knee_db)
    a = np.abs(x); y = x.copy()
    m = a > k
    y[m] = np.sign(x[m]) * (k + (c - k) * np.tanh((a[m] - k) / (c - k)))
    return y

def write(x, name, mono=True):
    x = limit(x)
    tmp = OUT + name + '.wav'
    wav.write(tmp, SR, (x * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ac', '1' if mono else '2',
                    '-ar', str(SR), '-c:a', 'libmp3lame', '-b:a', '128k', OUT + name], check=True)
    os.remove(tmp)
    print(f'{name:22s} {len(x)/SR:6.1f}s  rms {20*np.log10(rms(x)):6.1f} dBFS  peak {20*np.log10(np.abs(x).max()):5.1f}')

# ── door_heavy.mp3 — the great door swings back ─────────────────────────────
# A door-handle creak taken an octave and a half down becomes a hinge the
# size of a cart wheel; a low boom as the door comes to rest; a stone hall.
creak = load('Door_handle_creaking.wav')[: int(2.9 * SR)]
creak = hp(creak, 60)
big = stretch_pitch(creak, 2.6)                       # ~7.5 s, ~16 semitones lower
big = bp(big, 70, 2400)
big = fade(big, 0.15, 1.2)
clank = load('Rusty_metal_door_clasp_02.wav')
s = int(12.0 * SR); clank = clank[s: s + int(0.9 * SR)]
clank = stretch_pitch(hp(clank, 120), 1.35)
clank = fade(clank, 0.0, 0.25)
n = int(9.5 * SR); door = np.zeros(n, np.float32)
door[: len(clank)] += norm_peak(clank, -9)
c0 = int(0.55 * SR); door[c0: c0 + len(big)] += norm_peak(big, -6)[: n - c0]
t = np.arange(int(1.6 * SR)) / SR
boom = (np.sin(2 * np.pi * 42 * t) + 0.5 * np.sin(2 * np.pi * 63 * t)) * np.exp(-t * 3.2)
boom += lp(rng.standard_normal(len(t)), 220) * np.exp(-t * 9) * 0.6
b0 = int(6.9 * SR); door[b0: b0 + len(boom)] += norm_peak(boom.astype(np.float32), -4)[: n - b0]
door = reverb(door, rt60=2.8, wet=0.38)
door = fade(door, 0.0, 1.5)
write(norm_peak(door, -3), 'door_heavy.mp3')

# ── wolves.mp3 — "the howling of many wolves", from down in the valley ──────
w = load('Wolf_howls.wav')
s = int(1.0 * SR); w = w[s: s + int(16 * SR)]
w = lp(hp(w, 150), 3200)                              # distance takes the top off
w = reverb(w, rt60=3.2, wet=0.45, bright=2500, seed=11)
w = fade(w, 0.6, 4.0)
write(norm_peak(w, -4), 'wolves.mp3')

# ── fire.mp3 — the castle bed: a fire in the grate in a stone room ──────────
# sound.js plays this one file as three loops at different rates and offsets,
# so it carries no events that would audibly repeat — texture only.
L = 64.0
f = load('Dry_grass_burning_in_open_fireplace.wav')
f = lp(hp(f, 80), 4200, 2)             # a hearth, not a hiss: take the top down
f = f[int(0.5 * SR): int(24.5 * SR)]
reps = int(np.ceil(L * SR / (len(f) - 2 * SR))) + 1
fire = np.zeros(int(L * SR) + 4 * SR, np.float32); pos = 0
for i in range(reps):                                  # overlap-add with 2 s equal-power seams
    seg = fade(f, 2.0, 2.0) * (0.85 + 0.3 * rng.random())
    end = min(len(fire), pos + len(seg)); fire[pos:end] += seg[: end - pos]
    pos += len(f) - 2 * SR
    if pos >= len(fire): break
fire = fire[: int(L * SR)]
# warmth under the crackle: a low, slowly breathing rumble of the burning
rumble = lp(rng.standard_normal(len(fire)), 140, 2)
breath = 0.75 + 0.25 * np.sin(2 * np.pi * np.arange(len(fire)) / SR / 9.3)
fire = norm_rms(fire, -30) + norm_rms(rumble * breath, -34)
# the room itself: very low air, a cold stone hall
room = lp(np.cumsum(rng.standard_normal(len(fire))) * 0.002, 320, 2)
room = hp(room, 25)
bed = fire + norm_rms(room, -42)
bed = reverb(bed, rt60=1.6, wet=0.22, seed=3)[: len(bed)]
bed = loop_seamless(bed, 4.0)
write(norm_rms(bed, -24), 'fire.mp3')

# ── score-dread.mp3 — Harker's journal. Piano and low strings, no resolution.
# Static. An open fifth in the low strings that never moves, a second voice
# that leans a semitone up and back, and a few low piano notes far apart.
# Nothing arrives anywhere. Built to loop.
L = 128.0
N = int(L * SR); tt = np.arange(N) / SR
def string_voice(freq_fn, amp_fn, detune=0.004, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros(N, np.float32)
    for d in (-detune, 0.0, detune):
        vib = 1 + 0.0025 * np.sin(2 * np.pi * (4.6 + r.random()) * tt + r.random() * 6)
        ph = 2 * np.pi * np.cumsum(freq_fn(tt) * (1 + d) * vib) / SR
        saw = np.zeros(N)
        for h in range(1, 14):                           # band-limited sawtooth
            saw += ((-1) ** (h + 1)) * np.sin(h * ph) / h
        out += saw.astype(np.float32)
    bow = 1 + 0.08 * lp(np.random.default_rng(seed + 9).standard_normal(N), 3, 1) * 20
    return lp(out * amp_fn(tt) * bow, 900, 2)

swell = lambda per, ph: (0.55 + 0.45 * np.sin(2 * np.pi * tt / per + ph))
D2, A2, D3 = 73.42, 110.0, 146.83
low = string_voice(lambda t: np.full_like(t, D2), lambda t: swell(23, 0.0), seed=1)
fifth = string_voice(lambda t: np.full_like(t, A2), lambda t: swell(31, 1.7), seed=2)
# the leaning voice: D3, rising a semitone to Eb3 for a long while, then back. Never settles.
def lean(t):
    m = (np.sin(2 * np.pi * t / 64.0 - np.pi / 2) + 1) / 2            # 0..1 over 64 s
    m = np.clip((m - 0.35) * 3, 0, 1)
    return D3 * (2 ** (m / 12))
upper = string_voice(lean, lambda t: 0.6 * swell(19, 2.9), detune=0.003, seed=3)
strings = norm_rms(low, -27) + norm_rms(fifth, -30) + norm_rms(upper, -31)

def piano_note(freq, dur=7.0, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for h, a in enumerate([1, .55, .33, .22, .14, .09, .06, .04], start=1):
        f = freq * h * np.sqrt(1 + 0.0004 * h * h)        # slight inharmonicity
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t * (0.55 + 0.35 * h))
    y += 0.04 * lp(rng.standard_normal(n), 2500) * np.exp(-t * 60)   # the hammer
    y *= np.minimum(1, t / 0.004)
    return (y * vel).astype(np.float32)

notes = [(4.0, 73.42), (13.5, 116.54), (21.0, 87.31), (33.5, 77.78), (44.0, 73.42),
         (57.0, 110.0), (66.5, 116.54), (78.0, 82.41), (91.0, 73.42), (101.5, 87.31),
         (113.0, 77.78)]                                   # D Bb F Eb D A Bb E D F Eb
piano = np.zeros(N, np.float32)
for at, fr in notes:
    p = piano_note(fr, 8.0, 0.8 + 0.25 * rng.random())
    i = int(at * SR); piano[i: i + len(p)] += p[: N - i]
piano = reverb(piano, rt60=3.5, wet=0.4, seed=5)[:N]
score = strings + norm_rms(piano, -31)
score = reverb(score, rt60=2.2, wet=0.18, seed=6)[:N]
score = loop_seamless(score, 6.0)
write(norm_rms(score, -22), 'score-dread.mp3')
