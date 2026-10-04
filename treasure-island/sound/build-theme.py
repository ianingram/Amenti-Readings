#!/usr/bin/env python3
"""EXPERIMENT — 'Fifteen men on the dead man's chest', as a 4/4 hip-hop cut in D minor.

Stevenson wrote the words and no tune, so the melody here is ORIGINAL, set to the
natural stresses of his line:   FIF-teen MEN on the DEAD man's CHEST —
                                YO-ho-HO and a BOT-tle of RUM!
88 bpm, swung and LOOSE, i – VI – VII – V (Dm Bb C A).
v2 — CRUDE, NOT POLISHED. The beat is the ship: the KICK is a mallet on an empty
whiskey barrel (a muffled drum, a dull thud and the hollow ring of the cask); the
SNARE is an oar slapped flat on the deck; the HATS are knuckles and a belaying pin
ticking on wood, with a bottle knocked over on the last beat of every fourth bar,
and boots stamping the deck under it all. Every hit is late or early by a few
milliseconds and never the same twice. The tavern piano is out of tune, the strings
are gone, the whole thing is driven into the tape until it frays.
v3-v6 — the crew's 'yo, ho' (1-2, and deeper 3-4); an arranged form with intro, verses,
a slow half-time chant, choruses, a breakdown and an outro; an opening horn call; the
deck (sea, wind, gulls, canvas, a rope under strain) and orders shouted and answered.
v7 — RECAST AND CLEAN. An opening sequence: 'All hands on deck!' — the ship's bell —
'All hands on deck!' — bell, bell, bell, a clear bronze tone; then the horn call, then
the song. The chant recast with deep natural male voices (Charon, Sadaltager and
Rasalgethi for the deep answer; Orus, Zubenelgenubi and Algenib for the call), level-
matched and set on a sound stage built for reverb — clean, no grit, no synthesis.
v8 — THE DRUMS OF WAR at 1:27: a terrific volley of kettle drums and toms, and in the
midst of it the snares fire like a military drum corps — three snares (one a marching
drum) playing rolls, flams and accents as a section — over kettle-drum downbeats and
tom runs, until they begin to fade at 2:00 and are gone at the end.
v9 — THE GULLS AS PLAYERS, not wallpaper: one far off before the first order; one
answering the horn call as it dies; a pair wheeling overhead as the beat drops; single
cries dropped into the rests the chant leaves; a whole flock bursting up in panic at the
first crash of the volley, scattering and gone; silence from the birds while the drums
play; and one lone gull, far away, as the last sound when the drums have faded.
v10 — THE BATTLE RISES from 1:13: men shouting more and more (Man the guns! Here they
come! Fire! Get down! Reload! They're boarding us! Hold, lads!), round shot whistling
overhead and close, far guns and then near ones, pistols fired at close range, and the
band pressed down under it all as the voices take over — climbing into the volley at
1:27, then the voices thin and fade away under the drums.
v11 — ADRIFT. When it is all over: one person alone in a small boat, drifting round an
island. Water lapping close against a little hull, the boat creaking as it rocks, an oar
dipped once and the drips running off it, the surf on the island far off, a breath of
wind, a gull very far away — and the tune, slow, on a flute alone, across the water.
v12 — DAWN FIRST. Ten seconds of a calm sea and gulls, peaceful and serene; then the
ship's bell rings the watch; the calm holds; and only at 0:25 does the first 'All hands
on deck!' break it — everything after moved 24.4 seconds later.
v13 — THE SONG. 'All hands on deck!' four times: the whole sequence twice, the first
beginning in the calm. And at 1:30 the crew sings Stevenson's own verse — 'Fifteen men on
the dead man's chest — Yo-ho-ho, and a bottle of rum! / Drink and the devil had done for
the rest — Yo-ho-ho, and a bottle of rum!' — in half time, a line every two bars, three
deep voices together with the flute doubling the tune beneath them. Four bars longer;
3:30 in all.
v14 — the verse said a little quicker (each line fills about four-fifths of its two
bars instead of all of them), and the 'Yo-ho-ho, and a bottle of rum!' lines turned
down beneath the lines that carry the story.
v15 — ONE WAKE-UP CALL, AND IT IS GENTLE. The extra sequence in the calm is gone; the
opening is the original single sequence again. Its first 'All hands on deck!' is the
low, ghostly voice — set further off, softer, in more of the hall — because everything
is still calm when it comes; the second call, nearer and full, is the one that wakes the ship.
v16 — CLOSE QUARTERS from 2:40, before the boat: the fighting comes right up to you —
steel on steel, musket locks snapped to full cock and ramrods rattled down barrels,
bullets zipping past the ear, pistols and muskets fired close, and men calling each
other to it ('Cover the entrance!', 'Stay back!', 'To me, lads!', 'Load and fire!',
'Watch your left!', 'Keep your heads down!') — then it fades into the water.
v17 — THE LONG DRIFT, to 4:00. The coda grows to over a minute: the flute keeps playing
the tune in the distance, phrase after phrase, each a little further away; cannon fire
very far off now and then, a war going on somewhere else; the waves, the gulls; peace.
v18 — A LEVEL AND TIMING PASS, from a probe of v17: the first 'All hands on deck!' softer
again; the horn call brought down 6 dB (it was the loudest thing in the opening, louder
than the beat it introduces, so the drop at 0:46 felt like a step down); the watch bell
eased; and the five-second hole before the coda filled — the flute enters sooner and the
whole coda sits 3 dB higher, so the drift reads as quiet, not as a dropout.
v19 — the crew's 'yo, ho' falls silent a full bar before the verse, so its echo is gone
by the time 'Fifteen men on the dead man's chest' begins; the verse is heard alone.
"""
src = open('/tmp/snd/ch16_assets.py').read().split('# ═══════════════════ DREAD')[0].replace("OUT = '/tmp/snd/ch16/'", "OUT = '/tmp/ti/score/'")
import os; os.makedirs('/tmp/ti/score', exist_ok=True)
exec(src)
# VSCO samples are 24-bit (read as int32): scale by the file's own bit depth, so the
# instruments and the synthesized drums meet at the same level
def load(path, semis=0.0):
    k = (path, round(semis, 4))
    if k in _c: return _c[k]
    sr, x = wv.read(path)
    scale = {np.dtype('int16'): 32768.0, np.dtype('int32'): 2147483648.0, np.dtype('uint8'): 128.0}.get(x.dtype, 1.0)
    x = x.astype(np.float32) / scale
    if x.ndim > 1: x = x.mean(1)
    ratio = SR / sr * (2 ** (-semis / 12))
    if abs(ratio - 1) > 1e-6: x = sg.resample_poly(x, int(round(ratio * 1000)), 1000).astype(np.float32)
    _c[k] = x; return x
rng = np.random.default_rng(1883)
BPM = 88.0; B = 60 / BPM; BAR = 4 * B; S16 = B / 4
SWING = 0.58                                              # the off-sixteenths land late
def t16(bar, step):                                       # time of a sixteenth, swung
    pair, odd = divmod(step, 2)
    return bar * BAR + pair * 2 * S16 + (2 * S16 * SWING if odd else 0)
BARS = 54; N = int((BARS * BAR + 4) * SR)
drums = np.zeros(N, np.float32); bass = np.zeros(N, np.float32); keys = np.zeros(N, np.float32)
hook = np.zeros(N, np.float32); pad = np.zeros(N, np.float32)

THUD = load('/tmp/snd/w_Dull_thud.wav')[:int(0.5 * SR)]
RAP = load('/tmp/ti/src/Knocking_on_wood_or_door.wav')[int(4.5 * SR): int(4.75 * SR)]
GLASS = load('/tmp/snd/w_Wine_glass.wav')[int(4.8 * SR): int(5.6 * SR)]
MUTED = load(V + 'VSCO 1 Percussion/drums/bass/bdrum_muted_pp_1.wav')
def cask(f0):
    """the hollow ring of an empty barrel: a few low wooden modes, quickly damped"""
    n = int(0.35 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for ratio, a, d in ((1.0, 1.0, 16), (1.58, .5, 22), (2.32, .3, 30), (3.1, .18, 40)):
        y += a * np.sin(2 * np.pi * f0 * ratio * t + rng.random()) * np.exp(-t * d)
    return (y * np.minimum(1, t / 0.002)).astype(np.float32)
def kick():                                                   # a mallet on an empty whiskey barrel
    y = np.zeros(int(0.5 * SR), np.float32)
    put(y, lp(MUTED, 900), 0, 1.0); put(y, lp(THUD, 700), 0, 1.2); put(y, cask(92 + 10 * rng.random()), 0.002, 0.7)
    return y
def snare():                                                  # an oar slapped flat on the deck
    y = np.zeros(int(0.45 * SR), np.float32); n = int(0.18 * SR); t = np.arange(n) / SR
    slap = bp(rng.standard_normal(n), 700, 3800) * np.exp(-t * 38)
    put(y, slap.astype(np.float32), 0, 0.9); put(y, hp(RAP, 300), 0.004, 1.3)
    put(y, cask(210 + 30 * rng.random()) * 0.5, 0.003, 0.6)       # the plank answering
    return y
def hat(open_=False):                                         # knuckles and a belaying pin on wood
    x = hp(sg.resample(RAP, int(len(RAP) / (2.2 + 0.4 * rng.random()))).astype(np.float32), 1500)
    return x[: int((0.12 if open_ else 0.05) * SR)]
def stomp():                                                  # boots on the deck
    return lp(THUD, 400) * 1.2
SNARE = None
def sub(midi, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = 440 * 2 ** ((midi - 69) / 12)
    y = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)   # harmonics so a laptop speaker hears the 808
    y *= np.minimum(1, t / 0.006) * np.exp(-t * 1.2)
    y[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return y.astype(np.float32)

DETUNE = {m: rng.normal(0, 0.18) for m in range(20, 100)}         # a tavern upright nobody has tuned this voyage
PROG = [(38, [62, 65, 69]), (34, [58, 62, 65]), (36, [60, 64, 67]), (33, [57, 61, 64])]   # Dm Bb C A
# sections: 0-1 intro (keys + crackle) · 2-9 verse (beat, bass, keys) · 10-17 hook · 18-21 verse · 22-25 hook out
# THE FORM — 47 bars, about two minutes
#   0-3   intro        piano and crackle alone
#   4-11  verse 1      the beat comes in; no crew
#   12-15 slow chant   half time: 'yo…' on 1, '…ho' on 3, high bar then deep bar
#   16-23 chorus       the full chant 1-2 / deep 3-4, and the tune on flute
#   24-31 verse 2      beat and piano; the crew only on the last bar of each four
#   32-35 breakdown    barrel and boots only, the deep slow chant
#   36-43 chorus       full chant and tune
#   44-46 outro        piano, and one last slow deep 'yo… ho'
FORM = ['intro'] * 7 + ['verse'] * 8 + ['slow'] * 4 + ['chorus'] * 4 + ['lyric'] * 8 + ['verse2'] * 8 + ['break'] * 4 + ['chorus'] * 8 + ['outro'] * 3
def section(bar): return FORM[bar]
for bar in range(BARS):
    sec = section(bar); root, triad = PROG[bar % 4]
    if bar < 5: continue                                   # the orders, the bell and the horn first; the piano waits
    # piano stabs: the boom-bap pattern — on 1, the 'a' of 2, and the '&' of 3
    for step, g in ((0, 1.0), (7, 0.7), (10, 0.85)):
        for k, m in enumerate(triad):
            put(keys, piano(m + DETUNE[m], 2, 1.6), t16(bar, step) + 0.004 * k + abs(rng.normal(0, 0.008)), 0.26 * g)
    put(keys, piano(root + 12 + DETUNE[root + 12], 2, 2.0), t16(bar, 0), 0.32)
    if sec in ('intro', 'outro'): continue
    brk = (sec == 'break')
    # drums — loose: every hit a little early or late, never the same strength twice
    J = lambda: rng.normal(0, 0.012)
    for step in (0, 6, 10) if bar % 2 == 0 else (0, 3, 8, 10):
        put(drums, kick(), t16(bar, step) + J(), 0.85 + 0.25 * rng.random())
    for step in (() if brk else (4, 12)):
        put(drums, snare(), t16(bar, step) + 0.014 + J(), 0.8 + 0.3 * rng.random())   # the oar drags a hair behind
    for step in (range(0) if brk else range(16)):
        if step % 2 == 0 or rng.random() < 0.45:
            put(drums, hat(open_=(step == 14 and bar % 4 == 3)), t16(bar, step) + J(), (0.35 if step % 4 else 0.55) * (0.6 + 0.6 * rng.random()))
    for step in (0, 8):
        put(drums, stomp(), t16(bar, step) + J() * 2, 0.35)
    if bar % 4 == 3 and not brk:
        put(drums, GLASS, t16(bar, 12) + 0.05 + J(), 0.5)                              # a bottle knocked over
    # 808 sub on the roots, a slide into the next bar
    put(bass, np.tanh(3 * sub(root - 12, BAR * (0.9 if brk else 0.62))) * 0.5, t16(bar, 0), 0.75)
    put(bass, sub(root - 12, BAR * 0.2), t16(bar, 10), 0.6)
    put(bass, sub(PROG[(bar + 1) % 4][0] - 12 + (0 if bar % 4 != 3 else 0), BAR * 0.12), t16(bar, 14), 0.5)


# THE CREW — "Yo, ho" on 1-2, and deeper "Yo, ho" on 3-4
import scipy.io.wavfile as _w
CUT = {'Alnilam': [(0.26, 0.72), (1.54, 1.82)], 'Orus': [(0.42, 0.76), (1.24, 1.48)], 'Charon': [(0.34, 0.78), (1.24, 1.52)],
       'Algenib': [(0.26, 1.0), (1.7, 2.18)], 'Gacrux': [(0.28, 0.8), (1.22, 1.72)]}
def syll(voice, k, semis):
    a, b = CUT[voice][k]
    x = load('/tmp/ti/vox/%s.wav' % voice, semis)
    r = 2 ** (semis / 12)                       # load() pitch-shifts by resampling, so the times stretch with it
    x = x[int(max(0, a - 0.03) / r * SR): int((b + 0.1) / r * SR)].copy()
    x[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    return x / (np.abs(x).max() + 1e-9)
HIGH = [('Alnilam', 1), ('Orus', 2), ('Charon', 0)]                 # the first 'yo, ho'
LOW = [('Algenib', -4), ('Gacrux', -5), ('Charon', -7), ('Orus', -6)]  # the answer, deeper
def stretch(x, k):
    """draw a syllable out, pitch kept: overlap-add of short grains read slower than they are written"""
    g = int(0.06 * SR); hop_out = g // 4; hop_in = max(1, int(hop_out / k)); w = np.hanning(g).astype(np.float32)
    n_out = int(len(x) * k) + g; y = np.zeros(n_out, np.float32); norm = np.zeros(n_out, np.float32)
    i = o = 0
    while i + g < len(x) and o + g < n_out:
        y[o:o + g] += x[i:i + g] * w; norm[o:o + g] += w; i += hop_in; o += hop_out
    y = y / np.maximum(norm, 1e-3); return y[:o]
vox = np.zeros(N, np.float32)
# ── THE CREW, IN TUNE ──────────────────────────────────────────────────────────
TAKES = {'Algenib': ((0.27, 0.79), (1.52, 2.25)), 'Gacrux': ((0.31, 0.7), (1.51, 2.07)),
         'Iapetus': ((0.3, 1.26), (1.94, 3.04)), 'Orus': ((0.31, 0.93), (1.23, 2.27))}
def _yin(frame, fmin=70, fmax=420, thr=0.15):
    n = len(frame); tau_max = int(SR / fmin); tau_min = int(SR / fmax)
    d = np.array([np.sum((frame[:n - tau_max] - frame[t:n - tau_max + t]) ** 2) for t in range(tau_max)])
    cm = np.ones_like(d); cs = np.cumsum(d[1:]); cm[1:] = d[1:] * np.arange(1, tau_max) / np.maximum(cs, 1e-12)
    for t in range(tau_min, tau_max - 1):
        if cm[t] < thr:
            while t + 1 < tau_max and cm[t + 1] < cm[t]: t += 1
            return SR / t
    return np.nan
def f0_track(x, hop):
    """YIN pitch, frame by frame — the first dip, so it never mistakes a voice for its own octave below"""
    fr = int(0.05 * SR); out = []
    xs = sg.resample_poly(x, 1, 4).astype(np.float32); sr4 = SR // 4                 # 12 kHz is plenty for a voice
    fr4 = fr // 4; hop4 = max(1, hop // 4)
    global_SR = SR
    for i in range(0, max(1, len(xs) - fr4), hop4):
        f_ = xs[i:i + fr4]
        if np.sqrt(np.mean(f_ ** 2)) < 0.01: out.append(np.nan); continue
        d = _yin4(f_, sr4)
        out.append(d)
    return np.array(out)
def _yin4(frame, sr, fmin=70, fmax=420, thr=0.15):
    n = len(frame); tau_max = min(int(sr / fmin), n // 2); tau_min = int(sr / fmax)
    d = np.array([np.sum((frame[:n - tau_max] - frame[t:n - tau_max + t]) ** 2) for t in range(tau_max)])
    cm = np.ones_like(d); cs = np.cumsum(d[1:]); cm[1:] = d[1:] * np.arange(1, tau_max) / np.maximum(cs, 1e-12)
    for t in range(tau_min, tau_max - 1):
        if cm[t] < thr:
            while t + 1 < tau_max and cm[t + 1] < cm[t]: t += 1
            return sr / t
    return np.nan
def tune(x, target, keep=1.0):
    """move the whole syllable so its centre pitch lands on the target, keeping all of its own
    rise and fall (a constant ratio): in tune with the chord, still a man shouting. Timing kept."""
    tr = f0_track(x, int(0.01 * SR)); med = np.nanmedian(tr) if np.any(~np.isnan(tr)) else target
    r = float(np.clip(target / med, 0.5, 2.0))
    g = int(0.04 * SR); hop = g // 4; w_ = np.hanning(g).astype(np.float32)
    y = np.zeros(len(x) + 2 * g, np.float32); nrm = np.zeros_like(y)
    for i in range(0, len(x) - g, hop):
        L_ = int(g * r); st = max(0, i + g // 2 - L_ // 2); grain = x[st: st + L_]
        if len(grain) < 8: continue
        grain = sg.resample(grain, g).astype(np.float32) * w_
        y[i:i + g] += grain; nrm[i:i + g] += w_
    return (y / np.maximum(nrm, 1e-3))[:len(x)]
def hz(m): return 440 * 2 ** ((m - 69) / 12)
CHORD_TONES = {0: (50, 53, 57, 62), 1: (46, 50, 53, 58), 2: (48, 52, 55, 60), 3: (45, 49, 52, 57)}   # Dm Bb C A
_takes = {}
def take(voice, k):
    if (voice, k) not in _takes:
        a_, b_ = TAKES[voice][k]; x = load('/tmp/ti/vox2/haul_%s.wav' % voice)
        x = x[int(max(0, a_ - 0.03) * SR): int((b_ + 0.12) * SR)].copy(); x[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
        tr = f0_track(x, int(0.01 * SR)); _takes[(voice, k)] = (x / (np.abs(x).max() + 1e-9), float(np.nanmedian(tr)))
    return _takes[(voice, k)]
# THE HARMONY. Hoarse shouts carry almost no steady pitch — a pitch tracker finds a
# voiced frame in one of ten — so they cannot be tuned like a singer. Instead the crew
# SINGS UNDER ITS OWN SHOUTING: a choir of men on 'yo' and 'ho', each voice on a chord
# tone (root, third and fifth of Dm, Bb, C and A, two men to a note, a little apart in
# pitch and time), shaped by the same syllables. The shouts give the grit and the
# rhythm; the singing under them gives the chord.
FORM_O = (450, 800, 2480); FORM_I = (300, 2100, 2900)            # the vowel of 'ho', and the 'y' of 'yo'
def voice_pulse(f0, dur, seed):
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * (5.0 + r.random()) * t + r.random() * 6) + 0.003 * r.standard_normal(n).cumsum() / np.sqrt(n)
    ph = np.cumsum(2 * np.pi * f0 * vib / SR)
    x = sg.sawtooth(ph, 0.85) + 0.15 * r.standard_normal(n)        # a glottal buzz with breath in it
    return x.astype(np.float32)
def formant(x, F, bw=(90, 110, 160)):
    y = np.zeros_like(x)
    for f, b_ in zip(F, bw):
        y += sg.lfilter(*sg.iirpeak(f, f / b_, fs=SR), x).astype(np.float32) * (1.0 if f < 1000 else 0.5)
    return y
def sing(f0, dur, syl, seed):
    """one man singing 'yo' or 'ho' on f0"""
    x = voice_pulse(f0, dur, seed); n = len(x)
    o = formant(x, FORM_O)
    if syl == 0:                                                   # 'yo': glide out of the y
        i_ = formant(x, FORM_I); k = np.clip(np.arange(n) / (0.09 * SR), 0, 1).astype(np.float32)
        y = i_ * (1 - k) + o * k
    else:                                                          # 'ho': a breath first
        br = bp(np.random.default_rng(seed + 1).standard_normal(n).astype(np.float32), 600, 3000) * np.exp(-np.arange(n) / SR * 25)
        y = o + br * 2.0
    t = np.arange(n) / SR
    e = np.minimum(1, t / 0.04) * np.exp(-t * (0.6 / dur)) * np.minimum(1, (dur - t) / 0.12).clip(0, 1)
    return (y * e).astype(np.float32)
CHOIR_HIGH = {0: (57, 62, 65), 1: (58, 62, 65), 2: (60, 64, 67), 3: (57, 61, 64)}     # the call: a close triad around A3-G4
CHOIR_DEEP = {0: (38, 45, 50), 1: (34, 41, 46), 2: (36, 43, 48), 3: (33, 40, 45)}     # the answer: root, fifth, octave, down low
_choir = {}
def choir(bar, syl, deep, dur):
    key = (bar % 4, syl, deep, round(dur, 2))
    if key not in _choir:
        notes = (CHOIR_DEEP if deep else CHOIR_HIGH)[bar % 4]
        n = int((dur + 0.3) * SR); y = np.zeros(n, np.float32)
        for j, m in enumerate(notes):
            for man in range(2):
                f = hz(m) * (1 + (man - 0.5) * 0.006)
                put(y, sing(f, dur, syl, seed=bar % 4 * 100 + j * 10 + man + syl * 1000 + deep * 5000), 0.012 * man + 0.006 * j, 0.5)
        _choir[key] = lp(y, 3800 if not deep else 2400)
    return _choir[key]
def stage(x, dist=0.2, seed=0):
    """a sound stage built for reverb: the voice level-matched and left clean — no grit,
    no band-limiting — then a smooth hall: a short pre-delay, early reflections, a long tail"""
    x = hp(x, 70); loud = np.abs(x) > 0.02 * np.abs(x).max()
    x = x / (np.sqrt(np.mean(x[loud] ** 2)) + 1e-9) * 0.12
    er = np.zeros(int(0.12 * SR), np.float32)
    for d, g in ((0.011, .5), (0.019, .38), (0.031, .3), (0.047, .22), (0.068, .16), (0.091, .1)):
        er[int(d * SR)] += g
    early = sg.fftconvolve(x, er)[:len(x)].astype(np.float32)
    tail = reverb(np.concatenate([np.zeros(int(0.022 * SR), np.float32), x, np.zeros(int(2.4 * SR), np.float32)]), 2.1, 1.0, seed=60 + seed, bright=5200)
    dry = np.concatenate([x, np.zeros(len(tail) - len(x), np.float32)])
    ear = np.concatenate([early, np.zeros(len(tail) - len(early), np.float32)])
    return (dry * (1.0 - 0.5 * dist) + ear * (0.35 + 0.3 * dist) + tail * (0.22 + 0.35 * dist)).astype(np.float32)
def open_air(x, dist=0.3, seed=0): return stage(x, min(0.9, dist + 0.2), seed)
CREW = ['Algenib', 'Gacrux', 'Iapetus', 'Orus']
import json as _j2
CUTS3 = _j2.load(open('/tmp/ti/vox3/cuts.json'))
CALL_V = ['Orus', 'Zubenelgenubi', 'Algenib']                  # the call
DEEP_V = ['Charon', 'Sadaltager', 'Rasalgethi']                # the answer — the three deepest
_clean = {}
def clean(voice, k, semis=0.0):
    key = (voice, k, semis)
    if key not in _clean:
        a_, b_ = CUTS3['yoho_' + voice][k]; x = load('/tmp/ti/vox3/yoho_%s.wav' % voice, semis)
        r = 2 ** (semis / 12); x = x[int(max(0, a_ - 0.04) / r * SR): int((b_ + 0.15) / r * SR)].copy()
        x[-int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))
        _clean[key] = x
    return _clean[key]
def crew(bar, steps, who, g, slow=1.0):
    voices = DEEP_V if who == 'deep' else CALL_V
    semis = -2.0 if who == 'deep' else 0.0
    for n_, voice in enumerate(voices):
        j = rng.normal(0, 0.015 * slow)
        for k, step in enumerate(steps):
            x = clean(voice, k, semis)
            if slow > 1: x = stretch(x, slow)
            put(vox, stage(x, 0.15 + 0.1 * n_, seed=n_ * 3 + k), t16(bar, step) - 0.05 + j, g * 0.6)
import json as _j5
SP5 = _j5.load(open('/tmp/ti/vox5/spans.json'))
def sing_line(line, bar, g=0.75):
    """one line of the verse: three deep voices, each stretched to fill two bars, on the downbeat"""
    for n_, voice in enumerate(('Charon', 'Orus', 'Sadaltager')):
        name = '%s_%s' % (voice, line); a_, b_ = SP5[name]
        x = load('/tmp/ti/vox5/%s.wav' % name, -1.0)[int(max(0, a_ - 0.05) / 2 ** (-1 / 12) * SR): int((b_ + 0.1) / 2 ** (-1 / 12) * SR)]
        k = (2 * BAR * 0.78) / (len(x) / SR)                    # a little quicker than filling both bars
        x = stretch(x, k) if abs(k - 1) > 0.04 else x
        put(vox, stage(x, 0.12 + 0.08 * n_, seed=40 + n_), t16(bar, 0) - 0.05 + rng.normal(0, 0.012), g)
for bar, line in ((23, 'l1'), (25, 'l2'), (27, 'l3'), (29, 'l2')):
    sing_line(line, bar, 0.75 if line != 'l2' else 0.38)      # the yo-ho-ho lines sit under the story lines
for bar in range(BARS):
    sec = section(bar)
    if sec == 'chorus' and bar + 1 < BARS and section(bar + 1) == 'lyric':
        pass                                                                          # a bar of breath: the verse must start in the clear
    elif sec == 'chorus':
        crew(bar, (0, 4), 'high', 0.8); crew(bar, (8, 12), 'deep', 1.0)              # yo-ho / deep yo-ho, a beat each
    elif sec == 'slow':
        crew(bar, (0, 8), 'high' if bar % 2 == 0 else 'deep', 0.95, slow=1.9)          # yo…  …ho, two beats each
    elif sec == 'verse2' and bar % 4 == 3:
        crew(bar, (8, 12), 'deep', 0.9)                                              # only the deep answer, once in four
    elif sec == 'break':
        crew(bar, (0, 8), 'deep', 1.0, slow=2.2)                                     # the deep slow haul
    elif sec == 'outro' and bar == BARS - 3:
        crew(bar, (0, 8), 'deep', 1.0, slow=2.4)                                     # one last
# THE HORN CALL — bars 0-3: 'yooo' over bars 0-1, 'hooo' over bars 2-3
def ship_horn(midi, dur):
    """a low ship's horn: two slightly beating reeds, filtered, slow to speak and slow to die"""
    n = int(dur * SR); t = np.arange(n) / SR; f = 440 * 2 ** ((midi - 69) / 12)
    y = np.zeros(n)
    for d in (0.0, 0.6):
        ph = 2 * np.pi * (f + d) * t
        y += sg.sawtooth(ph) * 0.5
    y = lp(y.astype(np.float32), 520, 3)
    e = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 1.6).clip(0, 1)
    return (y * e).astype(np.float32)
horn = np.zeros(N, np.float32)
CALL = [('Charon', 0), ('Sadaltager', 0), ('Rasalgethi', 0)]
for k, (bar, note) in enumerate(((3, 38), (5, 33))):          # after the bells: D, then down to A
    for voice, semis in CALL:
        x = stretch(clean(voice, k, -3.0), 4.0)                    # drawn out long, still a man's voice
        put(horn, stage(x, 0.6, seed=k), bar * BAR + 0.15 + rng.normal(0, 0.03), 0.8)
    put(horn, ship_horn(note, 2 * BAR + 0.8), bar * BAR, 0.9)
horn = reverb(bp(horn, 50, 7000), 3.2, 0.35, seed=12, bright=3000)


# THE HOOK — an original tune on Stevenson's stresses
#   FIF-teen MEN on the DEAD man's CHEST ——   YO-ho-HO and a BOT-tle of RUM ——
D5, C5, E5, F5, G5, A5, A4, Bb4 = 74, 72, 76, 77, 79, 81, 69, 70
PHRASE_A = [(0, D5, 2), (2, D5, 2), (4, F5, 3), (7, E5, 1), (8, E5, 2), (10, D5, 2), (12, A4, 4),          # Fif-teen MEN on-the DEAD man's CHEST
            (16, D5, 2), (18, D5, 2), (20, F5, 3), (23, G5, 1), (24, F5, 2), (26, E5, 1), (27, C5, 1), (28, D5, 4)]  # Yo-ho-HO and-a BOT-tle-of RUM
PHRASE_B = [(0, A5, 2), (2, A5, 2), (4, G5, 3), (7, F5, 1), (8, E5, 2), (10, F5, 2), (12, E5, 4),
            (16, D5, 2), (18, F5, 2), (20, E5, 3), (23, C5, 1), (24, D5, 2), (26, C5, 1), (27, A4, 1), (28, D5, 4)]
def play(phrase, start_bar):
    for step, m, d in phrase:
        bar = start_bar + step // 16; s = step % 16
        put(hook, held('flute', m, d * S16 * 1.05 + 0.08, xf=0.12), t16(bar, s), 0.34)
for sb, ph in ((19, PHRASE_A), (21, PHRASE_A), (43, PHRASE_A), (45, PHRASE_A), (47, PHRASE_B), (49, PHRASE_A)):
    play(ph, sb)
# THE VERSE, in half time: the flute doubles the crew, a line every two bars
def play_half(phrase, start_bar):
    for step, m, d in phrase:
        st2 = step * 2; bar = start_bar + st2 // 16; s_ = st2 % 16
        put(hook, held('flute', m, d * 2 * S16 * 1.05 + 0.1, xf=0.15), t16(bar, s_), 0.3)
play_half(PHRASE_A, 23); play_half(PHRASE_B, 27)

# ── THE DECK — sea, wind, gulls, canvas, rope, and the orders ─────────────────
import subprocess as _sp
def mp3(path):
    raw = _sp.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
deck = np.zeros(N, np.float32)
seas = mp3('/tmp/snd/ch7/hull.mp3'); seas = np.tile(seas, int(np.ceil(N / len(seas))))[:N]
wind_ = load('/tmp/snd/src3/Howling_wind.wav'); wind_ = np.tile(wind_, int(np.ceil(N / len(wind_))))[:N]
deck += rms_db(seas, -30) + rms_db(lp(wind_, 1500), -38)
# THE GULLS — every cry placed, each at its own distance
B_ = lambda bar, beat=0: bar * BAR + beat * B
G1 = load('/tmp/snd/src3/Gull_1.wav'); HG = load('/tmp/ti/src/herring.wav'); WG = load('/tmp/ti/src/Western_Gull_Golden_Gate_National_Recreation_Area.wav')
CRIES = [G1[int(a_ * SR): int(b_ * SR)] for a_, b_ in ((6.6, 7.25), (7.95, 8.95), (10.75, 11.6), (12.45, 13.35))] + \
        [HG[int(a_ * SR): int(b_ * SR)] for a_, b_ in ((6.45, 6.85), (7.25, 7.75), (8.1, 8.6))]
LAUGH = G1[int(0.1 * SR): int(3.15 * SR)]                        # the laughing run: a gull holding forth
def at_dist(x, dist, semis=0.0):
    if semis: x = sg.resample(x, int(len(x) / 2 ** (semis / 12))).astype(np.float32)
    x = x / (np.abs(x).max() + 1e-9)
    x = lp(x, 9000 - 6500 * dist)
    x = env(x, [(0, 0), (0.01, 1), (len(x) / SR - 0.06, 1), (len(x) / SR, 0)])
    y = reverb(np.concatenate([x, np.zeros(int(3.0 * SR), np.float32)]), 1.2 + 2.2 * dist, 0.12 + 0.5 * dist, seed=int(dist * 100) + 3, bright=int(6000 - 3500 * dist))
    return y * (1.0 - 0.8 * dist)
def gull(t_, dist, which=None, semis=0.0, g=0.22):
    x = CRIES[rng.integers(len(CRIES))] if which is None else which
    put(deck, at_dist(x, dist, semis) * g, t_)
gull(0.25, 0.85)                                                 # far off, before anyone speaks
gull(B_(5, 3) + 0.4, 0.55, WG)                                   # answering the horn as it dies
gull(B_(6, 2), 0.35, CRIES[1]); gull(B_(6, 3) + 0.2, 0.3, CRIES[3], 1.0)   # a pair wheeling overhead as the beat drops
for bar_ in (8, 10, 12):                                         # verse 1: in the rests between orders
    gull(B_(bar_, 3) + 0.3, 0.65)
gull(B_(18, 3) + 0.25, 0.5, LAUGH, g=0.18)                       # holding forth as the slow chant ends
for bar_ in (31, 33):                                            # verse 2: into the space the crew leaves
    gull(B_(bar_, 1) + 0.2, 0.6)
# THE FLOCK BURSTS UP at the first crash of the volley: wings, then panic, scattering away
V0 = 36 * BAR
for k in range(10):
    m = int(0.12 * SR); burst = lp(rng.standard_normal(m), 700) * np.exp(-np.arange(m) / SR * 22)
    put(deck, burst.astype(np.float32) * 0.18, V0 + 0.05 + k * 0.07)
for k in range(9):
    d_ = 0.2 + 0.08 * k
    gull(V0 + 0.15 + k * 0.33 + 0.12 * rng.random(), min(0.9, d_), semis=1.0 + rng.random(), g=0.28)
# …and while the drums play, the birds are gone. One comes back, alone and far, at the very end.
gull(BARS * BAR - 3.2, 0.9, CRIES[2], g=0.25)

def sail_flap(d=2.0):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k in range(int(d * 5)):
        i = int((k / 5 + 0.05 * rng.random()) * SR); m = int(0.18 * SR)
        burst = lp(rng.standard_normal(m), 900 + 600 * rng.random()) * np.exp(-np.arange(m) / SR * 18)
        y[i:i + m] += burst[: max(0, n - i)] * (0.4 + 0.6 * rng.random())
    return y * np.sin(np.pi * t / d) ** 0.5
creak_ = load('/tmp/snd/w_Creaky_wooden_casket.wav')
def rope_creak():
    x = sg.resample(creak_[: int(1.2 * SR)], int(1.2 * SR * 2.2)).astype(np.float32)   # slower and lower: a hawser taking the strain
    return lp(x, 1400)
def line(name, t_, dist, g=1.0):
    x = load('/tmp/ti/vox2/%s.wav' % name)
    put(deck, open_air(x, dist, seed=sum(map(ord, name)) % 97), t_, g * (1.2 - dist))
def ayes(t_):
    for k, v in enumerate(['Alnilam', 'Fenrir', 'Iapetus', 'Umbriel', 'Enceladus']):
        line('crew_aye_' + v, t_ + 0.12 * k + 0.08 * rng.random(), 0.65 + 0.06 * k, 0.55)
B_ = lambda bar, beat=0: bar * BAR + beat * B
# THE OPENING SEQUENCE — All hands on deck! · bell · All hands on deck! · bell, bell, bell
def ship_bell(f0=880.0):
    """a small bronze ship's bell, struck: a clear prime and nominal that ring on, a quiet minor
    third and fifth for the bronze, and the clap of the clapper"""
    n = int(4.5 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for ratio, a_, d in ((0.5, .35, 0.9), (1.0, 1.0, 1.1), (1.19, .18, 2.2), (1.5, .22, 1.8), (2.0, .55, 1.6), (2.66, .18, 3.0), (3.0, .12, 3.6)):
        y += a_ * np.sin(2 * np.pi * f0 * ratio * t + rng.random()) * np.exp(-t * d)
    y += 0.25 * hp(rng.standard_normal(n), 3000) * np.exp(-t * 300)
    return (y * np.minimum(1, t / 0.0015)).astype(np.float32)
put(deck, reverb(stage(load('/tmp/ti/vox5/allhands_3.wav', -1.0), 0.8, 1), 3.2, 0.35, seed=21, bright=2600), 0.6, 0.3)   # low and ghostly, from far off: the calm is not yet broken
put(deck, reverb(ship_bell(), 2.6, 0.3, seed=90), 2.55, 0.42)
put(deck, stage(load('/tmp/ti/vox3/allhands_2.wav'), 0.3, 2), 3.4, 1.0)
for k in range(3): put(deck, reverb(ship_bell(880.0 * (1 + 0.002 * k)), 2.6, 0.3, seed=91 + k), 5.6 + k * 0.75, 0.42)
# the orders through the song (three bars later than before, to make room)
line('capt_hoist', B_(9, 0), 0.35); ayes(B_(10, 0)); put(deck, sail_flap(3.0) * 0.5, B_(10, 2))
line('bos_heave', B_(11, 2), 0.5); put(deck, rope_creak() * 0.5, B_(11, 2)); put(deck, rope_creak() * 0.4, B_(12, 1))
line('capt_batten', B_(13, 0), 0.4); ayes(B_(14, 0))
line('bos_lively', B_(32, 0), 0.5); put(deck, sail_flap(2.5) * 0.45, B_(33, 0))
line('capt_hoist', B_(35, 0), 0.4); ayes(B_(36, 0)); put(deck, rope_creak() * 0.45, B_(36, 2))
line('capt_batten', B_(39, 0), 0.35); ayes(B_(40, 0)); line('bos_heave', B_(41, 0), 0.45); put(deck, rope_creak() * 0.5, B_(41, 0))
put(deck, sail_flap(4.0) * 0.4, B_(51, 0))


# ── THE BATTLE — from bar 27 (1:13), climbing into the volley, then fading under the drums
battle = np.zeros(N, np.float32)
T0, T1, T2 = 31 * BAR, 36 * BAR, 36 * BAR + 12.0               # rise · climax · gone
def whistle_shot(near=True):
    """round shot going over: a rushing tone sliding down as it passes, then gone"""
    d = 1.6 if near else 2.2; n = int(d * SR); t = np.arange(n) / SR
    f = 1500 * np.exp(-t * (0.9 if near else 0.5)) + 380
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6
    rush = bp(rng.standard_normal(n), 400, 3000) * 0.8
    e = (t / d) ** (2.5 if near else 1.5) * np.exp(-np.clip(t - 0.88 * d, 0, None) * 30)
    y = (tone + rush) * e
    return lp(y.astype(np.float32), 6000 if near else 2500)
def splash():
    n = int(2.0 * SR); t = np.arange(n) / SR
    y = lp(rng.standard_normal(n), 1800) * np.exp(-t * 3.5) + 0.4 * hp(rng.standard_normal(n), 2500) * np.exp(-t * 6)
    return y.astype(np.float32)
TI = lambda f: mp3('/tmp/ti/sound/' + f)
PISTOL, CANNON_N, CANNON_F, VOLLEY_F, CRASH = TI('pistol-near.mp3'), TI('cannon-near.mp3'), TI('cannon-far.mp3'), TI('musket-volley-far.mp3'), TI('door-crash.mp3')
def shout(name, t_, dist, g=1.0):
    put(battle, stage(load('/tmp/ti/vox4/%s.wav' % name), dist, seed=sum(map(ord, name)) % 50), t_, g)
grow = lambda t_: float(np.clip((t_ - T0) / (T1 - T0), 0, 1))  # 0 at 1:13, 1 at 1:27
# the guns and the shot, thickening
for t_, kind in ((T0 + 0.5, 'cf'), (T0 + 3.2, 'w'), (T0 + 4.1, 'splash'), (T0 + 5.6, 'cf'), (T0 + 6.4, 'vf'), (T0 + 7.7, 'wn'),
                 (T0 + 8.5, 'crash'), (T0 + 9.0, 'p'), (T0 + 9.9, 'cn'), (T0 + 10.6, 'w'), (T0 + 11.0, 'p'), (T0 + 11.5, 'splash'),
                 (T0 + 11.9, 'wn'), (T0 + 12.4, 'p'), (T0 + 12.7, 'crash'), (T0 + 13.0, 'cn'), (T0 + 13.3, 'p')):
    g = 0.5 + 0.5 * grow(t_)
    if kind == 'cf': put(battle, CANNON_F, t_, 0.55 * g)
    elif kind == 'cn': put(battle, CANNON_N, t_, 0.75 * g)
    elif kind == 'vf': put(battle, VOLLEY_F, t_, 0.6 * g)
    elif kind == 'w': put(battle, reverb(whistle_shot(False), 1.8, 0.3, seed=5), t_, 0.35 * g)
    elif kind == 'wn': put(battle, reverb(whistle_shot(True), 1.2, 0.2, seed=6), t_, 0.6 * g)
    elif kind == 'splash': put(battle, reverb(splash(), 1.6, 0.25, seed=7), t_, 0.35 * g)
    elif kind == 'crash': put(battle, CRASH, t_, 0.5 * g)
    elif kind == 'p': put(battle, PISTOL, t_ + rng.normal(0, 0.05), 0.7 * g)
# the men — a few at first, far; then more, nearer, overlapping, until they are all you hear
CALLS = ['man_guns', 'here_they_come', 'fire', 'get_down', 'reload', 'boarding', 'hold', 'rail', 'fire2']
t_ = T0 + 1.0; k = 0
while t_ < T1 + 0.5:
    g = grow(t_); name = CALLS[k % len(CALLS)]
    shout(name, t_, 0.75 - 0.5 * g, 0.55 + 0.6 * g); k += 1
    if g > 0.5 and rng.random() < 0.6:                        # men shouting over each other
        shout(CALLS[(k + 3) % len(CALLS)], t_ + 0.35 + 0.3 * rng.random(), 0.6 - 0.3 * g, 0.5 + 0.4 * g)
    if g > 0.3: ayes(t_ + 0.8) if rng.random() < 0.25 else None
    t_ += 1.6 - 1.05 * g + 0.3 * rng.random()
# after the volley lands the shouting thins and fades away under the drums
for j, t2 in enumerate(np.arange(T1 + 1.0, T2, 1.4)):
    f = 1 - (t2 - T1) / (T2 - T1)
    shout(CALLS[(j + 2) % len(CALLS)], t2 + rng.random() * 0.3, 0.5 + 0.4 * (1 - f), 0.7 * f)
tb = np.arange(N) / SR
battle *= np.interp(tb, [0, T0, T1, T2, T2 + 3], [0, 1, 1, 0.6, 0]).astype(np.float32) + (tb < T0)
# the band gives way: pressed down as the voices take over, and back when they fade
DUCK = np.interp(tb, [0, T0, T1, T1 + 1.0, T2], [1, 1, 0.5, 0.5, 1]).astype(np.float32)

# ── CLOSE QUARTERS — 2:40 to the coda (mix time; the song starts 27.3 s into the track)
melee = np.zeros(N + int(10 * SR), np.float32)
M0 = 160.0 - 27.3; M1 = BARS * BAR + 2.5 - 2.5                 # 2:40 · where the coda takes over
CLASH = TI('cutlass-clash.mp3'); MUSK = TI('musket-near.mp3')
def zip_by():
    """a ball going past the ear: a thin whine bent down as it passes, over in a quarter second"""
    n = int(0.28 * SR); t = np.arange(n) / SR
    f = 3200 - 2200 * (t / t[-1]) ** 0.7
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + 0.5 * bp(rng.standard_normal(n), 1500, 6000)
    e = np.exp(-((t - 0.11) / 0.05) ** 2)
    return (y * e).astype(np.float32)
def cock():
    """a musket lock drawn back: half-cock, then the hard snap to full"""
    y = np.zeros(int(0.5 * SR), np.float32)
    for t_, f, g in ((0.0, 3300, 0.5), (0.22, 2600, 1.0)):
        n = int(0.06 * SR); tt = np.arange(n) / SR
        click = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 140) + 0.5 * hp(rng.standard_normal(n), 3000) * np.exp(-tt * 200)) * g
        put(y, click.astype(np.float32), t_)
    return y
def ramrod():
    """a steel ramrod rattled down a barrel and drawn"""
    n = int(0.8 * SR); t = np.arange(n) / SR
    r_ = bp(rng.standard_normal(n), 2500, 7000) * (0.4 + 0.6 * (np.sin(2 * np.pi * 9 * t) > 0)) * np.sin(np.pi * t / t[-1])
    return (r_ * 0.5).astype(np.float32)
def call(name, t_, dist, g=1.0):
    put(melee, stage(load('/tmp/ti/vox6/%s.wav' % name), dist, seed=sum(map(ord, name)) % 40), t_, g)
t_ = M0; k = 0; CALLS2 = ['cover', 'stay_back', 'to_me', 'load_fire', 'your_left', 'heads_down']
while t_ < M1 - 1.0:
    f = (t_ - M0) / (M1 - M0)
    r = rng.random()
    if r < 0.28: put(melee, CLASH, t_, 0.5 + 0.3 * rng.random())                                      # steel on steel
    elif r < 0.42: put(melee, zip_by(), t_, 0.45); put(melee, zip_by(), t_ + 0.18 + 0.1 * rng.random(), 0.35)   # balls past the ear
    elif r < 0.52: put(melee, cock(), t_, 0.5)                                                           # a lock snapped to full cock
    elif r < 0.60: put(melee, ramrod(), t_, 0.4)
    elif r < 0.72: put(melee, PISTOL, t_, 0.55)
    elif r < 0.80: put(melee, MUSK, t_, 0.5)
    else: call(CALLS2[k % len(CALLS2)], t_, 0.15 + 0.2 * rng.random(), 0.9); k += 1                   # men calling each other to it
    t_ += 0.35 + 0.55 * rng.random()
for j, nm in enumerate(CALLS2):                                   # make sure every call is heard once, early
    call(nm, M0 + 0.4 + j * 1.6, 0.2, 0.85)
tm = np.arange(len(melee)) / SR
melee *= np.interp(tm, [0, M0, M0 + 1.5, M1 - 3.0, M1 + 0.5], [0, 0, 1, 1, 0]).astype(np.float32)
melee = melee[:N]

# ── THE DRUM CORPS — from bar 32 (1:27) to the end ─────────────────────────────
corps = np.zeros(N, np.float32)
PD = V + 'VSCO 1 Percussion/drums/'
SN = {'march': {'pp': ['snare3_pp_1', 'snare3_pp_2'], 'p': ['snare3_p_1', 'snare3_p_2', 'snare3_p_3', 'snare3_p_4'], 'mf': ['snare3_mp_1'],
                'f': ['snare3_f_1', 'snare3_f_2'], 'ff': ['snare3_fff_1'], 'rim': ['snare3_rimshot_ff_1']},
      'one': {'pp': ['snare1_pp_1'], 'p': ['snare1_p_1'], 'mf': ['snare1_mp_1', 'snare1_mp_2'], 'f': ['snare1_f_1', 'snare1_f_2', 'snare1_f_3'],
              'ff': ['snare1_ff_1', 'snare1_ff_2'], 'rim': ['snare1_rimshot_fff_1']},
      'two': {'pp': ['snare2_mp_1'], 'p': ['snare2_mp_1'], 'mf': ['snare2_mf_1', 'snare2_mf_2'], 'f': ['snare2_f_1', 'snare2_f_2', 'snare2_f_3'],
              'ff': ['snare2_ff_1', 'snare2_fff_1'], 'rim': ['snare2_ff_1']}}
DIR = {'march': 'drum3_marching', 'one': 'drum1', 'two': 'drum2'}
def sn(drum, dyn):
    names = SN[drum][dyn]; return load(PD + 'snare/%s/%s.wav' % (DIR[drum], names[rng.integers(len(names))]))
def stroke(t_, dyn, g=1.0):
    for k, drum in enumerate(('march', 'one', 'two')):            # the section: three snares, never quite together
        put(corps, sn(drum, dyn), t_ + 0.004 * k + rng.normal(0, 0.003), g * (1.0 if drum == 'march' else 0.7) * (0.85 + 0.3 * rng.random()))
def flam(t_, g=1.0): stroke(t_ - 0.028, 'p', 0.5 * g); stroke(t_, 'ff', g)
def roll(t0, t1, d0='p', d1='f'):
    n = max(2, int((t1 - t0) / (S16 / 2)))
    for i in range(n):
        f = i / (n - 1); stroke(t0 + i * (t1 - t0) / n, 'p' if f < 0.4 else ('mf' if f < 0.8 else 'f'), 0.45 + 0.5 * f)
TIMP_HIT = lambda d, v, r=1: V + f'Percussion/Timpani/Timpani{d}_Hit_v{v}_rr{r}_Sum.wav'
TIMP_ROLL = lambda d, v: V + f'Percussion/Timpani/Rolls/Timpani{d}_Roll_v{v}_rr1_Sum.wav'
def timp(t_, d, v, g=1.0): put(corps, load(TIMP_HIT(d, v, 1 + rng.integers(2))), t_, g)
def troll(t0, dur, d, v=5, g=1.0):
    x = load(TIMP_ROLL(d, v))
    while len(x) < int(dur * SR): x = np.concatenate([x, x[int(0.3 * SR):]])
    x = x[: int(dur * SR)].copy(); tt = np.arange(len(x)) / SR
    put(corps, x * np.clip(0.25 + 0.75 * tt / dur, 0, 1) * np.minimum(1, (dur - tt) / 0.05).clip(0, 1), t0, g)
TOM = lambda hi, dyn, n: PD + ('tenor/tenor_higher/tenorH_%s_%d.wav' % (dyn, n) if hi else 'tenor/tenor_lower/tenor_%s_%d.wav' % (dyn, n))
def tom(t_, hi, g=1.0):
    try: x = load(TOM(hi, 'fff', 1 + rng.integers(3)))
    except Exception: x = load(TOM(hi, 'ff', 1))
    put(corps, x, t_, g)
C0 = 36                                                        # the volley
# THE VOLLEY — two bars: kettle drums rolling up from nothing, toms tumbling down through them
troll(t16(C0, 0), 2 * BAR, 2, 5, 1.0); troll(t16(C0, 0) + 0.02, 2 * BAR, 4, 5, 0.9)
for k in range(24):                                            # tom triplets, quickening and heavier
    f = k / 23; t_ = t16(C0, 8) + k * (BAR * 1.5 / 24) * (1.15 - 0.3 * f)
    tom(t_, k % 3 != 2, 0.45 + 0.55 * f)
roll(t16(C0 + 1, 0), t16(C0 + 2, 0), 'p', 'f')                  # and in the midst of it the snares fire
for d in (2, 3, 4): timp(t16(C0 + 2, 0), d, 4, 1.0)            # the landing
tom(t16(C0 + 2, 0), False, 1.0); flam(t16(C0 + 2, 0), 1.2)
# THE CADENCE — military, a section, two alternating bars, to the end
A_ = [(0, 'F'), (2, 't'), (3, 't'), (4, 'A'), (6, 't'), (7, 't'), (8, 'R', 10), (10, 'A'), (11, 't'), (12, 'F'), (14, 't'), (14.5, 't'), (15, 't'), (15.5, 't')]
B2 = [(0, 'A'), (1, 't'), (2, 't'), (3, 't'), (4, 'R', 6), (6, 'A'), (8, 'F'), (9, 't'), (10, 'F'), (11, 't'), (12, 'R', 16)]
def tt16(bar, x):
    i = int(x); fr = x - i
    return t16(bar, i) + fr * S16 if i < 16 else t16(bar + 1, 0)
for bar in range(C0 + 2, BARS):
    pat = A_ if (bar - C0) % 2 == 0 else B2
    for ev in pat:
        st, kind = ev[0], ev[1]; t_ = tt16(bar, st)
        if kind == 't': stroke(t_, 'p' if rng.random() < 0.5 else 'mf', 0.6)
        elif kind == 'A': stroke(t_, 'ff', 1.0); stroke(t_ + 0.001, 'rim', 0.25)
        elif kind == 'F': flam(t_, 1.0)
        elif kind == 'R': roll(t_, tt16(bar, ev[2]))
    timp(t16(bar, 0), 2 if bar % 2 == 0 else 4, 3, 0.8)          # the kettle drums mark every downbeat
    if (bar - C0) % 4 == 3:                                      # and roll into every fourth bar, toms answering
        troll(t16(bar, 8), BAR / 2, 3, 5, 0.7)
        for k in range(6): tom(t16(bar, 10) + k * S16 * 0.66, k % 2 == 0, 0.6 + 0.07 * k)
# the fade — full until 2:00, gone by the end
tt_ = np.arange(N) / SR
corps *= np.interp(tt_, [0, 120.0 + 4 * BAR, BARS * BAR + 0.5], [1, 1, 0]).astype(np.float32)
corps = reverb(corps, 1.6, 0.18, seed=88, bright=6000)

# wax crackle under the keys: the lo-fi dust
cr = np.zeros(N, np.float32); ix = rng.choice(N, int(N / SR * 30), replace=False)
cr[ix] = (rng.standard_normal(len(ix)) * rng.random(len(ix)) ** 3).astype(np.float32); cr = bp(cr, 1200, 6000) * 0.5
keys_lofi = lp(keys, 3800) + cr * 0.06
# the balance, set by rule over the hook bars (10-17): the beat leads, the bass sits
# just under it, the tune rides above the keys, the strings are felt not heard
win = slice(int(19 * BAR * SR), int(27 * BAR * SR))
def at(x, db):
    r = np.sqrt(np.mean(x[win] ** 2)) + 1e-12
    return x * (10 ** (db / 20) / r)
mix = (at(reverb(drums, 0.35, 0.12, seed=3, bright=2500), -14) + at(bass, -21) + at(reverb(keys_lofi, 0.9, 0.16, seed=4), -21)
       + at(reverb(hook, 1.2, 0.2, seed=5), -21))
r_ = np.sqrt(np.mean(horn[: int(4 * BAR * SR)] ** 2)) + 1e-12
# into the tape: driven, band-limited, a little wow — frayed at the edges
mix = np.tanh(mix * 3.2) / 3.2
mix = lp(hp(mix, 45), 6500)
wow = 1 + 0.002 * np.sin(2 * np.pi * np.arange(len(mix)) / SR * 0.6)
idx = np.clip(np.cumsum(wow) - 1, 0, len(mix) - 1); i0 = idx.astype(int)
mix = (mix[i0] * (1 - (idx - i0)) + mix[np.minimum(i0 + 1, len(mix) - 1)] * (idx - i0)).astype(np.float32)
mix += cr * 0.04
mix = mix * DUCK[: len(mix)] if len(mix) <= len(DUCK) else mix
# ONLY THE BAND GOES INTO THE TAPE. The crew, the horn call and the deck are added after
# it, clean, so the voices keep their full range and are never driven or dulled.
rc = np.sqrt(np.mean(corps[int((C0 + 2) * BAR * SR): int((C0 + 10) * BAR * SR)] ** 2)) + 1e-12
mix = mix + at(vox, -17) + horn * (10 ** (-25 / 20) / r_) + deck * 0.9 + corps * (10 ** (-15 / 20) / rc) + battle * 0.85 + melee[: len(mix)] * 0.8
mix = mix[: int((BARS * BAR + 2.5) * SR)]
mix = env(mix, [(0, 0), (0.3, 1), (len(mix) / SR - 2.5, 1), (len(mix) / SR, 0)])
# ── ADRIFT — the coda: alone in a small boat, drifting round an island ─────────
LC = 240.0 - (27.3 + BARS * BAR + 2.5) + 2.5; NC = int(LC * SR); coda = np.zeros(NC, np.float32); rc_ = np.random.default_rng(1885)
t_ = 0.3
while t_ < LC - 1:                                              # water lapping against a little hull, close
    n = int((0.25 + 0.2 * rc_.random()) * SR); tt = np.arange(n) / SR
    slap = lp(rc_.standard_normal(n), 900 + 500 * rc_.random()) * np.exp(-tt * (14 + 8 * rc_.random()))
    slap += 0.25 * hp(rc_.standard_normal(n), 2500) * np.exp(-tt * 30)
    put(coda, slap.astype(np.float32) * (0.15 + 0.12 * rc_.random()), t_); t_ += 0.7 + 0.9 * rc_.random()
swell_ = lp(rc_.standard_normal(NC), 140, 2).astype(np.float32)
coda += rms_db(swell_, -40)
for t_ in np.arange(4.0, LC - 6, 7.5 + 2.0 * rc_.random()):    # the boat creaks as it rocks
    x = sg.resample(creak_[: int(0.9 * SR)], int(0.9 * SR * 1.6)).astype(np.float32)
    put(coda, lp(x, 1600) * 0.12, t_ + rc_.random())
dip = lp(rc_.standard_normal(int(0.5 * SR)), 1400) * np.exp(-np.arange(int(0.5 * SR)) / SR * 6)
put(coda, dip.astype(np.float32) * 0.2, 15.0)                   # an oar dipped once…
for k in range(9):                                              # …and the drips running off it
    m = int(0.05 * SR); tt = np.arange(m) / SR; fq = 900 + 900 * rc_.random()
    drop = np.sin(2 * np.pi * fq * (1 + 2 * tt / tt[-1]) * tt) * np.exp(-tt * 60)
    put(coda, drop.astype(np.float32) * 0.05, 16.0 + k * 0.32 + 0.15 * rc_.random())
isle = mp3('/tmp/ti/sound/cove.mp3'); isle = np.tile(isle, int(np.ceil(NC / len(isle))))[:NC]
coda += rms_db(lp(isle, 700), -36)                              # the surf on the island, far off
coda += rms_db(lp(load('/tmp/snd/src3/Howling_wind.wav')[int(40 * SR): int(40 * SR) + NC], 900), -44)
for t_, c_, d_ in ((22.0, CRIES[2], 0.95), (31.0, CRIES[0], 0.85), (40.5, WG, 0.9), (49.0, CRIES[4], 0.8), (57.0, CRIES[3], 0.95)):
    if t_ < LC - 4: put(coda, at_dist(c_, d_) * 0.16, t_)       # gulls, far away and unhurried
CF = TI('cannon-far.mp3')
for t_ in (12.0, 26.5, 29.0, 44.0, 58.5):                       # a war going on somewhere else, very far off
    if t_ < LC - 6: put(coda, reverb(lp(CF, 260), 4.0, 0.5, seed=int(t_), bright=600) * 0.22, t_)
# the tune, slow, on a flute alone, across the water
fl = np.zeros(NC, np.float32); SL = S16 * 2.1
t_f = 2.5; dist_f = 0.0
for ph in (PHRASE_A, PHRASE_A, PHRASE_B, PHRASE_A, PHRASE_A):   # phrase after phrase, each a little further off
    if t_f > LC - 4: break
    one = np.zeros(NC, np.float32)
    for st, m, d in ph:
        put(one, held('flute', m, d * SL * 1.05 + 0.2, xf=0.2), t_f + st * SL, 0.3)
    one = lp(one, 6000 - 3500 * dist_f) if dist_f > 0 else one
    fl += one * (1.0 - 0.55 * dist_f)
    t_f += 32 * SL + 1.5; dist_f = min(1.0, dist_f + 0.25)
coda += rms_db(reverb(fl, 3.8, 0.5, seed=77, bright=3600), -27)
coda = env(coda, [(0, 0), (1.5, 1), (LC - 7.0, 1), (LC, 0)]) * 1.41
# the drums fade into the water: overlap the last seconds of the song with the coda's first
ov = int(2.5 * SR)
mix = np.concatenate([mix[:-ov], mix[-ov:] + coda[:ov], coda[ov:]]).astype(np.float32)
# ── DAWN — before anything: a calm sea, gulls, and the ship's bell ringing the watch ──
SHIFT = 27.3                                                    # the verse lands at 1:30
LD = SHIFT + 4.0; ND = int(LD * SR); dawn = np.zeros(ND, np.float32); rd = np.random.default_rng(1886)
t_ = 0.0
while t_ < LD:                                                  # small waves running up a beach and back, unhurried
    d = 5.0 + 3.0 * rd.random(); n = int(d * SR); tt = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 2.5
    w_ = lp(rd.standard_normal(n), 1100, 2) * e + 0.18 * hp(rd.standard_normal(n), 2800) * e * np.clip((tt - 0.5 * d) / (0.3 * d), 0, 1)
    put(dawn, w_.astype(np.float32) * (0.5 + 0.3 * rd.random()), t_); t_ += d * (0.55 + 0.2 * rd.random())
dawn = rms_db(reverb(dawn, 1.4, 0.2, seed=40), -30)
dawn += rms_db(lp(rd.standard_normal(ND), 120, 2).astype(np.float32), -42)       # the slow breathing of the swell
for t_, x_, dist in ((1.2, CRIES[0], 0.8), (4.6, CRIES[4], 0.7), (7.9, WG, 0.85), (15.0, CRIES[3], 0.75), (21.0, CRIES[5], 0.85)):
    put(dawn, at_dist(x_, dist) * 0.2, t_)                      # gulls, unhurried, far and near
for k, t_ in enumerate((10.0, 10.55, 12.0, 12.55)):             # the watch bell: ding-ding, ding-ding
    put(dawn, reverb(ship_bell(880.0 * (1 + 0.001 * k)), 3.0, 0.32, seed=95 + k), t_, 0.08)
dawn = env(dawn, [(0, 0), (2.0, 1), (SHIFT, 1), (LD, 0)])
out = np.zeros(int(SHIFT * SR) + len(mix), np.float32)
out[:ND] += dawn; out[int(SHIFT * SR):] += mix
mix = out
mix = hp(mix, 28)
write_mp3(rms_db(mix, -17), 'EXPERIMENT-fifteen-men-hiphop-v19.mp3', br='192k')
print(files, f'{BARS} bars at {BPM} bpm')
