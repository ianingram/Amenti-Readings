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

## Book the Second, chapters 7–18 (15 Nov 2026)
Rooms built for this book (`build-rooms-b2.py`), all BigSoundBank (CC0):
- **fleet-street.mp3**: #0610 and #0611 (hoof strikes, set at a walk going by), #1316 (wheels), #2968 and #2969 (people talking outdoors), #1318 (steps).
- **old-bailey.mp3**: #3515 and #3516 (a crowd of 50–60 people indoors), given a high hall's reverb.
- **soho-corner.mp3**: #0659 (wind in a tree), #1859 (evening birds), the Fleet Street room far off.
- **storm.mp3**: #1019 (summer rain on a terrace), #0740 (rain and storm), #2719 (storm and rain: the thunder rolls).
- **after-rain.mp3**: #0555 (night after rain), #1384 and #1385 (drops of water).
- **salon.mp3**: #3516 and #3515 (the crowd), #0472 and #1205 (glasses).
- **paris-fountain.mp3**: the Fleet Street room and #0913 (a fountain).
- **coach-dusk.mp3**: Book the First's `coach-night.mp3` and #1859 (evening birds).
- **village-evening.mp3**: #0913 (the fountain), #1859 (birds), #2968/#2969 far off.
- **chateau-night.mp3**: #1386 and #1387 (drops: the fountain into its stone basin), #0429 and #1400 (owls), #0425 and #0426 (night insects), #0315 (birds at night).
- **chateau-dawn.mp3**: #0222 and #0999 (birds waking), #0913.

One-shots built for this book (`build-oneshots-b2.py`), BigSoundBank (CC0):
- **hand-bell.mp3** #0292 · **church-one.mp3** #3446 · **thunder-far.mp3** #3114 · **thunder-crash.mp3** #3116 · **rain-drops.mp3** #1384, #1385 · **steps-echo.mp3**, **steps-rush.mp3** #1318, #1319 (the echoing corner) · **chateau-bell.mp3** #0135 · **owl.mp3** #0429 · **horses-stable.mp3** #0289 · **coin.mp3** #0193.

Borrowed by URL:
- A Christmas Carol: `bed-counting-house-v2.mp3` (Tellson's), `bed-chambers-v2.mp3` (Stryver's chambers), the tavern, the yard (Mr. Cruncher's lodging), the street (London at night), the door-bell, the poker in the fire.
- Dracula: the wind (dawn by the river), the glass breaking, the heavy door, the horse's neigh.

Score (`build-moods.py`, VSCO 2 CE, CC0): **score-bailey.mp3** (the Old Bailey), **score-carton.mp3** (Sydney Carton), **score-monseigneur.mp3** (Monseigneur and the Marquis).
