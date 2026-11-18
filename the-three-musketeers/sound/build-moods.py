#!/usr/bin/env python3
"""The Three Musketeers: the score · 18 Nov 2026.
Built the way Ian approved for Treasure Island and A Tale of Two Cities: mood strings in 4/4 with
percussion, made to sit under the voice and loop (treasure-island/sound/build-moods.py does the work;
VSCO 2 CE, CC0). The book's own theme is a leaping call, "All for one": root, fifth, octave, then
down to the sixth and fifth, heard in the title and carried by the violins through the moods.
usage: build-moods.py [out dir] [mood …]   (writes score-<name>.mp3)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = (sys.argv[1] if len(sys.argv) > 1 else HERE).rstrip('/') + '/'
ONLY = sys.argv[2:]
TI = os.path.join(HERE, '..', '..', 'treasure-island', 'sound', 'build-moods.py')
src = open(TI).read().split('ARGS = sys.argv[2:]')[0]
src = src.replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.dirname(os.path.abspath(TI))))
src = src.replace("'title=Treasure Island mood strings: '", "'title=The Three Musketeers score: '")
sys.argv = [sys.argv[0], OUT]; exec(src)

def call(bar, root, minor=False, beats=(0.5, 0.5, 1.0, 1.0, 1.0)):
    """All for one: root, fifth, octave, sixth, fifth: a leaping cavalier's call."""
    six = 8 if minor else 9; notes = [root, root + 7, root + 12, root + six, root + 7]
    out = []; b, bt = bar, 0.0
    for m, d in zip(notes, beats):
        out.append((b, bt, m, d + 0.3)); bt += d
        while bt >= 4: bt -= 4; b += 1
    return out
def p_ride(b, nb, bass, beat):                 # the Gascon road: a galloping figure in the drums, cymbal at the phrase
    out = [(BD(3, 1 + b % 2) * 0.9, 0), (BD(2, 2 - b % 2) * 0.6, 0.75 * beat), (BD(3, 1) * 0.8, 2 * beat), (BD(2, 2) * 0.55, 2.75 * beat),
           (SNARE(3, 1 + b % 2) * 0.45, beat), (SNARE(3, 2 - b % 2) * 0.5, 3 * beat), (TAP(1, 1) * 0.3, 1.5 * beat), (TAP(1, 2) * 0.3, 3.5 * beat)]
    if b % 4 == 3: out.append((kit('Snare2-rollSN_v3_rr1_Sum.wav')[: int(beat * SR)] * 0.45, 3 * beat))
    if b % 8 == 0: out.append((kit('susCymb1-hit_mp_rr%d.wav' % (1 + b % 2)) * 0.35, 0))
    return out
def p_duel(b, nb, bass, beat):                 # a quarrel at the inn: sharp side drum on the off-beats, timpani at the phrase
    out = [(BD(2, 1) * 0.7, 0), (SNARE(3, 1 + b % 2) * 0.35, 1.5 * beat), (SNARE(3, 2 - b % 2) * 0.4, 3.5 * beat)]
    if b % 4 == 3: out.append((timp(max(40, bass if bass <= 53 else bass - 12), 0.7), 2 * beat))
    return out
MOODS = {
    # the title and the road from Gascony: D major, a cavalier's gallop
    'gascony': dict(bpm=104, chords='D A Bm G D A G A D Bm G A Bm G A D'.split(), pulse=[(0, 0, 0.5), (1, 2, 0.3), (2, 0, 0.45), (3, 2, 0.3)],
                    perc=p_ride, top=call(0, 74) + call(4, 74) + call(8, 74) + call(12, 74)),
    # Meung, the affront, the man in the window: E minor, quick and sharp
    'meung': dict(bpm=92, chords='Em Em C B Em Am B B C Am Em B C Am B Em'.split(), pulse=[(0, 0, 0.55), (2, 0, 0.4)],
                  perc=p_duel, top=call(8, 76, True)),
    # the Cardinal: intrigue in the Palais-Cardinal, C minor, slow and cold
    'intrigue': dict(bpm=58, chords='Cm Cm Ab G Cm Fm G G Ab Fm Cm G Ab Fm G Cm'.split(), perc=p_dread, top=call(12, 72, True)),
    # Constance, the queen, Buckingham: F major, unhurried
    'romance': dict(bpm=62, chords='F Dm Bb C F Am Bb C Gm Bb F C Dm Bb C F'.split(), pulse=[(0, 0, 0.4)], perc=p_calm,
                    top=call(4, 77) + call(12, 77)),
}
for k, v in MOODS.items():
    if ONLY and k not in ONLY: continue
    mood(k, **v)
    os.replace(OUT + 'mood-%s.mp3' % k, OUT + 'score-%s.mp3' % k)
