#!/usr/bin/env python3
"""Places the birds of Treasure Island in the cue sheets, by script · 14 Nov 2026.

Ian: gulls as players, "sometimes close and boisterous, sometimes far away, swooping
down", and editing is what eats the time, so this places them from the text:
  - the chapter's place (its bed) sets who is about: docks, deck, cove and the coracle
    have gulls of every kind; on the island only far ones, now and then;
  - one bird event every so often by place, on a phrase inside a line (not on its
    first word), never in a line that speaks of night, dark, moon or stars;
  - where Stevenson names gulls or sea-birds, they cry on those words;
  - the first gunshot of a chapter by the shore or at sea starts a flock up.
Every placed entry carries "by": "place-birds", so running this again first removes
what it placed before, and hand-placed sounds are never touched.
usage: place-birds.py  (from treasure-island/)
"""
import json, glob, re, collections, random
SEC_PER_CHAR = 1 / 14.5                                     # the voice's pace, roughly
NIGHT = re.compile(r'\b(night|dark|darkness|moon|moonlight|stars?|midnight|candle|lantern)\b', re.I)
GUN = re.compile(r'^(cannon|musket|pistol|long-gun|round-shot|stockade-attack)', re.I)
NAMED = re.compile(r'\b(gulls?|sea-?birds?|sea birds)\b', re.I)
KINDS = {   # place -> (seconds between events, [(kind, weight)])
    'docks':   (55, [('near', 3), ('pair', 3), ('laugh', 2), ('far', 2)]),
    'deck':    (70, [('far', 4), ('swoop', 2), ('pair', 2), ('near', 1)]),
    'cove':    (65, [('far', 4), ('pair', 2), ('laugh', 1), ('near', 1)]),
    'coracle': (45, [('near', 3), ('swoop', 3), ('pair', 2), ('far', 1)]),
    'island':  (160, [('far', 1)]),
}
COUNT = {'near': 3, 'pair': 3, 'laugh': 2, 'far': 3, 'swoop': 3, 'flock': 2}
snd = json.load(open('sound.json'))
place = {c['n']: c.get('bed') for c in snd['chapters']}

def phrase(text, rnd):
    """a short run of words from inside the line, exactly as written (whitespace evened)"""
    t = re.sub(r'\s+', ' ', text).strip(); words = t.split(' ')
    if len(words) < 8: return None
    i = rnd.randint(int(len(words) * 0.3), max(int(len(words) * 0.3), len(words) - 4))
    p = ' '.join(words[i:i + 4])
    return p if t.count(p) == 1 else None

total = collections.Counter()
for path in sorted(glob.glob('ep*.json')):
    n = int(path[2:4]); raw = open(path).read(); d = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    rnd = random.Random(1883 + n)
    for c in d['cues']:                                      # first, take away what this script placed before
        if c.get('sfx'):
            c['sfx'] = [e for e in c['sfx'] if not (isinstance(e, dict) and e.get('by') == 'place-birds')]
            if not c['sfx']: del c['sfx']
    pl = place.get(n); gap, kinds = KINDS.get(pl, (None, None)); since = gap * 0.5 if gap else 0
    flock_done = False
    for c in d['cues']:
        if c.get('audio'): continue
        text = c.get('text') or ''; secs = len(text) * SEC_PER_CHAR; add = []
        m = NAMED.search(text)
        if m and not NIGHT.search(text):
            add.append({'key': 'gull_%s_%d' % (rnd.choice(['near', 'pair']), rnd.randint(1, 3)), 'at': m.group(0), 'by': 'place-birds'})
        if pl in KINDS and not flock_done and pl != 'inn':
            for e in c.get('sfx') or []:
                k = e if isinstance(e, str) else e.get('key', '')
                if k and GUN.match(k):
                    ent = {'key': 'gull_flock_%d' % rnd.randint(1, 2), 'by': 'place-birds'}
                    if isinstance(e, dict) and e.get('at'): ent['at'] = e['at']; ent['offset'] = (e.get('offset') or 0) + 0.45
                    add.append(ent); flock_done = True; break
        since += secs
        if gap and since >= gap and not NIGHT.search(text) and not add:
            p = phrase(text, rnd)
            if p:
                kind = rnd.choices([k for k, w in kinds], [w for k, w in kinds])[0]
                add.append({'key': 'gull_%s_%d' % (kind, rnd.randint(1, COUNT[kind])), 'at': p, 'by': 'place-birds'})
                since = rnd.uniform(-0.25, 0.25) * gap
        if add:
            c['sfx'] = (c.get('sfx') or []) + add
            for a in add: total[a['key'].rsplit('_', 1)[0]] += 1
    open(path, 'w').write(json.dumps(d, indent=1, ensure_ascii=False) + ('\n' if raw.endswith('\n') else ''))

# the sound sheet learns the gulls' names
f = snd['files']; f.setdefault('sfx_levels', {})
for kind, k in COUNT.items():
    for i in range(1, k + 1):
        key = 'gull_%s_%d' % (kind, i); f['oneshots'][key] = 'gull-%s-%d.mp3' % (kind, i); f['sfx_levels'].setdefault(key, 0.9)
json.dump(snd, open('sound.json', 'w'), indent=2, ensure_ascii=False); open('sound.json', 'a').write('\n')
print('placed:', dict(total), '· total', sum(total.values()))
