import numpy as np, subprocess, glob, math
from scipy.ndimage import gaussian_filter
W,H=1456,816; FPS=24
vs=sorted(glob.glob('/tmp/claude-0/cc/z/*.mp4'))
def frames(v,speed,maxt):
  p=subprocess.run(['ffmpeg','-v','error','-i',v,'-vf',f'setpts={1/speed}*PTS,fps={FPS},scale={W}:{H}:flags=lanczos','-t',str(maxt),'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
  return np.frombuffer(p,np.uint8).reshape(-1,H,W,3)
A=frames(vs[3],0.8,6.5); B=frames(vs[0],0.8,4.0)
xf=12
seq=list(A[:-xf])+[ (A[-xf+i].astype(np.float32)*(1-i/xf)+B[i].astype(np.float32)*(i/xf)).astype(np.uint8) for i in range(xf)]+list(B[xf:])
rng=np.random.default_rng(3)
def noise(h,w,s): 
  n=gaussian_filter(rng.standard_normal((h,w)).astype(np.float32),s,mode='wrap'); return (n-n.min())/(n.max()-n.min())
TW=W*3
YY,XX=np.mgrid[0:H,0:W]
fogA=noise(H//4,TW//4,(10,30)); fogA=np.kron(fogA,np.ones((4,4)))[:H,:TW]
fogB=noise(H//4,TW//4,(6,14)); fogB=np.kron(fogB,np.ones((4,4)))[:H,:TW]
yy=np.arange(H)[:,None]
fogC=noise(H//4,TW//4,(5,9)); fogC=np.kron(fogC,np.ones((4,4)))[:H,:TW]
ground=np.clip((yy-H*0.45)/(H*0.4),0,1)
# streaks: thin horizontal white trails
N_S=26
sx=rng.uniform(0,W,N_S); sy=rng.uniform(H*0.1,H*0.95,N_S); sl=rng.uniform(260,720,N_S); sv=rng.uniform(900,2200,N_S); sa=rng.uniform(0.10,0.30,N_S); sw=rng.uniform(0.6,2.0,N_S)
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-vf','tpad=stop_mode=clone:stop_duration=8,format=yuv420p','-c:v','libx264','-crf','19','-preset','slow','-movflags','+faststart','/tmp/claude-0/cc/ch01-r-crazy-0.mp4'],stdin=subprocess.PIPE)
mist=np.array([0.80,0.84,0.95])
for f,fr in enumerate(seq):
  t=f/FPS
  o=fr.astype(np.float32)/255
  # cool it toward dusk to match the Pass
  o=o**1.12*np.array([0.88,0.92,1.06])
  fa=np.roll(fogA,int(-t*520)%TW,axis=1)[:,:W]; fb=np.roll(fogB,int(-t*980)%TW,axis=1)[:,:W]
  fog=np.clip((fa-0.45)*2.2,0,1)*0.55*(0.35+0.65*ground) + np.clip((fb-0.5)*2.5,0,1)*0.5*ground
  o=o*(1-fog[...,None])+mist*fog[...,None]
  # swirling vapor: a third soft layer whose sampling is warped by a slowly turning field
  ph=t*0.9
  dx=(np.sin(YY/70+ph)*38+np.cos(XX/110-ph*1.3)*30).astype(np.int32)
  dy=(np.cos(XX/90+ph*0.8)*22+np.sin(YY/60-ph)*16).astype(np.int32)
  xs=(XX+dx+int(t*700))%TW; ys=np.clip(YY+dy,0,H-1)
  sw=fogC[ys,xs]
  vap=np.clip((sw-0.5)*2.6,0,1)*0.5*(0.3+0.7*ground)
  o=o*(1-vap[...,None])+mist*vap[...,None]
  ff.stdin.write((np.clip(o,0,1)*255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
print(len(seq)/FPS)
