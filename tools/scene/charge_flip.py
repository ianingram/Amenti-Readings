import numpy as np, subprocess, glob, math
from PIL import Image
fs=sorted(glob.glob('/tmp/claude-0/t2/z/*.png')); W,H=1456,816
ims=[Image.open(f).convert('RGB').crop((0,190,1024,766)).resize((W,H),Image.LANCZOS) for f in fs]
FPS=24; T=5.0; N=int(FPS*T); rng=np.random.default_rng(4)
order=[0,1,2,3,2,1]
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-vf','tpad=stop_mode=clone:stop_duration=6,format=yuv420p','-c:v','libx264','-crf','19','-preset','slow','-movflags','+faststart','/tmp/claude-0/t2/ch01-tn-charge.mp4'],stdin=subprocess.PIPE)
k=0;hold=0;cur=0
for f in range(N):
  t=f/FPS
  if hold<=0: cur=order[k%6]; k+=1; hold=int(rng.integers(2,4)); jolt=1
  hold-=1
  p=t/T; z=1.04+0.36*p*p
  cx=W/2+rng.normal(0,4)*jolt; cy=H*0.56+rng.normal(0,4)*jolt+4*math.sin(t*13)
  jolt*=0.5
  cw,ch=W/z,H/z
  fr=ims[cur].crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((W,H),Image.BICUBIC)
  ff.stdin.write(np.asarray(fr).tobytes())
ff.stdin.close(); ff.wait()
