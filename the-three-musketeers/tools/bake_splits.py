#!/usr/bin/env python3
"""Abbreviation splits, The Three Musketeers · 19 Nov 2026 (amenti-studios-production §7, the splice).
The locked chunker ends a measure after M./Mme./MM./St.; the voice then invents words ("the gate of
St. Germain. Antoine"). tools/sampler/tm-fixes-*.json renders the pieces on both sides of each such
split as ONE line, the word written out, 3 takes (probe). This script transcribes every take, keeps
the best that matches its words and is not a runaway, matches its loudness to the cached pieces,
and bakes the whole cue (cached pieces kept, the engine's rests between) as
sound/tm-chNN-cueNNN-v1.mp3. The cue text never changes; its "audio" points at the baked file.
usage: bake_splits.py <sheet.json> <takes dir> <voice root (fetch_voice out dirs per NN)> <out sound dir> [report.json]"""
import json, sys, subprocess, difflib, re, glob, os, numpy as np
from faster_whisper import WhisperModel
SHEET, TAKES, VROOT, OUT = sys.argv[1:5]; REPORT = sys.argv[5] if len(sys.argv) > 5 else None; SR = 24000
M = WhisperModel('small.en', device='cpu', compute_type='int8')
S = json.load(open(SHEET)); tags = S['tags']
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def heard(a):
    a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    segs, _ = M.transcribe(a16, language='en', beam_size=5)
    return ' '.join(s.text.strip() for s in segs)
SAME = {'monsieur': 'monsieur', 'mr': 'monsieur', 'messrs': 'messieurs', 'artagnon': 'artagnan', 'dartagnan': 'artagnan', 'dartagnon': 'artagnan'}
N = lambda s: [SAME.get(w, w) for w in re.sub(r"[^a-z0-9 ]", ' ', s.lower().replace('’', "'").replace("d'", 'd ')).split()]
EXP = [(r'\bMM\.(?=\s)', 'Messieurs'), (r'\bMme\.(?=\s)', 'Madame'), (r'\bMlle\.(?=\s)', 'Mademoiselle'), (r'\bM\.(?=\s)', 'Monsieur'), (r'\bSt\.(?=\s)', 'Saint')]
def expand(t):
    for x, y in EXP: t = re.sub(x, y, t)
    return t
ratio = lambda want, got: difflib.SequenceMatcher(None, N(want), N(got)).ratio()
def trim(a, thr=0.004):
    i = np.where(np.abs(a) > thr)[0]
    return a[max(0, i[0] - int(0.03 * SR)): i[-1] + int(0.12 * SR)] if len(i) else a
def rms(a):
    v = a[np.abs(a) > 0.01]; return float(np.sqrt(np.mean(v ** 2))) if len(v) else 0.0
def fade(a, i=0.008, o=0.03):
    a = a.copy(); a[:int(i * SR)] *= np.linspace(0, 1, int(i * SR)); a[-int(o * SR):] *= np.linspace(1, 0, int(o * SR)); return a
take = lambda tag, k: (glob.glob(TAKES + '/%02d.*' % (tags.index('%s/%d' % (tag, k)) + 1)) or [None])[0]

manifests, cues, report = {}, {}, []
for g in S['plan']:
    ch, n, (a, b), tag, text = g['ch'], g['n'], g['pieces'], g['tag'], g['text']
    if ch not in manifests: manifests[ch] = json.load(open('%s/%s/manifest.json' % (VROOT, ch)))
    c = [c for c in manifests[ch]['cues'] if c['n'] == n][0]
    if (ch, n) not in cues:
        cues[(ch, n)] = {'parts': [load('%s/%s/voice/%s' % (VROOT, ch, p['file'])) for p in c['chunks']],
                         'rests': [p['rest'] for p in c['chunks']], 'text': c['text'], 'kept': set(range(len(c['chunks'])))}
    best = None; exp = len(text) / 12.5 + 1.2
    for k in range(3):
        f = take(tag, k)
        if not f: report.append({'tag': tag, 'k': k, 'why': 'no take'}); continue
        t = trim(load(f)); secs = len(t) / SR
        if secs > 1.6 * exp and secs - exp > 2.5: report.append({'tag': tag, 'k': k, 'why': 'runaway %.1fs/%.1fs' % (secs, exp)}); continue
        h = heard(t); r = ratio(text, h); report.append({'tag': tag, 'k': k, 'r': round(r, 3), 'secs': round(secs, 1), 'heard': h})
        if best is None or r > best[0]: best = (r, t, k, h)
    if best is None or best[0] < 0.85: print('NO GOOD TAKE', tag, best and round(best[0], 2), best and best[3][-100:]); continue
    q = cues[(ch, n)]
    for i in range(a, b + 1): q['kept'].discard(i)
    q['parts'][a] = ('take', best[1]); q['rests'][a] = q['rests'][b]
    for i in range(a + 1, b + 1): q['parts'][i] = None
    print('ok', tag, 'take', best[2], round(best[0], 3))

os.makedirs(OUT, exist_ok=True); baked = []
for (ch, n), q in cues.items():
    if not any(isinstance(p, tuple) for p in q['parts']): continue
    ref = [rms(q['parts'][i]) for i in q['kept']]; ref = np.median(ref) if ref else None
    out = []
    for p, r in zip(q['parts'], q['rests']):
        if p is None: continue
        if isinstance(p, tuple):
            p = p[1]
            if ref: p = p * min(2.0, max(0.5, ref / max(rms(p), 1e-6)))     # the take at the cached pieces' level
            p = fade(p)
        out += [p, np.zeros(int(r * SR), np.float32)]
    a = np.clip(np.concatenate(out[:-1]), -1, 1)
    f = '%s/tm-ch%s-cue%03d-v1.mp3' % (OUT, ch, n)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', f],
                   input=a.astype(np.float32).tobytes(), check=True)
    h = heard(a); r = ratio(expand(q['text'].replace('\n', ' ')), h)
    baked.append({'ch': ch, 'n': n, 'file': os.path.basename(f), 'secs': round(len(a) / SR, 1), 'match': round(r, 3), 'heard': h})
    print('baked', os.path.basename(f), '%.1f s' % (len(a) / SR), 'match %.3f' % r)
if REPORT: json.dump({'takes': report, 'baked': baked}, open(REPORT, 'w'), ensure_ascii=False, indent=1)
