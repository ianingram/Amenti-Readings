#!/usr/bin/env python3
"""THE VIGIL with a fill (Ian, 18 Nov 2026): the music box as before; from ~47 s a single low
piano A, struck lightly and held, growing more pronounced as the tune runs out; the fill fades;
then strong low piano chords walking down Am - G - F - E and home to Am (Ian: "the walk down... bum, bum, bum";
the ear yearns for the completion), whose ringing tail fades into the start of the loop.
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
V = len(vigil) / SR; T = 82.0                                  # the new loop length
N = int((T + 14) * SR)                                         # room for the tail, wrapped below
fill = np.zeros(N, np.float32); chords = np.zeros(N, np.float32)
ref = np.sqrt(np.mean(vigil[int(5 * SR):int(45 * SR)] ** 2))  # the music box's own level

# the fill: one low A (A1), struck lightly and held, more pronounced as the tune runs out
for t, dyn, g in [(47.0, 1, 1.0), (51.0, 2, 0.6), (54.6, 2, 1.0)]:
    put(fill, piano(33, dyn), t, g)
put(fill, piano(45, 1), 54.65, 0.8)                            # the octave joins on the last strike
bass = wav(f'/tmp/vsco/Strings/Solo Contrabass/SusNV/BKCtbss_SusNV_A1_v1_rr1.wav')
while len(bass) < int(16 * SR): bass = np.concatenate([bass, bass[int(0.5 * SR):]])
put(fill, bass[:int(16 * SR)] * env(int(16 * SR), [(0, 0), (6, 0.35), (10, 0.6), (13, 0.25), (16, 0)]), 48.0)
fill *= env(N, [(0, 1), (59.0, 1), (62.0, 0.2), (63.5, 0)])    # the fill fades before the chords
# strong power chords: A5, F5, E5 (root, fifth, octave, fifth) — the E rings into the loop
B2 = 2 * 60 / 52                                               # two beats of the box's tempo
WALK = [(62.0, [33, 40, 45, 52]),                              # Am  - the walk down: A, G, F, E in the bass
        (62.0 + B2, [31, 38, 43, 50]),                         # G
        (62.0 + 2 * B2, [29, 36, 41, 48]),                     # F
        (62.0 + 3 * B2, [28, 35, 40, 47, 52]),                 # E   - held a beat longer: the ear waits
        (62.0 + 5 * B2, [33, 40, 45, 48, 52, 57])]             # Am  - home: the completion, ringing into the loop
for t, notes in WALK:
    for m in notes: put(chords, piano(m, 3), t, 1.0 - 0.08 * (m > 40))
chords *= env(N, [(0, 1), (74.0, 1), (84.0, 0.35), (94.0, 0)])

def lvl(x, a, b): return np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)) + 1e-12
fill *= (ref * 0.85) / lvl(fill, 52, 57)                       # the held note under the box, then rising
chords *= (ref * 1.6) / lvl(chords, 62, 66)                    # the chords stand out, ~4 dB over the box
mix = np.zeros(N, np.float32); put(mix, vigil, 0.0)
mix += reverb(fill, 4.5, 0.5, 11) + reverb(chords, 5.0, 0.42, 12)
loop = mix[:int(T * SR)].copy(); tail = mix[int(T * SR):]
loop[:len(tail)] += tail                                       # the chords' tail fades into the start of the loop
pk = np.abs(loop).max(); vpk = np.abs(vigil).max()
loop *= min(1.0, (vpk * 1.6) / pk)                             # fixed gain; only the chord peaks are reined in
subprocess.run(['ffmpeg', '-v', '0', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-b:a', '160k', OUT], input=loop.astype(np.float32).tobytes())
print(f'vigil {V:.1f}s -> loop {T:.1f}s; box rms {20*np.log10(ref):.1f} dB, peak {20*np.log10(np.abs(loop).max()):.1f} dB')
