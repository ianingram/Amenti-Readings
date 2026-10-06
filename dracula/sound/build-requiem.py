#!/usr/bin/env python3
"""Dracula — THE REQUIEM, for Lucy's funeral (chapter 13). 6 Oct 2026.

Gregorian chant, at Ian's direction — in 4/4 and very slow. The chant is real: the DIES IRAE,
the sequence of the Requiem Mass itself, a Gregorian recording placed in the public domain on
Wikimedia Commons (Membeth). Its first three minutes, slowed to 88 % (pitch kept), so the
monks sing it at a funeral's pace.

Under it, the slow 4/4: 40 BPM, a bar every six seconds — a muffled bass drum on beat one and
a soft tenor drum on beat three, like a cortège's step; the passing bell once every four
bars. No pitched drone, so nothing argues with the singers' mode.

Drums: VSCO 2 CE (CC0); bell: Romeo and Juliet's passing-bell.mp3. Seed 1897."""
import os, subprocess
exec(open('/tmp/qv/prod/qv_score.py').read().split('# ═══ OPULENCE')[0].replace("/tmp/qv/score/", "/tmp/dr/cues/"))
chant = load('/tmp/req/slow.wav')
BPM = 40; BT = 60 / BPM; BAR = 4 * BT
N = len(chant); bars = int(N / SR / BAR)
BD = '/tmp/vsco/VSCO 1 Percussion/drums/bass/'
bd = load16(BD + 'bdrum2_pp_1.wav'); td = load16('/tmp/vsco/VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f_1.wav')
bell = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', '/tmp/rd2/romeo-and-juliet/sound/passing-bell.mp3', '-f', 'f32le',
                                     '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).copy()
pulse, bl = np.zeros(N, np.float32), np.zeros(N, np.float32)
for b in range(bars):
    put(pulse, lp(bd, 300), b * BAR + 0.5, 1.0)              # beat one: the cortège's step
    put(pulse, lp(td, 900), b * BAR + 0.5 + 2 * BT, 0.45)    # beat three: softer
    if b % 4 == 0: put(bl, bell, b * BAR + 0.5, 0.6)          # the passing bell
mix = stems((chant, -22), (reverb(pulse, 4.0, 0.45, seed=41), -33), (reverb(bl, 4.5, 0.45, seed=42), -34))
mix[:int(1.5 * SR)] *= np.linspace(0, 1, int(1.5 * SR)); mix[-int(8 * SR):] *= np.linspace(1, 0, int(8 * SR))
write_mp3(rms_db(mix, -24), 'score-requiem.mp3')
print('requiem', round(N / SR, 1), 's,', bars, 'bars of 4/4 at', BPM, 'BPM')
