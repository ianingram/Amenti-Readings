"""Round 2 · 19 Nov 2026: QA-confirmed invented words (medium.en, 4+ extra words) and cue 15/17."""
import json, glob, re
from mksheet import expand, groups
R = json.load(open('round2.json')) + [['15', 17, None, 5]]
plans = {}
for f in glob.glob('/home/claude/amenti-readings/tools/sampler/tm-fixes-ch*.json'):
    for g in json.load(open(f))['plan']: plans.setdefault((g['ch'], g['n']), []).append(g)
def lastclause(t, cap=150):
    t = t.replace('\n', ' ').strip(); parts = re.split(r'(?<=[.!?;:])\s+', t); out = ''
    for p in reversed(parts):
        if len(out) + len(p) > cap and out: break
        out = (p + ' ' + out).strip()
    return out[-cap * 2:]
tags, lines, plan = [], [], []
bycue = {}
for ch, n, k, np_ in R: bycue.setdefault((ch, n), []).append(k)
for (ch, n), ks in sorted(bycue.items()):
    m = json.load(open('/home/claude/v3m/%s/manifest.json' % ch)); c = [c for c in m['cues'] if c['n'] == n][0]
    ch_ = c['chunks']; L = len(ch_)
    if L == 1:
        prev = [x for x in m['cues'] if x['n'] == n - 1]
        own = expand(ch_[0]['text']); lead = expand(lastclause(prev[0]['text'])) if prev else ''
        gs = [{'pieces': [0, 0], 'text': (lead + ' ' + own).strip(), 'own': own}]
    else:
        joins = set()
        for k in ks:
            if k is None: joins |= set(range(L - 1))
            else: joins.add(k - 1 if k > 0 else 0)
        for g in plans.get((ch, n), []): joins |= set(range(g['pieces'][0], g['pieces'][1]))   # round-1 joins redone with the cue
        gs = [{'pieces': [a, b], 'text': expand(' '.join(x['text'] for x in ch_[a:b + 1]))} for a, b in groups(ch_, joins)]
    for i, g in enumerate(gs):
        tag = '%s-%d-r%d' % (ch, n, i); g.update(ch=ch, n=n, tag=tag); plan.append(g)
        for t in range(3): tags.append('%s/%d' % (tag, t)); lines.append([c['role'], c['cast'], c['voice'], g['text']])
json.dump({'work': 'the-three-musketeers', 'note': __doc__.strip() + ' 3 takes each, probe.', 'tags': tags, 'lines': lines, 'plan': plan},
          open('/home/claude/amenti-readings/tools/sampler/tm-fixes-round2.json', 'w'), ensure_ascii=False, indent=1)
print(len(plan), 'groups', len(lines), 'lines', max(len(g['text']) for g in plan), 'chars max')
for g in plan: print(g['tag'], g['pieces'], ('OWN: ' + g['own'] if g.get('own') else '')[:60], '|', g['text'][:70])
