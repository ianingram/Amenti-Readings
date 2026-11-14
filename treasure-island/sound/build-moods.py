#!/usr/bin/env python3
"""Mood strings for Treasure Island · 14 Nov 2026.
Ian: "the flying dutchman is a good score... but its complex. some general mood
strings and 4/4 time will be useful." So: plain underscore, strings only, 4/4,
16 bars each, made to sit under the voice and loop: sustained chords that swell
and ease each bar, a bass, and at most one quiet pulse. VSCO 2 CE (CC0).
usage: build-moods.py [out dir]   (writes mood-<name>.mp3)"""
import sys, os, subprocess
import numpy as np, scipy.signal as sg
OUTDIR = (sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))).rstrip('/') + '/'
JR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'dracula', 'sound', 'build-journey.py')
sys.argv = [sys.argv[0], OUTDIR]
exec(open(JR).read().split('# ── the form')[0])
BANK.update({
    'kb_sus': bank('Strings/Solo Contrabass/SusVib/*.wav', r'SusVib_([A-G]#?\d)_v1'),
    'vc_pizz': bank('Strings/Cello Section/pizzT/*.wav', r'_([A-G]#?\d)_'),
})
if not BANK['kb_sus']: BANK['kb_sus'] = bank('Strings/Solo Contrabass/SusVib/*.wav', r'SusVib_([A-G]#?\d)_')
if not BANK['vc_pizz']: BANK['vc_pizz'] = BANK['pizz']

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
QUAL = {'': (0, 4, 7), 'm': (0, 3, 7), 'sus': (0, 5, 7), '7': (0, 4, 7, 10), 'm7': (0, 3, 7, 10), 'add9': (0, 4, 7, 14), 'dim': (0, 3, 6)}
def parse(c):
    r = c[:2] if len(c) > 1 and c[1] in '#b' else c[:1]; q = c[len(r):]
    return NOTE[r], QUAL[q]
def voice(prev, root, q, lo=55, hi=79, n=4):
    """four upper voices (viola + violins) from the chord, each moving as little as it can"""
    pcs = [(root + i) % 12 for i in q]
    cands = sorted(m for m in range(lo, hi + 1) if m % 12 in pcs)
    if prev is None:
        mid = (lo + hi) // 2; out = []
        for pc in (pcs * 2)[:n]:
            out.append(min((m for m in cands if m % 12 == pc and m not in out), key=lambda m: abs(m - mid)))
        return sorted(out)
    out = []
    for p in prev:
        m = min((m for m in cands if m not in out), key=lambda m: abs(m - p) + (0.5 if m % 12 in [x % 12 for x in out] else 0))
        out.append(m)
    for pc in pcs[:3]:                       # keep the chord's root, third, fifth present
        if pc not in [m % 12 for m in out]:
            i = max(range(len(out)), key=lambda i: [m % 12 for m in out].count(out[i] % 12))
            out[i] = min((m for m in cands if m % 12 == pc), key=lambda m: abs(m - out[i]))
    return sorted(out)

def swell(n, shape):
    t = np.linspace(0, 1, n)
    if shape == 'breath': return (0.72 + 0.28 * np.sin(np.pi * t) ** 1.2).astype(np.float32)
    if shape == 'flat': return np.ones(n, np.float32)
    return (0.8 + 0.2 * np.sin(np.pi * t)).astype(np.float32)

def mood(name, bpm, chords, pulse=None, shape='breath', top=None, lo=55, hi=79, level=1.0):
    beat = 60 / bpm; bar = 4 * beat; T0 = 0.3; nb = len(chords)
    L = T0 + nb * bar + 5.0; N = int(L * SR)
    up = np.zeros(N, np.float32); vc = np.zeros(N, np.float32); kb = np.zeros(N, np.float32); pu = np.zeros(N, np.float32)
    prev = None
    for b, c in enumerate(chords):
        root, q = parse(c); t = T0 + b * bar
        v = voice(prev, root, q, lo, hi); prev = v
        for i, m in enumerate(v):
            inst = 'vla_sus' if i == 0 and m < 64 else 'vln_sus'
            x = held(inst, m, bar + 0.6, xf=0.3); x[:len(x)] *= swell(len(x), shape)
            a = int(0.25 * SR); x[:a] *= np.linspace(0, 1, a)
            put(up, x, t - 0.05 + 0.01 * i, 0.55)
        bass = 36 + (root - 0) % 12 if (36 + root % 12) >= 38 else 48 + root % 12
        x = held('vc_sus', bass + 12, bar + 0.6, xf=0.3) * swell(int((bar + 0.6) * SR), shape)[:len(held('vc_sus', bass + 12, bar + 0.6, xf=0.3))]
        put(vc, x, t - 0.05, 0.6)
        put(kb, held('kb_sus', bass, bar + 0.6, xf=0.3), t - 0.05, 0.55)
        if pulse:
            for k, (pos, deg, g) in enumerate(pulse):        # (beat, chord-tone index, gain)
                m = bass + 12 + [0, q[1], q[2], 12][deg]
                inst = 'vc_pizz' if pulse is not None and g > 0 else 'vc_pizz'
                put(pu, short(inst, m, beat * 1.5, rr=b + k), t + pos * beat, abs(g))
    if top:                                                   # an optional slow line: (bar, beat, midi, beats)
        for (b, bt, m, d) in top:
            x = held('vln_sus', m, d * beat + 0.4, xf=0.3); a = int(0.2 * SR); x[:a] *= np.linspace(0, 1, a)
            put(up, x, T0 + b * bar + bt * beat, 0.45)
    L_, R_ = np.zeros(N, np.float32), np.zeros(N, np.float32)
    for x, pan, g in ((up, -0.25, 1.0), (vc, 0.35, 1.0), (kb, 0.45, 0.8), (pu, 0.2, 0.5)):
        p = (pan + 1) * np.pi / 4; L_ += x * g * np.cos(p); R_ += x * g * np.sin(p)
    def hall(x, seed):
        r = np.random.default_rng(seed); n = int(3.2 * SR); tt = np.arange(n) / SR
        ir = lp((r.standard_normal(n) * np.exp(-6.91 * tt / 3.2)).astype(np.float32), 4000); ir /= np.sqrt(np.sum(ir ** 2))
        return sg.fftconvolve(x, np.concatenate([np.zeros(int(0.025 * SR), np.float32), ir]))[:len(x)].astype(np.float32)
    w = 0.35; L_ = (1 - w) * L_ + w * hall(L_, 3); R_ = (1 - w) * R_ + w * hall(R_, 4)
    st = np.stack([L_, R_], 1); st = lp(st.T.copy(), 7000).T if False else st
    st *= 0.5 / (np.sqrt(np.mean(st ** 2)) * 10 ** (20 / 20) + 1e-9) * level          # a fixed level, about -26 dBFS RMS
    pk = np.abs(st).max()
    if pk > 0.9: st *= 0.9 / pk
    f = np.ones(N, np.float32); r = int(4.0 * SR); f[-r:] = np.linspace(1, 0, r) ** 1.5; st *= f[:, None]
    tmp = OUTDIR + 'mood-%s.wav' % name
    import scipy.io.wavfile as wv; wv.write(tmp, SR, (st * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'highpass=f=35', '-c:a', 'libmp3lame', '-b:a', '160k',
                    '-metadata', 'title=Treasure Island mood strings: ' + name, OUTDIR + 'mood-%s.mp3' % name], check=True)
    os.remove(tmp); print('mood-%s.mp3' % name, round(L, 1), 's')

ARGS = sys.argv[2:]
MOODS = {
    # the sea on a fair day: D major, unhurried, a pizzicato step on 1 and 3
    'calm-sea': dict(bpm=66, chords='D Bm G A D F#m G A Bm G D A G A D Dsus'.split(), pulse=[(0, 0, 0.6), (2, 2, 0.45)]),
    # setting out, the voyage under sail: G major, a walking pizzicato on every beat
    'voyage': dict(bpm=84, chords='G C D G Em C D D G Bm C D C D G G'.split(), pulse=[(0, 0, 0.6), (1, 2, 0.35), (2, 3, 0.45), (3, 2, 0.35)], shape='gentle'),
    # something is wrong: A minor, a soft pulse of two
    'unease': dict(bpm=72, chords='Am Am F E Am Dm E E F Dm Am E F Dm E E'.split(), pulse=[(0, 0, 0.5), (2, 0, 0.35)]),
    # dread: D minor, low and slow, no pulse
    'dread': dict(bpm=56, chords='Dm Bb Gm A Dm Eb Gm A Bb Gm Dm A Gm Eb A Dm'.split(), lo=50, hi=72),
    # loss and grief: B minor, slow
    'sorrow': dict(bpm=58, chords='Bm G D F#m G Em F# F# Bm Em A D G Em F# Bm'.split()),
    # safe again, home: F major, warm
    'home': dict(bpm=68, chords='F Dm Bb C F Am Bb C Dm Bb F C Bb C F F'.split(), pulse=[(0, 0, 0.5)]),
}
for name, kw in MOODS.items():
    if ARGS and name not in ARGS: continue
    mood(name, **kw)
