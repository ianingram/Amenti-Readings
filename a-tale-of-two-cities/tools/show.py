import json, re, sys
ch = int(sys.argv[1]); lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0; hi = int(sys.argv[3]) if len(sys.argv) > 3 else 9999
raw = open('/home/claude/live/library/charles-dickens/a-tale-of-two-cities/ch%02d.md' % ch).read()
paras = [p for p in re.split(r'\n{2,}', raw) if p.strip()]
d = json.load(open('ep%02d.json' % ch)); sp = {}
for c in d['cues']:
    if c['text'].startswith('“'): sp.setdefault(c['para'], []).append(c['role'].split()[0][:8])
for i, p in enumerate(paras):
    if i < lo or i > hi: continue
    t = re.sub(r'\s+', ' ', p)
    if i in sp: print('%d [%s] %s' % (i, ','.join(sp[i]), t[:170]))
    else: print('%d    -- %s' % (i, t[:90]))
