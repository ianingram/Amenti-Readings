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

## Book the Second, chapters 19–30 (15 Nov 2026)
Rooms built for this book (`build-rooms-b2b.py`), all BigSoundBank (CC0). The protest recordings (#0108, #2980–#2983, #3382–#3391, "manifestation") are French street chants: they are cut into short grains and shuffled so no words or rhythm survive.
- **funeral-mob.mp3**: the protest recordings, #3515 and #3516 (a crowd), #0236 and #0237 (shouts), #0610 and #0611 (hooves at a slow walk), #1316 (wheels).
- **churchyard.mp3**: #0315 (night), #0659 (wind in the leaves), #0429 and #1400 (owls).
- **versailles.mp3**: #3515 and #3516, #2968 and #2969 (people outdoors), #0610/#0611, #0019 (applause, far off and low-passed: the shouting).
- **rising.mp3**: the protest recordings, #3515/#3516, #2402, #2405 and #2408 (drum rolls), #0135, #0829 and #0830 (church bells), far off.
- **bastille.mp3**: all of the above, with #1023 and #1806–#1808 (explosions far off: the cannon) and #2853, #2854, #0397 and #0532 (shots: the musketry).
- **bastille-within.mp3**: the Bastille room through stone, #1386 and #1387 (drops).
- **chateau-fire.mp3**: #0987–#0989 (a big fire), #1341 and #1342 (a fire roaring), #2855–#2857 (crackling), #0659 (wind).
- **village-fire.mp3**: #0913 (the fountain), the fire far off, #0135 (the bell, struck in runs: the tocsin), #2968/#2969.
- **soho-night.mp3**: #0425 and #0426 (night insects), #0315, #0659, #2968/#2969 very far off.

One-shots built for this book (`build-oneshots-b2b.py`), BigSoundBank (CC0):
- **spade.mp3** #1305 · **creak.mp3** #0539 · **wedding-bells.mp3** #0829 · **bells-drums.mp3** #0994, #2402, #2405 · **chop.mp3** #0536 · **cheer.mp3** #0019, #0236, #0237 · **roar.mp3** the protest recordings · **drum-jar.mp3** #2400 · **drum-beat.mp3** #2408, #2404 · **alarm-bells.mp3** #0135, #0829, #0830 · **cannon.mp3** #1806 · **volley.mp3** #2853, #2854, #0397 · **blaze.mp3** #1341 · **tocsin.mp3** #0135.

Score (`build-moods.py`, VSCO 2 CE, CC0): **score-rising.mp3** (the Revolution: D minor, march time, drums in the street).

## Book the Third, chapters 31–45 (15 Nov 2026)
Rooms built for this book (`build-rooms-b3.py`, using the helpers of `build-rooms-b2b.py`), all BigSoundBank (CC0):
- **escort-road.mp3**: #0610 and #0611 (hoof strikes, at a walk, dulled as in mire), #1019 (rain), #0659 (wind).
- **prison.mp3**: #0359, #0360 and #0361 (chains: the doors clanging), #0378, #2414, #2425, #2426 and #0445 (keys and locks), #0606 (steps on a stone staircase), #1386 and #1387 (drops), the protest recordings very far off.
- **prison-hall.mp3**: #3515 and #3516 under stone, and the prison room.
- **cell.mp3**: the protest recordings and #2402, #2405 and #2408 (drum rolls), heavily low-passed: the city's roar like muffled drums.
- **grindstone.mp3**: #0327–#0332 (blades scraped on a stone, one at every turn), #0832 (a whetstone), #2768 (a mill wheel: the axle), the protest recordings, #0236/#0237.
- **winter-street.mp3**: #0659 (wind), #0559 (a saw on wood: the wood-sawyer), #2968/#2969 far off.
- **carmagnole.mp3**: #1318 and #1319 (footsteps, struck in time as stamping), the protest recordings, #0236/#0237.
- **tribunal.mp3**: #3515/#3516 and the protest recordings, under a stone hall's reverb.
- **seine-dawn.mp3**: #3132 and #3134 (a watercourse), #0222 and #0999 (birds waking).
- **tumbrils.mp3**: #1316 (wheels), #2516–#2519 (squeaking wheelbarrows: the axles), #0610/#0611 (horses at a walk), #3515/#3516 (the crowd lining the way).
- **execution.mp3**: #3515/#3516 and the protest recordings, heaving.

One-shots (`build-oneshots-b3.py`):
- **blade.mp3** #1234 (a trap snapping) and Dracula's `door_heavy.mp3` · **pistol.mp3** #0437 · **door-blow.mp3** Dracula's `door_heavy.mp3` · **chains.mp3** #0619, #0359 · **tumbril.mp3** #1316, #2517 · **saw.mp3** #0559 · **snow-step.mp3** #3363 · **clock-hour.mp3**, **clock-two.mp3** #3446.

Score (`build-moods.py`, VSCO 2 CE, CC0): **score-terror.mp3** (the Terror: C minor, a timpani tolling every bar) and **score-farewell.mp3** ("It is a far, far better thing": D major, a slow hymn with Recalled to Life in every phrase).
