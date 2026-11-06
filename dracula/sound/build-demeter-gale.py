"""The Demeter's gale bed (Book II ch VII, the log's storm days): howling wind over heavy sea and
breaking waves, built from the folder's wind.mp3, sea.mp3 and storm-4.wav. 60 s, seamless loop.
Run from dracula/sound: python3 build-demeter-gale.py"""
import numpy as np,subprocess
SR=44100; D=60
def load(f,af=''):
  cmd=['ffmpeg','-v','error','-i',f]+(['-af',af] if af else [])+['-ac','2','-ar',str(SR),'-f','f32le','-']
  a=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).reshape(-1,2).copy()
  n=SR*(D+4); return np.resize(a,(n,2))
def rms(x): return np.sqrt(np.mean(x**2))+1e-9
wind=load('wind.mp3','highpass=f=180,equalizer=f=900:t=q:w=1:g=4')
howl=load('wind.mp3','asetrate=44100*0.82,aresample=44100,bandpass=f=600:width_type=q:w=1.2')
sea=load('sea.mp3','asetrate=44100*0.85,aresample=44100,lowshelf=f=160:g=6')
crash=load('storm-4.wav','lowshelf=f=120:g=4')
t=np.arange(len(wind))/SR
gust=(0.75+0.25*np.sin(2*np.pi*t/7.3)+0.12*np.sin(2*np.pi*t/2.9))[:,None]
mix=wind/rms(wind)*0.9*gust + np.roll(howl,SR*11,0)/rms(howl)*0.45*(0.6+0.4*np.sin(2*np.pi*t/11)[:,None]) + sea/rms(sea)*0.8 + crash/rms(crash)*0.6
n=SR*D; f=SR*4
loop=mix[:n].copy(); w=np.linspace(0,1,f)[:,None]
loop[:f]=loop[:f]*w+mix[n:n+f]*(1-w)
loop=loop/np.abs(loop).max()*0.9
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','libmp3lame','-b:a','160k','demeter-gale.mp3'],stdin=subprocess.PIPE)
p.stdin.write(loop.astype(np.float32).tobytes()); p.stdin.close(); p.wait()
