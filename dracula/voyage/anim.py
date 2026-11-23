import sys, subprocess, math
from PIL import Image
import map as M
SHIP_C=(140,30,25); TRAIN_C=(30,40,70)
B=Image.open('/home/claude/vm/base_lab.png') if False else None
def ease(t): return 0.5-0.5*math.cos(math.pi*max(0,min(1,t)))
def render(out, dur, ship_kf, train_kf, box0, box1, stamps, fps=24):
    """ship_kf/train_kf: list of (t, frac). box: (cx,cy,w) in 2912 coords. stamps: (kind,place_lonlat,text,sub,dx,dy)"""
    base=M.base(); M.labels(base)
    sf={s[2]:M.frac_at(M.SHIP_D if s[0]=='ship' else M.TRAIN_D, s[1]) for s in stamps}
    def interp(kf,t):
        for (t0,f0),(t1,f1) in zip(kf,kf[1:]):
            if t<=t1: return f0+(f1-f0)*ease((t-t0)/max(1e-6,t1-t0))
        return kf[-1][1]
    p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1456x816','-r',str(fps),'-i','-',
        '-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',out],stdin=subprocess.PIPE)
    N=int(dur*fps)
    for i in range(N):
        t=i/fps; im=base.copy()
        tf=interp(train_kf,t); shf=interp(ship_kf,t)
        if tf>0.002: M.draw_route(im,M.TRAIN_D,tf,TRAIN_C,dash=(26,14),width=6)
        if shf>0.002:
            hx,hy=M.draw_route(im,M.SHIP_D,shf,SHIP_C,width=8)
        for kind,ll,txt,sub,dx,dy in stamps:
            f=tf if kind=='train' else shf
            if f>0.002 and f>=sf[txt]-0.004:
                x,y=M.proj(*ll); M.stamp(im,x+dx,y+dy,txt,sub,SHIP_C if kind=='ship' else TRAIN_C)
        if shf>0.002: M.ship_icon(im,hx,hy-6,1.1)
        e=ease(t/dur)
        cx=box0[0]+(box1[0]-box0[0])*e; cy=box0[1]+(box1[1]-box0[1])*e; w=box0[2]+(box1[2]-box0[2])*e; h=w*816/1456
        cx=min(max(cx,w/2),M.W-w/2); cy=min(max(cy,h/2),M.H-h/2)
        fr=im.crop((int(cx-w/2),int(cy-h/2),int(cx+w/2),int(cy+h/2))).resize((1456,816),Image.LANCZOS)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
