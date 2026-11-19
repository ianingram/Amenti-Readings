"""Three Musketeers abbreviation splits · 19 Nov 2026. The locked chunker ends a measure after
M./Mme./MM./St.; the voice then invents words. For each such split the pieces on both sides are
re-rendered as ONE line with the word written out, and later baked into the cue's audio.
usage: mksheet.py <out sheet> <rows.json: [{ch,n,cast,voice,role,chunks:[{text,rest}]}]> [extra 'ch:n:i-j' ...]"""
import json, re, sys
ABBR = re.compile(r'\b(M|Mme|MM|Mlle|St)\.\s*$')
EXP = [(r'\bMM\.(?=\s)', 'Messieurs'), (r'\bMme\.(?=\s)', 'Madame'), (r'\bMlle\.(?=\s)', 'Mademoiselle'),
       (r'\bM\.(?=\s)', 'Monsieur'), (r'\bSt\.(?=\s)', 'Saint')]
def expand(t):
    for a, b in EXP: t = re.sub(a, b, t)
    return t
def groups(chunks, extra=()):
    joins = {k for k in range(len(chunks) - 1) if ABBR.search(chunks[k]['text'])} | set(extra)
    out, k = [], 0
    while k < len(chunks):
        if k in joins:
            j = k
            while j in joins: j += 1
            out.append((k, j)); k = j + 1
        else: k += 1
    return out
if __name__ == '__main__':
    out, rows = sys.argv[1], json.load(open(sys.argv[2])); extra = {}
    for e in sys.argv[3:]:
        ch, n, rg = e.split(':'); a, b = map(int, rg.split('-')); extra.setdefault((ch, int(n)), set()).update(range(a, b))
    tags, lines, plan = [], [], []
    for r in rows:
        for g, (a, b) in enumerate(groups(r['chunks'], extra.get((r['ch'], r['n']), ()))):
            text = expand(' '.join(c['text'] for c in r['chunks'][a:b + 1]))
            plan.append({'ch': r['ch'], 'n': r['n'], 'pieces': [a, b], 'tag': '%s-%d-%d' % (r['ch'], r['n'], g), 'text': text})
            for k in range(3): tags.append('%s-%d-%d/%d' % (r['ch'], r['n'], g, k)); lines.append([r['role'], r['cast'], r['voice'], text])
    json.dump({'work': 'the-three-musketeers', 'note': __doc__.split('\n')[0] + ' 3 takes each, probe.', 'tags': tags, 'lines': lines, 'plan': plan},
              open(out, 'w'), ensure_ascii=False, indent=1)
    print(len(plan), 'groups,', len(lines), 'lines,', max(len(p['text']) for p in plan), 'chars max')
