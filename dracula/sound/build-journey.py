#!/usr/bin/env python3
"""THE JOURNEY EAST — the train ride in Dracula chapter I (Book I's opening).

21 Oct 2026, Ian: "a 4/4 beat with strings in a major scale" for the train ride, and an
opening score under the first narration. D major, 4/4, 112 BPM — the strings carry the beat
(spiccato eighths like wheels on rails), the melody sings over it, pizzicato bass on 1 and 3,
soft timpani, snare taps on 2 and 4, sleigh bells on the offbeats for the jingle of the
carriage. Through-composed (intro, A, B, A', a thinned turn back) so the ~2½-minute piece is
not heard to repeat inside one stretch of the chapter; folded to loop seamlessly.

Instruments: Versilian Studios, VSCO 2 Community Edition (CC0; credit requested) —
violin/viola/cello sections (spiccato, sustain), solo violin, solo contrabass pizzicato,
timpani, snare, triangle, sleigh bells. Deterministic (seed 1897).
"""
import numpy as np, scipy.io.wavfile as wv, scipy.signal as sg, subprocess, os, re, glob, warnings, sys
warnings.filterwarnings('ignore')
SR = 48000
V = '/tmp/vsco/'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/journey/'
rng = np.random.default_rng(1897)
_c = {}

def load(path, semis=0.0):
    k = (path, round(semis, 4))
    if k in _c: return _c[k]
    sr, x = wv.read(path); x = x.astype(np.float32)
    if x.ndim > 1: x = x.mean(1)
    x /= (32768.0 if np.abs(x).max() > 2 else 1.0)
    ratio = SR / sr * (2 ** (-semis / 12))
    if abs(ratio - 1) > 1e-6: x = sg.resample_poly(x, int(round(ratio * 1000)), 1000).astype(np.float32)
    _c[k] = x; return x
def lp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'low', fs=SR, output='sos'), x).astype(np.float32)
def hp(x, f, o=2): return sg.sosfilt(sg.butter(o, f, 'high', fs=SR, output='sos'), x).astype(np.float32)
def put(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i < 0: return
    n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n] * g
def reverb(x, rt=2.0, wet=0.2, seed=5, bright=5000):
    r = np.random.default_rng(seed); n = int(rt * SR); tt = np.arange(n) / SR
    ir = lp(r.standard_normal(n) * np.exp(-6.91 * tt / rt), bright); ir /= np.sqrt(np.sum(ir ** 2))
    return ((1 - wet) * x + wet * sg.fftconvolve(x, ir)[:len(x)]).astype(np.float32)
def rms_db(x, db): return x * (10 ** (db / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12))
def fold(x, xf):
    k = int(xf * SR); body = x[:-k].copy(); a = np.linspace(0, np.pi / 2, k)
    body[:k] = body[:k] * np.sin(a) + x[-k:] * np.cos(a); return body
def limit(x, c=-1.0, k=-6.0):
    c, k = 10 ** (c / 20), 10 ** (k / 20); a = np.abs(x); y = x.copy(); m = a > k
    y[m] = np.sign(x[m]) * (k + (c - k) * np.tanh((a[m] - k) / (c - k))); return y
def write_mp3(x, name, br='160k'):
    x = limit(x); tmp = OUT + name + '.tmp.wav'; wv.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ac', '1', '-c:a', 'libmp3lame', '-b:a', br, OUT + name], check=True)
    os.remove(tmp)

PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def midi_of(name):
    m = re.match(r'([A-G])(#?)(-?\d)', name); return (int(m.group(3)) + 1) * 12 + PC[m.group(1)] + (1 if m.group(2) else 0)
def bank(pattern, rx):
    out = {}
    for f in sorted(glob.glob(V + pattern)):
        m = re.search(rx, os.path.basename(f))
        if m: out.setdefault(midi_of(m.group(1)), []).append(f)
    return out
BANK = {
    'vln_spic': bank('Strings/Violin Section/Spic/*.wav', r'Spic_([A-G]#?\d)_v2'),
    'vla_spic': bank('Strings/Viola Section/spic/*.wav', r'spic_([A-G]#?\d)_v2'),
    'vc_spic':  bank('Strings/Cello Section/spic/*.wav', r'spic_([A-G]#?\d)_v2'),
    'vln_sus':  bank('Strings/Violin Section/susVib/*.wav', r'susVib_([A-G]#?\d)_v1'),
    'vla_sus':  bank('Strings/Viola Section/susvib/*.wav', r'susvib_([A-G]#?\d)_v1'),
    'vc_sus':   bank('Strings/Cello Section/susvib/*.wav', r'susvib_([A-G]#?\d)_v1'),
    'solo':     bank('Strings/Solo Violin/Arco Vib/*.wav', r'ArcoVib_([A-G]#?\d)_p'),
    'pizz':     bank('Strings/Solo Contrabass/Pizz/*.wav', r'Pizz_([A-G]#?\d)_v3'),
}
for k, b in BANK.items():
    if not b: raise SystemExit('empty bank ' + k)
def nearest(inst, m, rr=0):
    b = BANK[inst]; k = min(b, key=lambda x: abs(x - m)); fs = b[k]; return fs[rr % len(fs)], m - k
def short(inst, m, dur, rr=0):
    f, semis = nearest(inst, m, rr); s = load(f, semis)
    n = min(len(s), int(dur * SR)); x = s[:n].copy(); r = min(int(0.06 * SR), n // 3); x[-r:] *= np.linspace(1, 0, r); return x
def held(inst, m, dur, xf=0.5):
    f, semis = nearest(inst, m); s = load(f, semis)
    head = int(0.25 * SR); mid = s[head: max(head + int(0.8 * SR), len(s) - int(0.4 * SR))]
    n = int(dur * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    k = int(xf * SR); step = max(int(0.35 * SR), len(mid) - k); pos = max(int(0.35 * SR), len(s) - len(mid) // 2 - k)
    w = np.ones(len(mid), np.float32); w[:k] = np.linspace(0, 1, k); w[-k:] = np.linspace(1, 0, k)
    while pos < n: out[pos:pos + len(mid)] += mid * w; pos += step
    out = out[:n]; r = min(int(0.35 * SR), n // 3); out[-r:] *= np.linspace(1, 0, r) ** 1.4
    a = min(int(0.08 * SR), n // 4); out[:a] *= np.linspace(0, 1, a)
    return out
P = V + 'Percussion/'
def perc(name, semis=0.0, dur=None):
    x = load(P + name, semis)
    if dur: n = min(len(x), int(dur * SR)); x = x[:n].copy(); r = min(int(0.1 * SR), n // 3); x[-r:] *= np.linspace(1, 0, r)
    return x

# ── the form ────────────────────────────────────────────────────────────────
BPM = 112.0; BEAT = 60.0 / BPM; BAR = 4 * BEAT
D, E, Fs, G, A, B, Cs = 2, 4, 6, 7, 9, 11, 1
# chords as (root pitch class, quality) — major unless 'm'
def triad(root, minor=False):
    third = 3 if minor else 4; return [root, root + third, root + 7]
CH = {'D': (D, False), 'A': (A, False), 'Bm': (B, True), 'G': (G, False), 'Em': (E, True), 'F#m': (Fs, True)}
INTRO = ['D', 'D', 'D', 'A']
A1 = ['D', 'A', 'Bm', 'G', 'D', 'A', 'G', 'A']
A2 = ['D', 'A', 'Bm', 'G', 'G', 'A', 'D', 'D']
B1 = ['G', 'D', 'A', 'Bm', 'G', 'D', 'Em', 'A']
B2 = ['G', 'D', 'A', 'Bm', 'Em', 'F#m', 'G', 'A']
TURN = ['D', 'G', 'D', 'A', 'G', 'A', 'D', 'A']
FORM = INTRO + A1 + A2 + B1 + B2 + A1 + A2 + TURN          # 4 + 48 + 8 = 60 bars
SECT = (['intro'] * 4 + ['A'] * 16 + ['B'] * 16 + ['A2'] * 16 + ['turn'] * 8)
NB = len(FORM); L = NB * BAR + 6.0; N = int(L * SR)

# the tune (midi, beats) per 8-bar phrase
TUNE_A1 = [(78, 2), (76, 1), (74, 1), (73, 3), (76, 1), (74, 2), (71, 1), (74, 1), (71, 3), (69, 1),
           (69, 1), (74, 1), (78, 2), (76, 2), (73, 1), (76, 1), (74, 1), (71, 1), (67, 1), (71, 1), (69, 4)]
TUNE_A2 = [(78, 2), (76, 1), (74, 1), (73, 3), (76, 1), (74, 2), (71, 1), (74, 1), (71, 3), (69, 1),
           (71, 2), (74, 2), (76, 2), (73, 2), (74, 4), (74, 4)]
TUNE_B1 = [(71, 2), (74, 2), (78, 3), (76, 1), (76, 2), (73, 2), (74, 4),
           (79, 2), (78, 1), (76, 1), (74, 2), (78, 2), (76, 2), (71, 2), (73, 4)]
TUNE_B2 = [(71, 2), (74, 2), (78, 3), (76, 1), (76, 2), (73, 2), (74, 4),
           (76, 2), (78, 1), (79, 1), (78, 2), (73, 2), (74, 2), (71, 2), (73, 4)]

mel = np.zeros(N, np.float32); solo = np.zeros(N, np.float32); chug = np.zeros(N, np.float32)
offs = np.zeros(N, np.float32); bass = np.zeros(N, np.float32); pad = np.zeros(N, np.float32)
drum = np.zeros(N, np.float32); bells = np.zeros(N, np.float32)

def tune(buf, inst, notes, t0, g, octave=0, harm=None):
    t = t0
    for m, beats in notes:
        d = beats * BEAT
        put(buf, held(inst, m + octave, d * 0.98), t, g)
        if harm is not None: put(buf, held(inst, m + octave - harm, d * 0.98), t, g * 0.55)
        t += d

# melody placement
bar0 = lambda b: 4.0 * BEAT * b   # a hair of lead-in is not needed: bar 0 starts at 0
tune(mel, 'vln_sus', TUNE_A1, bar0(4), 0.62, harm=3)          # A, in thirds-ish below
tune(mel, 'vln_sus', TUNE_A2, bar0(12), 0.62, harm=3)
tune(solo, 'solo', TUNE_B1, bar0(20), 0.7)                     # B: the solo violin sings
tune(solo, 'solo', TUNE_B2, bar0(28), 0.7)
tune(mel, 'vln_sus', TUNE_A1, bar0(36), 0.7, harm=3)           # A': fuller, with the octave below
tune(mel, 'vla_sus', TUNE_A1, bar0(36), 0.4, octave=-12)
tune(mel, 'vln_sus', TUNE_A2, bar0(44), 0.7, harm=3)
tune(mel, 'vla_sus', TUNE_A2, bar0(44), 0.4, octave=-12)

def pc_to(pc, lo):                 # lowest midi >= lo with that pitch class
    m = lo + ((pc - lo) % 12); return m
for b, name in enumerate(FORM):
    t = bar0(b); root, minor = CH[name]; tri = triad(root, minor); sec = SECT[b]
    # the chug: cello spiccato eighths, root–fifth–octave–fifth (wheels on rails)
    r2 = pc_to(root, 38)                                           # cello, D2 up
    pat = [r2, r2 + 7, r2 + 12, r2 + 7] * 2
    acc = [1.0, 0.62, 0.8, 0.62, 0.92, 0.62, 0.8, 0.62]
    g_ch = 0.55 if sec == 'intro' else (0.42 if sec == 'B' else 0.5)
    for i, m in enumerate(pat):
        put(chug, short('vc_spic', m, BEAT * 0.48, rr=i + b), t + i * BEAT / 2 + rng.normal(0, 0.004), g_ch * acc[i])
    # the offbeats: violas on the "and" of each beat, the chord's third and fifth
    if sec != 'intro' or b >= 2:
        third = pc_to(tri[1], 55); fifth = pc_to(tri[2], 55)
        for k in range(4):
            tt = t + k * BEAT + BEAT / 2
            put(offs, short('vla_spic', third, BEAT * 0.4, rr=k + b), tt, 0.30)
            put(offs, short('vla_spic', fifth, BEAT * 0.4, rr=k + b + 1), tt, 0.24)
            if sec in ('A2',): put(offs, short('vln_spic', pc_to(tri[0], 67), BEAT * 0.4, rr=k), tt, 0.2)
    # bass pizzicato on 1 and 3
    rb = pc_to(root, 28)
    put(bass, short('pizz', rb, BEAT * 1.6, rr=b), t, 0.9)
    put(bass, short('pizz', rb + (7 if b % 2 else 0), BEAT * 1.6, rr=b + 1), t + 2 * BEAT, 0.75)
    # a soft pad under the A' and B sections: the chord held by the sections
    if sec in ('B', 'A2'):
        for j, pc in enumerate(tri):
            put(pad, held('vc_sus' if j == 0 else 'vla_sus', pc_to(pc, 50 if j else 43), BAR * 1.02), t, 0.16)
    # drums: timpani on 1 (root D or A), snare taps on 2 and 4, triangle at the phrase heads
    if sec != 'intro' or b == 3:
        semis = (38 - 41.4) if root in (D, G, B, E) else (45 - 41.4)
        put(drum, perc('Timpani/Timpani1_Hit_v1_rr1_Sum.wav' if b % 2 else 'Timpani/Timpani1_Hit_v1_rr2_Sum.wav', semis, 1.6), t, 0.55 if sec != 'turn' else 0.4)
    if sec in ('A', 'B', 'A2'):
        for k in (1, 3):
            put(drum, perc('Snare2-taps_v2_rr%d_Sum.wav' % (1 + (b + k) % 2), 0, 0.5), t + k * BEAT, 0.32 if sec != 'B' else 0.22)
    if b % 8 == 4 and sec != 'turn':
        put(drum, perc('Triangle3-Hit_v1_rr1_Sum.wav'), t, 0.35)
    # sleigh bells on the offbeats: the jingle of the carriage (lighter in B)
    if sec in ('A', 'A2', 'turn') or (sec == 'B' and b % 2 == 0):
        for k in range(4):
            put(bells, perc('Sleighbells_Hit_v1_rr%d_Mid.wav' % (1 + k % 2), 0, 0.35), t + k * BEAT + BEAT / 2, 0.16 if sec != 'B' else 0.1)

# the intro swells in; the turn thins toward the loop point
env = np.ones(N, np.float32); tt = np.arange(N) / SR
env *= np.clip(0.35 + 0.65 * tt / (4 * BAR), 0, 1)
strings = mel + solo * 0.9 + chug + offs * 0.9 + pad + bass * 0.8
mix = reverb(hp(strings, 35), 1.9, 0.22, seed=11) + reverb(drum, 1.4, 0.16, seed=12) * 0.75 + reverb(bells, 1.2, 0.2, seed=13) * 0.7
mix = mix * env
write_mp3(rms_db(fold(mix, 4.0), -23), 'score-journey.mp3')
print('score-journey.mp3', round((N - int(4.0 * SR)) / SR, 2), 's', NB, 'bars at', BPM, 'BPM')
