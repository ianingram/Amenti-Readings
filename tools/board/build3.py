"""Book III Production Board builder (Dracula XVII–XXVII).

usage: python3 tools/board/build3.py <out.html> [--thumbs DIR]
Run from the Amenti-Readings root. Reads dracula/art.json, dracula/epNN.json and
dracula/sound.json; fetches each picture (or a frame of each clip) from the live
site into DIR (cached), packs one sprite per chapter into the page, and writes a
single self-contained HTML file. Publish it to the claude.ai artifact
"Book III Production Board" (https://claude.ai/artifact/3WLsxAbmHkwyYtGwqivagW);
notes live in its db collection `notes`, doc id `c<ch>-<file>`.

Timing follows player/art.js: a scene runs from its cue (or its "at" phrase) to
the next scene, measured in words at 2.5 words/s; picture k of N comes up k/N of
the way through, never sooner than MIN_HOLD (9 s) after the one before, so a
picture whose turn falls after the scene ends is never shown. A "pause" adds its
seconds at the top of the scene. Spoken-time estimates, not the recorded clocks.
"""
import sys, os, json, base64, io, subprocess, concurrent.futures as cf, urllib.request

ROMAN = {17: 'XVII', 18: 'XVIII', 19: 'XIX', 20: 'XX', 21: 'XXI', 22: 'XXII', 23: 'XXIII', 24: 'XXIV', 25: 'XXV', 26: 'XXVI', 27: 'XXVII'}
LIVE = 'https://ianingram.github.io/Amenti-Readings/dracula/'
WPS, MIN_HOLD, COLS, TW, TH = 2.5, 9, 10, 200, 113

out = sys.argv[1]
thumbs = sys.argv[sys.argv.index('--thumbs') + 1] if '--thumbs' in sys.argv else '/tmp/board3-thumbs'
os.makedirs(thumbs, exist_ok=True)
art = json.load(open('dracula/art.json'))
base = art.get('base', 'art/')
TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'board3.template.html')).read()


def words(s): return len(s.split())


def build_chapter(n):
    cues = json.load(open(f'dracula/ep{n}.json'))['cues']
    idx = {q['n']: i for i, q in enumerate(cues)}
    start = []; t = 0
    for q in cues: start.append(t); t += words(q['text']) / WPS
    total = t

    def time_of(cue_n, at=None):
        i = idx[cue_n]; s = start[i]
        if at and at in cues[i]['text']:
            s += words(cues[i]['text'][:cues[i]['text'].find(at)]) / WPS
        return s

    # sound events: (time, label)
    ev = []
    for i, q in enumerate(cues):
        for key in ('score', 'sfx', 'bed', 'under'):
            v = q.get(key)
            if v is None: continue
            for e in (v if isinstance(v, list) else [v]):
                if isinstance(e, dict):
                    k = e.get('key'); at = e.get('at')
                else:
                    k, at = e, None
                tt = time_of(q['n'], at)
                lab = {'score': 'score', 'sfx': 'sfx', 'bed': 'room', 'under': 'under'}[key]
                ev.append((tt, f"{lab}: {k if k else '— off'}" + (f" at “{at}”" if at else '')))
    ev.sort()

    scenes = sorted(art['episodes'][str(n)], key=lambda s: (s['from'], 'at' in s))
    pics = []; shift = 0.0
    for si, s in enumerate(scenes):
        if s['from'] not in idx: continue
        s0 = time_of(s['from'], s.get('at')) + shift
        if s.get('pause'): shift += s['pause']
        nxt = scenes[si + 1] if si + 1 < len(scenes) else None
        s1 = (time_of(nxt['from'], nxt.get('at')) + shift) if nxt and nxt['from'] in idx else total + shift
        imgs = s.get('images', []); N = len(imgs)
        starts = []; prev = None
        for k in range(N):
            st = s0 + k * (s1 - s0) / max(N, 1)
            if prev is not None: st = max(st, prev + MIN_HOLD)
            starts.append(st); prev = st
        q = cues[idx[s['from']]]
        for k, f in enumerate(imgs):
            st = starts[k]; en = min(starts[k + 1] if k + 1 < N else s1, s1)
            on = max(0, round(en - st)) if st < s1 else 0
            snd = [lab for tt, lab in ev if (st - 0.01 <= tt < max(en, st + 0.01)) or (k == 0 and abs(tt - s0) < 0.5)]
            pics.append(dict(k=f'c{n}-{f}', file=f, url=LIVE + base + f, cue=s['from'], t=int(st), on=on,
                             first=(k == 0), at=s.get('at', ''), cap=s.get('caption', '') if k == 0 else '',
                             snd=list(dict.fromkeys(snd))[:6], who=q.get('role', ''), line=q['text'].replace('\n', ' ')[:260],
                             mv=f.endswith('.mp4')))
    return dict(n=n, roman=ROMAN[n], pics=pics, mins=round(total / 60))


def fetch(f):
    p = os.path.join(thumbs, f + '.jpg')
    if os.path.exists(p) and os.path.getsize(p) > 0: return f, p
    url = LIVE + base + f
    if f.endswith('.mp4'):
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-ss', '1', '-i', url, '-frames:v', '1', '-vf', f'scale={TW}:{TH}', p])
    else:
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
            from PIL import Image
            Image.open(io.BytesIO(data)).convert('RGB').resize((TW, TH)).save(p, quality=80)
        except Exception as e:
            print('miss', f, e); return f, None
    return f, p if os.path.exists(p) else None


from PIL import Image
chapters = [build_chapter(n) for n in range(17, 28)]
allf = sorted({p['file'] for c in chapters for p in c['pics']})
with cf.ThreadPoolExecutor(16) as ex: got = dict(ex.map(fetch, allf))
for c in chapters:
    files = list(dict.fromkeys(p['file'] for p in c['pics']))
    rows = (len(files) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * TW, max(rows, 1) * TH))
    pos = {}
    for i, f in enumerate(files):
        pos[f] = i
        if got.get(f): sheet.paste(Image.open(got[f]), ((i % COLS) * TW, (i // COLS) * TH))
    b = io.BytesIO(); sheet.save(b, 'JPEG', quality=62)
    c['sprite'] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    c['cols'], c['rows'] = COLS, max(rows, 1)
    for p in c['pics']: p['ti'] = pos[p['file']] if got.get(p['file']) else -1
html = TEMPLATE.replace('/*__DATA__*/', 'const D=' + json.dumps({'chapters': chapters}, ensure_ascii=False, separators=(',', ':')) + ';')
open(out, 'w').write(html)
print('wrote', out, round(len(html) / 1e6, 1), 'MB;', sum(len(c['pics']) for c in chapters), 'pictures;',
      sum(1 for c in chapters for p in c['pics'] if p['on'] == 0), 'never shown')
