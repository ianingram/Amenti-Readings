"""Amenti-Readings/dracula/sound/build-places.py · 22 Nov 2026
Rooms for Book III's public places (Ian: "most hotels have a noise about them.. just like a
train station, or a restaurant, or armory"). BigSoundBank recordings, CC0 (SOURCES.md).
Beds are texture only — the player plays three loops of one file at once, so nothing in a
bed may stand out; distinct sounds (bells, whistles, a rifle action) are one-shots on words.
Talk is cut into shuffled 0.6–1.8 s grains and low-passed so no words survive."""
import subprocess, numpy as np, sys, os
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; S = sys.argv[1] if len(sys.argv) > 1 else '../src/'; OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
R = np.random.default_rng(1893)
def load(n):
    r = subprocess.run(['ffmpeg','-v','0','-i',os.path.join(S,n+'.mp3'),'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(r, np.float32).copy()
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def rms(x): return np.sqrt(np.mean(x**2))+1e-12
def room(x, tail, early, wet):
    n = int(tail*3*SR); ir = np.zeros(n); ir[0] = 1
    for ms, g in early: ir[int(ms*SR/1000)] += g
    ir += R.standard_normal(n)*np.exp(-np.arange(n)/(tail*SR))*0.08
    y = fftconvolve(x, ir)[:len(x)]
    return (1-wet)*x + wet*y/ (rms(y)/rms(x))
def grains(srcs, L, layers=3, gmin=.6, gmax=1.8, step=(.45,.7)):
    out = np.zeros(L)
    for _ in range(layers):
        pos = int(R.uniform(0,.5)*SR)
        while pos < L:
            s = srcs[R.integers(len(srcs))]; n = int(R.uniform(gmin,gmax)*SR)
            st = R.integers(0, len(s)-n); y = s[st:st+n].copy()
            if rms(y) < 1e-3: pos += n//2; continue
            y = y/rms(y)*np.hanning(n)*R.uniform(.5,1); e = min(L,pos+n); out[pos:e] += y[:e-pos]
            pos += int(n*R.uniform(*step))
    return out
def scatter(out, src, every, gain, dur=None, lpf=None, jitter=.5):
    t = R.uniform(0, every)
    while t < len(out)/SR - 1:
        s = src[R.integers(len(src))] if isinstance(src, list) else src
        n = int((dur or len(s)/SR)*SR); n = min(n, len(s)); st = R.integers(0, len(s)-n+1)
        y = s[st:st+n].copy(); f = np.ones(n); k = min(n//4, int(.03*SR)); f[:k] = np.linspace(0,1,k); f[-k:] = np.linspace(1,0,k)
        y = y*f/ (np.abs(y).max()+1e-9)
        if lpf: y = lp(y, lpf)
        p = int(t*SR); e = min(len(out), p+n); out[p:e] += gain*y[:e-p]*R.uniform(.6,1)
        t += every*R.uniform(1-jitter, 1+jitter)
def loopify(x, L, xf=6):
    n = int(xf*SR); y = x[:L].copy(); tail = x[L:L+n]
    w = np.linspace(0,1,n); y[:n] = y[:n]*np.sqrt(w) + tail*np.sqrt(1-w); return y
def save(x, name, target):
    x = x/rms(x)*10**(target/20); pk = np.abs(x).max()
    if pk > .5: x *= .5/pk
    subprocess.run(['ffmpeg','-v','0','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','libmp3lame','-b:a','160k',os.path.join(OUT,name)], input=x.astype(np.float32).tobytes())
    print(name, round(len(x)/SR,1), 's')
L = 64*SR; LL = 70*SR
talk = [load(n) for n in ['3542','3376','0624']]
# ── hotel lobby: low talk, a cup and saucer, a newspaper, feet crossing a parquet floor
h = 1.0*lp(hp(grains([lp(t,1500) for t in talk], LL, 3), 140), 1500)
cups = [load('1196'), load('1192'), load('1193')]
scatter(h, cups, 5.0, 0.18, dur=1.2, lpf=4000)
scatter(h, load('1250'), 11.0, 0.10, dur=1.5, lpf=3500)
scatter(h, [load('0376')], 9.0, 0.14, dur=3.0, lpf=3000)
h = room(h, 0.35, [(11,.3),(23,.22),(41,.15),(67,.1)], 0.35)
save(loopify(h, L), 'hotel-lobby.mp3', -30)
# ── a London terminus, 1893: the crowd under a glass roof, steam breathing, a far engine, feet on stone
crowd = [lp(load('3515'),1200), lp(load('2969'),1200)] + [lp(t,1100) for t in talk]
st = 1.0*grains(crowd, LL, 4)
hiss = [load('0227'), load('0228'), load('3011')]
scatter(st, hiss, 6.0, 0.5, lpf=5000)
eng = lp(load('3018'), 900); n = len(eng)
seg = np.concatenate([eng]*2)[:LL]; st += 0.35*seg/ (np.abs(seg).max()+1e-9) * (rms(st)/rms(seg)*.6/0.35)
scatter(st, [load('1318'), load('0514')], 7.0, 0.22, dur=3.0, lpf=3500)
st = room(hp(st, 60), 1.6, [(35,.3),(80,.25),(140,.2),(230,.15)], 0.6)
save(loopify(st, L), 'station.mp3', -28)
# ── a gunsmith's shop: a quiet room, boards underfoot, the street muffled through the window
street = lp(np.concatenate([load('0610'), load('1316'), load('0611')]*4)[:LL], 700)
sh = 0.5*street/rms(street)
sh += 0.25*lp(grains([lp(load('2969'),900)], LL, 2), 900)/1.0
scatter(sh, [load('0165')], 10.0, 0.25, dur=2.0, lpf=3000)
sh += R.standard_normal(LL)*0.02
sh = room(sh, 0.25, [(7,.35),(15,.25),(29,.15)], 0.3)
save(loopify(sh, L), 'gunshop.mp3', -33)
# ── one-shots
def one(x, name, target, peak=.7):
    x = x/ (np.abs(x).max()+1e-9)*peak
    save(x, name, target)
b = load('2530'); o = np.argmax(np.abs(b) > .2*np.abs(b).max()); bell = b[o:o+int(2.2*SR)]*np.linspace(1,0,int(2.2*SR))**.5
one(room(hp(bell,300), 0.6, [(11,.3),(23,.22),(41,.15)], .3), 'hotel-desk-bell.mp3', -24)
# the train comes in: a far whistle under the roof, the engine easing to a stop, steam let off
w = load('0226'); stop = load('3015'); hs = load('0228')
T = int(12*SR); x = np.zeros(T)
x[:len(w)] += 0.6*lp(w, 4000)/np.abs(w).max()
p = int(2.0*SR); x[p:p+len(stop)] += 0.9*lp(stop, 3000)[:T-p]/np.abs(stop).max()
p = int(6.5*SR); x[p:p+len(hs)] += 0.7*hs[:T-p]/np.abs(hs).max()
x *= np.minimum(1, np.linspace(12, 0, T)/2)
one(room(x, 1.6, [(35,.3),(80,.25),(140,.2)], .55), 'train-arrives.mp3', -22)
w2 = load('3316'); one(room(lp(w2,3500), 2.0, [(60,.3),(150,.2)], .6), 'train-whistle-far.mp3', -26, .5)
# a Winchester's lever worked, once
g = np.concatenate([load('1988'), np.zeros(int(.25*SR)), load('1987')])
one(room(g, 0.25, [(7,.35),(15,.25)], .25), 'rifle-action.mp3', -22)
