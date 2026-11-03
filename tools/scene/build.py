"""Scene page: one critical scene laid out on the narration's clock, beat by beat, with the
pictures in place and copyable Midjourney prompts for the ones still to paint.
Run: python3 tools/scene/build.py scene.json out.html
scene.json = {"title","h1","ep","from","to","beats":[{"cue","at"?,"name","words","images"?:[...],"prompt"?,"note"?}]}
Times come from the cue audio (or 2.5 words/s); a beat starts at its cue + the position of "at" in the text."""
import json,sys,io,base64,subprocess,os,pathlib
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[2]; R=ROOT/'dracula'
spec=json.load(open(sys.argv[1])); cues={c['n']:c for c in json.load(open(R/f"ep{spec['ep']:02d}.json"))['cues']}
def dur(c):
  au=c.get('audio')
  if au and (R/'sound'/au.split('/')[-1]).exists():
    return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(R/'sound'/au.split('/')[-1])],capture_output=True,text=True).stdout)
  return len(c['text'].split())/2.5
T={};t=0
for n in range(spec['from'],spec['to']+1): T[n]=(t,dur(cues[n])); t+=T[n][1]
total=t
def th(p):
  url=p if p.startswith('http') else None
  p=p.split('/')[-1]; src=R/'art'/p
  if url and not src.exists():
    src=pathlib.Path('/tmp')/p
    if not src.exists(): subprocess.run(['curl','-s','--retry','3','-m','200','-o',str(src),url])
  if p.endswith('.mp4'):
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss','1','-i',str(src),'-frames:v','1','/tmp/scene-th.jpg']); src='/tmp/scene-th.jpg'
  im=Image.open(src).convert('RGB'); im.thumbnail((560,316)); b=io.BytesIO(); im.save(b,'JPEG',quality=70)
  return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
# every picture already placed in this stretch comes straight from art.json, so nothing is left out
A=json.load(open(R/'art.json'))['episodes'][str(spec['ep'])]
def start_of(cue,at=None):
  tx=' '.join(cues[cue]['text'].split()); s0,d=T[cue]
  return s0+(d*tx.index(at)/len(tx) if at and at in tx else 0)
rows=[]
prev=[sc for sc in A if sc['from']<spec['from'] and sc.get('images')]
if prev:   # the picture already on screen when the stretch begins
  sc=prev[-1]; rows.append(dict(cue=spec['from'],at=None,name=(sc.get('caption') or f"Carried over from cue {sc['from']}"),images=sc['images'],placed=True))
for sc in A:
  if spec['from']<=sc['from']<=spec['to'] and sc.get('images'):
    rows.append(dict(cue=sc['from'],at=sc.get('at'),name=sc.get('caption') or '',images=sc['images'],placed=True))
for b in spec.get('beats',[]):
  if not b.get('images'): rows.append(dict(b,placed=False))
for r in rows: r['t']=start_of(r['cue'],r.get('at'))
rows.sort(key=lambda r:(r['t'],r['placed']==False))
beats=[]
for i,r in enumerate(rows):
  c=cues[r['cue']]; tx=' '.join(c['text'].split()); a=tx.index(r['at']) if r.get('at') and r['at'] in tx else 0
  nxt=[x for x in rows[i+1:] if x['cue']==r['cue'] and x.get('at') and x['at'] in tx]
  z=tx.index(nxt[0]['at']) if nxt else len(tx); words=tx[a:z]
  if len(words)>420: words=words[:420].rsplit(' ',1)[0]+' …'
  im=r.get('images') or []
  beats.append(dict(start=round(r['t']),cue=r['cue'],who=c.get('role',''),name=r.get('name') or (f"Cue {r['cue']}" + (f" · “{r['at']}”" if r.get('at') else '')),
    words=words,note=r.get('note'),prompt=r.get('prompt'),status='in' if im else 'need',
    img=th(im[0]) if im else None,extra=[th(x) for x in im[1:]],files=[x.split('/')[-1] for x in im]))
for i,b in enumerate(beats): b['end']=beats[i+1]['start'] if i+1<len(beats) else round(total)
mm=lambda s:f"{int(s//60)}:{int(round(s%60)):02d}"
html=open(pathlib.Path(__file__).with_name('scene_tpl.html')).read()
html=(html.replace("__FOCUS__",spec.get("focus","")).replace('__TITLE__',spec['title']).replace('__H1__',spec['h1']).replace('__END__',mm(total))
  .replace('__SUB__',f"{mm(total)} of narration. Each beat starts on its words and holds until the next. Green is in the book, red still needs painting.")
  .replace('__DATA__',json.dumps({'beats':beats},ensure_ascii=False)))
open(sys.argv[2],'w').write(html); print('wrote',sys.argv[2],len(beats),'beats',mm(total))
