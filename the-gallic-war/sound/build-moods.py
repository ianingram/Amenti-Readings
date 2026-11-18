#!/usr/bin/env python3
"""The Gallic War: the score · 18 Nov 2026.
Built on the shared mood-strings engine (treasure-island/sound/build-moods.py; VSCO 2 CE, CC0), as Two Cities is.
The book's figure is a falling-then-rising fourth, "Veni" (root, fourth below, root, fifth above), heard in every mood:
  march  : the legion on the road, D minor in march time, side drum and bass drum on the step
  gaul   : the Gauls, their forests and rivers; A dorian over a drone, a frame-drum pulse, the figure in the violins
  camp   : the camp at night, councils and waiting; F major, slow, only a soft roll at the phrase
  battle : the line closing; C minor, fast, timpani and a roll into every other bar
Caesar's own theme from the Julius Caesar production (score-caesar) and its Philippi are reused for councils and the big fights.
usage: build-moods.py [out dir] [mood …]   (writes score-<name>.mp3)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = (sys.argv[1] if len(sys.argv) > 1 else HERE).rstrip('/') + '/'
ONLY = sys.argv[2:]
TI = os.path.join(HERE, '..', '..', 'treasure-island', 'sound', 'build-moods.py')
src = open(TI).read().split('ARGS = sys.argv[2:]')[0]
src = src.replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.dirname(os.path.abspath(TI))))
src = src.replace("'title=Treasure Island mood strings: '", "'title=The Gallic War score: '")
sys.argv = [sys.argv[0], OUT]; exec(src)

def veni(bar, root, beats=(1.0, 1.0, 2.0, 4.0)):
    notes = [root, root - 5, root, root + 7]; out = []; b, bt = bar, 0.0
    for m, d in zip(notes, beats):
        out.append((b, bt, m, d)); bt += d
        while bt >= 4: bt -= 4; b += 1
    return out
def p_march(b, nb, bass, beat):                 # the legion's step: bass drum on 1 and 3, side drum on 2 and 4, a roll into the phrase
    out = [(BD(2, 1 + b % 2) * 1.1, 0), (SNARE(3, 1 + b % 2) * 0.55, beat), (BD(1, 2) * 0.8, 2 * beat), (SNARE(1, 2 - b % 2) * 0.5, 3 * beat)]
    if b % 4 == 3: out.append((kit('Snare2-rollNS_v1_rr1_Sum.wav')[: int(beat * SR)] * np.linspace(0.2, 0.7, int(beat * SR)), 3 * beat))
    return out
def p_gaul(b, nb, bass, beat):                  # a frame drum, uneven, far off
    out = [(BD(1, 1 + b % 2) * 0.8, 0), (TAP(1, 1 + b % 2) * 0.5, 1.5 * beat), (BD(1, 2) * 0.55, 2.5 * beat)]
    if b % 4 == 3: out.append((timp(max(40, bass if bass <= 53 else bass - 12), 0.6), 3 * beat))
    return out
def p_battle(b, nb, bass, beat):
    out = [(timp(max(40, bass if bass <= 53 else bass - 12), 0.85), 0), (BD(2, 1 + b % 2) * 1.2, 2 * beat)]
    out += [(TAP(1, 1 + (b + i) % 2) * 0.5, (i + 0.5) * beat) for i in range(4)]
    if b % 2 == 1: out.append((kit('Snare2-rollNS_v1_rr1_Sum.wav')[: int(2 * beat * SR)] * np.linspace(0.2, 0.9, int(2 * beat * SR)), 2 * beat))
    return out
MOODS = {
    'march': dict(bpm=92, chords='Dm Dm Bb C Dm Gm A A Bb Gm Dm A Gm Bb A Dm'.split(), pulse=[(0, 0, 0.55), (1, 2, 0.3), (2, 0, 0.5), (3, 2, 0.3)],
                  perc=p_march, top=veni(0, 74) + veni(8, 74)),
    'gaul': dict(bpm=70, chords='Am G Am D Am G C D Am G Am D C G Am Am'.split(), pulse=[(0, 0, 0.5), (2, 2, 0.35)], perc=p_gaul,
                 top=veni(4, 76) + veni(12, 76), lo=50, hi=76),
    'camp': dict(bpm=60, chords='F Dm Bb C F Am Bb C Gm Bb F C Dm Bb C F'.split(), pulse=[(0, 0, 0.4)], perc=p_sorrow, top=veni(12, 77)),
    'battle': dict(bpm=108, chords='Cm Cm Ab G Cm Fm G G Ab Fm Cm G Fm Ab G Cm'.split(), pulse=[(0, 0, 0.6), (1, 0, 0.4), (2, 0, 0.55), (3, 0, 0.4)],
                   perc=p_battle, top=veni(8, 72)),
}
for name, kw in MOODS.items():
    if ONLY and name not in ONLY: continue
    mood(name, **kw)
    os.replace(OUT + 'mood-%s.mp3' % name, OUT + 'score-%s.mp3' % name)
