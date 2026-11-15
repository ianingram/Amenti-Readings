#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Third (chapters 31-45): the new rooms · 15 Nov 2026.
  escort-road.mp3      Darnay's ride to Paris under escort: horses at a walk in deep mire, rain, wind
  prison.mp3           La Force and the Conciergerie: stone passages, doors clanging and locking far off,
                       keys, a footstep, water dropping
  prison-hall.mp3      the large, low, vaulted chamber where the prisoners sit: quiet talk under stone
  cell.mp3             a solitary cell: the roar of the city like muffled drums, a swell of voices
  grindstone.mp3       the courtyard of Tellson's in Paris: the grindstone whirling and spluttering, the
                       throng round it
  winter-street.mp3    the street by the prison wall in winter: wind, the wood-sawyer's saw, the city
                       hushed by snow
  carmagnole.mp3       the Carmagnole: a crowd dancing and shouting, feet stamping in time
  tribunal.mp3         the Revolutionary Tribunal: a rough crowd packed into the hall. 1 a murmur,
                       2 an uproar, 3 hushed
  seine-dawn.mp3       the bridge over the Seine at dawn: the water splashing the river-walls, birds
  tumbrils.mp3         the death-carts in the streets: wheels rumbling hollow and harsh, axles
                       creaking, horses at a walk, the crowd lining the way
  execution.mp3        the place of execution: a great crowd murmuring and pressing in
Real recordings only (BigSoundBank, CC0 — numbers in sound/SOURCES.md). The helpers are those of
build-rooms-b2b.py. Nothing in a room repeats inside its 60 s; the seam is crossfaded.
usage: build-rooms-b3.py <out dir> <bsb dir> [more bsb dirs …]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'build-rooms-b2b.py')).read().split('\nprotest = cat(')[0].split('"""', 2)[2])
R = np.random.default_rng(1793)

protest = cat('2980', '2982', '3382', '0108', '2981', '2983', '3383', '3385', '3386', '3389', '3390', '3391')
crowd = cat('3515', '3516'); shouts = cat('0236', '0237'); talk = cat('2968', '2969')
leaves = load('0659'); night = load('0315'); rolls = [fade(load(n), 0.01, 0.6) for n in ('2402', '2405', '2408')]
steps = cat('1318', '1319'); stone_steps = load('0606')
clang = [fade(load(n), 0.005, 0.4) for n in ('0359', '0360', '0361')]
keys = cat('0378', '2414', '2425', '2426', '0445')
drips = cat('1386', '1387')
def stone(x, secs=2.6, wet=0.55): return reverb(x, secs, wet, 0.04, 2600)

# --- the escort on the mire-deep roads, by night and in rain -----------------------------------
def walking(n, horses=3):
    """Horses at a steady walk, close by, not passing: each keeps its own stride and place."""
    out = np.zeros((n, 2), np.float32)
    for h in range(horses):
        stride = R.uniform(1.15, 1.3); pan = (-0.6, 0.1, 0.6)[h % 3]; t = R.uniform(0, 1)
        while t < n / SR:
            for ph in (0, 0.25, 0.5, 0.75):
                put(out, pitch(hoof[R.integers(len(hoof))], R.uniform(-3, -1)), t + ph * stride + R.normal(0, 0.02), db(R.uniform(-6, 0)), pan)
            t += stride * R.uniform(0.97, 1.03)
    return out
mire = tame(lp(walking(T), 900), 10)                               # hooves sunk in mud: dull, no ring
rain = texture(load('1019'), T, (5, 10), 1.5)
er = norm(mire, -30) + norm(rain, -29) + norm(lp(texture(leaves, T, (6, 12), 1.5), 1800), -34)
save(loop(er), 'escort-road.mp3')

# --- the prison: stone passages ----------------------------------------------------------------
pr = np.zeros((T, 2), np.float32)
pr += norm(stone(lp(drop(clang, T, (7, 15), (-12, -2), 0.9), 2500), 3.0, 0.6), -40)
pr += norm(stone(lp(scatter(keys, T, (9, 18), (0.8, 2.0), (-12, -3), 0.9, (0.05, 0.3)), 3500), 2.5, 0.5), -42)
pr += norm(stone(lp(scatter(stone_steps, T, (8, 16), (2, 4), (-12, -4), 0.9, (0.3, 0.6)), 3000), 2.5, 0.6), -42)
pr += norm(stone(lp(scatter(drips, T, (1.5, 4), (0.6, 1.4), (-14, 0), 0.6, (0.05, 0.3)), 4000), 2.0, 0.5), -42)
pr += norm(lp(texture(protest, T, (4, 8), 1.0), 300), -48)          # the city, very far, through walls
save(loop(pr), 'prison.mp3')

# --- the vaulted chamber where the prisoners are ----------------------------------------------------
hall = stone(lp(hp(texture(crowd, T, (4, 8), 1.0), 180), 2200), 2.2, 0.5)
save(loop(norm(hall, -33) + norm(pr, -40)), 'prison-hall.mp3')

# --- a solitary cell: the roar of the city like muffled drums --------------------------------------
city = lp(hp(grains(protest, T, (0.8, 2.0), 4), 100), 500)
mdrums = lp(drop(rolls, T, (3, 7), (-8, 0), 0.6), 400)
swells = np.sin(np.linspace(0, 2 * np.pi * 3, T)) * 0.35 + 1.0     # a wild swell of voices, three times a minute
cl = (norm(city, -34) + norm(mdrums, -36)) * swells[:, None] + norm(stone(lp(scatter(drips, T, (3, 7), (0.6, 1.4), (-14, 0), 0.4, (0.05, 0.3)), 4000), 1.6, 0.5), -44)
save(loop(cl), 'cell.mp3')

# --- the grindstone in the courtyard ----------------------------------------------------------------
scr = [fade(load(n), 0.005, 0.15) for n in ('0327', '0328', '0329', '0330', '0331', '0332')]
whet = load('0832'); wheel = load('2768')
def grinding(n, rate=(2.2, 2.9), spells=((0, 60),)):
    """The stone whirled madly by two men: a scrape at every turn, sparks of a splutter, the axle."""
    out = np.zeros((n, 2), np.float32); t = 0.0
    while t < n / SR:
        r = R.uniform(*rate); put(out, pitch(scr[R.integers(len(scr))], R.uniform(-4, 1)), t, db(R.uniform(-5, 0)), R.uniform(-0.2, 0.2))
        if R.random() < 0.15: put(out, fade(whet[R.integers(0, len(whet) - SR):][: int(0.4 * SR)], 0.01, 0.2), t, db(-6), 0.1)
        t += 1 / r
    return out
gs = norm(grinding(T), -27) + norm(lp(texture(wheel, T, (4, 8), 1.0), 1500), -34) \
   + norm(lp(hp(grains(protest, T, (0.5, 1.4), 3), 150), 2400), -29) + norm(lp(scatter(shouts, T, (3, 7), (0.6, 1.4), (-10, -2), 0.8, (0.05, 0.3)), 2600), -34)
save(loop(reverb(gs, 1.2, 0.25, 0.02, 4000)), 'grindstone.mp3')

# --- the winter street by the prison wall ------------------------------------------------------------
saw = load('0559')
sawing = scatter(saw, T, (8, 16), (3, 6), (-6, 0), 0.4, (0.2, 0.4))   # the wood-sawyer at work now and then
ws = norm(lp(texture(leaves, T, (6, 12), 1.5), 1400), -33) + norm(lp(sawing, 4500), -35) + norm(lp(texture(talk, T, (5, 9), 1.0), 700), -44)
save(loop(ws), 'winter-street.mp3')

# --- the Carmagnole ----------------------------------------------------------------------------------
st = []
for o in onsets(steps.mean(1), -26, 0.15):
    s = steps[max(0, o - 100): o + int(0.2 * SR)]
    if len(s) > 0.18 * SR: st.append(fade(s / (np.abs(s).max() + 1e-9), 0.001, 0.12))
stamp = np.zeros((T, 2), np.float32); beat = 60 / 132                  # five hundred people dancing: stamps in time, ragged
for b in range(int(T / SR / beat)):
    for k in range(R.integers(5, 10)):
        put(stamp, pitch(st[R.integers(len(st))], R.uniform(-5, -1)), b * beat + R.normal(0, 0.03), db(R.uniform(-8, 0) + (2 if b % 2 == 0 else -2)), R.uniform(-0.9, 0.9))
cg = norm(lp(stamp, 2500), -27) + norm(lp(hp(grains(protest, T, (0.4, 1.1), 6), 150), 2800), -25) \
   + norm(lp(scatter(shouts, T, (1, 3), (0.5, 1.2), (-8, 0), 0.9, (0.05, 0.2)), 3000), -30)
save(loop(cg), 'carmagnole.mp3')

# --- the Revolutionary Tribunal ----------------------------------------------------------------------
tb = stone(lp(hp(texture(crowd, T, (3, 7), 0.8) + 0.6 * grains(protest, T, (0.6, 1.6), 3), 150), 3000), 2.0, 0.4)
save(loop(norm(tb, -24)), 'tribunal.mp3')

# --- the Seine at dawn ---------------------------------------------------------------------------------
river = lp(texture(cat('3132', '3134'), T, (6, 12), 1.5), 2200)
birds = hp(scatter(cat('0222', '0999'), T, (4, 9), (2, 5), (-8, 0), 0.9, (0.4, 0.8)), 900)
save(loop(norm(river, -30) + norm(lp(birds, 6000), -36)), 'seine-dawn.mp3')

# --- the tumbrils --------------------------------------------------------------------------------------
axle = cat('2516', '2517', '2518', '2519')
creak = lp(texture(axle, T, (3, 6), 0.8), 1800)                        # wooden axles complaining
rumble = lp(texture(load('1316'), T, (4, 8), 1.0), 700)                # wheels hollow and harsh on the stones
tb_h = lp(walking(T, 2), 1800)
lining = lp(hp(texture(crowd, T, (3, 6), 0.8), 160), 2200)
tm = norm(rumble, -27) + norm(creak, -33) + norm(tb_h, -33) + norm(lining, -31)
save(loop(tm), 'tumbrils.mp3')

# --- the place of execution -----------------------------------------------------------------------------
heave = np.sin(np.linspace(0, 2 * np.pi * 2, T)) * 0.25 + 1.0
ex = (norm(lp(hp(texture(crowd, T, (3, 6), 0.8), 140), 2600), -26) + norm(lp(hp(grains(protest, T, (0.8, 2.0), 3), 140), 1800), -31)) * heave[:, None]
save(loop(ex), 'execution.mp3')
