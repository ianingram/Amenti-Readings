#!/usr/bin/env python3
"""A Tale of Two Cities: the score for Books the First and Second · 14–15 Nov 2026.
Built the way Ian approved for Treasure Island: mood strings in 4/4 with light percussion,
made to sit under the voice and loop (treasure-island/sound/build-moods.py does the work;
VSCO 2 CE, CC0). The book's own theme is a rising four-note figure, "Recalled to Life"
(fifth, root, second, third), heard in the overture and carried by the violins in every
mood, so the motif returns through the book.
usage: build-moods.py [out dir] [mood …]   (writes score-<name>.mp3)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = (sys.argv[1] if len(sys.argv) > 1 else HERE).rstrip('/') + '/'
ONLY = sys.argv[2:]
TI = os.path.join(HERE, '..', '..', 'treasure-island', 'sound', 'build-moods.py')
src = open(TI).read().split('ARGS = sys.argv[2:]')[0]
src = src.replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.dirname(os.path.abspath(TI))))
src = src.replace("'title=Treasure Island mood strings: '", "'title=A Tale of Two Cities score: '")
sys.argv = [sys.argv[0], OUT]; exec(src)

def motif(bar, root_midi, minor=False, beats=(1.5, 1.0, 1.0, 4.5)):
    """Recalled to Life: fifth below, root, second, third: rising, the last note held."""
    third = 3 if minor else 4; notes = [root_midi - 5, root_midi, root_midi + 2, root_midi + third]
    out = []; b, bt = bar, 0.0
    for m, d in zip(notes, beats):
        out.append((b, bt, m, d)); bt += d
        while bt >= 4: bt -= 4; b += 1
    return out
def p_hunger(b, nb, bass, beat):                # Saint Antoine: a muffled drum far off, the Revolution not yet come
    out = [(BD(2, 1 + b % 2) * 1.1, 0)]
    if b % 2 == 1: out.append((TAP(1, 1 + b % 2) * 0.55, 3 * beat)); out.append((TAP(1, 2 - b % 2) * 0.45, 3.5 * beat))
    if b % 4 == 3: out.append((kit('Snare2-rollNS_v1_rr1_Sum.wav')[: int(2 * beat * SR)] * np.linspace(0, 0.6, int(2 * beat * SR)), 2 * beat))
    return out
def p_road(b, nb, bass, beat):                  # the mail at night: a low heartbeat and a timpani at the phrase
    out = [(BD(2, 1) * 1.0, 0), (BD(1, 2) * 0.65, 0.38 * beat)]
    if b % 4 == 3: out.append((timp(max(40, bass if bass <= 53 else bass - 12), 0.7), 2 * beat))
    return out
def p_rising(b, nb, bass, beat):                # the Revolution in the streets: march drums, a roll into every other bar
    out = [(BD(2, 1 + b % 2) * 1.2, 0), (BD(1, 2) * 0.8, 2 * beat)]
    out += [(TAP(1, 1 + (b + i) % 2) * 0.45, (i + 0.5) * beat) for i in range(4)]
    if b % 2 == 1: out.append((kit('Snare2-rollNS_v1_rr1_Sum.wav')[: int(2 * beat * SR)] * np.linspace(0.2, 0.8, int(2 * beat * SR)), 2 * beat))
    if b % 4 == 3: out.append((timp(max(40, bass if bass <= 53 else bass - 12), 0.8), 3 * beat))
    return out
def p_toll(b, nb, bass, beat):                  # the Terror: a low timpani tolling each bar, a muffled roll at the phrase
    out = [(timp(max(40, bass if bass <= 53 else bass - 12), 0.75), 0), (BD(1, 1 + b % 2) * 0.5, 2 * beat)]
    if b % 4 == 3: out.append((kit('Snare2-rollNS_v1_rr1_Sum.wav')[: int(2 * beat * SR)] * np.linspace(0, 0.35, int(2 * beat * SR)), 2 * beat))
    return out

MOODS = {
    # Book the First opens: "the best of times, the worst of times": C major turning to C minor and back
    'period': dict(bpm=66, chords='C Am F G C Em F G Cm Ab Fm G Cm Ab G C'.split(), pulse=[(0, 0, 0.5), (2, 2, 0.35)],
                   perc=p_calm, top=motif(0, 72) + motif(4, 72) + motif(8, 72, True) + motif(12, 72)),
    # the Dover mail at night on Shooter's Hill: D minor, a walking pizzicato like the labouring team
    'road': dict(bpm=76, chords='Dm Dm Bb A Dm Gm A A Bb Gm Dm A Gm Bb A Dm'.split(), pulse=[(0, 0, 0.55), (1, 2, 0.3), (2, 0, 0.45), (3, 2, 0.3)],
                 perc=p_road, top=motif(8, 74, True)),
    # Mr. Lorry and Lucie at the Royal George; tenderness: F major, unhurried
    'tender': dict(bpm=64, chords='F Dm Bb C F Am Bb C Gm Bb F C Dm Bb C F'.split(), pulse=[(0, 0, 0.45)], perc=p_calm,
                   top=motif(4, 77) + motif(12, 77)),
    # Saint Antoine: hunger and the stain of the wine: E minor, the drum far off
    'hunger': dict(bpm=70, chords='Em Em C B Em Am B B C Am Em B C Am B Em'.split(), pulse=[(0, 0, 0.5), (2, 0, 0.35)],
                   perc=p_hunger, top=motif(8, 76, True)),
    # the garret, the shoemaker, the golden hair: B minor that finds D major at the end
    'recalled': dict(bpm=58, chords='Bm G D F#m G Em F# F# Bm G D A G Em A D'.split(), perc=p_sorrow,
                     top=motif(12, 74)),
    # --- Book the Second (15 Nov 2026) ---
    # the Old Bailey: a man's life on trial: G minor, a steady heartbeat under the court
    'bailey': dict(bpm=72, chords='Gm Gm Eb D Gm Cm D D Eb Cm Gm D Cm Eb D Gm'.split(), pulse=[(0, 0, 0.5), (2, 0, 0.4)],
                   perc=p_unease, top=motif(8, 74, True)),
    # Sydney Carton: waste, and what he might have been: A minor, slow, only a roll at the phrase
    'carton': dict(bpm=56, chords='Am F C G Am Dm E E F Dm Am E F G E Am'.split(), perc=p_sorrow,
                   top=motif(12, 76, True)),
    # Monseigneur: gilded and cold: E flat major turning to C minor, a crisp court pulse on every beat
    'monseigneur': dict(bpm=80, chords='Eb Cm Ab Bb Eb Gm Ab Bb Cm Ab Fm G Cm Ab Bb Eb'.split(),
                        pulse=[(0, 0, 0.45), (1, 0, 0.3), (2, 0, 0.4), (3, 0, 0.3)], perc=p_calm, top=motif(8, 75)),
    # The Revolution: the sea rises: D minor, march time, drums in the street, a roll into every other bar
    'rising': dict(bpm=96, chords='Dm Dm Bb A Dm Gm A A Bb Gm Dm A Gm Bb A Dm'.split(),
                   pulse=[(0, 0, 0.55), (1, 0, 0.35), (2, 0, 0.5), (3, 0, 0.35)], perc=p_rising, top=motif(8, 74, True)),
    # The Terror: the Tribunal and the Guillotine: C minor, slow, a timpani tolling every bar
    'terror': dict(bpm=60, chords='Cm Cm Ab G Cm Fm G G Ab Fm Cm G Fm Ab G Cm'.split(), pulse=[(0, 0, 0.5)], perc=p_toll,
                   top=motif(8, 72, True)),
    # "It is a far, far better thing": D major, a slow hymn; Recalled to Life carried through every phrase
    'farewell': dict(bpm=54, chords='D Bm G A D F#m G A Bm G D A G Em A D'.split(), pulse=[(0, 0, 0.45)], perc=p_calm,
                     top=motif(0, 74) + motif(4, 74) + motif(8, 74) + motif(12, 74)),
}
for name, kw in MOODS.items():
    if ONLY and name not in ONLY: continue
    mood(name, **kw)
    os.replace(OUT + 'mood-%s.mp3' % name, OUT + 'score-%s.mp3' % name)
