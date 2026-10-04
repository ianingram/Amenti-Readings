#!/usr/bin/env python3
"""Treasure Island — Part Five: My Sea Adventure. THE THEME COMES HOME. The coda's water
becomes the coracle; the crew's verse is heard far off round the pirates' camp-fire;
the theme's lone flute drifts with Jim round the island; the drums gather for Israel
Hands. Built from the theme's own material (VSCO 2 CE, the voice-service takes) and the
recordings in SOURCES.md. Deterministic (seed 1883)."""
import os, json
src = open('/tmp/snd/ch16_assets.py').read().split('# ═══════════════════ DREAD')[0]
src = src.replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/ti/sound5/'")
exec(src)
os.makedirs('/tmp/ti/sound5', exist_ok=True)
rng = np.random.default_rng(1883)
import subprocess as _sp
def mp3(path):
    raw = _sp.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def load16(path, semis=0.0):                                 # bit-depth-correct loader (VSCO is 24-bit)
    sr, x = wv.read(path); scale = {np.dtype('int16'): 32768.0, np.dtype('int32'): 2147483648.0}.get(x.dtype, 1.0)
    x = x.astype(np.float32) / scale
    if x.ndim > 1: x = x.mean(1)
    r = SR / sr * 2 ** (-semis / 12)
    return sg.resample_poly(x, int(round(r * 1000)), 1000).astype(np.float32) if abs(r - 1) > 1e-6 else x
def stage(x, dist=0.2, seed=0):
    x = hp(x, 70); loud = np.abs(x) > 0.02 * np.abs(x).max(); x = x / (np.sqrt(np.mean(x[loud] ** 2)) + 1e-9) * 0.12
    return reverb(np.concatenate([x, np.zeros(int(2.4 * SR), np.float32)]), 2.1 + 2 * dist, 0.25 + 0.35 * dist, seed=60 + seed, bright=int(5200 - 3000 * dist))
creak = load('/tmp/snd/w_Creaky_wooden_casket.wav')

# ── the coracle: the theme's coda water — lapping close against a little hull, the boat
#    creaking as it rocks, the surf far off — as a room for the reading
L = 64.0; N = int(L * SR); co = np.zeros(N, np.float32); t_ = 0.3
while t_ < L - 1:
    n = int((0.25 + 0.2 * rng.random()) * SR); tt = np.arange(n) / SR
    slap = lp(rng.standard_normal(n), 900 + 500 * rng.random()) * np.exp(-tt * (14 + 8 * rng.random())) + 0.25 * hp(rng.standard_normal(n), 2500) * np.exp(-tt * 30)
    put(co, slap.astype(np.float32) * (0.15 + 0.12 * rng.random()), t_); t_ += 0.7 + 0.9 * rng.random()
co += rms_db(lp(rng.standard_normal(N), 140, 2).astype(np.float32), -40)
for t_ in np.arange(3.0, L - 2, 8.0):
    x = sg.resample(creak[: int(0.9 * SR)], int(0.9 * SR * 1.6)).astype(np.float32); put(co, lp(x, 1600) * 0.12, t_ + rng.random())
cove = mp3('/tmp/ti/sound/cove.mp3'); co += rms_db(lp(np.tile(cove, 2)[:N], 700), -36)
write_mp3(rms_db(fold(co, 4.0), -27), 'coracle.mp3')

# ── the camp-fire chorus: the crew's verse from the theme, the same three deep voices,
#    at their own pace — heard far off across the water, through the trees
SP = json.load(open('/tmp/ti/vox5/spans.json'))
ch = np.zeros(int(26 * SR), np.float32); t_ = 0.5
for line in ('l1', 'l2', 'l3', 'l2'):
    longest = 0
    for k, v in enumerate(('Charon', 'Orus', 'Sadaltager')):
        a_, b_ = SP['%s_%s' % (v, line)]; x = load16('/tmp/ti/vox5/%s_%s.wav' % (v, line))[int(max(0, a_ - 0.05) * SR): int((b_ + 0.1) * SR)]
        put(ch, x / (np.abs(x).max() + 1e-9), t_ + 0.03 * k + rng.normal(0, 0.02), 0.5); longest = max(longest, len(x) / SR)
    t_ += longest + 0.5
fire = lp(rng.standard_normal(len(ch)), 2500) * (rng.random(len(ch)) < 0.004) * 2.0                 # the fire's crackle, far
chorus = reverb(lp(ch + fire.astype(np.float32) * 0.05, 1700), 4.0, 0.55, seed=81, bright=1300)
chorus = env(chorus[: int(26 * SR)], [(0, 0), (1.5, 1), (22.5, 1), (26, 0)])
write_mp3(peak_db(chorus, -14), 'campfire-chorus.mp3')
# 'a dull, old, droning sailor's song, with a droop and a quaver at the end of every verse'
dr = np.zeros(int(12 * SR), np.float32)
for k, v in enumerate(('Charon', 'Sadaltager')):
    a_, b_ = SP['%s_l2' % v]; x = load16('/tmp/ti/vox5/%s_l2.wav' % v, -3.0)
    x = x[int(max(0, a_ - 0.05) / 2 ** (-3 / 12) * SR): int((b_ + 0.1) / 2 ** (-3 / 12) * SR)]
    put(dr, x / (np.abs(x).max() + 1e-9), 0.5 + 0.05 * k, 0.5)
write_mp3(peak_db(env(reverb(lp(dr, 1400), 4.0, 0.6, seed=82, bright=1100), [(0, 0), (1, 1), (9, 1), (12, 0)]), -18), 'campfire-drone.mp3')

# ── the drifting flute: the theme's tune, slow and far, phrase after phrase — a score loop
V = '/tmp/vsco/'
FL = {}
for f in glob.glob(V + 'Woodwinds/Flute/expvib/*.wav'):
    m_ = re.search(r'expvib_([A-G]#?\d)_v1', os.path.basename(f))
    if m_: FL[midi_of(m_.group(1))] = f
def flute(m, d):
    k = min(FL, key=lambda q: abs(q - m)); s = load16(FL[k], m - k)
    head = int(0.25 * SR); mid = s[head: max(head + int(0.8 * SR), len(s) - int(0.4 * SR))]
    n = int(d * SR); out = np.zeros(n + len(s), np.float32); out[:len(s)] += s
    kx = int(0.2 * SR); step = max(int(0.3 * SR), len(mid) - kx); pos = max(int(0.3 * SR), len(s) - len(mid) // 2 - kx)
    w = np.ones(len(mid), np.float32); w[:kx] = np.linspace(0, 1, kx); w[-kx:] = np.linspace(1, 0, kx)
    while pos < n: out[pos:pos + len(mid)] += mid * w; pos += step
    out = out[:n]; r = min(int(0.4 * SR), n // 3); out[-r:] *= np.linspace(1, 0, r); return out
D5, C5, E5, F5, G5, A5, A4 = 74, 72, 76, 77, 79, 81, 69
PA = [(0, D5, 2), (2, D5, 2), (4, F5, 3), (7, E5, 1), (8, E5, 2), (10, D5, 2), (12, A4, 4), (16, D5, 2), (18, D5, 2), (20, F5, 3), (23, G5, 1), (24, F5, 2), (26, E5, 1), (27, C5, 1), (28, D5, 4)]
PB = [(0, A5, 2), (2, A5, 2), (4, G5, 3), (7, F5, 1), (8, E5, 2), (10, F5, 2), (12, E5, 4), (16, D5, 2), (18, F5, 2), (20, E5, 3), (23, C5, 1), (24, D5, 2), (26, C5, 1), (27, A4, 1), (28, D5, 4)]
SL = (60 / 88 / 4) * 2.1
fl = np.zeros(int(60 * SR), np.float32); t0 = 1.0
for ph, g in ((PA, 1.0), (PB, 0.85), (PA, 0.75)):
    for st, m, d in ph: put(fl, flute(m, d * SL * 1.05 + 0.2), t0 + st * SL, 0.3 * g)
    t0 += 32 * SL + 2.5
fl = reverb(lp(fl, 5000), 3.8, 0.5, seed=77, bright=3600)[: int(t0 * SR)]
write_mp3(rms_db(fold(fl, 3.0), -27), 'score-flute-drift.mp3')

# ── Israel Hands: the drums gather as he climbs with the dirk in his teeth — kettle rolls
#    and the snares rising — and stop dead at the pistols
TR = lambda d, v: V + f'Percussion/Timpani/Rolls/Timpani{d}_Roll_v{v}_rr1_Sum.wav'
SN = lambda nm: V + 'VSCO 1 Percussion/drums/snare/drum3_marching/%s.wav' % nm
L = 22.0; st = np.zeros(int(L * SR), np.float32)
def roll(t0, dur, d, v=5, g=1.0):
    x = load16(TR(d, v))
    while len(x) < int(dur * SR): x = np.concatenate([x, x[int(0.3 * SR):]])
    x = x[: int(dur * SR)]; tt = np.arange(len(x)) / SR; put(st, x * np.clip(0.15 + 0.85 * tt / dur, 0, 1), t0, g)
roll(0.0, L, 2, 5, 0.9); roll(4.0, L - 4, 4, 5, 0.8)
t_ = 8.0
while t_ < L - 0.05:                                             # the snares: a roll that never stops rising
    f = (t_ - 8) / (L - 8); nm = ['snare3_pp_1', 'snare3_p_1', 'snare3_p_3', 'snare3_mp_1', 'snare3_f_1', 'snare3_fff_1'][min(5, int(f * 6))]
    put(st, load16(SN(nm)), t_, 0.3 + 0.6 * f); t_ += 0.085 - 0.03 * f
st[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))       # it stops dead
write_mp3(peak_db(reverb(st, 1.4, 0.18), -6), 'hands-drums.mp3')
# the dirk: a hiss through the air, and the thock into the mast
n = int(1.2 * SR); dk = np.zeros(n, np.float32); tt = np.arange(int(0.35 * SR)) / SR
put(dk, (bp(rng.standard_normal(len(tt)), 1200, 6000) * np.sin(np.pi * tt / tt[-1]) ** 3).astype(np.float32), 0.0, 0.4)
put(dk, lp(load('/tmp/snd/w_Dull_thud.wav')[: int(0.4 * SR)], 3500), 0.33, 1.0)
write_mp3(peak_db(reverb(dk, 0.9, 0.2), -8), 'dirk-mast.mp3')
# Israel Hands goes over: the body into the water
n = int(3.0 * SR); tt = np.arange(n) / SR
sp_ = lp(rng.standard_normal(n), 1600) * np.exp(-tt * 3) * 1.4 + 0.4 * hp(rng.standard_normal(n), 2500) * np.exp(-tt * 5)
write_mp3(peak_db(reverb(sp_.astype(np.float32), 1.4, 0.25), -6), 'body-water.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:24s} {v_:6.2f}s')
