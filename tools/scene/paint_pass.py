"""Turn a photographic still toward Book II's painted look: oil-paint brush clustering, softened edges,
warm amber grade and a gentle vignette. Writes <name>-p.jpg beside the original.
Run: python3 tools/scene/paint_pass.py dracula/art/<file>.jpg [...]"""
import cv2,numpy as np,sys,os
for src in sys.argv[1:]:
  im=cv2.imread(src)
  oil=cv2.xphoto.oilPainting(im,5,1)
  soft=cv2.bilateralFilter(im,9,45,9)
  x=cv2.addWeighted(oil,0.7,soft,0.3,0).astype(np.float32)/255
  dark=x.mean()<0.3
  x=x**(1.0 if dark else 1.1); x[...,2]*=1.07; x[...,1]*=0.99; x[...,0]*=0.84          # amber
  H,W=x.shape[:2]; yy,xx=np.mgrid[0:H,0:W]
  v=1-(0.15 if dark else 0.35)*(((xx-W/2)/(W/2))**2*0.6+((yy-H/2)/(H/2))**2)
  x*=np.clip(v,0.55,1)[...,None]
  out=os.path.splitext(src)[0]+'-p.jpg'
  cv2.imwrite(out,np.clip(x*255,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,80]); print(out)
