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
  p=p.split('/')[-1]; src=R/'art'/p
  if p.endswith('.mp4'):
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss','1','-i',str(src),'-frames:v','1','/tmp/scene-th.jpg']); src='/tmp/scene-th.jpg'
  im=Image.open(src).convert('RGB'); im.thumbnail((560,316)); b=io.BytesIO(); im.save(b,'JPEG',quality=70)
  return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
beats=[]
for b in spec['beats']:
  c=cues[b['cue']]; tx=' '.join(c['text'].split()); s0,d=T[b['cue']]
  st=s0+(d*tx.index(b['at'])/len(tx) if b.get('at') else 0)
  im=b.get('images') or []
  beats.append(dict(start=round(st),name=b['name'],words=b['words'],note=b.get('note'),prompt=b.get('prompt'),
    status='in' if im else 'need',img=th(im[0]) if im else None,extra=[th(x) for x in im[1:]]))
for i,b in enumerate(beats): b['end']=beats[i+1]['start'] if i+1<len(beats) else round(total)
mm=lambda s:f"{int(s//60)}:{int(round(s%60)):02d}"
html=open(pathlib.Path(__file__).with_name('scene_tpl.html')).read()
html=(html.replace('__TITLE__',spec['title']).replace('__H1__',spec['h1']).replace('__END__',mm(total))
  .replace('__SUB__',f"{mm(total)} of narration. Each beat starts on its words and holds until the next. Green is in the book, red still needs painting.")
  .replace('__DATA__',json.dumps({'beats':beats},ensure_ascii=False)))
open(sys.argv[2],'w').write(html); print('wrote',sys.argv[2],len(beats),'beats',mm(total))
