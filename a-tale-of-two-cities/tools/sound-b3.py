#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Third, chapters 31-45: rooms, sounds on the words, score · 15 Nov 2026.
Writes the plan into sound.json (files, beds, levels) and the cue sheets ep31-ep45 (bed, state,
sfx, score). Cue text is never touched (asserted). Every anchor must occur exactly once in its
cue (whitespace-normalised), or the script stops.
usage (from a-tale-of-two-cities/): python3 tools/sound-b3.py"""
import json, re
FIRST, LAST = 31, 45

BEDS = {   # key: (file, note, levels by state)
 'escort_road': ('escort-road.mp3', "Darnay's ride to Paris under escort: horses at a walk in deep mire, rain, wind (built for this book).", {1: 1.0}),
 'prison': ('prison.mp3', 'La Force and the Conciergerie: stone passages, doors clanging and locking far off, keys, a footstep, water dropping (built for this book).', {1: 1.0}),
 'prison_hall': ('prison-hall.mp3', 'The large, low, vaulted chamber where the prisoners sit: quiet talk under stone (built for this book).', {1: 1.0}),
 'cell': ('cell.mp3', 'A solitary cell: the roar of the city like muffled drums, a wild swell of voices (built for this book).', {1: 1.0}),
 'grindstone': ('grindstone.mp3', "The courtyard of Tellson's in Paris: the grindstone whirling and spluttering, the throng round it. 1 seen from the window, 2 heard through the closed window, feeble and fitful (built for this book).", {1: 0.55, 2: 0.2}),
 'winter_street': ('winter-street.mp3', "The corner by the prison wall: wind, the wood-sawyer's saw now and then, the city hushed (built for this book).", {1: 1.0}),
 'carmagnole': ('carmagnole.mp3', 'The Carmagnole: a crowd dancing and shouting, feet stamping in time. 1 all round, 2 whirled away (built for this book).', {1: 0.9, 2: 0.4}),
 'tribunal': ('tribunal.mp3', 'The Revolutionary Tribunal: a rough crowd packed into the hall. 1 a murmur, 2 an uproar, 3 hushed (built for this book).', {1: 0.7, 2: 1.0, 3: 0.3}),
 'seine_dawn': ('seine-dawn.mp3', 'The bridge over the Seine at dawn: the water splashing the river-walls, birds (built for this book).', {1: 1.0}),
 'tumbrils': ('tumbrils.mp3', 'The death-carts in the streets: wheels rumbling hollow and harsh, axles creaking, horses at a walk, the crowd lining the way (built for this book).', {1: 0.8}),
 'execution': ('execution.mp3', 'The place of execution: a great crowd murmuring and pressing in. 1 the square, 2 far off as the story leaves it (built for this book).', {1: 1.0, 2: 0.3}),
}
LEVELS = {}
ONESHOTS = {   # key: (file, level)
 'blade': ('blade.mp3', 0.55), 'pistol': ('pistol.mp3', 0.6), 'door_blow': ('door-blow.mp3', 0.55), 'chains': ('chains.mp3', 0.4),
 'tumbril': ('tumbril.mp3', 0.45), 'saw': ('saw.mp3', 0.4), 'snow_step': ('snow-step.mp3', 0.5), 'clock_hour': ('clock-hour.mp3', 0.45),
 'clock_two': ('clock-two.mp3', 0.45),
}
SCORE = {'terror': 'score-terror.mp3', 'farewell': 'score-farewell.mp3'}

CH = {   # chapter: (opening bed, state, score, lead)
 31: ('escort_road', 1, 'road', None), 32: ('chambers', 1, 'bailey', None), 33: ('tellsons', 1, 'bailey', None),
 34: ('chambers', 1, 'recalled', None), 35: ('saint_antoine', 2, 'terror', None), 36: ('prison_hall', 1, 'terror', None),
 37: ('garret', 1, 'tender', None), 38: ('saint_antoine', 1, 'hunger', None), 39: ('chambers', 1, 'carton', None),
 40: ('tribunal', 3, 'recalled', None), 41: ('tribunal', 3, 'terror', None), 42: ('paris_night', 1, 'carton', None),
 43: ('prison', 1, 'terror', None), 44: ('wine_shop', 2, 'rising', None), 45: ('tumbrils', 1, 'terror', None),
}
ROOM = {   # (chapter, cue): (bed, state) — a bed of None keeps the room and changes its level
 (31, 27): ('wine_shop', 2), (31, 29): ('escort_road', 1), (31, 31): ('rising', 1), (31, 43): (None, 2), (31, 50): (None, 1),
 (31, 61): ('escort_road', 1), (31, 62): ('saint_antoine', 1), (31, 72): ('wine_shop', 2), (31, 98): ('saint_antoine', 1),
 (31, 131): ('prison', 1), (31, 152): ('prison_hall', 1), (31, 167): ('prison', 1), (31, 175): ('cell', 1),
 (32, 28): ('grindstone', 2), (32, 46): (None, 1), (32, 57): (None, 2), (32, 59): (None, 1), (32, 65): (None, 2), (32, 66): ('soho', 1),
 (33, 6): ('garret', 1), (33, 7): ('chambers', 1), (33, 36): ('garret', 1),
 (34, 17): ('saint_antoine', 2),
 (35, 12): ('winter_street', 1), (35, 41): ('carmagnole', 1), (35, 42): ('winter_street', 1), (35, 71): ('paris_night', 1), (35, 72): ('chambers', 1),
 (36, 10): ('prison', 1), (36, 13): ('tribunal', 1), (36, 45): (None, 2), (36, 48): ('rising', 2), (36, 51): ('carmagnole', 1), (36, 52): ('garret', 1),
 (38, 4): ('wine_shop', 1), (38, 10): (None, 2), (38, 95): ('chambers', 1),
 (39, 107): ('paris_night', 1), (39, 156): ('seine_dawn', 1), (39, 163): ('tribunal', 2), (39, 165): (None, 1), (39, 178): (None, 2), (39, 184): (None, 3),
 (40, 121): (None, 2),
 (41, 4): (None, 2), (41, 6): (None, 3), (41, 25): ('paris_night', 1), (41, 26): ('garret', 1),
 (42, 14): ('wine_shop', 2), (42, 90): ('wine_shop', 1), (42, 91): ('paris_night', 1), (42, 92): ('chambers', 1),
 (43, 5): ('cell', 1), (43, 127): ('prison_hall', 1), (43, 147): ('saint_antoine', 1), (43, 172): ('coach_night', 1),
 (44, 89): ('garret', 1), (44, 218): ('saint_antoine', 1),
 (45, 29): ('execution', 1), (45, 69): (None, 2),
}
SFX = [   # (chapter, cue, key, anchor: the sound lands at the end of these words)
 (31, 43, 'roar', 'At this the crowd roared approval'),
 (31, 49, 'door_clang', 'shut and barred the crazy double gates'),
 (31, 49, 'door_blow', 'The farrier struck a blow upon them with his hammer'),
 (31, 141, 'hand_bell', 'responsive to a bell she rang'),
 (31, 152, 'door_clang', 'many doors clanging and locking behind them'),
 (31, 168, 'key_lock', 'the gaoler opened a low black door'),
 (32, 28, 'door_bell', 'the bell of the great gate rang again'),
 (32, 45, 'key_lock', 'and turned the key'),
 (32, 59, 'door_bell', 'Twice more in the darkness the bell at the great gate sounded'),
 (35, 11, 'clock_two', 'As the clock struck two'),
 (35, 54, 'snow_step', 'A footstep in the snow.'),
 (35, 67, 'tumbril', 'One.'), (35, 67, 'tumbril', 'Two.'), (35, 67, 'tumbril', 'Three.'),
 (36, 18, 'hand_bell', 'The President rang his bell'),
 (36, 38, 'hand_bell', 'the President rang his bell to quiet them'),
 (36, 47, 'cheer', 'Long live the Republic!'),
 (37, 66, 'door_blow', 'a blow was struck upon the door'),
 (39, 178, 'roar', 'A great uproar took place in the court'),
 (40, 121, 'roar', 'Unanimously voted.'),
 (41, 25, 'horses_start', 'he took his seat beside the driver'),
 (42, 93, 'clock_hour', 'and the clock struck twelve'),
 (43, 17, 'clock_hour', 'Nine gone for ever'), (43, 17, 'clock_hour', 'ten gone for ever'), (43, 17, 'clock_hour', 'eleven gone for ever'),
 (43, 18, 'clock_hour', 'Twelve gone for ever.'),
 (43, 23, 'stairs', 'Footsteps in the stone passage outside the door.'),
 (43, 24, 'key_lock', 'The key was put in the lock, and turned'),
 (43, 26, 'door_close', 'The door was quickly opened and closed'),
 (43, 124, 'door_close', 'The door closed'),
 (43, 124, 'clock_two', 'until the clock struck Two'),
 (43, 179, 'horses_halt', 'our four horses are taken out'),
 (43, 180, 'horses_start', 'At length the new postilions are in their saddles'),
 (43, 190, 'horse_gallop', 'The wind is rushing after us'),
 (44, 215, 'pistol', 'struck out a flash and a crash'),
 (44, 217, 'key_lock', 'shutting and locking the door'),
 (45, 3, 'tumbril', 'the death-carts rumble, hollow and harsh'),
 (45, 29, 'clock_hour', 'The clocks are on the stroke of three'),
 (45, 44, 'blade', 'Crash!'), (45, 45, 'blade', 'Crash!'),
 (45, 68, 'blade', 'all flashes away'),
]
CUE_SCORE = [   # (chapter, cue, mood or None, anchor or None, crossfade s)
 (31, 31, 'hunger', None, 8), (31, 61, 'road', None, 8), (31, 144, 'recalled', None, 9),
 (32, 28, 'rising', 'the bell of the great gate rang again', 6), (32, 66, 'terror', None, 9),
 (33, 6, 'tender', None, 8), (33, 27, 'bailey', None, 8),
 (34, 17, 'terror', None, 9),
 (35, 12, 'tender', None, 8), (35, 41, 'rising', 'a troubled movement and a shouting coming along', 6), (35, 42, 'tender', None, 9),
 (35, 54, 'bailey', 'A footstep in the snow.', 6), (35, 67, 'terror', None, 8),
 (36, 45, 'rising', None, 6), (36, 52, 'tender', None, 9),
 (37, 66, 'terror', 'a blow was struck upon the door', 6),
 (38, 95, 'carton', None, 8),
 (39, 111, 'terror', None, 8), (39, 151, 'farewell', None, 9), (39, 163, 'terror', None, 8),
 (40, 121, 'terror', None, 6),
 (41, 23, 'carton', None, 9),
 (42, 14, 'bailey', None, 8), (42, 91, 'carton', None, 8),
 (43, 26, 'carton', None, 8), (43, 147, 'bailey', None, 8), (43, 172, 'road', None, 8),
 (44, 155, 'bailey', None, 8), (44, 215, None, None, 2), (44, 219, 'road', None, 9),
 (45, 46, 'farewell', None, 9),
]
WS = lambda s: re.sub(r'\s+', ' ', s)

s = json.load(open('sound.json')); f = s['files']
for k, (url, note, lv) in BEDS.items():
    f['beds'][k] = url; s['beds'][k] = {'note': note, 'levels': {str(a): b for a, b in lv.items()}}
for k, (url, lv) in ONESHOTS.items(): f['oneshots'][k] = url; f['sfx_levels'][k] = lv
for k, url in SCORE.items(): f['score'][k] = url; f['levels'][k] = 0.38
for k, lv in LEVELS.items():
    for a, b in lv.items(): s['beds'][k]['levels'][str(a)] = b
for c in s['chapters']:
    if c['n'] in CH:
        bed, st, sc, lead = CH[c['n']]; c.update(bed=bed, state=st, score=sc)
        if lead: c['lead'] = lead
        else: c.pop('lead', None)
s['_updated'] = '2026-11-15'
s['note'] = 'All three books (14-15 Nov 2026): rooms, sounds on the words and score placed.'
open('sound.json', 'w').write(json.dumps(s, ensure_ascii=False, indent=2) + '\n')

known = set(f['beds']) | {None}
for n in range(FIRST, LAST + 1):
    p = 'ep%02d.json' % n; e = json.load(open(p)); before = [c['text'] for c in e['cues']]
    cues = {c['n']: c for c in e['cues']}
    for c in e['cues']:
        for k in ('bed', 'state', 'sfx', 'score'): c.pop(k, None)        # this script owns these fields for ch 31-45
    for (ch, q), (bed, st) in ROOM.items():
        if ch != n: continue
        assert bed in known, bed
        if bed: cues[q]['bed'] = bed
        cues[q]['state'] = st
    for ch, q, key, at in SFX:
        if ch != n: continue
        assert key in f['oneshots'], key
        t = WS(cues[q]['text']); k = t.count(WS(at)); assert k == 1, (n, q, at, k)
        cues[q].setdefault('sfx', []).append({'key': key, 'at': at})
    for ch, q, key, at, xf in CUE_SCORE:
        if ch != n: continue
        assert key is None or key in f['score'], key
        sc = {'key': key, 'xfade': xf}
        if at:
            assert WS(cues[q]['text']).count(WS(at)) == 1, (n, q, at); sc['at'] = at
        cues[q]['score'] = sc
    assert [c['text'] for c in e['cues']] == before
    open(p, 'w').write(json.dumps(e, ensure_ascii=False, indent=1) + '\n')
    print(p, sum(1 for c in e['cues'] if 'bed' in c or 'state' in c), 'room changes,', sum(len(c.get('sfx', [])) for c in e['cues']), 'sounds,',
          sum(1 for c in e['cues'] if 'score' in c), 'score changes')
