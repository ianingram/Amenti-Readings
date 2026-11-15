# A Tale of Two Cities: sound sources

Every recording is CC0 or public domain, or is our own build from such recordings.

## Rooms built for this book (`build-rooms.py`, 14 Nov 2026)
- **coach-night.mp3**:
  - BigSoundBank #0610 and #0611 (horse hooves): the strikes;
  - #1316 (wheels);
  - #2516 and #2517 (squeaks, pitched down as leather springs);
  - Dracula's `wind.mp3`.
- **dover-beach.mp3**: BigSoundBank #2570 (cliff), #1445 (small waves, rocks and beach), #2573 (gulls on the harbour).

BigSoundBank (bigsoundbank.com) releases all its sounds under CC0.

## Rooms borrowed from other productions
- Dracula: `wind.mp3`, `fire.mp3`.
- A Christmas Carol: `bed-street-fog-v2.mp3`, `bed-tavern-v2.mp3`, `bed-yard-v2.mp3`.

Their sources are listed in those productions' SOURCES.md.

## One-shots built for Book the First (`build-oneshots.py`)
- **whip-crack.mp3**: BigSoundBank #2949.
- **horse-snort.mp3**: #0285 and #0286.
- **shoe-hammer-1.mp3, shoe-hammer-2.mp3**: #0005 and #0006 (nail and hammer).
- **pocket-watch.mp3**: #1372.

Borrowed by URL:
- Treasure Island: the horses arriving, trotting away, coming and going; the body fall.
- Dracula: the gallop, the cart, the door, the stairs.
- A Christmas Carol: door, window, steps, key.
- Julius Caesar: the stalls overturned (the cask), the crowd's laughter.
- Quo Vadis: the splash (the wine).
- Romeo and Juliet: the knock.

## Score (`build-moods.py`)
Mood strings in 4/4 with light percussion, built with Treasure Island's mood builder from VSCO 2 Community Edition samples (Versilian Studios, CC0):
- **score-period.mp3**: the overture; 32 s before chapter I's first words.
- **score-road.mp3**
- **score-tender.mp3**
- **score-hunger.mp3**
- **score-recalled.mp3**

The book's theme, "Recalled to Life", is a rising four-note figure carried by the violins in every mood.

## Short endings (`tools/splice.py`, 15 Nov 2026)
`tc-chNN-cueNNN-v1.mp3` are the cast voice, re-rendered inside a longer clause (`tools/sampler/tc-fixes-b1.json`), cut back to the book's words, spliced to the cached pieces and checked by transcription.
