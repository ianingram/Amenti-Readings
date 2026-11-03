import numpy as np, subprocess, glob, math
from PIL import Image
fs=sorted(glob.glob('z/*.png'))
W,H=1456,816
ims=[np.asarray(Image.open(f).convert('RGB')).astype(np.float32) for f in fs]
order=[0,1,2,3,2,1]
FPS=24; T=14; N=FPS*T
def sm(x): x=min(1,max(0,x)); return x*x*(3-2*x)
keys=[(0,0),(2.6,0),(3.4,1),(6.2,1),(7.2,0),(9.4,0),(9.9,1),(12.6,1),(13.4,0),(14,0)]
def speed(t):
  for (a,va),(b,vb) in zip(keys,keys[1:]):
    if a<=t<=b: return va+(vb-va)*sm((t-a)/(b-a))
  return 0
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-vf','tpad=stop_mode=clone:stop_duration=6,format=yuv420p','-c:v','libx264','-crf','19','-preset','slow','-movflags','+faststart','ch01-r-flip-cam.mp4'],stdin=subprocess.PIPE)
phi=0.0; swayph=0.0; bumpph=0.0; last=-1; jolt=0; punch=0
for f in range(N):
  t=f/FPS; s=speed(t); p=t/T
  rate=0.62+s*(5.5-0.62); phi+=rate/FPS
  k=int(phi); fr=phi-k; sharp=1+s*14
  w=sm((fr-0.5)*sharp+0.5) if s<0.98 else (1.0 if fr>0.5 else 0.0)
  img=ims[order[k%6]]*(1-w)+ims[order[(k+1)%6]]*w
  cur=order[(k+(1 if w>0.5 else 0))%6]
  if cur!=last and s>0.5: jolt=1.0*s
  last=cur
  swayph+=(1/3.2+s*(1/1.3-1/3.2))/FPS; bumpph+=(1/1.6+s*(1/0.62-1/1.6))/FPS
  ang=1.5*math.sin(2*math.pi*swayph)+0.6*jolt*(1 if f%2 else -1)
  # camera: a slow push in, tracking from the coach to the horses; it punches in on the fast bursts
  punch+= (s-punch)*0.12
  z=1.14+0.26*sm(p)+0.10*punch
  cx=W*(0.44+0.20*sm(p)) ; cy=H*(0.55+0.03*sm(p))
  cx+=3.5*math.sin(2*math.pi*t/2.4); cy+=6.5*math.sin(2*math.pi*bumpph)+5*jolt
  jolt*=0.55
  im=Image.fromarray(img.astype(np.uint8)).rotate(ang,resample=Image.BICUBIC,center=(cx,cy))
  cw,ch=W/z,H/z; m=0.045
  cx=min(max(cx,cw/2+W*m),W-cw/2-W*m); cy=min(max(cy,ch/2+H*m),H-ch/2-H*m)
  fr_=im.crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((W,H),Image.LANCZOS)
  ff.stdin.write(np.asarray(fr_).tobytes())
ff.stdin.close(); ff.wait()
