#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Second, chapters 7-18: rooms, sounds on the words, score · 15 Nov 2026.
Writes the plan into sound.json (files, beds, levels) and the cue sheets ep07-ep18 (bed, state,
sfx, score). Cue text is never touched (asserted). Every anchor must occur exactly once in its
cue (whitespace-normalised), or the script stops.
usage (from a-tale-of-two-cities/): python3 tools/sound-b2a.py"""
import json, re
ACC = 'https://ianingram.github.io/Amenti-Readings/a-christmas-carol/sound/'
DRA = 'https://ianingram.github.io/Amenti-Readings/dracula/sound/'

BEDS = {   # key: (file, note, levels by state)
 'tellsons': (ACC + 'bed-counting-house-v2.mp3', "Tellson's Bank by Temple Bar: a fire, a clock ticking, horses muffled in Fleet Street (A Christmas Carol's counting-house).", {1: 0.45}),
 'cruncher': (ACC + 'bed-yard-v2.mp3', "Mr. Cruncher's lodging in Hanging-sword-alley on a windy March morning (A Christmas Carol's yard, held low).", {1: 0.4}),
 'fleet_street': ('fleet-street.mp3', 'Fleet Street by day, 1780: horses at a walk going by, wheels, people talking, quick steps (built for this book).', {1: 0.9, 2: 1.0}),
 'court': ('old-bailey.mp3', 'The Old Bailey: a packed hall under a high ceiling. 1 the court murmuring, 2 a buzz or a stir, 3 hushed for the evidence, 4 the passages below, far off (built for this book).', {1: 0.7, 2: 1.0, 3: 0.3, 4: 0.16}),
 'london_night': (ACC + 'bed-street-fog-v2.mp3', 'A London street at night (A Christmas Carol\'s street, held low).', {1: 0.4}),
 'tavern': (ACC + 'bed-tavern-v2.mp3', 'A Fleet Street tavern: 1 the house busy, 2 late, nearly empty (A Christmas Carol\'s tavern).', {1: 0.5, 2: 0.22}),
 'chambers': (ACC + 'bed-chambers-v2.mp3', "Stryver's chambers in the Temple: a blazing fire, a clock (A Christmas Carol's chambers).", {1: 0.5}),
 'river_dawn': (DRA + 'wind.mp3', 'Dawn by the river, cold and sad: the wind off the water (Dracula\'s wind, low).', {1: 0.4}),
 'soho': ('soho-corner.mp3', "The Doctor's quiet corner in Soho: the plane tree's leaves, birds, the city far off. 1 a fine afternoon, 2 the sultry evening, windows open (built for this book).", {1: 1.0, 2: 0.6}),
 'storm': ('storm.mp3', 'The storm over Soho: the rush and roar of rain, thunder rolling inside it (built for this book).', {1: 1.0}),
 'after_rain': ('after-rain.mp3', 'The night after the storm: wet quiet, dripping (built for this book).', {1: 0.9}),
 'salon': ('salon.mp3', "Monseigneur's reception in his grand hotel in Paris: a crowd of fine people in a great room, glasses (built for this book).", {1: 0.9}),
 'paris_fountain': ('paris-fountain.mp3', 'The Paris street corner by the fountain: the street, the water running (built for this book).', {1: 0.8}),
 'coach_dusk': ('coach-dusk.mp3', "The Marquis's travelling carriage on the hills at sunset: Book the First's coach, evening birds. 1 driving, 2 far off as the story looks away (built for this book).", {1: 0.8, 2: 0.4}),
 'village': ('village-evening.mp3', 'The poor village: its one fountain, birds, voices far off (built for this book).', {1: 1.0}),
 'chateau_night': ('chateau-night.mp3', 'The chateau at night: the fountain dropping into its stone basin, owls, insects. 1 the courtyard, 2 heard from inside through an open window (built for this book).', {1: 1.0, 2: 0.45}),
 'chateau_dawn': ('chateau-dawn.mp3', 'The chateau at sunrise: the birds waking, the fountain (built for this book).', {1: 1.0}),
}
ONESHOTS = {   # key: (file, level)
 'hand_bell': ('hand-bell.mp3', 0.45), 'church_one': ('church-one.mp3', 0.55), 'thunder_far': ('thunder-far.mp3', 0.5),
 'thunder_crash': ('thunder-crash.mp3', 0.75), 'rain_drops': ('rain-drops.mp3', 0.45), 'steps_echo': ('steps-echo.mp3', 0.5),
 'steps_rush': ('steps-rush.mp3', 0.6), 'chateau_bell': ('chateau-bell.mp3', 0.45), 'owl': ('owl.mp3', 0.4),
 'horses_stable': ('horses-stable.mp3', 0.4), 'coin': ('coin.mp3', 0.5),
 'door_bell': (ACC + 'door-bell-v2.mp3', 0.45), 'poke_fire': (ACC + 'poke-fire-v2.mp3', 0.45),
 'glass_smash': (DRA + 'glass-crash.mp3', 0.45), 'door_clang': (DRA + 'door_heavy.mp3', 0.55), 'horse_neigh': (DRA + 'horse-neigh.mp3', 0.5),
}
SCORE = {'bailey': 'score-bailey.mp3', 'carton': 'score-carton.mp3', 'monseigneur': 'score-monseigneur.mp3'}

CH = {   # chapter: (opening bed, state, score, lead)
 7: ('tellsons', 1, 'period', 16), 8: ('tellsons', 1, 'bailey', None), 9: ('court', 3, 'bailey', None),
 10: ('court', 4, 'carton', None), 11: ('tavern', 2, 'carton', None), 12: ('soho', 1, 'tender', None),
 13: ('salon', 1, 'monseigneur', None), 14: ('coach_dusk', 1, 'monseigneur', None), 15: ('chateau_night', 1, 'monseigneur', None),
 16: ('soho', 1, 'tender', None), 17: ('chambers', 1, 'carton', None), 18: ('fleet_street', 1, 'period', None),
}
ROOM = {   # (chapter, cue): (bed, state) — a bed of None keeps the room and changes its level
 (7, 12): ('cruncher', 1), (7, 52): ('fleet_street', 1),
 (8, 44): ('fleet_street', 2), (8, 48): ('court', 1), (8, 71): (None, 2), (8, 75): (None, 3),
 (9, 4): (None, 2), (9, 5): (None, 3), (9, 119): (None, 1), (9, 141): (None, 4), (9, 153): ('fleet_street', 2),
 (10, 35): ('london_night', 1), (10, 68): ('tavern', 1), (10, 122): (None, 2),
 (11, 15): ('london_night', 1), (11, 16): ('chambers', 1), (11, 88): ('river_dawn', 1),
 (12, 148): (None, 2), (12, 175): ('storm', 1), (12, 176): ('after_rain', 1),
 (13, 26): ('coach_night', 1), (13, 28): ('paris_fountain', 1), (13, 71): ('coach_night', 1),
 (14, 11): ('village', 1), (14, 52): ('coach_dusk', 1), (14, 71): (None, 2), (14, 72): ('chateau_night', 1),
 (15, 6): (None, 2), (15, 180): (None, 1), (15, 183): ('chateau_dawn', 1), (15, 184): ('village', 1), (15, 185): ('chateau_dawn', 1), (15, 188): ('village', 1),
 (18, 8): ('tellsons', 1), (18, 121): ('chambers', 1), (18, 146): ('london_night', 1),
}
SFX = [   # (chapter, cue, key, anchor: the sound lands at the end of these words)
 (7, 6, 'door_open', 'with a weak rattle in its throat'),
 (8, 48, 'door_open', 'the door grudgingly turned on its hinges'),
 (10, 35, 'door_clang', 'closed with a jar and a rattle'),
 (10, 82, 'glass_smash', 'where it shivered to pieces'), (10, 82, 'hand_bell', 'then, rang the bell'),
 (10, 106, 'hand_bell', 'rising to ring the bell'),
 (11, 15, 'poke_fire', 'stirring the fire continuously'), (11, 16, 'door_open', 'the Stryver principal opened the door'),
 (12, 9, 'door_bell', 'when he rang the door-bell'),
 (12, 144, 'rain_drops', 'There are large drops of rain falling'),
 (12, 148, 'thunder_far', 'some of the thunder-gusts that whirled into the corner'),
 (12, 155, 'steps_echo', 'resounded with the echoes of footsteps coming and going'),
 (12, 165, 'steps_rush', 'The footsteps were incessant'),
 (12, 171, 'thunder_far', 'after there had been a vivid flash'),
 (12, 173, 'thunder_far', 'after a peal of thunder'),
 (12, 175, 'thunder_crash', 'A memorable storm of thunder and lightning broke'),
 (12, 176, 'church_one', 'was striking one in the cleared air'),
 (13, 20, 'hand_bell', 'the precious little bells went ringing downstairs'),
 (13, 26, 'horses_start', 'got into his carriage, and drove away'),
 (13, 27, 'horse_neigh', 'the horses reared and plunged'),
 (13, 28, 'horses_halt', "twenty hands at the horses’ bridles"),
 (13, 46, 'coin', 'He threw out a gold coin'),
 (13, 59, 'coin', 'throwing him another gold coin'),
 (13, 61, 'coin', 'ringing on its floor'),
 (13, 71, 'whip_crack', 'He was driven on'),
 (14, 13, 'whip_crack', "the cracking of his postilions’ whips"),
 (14, 13, 'horses_halt', 'drew up in his travelling carriage at the posting-house gate'),
 (14, 51, 'horses_start', 'the wheels turned so suddenly'),
 (14, 70, 'whip_crack', 'the postilions had quickened the pace'),
 (14, 72, 'horses_halt', 'as his carriage stopped'), (14, 72, 'door_open', 'the great door of his chateau was opened to him'),
 (15, 4, 'owl', 'loud remonstrance from an owl'),
 (15, 5, 'door_clang', 'The great door clanged behind him'),
 (15, 25, 'horses_halt', 'came up to the front of the chateau'),
 (15, 128, 'hand_bell', 'after ringing a small bell on the table'),
 (15, 172, 'hand_bell', 'before he rang his little bell again'),
 (15, 180, 'horses_stable', 'the horses in the stables rattled at their racks'), (15, 180, 'owl', 'and the owl made a noise'),
 (15, 186, 'chateau_bell', 'the ringing of the great bell of the chateau'),
 (15, 186, 'horse_gallop', 'the quick saddling of horses and riding away'),
 (16, 115, 'shoe_hammer_1', 'she heard a low hammering sound in his bedroom'),
 (16, 117, 'knock', 'tapped at his door'),
 (18, 7, 'door_open', 'he pushed open the door with the weak rattle in its throat'),
 (18, 146, 'door_close', 'Mr. Lorry was out in the night'),
]
CUE_SCORE = [   # (chapter, cue, mood or None, anchor or None, crossfade s)
 (10, 3, None, None, 6),                     # the trial is over: silence in the passages until Carton steps out
 (10, 36, 'carton', 'Another person, who had not joined the group', 8),
 (12, 139, 'recalled', None, 8),             # Darnay's story of the dungeon in the Tower: the Doctor's old horror
 (12, 155, 'hunger', 'There was a great hurry in the streets', 9),   # the footsteps: the crowd that is coming
 (12, 176, 'tender', None, 9),
 (13, 27, 'hunger', 'With a wild rattle and clatter', 6),
 (14, 11, 'hunger', None, 8), (14, 52, 'monseigneur', None, 8),
 (15, 180, 'hunger', None, 9), (15, 183, 'tender', 'Lighter and lighter', 9), (15, 186, 'hunger', 'Surely, not so the ringing', 6),
 (16, 40, 'recalled', None, 8), (16, 108, 'tender', None, 8), (16, 115, 'recalled', 'a low hammering sound', 6),
 (18, 121, 'carton', None, 8),
]
WS = lambda s: re.sub(r'\s+', ' ', s)

s = json.load(open('sound.json')); f = s['files']
for k, (url, note, lv) in BEDS.items():
    f['beds'][k] = url; s['beds'][k] = {'note': note, 'levels': {str(a): b for a, b in lv.items()}}
for k, (url, lv) in ONESHOTS.items(): f['oneshots'][k] = url; f['sfx_levels'][k] = lv
for k, url in SCORE.items(): f['score'][k] = url; f['levels'][k] = 0.38
for c in s['chapters']:
    if c['n'] in CH:
        bed, st, sc, lead = CH[c['n']]; c.update(bed=bed, state=st, score=sc)
        if lead: c['lead'] = lead
        else: c.pop('lead', None)
s['_updated'] = '2026-11-15'
s['note'] = 'Book the First (14 Nov 2026) and Book the Second ch 7-18 (15 Nov 2026): rooms, sounds on the words and score placed.'
open('sound.json', 'w').write(json.dumps(s, ensure_ascii=False, indent=2) + '\n')

known = set(f['beds']) | {None}
for n in range(7, 19):
    p = 'ep%02d.json' % n; e = json.load(open(p)); before = [c['text'] for c in e['cues']]
    cues = {c['n']: c for c in e['cues']}
    for c in e['cues']:
        for k in ('bed', 'state', 'sfx', 'score'): c.pop(k, None)        # this script owns these fields for ch 7-18
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
