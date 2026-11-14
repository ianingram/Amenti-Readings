#!/usr/bin/env python3
"""Wagner, Der fliegende Holländer, Overture, bars 1-23 (about 60 s), played on
VSCO 2 CE (CC0) from the public-domain full score (Wiener Philharmonischer Verlag
No. 20, archive.org/details/overturetoflying00wagn). A test for Ian: our clean
instruments playing the real thing.  Allegro con brio, half = 72, 6/4.
Simplified where the reading was uncertain; the horn call, the open fifths, the
chromatic storm in the low strings, the brass answer, the two great chords and
the falling line at bar 21 are as written.
usage: dutchman.py <out.mp3>"""
import sys, os, re, glob, subprocess
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wv
OUTF = sys.argv[1]
JR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "dracula", "sound", "build-journey.py")
src = open(JR).read().split('# ── the form')[0]
sys.argv = [sys.argv[0], os.path.dirname(os.path.abspath(OUTF)) + '/']
exec(src)

_c2 = {}
def load(path, semis=0.0):                # build-journey's, but scaled by the file's sample format
    k = (path, round(semis, 4))
    if k in _c2: return _c2[k]
    sr, x = wv.read(path)
    sc = {np.dtype('int16'): 32768.0, np.dtype('int32'): 2147483648.0, np.dtype('uint8'): 128.0}.get(x.dtype, 1.0)
    x = x.astype(np.float32) / sc
    if x.ndim > 1: x = x.mean(1)
    ratio = SR / sr * (2 ** (-semis / 12))
    if abs(ratio - 1) > 1e-6: x = sg.resample_poly(x, int(round(ratio * 1000)), 1000).astype(np.float32)
    _c2[k] = x; return x
def held(inst, m, dur, xf=0.5):          # build-journey's, safe for short samples
    f, semis = nearest(inst, m); s = load(f, semis)
    head = min(int(0.25 * SR), len(s) // 4); tail = min(int(0.4 * SR), len(s) // 4)
    mid = s[head: len(s) - tail]
    n = int(dur * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    if n > len(s) - tail:
        k = min(int(xf * SR), len(mid) // 3); step = len(mid) - k; pos = len(s) - tail - k
        w = np.ones(len(mid), np.float32); w[:k] = np.linspace(0, 1, k); w[-k:] = np.linspace(1, 0, k)
        out[pos + k:] *= 0
        while pos < n: out[pos:pos + len(mid)] += mid * w; pos += step
    out = out[:n]; r = min(int(0.35 * SR), n // 3); out[-r:] *= np.linspace(1, 0, r) ** 1.4
    a = min(int(0.08 * SR), n // 4); out[:a] *= np.linspace(0, 1, a)
    return out
def bank2(pattern, rx, prefs=('v3', 'v2', 'v1', '')):
    for v in prefs:
        b = bank(pattern, rx.replace('VV', v))
        if b: return b
    raise SystemExit('empty ' + pattern)
BANK.update({
    'vln_trem': bank2('Strings/Violin Section/Trem/*.wav', r'Trem_([A-G]#?\d)_VV', ('v2', 'v1')),
    'vla_trem': bank2('Strings/Viola Section/trem/*.wav', r'trem_([A-G]#?\d)_VV', ('v2', 'v1')),
    'vc_trem':  bank2('Strings/Cello Section/trem/*.wav', r'trem_([A-G]#?\d)_VV', ('v2', 'v1')),
    'kb_trem':  bank2('Strings/Solo Contrabass/Trem/*.wav', r'Trem_([A-G]#?\d)_VV', ('v2', 'v1')),
    'kb_sus':   bank2('Strings/Solo Contrabass/SusVib/*.wav', r'SusVib_([A-G]#?\d)_VV', ('v3', 'v1')),
    'horn':     bank2('Brass/F Horn/sus/*.wav', r'MOHorn_sus_([A-G]#?\d)_VV'),
    'horn_p':   bank2('Brass/F Horn/sus/*.wav', r'MOHorn_sus_([A-G]#?\d)_VV', ('v2', 'v1')),
    'tpt':      bank2('Brass/Trumpet/sus/*.wav', r'_sus_([A-G]#?\d)_VV'),
    'tbn':      bank2('Brass/Tenor Trombone/sus/*.wav', r'_sus_([A-G]#?\d)_VV'),
    'tuba':     bank2('Brass/Tuba/sus/*.wav', r'_sus_([A-G]#?\d)_VV_rr1'),
    'bsn':      bank2('Woodwinds/Bassoon/sus/*.wav', r'PSBassoon_([A-G]#?\d)_VV'),
    'picc':     bank('Woodwinds/Piccolo/Sus/*.wav', r'piccolo_([A-G]#?\d)_sustain'),
    'kb_spic':  bank2('Strings/Solo Contrabass/Spic/*.wav', r'Spic_([A-G]#?\d)_VV', ('v2', 'v3', 'v1')),
    'flute':    bank2('Woodwinds/Flute/susNV/*.wav', r'susNV_([A-G]#?\d)_VV', ('v3', 'v1')),
    'oboe':     bank('Woodwinds/Oboe/Sus/*.wav', r'_([A-G]#?\d)_'),
    'clar':     bank('Woodwinds/Clarinet/susLong/*.wav', r'susLong_([A-G]#?\d)_v2_rr1'),
})
for k in ('oboe', 'clar', 'picc'):
    if not BANK[k]: raise SystemExit('empty ' + k)

Q = 60 / 144.0; BAR = 6 * Q; T0 = 0.4; NB = 23; L = T0 + NB * BAR + 4.5
def T(b, beat=1.0): return T0 + (b - 1) * BAR + (beat - 1) * Q
N = int(L * SR)
BUS = {k: np.zeros(N, np.float32) for k in
       ('vln', 'vla', 'vc', 'kb', 'picc', 'fl', 'ob', 'cl', 'bsn', 'hn', 'tpt', 'tbn', 'tuba', 'timp')}
PAN = {'vln': -0.55, 'vla': 0.15, 'vc': 0.45, 'kb': 0.6, 'picc': -0.1, 'fl': -0.2, 'ob': 0.05, 'cl': -0.1,
       'bsn': 0.15, 'hn': -0.3, 'tpt': 0.25, 'tbn': 0.4, 'tuba': 0.5, 'timp': 0.0}

def note(bus, inst, m, t, d, g=1.0, att=0.03, legato=0.15):
    x = held(inst, m, d + legato, xf=0.35)
    a = min(int(att * SR), len(x) // 4); x[:a] *= np.linspace(0, 1, a)
    put(BUS[bus], x, t, g)
def chord(bus, inst, ms, t, d, g=1.0, **k):
    for i, m in enumerate(ms): note(bus, inst, m, t + 0.006 * i, d, g / np.sqrt(len(ms)) * 1.3, **k)
def run(bus, inst, ms, t, step=Q / 2, g=1.0):
    for i, m in enumerate(ms):
        x = short(inst, m, step + 0.09, rr=i)
        a = min(int(0.012 * SR), len(x) // 4); x[:a] *= np.linspace(0, 1, a)
        put(BUS[bus], x, t + i * step, g)
def roll(m, t, d, g=1.0, src='Timpani1_Roll_v5_rr1_Sum.wav', base=42.4):
    x = load(V + 'Percussion/Timpani/Rolls/' + src, m - base)
    body = x[int(0.3 * SR): len(x) - int(0.5 * SR)]
    n = int(d * SR); out = np.zeros(n + SR, np.float32); out[:len(x)] += x[:n + SR]
    k = int(0.4 * SR); pos = len(x) - int(0.5 * SR) - k
    w = np.ones(len(body), np.float32); w[:k] = np.linspace(0, 1, k); w[-k:] = np.linspace(1, 0, k)
    while pos < n: out[pos:pos + len(body)] += body * w; pos += len(body) - k
    out = out[:n]; r = min(int(0.3 * SR), n // 3); out[-r:] *= np.linspace(1, 0, r)
    put(BUS['timp'], out, t, g)
def hit(m, t, g=1.0):
    src, base = ('Timpani1_Hit_v3_rr1_Sum.wav', 41.5) if m < 48 else ('Timpani2_Hit_v3_rr1_Sum.wav', 46.6)
    put(BUS['timp'], load(V + 'Percussion/Timpani/' + src, m - base), t, g)

D2, A2, D3, A3, D4, A4, D5, A5, D6 = 38, 45, 50, 57, 62, 69, 74, 81, 86

# ── bars 1-12: the open fifth, the call, the storm rising ─────────────────────
def lev(b):                      # the strings' and winds' dynamic: f, p, then molto cresc. to bar 12
    if b <= 2: return 1.0
    if b <= 5: return 0.38
    return 0.42 + (b - 6) / 6 * 0.6
for b in range(1, 13):
    g = lev(b)
    for half in (1, 4):
        t = T(b, half)
        chord('vln', 'vln_trem', [D5, A5, D6], t, 3 * Q, 1.0 * g, att=0.01)
        chord('vln', 'vln_trem', [A4, D5, A5], t + 0.01, 3 * Q, 0.8 * g, att=0.01)
        if b < 10: chord('vla', 'vla_trem', [D4, A4], t, 3 * Q, 0.8 * g, att=0.01)
# winds: flutes and clarinets hold the fifth; oboes and trumpets bars 1-2 only, oboes back at 6
chord('fl', 'flute', [A5, D6], T(1), 12 * BAR, 0.55, att=0.05)
chord('cl', 'clar', [A4, D5], T(1), 12 * BAR, 0.5, att=0.05)
chord('ob', 'oboe', [D5, A5], T(1), 2 * BAR + Q, 0.6, att=0.04)
chord('ob', 'oboe', [D5, A5], T(6), 7 * BAR, 0.45, att=0.8)
chord('tpt', 'tpt', [A4, D5], T(1), 2 * BAR + Q, 0.5, att=0.04)
# THE DUTCHMAN'S CALL: horns (four) and bassoons, f molto marcato
CALL = [(A3, 1, 2, 6), (D4, 3, 3, 1), (D4, 2, 3, 4), (A3, 1, 3, 6),
        (D4, 2, 4, 1), (D4, 1, 4, 3), (A4, 5, 4, 4),
        (D4, 1, 5, 3), (D4, 2, 5, 4), (D4, 1, 5, 6),
        (A4, 3, 6, 1), (A4, 3, 6, 4)]
for m, q, b, beat in CALL:
    acc = 1.25 if (b == 6 and beat == 4) else 1.0
    note('hn', 'horn', m, T(b, beat), q * Q * 0.97, 1.35 * acc, att=0.02, legato=0.05)
    note('hn', 'horn', m, T(b, beat) + 0.012, q * Q * 0.97, 0.9 * acc, att=0.02, legato=0.05)
    note('bsn', 'bsn', m - 12, T(b, beat), q * Q * 0.97, 0.6, att=0.02, legato=0.05)
note('bsn', 'bsn', D3, T(6), 6 * BAR, 0.4, att=1.0)
# horns: accented A twice a bar, a grace note from below, bars 7-12
for b in range(7, 13):
    for beat in (1, 4):
        t = T(b, beat)
        note('hn', 'horn', 67, t - 0.07, 0.07, 0.4, att=0.005, legato=0.02)
        note('hn', 'horn', A4, t, 3 * Q * 0.92, 0.75 + 0.05 * (b - 7), att=0.015)
        note('hn', 'horn', A4, t + 0.015, 3 * Q * 0.92, 0.5, att=0.015)
roll(D3, T(6), 7 * BAR, 0.35, src='Timpani2_Roll_v5_rr1_Sum.wav', base=47.6)
# the storm: low strings in chromatic waves (basses an octave below, to bar 9)
WAVES = {6: [45, 45, 44, 45, 46, 45, 45, 44, 45, 46, 45, 46],
         7: [44, 45, 45, 46, 45, 46, 47, 48, 48, 49, 48, 49],
         8: [50, 51, 50, 52, 53, 54, 53, 54, 55, 54, 55, 56],
         9: [56, 57, 57, 58, 59, 60, 60, 61, 62, 61, 62, 63],
         10: [50, 51, 50, 52, 53, 52, 53, 54, 53, 55, 54, 55],
         11: [56, 57, 56, 57, 58, 59, 58, 59, 60, 59, 60, 61],
         12: [62, 61, 62, 63, 62, 63, 64, 63, 64, 65, 66, 67]}
for b, ms in WAVES.items():
    g = 0.5 + (b - 6) * 0.09
    run('vc', 'vc_spic', ms, T(b), g=g)
    if b <= 9: run('kb', 'kb_spic', [m - 12 for m in ms], T(b), g=0.8 * g)
    if b >= 10: run('vla', 'vla_spic', [m + 12 for m in ms], T(b), g=0.7 * g)
note('kb', 'kb_sus', D2, T(10), Q, 1.0)
# the brass answer the call: trombones (fifths) and tuba, f molto marcato
ANS = [(A2, 1, 9, 6), (D3, 3, 10, 1), (D3, 2, 10, 4), (A2, 1, 10, 6),
       (D3, 2, 11, 1), (D3, 1, 11, 3), (A3, 5, 11, 4),
       (D3, 1, 12, 3), (D3, 2, 12, 4), (D3, 1, 12, 6)]
for m, q, b, beat in ANS:
    d = q * Q * 0.95; t = T(b, beat)
    chord('tbn', 'tbn', [m + 12, m + 19], t, d, 0.95, att=0.02, legato=0.05)
    note('tuba', 'tuba', m, t, d, 0.9, att=0.02, legato=0.05)

# ── bars 13-20: the great chords and the gusts ────────────────────────────────
GREAT = dict(vln=[76, 82, 88], vln2=[73, 79, 85], vla=[61, 67], vc=[49, 61],
             wind=[79, 82, 85, 88], hn=[67, 70], tpt=[73, 76], tbn=[52, 55, 58])
def great(b):                    # two bars ff on the dominant (A, C#, E, G, B-flat), then the stab
    for bb in (b, b + 1):
        for half in (1, 4):
            t = T(bb, half)
            chord('vln', 'vln_trem', GREAT['vln'], t, 3 * Q, 1.25, att=0.008)
            chord('vln', 'vln_trem', GREAT['vln2'], t, 3 * Q, 1.05, att=0.008)
            chord('vla', 'vla_trem', GREAT['vla'], t, 3 * Q, 1.0, att=0.008)
            chord('vc', 'vc_trem', GREAT['vc'], t, 3 * Q, 1.0, att=0.008)
    d = 2 * BAR
    chord('fl', 'flute', GREAT['wind'][1:], T(b), d, 0.9, att=0.02)
    note('picc', 'picc', 93, T(b), d, 0.45, att=0.03)
    chord('ob', 'oboe', [76, 82], T(b), d, 0.8, att=0.02)
    chord('cl', 'clar', [73, 79], T(b), d, 0.8, att=0.02)
    chord('bsn', 'bsn', [49, 61], T(b), d, 0.8, att=0.02)
    chord('hn', 'horn', GREAT['hn'], T(b), d, 1.2, att=0.02)
    chord('tpt', 'tpt', GREAT['tpt'], T(b), d, 0.9, att=0.02)
    chord('tbn', 'tbn', GREAT['tbn'], T(b), d, 1.1, att=0.02)
    note('tuba', 'tuba', A2 - 12 if b > 13 else A2, T(b), d if b > 13 else Q, 0.9)
    hit(D3 if b == 13 else A2, T(b), 1.1)
    # the stab that ends it
    t = T(b + 2)
    chord('vln', 'vln_spic', [80, 81, 85], t, Q, 1.3)
    chord('fl', 'flute', [80, 85], t, Q, 0.9, att=0.01)
    chord('ob', 'oboe', [76, 80], t, Q, 0.8, att=0.01)
    chord('tbn', 'tbn', [52, 55, 61], t, Q, 1.0, att=0.01)
    chord('hn', 'horn', [69, 73], t, Q, 1.0, att=0.01)
def gust(b):                     # rising chromatic eighths (b), falling (b+1); the winds' figure; timpani on A
    up = lambda s, n=12: list(range(s, s + n))
    run('vln', 'vln_spic', up(61), T(b), g=0.8)                   # second violins
    run('vln', 'vln_spic', up(66, 6), T(b, 4), g=0.8)             # first violins join
    run('vla', 'vla_spic', up(49), T(b), g=0.8)
    run('vc', 'vc_spic', up(37), T(b), g=0.85)
    run('kb', 'kb_spic', up(25), T(b), g=0.6)
    dn = lambda s, n=12: list(range(s, s - n, -1))
    run('vln', 'vln_spic', dn(82, 8), T(b + 1), g=1.1)
    run('vln', 'vln_spic', dn(71), T(b + 1), g=1.0)
    run('vla', 'vla_spic', dn(61), T(b + 1), g=1.0)
    run('vc', 'vc_spic', dn(49), T(b + 1), g=1.0)
    run('kb', 'kb_spic', dn(37), T(b + 1), g=0.7)
    for bb in (b, b + 1):
        if bb == b + 1: chord('hn', 'horn', [57, 63], T(bb), Q, 0.9, att=0.01)
        for (lo, hi, inst, bus, g) in ((56, 57, 'horn', 'hn', 0.9), (68, 69, 'tpt', 'tpt', 0.7), (44, 45, 'bsn', 'bsn', 0.7)):
            note(bus, inst, lo, T(bb, 3), Q / 2, g, att=0.01, legato=0.02)
            note(bus, inst, hi, T(bb, 3.5), Q / 2, g, att=0.01, legato=0.02)
        chord('hn', 'horn', [57, 63], T(bb, 4), 3 * Q, 1.1, att=0.012)
        chord('tpt', 'tpt', [69, 75], T(bb, 4), 3 * Q, 0.8, att=0.012)
        chord('bsn', 'bsn', [49, 57], T(bb, 4), 3 * Q, 0.7, att=0.012)
    roll(A2, T(b), 2 * BAR, 0.75)
great(13); gust(15); great(17); gust(19)

# ── bars 21-23: the falling line over a falling bass, to the D-minor six-four ──
LINE = [(81, 9, 21), (80, 3, 22), (79, 3, 22.5), (78, 3, 23), (77, 3, 23.5)]
HARM = [(21, 1, 48, [51, 54, 57]), (21, 4, 47, [50, 53, 57]), (22, 1, 46, [50, 52, 56]),
        (22, 4, 46, [49, 52, 55]), (23, 1, 45, [50, 54, 57]), (23, 4, 45, [50, 53, 57])]
for m, q, b in LINE:
    bb, beat = int(b), 1 if b == int(b) else 4
    d = q * Q + (3.5 if bb == 23 and beat == 4 else 0)
    note('picc', 'picc', m + 12, T(bb, beat), d, 0.5, att=0.02)
    note('fl', 'flute', m, T(bb, beat), d, 0.8, att=0.02)
    note('hn', 'horn', m - 12, T(bb, beat), d, 1.1, att=0.02)
    note('hn', 'horn', m - 12, T(bb, beat) + 0.012, d, 0.8, att=0.02)
for b, beat, bass, up3 in HARM:
    last = (b == 23 and beat == 4)
    d = 3 * Q + (3.5 if last else 0); t = T(b, beat)
    chord('ob', 'oboe', [u + 12 for u in up3], t, d, 0.8, att=0.02)
    chord('cl', 'clar', [u + 12 for u in up3], t, d, 0.8, att=0.02)
    chord('bsn', 'bsn', up3, t, d, 0.8, att=0.02)
    chord('tbn', 'tbn', up3, t, d, 1.0, att=0.02)
    note('tuba', 'tuba', bass - 12, t, d, 1.0, att=0.02)
    note('kb', 'kb_sus', bass - 12, t, d, 1.0, att=0.02)
    note('vc', 'vc_trem', bass, t, d, 1.0, att=0.01)
    chord('vln', 'vln_trem', [u + 24 for u in up3], t, d, 1.15, att=0.01)
    chord('vla', 'vla_trem', [u + 12 for u in up3[:2]], t, d, 0.9, att=0.01)
roll(D3, T(22), BAR, 0.8, src='Timpani2_Roll_v5_rr1_Sum.wav', base=47.6)
roll(A2, T(23), BAR + 3.5, 0.8)

# winds follow the strings' dynamic through bar 12 (f, p, molto cresc.)
tt = np.arange(N) / SR; bpos = (tt - T0) / BAR + 1
env = np.interp(bpos, [0, 2.95, 3.05, 6.0, 12.9, 13.0], [1.0, 1.0, 0.38, 0.42, 1.0, 1.0]).astype(np.float32)
for k in ('fl', 'cl', 'ob'): BUS[k] *= env
import os as _o
if _o.environ.get('DBG'):
    for k,x in BUS.items():
        print(k.ljust(5), ' '.join('%4d'%round(20*np.log10(np.sqrt(np.mean(x[int(T(b)*SR):int(T(b+1)*SR)]**2))+1e-9)) for b in range(1,24)))
    raise SystemExit
# ── mix: seating, a hall, the level ───────────────────────────────────────────
LEVEL = {'vln': 0.55, 'vla': 0.5, 'vc': 0.6, 'kb': 1.1, 'picc': 0.25, 'fl': 0.35, 'ob': 0.6, 'cl': 0.32,
         'bsn': 0.4, 'hn': 0.55, 'tpt': 0.35, 'tbn': 0.45, 'tuba': 0.5, 'timp': 1.1}
Lch = np.zeros(N, np.float32); Rch = np.zeros(N, np.float32)
for k, x in BUS.items():
    p = (PAN[k] + 1) * np.pi / 4; x = x * LEVEL[k]
    Lch += x * np.cos(p); Rch += x * np.sin(p)
def hall(x, seed):
    r = np.random.default_rng(seed); n = int(2.6 * SR); tt = np.arange(n) / SR
    ir = lp(r.standard_normal(n) * np.exp(-6.91 * tt / 2.6), 4500); ir /= np.sqrt(np.sum(ir ** 2))
    pre = int(0.02 * SR); ir = np.concatenate([np.zeros(pre, np.float32), ir])
    return sg.fftconvolve(x, ir)[:len(x)].astype(np.float32)
wet = 0.3
Lo = (1 - wet) * Lch + wet * hall(Lch, 11); Ro = (1 - wet) * Rch + wet * hall(Rch, 12)
st = np.stack([Lo, Ro], 1); st /= np.abs(st).max() / 0.89
f = np.ones(N, np.float32); r = int(3.0 * SR); f[-r:] = np.linspace(1, 0, r) ** 1.5; st *= f[:, None]
tmp = OUTF + '.wav'; wv.write(tmp, SR, (st * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'highpass=f=32,loudnorm=I=-16:TP=-1.5', '-ar', '44100',
                '-c:a', 'libmp3lame', '-b:a', '192k',
                '-metadata', 'title=The Flying Dutchman, overture bars 1-23 (test)', '-metadata', 'artist=Wagner; VSCO 2 CE', OUTF], check=True)
os.remove(tmp); print('wrote', OUTF, round(L, 1), 's')
