#!/usr/bin/env python3
"""Chapters 1–6: the score on real instruments, the rooms, and the new sounds.

Instruments: Versilian Studios, VSCO 2 Community Edition (CC0; credit requested):
upright piano, cello / viola / violin sections, solo double bass, flute.
Recordings (Wikimedia Commons): Six Horses Galloping By (CC0), Wiehern (PD),
Howling wind (CC0), Church bells - Leverkusen 2007 (PD), Gull 1 (PD).
Deterministic (seed 1897).
"""
import numpy as np, scipy.io.wavfile as wv, scipy.signal as sg, subprocess, os, re, glob, warnings, json
warnings.filterwarnings('ignore')
SR = 48000
V = '/tmp/vsco/'
S3 = '/tmp/snd/src3/'
OUT = '/tmp/snd/ch16/'
os.makedirs(OUT, exist_ok=True)
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
def bp(x, a, b, o=2): return sg.sosfilt(sg.butter(o, [a, b], 'band', fs=SR, output='sos'), x).astype(np.float32)
def put(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i < 0: return
    n = min(len(x), len(buf) - i); buf[i:i + n] += x[:n] * g
def env(x, pts):
    t = np.arange(len(x)) / SR
    return (x * np.interp(t, [p[0] for p in pts], [p[1] for p in pts])).astype(np.float32)
def reverb(x, rt=2.4, wet=0.25, seed=5, bright=4000):
    r = np.random.default_rng(seed); n = int(rt * SR); tt = np.arange(n) / SR
    ir = lp(r.standard_normal(n) * np.exp(-6.91 * tt / rt), bright); ir /= np.sqrt(np.sum(ir ** 2))
    return ((1 - wet) * x + wet * sg.fftconvolve(x, ir)[:len(x)]).astype(np.float32)
def peak_db(x, db): return x * (10 ** (db / 20) / (np.abs(x).max() + 1e-12))
def rms_db(x, db): return x * (10 ** (db / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12))
def fold(x, xf):
    """loop: fold the last xf seconds over the first — no seam"""
    k = int(xf * SR); body = x[:-k].copy(); a = np.linspace(0, np.pi / 2, k)
    body[:k] = body[:k] * np.sin(a) + x[-k:] * np.cos(a); return body
def limit(x, c=-1.0, k=-6.0):
    c, k = 10 ** (c / 20), 10 ** (k / 20); a = np.abs(x); y = x.copy(); m = a > k
    y[m] = np.sign(x[m]) * (k + (c - k) * np.tanh((a[m] - k) / (c - k))); return y
files = {}
def write_mp3(x, name, br='160k'):
    x = limit(x); tmp = OUT + name + '.tmp.wav'; wv.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ac', '1', '-c:a', 'libmp3lame', '-b:a', br, OUT + name], check=True)
    os.remove(tmp); files[name] = round(len(x) / SR, 2)
def write_loop(x, name):
    y = sg.resample_poly(limit(x), 2, 3).astype(np.float32)
    wv.write(OUT + name, 32000, (np.clip(y, -1, 1) * 32767).astype(np.int16)); files[name] = round(len(y) / 32000, 2)

# ── the instruments ───────────────────────────────────────────────────────────
PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def midi_of(name):
    m = re.match(r'([A-G])(#?)(-?\d)', name); return (int(m.group(3)) + 1) * 12 + PC[m.group(1)] + (1 if m.group(2) else 0)
def bank(pattern, rx):
    out = {}
    for f in glob.glob(V + pattern):
        m = re.search(rx, os.path.basename(f))
        if m: out.setdefault(midi_of(m.group(1)), []).append(f)
    return out
BANK = {
    'cello':  bank('Strings/Cello Section/susvib/*.wav', r'susvib_([A-G]#?\d)_v1'),
    'viola':  bank('Strings/Viola Section/susvib/*.wav', r'susvib_([A-G]#?\d)_v1'),
    'violin': bank('Strings/Violin Section/susVib/*.wav', r'susVib_([A-G]#?\d)_v1'),
    'bass':   bank('Strings/Solo Contrabass/SusNV/*.wav', r'SusNV_([A-G]#?\d)_v1'),
    'flute':  bank('Woodwinds/Flute/expvib/*.wav', r'expvib_([A-G]#?\d)_v1'),
}
def nearest(inst, m):
    b = BANK[inst]; k = min(b, key=lambda x: abs(x - m)); return b[k][0], m - k
def held(inst, m, dur, xf=0.7):
    """a held note of any length from one recording: the attack once, then overlapped middles"""
    f, semis = nearest(inst, m); s = load(f, semis)
    head = int(0.3 * SR); mid = s[head: max(head + int(0.9 * SR), len(s) - int(0.5 * SR))]
    n = int(dur * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    k = int(xf * SR); step = max(int(0.4 * SR), len(mid) - k); pos = max(int(0.4 * SR), len(s) - len(mid) // 2 - k)
    w = np.ones(len(mid), np.float32); w[:k] = np.linspace(0, 1, k); w[-k:] = np.linspace(1, 0, k)
    while pos < n: out[pos:pos + len(mid)] += mid * w; pos += step
    out = out[:n]; r = min(int(1.2 * SR), n // 3)
    out[-r:] *= np.linspace(1, 0, r) ** 1.5
    a = min(int(0.4 * SR), n // 4); out[:a] *= np.linspace(0, 1, a)       # bowed in, never struck
    return out
def piano(m, dyn=1, dur=6.0):
    idx = int(round((m - 21) / 2)); idx -= idx % 2                        # samples every four semitones
    idx = max(0, min(44, idx)); key = 21 + 2 * idx
    if abs((key + 4) - m) < abs(key - m) and idx + 2 <= 44: idx += 2; key += 4
    x = load(V + f'Keys/Upright Piano/Player_dyn{dyn}_rr1_{idx:03d}.wav', m - key)
    n = min(len(x), int(dur * SR)); x = x[:n].copy(); r = int(0.4 * SR); x[-r:] *= np.linspace(1, 0, r)
    return x
def line(buf, inst, notes, g=1.0):
    """notes: [(start, midi, dur, gain)]"""
    for t, m, d, gg in notes: put(buf, held(inst, m, d), t, g * gg)

# ═══════════════════ DREAD — Harker's journal, on real instruments ═══════════════
# Static. The cellos and the double bass hold D and A and never move; the violas
# lean from D up to E-flat for a long while and back; the upright piano lets fall a
# few low notes far apart. Nothing arrives anywhere. 128 s, built to loop.
L = 134.0; N = int(L * SR)
strings = np.zeros(N, np.float32)
sw = lambda per, ph, n=N: (0.6 + 0.4 * np.sin(2 * np.pi * np.arange(n) / SR / per + ph)).astype(np.float32)
strings += held('bass', 26, L) * sw(29, 0.4) * 0.45                       # D1
strings += held('cello', 38, L) * sw(23, 0.0) * 0.55                      # D2
strings += held('cello', 45, L) * sw(31, 1.7) * 0.42                      # A2
vio = np.zeros(N, np.float32)                                              # D3, leaning to Eb3 and back
for t0, t1, m in [(0, 24, 50), (22, 46, 51), (44, 90, 50), (88, 110, 51), (108, L, 50)]:
    put(vio, held('viola', m, t1 - t0 + 2), t0, 0.32)
strings += vio * sw(19, 2.9)
pno = np.zeros(N, np.float32)
for t, m in [(4, 38), (13.5, 46), (21, 41), (33.5, 39), (44, 38), (57, 45), (66.5, 46), (78, 40), (91, 38), (101.5, 41), (113, 39)]:
    put(pno, piano(m, 1, 9.0), t, 0.55 + 0.15 * rng.random())
dread = reverb(strings, 2.4, 0.22, seed=6) + reverb(pno, 3.2, 0.38, seed=7) * 0.9
write_mp3(rms_db(fold(dread, 6.0), -22), 'score-dread.mp3')

# ═══════════════════ PASTORAL — the Whitby letters: warm, then souring ══════════════
# F major, never leaving it. WARM: I – V6 – vi – IV – I6 – ii – V – I, strings
# breathing, the piano in broken chords, the flute singing a little.
# SOUR: the same key, the same pace, but the chords curdle — the iv turns minor,
# the flat sixth intrudes, the flute is gone and a viola holds an E against the F.
CH = {  # (bass, [inner...]) midi
    'F':    (41, [53, 57, 60, 65]), 'C/E': (40, [52, 55, 60, 64]), 'Dm': (38, [53, 57, 62, 65]),
    'Bb':   (34, [53, 58, 62, 65]), 'F/A': (45, [53, 57, 60, 65]), 'Gm': (43, [55, 58, 62, 67]),
    'C':    (36, [52, 55, 60, 64]), 'Bbm':  (34, [53, 58, 61, 65]), 'Db':  (37, [53, 56, 61, 65]),
    'Gm7b5': (43, [55, 58, 61, 65]), 'C7':  (36, [52, 55, 58, 64]), 'Fsus': (41, [53, 58, 60, 65])}
def pastoral(prog, flute_phrases, sour=False, L=96.0, seed=0):
    global rng; rng = np.random.default_rng(300 + seed)
    N = int((L + 6) * SR); st = np.zeros(N, np.float32); pn = np.zeros(N, np.float32); fl = np.zeros(N, np.float32)
    seg = L / len(prog)
    for i, c in enumerate(prog):
        t = i * seg; b, inner = CH[c]
        put(st, held('cello' if b >= 36 else 'bass', b, seg + 1.6), t, 0.42)
        put(st, held('viola', inner[0], seg + 1.6), t, 0.26)
        put(st, held('violin', inner[2], seg + 1.6), t, 0.2)
        put(st, held('violin', inner[3], seg + 1.6), t, 0.15)
        # piano: broken chord, gentle, a quaver at 60 bpm
        pat = [b + 12, inner[0], inner[1], inner[2], inner[3], inner[2], inner[1], inner[0]] if not sour else [b + 12, inner[1], inner[3], inner[1]]
        step = seg / (len(pat) * (1 if not sour else 1))
        for k, m in enumerate(pat):
            put(pn, piano(m, 1, 4.0), t + k * step, (0.42 if not sour else 0.36) * (1.0 if k == 0 else 0.8))
    if sour:
        put(st, held('viola', 64, L), 0, 0.11)                              # an E held against the F, never resolving
    for t, notes in flute_phrases:
        tt = t
        for m, d in notes:
            put(fl, held('flute', m, d + 0.25, xf=0.5), tt, 0.24); tt += d
    x = reverb(st, 2.2, 0.22, seed=8) + reverb(pn, 2.4, 0.26, seed=9) * 0.9 + reverb(fl, 2.6, 0.3, seed=10)
    return fold(x[: int((L + 6) * SR)], 6.0)
warm = pastoral(['F', 'C/E', 'Dm', 'Bb', 'F/A', 'Gm', 'C', 'F', 'Dm', 'Bb', 'C', 'F'],
                [(8, [(69, 1.5), (67, 1.0), (65, 1.5), (67, 2.0)]), (40, [(72, 2.0), (70, 1.0), (69, 1.0), (67, 2.5)]),
                 (72, [(69, 1.0), (70, 1.0), (72, 2.0), (69, 2.5)])], seed=1)
write_mp3(rms_db(warm, -23), 'score-pastoral-warm.mp3')
sour = pastoral(['F', 'Dm', 'Bbm', 'F/A', 'Db', 'Gm7b5', 'C7', 'Fsus', 'Dm', 'Bbm', 'Db', 'F'], [], sour=True, seed=2)
write_mp3(rms_db(sour, -24), 'score-pastoral-sour.mp3')

# ═══════════════════ PHONOGRAPH — Seward's diary, spoken onto wax ═════════════════
# The crackle tier: hiss, wax crackle, a slow wow, the faint turn of the cylinder.
r = np.random.default_rng(91); L = 24.0; N = int(L * SR)
hiss = bp(r.standard_normal(N), 1800, 7000) * 0.12
cr = np.zeros(N, np.float32); ix = r.choice(N, int(L * 34), replace=False)
cr[ix] = (r.standard_normal(len(ix)) * r.random(len(ix)) ** 3).astype(np.float32)
cr = bp(cr, 900, 6000) * 1.2
big = np.zeros(N, np.float32); ib = r.choice(N, int(L * 1.2), replace=False); big[ib] = r.choice([-1, 1], len(ib)) * 0.9
big = lp(big, 2500)
turn = lp(r.standard_normal(N), 90) * (0.6 + 0.4 * np.sin(2 * np.pi * np.arange(N) / SR * (160 / 60)))   # 160 rpm cylinder
wow = 0.82 + 0.18 * np.sin(2 * np.pi * np.arange(N) / SR * 0.55)
ph = (hiss + cr + big + turn * 0.25) * wow
ph = np.concatenate([ph, ph[:int(2 * SR)]]); ph = fold(ph, 2.0)
write_loop(rms_db(ph, -36), 'phonograph-crackle.wav')

# ═══════════════════ THE ROOMS ═══════════════════════════════════════════════════
# pass: the Borgo Pass — high wind, snow, emptiness (Howling wind, CC0)
w = load(S3 + 'Howling_wind.wav')[int(10 * SR): int(80 * SR)]
w = hp(w, 60)
write_mp3(rms_db(fold(reverb(w, 1.4, 0.2), 4.0), -24), 'wind.mp3')
# london_interior: a quiet clinical room, a fire low, the street muffled beyond glass
r = np.random.default_rng(92); N = int(68 * SR)
room = lp(np.cumsum(r.standard_normal(N)) * 0.002, 300); room = hp(room, 30)
street = lp(r.standard_normal(N), 260, 3) * (0.7 + 0.3 * np.sin(2 * np.pi * np.arange(N) / SR / 11.0))
t = 3.0
while t < 64:                                                              # a cart going by, far off and muffled
    d = 4 + 3 * r.random(); n = int(d * SR); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    hooves = np.zeros(n, np.float32); hk = np.arange(0, n, int(SR * 0.19)); hooves[hk[hk < n]] = 1
    put(street, lp(hooves, 600) * e * 2.0 + lp(r.standard_normal(n), 400) * e * 0.4, t); t += 9 + 9 * r.random()
lr = rms_db(room, -40) + rms_db(street, -36)
write_mp3(rms_db(fold(reverb(lr, 0.8, 0.2), 4.0), -30), 'london.mp3')

# ═══════════════════ ONE-SHOTS ═══════════════════════════════════════════════════
def oneshot(src, a, b, name, db, fin=0.05, fout=0.8, room=(1.2, 0.2), band=None):
    x = load(src)[int(a * SR): int(b * SR)]
    if band: x = bp(x, *band)
    x = env(x, [(0, 0), (fin, 1), (len(x) / SR - fout, 1), (len(x) / SR, 0)])
    if room: x = reverb(np.concatenate([x, np.zeros(int(room[0] * SR), np.float32)]), room[0], room[1])
    write_mp3(peak_db(x, db), name)
oneshot(S3 + 'Six_Horses_Galloping_By.wav', 4.0, 16.0, 'horses-gallop.mp3', -9, fin=1.5, fout=2.5)
oneshot(S3 + 'Wiehern.wav', 0.0, 2.25, 'horse-neigh.mp3', -10, fin=0.01, fout=0.3)
oneshot(S3 + 'Church_bells_-_Leverkusen_2007.wav', 2.0, 16.0, 'church-bells.mp3', -14, fin=0.8, fout=3.0, room=(2.0, 0.25))
oneshot(S3 + 'Gull_1.wav', 0.0, 8.0, 'gulls.mp3', -18, fin=0.3, fout=1.5, room=(1.5, 0.2))
# the clock striking the hour: struck bell partials, four strokes
r = np.random.default_rng(93); N = int(9 * SR); clk = np.zeros(N, np.float32)
def bell(f0, n=int(4.5 * SR)):
    t = np.arange(n) / SR; y = np.zeros(n)
    for ratio, a, dec in [(0.5, .5, 1.0), (1.0, 1.0, 1.6), (1.19, .45, 2.4), (1.5, .35, 3.0), (2.0, .3, 3.5), (2.74, .2, 5.0), (3.0, .15, 6.0)]:
        y += a * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-t * dec)
    y *= np.minimum(1, t / 0.003); return y.astype(np.float32)
for k in range(4): put(clk, bell(392.0 * (1 + 0.003 * r.random())), 0.1 + k * 1.6, 1.0 - 0.06 * k)
write_mp3(peak_db(reverb(clk, 1.8, 0.3), -15), 'clock-strike.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k, v in files.items(): print(f'{k:28s} {v:7.2f}s')
