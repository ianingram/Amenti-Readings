#!/usr/bin/env python3
"""A Christmas Carol — the score and the sounds. Instruments: Versilian Studios,
VSCO 2 Community Edition (CC0; credit requested). Tunes: 'God Rest Ye Merry,
Gentlemen' (traditional, public domain). Deterministic (seed 1843)."""
import os, json
src = open('/tmp/snd/ch16_assets.py').read().split('# ═══════════════════ DREAD')[0]
src = src.replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/carol/sound/'")
exec(src)
rng = np.random.default_rng(1843)
os.system('cd /tmp/vsco && git checkout HEAD -- "Percussion/Glock" 2>/dev/null')
GLK = {midi_of(re.search(r'_([A-G]#?\d)\.wav', f).group(1)): f for f in glob.glob(V + 'Percussion/Glock/*.wav')}
def glock(m, g=1.0):
    k = min(GLK, key=lambda x: abs(x - m)); x = load(GLK[k], m - k); return x[:int(4 * SR)] * g

# ── God Rest Ye Merry, Gentlemen — E minor, as it is still sung ───────────────
# (traditional; melody line 1 = line 2; then 'to save us all…'; then the refrain)
Q = 0.62                                                      # a crotchet, unhurried
E4, Fs4, G4, A4, B4, C5, D5, D4, E5 = 64, 66, 67, 69, 71, 72, 74, 62, 76
L1 = [(E4, 1), (E4, 1), (B4, 1), (B4, 1), (A4, 1), (G4, 1), (Fs4, 1), (E4, 1), (D4, 1), (E4, 1), (Fs4, 1), (G4, 1), (A4, 1), (B4, 3)]
L3 = [(B4, 1), (C5, 1), (A4, 1), (B4, 1), (C5, 1), (D5, 1), (E5, 1), (B4, 1), (A4, 1), (G4, 1), (E4, 1), (Fs4, 1), (G4, 1), (A4, 3)]
REF = [(G4, 1), (A4, 2), (B4, 1), (C5, 1), (B4, 1), (B4, 1), (A4, 1), (G4, 1), (Fs4, 1), (E4, 2), (G4, 1), (Fs4, 1), (E4, 1), (Fs4, 2), (G4, 1), (A4, 2), (B4, 1), (C5, 1), (B4, 1), (A4, 1), (G4, 1), (Fs4, 1), (E4, 4)]
TUNE = L1 + L1 + L3 + REF
HARM = {E4: (40, [55, 59]), Fs4: (47, [54, 59]), G4: (43, [55, 59]), A4: (45, [57, 60]), B4: (47, [54, 59]), C5: (48, [55, 60]),
        D5: (43, [55, 59]), D4: (50, [54, 57]), E5: (40, [55, 59])}
def tune_render(inst='flute', bright=False, start=1.0):
    total = sum(d for _, d in TUNE) * Q + start + 4; N = int(total * SR)
    mel = np.zeros(N, np.float32); har = np.zeros(N, np.float32); pno = np.zeros(N, np.float32)
    t = start; bar = 0
    for i, (m, d) in enumerate(TUNE):
        dur = d * Q
        if inst == 'flute': put(mel, held('flute', m + (12 if bright else 0), dur + 0.15, xf=0.4), t, 0.28)
        else: put(mel, held('violin', m, dur + 0.2, xf=0.4), t, 0.22)
        if i % 2 == 0:                                         # harmony every other note, held under
            b, inner = HARM.get(m, (40, [55, 59]))
            put(har, held('cello', b, 2 * Q + 0.4), t, 0.34)
            put(har, held('viola', inner[0], 2 * Q + 0.4), t, 0.2)
            put(pno, piano(b + 12, 1, 3.0), t, 0.35); put(pno, piano(inner[1], 1, 3.0), t + Q / 2, 0.25)
        t += dur
    x = reverb(mel, 2.2, 0.28, seed=21) + reverb(har, 2.4, 0.24, seed=22) + reverb(pno, 2.4, 0.26, seed=23) * 0.8
    if bright:
        for k in range(0, int(t / (4 * Q))):                   # the bells of the morning, lightly
            put(x, glock(76 + [0, 7, 12, 7][k % 4], 0.18), start + k * 4 * Q)
    return x[:int((t + 3) * SR)]
carol = tune_render('flute'); write_mp3(rms_db(env(carol, [(0, 0), (1.0, 1), (len(carol) / SR - 3, 1), (len(carol) / SR, 0)]), -22), 'score-carol.mp3')
morning = tune_render('violin', bright=True); write_mp3(rms_db(env(morning, [(0, 0), (1.0, 1), (len(morning) / SR - 3, 1), (len(morning) / SR, 0)]), -21), 'score-carol-morning.mp3')
# the boy at the keyhole: the first line alone, on the flute, thin and cold
N = int(14 * SR); k = np.zeros(N, np.float32); t = 0.2
for m, d in L1: put(k, held('flute', m, d * 0.52 + 0.1, xf=0.35), t, 0.3); t += d * 0.52
write_mp3(peak_db(reverb(k, 1.6, 0.3), -14), 'keyhole-carol.mp3')

# ── The Ghost of Christmas Past — a music box, and strings far off ─────────────
L = 54.0; N = int((L + 6) * SR); mb = np.zeros(N, np.float32); st = np.zeros(N, np.float32)
G5, B5, D6, A5, C6, E6, Fs5 = 79, 83, 86, 81, 84, 88, 78
seq = [G5, B5, D6, B5, A5, C6, E6, C6, Fs5, A5, D6, A5, G5, B5, D6, G5 + 12]
t = 0.5; i = 0
while t < L:
    put(mb, glock(seq[i % len(seq)], 0.5 + 0.2 * rng.random()), t); t += 0.75; i += 1
for t0, (b, top) in zip(range(0, int(L) + 6, 12), [(43, 67), (45, 69), (50, 66), (43, 67), (43, 71)]):
    put(st, held('cello', b, 13.0), t0, 0.22); put(st, held('violin', top + 12, 13.0), t0, 0.08)
past = reverb(mb, 3.0, 0.42, seed=24) + reverb(st, 2.8, 0.3, seed=25)
write_mp3(rms_db(fold(past, 6.0), -25), 'score-past.mp3')

# ── Mr Fezziwig's fiddler — a country dance in D, 6/8, quick and bright ────────
E8 = 0.19
D5_, E5_, Fs5_, G5_, A5_, B5_, Cs6, D6_ = 74, 76, 78, 79, 81, 83, 85, 86
jig = [(A5_, 2), (Fs5_, 1), (D5_, 2), (Fs5_, 1), (A5_, 2), (D6_, 1), (B5_, 2), (A5_, 1), (G5_, 2), (B5_, 1), (A5_, 2), (Fs5_, 1), (E5_, 2), (Fs5_, 1), (D5_, 3),
       (Fs5_, 2), (A5_, 1), (D6_, 2), (A5_, 1), (B5_, 2), (G5_, 1), (E5_, 2), (G5_, 1), (Fs5_, 2), (D5_, 1), (E5_, 2), (Cs6, 1), (D6_, 3), (D6_, 3)]
L = sum(d for _, d in jig) * E8 * 2; N = int((L + 6) * SR); fd = np.zeros(N, np.float32); ac = np.zeros(N, np.float32)
t = 0.2
for rep in range(2):
    for m, d in jig: put(fd, held('violin', m - 12, d * E8 + 0.05, xf=0.12), t, 0.3); t += d * E8
for b in range(int(L / (6 * E8)) + 1):
    root = [50, 50, 55, 57][b % 4]
    put(ac, piano(root - 12, 2, 1.0), 0.2 + b * 6 * E8, 0.4); put(ac, piano(root + 4 if root != 55 else root + 4, 1, 0.6), 0.2 + b * 6 * E8 + 3 * E8, 0.3)
fz = reverb(fd, 1.4, 0.22, seed=26) + reverb(ac, 1.4, 0.2, seed=27)
write_mp3(rms_db(fz[:int((L + 1.5) * SR)], -20), 'fezziwig-dance.mp3')

# ── every bell in the house: small bells swinging, then ringing, then stopping together
N = int(9 * SR); hb = np.zeros(N, np.float32); r = np.random.default_rng(1844)
def smallbell(f0, n=int(2.2 * SR)):
    tt = np.arange(n) / SR; y = np.zeros(n)
    for ratio, a, dec in [(1, 1, 3), (2.76, .5, 5), (5.4, .3, 8), (8.9, .2, 12)]: y += a * np.sin(2 * np.pi * f0 * ratio * tt) * np.exp(-tt * dec)
    return (y * np.minimum(1, tt / 0.002)).astype(np.float32)
t = 0.2
while t < 7.6:
    dens = min(1.0, t / 2.5); g = 0.15 + 0.6 * dens
    put(hb, smallbell(900 + 900 * r.random()), t, g * (0.6 + 0.4 * r.random())); t += 0.5 - 0.42 * dens + 0.05 * r.random()
hb[int(7.7 * SR):] = 0
write_mp3(peak_db(reverb(hb, 1.6, 0.3), -12), 'house-bells.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v in files.items(): print(f'{k_:24s} {v:7.2f}s')
