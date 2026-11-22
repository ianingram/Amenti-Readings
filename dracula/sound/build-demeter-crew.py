import subprocess, numpy as np, sys
from scipy.signal import butter, sosfilt
SR=48000; S='/home/claude/demeter/src/'
def load(n):
    r=subprocess.run(['ffmpeg','-v','0','-i',S+n+'.mp3','-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(r,np.float32).copy()
def onset(x):
    e=np.abs(x); t=0.2*e.max(); return int(np.argmax(e>t))
def lp(x,f,o=4): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def save(x,name,target):
    x=x/np.sqrt(np.mean(x[np.abs(x)>1e-4]**2))*10**(target/20)
    pk=np.abs(x).max()
    if pk>0.7: x=x*0.7/pk
    subprocess.run(['ffmpeg','-v','0','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','libmp3lame','-b:a','128k',name],input=x.astype(np.float32).tobytes())
    print(name, round(len(x)/SR,2),'s')
# --- blow: crack + thump, then a body against wood 0.28 s later
crack=load('2463'); thump=load('0105'); fall=load('2455')
def seg(x,dur):
    o=onset(x); y=x[max(0,o-240):o+int(dur*SR)]
    f=np.ones(len(y)); n=int(0.05*SR); f[-n:]=np.linspace(1,0,n); return y*f
c=seg(crack,0.35); t=seg(thump,0.5); b=seg(fall,1.2)
out=np.zeros(int(2.2*SR))
out[:len(c)]+=0.6*hp(c,300)/np.abs(c).max()
out[:len(t)]+=1.0*lp(t,2500)/np.abs(t).max()
d=int(0.28*SR); out[d:d+len(b)]+=0.7*lp(b,3000)/np.abs(b).max()
# small room
ir=np.zeros(int(0.5*SR)); rng=np.random.default_rng(7)
for ms,g in [(9,.35),(17,.28),(31,.2),(46,.14)]: ir[int(ms*SR/1000)]=g
ir[0]=1; tail=rng.standard_normal(len(ir))*np.exp(-np.arange(len(ir))/(0.09*SR))*0.05; ir+=tail
out=np.convolve(out,ir)[:len(out)]
save(out,'demeter-blow.mp3',-20)
# --- crew murmur: shuffled grains of outdoor talk + whispers, low-passed, no words survive
rng=np.random.default_rng(26)
pool=[hp(lp(load(n),1300),150) for n in ['2968','2969','2970','2966']]
wh=[hp(lp(load(n),2200),300) for n in ['3255','3256']]
L=int(14*SR); bed=np.zeros(L)
for layer in range(3):
    pos=int(rng.uniform(0,0.4)*SR)
    while pos<L:
        src=pool[rng.integers(len(pool))]; g=rng.uniform(.6,1.8); n=int(g*SR)
        st=rng.integers(0,len(src)-n); y=src[st:st+n].copy()
        if np.sqrt(np.mean(y**2))<1e-3: continue
        y/=np.sqrt(np.mean(y**2)); w=np.hanning(n); y*=w
        end=min(L,pos+n); bed[pos:end]+=y[:end-pos]*rng.uniform(.5,1)
        pos+=int(n*rng.uniform(.45,.7))
for k in range(5):
    src=wh[rng.integers(2)]; n=int(rng.uniform(.6,1.2)*SR); st=rng.integers(0,len(src)-n)
    y=src[st:st+n]; y=y/(np.sqrt(np.mean(y**2))+1e-9)*np.hanning(n)*0.35
    p=int(rng.uniform(1,12)*SR); bed[p:p+n]+=y[:L-p]
# ebb and flow: swell, settle, fade out
t=np.arange(L)/SR
env=np.clip(t/2.5,0,1)*np.clip((14-t)/3,0,1)*(0.75+0.25*np.sin(2*np.pi*t/5.5))
save(bed*env,'demeter-crew-murmur.mp3',-30)
