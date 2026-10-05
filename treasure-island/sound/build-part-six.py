#!/usr/bin/env python3
"""Treasure Island — Part Six: Captain Silver. The treasure hunt, the voice among the
trees, the empty pit, Merry's end, Flint's gold in Ben Gunn's cave, and home. The theme
turned hollow at the pit (the tune slow and low on the cellos); the coins; the theme's
flute and the parrot to close the book. VSCO 2 CE (CC0) and built sounds. Seed 1883."""
import os, json
exec(open('/tmp/ti/ti_assets5.py').read().split('# ── the coracle')[0].replace("/tmp/ti/sound5/", "/tmp/ti/sound6/"))
os.makedirs('/tmp/ti/sound6', exist_ok=True)
V = '/tmp/vsco/'
CELLO = {}
for f in glob.glob(V + 'Strings/Cello Section/susvib/*.wav'):
    m_ = re.search(r'susvib_([A-G]#?\d)_v1', os.path.basename(f))
    if m_: CELLO[midi_of(m_.group(1))] = f
def cello(m, d):
    k = min(CELLO, key=lambda q: abs(q - m)); s = load16(CELLO[k], m - k)
    head = int(0.3 * SR); mid = s[head: max(head + int(0.9 * SR), len(s) - int(0.5 * SR))]
    n = int(d * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    kx = int(0.4 * SR); step = max(int(0.4 * SR), len(mid) - kx); pos = max(int(0.4 * SR), len(s) - len(mid) // 2 - kx)
    w = np.ones(len(mid), np.float32); w[:kx] = np.linspace(0, 1, kx); w[-kx:] = np.linspace(1, 0, kx)
    while pos < n: out[pos:pos + len(mid)] += mid * w; pos += step
    out = out[:n]; r = min(int(0.8 * SR), n // 3); out[-r:] *= np.linspace(1, 0, r); a = min(int(0.3 * SR), n // 4); out[:a] *= np.linspace(0, 1, a)
    return out
# THE THEME TURNED HOLLOW — the tune's first phrase, an octave and more down on the cellos,
# very slow, the A at the end held over nothing: the empty pit
D, F, E, A, G, C = 50, 53, 52, 45, 55, 48
PH = [(0, D, 2), (2, D, 2), (4, F, 3), (7, E, 1), (8, E, 2), (10, D, 2), (12, A, 6)]
SL = (60 / 88 / 4) * 3.0
ho = np.zeros(int(30 * SR), np.float32); t0 = 0.5
for rep in range(2):
    for st, m, d in PH: put(ho, cello(m, d * SL * 1.05 + 0.4), t0 + st * SL, 0.45)
    t0 += 18 * SL + 2.0
ho = reverb(ho, 3.4, 0.4, seed=93)[: int(t0 * SR)]
write_mp3(rms_db(fold(ho, 2.5), -26), 'score-hollow.mp3')
# Flint's gold: coins slipping and chinking in heaps in the firelight
n = int(5 * SR); cn = np.zeros(n, np.float32); t_ = 0.1
while t_ < 4.4:
    q = int(0.25 * SR); tq = np.arange(q) / SR; f0 = 2600 + 2200 * rng.random()
    y = sum(np.sin(2 * np.pi * f0 * r_ * tq + rng.random()) * np.exp(-tq * (25 + 20 * k)) / (k + 1) for k, r_ in enumerate((1, 2.41, 3.9)))
    put(cn, y.astype(np.float32), t_, 0.2 + 0.6 * rng.random()); t_ += 0.04 + 0.12 * rng.random()
write_mp3(peak_db(reverb(cn, 1.6, 0.3), -14), 'coins.mp3')
json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:22s} {v_:6.2f}s')
