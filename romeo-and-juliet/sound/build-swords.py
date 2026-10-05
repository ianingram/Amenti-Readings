#!/usr/bin/env python3
"""Romeo and Juliet — THE SWORDS, played as instruments.

A blade is a long thin steel bar: struck, it rings at a fundamental with inharmonic
overtones (a free bar's modes, 1 : 2.76 : 5.40 : 8.93 : 13.34 …), each a pair of close
partials beating against each other, the highs dying first, the fundamental singing on.
Every blade here is TUNED TO THE PLAY'S KEY (D minor: D, F, A, and C for the darker
blows), so the fights are played in D with the music.

The strokes:
  broad clash   blade full on blade: a hard impact, both blades roaring, a long ring
  parry         tip on tip: a light high 'tink', quickly gone
  wring         steel sliding along steel: friction rising up the blade, the 'shing'
  beat          a sharp knock aside, a short bright ring
  thrust        the blade driven home: a hiss of air and a dull stop
  swish         the blade cutting the air close past the microphone: the edge whistling
                ON A NOTE OF THE KEY, bent up as it comes and down as it goes

From these, the fights are choreographed in time (4/4 at 112) and placed in their rooms:
the piazza for the brawl and the duels, the vault for Paris and Romeo. Built entirely
here; no recordings. Deterministic (seed 1597)."""
import os, json
exec(open('/tmp/rj/rj_assets.py').read().split('# ═══ THE FEAST')[0])
rng = np.random.default_rng(1597)
MODES = [1.0, 2.756, 5.404, 8.933, 13.344, 18.64]
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def blade(f0, dur=3.0, strength=1.0, bright=1.0, decay=1.0, seed=0):
    """one blade ringing: paired partials beating, highs dying first"""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, ratio in enumerate(MODES):
        f = f0 * ratio
        if f > 16000: break
        amp = (0.9 ** k) * (bright ** k) / (1 + 0.35 * k)
        d = (0.55 + 1.6 * k ** 1.15) / decay                      # the fundamental rings longest
        for det in (-1, 1):                                       # a close pair: the shimmer of a long blade
            ff = f * (1 + det * (0.0009 + 0.0006 * r.random()))
            y += amp * 0.5 * np.sin(2 * np.pi * ff * t + r.random() * 6.28) * np.exp(-t * d)
    return (y * strength).astype(np.float32)
def impact(strength=1.0, seed=0, ms=4):
    r = np.random.default_rng(seed); n = int(0.06 * SR); t = np.arange(n) / SR
    click = hp(r.standard_normal(n).astype(np.float32), 2500) * np.exp(-t * (1000 / ms))
    chunk = bp(r.standard_normal(n).astype(np.float32), 900, 4500) * np.exp(-t * 90)
    return (click * 0.9 + chunk * 0.5) * strength
def scrape(dur=0.5, f_lo=1800, f_hi=6500, strength=1.0, seed=0):
    """steel riding along steel: friction noise climbing the blade, stick-slip grain"""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    noise = r.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32); seg = int(0.02 * SR)
    for i in range(0, n - seg, seg // 2):                         # a sweeping band, piece by piece
        f = f_lo + (f_hi - f_lo) * (i / n) ** 0.8
        w_ = np.hanning(seg).astype(np.float32)
        out[i:i + seg] += bp(noise[i:i + seg], f * 0.8, min(f * 1.25, 20000)) * w_
    grain = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * (220 + 380 * t / dur) * t))   # stick-slip chatter
    env_ = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    return (out * grain * env_ * strength).astype(np.float32)

def swish(n='A', dur=0.42, strength=0.8, seed=0, octave=1):
    """a blade cutting the air close past the microphone: the edge WHISTLES on a note of the
    key — a narrow band of rushing air centred on it, bent up as the blade comes and down as
    it goes (Doppler), loudest at the pass, with the low buffet of air you only hear up close"""
    r = np.random.default_rng(seed); n_ = int(dur * SR); t = np.arange(n_) / SR; tc = dur * 0.55; w = dur * 0.16
    f0 = hz(KEY[n] + 12 * octave) if n in KEY else hz(n)
    fc = f0 * (1 + 0.07 * np.tanh((tc - t) / (w * 0.8)))                   # higher coming, lower going
    noise = r.standard_normal(n_ + 2048).astype(np.float32)
    out = np.zeros(n_, np.float32); seg = int(0.012 * SR); hann = np.hanning(seg).astype(np.float32)
    for i in range(0, n_ - seg, seg // 3):                                   # the whistle: a tight band following the note
        f = fc[i + seg // 2]
        out[i:i + seg] += (bp(noise[i:i + seg + 256], f * 0.97, f * 1.03)[:seg] * 1.0 + bp(noise[i + 900:i + 900 + seg + 256], f * 1.96, f * 2.04)[:seg] * 0.35) * hann
    rush = bp(noise[:n_], 700, 6000)                                         # the rush of air around it
    buffet = lp(noise[1024:1024 + n_], 260) * 1.6                            # the push of air at the microphone
    prox = 1 / (1 + ((t - tc) / w) ** 2)                                     # loudest as it passes
    y = (out * 2.2 + rush * 0.35 + buffet * prox ** 2) * prox
    return (y / (np.abs(y).max() + 1e-9) * strength).astype(np.float32)

KEY = {'D': 74, 'F': 77, 'A': 69, 'C': 72, 'd': 62, 'a': 57}       # D5 F5 A4 C5, and the low blades D4 A3
def broad(n1='D', n2='A', strength=1.0, ring=1.0, seed=0):
    """blade full on blade: both roar"""
    out = np.zeros(int(4.2 * SR), np.float32)
    put(out, impact(1.0 * strength, seed, ms=3), 0)
    put(out, blade(hz(KEY[n1]), 4.0, 0.9 * strength, 1.0, ring, seed + 1), 0.001)
    put(out, blade(hz(KEY[n2]) * 1.003, 4.0, 0.75 * strength, 0.95, ring, seed + 2), 0.002)
    put(out, scrape(0.12, 2500, 5000, 0.35 * strength, seed + 3), 0.005)            # the bite of edge on edge
    return out
def parry(n='F', strength=0.6, seed=0):
    out = np.zeros(int(1.4 * SR), np.float32)
    put(out, impact(0.5 * strength, seed, ms=2), 0)
    put(out, blade(hz(KEY[n] + 12), 1.3, 0.5 * strength, 1.15, 2.6, seed + 1), 0.0005)   # the tips: an octave up, quick
    return out
def beat(n='C', strength=0.8, seed=0):
    out = np.zeros(int(1.8 * SR), np.float32)
    put(out, impact(0.8 * strength, seed, ms=3), 0)
    put(out, blade(hz(KEY[n]), 1.7, 0.6 * strength, 1.05, 1.8, seed + 1), 0.001)
    return out
def wring(n='D', dur=0.7, strength=0.8, seed=0):
    """the bind and slide: contact, the blades riding along each other, the release ring"""
    out = np.zeros(int((dur + 2.6) * SR), np.float32)
    put(out, impact(0.45 * strength, seed, ms=4), 0)
    put(out, scrape(dur, 1600, 7000, strength, seed + 1), 0.01)
    put(out, blade(hz(KEY[n]), 2.6, 0.35 * strength, 1.1, 1.3, seed + 2), 0.0)         # the blades sing under the slide
    put(out, blade(hz(KEY[n] + 7), 2.4, 0.45 * strength, 1.1, 1.2, seed + 3), dur)      # and ring free on release
    return out
def thrust(seed=0):
    r = np.random.default_rng(seed); n = int(1.2 * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    put(out, (bp(r.standard_normal(int(0.25 * SR)).astype(np.float32), 900, 4000) * np.sin(np.pi * np.arange(int(0.25 * SR)) / int(0.25 * SR)) ** 2) * 0.35, 0)
    put(out, lp(load('/tmp/snd/w_Dull_thud.wav')[: int(0.4 * SR)], 900) * 0.8, 0.24)
    return out
def piazza(x, wet=0.28): return reverb(x, 2.2, wet, seed=41, bright=7000)           # stone and open sky
def vault(x): return reverb(x, 4.2, 0.45, seed=42, bright=4500)                      # the tomb

# ── the single strokes ─────────────────────────────────────────────────────────────
write_mp3(peak_db(piazza(broad('D', 'A', 1.0, 1.0, 1)), -3), 'sword-clash.mp3')
write_mp3(peak_db(piazza(parry('F', 0.7, 2)), -8), 'sword-parry.mp3')
write_mp3(peak_db(piazza(wring('D', 0.7, 0.9, 3)), -5), 'sword-wring.mp3')
write_mp3(peak_db(piazza(beat('C', 0.9, 4)), -6), 'sword-beat.mp3')
write_mp3(peak_db(piazza(np.concatenate([swish('A', 0.45, 0.9, 5), np.zeros(int(0.9 * SR), np.float32)]), 0.18), -6), 'sword-swish.mp3')

# ── the fights, choreographed in time (4/4 at 112: a beat is 0.536 s) ──────────────
BT = 60 / 112
def fight(moves, room=piazza, length=None, seed=10):
    """moves: (beat, stroke, args) — strokes on the grid, a little human looseness"""
    r = np.random.default_rng(seed)
    L = length or (max(m[0] for m in moves) * BT + 5)
    lead = max(0.0, -min(m[0] for m in moves)) * BT                       # room for wind-ups before the first blow
    out = np.zeros(int((L + lead) * SR), np.float32)
    for i, (b, kind, args) in enumerate(moves):
        t_ = b * BT + lead + r.normal(0, 0.008)
        x = thrust(seed + i) if kind == 'thrust' else {'broad': broad, 'parry': parry, 'beat': beat, 'wring': wring, 'swish': swish}[kind](**args, seed=seed + 7 * i)
        put(out, x, max(0, t_))
    return room(out)
# I.1 — the brawl in the street: Sampson and Gregory against Abram and Balthasar; quick, ragged, many blades
brawl = [(-0.5, 'swish', dict(n='A', strength=0.6)), (0, 'beat', dict(n='C', strength=0.7)), (0.5, 'parry', dict(n='F')), (1, 'beat', dict(n='A', strength=0.8)), (1.5, 'parry', dict(n='D')),
         (1.75, 'swish', dict(n='D', dur=0.3, strength=0.6)), (2, 'broad', dict(n1='D', n2='C', strength=0.8, ring=0.8)), (3, 'parry', dict(n='A')), (3.5, 'beat', dict(n='F', strength=0.7)),
         (4, 'wring', dict(n='A', dur=0.5, strength=0.7)), (5.5, 'beat', dict(n='C')), (6, 'parry', dict(n='F')), (6.5, 'parry', dict(n='D')),
         (6.75, 'swish', dict(n='F', dur=0.3, strength=0.7)), (7, 'broad', dict(n1='A', n2='D', strength=0.9)), (8.5, 'beat', dict(n='D')), (9, 'parry', dict(n='A')), (9.25, 'parry', dict(n='F')),
         (9.6, 'swish', dict(n='A', dur=0.45, strength=0.85)), (10, 'broad', dict(n1='D', n2='A', strength=1.0, ring=1.1))]
write_mp3(peak_db(fight(brawl, seed=11), -3), 'fight-brawl.mp3')
# I.1 — the second fray: Benvolio and Tybalt, then the citizens' clubs among the blades
brawl2 = [(0, 'parry', dict(n='A')), (0.5, 'beat', dict(n='D', strength=0.8)), (1, 'parry', dict(n='F')), (1.25, 'swish', dict(n='C', dur=0.3, strength=0.6)), (1.5, 'broad', dict(n1='C', n2='A', strength=0.85)),
          (3, 'wring', dict(n='D', dur=0.6, strength=0.8)), (4.5, 'beat', dict(n='A')), (5, 'parry', dict(n='C')), (5.5, 'beat', dict(n='F', strength=0.7)),
          (5.0, 'swish', dict(n='F', dur=0.5, strength=0.7)), (6, 'broad', dict(n1='D', n2='F', strength=0.9)), (7.5, 'parry', dict(n='A')), (8, 'beat', dict(n='D')), (8.5, 'broad', dict(n1='A', n2='D', strength=1.0, ring=1.1))]
write_mp3(peak_db(fight(brawl2, seed=12), -3), 'fight-brawl-2.mp3')
# III.1 — Mercutio and Tybalt: a duel of masters, quick parries, a long bind, and the thrust under Romeo's arm
merc = [(-1, 'swish', dict(n='D', dur=0.5, strength=0.7)), (-0.5, 'swish', dict(n='A', dur=0.4, strength=0.6)), (0, 'parry', dict(n='F')), (0.5, 'parry', dict(n='A')), (1, 'beat', dict(n='D')), (2, 'parry', dict(n='F')), (2.25, 'parry', dict(n='D')),
        (2.5, 'parry', dict(n='A')), (2.75, 'swish', dict(n='F', dur=0.3, strength=0.65)), (3, 'broad', dict(n1='D', n2='F', strength=0.85)), (4.5, 'wring', dict(n='D', dur=0.9, strength=0.9)),
        (6.5, 'parry', dict(n='C')), (7, 'beat', dict(n='A')), (7.5, 'parry', dict(n='F')), (5.75, 'swish', dict(n='C', dur=0.45, strength=0.7)), (7.75, 'swish', dict(n='A', dur=0.3, strength=0.7)), (8, 'broad', dict(n1='A', n2='C', strength=0.9)),
        (9.5, 'parry', dict(n='D', strength=0.4)), (9.75, 'swish', dict(n='D', dur=0.3, strength=0.5, octave=0)), (10, 'thrust', {})]
write_mp3(peak_db(fight(merc, seed=21), -3), 'fight-mercutio.mp3')
# III.1 — Romeo and Tybalt: fury, broad blow after broad blow, then the end
romeo = [(-0.4, 'swish', dict(n='D', dur=0.4, strength=0.9)), (0, 'broad', dict(n1='D', n2='A', strength=1.0)), (0.7, 'swish', dict(n='C', dur=0.3, strength=0.8)), (1, 'broad', dict(n1='C', n2='A', strength=0.95)), (2, 'beat', dict(n='F')),
         (2.25, 'swish', dict(n='F', dur=0.3, strength=0.85)), (2.5, 'broad', dict(n1='D', n2='F', strength=1.0)), (3.5, 'wring', dict(n='A', dur=0.6, strength=1.0)), (4.6, 'swish', dict(n='A', dur=0.4, strength=0.9)), (5, 'broad', dict(n1='A', n2='D', strength=1.0)),
         (5.5, 'beat', dict(n='C')), (5.7, 'swish', dict(n='D', dur=0.35, strength=1.0)), (6, 'broad', dict(n1='D', n2='C', strength=1.0, ring=1.2)), (7.2, 'swish', dict(n='a', dur=0.35, strength=0.7, octave=1)), (7.5, 'thrust', {})]
write_mp3(peak_db(fight(romeo, seed=31), -3), 'fight-romeo-tybalt.mp3')
# V.3 — Paris and Romeo by torchlight in the churchyard, the vault ringing with it
paris = [(-0.5, 'swish', dict(n='a', dur=0.45, strength=0.7)), (0, 'beat', dict(n='a')), (0.5, 'parry', dict(n='D')), (1, 'broad', dict(n1='d', n2='a', strength=0.9, ring=1.3)),
         (2.5, 'wring', dict(n='d', dur=0.8, strength=0.85)), (4.1, 'swish', dict(n='d', dur=0.45, strength=0.85)), (4.5, 'broad', dict(n1='a', n2='C', strength=1.0, ring=1.3)), (5.7, 'swish', dict(n='a', dur=0.3, strength=0.6)), (6, 'thrust', {})]
write_mp3(peak_db(fight(paris, room=vault, seed=41), -3), 'fight-paris.mp3')

json.dump(files, open(OUT + 'manifest.json', 'w'), indent=1)
for k_, v_ in files.items(): print(f'{k_:24s} {v_:6.2f}s')
