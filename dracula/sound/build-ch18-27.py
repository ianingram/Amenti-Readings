#!/usr/bin/env python3
"""Dracula XVIII–XXVII — new sounds. Real recordings only (BigSoundBank, CC0 site-wide), cut,
filtered and placed; no synthesized effects. Deterministic (seed 1897).
  pistol-shot   #0438 .357 Magnum, one shot, heard from inside a room (low-pass, room slap)
  winchester    #0397 Winchester Magnum XTR, one shot, open air (long tail, wind-dulled)
  rats          #0459 'Mouse screams' — squeaks scattered by the hundred, pitched, rising
  terriers      #0682 small dog growling/barking, then #2953 a pack howling ('began to howl')
  whistle       #1017 one short blow, high and thin, at a distance
  coins         #0193 thirteen coins falling on a floor — the first cluster
  sear          #0145 frying pan — the first hiss, a hot iron on flesh
  chapel (bed)  #2135 'Cave #1' — still air under stone, low-passed, seamless 60 s loop
  river (bed)   #3137 'Watercourse 5.2' — far, low-passed, under a launch on the Sereth
  port (bed)    #2571 'Small fishing port #1' — Varna and Galatz harbour
  horse-walk    #1854 'Horse walking on a path' — Bloxam's cart horse (for Ian's approval)"""
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wv, subprocess, os, sys
SR=48000; S='/tmp/bsb/src/'; OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/snd18/out/'; os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(1897)
def load(k): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',S+k+'.mp3','-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout,np.float32).copy()
def lp(x,f): return sg.sosfilt(sg.butter(2,f,'low',fs=SR,output='sos'),x).astype(np.float32)
def hp(x,f): return sg.sosfilt(sg.butter(2,f,'high',fs=SR,output='sos'),x).astype(np.float32)
def put(b,x,t,g=1.0):
  i=int(t*SR)
  if 0<=i<len(b): n=min(len(x),len(b)-i); b[i:i+n]+=x[:n]*g
def reverb(x,rt,wet,seed=1,bright=4000):
  r=np.random.default_rng(seed); n=int(rt*SR); tt=np.arange(n)/SR
  ir=lp(r.standard_normal(n)*np.exp(-6.91*tt/rt),bright); ir/=np.sqrt(np.sum(ir**2))
  y=np.concatenate([x,np.zeros(n,np.float32)]); return ((1-wet)*y+wet*sg.fftconvolve(y,ir)[:len(y)]).astype(np.float32)
def fade(x,a=0.01,b=0.3):
  x=x.copy(); ia,ib=int(a*SR),int(b*SR)
  if ia: x[:ia]*=np.linspace(0,1,ia)
  if ib: x[-ib:]*=np.linspace(1,0,ib)
  return x
def trimsil(x,th=0.003):
  e=np.abs(x)>th; i=np.argmax(e); j=len(x)-np.argmax(e[::-1]); return x[max(0,i-int(.005*SR)):j]
def peak(x,db): return x*(10**(db/20)/(np.abs(x).max()+1e-12))
def rms(x,db): return x*(10**(db/20)/(np.sqrt(np.mean(x**2))+1e-12))
def fold(x,xf=3.0):
  k=int(xf*SR); b=x[:-k].copy(); a=np.linspace(0,np.pi/2,k); b[:k]=b[:k]*np.sin(a)+x[-k:]*np.cos(a); return b
def mp3(x,name):
  x=np.clip(x,-0.98,0.98); tmp=OUT+name+'.wav'; wv.write(tmp,SR,(x*32767).astype(np.int16))
  subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-ac','1','-c:a','libmp3lame','-b:a','160k',OUT+name],check=True); os.remove(tmp)
  print(f'{name:22s} {len(x)/SR:6.2f}s')
def onsets(x,th_db=-30,gap=0.08):
  env=np.sqrt(np.convolve(x**2,np.ones(int(.01*SR))/int(.01*SR),'same')); th=10**(th_db/20)*env.max(); on=[];last=-1
  for i in range(0,len(env),int(.005*SR)):
    if env[i]>th and (last<0 or (i-last)/SR>gap) and (i==0 or env[max(0,i-int(.02*SR))]<th): on.append(i); last=i
  return on
# pistol shot through a window, heard in the study
x=trimsil(load('0438')); x=lp(x[:int(1.6*SR)],5500); y=reverb(fade(x,0,0.4),1.1,0.35,seed=2,bright=3500)
mp3(peak(fade(y,0,0.5),-4),'pistol-shot.mp3')
# winchester in the open snow
x=trimsil(load('0397')); x=lp(x[:int(2.6*SR)],6000); y=reverb(fade(x,0,0.6),2.6,0.3,seed=3,bright=3000)
mp3(peak(fade(y,0,0.8),-4),'winchester.mp3')
# rats: squeaks scattered, a few at first, then hundreds
src=load('0459'); on=onsets(src,-26,0.06); grains=[]
for o in on:
  g=src[o:o+int(0.25*SR)]; g=trimsil(g,0.01)
  if 0.03*SR<len(g)<0.35*SR: grains.append(fade(g,0.003,0.03))
L=9.0; n=int(L*SR); b=np.zeros(n,np.float32); t=0.2
while t<L-0.4:
  dens=4+60*(t/L)**1.6; g=grains[rng.integers(len(grains))]; semis=rng.uniform(-3,5)
  g2=sg.resample_poly(g,100,int(round(100*2**(semis/12)))).astype(np.float32)
  put(b,g2,t,rng.uniform(0.15,0.6)*(0.4+0.6*rng.random())); t+=rng.exponential(1/dens)
scr=hp(rng.standard_normal(n).astype(np.float32),2500)*np.clip(np.linspace(0,1,n),0,1)**2*0.02   # claws on stone, under
y=reverb(hp(b,400)+scr,1.6,0.3,seed=4,bright=5000)
y[-int(1.5*SR):]*=np.linspace(1,0,int(1.5*SR)); mp3(peak(y,-6),'rats.mp3')
print('  rat grains',len(grains))
# terriers: yelping at a distance, then dashing in, then the howl
d=load('0682'); p=load('2953')
n=int(11*SR); b=np.zeros(n,np.float32)
far=lp(hp(d,300),2500); put(b,far,0.0,0.35); put(b,far,0.9,0.4)
put(b,hp(d,150),2.4,0.9); put(b,hp(sg.resample_poly(d,100,106).astype(np.float32),150),3.3,0.8)
seg=p[int(6*SR):int(13*SR)]; put(b,fade(hp(seg,150),0.4,1.5),4.2,0.8)
mp3(peak(reverb(b,1.3,0.25,seed=5)[:n],-5),'terriers.mp3')
# whistle: the first blow only, thin and far
w=load('1017'); on=onsets(w,-20,0.3); a=on[0] if on else 0
x=w[a:a+int(1.1*SR)]; x=lp(hp(x,1200),7000); mp3(peak(reverb(fade(x,0.01,0.25),1.2,0.3,seed=6),-10),'whistle.mp3')
# coins on the flagging
c=load('0193'); on=onsets(c,-28,0.4); a=on[0] if on else 0
x=c[max(0,a-int(.02*SR)):a+int(3.2*SR)]; mp3(peak(reverb(fade(x,0.005,0.6),0.9,0.25,seed=7),-8),'coins.mp3')
# the Wafer: one hiss
f=load('0145'); on=onsets(f,-24,0.5); a=on[0] if on else 0
x=f[a:a+int(1.6*SR)]; mp3(peak(fade(hp(x,700),0.004,0.5),-8),'sear.mp3')
# beds, all 60 s seamless loops
def bed(k,name,lpf,db,start=2.0,hpf=60):
  x=load(k)[int(start*SR):int((start+63)*SR)]; x=lp(hp(x,hpf),lpf); mp3(rms(fold(x,3.0),db),name)
bed('2135','chapel.mp3',1800,-34)
bed('3137','river.mp3',1200,-30)
bed('2571','port.mp3',6000,-28,start=10)
# Bloxam's cart horse, for approval
h=load('1854'); x=h[int(3*SR):int(23*SR)]; mp3(rms(fade(lp(x,7000),1.0,2.0),-26),'horse-walk.mp3')
