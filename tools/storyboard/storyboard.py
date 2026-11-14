#!/usr/bin/env python3
"""The preliminary storyboard · 14 Nov 2026 (Ian: "the middle path").
Draws each beat of a storyboard sheet with an API image model through the
amenti-proxy Worker (/storyboard/image, render key only), and writes the takes to
<out>/<tag>-<model>-<k>.<ext> plus <out>/takes.json. The workflow then sends them
to the private bucket. usage: storyboard.py <sheet.json> <out dir> <model,model> [takes]"""
import json, os, sys, base64, urllib.request, time
sheet = json.load(open(sys.argv[1])); out = sys.argv[2]; models = sys.argv[3].split(','); n = int(sys.argv[4]) if len(sys.argv) > 4 else 1
KEY = os.environ['VOICE_RENDER_KEY']; os.makedirs(out, exist_ok=True)
URL = 'https://amenti-proxy.ingram-ian.workers.dev/storyboard/image'
log = []
for b in sheet['beats']:
    who = '; '.join(sheet['people'][w] for w in b['who'])
    refs = [sheet['refs']['style']] + [sheet['refs'][w] for w in b['who'] if w in sheet['refs']]
    for m in models:
        gem = not m.startswith('imagen')
        lead = ('Use the first reference image only for its painting style, palette and light. '
                + ''.join('Reference image %d is the face and look of %s. ' % (i + 2, w.title()) for i, w in enumerate(b['who']) if w in sheet['refs'])
                if gem else '')
        prompt = lead + 'Scene: ' + b['text'] + (' People: ' + who + '.' if who else '') + ' Style: ' + sheet['style']
        body = {'model': m, 'prompt': prompt, 'aspect': '16:9', 'n': n}
        if gem: body['refs'] = refs
        for attempt in range(3):
            req = urllib.request.Request(URL, json.dumps(body).encode(), {'Content-Type': 'application/json', 'x-amenti-render': KEY, 'User-Agent': 'Mozilla/5.0 amenti-storyboard'})
            try:
                d = json.load(urllib.request.urlopen(req, timeout=240)); break
            except urllib.error.HTTPError as e:
                d = {'error': e.code, 'detail': e.read().decode()[:400]}
                if e.code in (429, 500, 502, 503): time.sleep(15 * (attempt + 1)); continue
                break
            except Exception as e:
                d = {'error': 'net', 'detail': str(e)[:200]}; time.sleep(10)
        imgs = d.get('images') or []
        ext = 'png' if 'png' in (d.get('mime') or 'image/png') else 'jpg'
        names = []
        for k, im in enumerate(imgs):
            f = '%s-%s-%d.%s' % (b['tag'], m.replace('.', '_'), k, ext); open(os.path.join(out, f), 'wb').write(base64.b64decode(im)); names.append(f)
        print('%-8s %-28s %d image(s) %s' % (b['tag'], m, len(names), ('' if names else json.dumps(d)[:300])), flush=True)
        log.append({'tag': b['tag'], 'cue': b['cue'], 'mj': b.get('mj'), 'model': m, 'files': names, 'text': d.get('text') or d.get('detail')})
json.dump(log, open(os.path.join(out, 'takes.json'), 'w'), indent=1)
