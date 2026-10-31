"""Dracula production board — builds dracula/board/index.html from art.json, the cue sheets and sound.json.
Run: python3 tools/board/build.py   (needs Pillow and ffmpeg). In the claude.ai artifact the note boxes save to the
artifact database; opened from GitHub Pages the board is read-only."""
import json,re,subprocess,os,sys
from PIL import Image
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
R=str(ROOT/'dracula')+'/'; LIVE='https://ianingram.github.io/Amenti-Readings/dracula/art/'
OUT=str(ROOT/'dracula'/'board')+'/'
A=json.load(open(R+'art.json'))
def adur(q):
  au=q.get('audio')
  if au:
    p=R+'sound/'+au.split('/')[-1]
    if os.path.exists(p): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
  return len((q.get('text') or '').split())/2.5
def fmt(v):
  if v is None: return ''
  if isinstance(v,str): return v
  if isinstance(v,dict): return (v.get('key') or 'off')+(' at “'+v['at']+'”' if v.get('at') else '')
  if isinstance(v,list): return '; '.join(fmt(x) for x in v)
  return str(v)
def thumb(name):
  base=re.sub(r'^dracula-','',name); base=re.sub(r'-air2?\.mp4$','.jpg',base).replace('.mp4','.jpg')
  src=R+'art/'+base
  if not os.path.exists(src):
    mp=R+'art/'+name
    if os.path.exists(mp): subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss','0.3','-i',mp,'-frames:v','1','/tmp/board-x.png']); src='/tmp/board-x.png'
    else: return None
  return Image.open(src).convert('RGB').resize((240,135),Image.LANCZOS)
data={'book':'Dracula · Book I · The Castle','chapters':[]}
TW,TH,COLS=240,135,10
for ep in (1,2,3,4):
  e=json.load(open(R+f'ep0{ep}.json')); cues={q['n']:q for q in e['cues']}
  T={};t=0
  for q in e['cues']: T[q['n']]=(t,adur(q)); t+=T[q['n']][1]
  def start(s):
    t0,d=T[s['from']]
    if 'at' in s:
      tx=re.sub(r'\s+',' ',cues[s['from']]['text']); return t0+d*max(0,tx.find(s['at']))/len(tx)
    return t0
  sc=sorted(A['episodes'][str(ep)],key=lambda s:(start(s),'at' in s))
  rows=[]; thumbs=[]; seen={}
  for i,s in enumerate(sc):
    st=start(s); en=start(sc[i+1]) if i+1<len(sc) else t
    N=len(s['images']); kk=0; since=st; tt=st; times=[st]
    while tt<en:
      tt+=0.25; want=min(N-1,int((tt-st)/max(0.01,en-st)*N))
      if want>kk and tt-since>=9: kk+=1; since=tt; times.append(tt)
    q=cues[s['from']]
    snd=[x for x in [('score: '+fmt(q['score'])) if 'score' in q else '',('room: '+q['bed']) if q.get('bed') else '',('sounds: '+fmt(q['sfx'])) if q.get('sfx') else '',('music under: '+q['under']) if q.get('under') else ''] if x]
    for j,im in enumerate(s['images']):
      name=im.split('/')[-1]; url=im if im.startswith('http') else LIVE+im
      on=round((times[j+1] if j+1<len(times) else en)-times[j]) if j<len(times) else 0
      tm=times[j] if j<len(times) else st
      key=f'c{ep}-'+re.sub(r'[^A-Za-z0-9_.~:@+-]','_',name); seen[key]=seen.get(key,0)+1
      if seen[key]>1: key+=f'-{seen[key]}'
      th=thumb(name); ti=-1
      if th: ti=len(thumbs); thumbs.append(th)
      rows.append({'k':key,'cue':s['from'],'at':s.get('at') if j==0 else None,'first':j==0,'t':round(tm),'on':on,'file':name,'url':url,'mv':name.endswith('.mp4'),'cap':(s.get('caption') or '') if j==0 else '','snd':snd if j==0 else [],'who':(q.get('role') or '') if j==0 else '','line':re.sub(r'\s+',' ',q.get('text') or '')[:260] if j==0 else '','ti':ti})
  rws=(len(thumbs)+COLS-1)//COLS; sp=Image.new('RGB',(COLS*TW,max(1,rws)*TH))
  for i,th in enumerate(thumbs): sp.paste(th,((i%COLS)*TW,(i//COLS)*TH))
  sp.save(OUT+f's{ep}.jpg',quality=72)
  data['chapters'].append({'n':ep,'roman':['I','II','III','IV'][ep-1],'title':e['title'],'mins':round(t/60),'sprite':f's{ep}.jpg','cols':COLS,'rows':rws,'pics':rows})
  print(ep,len(rows),os.path.getsize(OUT+f's{ep}.jpg')//1024,'KB')
import base64
for c in data['chapters']: c['sprite']='data:image/jpeg;base64,'+base64.b64encode(open(OUT+c['sprite'],'rb').read()).decode()
tpl=open(pathlib.Path(__file__).with_name('board_tpl.html')).read().replace("background-image:url(${c.sprite})","background-image:url('${c.sprite}')")
open(OUT+'index.html','w').write('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'+tpl.replace('__DATA__',json.dumps(data,ensure_ascii=False)))
for c in (1,2,3,4):
  try: os.remove(OUT+f's{c}.jpg')
  except OSError: pass
print('wrote',OUT+'index.html')
