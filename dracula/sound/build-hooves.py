"""Rebuild the ch I coach and calèche cues: the same voice, new hooves scored to the text."""
import sys, numpy as np, subprocess, scipy.io.wavfile as wv
sys.path.insert(0, '/tmp/claude-0/hb')
import engine as E
from engine import SR, db, put, one, lp, hp, pitch, norm, reverb, fade, stereo, curve, team, texture, wheels, creaks
from lib import separate, cue, mixfile, rmsdb
OUT = '/tmp/claude-0/hb/out/'; import os; os.makedirs(OUT, exist_ok=True)
R = np.random.default_rng(1897)

def setup(n):
    mix, res, ps, offs = separate(n)
    texts = [b['text'] for b in E.B if b['n'] == n]
    spans = [(o / SR, o / SR + len(p) / SR, t) for (o, g), p, t in zip(offs, ps, texts)]
    N = len(mix) + int(1.0 * SR)
    v = np.zeros(N, np.float32)
    for (o, g), p in zip(offs, ps): v[o:o + len(p)] += p * g
    return N, v, spans, res

def T(spans, ph, after=False): return E.at(spans, ph, after)

def stamps(bus, t0, t1, rate=1.5, gain=-8, surface='road', seed=0):
    rr = np.random.default_rng(seed); t = t0
    pool = E.POOL[surface]
    while t < t1:
        x = pitch(pool[rr.integers(len(pool))], rr.uniform(-2, 0.5)) * rr.uniform(0.4, 1.0)
        put(bus, x, t, gain, rr.uniform(-0.5, 0.5)); t += rr.exponential(1 / rate) + 0.12

NEIGH = ['0284', '0460', '0863', '1541', '1542']; SNORT = ['0285', '0286', '0287', '1543']
def neigh(bus, t, gain=-10, pan=0.0, semis=0.0, k=None):
    k = k or NEIGH[R.integers(len(NEIGH))]; put(bus, pitch(norm(one(k), -14), semis), t, gain, pan)
def snort(bus, t, gain=-14, pan=0.0):
    put(bus, pitch(norm(one(SNORT[R.integers(len(SNORT))]), -14), R.uniform(-3, 0)), t, gain, pan)
def whip(bus, t, gain=-6, k=None):
    k = k or ['2949', '2950', '2961', '2962'][R.integers(4)]; put(bus, reverb(E.peaknorm(one(k), -10), 0.9, 0.25), t, gain, R.uniform(-0.2, 0.2))
def wolves(bus, t, gain=-14, pan=0.0, k='wolves.mp3', far=0.0, dur=None):
    x = norm(one(k, E.F), -14)
    if dur: x = fade(x[:int(dur * SR)], 0.5, 2.0)
    if far: x = reverb(lp(x, 4000 - 2500 * far), 2.2, 0.3 + 0.4 * far)
    put(bus, x, t, gain, pan)
def dog(bus, t, gain=-20, pan=0.0, far=1.0):
    k = ['2450', '2451'][R.integers(2)]; x = norm(one(k), -14)
    x = reverb(lp(x, 2500 - 1200 * far), 2.6, 0.5); put(bus, x, t, gain, pan)
def wind(n, t0, level_keys, seed=0):
    w = E.load(E.F + 'wind.mp3'); w = np.tile(w, int(np.ceil(n / len(w))) + 1)[:n]
    return stereo(w * curve(level_keys, n), 0.0)

def finish(n_cue, name, N, v, fx, keep=None, free=None):
    """keep = (residual, t_until): reuse the old sound before t_until (crowd, inn)."""
    env = np.sqrt(sg_l(v ** 2, 0.25)); duck = 1 - 0.45 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    fx = fx * duck[:, None]
    if free is not None: fx = fx + free
    fx = limit(fx, -9)
    if keep is not None:
        res, tu = keep; k = int(tu * SR); xf = int(1.5 * SR)
        r = np.zeros(N, np.float32); r[:len(res)] = res
        g = np.ones(N, np.float32); g[k:k + xf] = np.linspace(1, 0, xf); g[k + xf:] = 0
        fx = fx * (1 - g)[:, None] + stereo(r * g)
    mix = (stereo(v) * np.sqrt(2) + fx) / np.sqrt(2)
    pk = np.abs(mix).max()
    mix = limit(mix, -0.7)
    wv.write(OUT + name + '-fx.wav', SR, fx)
    wv.write(OUT + name + '.wav', SR, mix)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + name + '.wav', '-ar', '44100', '-b:a', '160k', OUT + name + '.mp3'])
    print(n_cue, name, round(N / SR, 1), 's  voice', round(rmsdb(v), 1), ' fx', round(rmsdb(fx), 1))

import scipy.signal as sg
def limit(x, thr_db):
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    thr = db(thr_db); a = np.abs(x).max(1)
    g = np.minimum(1, thr / (a + 1e-9)); k = int(0.006 * SR)
    g = minimum_filter1d(g, 2 * k + 1); g = uniform_filter1d(g, k)
    return (x * g[:, None]).astype(np.float32)
def sg_l(x, sec):
    k = int(sec * SR); return sg.lfilter(np.ones(k) / k, 1, x)

# ═══ 30 — the whip, and a lurching start (keep the inn crowd before it) ═══════════════
def c30():
    N, v, s, res = setup(30); fx = np.zeros((N, 2), np.float32)
    tw = T(s, 'cracked his big whip'); ts = T(s, 'and we set off')
    stamps(fx, tw - 8, tw, 0.8, -14, seed=30)
    snort(fx, tw - 3, -16)
    whip(fx, tw + 0.4, -4); whip(fx, tw + 1.3, -7)
    sp = curve([(0, 0), (tw + 0.6, 0), (tw + 1.2, 1.2), (tw + 3.5, 2.0), (N / SR, 2.2)], N)
    fx += team(N, sp, 'road', 4, 1.5, seed=301) * db(-12)
    fx += wheels(N, sp, 302) * db(-8) + creaks(N, [tw + 1.0, tw + 2.2, tw + 4.0], 303) * db(-4)
    neigh(fx, tw + 0.9, -18, 0.3)
    finish(30, 'drac1-whip-29-v3', N, v, fx, keep=(res, tw - 1.0))

# ═══ 31 — an easy trot through the Mittel Land, fading under; quickening at 'feverish haste' ═══
def c31():
    N, v, s, res = setup(31); fx = np.zeros((N, 2), np.float32); L = N / SR
    th = T(s, 'seemed to fly over it with a feverish haste'); tb = T(s, 'reaching Borgo Prund', True)
    sp = curve([(0, 2.2), (th - 2, 2.1), (th + 1, 3.2), (tb, 3.0), (tb + 8, 2.2), (L, 2.1)], N)
    lev = curve([(0, -12), (14, -19), (th - 3, -21), (th, -14), (tb + 6, -16), (tb + 16, -21), (L, -21)], N)
    g = db(lev)[:, None]
    fx += team(N, sp, 'road', 4, 1.5, seed=311) * g
    fx += wheels(N, sp, 312) * g * db(3)
    fx += creaks(N, list(np.cumsum(R.uniform(5, 11, 30))), 313) * g * db(6)
    for t in [24, 58, th + 3, 96]:
        if t < L - 2: snort(fx, t, -26)
    finish(31, 'drac1-coach-30-v3', N, v, fx)

# ═══ 34 — dusk: trot, a peasant's cart passing, labouring at a walk on the climb, a stop to light the lamps ═══
def c34():
    N, v, s, res = setup(34); fx = np.zeros((N, 2), np.float32); L = N / SR
    tl = T(s, 'Now and again we passed a leiter-wagon'); tc = T(s, 'it began to get very cold')
    ts = T(s, 'the horses could only go slowly'); tdr = T(s, '“No, no,” he said')
    tp = T(s, "a moment’s pause to light his lamps")
    sp = curve([(0, 2.1), (tc, 2.0), (ts - 4, 2.0), (ts, 1.1), (tdr + 6, 1.0), (tdr + 14, 1.6), (tp - 1.5, 1.4), (tp + 1.5, 0), (L, 0)], N)
    lev = curve([(0, -20), (tl - 6, -21), (ts - 2, -19), (ts + 2, -15), (tdr, -17), (L, -17)], N)
    g = db(lev)[:, None]
    fx += team(N, sp, 'road', 4, 1.0, seed=341) * g
    fx += wheels(N, sp, 342) * g * db(3)
    fx += creaks(N, [t for t in np.cumsum(R.uniform(6, 13, 30)) if t < L - 2], 343) * g * db(6)
    # the leiter-wagon passing the other way: one horse at a walk, its wheels
    cart = norm(E.load(E.F + 'cart.mp3'), -20); cart = fade(cart, 3, 4) * np.hanning(len(cart))
    put(fx, cart, tl + 1, -6, 0.5)
    # labouring: breath and snorts on the climb
    for t in np.arange(ts + 1, tdr + 12, 4.5): snort(fx, t + R.uniform(0, 1.5), -16, R.uniform(-.5, .5))
    # the halt and the lamps
    stamps(fx, tp + 1.5, L, 1.2, -14, seed=344); snort(fx, tp + 2.0, -12)
    put(fx, norm(E.load(E.F + 'match.mp3'), -18), min(tp + 2.5, L - 2.2), -6)
    finish(34, 'drac1-dusk-33-v3', N, v, fx)

# ═══ 35 — lashed into a gallop; the coach rocks; thunder; slowing to a dead stop at the Pass ═══
def c35():
    N, v, s, res = setup(35); fx = np.zeros((N, 2), np.float32); L = N / SR
    tla = T(s, 'He lashed the horses unmercifully'); tro = T(s, 'the crazy coach rocked')
    tlev = T(s, 'The road grew more level'); tpa = T(s, 'we were entering on the Borgo Pass')
    tgif = T(s, 'One by one several of the passengers'); tfl = T(s, 'Then, as we flew along')
    tth = T(s, 'the heavy, oppressive sense of thunder'); tst = T(s, 'in which the steam from our hard-driven horses')
    tno = T(s, 'there was on it no sign of a vehicle'); tw = T(s, 'the driver, looking at his watch')
    sp = curve([(0, 2.2), (tla, 2.3), (tla + 1.5, 3.4), (tla + 5, 4.0), (tro, 4.0), (tlev, 4.3), (tpa, 4.2),
                (tgif + 2, 3.2), (tfl - 1, 3.3), (tfl + 1, 4.1), (tth, 3.8), (tst - 6, 3.0), (tno, 2.0),
                (tw - 3, 1.2), (tw, 0), (L, 0)], N)
    lev = curve([(0, -18), (tla, -16), (tla + 3, -10), (tro + 12, -14), (tlev, -11), (tpa + 4, -15),
                 (tgif + 4, -21), (tfl, -18), (tfl + 3, -12), (tth - 4, -17), (tno, -18), (tw, -18), (L, -18)], N)
    g = db(lev)[:, None]
    fx += team(N, sp, 'road', 4, 1.0, seed=351) * g
    fx += wheels(N, sp, 352) * g * db(4)
    rock = list(tro + np.cumsum(R.uniform(0.7, 1.6, 12))) + list(tfl + np.cumsum(R.uniform(1, 2.5, 8)))
    fx += creaks(N, [t for t in rock if t < L - 1], 353) * db(-6)
    for k, t in enumerate([tla + 0.3, tla + 1.6, tla + 3.4, tfl + 0.4]): whip(fx, t, -5 - 2 * (k % 2))
    neigh(fx, tla + 2.2, -16, -0.3)
    th = reverb(lp(norm(E.load(E.F + 'thunder.mp3'), -16), 900), 3.0, 0.5)
    put(fx, th, tth - 1, -6); put(fx, th, tth + 22, -12)
    for t in np.arange(tst - 1, tw + 6, 2.6): snort(fx, t + R.uniform(0, 1), -15, R.uniform(-.6, .6))
    stamps(fx, tw + 0.5, L, 1.0, -15, seed=354)
    finish(35, 'drac1-lashed-34-v3', N, v, fx)

# ═══ 46 — the calèche: black horses, heavier; into the dark at speed; the coach away to Bukovina ═══
def c46():
    N, v, s, res = setup(46); fx = np.zeros((N, 2), np.float32); L = N / SR
    tsh = T(s, 'Without a word he shook his reins'); tsw = T(s, 'we swept into the darkness of the Pass')
    tcr = T(s, 'Then the driver cracked his whip'); tsank = T(s, 'As they sank into the darkness')
    tcl = T(s, 'but a cloak was thrown')
    stamps(fx, 0.5, tsh, 0.9, -15, seed=461)
    snort(fx, 6, -16, 0.4); snort(fx, tsh - 3, -14, -0.4)
    sp = curve([(0, 0), (tsh, 0), (tsh + 1, 2.5), (tsw + 1, 3.8), (tcl, 3.6), (L, 3.4)], N)
    lev = curve([(0, -14), (tsw, -12), (tsw + 6, -17), (tcr, -20), (L, -19)], N)
    fx += team(N, sp, 'road', 4, -3.0, seed=462) * db(lev)[:, None]
    fx += wheels(N, sp, 463) * db(lev - 2)[:, None]
    # the old coach, behind and going away
    sp2 = curve([(0, 0), (tcr, 0), (tcr + 1.5, 2.6), (L, 3.0)], N)
    away = curve([(0, -60), (tcr, -14), (tsank, -22), (tsank + 8, -40), (L, -60)], N)
    fx += team(N, sp2, 'road', 4, 1.5, seed=464) * db(away)[:, None] * np.array([1.3, 0.5])
    whip(fx, tcr + 0.5, -10); put(fx, lp(norm(one('0460'), -14), 3000), tcr + 2.0, -18, 0.6)
    finish(46, 'drac1-into-the-pass-45-v3', N, v, fx)

# ═══ 48 — hard pace, a complete turn, the same ground again; a match struck ═══
def c48():
    N, v, s, res = setup(48); fx = np.zeros((N, 2), np.float32); L = N / SR
    thp = T(s, 'The carriage went at a hard pace'); ttu = T(s, 'then we made a complete turn')
    tsg = T(s, 'simply going over and over the same ground'); tm = T(s, 'I struck a match')
    tmid = T(s, 'it was within a few minutes of midnight')
    sp = curve([(0, 3.4), (thp, 3.8), (ttu, 3.9), (ttu + 1.5, 2.2), (ttu + 4, 2.4), (ttu + 7, 3.8), (tsg + 6, 3.9),
                (tsg + 12, 2.3), (tsg + 15, 3.7), (tm - 3, 3.6), (L, 3.5)], N)
    lev = curve([(0, -17), (thp, -13), (ttu + 8, -18), (tm - 2, -21), (tmid, -22), (L, -18)], N)
    fx += team(N, sp, 'road', 4, -3.0, seed=481) * db(lev)[:, None]
    fx += wheels(N, sp, 482) * db(lev - 1)[:, None]
    fx += creaks(N, [ttu + 0.5, ttu + 1.6, tsg + 12.5], 483) * db(-6)
    put(fx, norm(E.load(E.F + 'match.mp3'), -18), tm + 0.3, -4)
    finish(48, 'drac1-midnight-47-v3', N, v, fx)

# ═══ 49 — the dogs, the horses rear; the wolves; the driver soothes them; off at a great pace ═══
def c49():
    N, v, s, res = setup(49); fx = np.zeros((N, 2), np.float32); L = N / SR
    td = T(s, 'Then a dog began to howl'); tan = T(s, 'The sound was taken up by another dog')
    twi = T(s, 'a wild howling began'); tfh = T(s, 'At the first howl the horses began to strain and rear')
    tso = T(s, 'but the driver spoke to them soothingly'); tsh = T(s, 'but shivered and sweated')
    two = T(s, 'a louder and a sharper howling'); tre = T(s, 'whilst they reared again and plunged madly')
    tfew = T(s, 'In a few minutes, however'); tdes = T(s, 'the driver was able to descend')
    tpet = T(s, 'He petted and soothed them'); tre2 = T(s, 'The driver again took his seat')
    tgp = T(s, 'started off at a great pace'); tnar = T(s, 'he suddenly turned down a narrow roadway')
    sp = curve([(0, 3.0), (td, 3.0), (tfh, 2.8), (tfh + 1.0, 0), (tre2 + 1, 0), (tgp, 0), (tgp + 1.5, 3.4), (tnar, 4.0), (tnar + 2, 3.0), (L, 3.6)], N)
    lev = curve([(0, -20), (td, -22), (tfh, -18), (tgp, -12), (tgp + 5, -15), (L, -16)], N)
    fx += team(N, sp, 'road', 4, -3.0, seed=491) * db(lev)[:, None]
    fx += wheels(N, sp, 492) * db(lev - 1)[:, None]
    # the dogs: one far down the road, then another, and another, and another, then the whole country
    dogs = np.zeros((N, 2), np.float32)
    def howl(t, semis, gain, pan, far):
        k = ['2450', '2451'][R.integers(2)]; x = pitch(E.peaknorm(one(k), -6), semis)
        x = reverb(lp(x, 3600 - 1800 * far), 2.6, 0.3 + 0.35 * far, 7)
        put(dogs, x, t, gain, pan)
    t1 = T(s, 'began to howl', True)
    for t, sm in [(t1 + 0.2, -1.0), (t1 + 3.0, -0.5), (t1 + 5.8, -1.5)]: howl(t, sm, -7, 0.5, 0.5)
    for t in [tan + 1.2, tan + 3.8]: howl(t, 1.5, -9, -0.6, 0.6)
    ta1 = T(s, 'and then another'); ta2 = T(s, 'and another', True)
    for t in [ta1 + 0.6, ta1 + 3.4]: howl(t, -3.0, -10, 0.2, 0.7)
    for t in [ta2 + 0.1, ta2 + 3.0]: howl(t, 3.0, -11, -0.25, 0.75)
    rr = np.random.default_rng(49)
    for t in np.sort(rr.uniform(twi - 0.5, tfh + 4, 18)):
        howl(t, rr.uniform(-4, 4), rr.uniform(-18, -10), rr.uniform(-0.9, 0.9), rr.uniform(0.5, 1.0))
    dogs *= curve([(0, 1), (tfh + 2, 1), (tfh + 8, 0.25), (L, 0.25)], N)[:, None]
    # the horses strain and rear
    neigh(fx, tfh + 0.3, -8, -0.3, 2); stamps(fx, tfh, tso + 3, 3.0, -8, seed=493)
    for t in np.arange(tso, tsh + 6, 2.2): snort(fx, t + R.uniform(0, .8), -12, R.uniform(-.5, .5))
    # wolves from the mountains on each side
    wolves(fx, two, -12, -0.6, far=0.5); wolves(fx, two + 4, -14, 0.6, 'wolf-howl.mp3', far=0.4)
    wolves(fx, tre - 2, -12, 0.4, far=0.3, dur=16)
    neigh(fx, tre + 0.2, -6, 0.2, 3, '0863'); neigh(fx, tre + 1.6, -9, -0.4, 1.5)
    stamps(fx, tre, tfew + 4, 4.0, -6, seed=494)
    for t in np.arange(tdes, tre2, 2.4): snort(fx, t + R.uniform(0, .8), -16, R.uniform(-.4, .4))
    stamps(fx, tpet, tre2, 0.6, -18, seed=495)
    whip(fx, tgp - 0.2, -14)
    finish(49, 'drac1-howling-48-v3', N, v, fx, free=dogs)

# ═══ 50 — the tunnel of trees: wind, snow muffling the hooves, the wolves closing in ═══
def c50():
    N, v, s, res = setup(50); fx = np.zeros((N, 2), np.float32); L = N / SR
    trw = T(s, 'we could hear the rising wind'); tsn = T(s, 'fine, powdery snow began to fall')
    tdg = T(s, 'The keen wind still carried the howling of the dogs'); twn = T(s, 'The baying of the wolves sounded nearer')
    taf = T(s, 'I grew dreadfully afraid'); tdv = T(s, 'The driver, however')
    sp = curve([(0, 3.8), (tsn, 3.8), (tsn + 10, 3.4), (taf, 3.6), (L, 3.6)], N)
    snow = curve([(0, 0), (tsn, 0.1), (tsn + 12, 0.85), (L, 0.9)], N)
    lev = curve([(0, -14), (trw, -17), (tsn + 10, -15), (L, -15)], N)
    fx += team(N, sp, 'road', 4, -3.0, seed=501, snow=snow) * db(lev)[:, None]
    fx += wheels(N, sp, 502) * db(lev - 2)[:, None] * (1 - 0.6 * snow)[:, None]
    fx += wind(N, 0, [(0, 0.15), (trw, 0.25), (trw + 6, 0.6), (tsn + 10, 0.5), (L, 0.55)]) * db(-6)
    for t in [trw + 3, trw + 8.5]: put(fx, reverb(hp(norm(one('1316')[:int(0.8 * SR)], -18), 500), 1.0, 0.3), t, -14, R.uniform(-.6, .6))
    dog(fx, tdg + 0.5, -24, 0.7); dog(fx, tdg + 4, -27, -0.6)
    wolves(fx, twn, -16, -0.7, far=0.6); wolves(fx, twn + 6, -13, 0.6, 'wolf-howl.mp3', far=0.3)
    wolves(fx, tdv - 2, -11, -0.3, far=0.2, dur=14)
    for t in [taf + 1, taf + 4]: snort(fx, t, -14, R.uniform(-.5, .5))
    finish(50, 'drac1-tunnel-49-v3', N, v, fx)

# ═══ 51 — the blue flame: checked to a stop, the wolves closer; resumed; the moving circle ═══
def c51():
    N, v, s, res = setup(51); fx = np.zeros((N, 2), np.float32); L = N / SR
    tch = T(s, 'he at once checked the horses'); twc = T(s, 'the howling of the wolves grew closer')
    tre = T(s, 'and we resumed our journey'); tdr = T(s, 'I think I must have fallen asleep')
    ton = T(s, 'Once the flame appeared so near the road'); tst = T(s, 'gathering a few stones')
    tno = T(s, 'Then for a time there were no blue flames'); tsp = T(s, 'and we sped onwards through the gloom')
    sp = curve([(0, 3.6), (tch, 3.5), (tch + 2.5, 0), (tre - 0.5, 0), (tre + 2, 3.0), (ton - 2, 3.0), (ton + 1, 0.8),
                (tst + 6, 0.8), (tno - 1, 1.5), (tsp, 3.6), (tsp + 3, 4.0), (L, 4.0)], N)
    snow = curve([(0, 0.85), (L, 0.85)], N)
    lev = curve([(0, -15), (tch + 3, -16), (tdr, -20), (tsp, -13), (L, -13)], N)
    fx += team(N, sp, 'road', 4, -3.0, seed=511, snow=snow) * db(lev)[:, None]
    fx += wheels(N, sp, 512) * db(lev - 5)[:, None]
    snort(fx, tch + 2.6, -12, 0.3); stamps(fx, tch + 2.8, tre, 1.0, -16, seed=513)
    wolves(fx, twc, -12, -0.6, far=0.3, dur=15); wolves(fx, twc + 5, -15, 0.7, 'wolf-howl.mp3', far=0.2)
    stamps(fx, tst, tst + 6, 0.8, -18, seed=514)
    put(fx, reverb(norm(one('0496')[:int(0.4 * SR)], -24), 1.2, 0.4), tst + 1.0, -14, -0.5)   # stones
    # the moving circle: howls handed round from side to side
    for k, t in enumerate(np.arange(tsp, L - 3, 6.5)):
        wolves(fx, t, -13 - (k % 2) * 3, [-0.8, 0.0, 0.8, 0.3][k % 4], ['wolf-howl.mp3', 'wolves.mp3'][k % 2], far=0.3, dur=9)
    finish(51, 'drac1-blue-flame-50-v3', N, v, fx)

# ═══ 52 — alone: the horses tremble, snort and scream; then the grim silence of the ring ═══
def c52():
    N, v, s, res = setup(52); fx = np.zeros((N, 2), np.float32); L = N / SR
    ttr = T(s, 'the horses began to tremble worse than ever'); tsc = T(s, 'to snort and scream with fright')
    tce = T(s, 'the howling of the wolves had ceased altogether'); tmo = T(s, 'just then the moon')
    tgr = T(s, 'in the grim silence which held them')
    for t in np.arange(1, ttr, 3.5): snort(fx, t + R.uniform(0, 1), -20, R.uniform(-.5, .5))
    stamps(fx, 1, ttr, 0.5, -20, seed=521)
    stamps(fx, ttr, tce + 2, 3.5, -8, seed=522)
    for t in np.arange(ttr, tsc + 1, 1.3): snort(fx, t + R.uniform(0, .6), -10, R.uniform(-.6, .6))
    neigh(fx, tsc + 0.6, -5, -0.3, 3.5, '0863'); neigh(fx, tsc + 2.0, -7, 0.4, 2.5, '1542')
    # then nothing but breath, very low
    for t in np.arange(tmo, L - 2, 4.0): snort(fx, t + R.uniform(0, 1.5), -26, R.uniform(-.4, .4))
    finish(52, 'drac1-ring-51-v3', N, v, fx)

# ═══ 53 — the wolves howl as one; the horses rear and plunge; he beats the calèche; the wolves fall back ═══
def c53():
    N, v, s, res = setup(53); fx = np.zeros((N, 2), np.float32); L = N / SR
    thw = T(s, 'All at once the wolves began to howl'); tju = T(s, 'The horses jumped about and reared')
    tca = T(s, 'I called to the coachman to come'); tbe = T(s, 'I shouted and beat the side of the calèche')
    tvo = T(s, 'I heard his voice raised'); tfb = T(s, 'the wolves fell back and back further still')
    tcl = T(s, 'Just then a heavy cloud passed')
    for k, (dt, pan) in enumerate([(0, -0.8), (0.8, 0.8), (1.7, -0.2), (2.5, 0.4), (4, -0.5), (6, 0.7)]):
        wolves(fx, thw + dt, -9 - k, pan, ['wolves.mp3', 'wolf-howl.mp3'][k % 2], far=0.1)
    for k, t in enumerate(np.arange(thw + 9, tvo, 5.0)):
        wolves(fx, t, -13, [0.7, -0.7, 0.2][k % 3], ['wolf-howl.mp3', 'wolves.mp3'][k % 2], far=0.15, dur=10)
    stamps(fx, tju, tvo, 4.5, -5, seed=531)
    for k, t in enumerate([tju + 0.2, tju + 1.8, tju + 4.5, tca + 1, tbe + 3]):
        neigh(fx, t, -6 - (k % 2) * 2, [-.4, .4, 0, .3, -.3][k], 2.0 + k % 2)
    # beating the side of the calèche: wood
    knock = reverb(lp(E.peaknorm(one('0498'), -8), 2500), 0.6, 0.2)
    for k in range(6): put(fx, knock, tbe + 0.5 + k * 0.33 + R.uniform(0, .06), -4, 0.1)
    for t in np.arange(tvo, tfb + 4, 2.0): snort(fx, t + R.uniform(0, .6), -14, R.uniform(-.5, .5))
    # falling back: a last howl, far off
    wolves(fx, tfb + 1, -22, 0.0, 'wolf-howl.mp3', far=0.8)
    stamps(fx, tvo, tcl, 1.0, -15, seed=532)
    finish(53, 'drac1-wolves-52-v3', N, v, fx)

# ═══ 54 — climbing on; ascending, quick descents; pulled up on the stones of the courtyard ═══
def c54():
    N, v, s, res = setup(54); fx = np.zeros((N, 2), np.float32); L = N / SR
    tcl = T(s, 'the driver was climbing into the calèche'); tsw = T(s, 'as we swept on our way')
    tas = T(s, 'We kept on ascending'); tqd = T(s, 'with occasional periods of quick descent')
    tma = T(s, 'but in the main always ascending'); tsu = T(s, 'Suddenly, I became conscious')
    tpu = T(s, 'pulling up the horses in the courtyard')
    put(fx, creaks(N, [tcl + 0.6], 541)[: int(L * SR)], 0, 2)
    stamps(fx, 0.5, tcl + 2, 1.0, -16, seed=542)
    sp = curve([(0, 0), (tcl + 1.5, 0), (tcl + 3, 2.6), (tsw, 3.4), (tas, 2.6), (tqd, 2.4), (tqd + 1.5, 4.0), (tma - 0.5, 3.8),
                (tma + 2, 2.3), (tsu, 2.4), (tpu, 2.0), (tpu + 3, 1.0), (tpu + 5.5, 0), (L, 0)], N)
    stone = curve([(0, 0), (tpu - 0.5, 0), (tpu + 1.0, 1), (L, 1)], N)
    lev = curve([(0, -16), (tsw, -15), (tas, -17), (tqd + 1, -13), (tma + 2, -17), (tpu, -15), (L, -15)], N)
    road = team(N, sp, 'road', 4, -3.0, seed=543, snow=curve([(0, 0.85), (L, 0.85)], N))
    court = team(N, sp, 'stone', 4, -2.0, seed=544)
    court = reverb(court[:, 0], 2.4, 0.45, 5)[:, None] * np.array([[0.8, 0.8]])
    fx += (road * (1 - stone)[:, None] + court * stone[:, None]) * db(lev)[:, None]
    fx += wheels(N, sp, 545) * db(lev - 3)[:, None]
    for t in np.arange(tas + 1, tqd, 3.0): snort(fx, t, -18, R.uniform(-.5, .5))
    snort(fx, tpu + 5.8, -10, -0.3)
    put(fx, reverb(norm(one('0496')[:int(1.5 * SR)], -20), 2.4, 0.5, 5)[:, None] * np.array([[0.7, 0.7]]), tpu + 6.5, -10)
    finish(54, 'drac1-castle-53-v3', N, v, fx)

if __name__ == '__main__':
    todo = sys.argv[1:] or ['30', '31', '34', '35', '46', '48', '49', '50', '51', '52', '53', '54']
    for k in todo: globals()['c' + k]()
