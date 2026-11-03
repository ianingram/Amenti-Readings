import numpy as np, subprocess, math
from PIL import Image
from scipy.ndimage import gaussian_filter
im=np.asarray(Image.open('s4.png').convert('RGB')).astype(np.float32)/255
H,W,_=im.shape; yy,xx=np.mgrid[0:H,0:W]
eyes=[(945,114),(957,114)]
core=np.zeros((H,W),np.float32)
for x,y in eyes: core+=np.exp(-((xx-x)**2+(yy-y)**2)/(2*0.9**2))
glow=gaussian_filter(core,4)*8; halo=gaussian_filter(core,12)*30
def sm(x): x=min(1,max(0,x)); return x*x*(3-2*x)
FPS=24;T=16;N=FPS*T
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-vf','tpad=stop_mode=clone:stop_duration=6,format=yuv420p','-c:v','libx264','-crf','18','-preset','slow','-movflags','+faststart','ch01-n10-eyes.mp4'],stdin=subprocess.PIPE)
for f in range(N):
  t=f/FPS
  k=sm((t-8.0)/0.9)*(0.85+0.15*math.sin(t*7))
  o=im+ (core[...,None]*np.array([1,0.25,0.15])*1.6 + glow[...,None]*np.array([1,0.1,0.05]) + halo[...,None]*np.array([0.5,0.03,0.02]))*k
  o=np.clip(o,0,1)
  z=1.0+1.4*sm(t/T)                           # a slow push in to the driver
  cx=W/2+(951-W/2)*sm(t/T*1.1); cy=H/2+(150-H/2)*sm(t/T*1.1)
  cw,ch=W/z,H/z; cx=min(max(cx,cw/2),W-cw/2); cy=min(max(cy,ch/2),H-ch/2)
  fr=Image.fromarray((o*255).astype(np.uint8)).crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((W,H),Image.LANCZOS)
  ff.stdin.write(np.asarray(fr).tobytes())
ff.stdin.close(); ff.wait()
