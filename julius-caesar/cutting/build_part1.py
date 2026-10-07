#!/usr/bin/env python3
"""Julius Caesar, Part 1 — Acts I–III, ten scenes, one episode per scene (7 Oct 2026).
Writes julius-caesar/ep01–ep10.json, index.json (all eighteen scenes; 1–10 scripted),
sound.json, REVIEW.md, and the julius-caesar roles in cast.json (merged into the live file)."""
import json, os, re, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cut_jc as C
from cast_jc import CAST
S = '/tmp/claude-0/-home-claude/c002dc02-d023-5c73-9437-2a1012982e23/scratchpad'
OUT = HERE + '/z/julius-caesar/'; os.makedirs(OUT, exist_ok=True)
LEDGER = {r['Full Name'].lower(): r for r in csv.DictReader(open(S + '/al/names.csv', encoding='utf-8-sig'))}
ROMAN = ['I', 'II', 'III', 'IV', 'V']
R = 'https://ianingram.github.io/Amenti-Readings/'

eps = C.cut()
assert len(eps) == 18, len(eps)

# ── sound: beds, one-shots, score ──
SOUND = {
 '_file': 'Amenti-Readings/julius-caesar/sound.json', '_updated': '2026-10-07 08:30 UTC', 'work': 'julius-caesar',
 'note': ('Rome: the street and the Forum crowd; the night of portents, wind and rain and thunder; Brutus’s orchard '
          'under the crickets; Caesar’s palace at night; the senators murmuring under the Capitol’s portico. '
          'Trumpets for every flourish and sennet, a tower bell striking three, the assassination in blows, '
          'and the Forum’s great bell in G for Caesar’s death. The score is six sound worlds: CAESAR (C minor, '
          'the Colossus), CONSPIRACY (D minor, the storm night), BRUTUS (E minor, the quiet heart), FORUM '
          '(G minor, the crowd turned), GHOST (no pulse) and PHILIPPI (A minor, the battle).'),
 'files': {
  'base': R + 'julius-caesar/sound/',
  'beds': {'rome_street': R + 'quo-vadis/sound/rome-street.mp3', 'rome_night': R + 'quo-vadis/sound/rome-night.mp3',
           'palace_night': R + 'quo-vadis/sound/palace-night.mp3', 'orchard_night': R + 'romeo-and-juliet/sound/garden-night.mp3',
           'storm_night': 'storm-night.mp3', 'senate': 'senate.mp3'},
  'oneshots': {'thunder': R + 'dracula/sound/thunder.mp3', 'knock': R + 'romeo-and-juliet/sound/knock.mp3',
               'cheer': R + 'quo-vadis/sound/cheer.mp3', 'applause': R + 'quo-vadis/sound/applause.mp3',
               'flourish': 'flourish.mp3', 'sennet': 'sennet.mp3', 'clock_three': 'clock-three.mp3',
               'stabbing': 'stabbing.mp3', 'bell_toll': 'bell-toll.mp3', 'mob': 'mob.mp3'},
  'score': {'caesar': 'score-caesar.mp3', 'conspiracy': 'score-conspiracy.mp3', 'brutus': 'score-brutus.mp3',
            'forum': 'score-forum.mp3', 'ghost': 'score-ghost.mp3', 'philippi': 'score-philippi.mp3'},
  'levels': {'caesar': 0.36, 'conspiracy': 0.34, 'brutus': 0.36, 'forum': 0.38, 'ghost': 0.3, 'philippi': 0.38}},
 'beds': {}, 'chapters': []}
SOUND['beds'] = {k: {} for k in SOUND['files']['beds']}
BED = {1: 'rome_street', 2: 'rome_street', 3: 'storm_night', 4: 'orchard_night', 5: 'palace_night', 6: 'rome_street',
       7: 'rome_street', 8: 'senate', 9: 'rome_street', 10: 'rome_night'}
# (episode, anchor words, what) — the anchor is text in the cue; the first cue (from `after`) holding it gets it
def sc(key, xf, cut=False): d = {'score': {'key': key, 'xfade': xf}}; d['score'].update({'cut': True} if cut else {}); return d
def fx(*keys_offsets): return {'sfx': [dict(key=k, **({'offset': o} if o else {})) for k, o in keys_offsets]}
PLACE = [
 # I.i — a street: the tribunes scatter the holiday crowd
 (1, 'Enter Flavius, Marullus', fx(('cheer', 0.6))),
 # I.ii — the Lupercal: Caesar's music, the soothsayer, Cassius works on Brutus, the shouts offstage
 (2, 'Enter, in procession, with music', sc('caesar', 4)),
 (2, 'Music ceases.', sc(None, 3)),
 (2, 'Music.', sc('caesar', 3)),
 (2, 'Music ceases.', sc(None, 4)),
 (2, 'Sennet. Exeunt all but Brutus and Cassius.', fx(('sennet', 0))),
 (2, 'Will you go see the order of the course?', sc('brutus', 8)),
 (2, 'Flourish and shout.', fx(('flourish', 0), ('cheer', 1.2))),
 (2, 'Shout. Flourish.', fx(('cheer', 0), ('flourish', 1.4))),
 (2, 'Enter Caesar and his Train.', sc('caesar', 5)),
 (2, 'Exeunt Caesar and his Train. Casca stays.', sc(None, 6)),
 (2, 'Well, Brutus, thou art noble', sc('conspiracy', 6)),
 # I.iii — the night of portents
 (3, 'Thunder and lightning.', fx(('thunder', 0))),
 (3, 'Who ever knew the heavens menace so?', fx(('thunder', 2.0))),
 (3, 'Enter Cassius.', sc('conspiracy', 6)),
 (3, 'Thunder still.', fx(('thunder', 0))),
 (3, 'Exeunt.', sc(None, 8)),
 # II.i — Brutus's orchard
 (4, 'It must be by his death', sc('brutus', 6)),
 (4, 'Knock within.', fx(('knock', 0))),
 (4, 'Enter Cassius, Casca, Decius', sc('conspiracy', 5)),
 (4, 'Clock strikes.', fx(('clock_three', 0))),
 (4, 'Exeunt all but Brutus.', sc('brutus', 8)),
 (4, 'Knock.', fx(('knock', 0))),
 (4, 'Thunder.', fx(('thunder', 0))),
 (4, 'Exeunt.', sc(None, 8)),
 # II.ii — Caesar's house: Calpurnia's dream, Decius's reading of it
 (5, 'Thunder and lightning.', fx(('thunder', 0))),
 (5, 'Enter Calphurnia.', sc('ghost', 6)),
 (5, 'This dream is all amiss interpreted', sc('caesar', 6)),
 (5, 'Exeunt.', sc(None, 8)),
 # II.iii — Artemidorus's letter
 (6, 'Enter Artemidorus, reading a paper.', sc('conspiracy', 4)),
 (6, 'Exit.', sc(None, 6)),
 # II.iv — Portia
 (7, 'Enter Portia and Lucius.', sc('brutus', 5)),
 (7, 'Exeunt.', sc(None, 6)),
 # III.i — the ides of March
 (8, 'Flourish. Enter Caesar', {**fx(('flourish', 0)), **sc('caesar', 4)}),
 (8, 'Exeunt Antony and Trebonius.', sc('conspiracy', 5)),
 (8, 'Casca stabs Caesar in the neck', {**sc(None, 0.4, cut=True), **fx(('stabbing', 0))}),
 (8, 'Dies. The Senators and People retire in confusion.', fx(('bell_toll', 0.3), ('mob', 4.0))),
 (8, 'O mighty Caesar! Dost thou lie so low?', sc('brutus', 6)),
 (8, 'O, pardon me, thou bleeding piece of earth', sc('ghost', 6)),
 (8, 'Exeunt with Caesar’s body.', sc(None, 8)),
 # III.ii — the Forum
 (9, 'Live, Brutus! live, live!', fx(('cheer', 0.3))),
 (9, 'Enter Antony and others, with Caesar’s body.', fx(('applause', 0.5))),
 (9, 'Friends, Romans, countrymen, lend me your ears;', sc('forum', 8)),
 (9, 'If you have tears, prepare to shed them now.', sc('ghost', 6)),
 (9, 'Revenge,—about,—seek,—burn,', {**fx(('mob', 0)), **sc('forum', 3)}),
 (9, 'Exeunt Citizens, with the body.', fx(('mob', 0))),
 (9, 'Exeunt.', sc(None, 8)),
 # III.iii — Cinna the poet
 (10, 'Enter Cinna, the poet', sc('forum', 5)),
 (10, 'Tear him to pieces', fx(('mob', 0.2))),
 (10, 'Tear him, tear him! Come; brands, ho!', fx(('mob', 0))),
 (10, 'Exeunt.', sc(None, 6)),
]

def title(e):
    sc_ = e['scene']; m = re.match(r'SCENE ([IVX]+)\.\s*(.*)', sc_.replace('\n', ' '), re.S)
    return f"Act {e['act'].split()[1]}, Scene {m.group(1)} — {m.group(2).strip().rstrip('.')}", f"{e['act']} · SCENE {m.group(1)}"

roles_cast = {}
index = []
for n, e in enumerate(eps, 1):
    t, doc = title(e)
    index.append({'n': n, 'file': f'julius-caesar/ep{n:02d}.json', 'document': doc, 'summary': t,
                  'status': 'scripted' if n <= 10 else 'not yet'})
    if n > 10: continue
    cues = []
    for i, q in enumerate(e['cues'], 1):
        role, ledger, why = CAST[q['role']]
        cues.append({'n': i, 'role': role, 'cast': ledger, 'text': C.T[q['span'][0]:q['span'][1]]})
        roles_cast.setdefault(q['role'], CAST[q['role']])
    # place the sound
    used = {}
    for ep_n, anchor, what in PLACE:
        if ep_n != n: continue
        start = used.get(anchor, 0)
        hit = next((c for c in cues[start:] if anchor in c['text']), None)
        assert hit, (n, anchor)
        used[anchor] = hit['n']                       # a repeated anchor finds the next occurrence
        if 'score' in what:
            if 'score' in hit: hit['score'] = [hit['score']] if isinstance(hit['score'], dict) else hit['score']; hit['score'].append(dict(what['score'], at=anchor))
            else: hit['score'] = dict(what['score'], at=anchor)
        if 'sfx' in what:
            hit.setdefault('sfx', []).extend(dict(s, at=anchor) for s in what['sfx'])
    cast = []; seen = set()
    for c in cues:
        if (c['role'], c['cast']) not in seen: seen.add((c['role'], c['cast'])); cast.append({'role': c['role'], 'cast_as': c['cast']})
    ep = {'work': 'julius-caesar', 'episode': n, 'chapter': n, 'title': t, 'document': doc,
          'source': {'library': 'library/shakespeare-william/17-julius-caesar.md',
                     'text': 'William Shakespeare, The Tragedy of Julius Caesar · Project Gutenberg · public domain'},
          'note': ('Scene complete. One cue per speech in its speaker’s voice; every heading and stage direction is a cue '
                   'for Shakespeare. Every cue is byte-identical to the library file. The Romans play themselves.'),
          'cast': cast, 'cues': cues}
    # sound order inside a cue: score first, then sfx (as the other works write it)
    for c in cues:
        for k in ('score', 'sfx'):
            if k in c: v = c.pop(k); c[k] = v
    for c in cues:                                    # the keys in the order the player expects: n, [score/sfx], role, cast, text
        ks = ['n'] + [k for k in ('score', 'sfx') if k in c] + ['role', 'cast', 'text']
        d = {k: c[k] for k in ks}; c.clear(); c.update(d)
    json.dump(ep, open(OUT + f'ep{n:02d}.json', 'w'), ensure_ascii=False, indent=1)
    SOUND['chapters'].append({'n': n, 'bed': BED[n], 'state': 1, 'score': None})

json.dump({'work': 'julius-caesar', 'title': 'Julius Caesar', 'author': 'William Shakespeare', 'first_published': 1599,
           'source': 'library/shakespeare-william/17-julius-caesar.md in Amenti.live · public domain',
           'note': ('A play is already a cast recording: every speech carries its speaker’s name, so nothing is inferred. '
                    'Shakespeare reads every stage direction. The Romans play themselves — Caesar, Brutus, Cassius, Antony, '
                    'Octavius (Augustus), Lepidus, Cicero; Calpurnia by Venus, Portia by Zenobia; the small parts doubled, '
                    'as in Shakespeare’s own company. One episode per scene. Part One (Acts I–III) is scripted.'),
           'unit': 'scenes', 'chapters': index}, open(OUT + 'index.json', 'w'), ensure_ascii=False, indent=1)
json.dump(SOUND, open(OUT + 'sound.json', 'w'), ensure_ascii=False, indent=1)

# ── cast.json: the live file, with julius-caesar added ──
live = json.load(open(S + '/rd/cast.json'))
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower().replace('’', '').replace("'", '')).strip('-')
roles = {}
for key, (role, ledger, why) in CAST.items():                 # the whole play's cast, decided once
    r = LEDGER[ledger.lower()]
    roles[slug(role)] = {'ledger_name': ledger, 'ledger': r['Dialect'], 'why': why}
live['roles']['julius-caesar'] = roles
json.dump(live, open(HERE + '/z/cast.json', 'w'), ensure_ascii=False, indent=1)

# ── REVIEW.md ──
L = ['# Julius Caesar — attribution review', '',
     'A play: every speech is headed by its speaker, so attribution is mechanical. What was decided by hand:', '',
     '- **Cinna** in Act III, Scene III is *Cinna the poet* (Catullus), not Cinna the conspirator (Sextus Pompey) — the text uses the same heading for both.',
     '- **VARRO. CLAUDIUS.** (a line spoken by both, Act IV) is given to Varro.',
     '- Stage directions that stand alone without “Enter/Exit” — *Thunder and lightning…*, *A crowd of people…*, *Caesar enters the Capitol…* — are read by Shakespeare as directions.',
     '- The small parts are doubled (see cast.json → why).', '',
     '## Part One — Acts I–III', '']
for n in range(1, 11):
    ep = json.load(open(OUT + f'ep{n:02d}.json'))
    L.append(f"### {n:02d} · {ep['title']} — {len(ep['cues'])} cues")
    counts = {}
    for c in ep['cues']: counts[c['role']] = counts.get(c['role'], 0) + 1
    L.append(', '.join(f'{k} ({v})' for k, v in sorted(counts.items(), key=lambda x: -x[1])))
    for c in ep['cues']:
        if 'score' in c or 'sfx' in c:
            bits = []
            for s in (c['score'] if isinstance(c.get('score'), list) else [c['score']] if 'score' in c else []): bits.append(f"score → {s['key'] or 'silence'}")
            for s in c.get('sfx', []): bits.append(f"sound: {s['key']}")
            L.append(f"- cue {c['n']} · {c['role']} · “{c['text'][:60].replace(chr(10), ' ')}” · {'; '.join(bits)}")
    L.append('')
open(OUT + 'REVIEW.md', 'w').write('\n'.join(L))
print('wrote', sorted(os.listdir(OUT)))
