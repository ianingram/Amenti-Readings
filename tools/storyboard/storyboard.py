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
    R = sheet.get('refs') or {}
    refs = ([R['style']] if R.get('style') else []) + [R[w] for w in b['who'] if w in R]
    for m in models:
        gem = not m.startswith('imagen')
        faces = [w for w in b['who'] if w in R]; off = 2 if R.get('style') else 1
        lead = (('Use the first reference image only for its painting style, palette and light. ' if R.get('style') else '')
                + ''.join('Reference image %d is the face and look of %s. ' % (i + off, w.title()) for i, w in enumerate(faces))
                if gem else '')
        prompt = lead + 'Scene: ' + b['text'] + (' People: ' + who + '.' if who else '') + ' Style: ' + sheet['style']
        body = {'model': m, 'prompt': prompt, 'aspect': b.get('aspect', '16:9'), 'n': n}
        if gem and refs: body['refs'] = refs
        if gem and (b.get('size') or sheet.get('size')): body['size'] = b.get('size') or sheet['size']   # '2K' (18 Nov); absent = 1K
        if b.get('edit'):   # repair an existing painting: the image goes in, the change is described, the rest is kept
            body['refs'] = [b['edit']] + refs[:3]
            body['prompt'] = ('Edit the first image, a finished oil painting. ' + b['text'] + ' Change nothing else: keep the same '
                              'composition, framing, people, faces, light, colours, brushwork and aspect ratio. No text, signature or border.')
        time.sleep(float(os.environ.get('PACE', '12')))  # Vertex's per-minute image quota
        for attempt in range(10):   # 20 Nov: Google's shared image capacity refuses at peak; wait it out (~20 min) rather than lose the beat
            req = urllib.request.Request(URL, json.dumps(body).encode(), {'Content-Type': 'application/json', 'x-amenti-render': KEY, 'User-Agent': 'Mozilla/5.0 amenti-storyboard'})
            try:
                d = json.load(urllib.request.urlopen(req, timeout=240)); break
            except urllib.error.HTTPError as e:
                try: det = e.read().decode()[:400]
                except Exception: det = ''                   # a reset while reading the error body (18 Nov) must not kill the run
                d = {'error': e.code, 'detail': det}
                if e.code in (429, 500, 502, 503) and attempt < 9: time.sleep(min(30 * (attempt + 1), 180)); continue
                break
            except Exception as e:
                d = {'error': 'net', 'detail': str(e)[:200]}; time.sleep(10)
        imgs = d.get('images') or []
        ext = 'png' if 'png' in (d.get('mime') or 'image/png') else 'jpg'
        names = []
        for k, im in enumerate(imgs):
            f = '%s-%s-%d.%s' % (b['tag'], m.replace('.', '_'), k, ext); open(os.path.join(out, f), 'wb').write(base64.b64decode(im)); names.append(f)
        print('%-8s %-28s %d image(s) %s' % (b['tag'], m, len(names), ('' if names else json.dumps(d)[:300])), flush=True)
        log.append({'tag': b['tag'], 'cue': b.get('cue'), 'mj': b.get('mj'), 'chapter': b.get('chapter'), 'model': m, 'files': names, 'roads': d.get('roads') or d.get('road'), 'text': d.get('text') or d.get('detail')})
json.dump(log, open(os.path.join(out, 'takes.json'), 'w'), indent=1)
