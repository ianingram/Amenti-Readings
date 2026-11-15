#!/usr/bin/env python3
"""A Tale of Two Cities, Book the Third (chapters 31-45): the new one-shots · 15 Nov 2026.
  blade.mp3        "Crash!": the knife of the Guillotine falling, heard from the crowd      1234, Dracula's heavy door
  pistol.mp3       "a flash and a crash": a pistol fired in a closed room                     0437
  door-blow.mp3    a blow struck upon the door                                                Dracula's heavy door
  chains.mp3       a chain dragged and dropped on stone                                       0359 0619
  tumbril.mp3      one death-cart going by: wheels on the stones, the axle complaining        1316 2517
  saw.mp3          the wood-sawyer's saw, a few strokes                                       0559
  snow-step.mp3    a footstep in the snow                                                     3363
  clock-hour.mp3   a clock striking the hour, far off over the roofs                          3446
  clock-two.mp3    the prison clock striking Two                                              3446
Real recordings only (BigSoundBank, CC0); the heavy door is Dracula's (dracula/sound/SOURCES.md).
usage: build-oneshots-b3.py <out dir> <bsb dir> [more bsb dirs …]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'build-oneshots-b2b.py')).read().split('\n# the spade:')[0].split('"""', 2)[2])
R = np.random.default_rng(1794)
def file(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
door = file(os.path.join(HERE, '..', '..', 'dracula', 'sound', 'door_heavy.mp3'))
hit = events(door, 1.2, -18, 0.3)[0]

# the Guillotine: a hard wooden snap and a heavy fall, out in the open square
snap = span(load('1234'))[: int(0.6 * SR)]
b = np.zeros((int(3 * SR), 2), np.float32); put(b, lp(snap, 5000), 0, 0.6); put(b, lp(pitch(hit, -5), 1600), 0.03, 1.0)
save(fade(reverb(b, 1.6, 0.3, 0.05, 3000), 0.001, 1.2), 'blade.mp3', -2)
# a pistol in a closed room: an old charge, duller than a modern shot, the room ringing after it
p = span(load('0437'))[: int(1.5 * SR)]
save(fade(reverb(lp(pitch(p, -3), 3500), 0.9, 0.35, 0.01, 3500), 0.001, 0.8), 'pistol.mp3', -1)
# a blow struck upon the door
save(fade(reverb(lp(pitch(hit, -2), 2500), 0.8, 0.3, 0.01, 3000), 0.001, 0.6), 'door-blow.mp3', -3)
# chains dragged on stone
c = np.concatenate([span(load('0619'))[: int(3 * SR)], span(load('0359'))])
save(fade(reverb(lp(c, 5000), 2.2, 0.45, 0.03, 3000), 0.01, 1.2), 'chains.mp3', -6)
# one tumbril going by
L = int(9 * SR); wh = lp(span(load('1316'))[:L], 800); ax = lp(span(load('2517'))[:L], 1800)
n = min(len(wh), len(ax)); sw = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
tb = (wh[:n] + 0.5 * ax[:n]) * sw[:, None]
save(fade(reverb(tb, 1.2, 0.3, 0.03, 3000), 0.3, 1.5), 'tumbril.mp3', -6)
# the wood-sawyer's saw
s = span(load('0559')); save(fade(lp(s[: int(5 * SR)], 6000), 0.05, 0.8), 'saw.mp3', -6)
# a footstep in the snow
ss = events(load('3363'), 0.7, -22, 0.3); save(fade(lp(ss[min(2, len(ss) - 1)], 6000), 0.002, 0.3), 'snow-step.mp3', -8)
# clocks: strokes of a far bell
strokes = events(load('3446'), 2.6, -20, 0.6); print('clock strokes', len(strokes))
ch = np.zeros((int(10 * SR), 2), np.float32)
for k in range(4): put(ch, strokes[k % len(strokes)], k * 1.9, 1.0 - k * 0.08, -0.3)
save(fade(reverb(lp(ch, 2400), 3.0, 0.5, 0.06, 2200), 0.01, 3), 'clock-hour.mp3', -8)
c2 = np.zeros((int(5 * SR), 2), np.float32)
for k in range(2): put(c2, strokes[k % len(strokes)], k * 1.9, 1.0, -0.2)
save(fade(reverb(lp(c2, 2600), 2.6, 0.45, 0.05, 2400), 0.01, 2), 'clock-two.mp3', -8)
