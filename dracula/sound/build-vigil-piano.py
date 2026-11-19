#!/usr/bin/env python3
"""THE VIGIL with piano (Ian, 18 Nov 2026): "I want them in the score, not as a repeat at the end."
Final (20:42): "the music box must lead." No piano under the tune. After the box's last note (~47 s)
the piano fills the last beats: the bass walks down A - G - F - E, growing, and the progression ends on
a full A minor at ~54 s, which rings ~10 s into the start of the loop (64 s).
(Earlier draft, the fill: (Ian, 18 Nov 2026): the music box as before; from ~47 s a single low
piano A, struck lightly and held, growing more pronounced as the tune runs out; the fill fades;
then strong low piano chords walking down Am - G - F - E and home to Am (Ian: "the walk down... bum, bum, bum";
the ear yearns for the completion), whose ringing tail fades into the start of the loop.
Then strong chords at the end — replaced by this.)
Built on the existing score-vigil.mp3 (55.4 s) so the music box is untouched.
Piano: VSCO 2 CE Upright Piano (Simon Dalzell / Ivy Audio, Versilian; CC0).
Contrabass: VSCO 2 CE Solo Contrabass sustain (CC0). usage: build-vigil-fill.py <vsco2 Keys dir> <out.mp3>"""
import sys, subprocess, numpy as np, soundfile as sf, scipy.signal as sg
SR = 48000; KEYS = sys.argv[1]; OUT = sys.argv[2]
rng = np.random.default_rng(1897)

def dec(path):
    raw = subprocess.run(['ffmpeg', '-v', '0', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def wav(path):
    x, sr = sf.read(path, dtype='float32'); x = x.mean(1) if x.ndim > 1 else x
    return sg.resample_poly(x, SR, sr).astype(np.float32) if sr != SR else x

def shift(x, semis):
    if not semis: return x
    r = 2 ** (semis / 12); idx = np.arange(0, len(x) - 1, r)
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)

def piano(m, dyn):                         # samples every 4 semitones from key 21
    k = min(range(21, 110, 4), key=lambda q: abs(q - m))
    return shift(wav(f'{KEYS}/Upright Piano/Player_dyn{dyn}_rr1_{(k - 21) // 2:03d}.wav'), m - k)

def reverb(x, rt60=4.0, wet=0.45, seed=7):
    n = int(rt60 * SR); t = np.arange(n) / SR
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-6.9 * t / rt60)
    ir = sg.sosfilt(sg.butter(2, 3200, 'low', fs=SR, output='sos'), ir); ir[:int(0.03 * SR)] = 0
    w = sg.fftconvolve(x, ir)[:len(x)]; w *= np.sqrt(np.mean(x ** 2) + 1e-12) / (np.sqrt(np.mean(w ** 2)) + 1e-12)
    return ((1 - wet) * x + wet * w).astype(np.float32)

def put(buf, x, t, g=1.0):
    i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * g

def env(n, pts):                           # piecewise-linear gain over a buffer, pts = [(sec, gain)]
    t = np.arange(n) / SR; return np.interp(t, [p[0] for p in pts], [p[1] for p in pts]).astype(np.float32)

vigil = dec(sys.argv[3] if len(sys.argv) > 3 else 'score-vigil.mp3')
SR_ = SR; BT = 60 / 52; step = BT / 2
TUNE = [76, 72, 69, 71, 72, 69, 64, 0, 76, 74, 72, 71, 69, 0, 0, 0, 74, 72, 71, 69, 68, 69, 71, 0, 72, 69, 64, 65, 64, 0, 0, 0] * 2
E8 = []; t = 0.5                                              # every eighth of the box, with its run-down drag
for i in range(len(TUNE)): E8.append(t); t += step * (1 + 0.012 * i)
END = t                                                       # 51.4 s: the last eighth of the tune
# Ian (20:42): "the music box must lead" — no piano under the tune. The piano comes in on the box's
# last rests and fills the last beats: the walk down A - G - F - E, then home on A minor at ~54 s.
BEAT = 1.2
WALK = [(E8[61], [33, 45, 52], 1, 0.6), (E8[61] + BEAT, [31, 43, 50], 2, 0.75),
        (E8[61] + 2 * BEAT, [29, 41, 48], 2, 0.9), (E8[61] + 3 * BEAT, [28, 40, 47, 56], 3, 0.9)]
HOME = 54.2; T = HOME + 10.0                                  # the home chord rings ~10 s, then the box again
N = int((T + 14) * SR)
walk = np.zeros(N, np.float32); home = np.zeros(N, np.float32)
def chord(buf, notes, t, dyn, g=1.0):
    for k, m in enumerate(notes): put(buf, piano(m, dyn), t + 0.012 * k, g * (1.0 if k == 0 else 0.7))   # a slight roll, bass first
for t_, notes, dyn, g in WALK: chord(walk, notes, t_, dyn, g)
chord(home, [33, 45, 52, 57, 60, 64], HOME, 3)                # home: A minor, full
ref = np.sqrt(np.mean(vigil[int(5 * SR):int(45 * SR)] ** 2))
def lvl(x, a, b): return np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)) + 1e-12
walk *= (ref * 1.1) / lvl(walk, WALK[0][0], HOME)
home *= (ref * 1.4) / lvl(home, HOME, HOME + 4)
home *= env(N, [(0, 1), (HOME + 6, 1), (T + 2, 0.3), (T + 12, 0)])
mix = np.zeros(N, np.float32); put(mix, vigil, 0.0)
mix += reverb(walk + home, 4.2, 0.42, 12)
loop = mix[:int(T * SR)].copy(); tail = mix[int(T * SR):]
loop[:len(tail)] += tail                                      # the home chord's tail fades into the start of the loop
loop *= min(1.0, (np.abs(vigil).max() * 1.6) / np.abs(loop).max())
subprocess.run(['ffmpeg', '-v', '0', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-b:a', '160k', OUT], input=loop.astype(np.float32).tobytes())
print(f'loop {T:.1f}s; last box note {E8[60]:.1f}s; walk from {WALK[0][0]:.1f}s; home at {HOME:.1f}s; box rms {20*np.log10(ref):.1f} dB')
