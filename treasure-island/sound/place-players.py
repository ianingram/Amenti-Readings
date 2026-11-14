#!/usr/bin/env python3
"""Places the ship, the island, the horses and the map in the cue sheets, by script · 14 Nov 2026.

The players come from build-players.py (creaks, ropes, sails, rigging, feet, distant
voices, trees in the wind, birds by the time of day, insects, single waves, the horses,
the map). As with the gulls, editing time is the enemy, so this places them from the text:
  - the chapter's place (its bed) decides who is about, and each kind keeps its own
    rough interval, on a phrase inside a line (never its first words);
  - the time of day is read from the text as it goes (dawn, day, dusk, night) and
    carried from chapter to chapter: it picks the birds and insects, and keeps gulls,
    day-birds and cicadas out of the night (place-birds.py's gulls included);
  - the horses, the map and the riders are placed by hand-picked words below.
Every placed entry carries "by": "place-players"; running this again first removes
what it placed before. Hand-placed sounds are never touched.
usage: place-players.py  (from treasure-island/, after place-birds.py)
"""
import json, glob, re, collections, random
SEC_PER_CHAR = 1 / 14.5
# the time of day: where each chapter starts (from the book), and the words that turn it
START = {1: 'day', 2: 'day', 3: 'day', 4: 'night', 5: 'night', 6: 'night', 7: 'day', 8: 'day', 9: 'day', 10: 'day',
         11: 'night', 12: 'night', 13: 'day', 14: 'day', 15: 'day', 16: 'day', 17: 'day', 18: 'day', 19: 'day',
         20: 'dawn', 21: 'day', 22: 'day', 23: 'night', 24: 'dawn', 25: 'day', 26: 'day', 27: 'night', 28: 'night',
         29: 'night', 30: 'dawn', 31: 'day', 32: 'day', 33: 'day', 34: 'day'}
TURN = [('dusk', re.compile(r'sun (?:went|had gone|was going) down|sun had set|sunset|the evening (?:fell|came)|dusk', re.I)),
        ('night', re.compile(r'night (?:fell|had fallen|came on)|it was (?:now )?(?:quite |pitch )?dark|darkness (?:had )?(?:fallen|come)|the moon (?:rose|had risen|was up)|by moonlight', re.I)),
        ('dawn', re.compile(r'\bdawn\b|day ?break|day broke|first (?:grey|gray) of|sun rose|sunrise', re.I)),
        ('day', re.compile(r'broad daylight|full day|the sun was (?:up|high|hot)|heat of the (?:sun|day)|\bnoon\b|forenoon', re.I))]
AFTER = {'dawn': ('day', 5), 'dusk': ('night', 10)}       # dawn turns to day, dusk to night, after so many lines
P = collections.OrderedDict
GROUPS = {  # bed -> {group: (seconds between, [(key prefix, weight)])}
    'deck':     {'creak': (28, [('creak', 1)]), 'rope': (45, [('rope', 1)]), 'sail': (40, [('sail', 1)]),
                 'rigging': (85, [('rigging', 1)]), 'feet': (75, [('feet', 1)]), 'voices': (110, [('voices_far', 1)])},
    'coracle':  {'creak': (30, [('creak', 1)]), 'wave': (25, [('wave', 1)])},
    'docks':    {'creak': (50, [('creak', 1)]), 'rope': (55, [('rope', 1)]), 'voices': (45, [('voices_far', 1)]), 'feet': (80, [('feet', 1)])},
    'cove':     {'wave': (30, [('wave', 1)]), 'trees': (90, [('trees', 1)])},
    'island':   {'trees': (45, [('trees', 1)]), 'birds': (40, [('birds', 1)]), 'insects': (75, [('insects', 1)]), 'cry': (900, [('bird_cry', 1)])},
    'stockade': {'trees': (60, [('trees', 1)]), 'birds': (55, [('birds', 1)]), 'insects': (90, [('insects', 1)])},
    'inn':      {'creak': (120, [('creak', 1)])},
    'tavern':   {'creak': (120, [('creak', 1)])},
}
BY_HAND = [  # (chapter, cue n, key, words in that cue)
    (1, 47, 'horse_come_go', 'horse came to the door'),
    (5, 61, 'horses_trot_away', 'struck out at a bouncing trot'),
    (6, 3, 'horses_arrive', 'drew up before'),
    (6, 84, 'map_unfold', 'the map of an island'),
    (12, 18, 'map_unfold', 'took the chart'),
    (29, 50, 'map_fold', 'cast down upon the floor'),
]
pl = json.load(open('sound/players.json'))['counts']
snd = json.load(open('sound.json')); place = {c['n']: c.get('bed') for c in snd['chapters']}

def key_for(prefix, tod, rnd):
    if prefix == 'birds': prefix = 'birds_' + tod
    if prefix == 'insects':
        if tod in ('dawn', 'dusk'): return None
        prefix = 'insects_' + tod
    if prefix == 'bird_cry': return 'bird_cry_1' if tod != 'night' else None
    if prefix == 'voices_far' and tod == 'night': return None
    n = pl.get(prefix)
    return '%s_%d' % (prefix, rnd.randint(1, n)) if n else None

def phrase(text, rnd, used):
    t = re.sub(r'\s+', ' ', text).strip(); words = t.split(' ')
    if len(words) < 8: return None
    for _ in range(6):
        i = rnd.randint(int(len(words) * 0.25), max(int(len(words) * 0.25), len(words) - 4))
        p = ' '.join(words[i:i + 4])
        if t.count(p) == 1 and p not in used: return p
    return None

total = collections.Counter(); gulls_cut = 0
for path in sorted(glob.glob('ep*.json')):
    n = int(path[2:4]); raw = open(path).read(); d = json.loads(raw, object_pairs_hook=P)
    rnd = random.Random(1881 + n); tod = START.get(n, 'day'); held = 0
    for c in d['cues']:
        if c.get('sfx'):
            c['sfx'] = [e for e in c['sfx'] if not (isinstance(e, dict) and e.get('by') == 'place-players')]
            if not c['sfx']: del c['sfx']
    groups = GROUPS.get(place.get(n), {})
    since = {g: rnd.uniform(0.3, 0.8) * gap for g, (gap, _) in groups.items()}
    for c in d['cues']:
        text = c.get('text') or ''
        found = sorted((m.start(), nm) for nm, rx in TURN for m in rx.finditer(text))
        if found: tod = found[-1][1]; held = 0
        else:
            held += 1
            if tod in AFTER and held >= AFTER[tod][1]: tod = AFTER[tod][0]; held = 0
        if c.get('audio'): continue
        # at night the day's birds keep quiet (gulls from place-birds included, unless named)
        if tod == 'night' and c.get('sfx'):
            keep = [e for e in c['sfx'] if not (isinstance(e, dict) and e.get('by') == 'place-birds' and not re.search(r'gull|sea-?bird', e.get('at') or '', re.I))]
            gulls_cut += len(c['sfx']) - len(keep); c['sfx'] = keep
            if not keep: del c['sfx']
        secs = len(text) * SEC_PER_CHAR; add = []; used = set(e.get('at') for e in c.get('sfx') or [] if isinstance(e, dict))
        for ch, cn, key, words in BY_HAND:
            if ch == n and c.get('n') == cn and words in re.sub(r'\s+', ' ', text):
                add.append(P([('key', key), ('at', words), ('by', 'place-players')])); used.add(words)
        for g, (gap, kinds) in groups.items():
            since[g] += secs
            if since[g] < gap or len(add) >= 2: continue
            k = key_for(rnd.choices([a for a, w in kinds], [w for a, w in kinds])[0], tod, rnd)
            if not k: since[g] = 0; continue
            p = phrase(text, rnd, used)
            if not p: continue
            add.append(P([('key', k), ('at', p), ('by', 'place-players')])); used.add(p)
            since[g] = rnd.uniform(-0.3, 0.3) * gap
        if add:
            c['sfx'] = (c.get('sfx') or []) + add
            for a in add: total[a['key'].rstrip('0123456789').rstrip('_')] += 1
    open(path, 'w').write(json.dumps(d, indent=1, ensure_ascii=False) + ('\n' if raw.endswith('\n') else ''))

# the sound sheet learns the players' names
f = snd['files']; f.setdefault('sfx_levels', {})
LEVEL = {'voices_far': 0.6, 'insects_day': 0.5, 'insects_night': 0.5, 'rigging': 0.6, 'trees': 0.7, 'wave': 0.75}
for prefix, cnt in pl.items():
    for i in range(1, cnt + 1):
        key = '%s_%d' % (prefix, i); f['oneshots'][key] = '%s-%d.mp3' % (prefix.replace('_', '-'), i)
        f['sfx_levels'].setdefault(key, LEVEL.get(prefix, 0.7))
for key in ('bird_cry_1', 'map_unfold', 'map_fold', 'horse_come_go', 'horses_arrive', 'horses_trot_away'):
    f['oneshots'][key] = key.replace('_', '-').replace('bird-cry-1', 'bird-cry-1') + '.mp3'
    f['sfx_levels'].setdefault(key, 0.85)
json.dump(snd, open('sound.json', 'w'), indent=2, ensure_ascii=False); open('sound.json', 'a').write('\n')
print('placed:', dict(sorted(total.items())), '· total', sum(total.values()), '· night gulls removed', gulls_cut)
