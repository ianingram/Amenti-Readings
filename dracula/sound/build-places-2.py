"""Amenti-Readings/dracula/sound/build-places-2.py · 22 Nov 2026
Books I–II public places, by the standing rule (Ian, 22 Nov: "Public spaces get their own
story room"). Same method as build-places.py, whose helpers it imports. BigSoundBank CC0."""
import sys, os, numpy as np
sys.argv = sys.argv[:3]
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import importlib.util
spec = importlib.util.spec_from_file_location('bp', os.path.join(here, 'build-places.py'))
src = open(os.path.join(here, 'build-places.py')).read().split('L = 64*SR')[0]   # helpers only
bp = {}; exec(compile(src, 'build-places.py', 'exec'), bp)
load, lp, hp, rms, room, grains, scatter, loopify, save, SR, R = (bp[k] for k in
    'load lp hp rms room grains scatter loopify save SR R'.split())
L = 64*SR; LL = 70*SR
talk = [load(n) for n in ['3542','3376','0624','0480','2561']]
fire = [load('2855'), load('2856')]
def bedfire(LL, g):
    f = np.concatenate([fire[0], fire[1]]*3)[:LL]; return g*f/rms(f)
# ── an old inn at night (the Golden Krone): a fire, talk below through the floor, boards, a cup
inn = bedfire(LL, 0.6)
inn += 0.5*lp(grains([lp(t,700) for t in talk], LL, 2), 600)/1.0
scatter(inn, [load('0165'), load('1515')], 12.0, 0.18, dur=2.5, lpf=2500)
scatter(inn, [load('1196'), load('1192')], 14.0, 0.08, dur=1.0, lpf=3000)
inn = room(hp(inn, 50), 0.3, [(9,.3),(19,.22),(37,.15)], 0.3)
save(loopify(inn, L), 'inn-night.mp3', -31)
# ── a noisy country inn full of diners (Jack Straw's Castle): talk, glasses, laughter well back, a fire
tav = 1.0*lp(hp(grains([lp(t,1700) for t in talk], LL, 5), 120), 1700)
scatter(tav, [load('0472'), load('0471')], 4.0, 0.2, dur=1.5, lpf=5000)
scatter(tav, [lp(load('0490'),2000), lp(load('0480'),1500)], 9.0, 0.12, dur=1.6)
tav += bedfire(LL, 0.25)
tav = room(tav, 0.4, [(10,.3),(21,.24),(39,.18),(63,.1)], 0.4)
save(loopify(tav, L), 'tavern.mp3', -27)
# ── the Zoological Gardens by day: birds and aviaries, the beast houses at a distance, visitors on gravel
zoo = 0.6*np.concatenate([load('1164'), load('1165') if os.path.exists(os.path.join(bp['S'],'1165.mp3')) else load('1164')])[:LL]
zoo = zoo/rms(zoo)*0.6
b = load('0222'); st = R.integers(0, len(b)-LL); zoo += 0.5*b[st:st+LL]/rms(b[st:st+LL])
beasts = lp(np.concatenate([load('1005'), load('1004')]*2)[:LL], 1500); zoo += 0.45*beasts/rms(beasts)
zoo += 0.35*lp(grains([lp(load('1082'),1200), lp(load('2728'),1200)], LL, 2), 1200)
scatter(zoo, [load('3216')], 9.0, 0.25, dur=3.0, lpf=4000)
zoo = hp(zoo, 80)
save(loopify(zoo, L), 'zoo.mp3', -29)
# ── Hyde Park Corner and Piccadilly, 1893: carriages and cabs on wood and stone, the crowd, a far 'bus
hooves = [load(n) for n in ['0610','0496','1854','0289']]
st = np.zeros(LL)
for k in range(14):                    # carriages passing: a trotting horse with wheels, rising and falling
    t0 = R.uniform(-3, 68); dur = R.uniform(6, 11); n = int(dur*SR)
    h = hooves[R.integers(len(hooves))]; s0 = R.integers(0, max(1, len(h)-n)); y = h[s0:s0+n]
    if len(y) < n: y = np.pad(y, (0, n-len(y)))
    w = load('1316'); w = np.resize(w, n)
    env = np.hanning(n)**1.5
    y = (y/rms(y) + 0.5*lp(w,1500)/rms(w))*env*R.uniform(.4,1)
    p = int(t0*SR); a, bnd = max(0,p), min(LL, p+n)
    if bnd > a: st[a:bnd] += y[a-p:bnd-p]
st = lp(st, 4500)
crowd = [lp(load('3515'),1300), lp(load('2969'),1300), lp(load('2728'),1300)]
st += 0.8*grains(crowd, LL, 3)
scatter(st, [load('1318'), load('0514')], 5.0, 0.2, dur=3.0, lpf=3500)
st = room(hp(st, 60), 0.5, [(25,.25),(60,.18),(110,.12)], 0.25)
save(loopify(st, L), 'street-1893.mp3', -27)
