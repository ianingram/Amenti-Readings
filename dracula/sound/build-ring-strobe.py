import numpy as np, subprocess
from scipy.ndimage import uniform_filter1d, maximum_filter1d, minimum_filter1d
from scipy.signal import butter, sosfilt
SR=44100; S='/tmp/claude-0/wf/'
def load(p,ch=1,af=None):
  cmd=['ffmpeg','-v','error','-i',p]+(['-af',af] if af else [])+['-ac',str(ch),'-ar',str(SR),'-f','f32le','-']
  a=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32)
  return a.reshape(-1,ch).copy() if ch>1 else a.copy()
def events(a,minlen=0.12,maxlen=1.6):
  e=uniform_filter1d(np.abs(a),int(0.02*SR)); th=e.max()*0.18
  on=e>th; out=[]; i=0; n=len(a)
  while i<n:
    if on[i]:
      j=i
      while j<n and (on[j] or (j+int(0.06*SR)<n and on[j:j+int(0.06*SR)].any())): j+=1
      s=max(0,i-int(0.02*SR)); t=min(n,j+int(0.08*SR))
      if minlen*SR<t-s<maxlen*SR: out.append(a[s:t])
      i=j
    i+=1
  return out
rng=np.random.default_rng(7)
barks=[]
for n,af in [('2954','asetrate=44100*0.78,aresample=44100'),('2955','asetrate=44100*0.78,aresample=44100'),('0868','asetrate=44100*0.8,aresample=44100'),('2353','asetrate=44100*0.82,aresample=44100'),('1544','asetrate=44100*0.85,aresample=44100'),('1545','asetrate=44100*0.85,aresample=44100')]:
  barks+=events(load(S+'src/'+n+'.mp3',1,af))
growls=events(load(S+'src/1060.mp3',1,'asetrate=44100*0.55,aresample=44100,lowpass=f=2500'),0.2,2.5)
neighs=[load(S+'src/'+n+'.mp3',1,'asetrate=44100*1.06,aresample=44100,highpass=f=300') for n in ['0284','0460','0863','1541','1542']]
print(len(barks),len(growls))
mix=load(S+'v3.mp3',2); D=len(mix)/SR
fx=np.zeros(len(mix),np.float32)
def put(sig,t,g):
  sig=sig*np.hanning(len(sig))**0.15
  i=int(t*SR); n=min(len(sig),len(fx)-i)
  if n>0: fx[i:i+n]+=sig[:n]/(np.abs(sig).max()+1e-9)*g
A,B=7.8,23.6
# barks & snarls: sparse at first (the animation), a storm under the strobe, thinning at the end
t=A
while t<B:
  dens=0.35 if t<12.8 else 0.16
  if t>B-2.5: dens=0.45
  put(barks[rng.integers(len(barks))],t,rng.uniform(0.25,0.5))
  if rng.random()<0.35: put(growls[rng.integers(len(growls))],t+rng.uniform(0,0.3),rng.uniform(0.25,0.4))
  t+=dens*rng.uniform(0.6,1.5)
# horse screams
for t,k in [(8.2,0),(11.0,2),(13.0,1),(15.6,3),(17.9,2),(20.4,4),(22.6,0)]:
  put(neighs[k],t,0.55)
# a short reverb to put it in the night air
ir=np.zeros(int(0.9*SR),np.float32)
for d,g in [(0.05,0.5),(0.11,0.35),(0.19,0.25),(0.31,0.16),(0.47,0.1),(0.7,0.06)]: ir[int(d*SR)]=g
from scipy.signal import fftconvolve
fx=fx+fftconvolve(fx,ir)[:len(fx)]
# fade in/out of the layer
env=np.ones(len(fx)); a,b=int(A*SR),int(B*SR)
env[:a]=0; env[b+int(1.5*SR):]=0
env[a:a+int(0.4*SR)]=np.linspace(0,1,int(0.4*SR)); env[b:b+int(1.5*SR)]=np.linspace(1,0,int(1.5*SR))
fx*=env
# duck under the voice: voice band energy of the existing mix
sos=butter(4,[300,3400],btype='band',fs=SR,output='sos')
vb=uniform_filter1d(np.abs(sosfilt(sos,mix.mean(1))),int(0.08*SR))
vth=np.percentile(vb[a:b],60)
speak=uniform_filter1d((vb>vth).astype(np.float32),int(0.15*SR))
ref=np.sqrt(np.mean(mix[a:b]**2))
fx=fx/ (np.sqrt(np.mean(fx[a:b]**2))+1e-9)*ref*0.9
fx*=(1-0.45*speak)
out=mix+fx[:,None]
g=np.minimum(1,0.97/np.maximum(np.abs(out).max(1),1e-9)); g=uniform_filter1d(minimum_filter1d(g,int(0.01*SR)),int(0.005*SR)); out*=g[:,None]
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','libmp3lame','-b:a','160k',S+'drac1-wolves-52-v4.mp3'],stdin=subprocess.PIPE)
p.stdin.write(out.astype(np.float32).tobytes()); p.stdin.close(); p.wait()
subprocess.run(['ffmpeg','-v','error','-y','-ss','4','-t','24','-i',S+'drac1-wolves-52-v4.mp3','-c:a','libmp3lame','-b:a','160k',S+'preview-wolves.mp3'])
print('ok', D)
