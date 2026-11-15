#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Second, chapters 19-30: rooms, sounds on the words, score · 15 Nov 2026.
Writes the plan into sound.json (files, beds, levels) and the cue sheets ep19-ep30 (bed, state,
sfx, score). Cue text is never touched (asserted). Every anchor must occur exactly once in its
cue (whitespace-normalised), or the script stops.
usage (from a-tale-of-two-cities/): python3 tools/sound-b2b.py"""
import json, re
ACC = 'https://ianingram.github.io/Amenti-Readings/a-christmas-carol/sound/'
DRA = 'https://ianingram.github.io/Amenti-Readings/dracula/sound/'
FIRST, LAST = 19, 30

BEDS = {   # key: (file, note, levels by state)
 'funeral_mob': ('funeral-mob.mp3', "Roger Cly's funeral in Fleet Street: a jeering mob round the hearse and mourning coach, horses at a walk. 1 coming down the street, 2 all round (built for this book).", {1: 0.4, 2: 0.8}),
 'churchyard': ('churchyard.mp3', 'The churchyard in the fields at night: the night air, the grass and leaves, an owl (built for this book).', {1: 1.0}),
 'versailles': ('versailles.mp3', 'Versailles: the crowd waiting for the King and Queen, horses far off, swells of shouting. 1 waiting, 2 thinning away (built for this book).', {1: 0.9, 2: 0.45}),
 'rising': ('rising.mp3', 'Saint Antoine rising: a vast crowd seething, drums and alarm-bells far off. 1 heaving, 2 the living sea at full (built for this book).', {1: 0.7, 2: 1.0}),
 'bastille': ('bastille.mp3', 'The attack on the Bastille: the roar of the crowd, cannon, musketry, drums, bells (built for this book).', {1: 0.9}),
 'bastille_within': ('bastille-within.mp3', 'Inside the fortress: the storm outside heard only in a dull, subdued way through the stone (built for this book).', {1: 1.0}),
 'chateau_fire': ('chateau-fire.mp3', 'The chateau burning: the roar of the fire and the wind it makes, timbers cracking (built for this book).', {1: 0.75}),
 'village_fire': ('village-fire.mp3', 'The village at its fountain under the fire on the sky: the tocsin rung impatiently, people, the fire far off (built for this book).', {1: 0.9}),
 'soho_night': ('soho-night.mp3', 'The corner in Soho on a moonlit night: insects, the leaves, the city very far off (built for this book).', {1: 1.0}),
}
LEVELS = {'wine_shop': {2: 0.15}}   # extra states for rooms that already exist: 2 the shop closed or emptied
ONESHOTS = {   # key: (file, level)
 'spade': ('spade.mp3', 0.45), 'creak': ('creak.mp3', 0.4), 'wedding_bells': ('wedding-bells.mp3', 0.4),
 'bells_drums': ('bells-drums.mp3', 0.45), 'chop': ('chop.mp3', 0.45), 'cheer': ('cheer.mp3', 0.4), 'roar': ('roar.mp3', 0.5),
 'drum_jar': ('drum-jar.mp3', 0.4), 'drum_beat': ('drum-beat.mp3', 0.5), 'alarm_bells': ('alarm-bells.mp3', 0.5),
 'cannon': ('cannon.mp3', 0.6), 'volley': ('volley.mp3', 0.5), 'blaze': ('blaze.mp3', 0.45), 'tocsin': ('tocsin.mp3', 0.45),
}
SCORE = {'rising': 'score-rising.mp3'}

CH = {   # chapter: (opening bed, state, score, lead)
 19: ('london_night', 1, 'carton', None), 20: ('fleet_street', 1, 'period', None), 21: ('wine_shop', 1, 'hunger', None),
 22: ('dover_road', 1, 'hunger', None), 23: ('soho', 2, 'tender', None), 24: ('soho', 1, 'tender', None),
 25: ('soho', 1, 'recalled', None), 26: ('soho', 1, 'carton', None), 27: ('soho', 1, 'tender', None),
 28: ('saint_antoine', 1, 'hunger', None), 29: ('village', 1, 'hunger', None), 30: ('tellsons', 1, 'period', None),
}
ROOM = {   # (chapter, cue): (bed, state) — a bed of None keeps the room and changes its level
 (19, 5): ('soho', 1),
 (20, 8): ('funeral_mob', 1), (20, 23): (None, 2), (20, 52): (None, 1), (20, 53): ('soho', 1), (20, 58): ('fleet_street', 1),
 (20, 60): ('cruncher', 1), (20, 95): ('london_night', 1), (20, 97): ('churchyard', 1), (20, 103): ('cruncher', 1), (20, 121): ('fleet_street', 1),
 (21, 24): ('garret', 1), (21, 141): ('versailles', 1), (21, 155): (None, 2),
 (22, 5): ('paris_night', 1), (22, 6): ('saint_antoine', 2), (22, 27): ('wine_shop', 2), (22, 81): ('wine_shop', 1), (22, 83): (None, 2),
 (22, 220): ('saint_antoine', 1),
 (23, 3): ('soho_night', 1), (23, 53): ('soho', 1),
 (25, 124): ('soho_night', 1),
 (26, 40): ('soho_night', 1),
 (27, 25): ('soho_night', 1), (27, 53): ('rising', 1), (27, 68): ('bastille', 1), (27, 78): ('rising', 2), (27, 105): ('bastille_within', 1),
 (27, 128): ('rising', 2),
 (28, 11): ('rising', 1), (28, 38): (None, 2), (28, 52): ('saint_antoine', 2),
 (29, 52): ('chateau_night', 1), (29, 53): ('chateau_fire', 1), (29, 54): ('village', 1), (29, 56): ('village_fire', 1),
 (29, 64): ('chateau_fire', 1), (29, 65): ('village_fire', 1), (29, 68): ('village', 1),
 (30, 131): ('london_night', 1),
}
SFX = [   # (chapter, cue, key, anchor: the sound lands at the end of these words)
 (19, 58, 'door_close', 'and left her'),
 (20, 48, 'roar', 'mobbed the two vehicles so closely that they came to a stop'),
 (20, 98, 'creak', 'nimbly scaling an iron gate'),
 (20, 100, 'spade', 'They fished with a spade, at first'),
 (20, 100, 'church_one', 'the awful striking of the church clock'),
 (20, 101, 'creak', 'There was a screwing and complaining sound down below'),
 (20, 102, 'stairs', 'followed him upstairs with a bump on every stair'),
 (21, 153, 'cheer', 'Long live the King, Long live the Queen'),
 (22, 5, 'horses_halt', 'to that gate of Paris whereunto their journey naturally tended'),
 (22, 226, 'bells_drums', 'the distant beating of the military drums in the Palace Courtyard'),
 (24, 43, 'horses_start', 'took her down-stairs to the chariot'),
 (24, 43, 'wedding_bells', 'Charles Darnay and Lucie Manette were happily married'),
 (24, 53, 'shoe_hammer_1', 'he was stopped by a low sound of knocking'),
 (25, 124, 'chop', 'hacked the shoemaker’s bench to pieces'),
 (25, 124, 'poke_fire', 'commenced without delay in the kitchen fire'),
 (25, 124, 'spade', 'were buried in the garden'),
 (27, 51, 'steps_rush', 'Only hear them!'),
 (27, 53, 'roar', 'A tremendous roar arose from the throat of Saint Antoine'),
 (27, 68, 'roar', 'With a roar that sounded as if all the breath in France had been shaped into the detested word'),
 (27, 68, 'alarm_bells', 'Alarm-bells ringing'), (27, 68, 'drum_beat', 'drums beating'),
 (27, 69, 'cannon', 'eight great towers, cannon'), (27, 69, 'volley', 'muskets, fire and smoke'), (27, 69, 'cannon', 'he became a cannonier'),
 (27, 70, 'cheer', 'One drawbridge down!'),
 (27, 77, 'volley', 'shrieks, volleys'), (27, 77, 'cannon', 'boom smash and rattle'),
 (27, 78, 'cheer', 'in among the eight great towers surrendered!'),
 (27, 106, 'key_lock', 'put a key in a clashing lock'), (27, 106, 'door_open', 'swung the door slowly open'),
 (27, 128, 'blaze', 'The turnkey fired the little pile'),
 (28, 11, 'roar', 'a fast-spreading murmur came rushing along'),
 (28, 34, 'drum_jar', 'the jar of a drum was heard'),
 (28, 38, 'drum_beat', 'the drum was beating in the streets'),
 (28, 48, 'roar', 'when the cry seemed to go up, all over the city'),
 (29, 53, 'blaze', 'flames burst forth'),
 (29, 54, 'horse_gallop', 'there was a saddling of a horse and riding away'),
 (29, 54, 'horses_halt', 'the horse in a foam stood at Monsieur Gabelle’s door'),
 (29, 56, 'tocsin', 'The tocsin rang impatiently'),
 (29, 59, 'horse_gallop', 'galloped up the stony steep'),
 (29, 63, 'horse_gallop', 'As the rider rattled down the hill again'),
 (29, 66, 'door_close', 'did heavily bar his door'),
 (29, 67, 'knock', 'the beating at his door'),
 (30, 114, 'horses_halt', 'A carriage with post-horses was ready at the Bank door'),
 (30, 135, 'horses_start', 'as the carriage rolled away'),
 (30, 138, 'horse_gallop', 'took horse for Dover; and began his journey'),
]
CUE_SCORE = [   # (chapter, cue, mood or None, anchor or None, crossfade s)
 (20, 8, 'bailey', 'some kind of funeral was coming along', 8), (20, 53, 'period', None, 8),
 (20, 96, 'bailey', None, 8), (20, 121, 'period', None, 8),
 (21, 141, 'monseigneur', 'to Versailles', 8), (21, 155, 'hunger', None, 8),
 (22, 82, 'bailey', 'A figure entering at the door', 6), (22, 219, 'hunger', None, 8),
 (23, 26, 'recalled', None, 8), (23, 53, 'tender', None, 8),
 (24, 48, 'recalled', 'a great change to have come over the Doctor', 8),
 (26, 40, 'tender', None, 8),
 (27, 24, 'hunger', 'an awful sound, as of a great storm in France', 9), (27, 53, 'rising', None, 6),
 (27, 105, 'recalled', None, 9), (27, 128, 'rising', 'until they were in the raging flood once more', 8),
 (28, 38, 'rising', None, 6), (28, 52, 'hunger', None, 9),
 (29, 52, 'bailey', None, 9), (29, 53, 'rising', None, 8), (29, 67, 'hunger', 'But, the friendly dawn appearing at last', 9),
 (30, 138, 'road', None, 8),
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
s['note'] = 'Book the First (14 Nov 2026) and Book the Second (15 Nov 2026): rooms, sounds on the words and score placed.'
open('sound.json', 'w').write(json.dumps(s, ensure_ascii=False, indent=2) + '\n')

known = set(f['beds']) | {None}
for n in range(FIRST, LAST + 1):
    p = 'ep%02d.json' % n; e = json.load(open(p)); before = [c['text'] for c in e['cues']]
    cues = {c['n']: c for c in e['cues']}
    for c in e['cues']:
        for k in ('bed', 'state', 'sfx', 'score'): c.pop(k, None)        # this script owns these fields for ch 19-30
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
