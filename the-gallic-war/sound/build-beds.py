"""The Gallic War: the legion on the march (march-column.mp3), built from real CC0 recordings (BigSoundBank):
#1117, #3202, #3216 footsteps on gravel and #0839 feet on pebbles layered thirty-two deep at random offsets and
slight pitch changes into a column of men on a road; #0610/#0611 hooves at a walk for the officers; #0659 wind.
Seamless 60 s loop."""
import subprocess, numpy as np, random
SR=44100; L=60*SR; random.seed(7)
def load(f, rate=1.0):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-af',f'asetrate={int(SR*rate)},aresample={SR}','-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).copy()
def lp(x,fc):
    import scipy.signal as sg; b,a=sg.butter(2,fc/(SR/2)); return sg.lfilter(b,a,x).astype(np.float32)
out=np.zeros(L+8*SR,np.float32)
feet=['src/1117.mp3','src/3202.mp3','src/3216.mp3','src/0839.mp3']
for i in range(32):
    x=load(random.choice(feet),random.uniform(0.9,1.08)); s=random.randint(0,max(0,len(x)-20*SR)); seg=x[s:s+random.randint(14,22)*SR]
    seg=lp(seg,random.uniform(1800,4200))*random.uniform(0.25,0.7)
    t=random.randint(0,L); n=min(len(seg),len(out)-t); env=np.ones(n,np.float32); k=min(n//4,SR); env[:k]=np.linspace(0,1,k); env[-k:]=np.linspace(1,0,k)
    out[t:t+n]+=seg[:n]*env
    if t+len(seg)>L: r=t+len(seg)-L; out[:min(r,L)]+=seg[len(seg)-r:][:L]*0  # wrap handled by crossfade below
for i in range(6):
    x=lp(load(random.choice(['src/0610.mp3','src/0611.mp3']),random.uniform(0.95,1.03)),2500)*0.45; t=random.randint(0,L-len(x)); out[t:t+len(x)]+=x
w=lp(load('src/0659.mp3'),900); out[:L]+=np.resize(w,L)*0.35
# seamless: crossfade the tail beyond L into the head
X=4*SR; tail=out[L:L+X]; out=out[:L].copy(); out[:X]=out[:X]*np.linspace(0,1,X)+tail*np.linspace(1,0,X)
out=out/np.sqrt((out**2).mean())*10**(-26/20); out=np.clip(out,-0.95,0.95)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ac','1','-ar',str(SR),'-i','-','-ac','2','-b:a','128k','/home/claude/ar/the-gallic-war/sound/march-column.mp3'],input=out.tobytes(),check=True)
print('ok')
