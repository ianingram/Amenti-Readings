"""Amenti Studios score toolkit (rebuilt 7 Oct 2026 for Julius Caesar).

A small sample player over VSCO 2 CE (CC0): banks of pitched samples keyed by MIDI,
sustain/loop of long notes, plucks, a convolution reverb from a synthetic hall,
per-stem levelling, a crossfaded loop seam, mp3 out through ffmpeg.

Sample names in VSCO are not all in the same octave convention (the trumpet and the
tenor trombone are written an octave low), so every bank is CALIBRATED: a few of its
samples are pitch-tracked and the octave offset is set from the measurement, not
assumed from the file name."""
import os, re, glob, subprocess
import numpy as np
import scipy.signal as sg
import scipy.io.wavfile as wavfile

SR = 48000
V = '/tmp/claude-0/-home-claude/c002dc02-d023-5c73-9437-2a1012982e23/scratchpad/vsco2/'
NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
_cache = {}

def midi_of(name):
    m = re.match(r'([A-G]#?)(-?\d)', name)
    return 12 * (int(m.group(2)) + 1) + NOTE[m.group(1)]

def read(path):
    if path in _cache: return _cache[path]
    sr, x = wavfile.read(path)
    x = x.astype(np.float32)
    if x.dtype != np.float32 or np.abs(x).max() > 2: x = x / 32768.0
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = sg.resample_poly(x, SR, sr).astype(np.float32)
    _cache[path] = x
    return x

def load16(path, semis=0.0):
    x = read(path)
    if abs(semis) < 1e-3: return x.copy()
    r = 2 ** (semis / 12)                                   # pitch shift by resampling
    n = int(len(x) / r); idx = np.arange(n) * r
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)

def f0(x):
    seg = x[int(0.15 * SR): int(0.65 * SR)]
    if len(seg) < 4000 or np.abs(seg).max() < 1e-4: return None
    seg = seg - seg.mean(); ac = np.correlate(seg[:6000], seg[:6000], 'full')[5999:]
    lo, hi = int(SR / 1400), int(SR / 25)
    k = lo + int(np.argmax(ac[lo:hi]))
    return SR / k if ac[k] > 0.3 * ac[0] else None

def bank(pattern, rx, calibrate=True):
    b = {}
    for f in sorted(glob.glob(V + pattern)):
        m = re.search(rx, os.path.basename(f))
        if m: b.setdefault(midi_of(m.group(1)), f)
    if calibrate and b:
        offs = []
        for k in list(b)[:: max(1, len(b) // 5)][:5]:
            f = f0(read(b[k]))
            if f:
                meas = 69 + 12 * np.log2(f / 440)
                d = meas - k
                offs.append(12 * round(d / 12))
        if offs:
            o = int(np.median(offs))
            if o: b = {k + o: v for k, v in b.items()}
    return b

def pluck(b, m, g=1.0):
    k = min(b, key=lambda q: abs(q - m)); return load16(b[k], m - k) * g

def sustain(b, m, d, head=0.25, kx=0.2, tail=0.4):
    k = min(b, key=lambda q: abs(q - m)); s = load16(b[k], m - k)
    hd = int(head * SR); mid = s[hd: max(hd + int(0.8 * SR), len(s) - int(0.4 * SR))]
    n = int(d * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    k_ = int(kx * SR); step = max(int(0.3 * SR), len(mid) - k_); pos = max(int(0.3 * SR), len(s) - len(mid) // 2 - k_)
    w = np.ones(len(mid), np.float32); w[:k_] = np.linspace(0, 1, k_); w[-k_:] = np.linspace(1, 0, k_)
    while pos < n: out[pos:pos + len(mid)] += mid * w; pos += step
    out = out[:n]; r = min(int(tail * SR), n // 3); out[-r:] *= np.linspace(1, 0, r); return out

def put(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    a = max(0, -i); j = max(0, i); n = min(len(x) - a, len(buf) - j)
    buf[j:j + n] += x[a:a + n] * g

def lp(x, f): return sg.sosfilt(sg.butter(4, f, 'low', fs=SR, output='sos'), x).astype(np.float32)
def hp(x, f): return sg.sosfilt(sg.butter(4, f, 'high', fs=SR, output='sos'), x).astype(np.float32)
def bp(x, a, b): return sg.sosfilt(sg.butter(4, [a, b], 'band', fs=SR, output='sos'), x).astype(np.float32)

def reverb(x, secs=2.2, wet=0.3, seed=1):
    r = np.random.default_rng(seed); n = int(secs * SR)
    ir = r.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / SR * (6.9 / secs)).astype(np.float32)
    ir = lp(ir, 6000); ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    w = sg.fftconvolve(x, ir)[:len(x) + n // 2].astype(np.float32)
    out = np.zeros(len(w), np.float32); out[:len(x)] += x * (1 - wet); out += w * wet
    return out[:len(x)]

def at_rms(x, db):
    r = np.sqrt(np.mean(x ** 2)) + 1e-12; return (x * (10 ** (db / 20) / r)).astype(np.float32)

def stems(*pairs):
    n = max(len(x) for x, _ in pairs); out = np.zeros(n, np.float32)
    for x, db in pairs: out[:len(x)] += at_rms(x, db)
    return out

def fold(x, xf):
    """a loop: the last xf seconds (the reverb's ring after the music ends) laid over the start,
    so when the file repeats the ring carries across the seam instead of being cut off"""
    n = int(xf * SR)
    if len(x) <= 2 * n: return x
    out = x[:-n].copy(); out[:n] += x[-n:]
    return out

def rms_db(x, db):
    y = at_rms(x, db); pk = np.abs(y).max()
    if pk > 0.95: y = (np.tanh(y / pk * 1.4) / np.tanh(1.4) * 0.95).astype(np.float32)
    return y

def write_mp3(x, path, kbps=192):
    tmp = path + '.wav'
    wavfile.write(tmp, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-b:a', f'{kbps}k', path], check=True)
    os.remove(tmp)
