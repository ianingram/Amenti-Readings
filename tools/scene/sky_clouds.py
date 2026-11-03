import numpy as np, subprocess, sys
from PIL import Image
from scipy.ndimage import gaussian_filter, minimum_filter1d
rng=np.random.default_rng(7)
im=np.asarray(Image.open('/home/claude/ar/dracula/art/ch01-n09-1.jpg')).astype(np.float32)/255
H,W,_=im.shape; L=gaussian_filter(im.mean(2),1.5)
depth=np.zeros(W,int)
for x in range(W):
  y=0
  while y<H and L[y,x]>0.20: y+=1
  depth[x]=y
depth=minimum_filter1d(depth,7)
depth=np.minimum(depth,np.where(np.arange(W)>1140,660,600))
yy=np.arange(H)[:,None]
m=(yy<depth[None,:]).astype(np.float32); m=gaussian_filter(m,1.5)
def fbm(h,w,sx,sy,oct=4):
  out=np.zeros((h,w),np.float32); a=1
  for o in range(oct):
    n=gaussian_filter(rng.standard_normal((h,w)).astype(np.float32),(sy/2**o,sx/2**o),mode='wrap')
    out+=a*n/n.std(); a*=0.5
  return (out-out.min())/(out.max()-out.min())
TW=W*3
hi=fbm(H,TW,90,10)          # streaky high cloud
lo=fbm(H,TW,60,18)          # rolling low cloud
def ss(x,a,b): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
# moon glow
mx,my,mr=930,232,115
d=np.sqrt((np.arange(W)[None,:]-mx)**2+(yy-my)**2)
glow=np.exp(-np.maximum(d-mr,0)/180)
hiband=ss(yy,0,60)*(1-ss(yy,420,560))
loband=ss(yy,380,470)*(1-ss(yy,700,780))
FPS,T=24,14; N=FPS*T
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
 '-vf','tpad=stop_mode=clone:stop_duration=6,format=yuv420p','-c:v','libx264','-crf','20','-preset','slow','-movflags','+faststart',sys.argv[1]],stdin=subprocess.PIPE)
base=im.copy()
for f in range(N):
  t=f/FPS
  oh=int(t*22)%TW; ol=int(-t*38)%TW
  h=np.roll(hi,-oh,axis=1)[:,:W]; l=np.roll(lo,-ol,axis=1)[:,:W]
  ah=ss(h,0.52,0.78)*0.6*hiband
  al=ss(l,0.45,0.75)*0.75*loband
  ch=np.stack([0.50,0.58,0.68])[None,None,:]*(0.55+0.9*glow[...,None])
  cl=np.stack([0.30,0.36,0.44])[None,None,:]*(0.7+0.5*glow[...,None])
  o=base*(1-ah[...,None]*m[...,None])+np.clip(ch,0,1)*ah[...,None]*m[...,None]
  o=o*(1-al[...,None]*m[...,None])+cl*al[...,None]*m[...,None]
  # faint mist in front of the right-hand rocks, clear of the carriage
  fm=al*0.22*ss(np.arange(W)[None,:],820,980)*(ss(yy,520,580)*(1-ss(yy,700,760)))
  o=o*(1-fm[...,None])+cl*fm[...,None]
  ff.stdin.write((np.clip(o,0,1)*255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
