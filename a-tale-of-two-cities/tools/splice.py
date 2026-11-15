#!/usr/bin/env python3
"""Short endings, Book the First · 14 Nov 2026 (the splice of amenti-studios-production §7).
Each faulty tail was rendered inside a longer clause (tools/sampler/tc-fixes-b1.json, 3 takes).
For each fix: transcribe every take with word times, keep the take whose words match, cut it
to the cue's own words, and bake the whole cue (the good pieces as cached, the repaired part
spliced in, the engine's rests between pieces) as sound/tc-chNN-cueNNN-v1.mp3. The cue's
text never changes; its "audio" points at the baked file.
usage: splice.py <voice root (fetch_voice out dirs)> <takes dir> <out sound dir>"""
import json, sys, subprocess, difflib, re, glob, numpy as np
from faster_whisper import WhisperModel
VROOT, TAKES, OUT = sys.argv[1:4]; SR = 24000
M = WhisperModel('small.en', device='cpu', compute_type='int8')
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def words(a):
    a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    segs, _ = M.transcribe(a16, language='en', beam_size=5, word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
N = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('’', "'")).split()
def find(ws, phrase):
    """index of the word where phrase begins (fuzzy on the first three words)"""
    p = N(phrase)[:3]; toks = [N(w[0])[0] if N(w[0]) else '' for w in ws]
    best = (0, None)
    for i in range(len(toks)):
        r = difflib.SequenceMatcher(None, toks[i:i + len(p)], p).ratio()
        if r > best[0]: best = (r, i)
    return best[1] if best[0] >= 0.66 else None
def quiet(a, t0, t1):
    """the quietest 10 ms inside [t0, t1] seconds: where to cut"""
    i0, i1 = int(t0 * SR), max(int(t0 * SR) + 1, int(t1 * SR)); w = int(0.01 * SR)
    e = np.convolve(a[i0:i1] ** 2, np.ones(w) / w, 'same') if i1 - i0 > w else a[i0:i1] ** 2
    return i0 + int(np.argmin(e))
def trim(a, thr=0.004):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.12 * SR)] if len(idx) else a
def fadeio(a, i=0.008, o=0.03):
    a = a.copy(); a[:int(i * SR)] *= np.linspace(0, 1, int(i * SR)); a[-int(o * SR):] *= np.linspace(1, 0, int(o * SR)); return a
def score(a, text):
    heard = ' '.join(w[0] for w in words(a)); return difflib.SequenceMatcher(None, N(text), N(heard)).ratio(), heard

tags = json.load(open('/home/claude/ar/tools/sampler/tc-fixes-b1.json'))['tags']
take = lambda tag, k: glob.glob(TAKES + '/%02d.*' % (tags.index('%s/%d' % (tag, k)) + 1))[0]
FIX = [  # (chapter, cue, tag, the cue's own words in the take, (piece to cut, words it is cut before) or None, pieces replaced)
 ('01', 3, '01-3', 'The Period', None, [0]),
 ('03', 3, '03-3', 'is, in some of its imaginings, a secret to the heart nearest it!', (1, 'is, in some'), [2]),
 ('04', 9, '04-9', 'all kinds and varieties of men came out of it.', (0, 'all kinds and'), [1]),
 ('04', 36, '04-36a', 'when the hail drifted heavily and the sea ran high.', (4, 'when the hail'), [5]),
 ('04', 36, '04-36b', 'and he made his formal bow to Miss Manette.', (6, 'and he made'), [7]),
 ('05', 68, '05-68', 'the latter whispered.', None, [0]),
 ('06', 20, '06-20', 'laying the palest shadow of a stress upon the second word.', None, [0]),
 ('06', 78, '06-78', 'she sighed', None, [0]),
 ('06', 93, '06-93', 'he exclaimed.', None, [0]),
 ('06', 145, '06-145', 'from the uniform.', None, [0]),
]
done = {}; report = []
for ch, n, tag, own, prev, repl in FIX:
    best = None
    for k in range(3):
        a = load(take(tag, k)); ws = words(a); i = find(ws, own)
        if i is None: report.append((tag, k, 'words not found', ' '.join(w[0] for w in ws))); continue
        s = quiet(a, ws[i - 1][2], ws[i][1]) if i > 0 else max(0, int((ws[i][1] - 0.05) * SR))
        cut = trim(a[s:]); r, heard = score(cut, own)
        report.append((tag, k, round(r, 2), heard))
        if best is None or r > best[0]: best = (r, cut, k, heard)
    if best is None or best[0] < 0.8: print('NO GOOD TAKE', tag, best and best[3]); continue
    m = json.load(open('%s/%s/manifest.json' % (VROOT, ch))); c = [c for c in m['cues'] if c['n'] == n][0]
    key = (ch, n); parts = done.get(key) or [load('%s/%s/voice/%s' % (VROOT, ch, p['file'])) for p in c['chunks']]
    if prev:
        pi, before = prev; pa = parts[pi]; pw = words(pa); j = find(pw, before)
        if j is None: print('CUT POINT NOT FOUND', tag, ' '.join(w[0] for w in pw)); continue
        e = quiet(pa, pw[j - 1][2], pw[j][1]) if j > 0 else 0
        parts[pi] = np.concatenate([fadeio(pa[:e]), np.zeros(int(0.12 * SR), np.float32)])
    for r in repl: parts[r] = np.zeros(0, np.float32)
    parts[repl[0]] = fadeio(best[1])
    done[key] = parts; c['_rests'] = [p['rest'] for p in c['chunks']]; done[key + ('rests',)] = c['_rests']
    print('ok', tag, 'take', best[2], round(best[0], 2), '|', best[3])
for key, parts in list(done.items()):
    if len(key) == 3: continue
    ch, n = key; rests = done[key + ('rests',)]; out = []
    for p, r in zip(parts, rests):
        if len(p): out += [p, np.zeros(int(r * SR), np.float32)]
    a = np.concatenate(out[:-1]) if out else np.zeros(1, np.float32)
    f = '%s/tc-ch%s-cue%03d-v1.mp3' % (OUT, ch, n)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', f],
                   input=a.astype(np.float32).tobytes(), check=True)
    text = [c for c in json.load(open('%s/%s/manifest.json' % (VROOT, ch)))['cues'] if c['n'] == n][0]['text']
    r, heard = score(a, text)                                 # the whole baked cue against the book
    print('baked', f, '%.1f s' % (len(a) / SR), 'match %.2f' % r, '|', heard[-120:])
json.dump(report, open('/home/claude/tcqa/fix/report.json', 'w'), indent=1)
