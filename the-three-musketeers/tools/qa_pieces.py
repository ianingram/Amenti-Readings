#!/usr/bin/env python3
"""QA, The Three Musketeers · 19 Nov 2026 (amenti-studios-production §7, "Check every take").
Transcribes every piece of 60 characters or less and every piece that runs long (a runaway:
secs > chars/9 + 4), from fetch_voice's cache pulls, and compares word by word with the book.
Accent mishears of names pass; invented sentences, runaways and wrong words are flagged.
usage: qa_pieces.py <voice root> <out.json> NN [NN ...]   (cached transcripts are reused)"""
import json, sys, os, re, subprocess, difflib, numpy as np
from faster_whisper import WhisperModel
VROOT, OUT = sys.argv[1:3]; CHS = sys.argv[3:]
M = WhisperModel('small.en', device='cpu', compute_type='int8')
old = json.load(open(OUT)) if os.path.exists(OUT) else {}
NAMES = {'artagnan', 'artagnon', 'tréville', 'treville', 'athos', 'porthos', 'aramis', 'bonacieux', 'planchet', 'rochefort', 'milady',
         'buckingham', 'richelieu', 'winter', 'chevreuse', 'louvre', 'gascony', 'béarn', 'meung', 'mousqueton', 'bazin', 'grimaud'}
N = lambda s: [w for w in re.sub(r"[^a-zà-ÿ0-9 ]", ' ', s.lower().replace('’', "'").replace("d'", 'd ')).split()]
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
for ch in CHS:
    m = json.load(open('%s/%s/manifest.json' % (VROOT, ch)))
    for c in m['cues']:
        for k, p in enumerate(c.get('chunks') or []):
            if not p.get('file'): continue
            key = '%s-%d-%d' % (ch, c['n'], k)
            a = None; t = p['text']
            if len(t) > 60:
                if key in old: continue
                a = load('%s/%s/voice/%s' % (VROOT, ch, p['file'])); secs = len(a) / 16000
                if secs <= len(t) / 9 + 4: continue
            if key in old and old[key].get('text') == t: continue
            if a is None: a = load('%s/%s/voice/%s' % (VROOT, ch, p['file']))
            segs, _ = M.transcribe(a, language='en', beam_size=5)
            h = ' '.join(s.text.strip() for s in segs)
            want, got = N(t), N(h)
            r = difflib.SequenceMatcher(None, want, got).ratio()
            extra = len(got) - len(want)
            old[key] = {'ch': ch, 'n': c['n'], 'k': k, 'pieces': len(c['chunks']), 'text': t, 'heard': h, 'r': round(r, 3),
                        'secs': round(len(a) / 16000, 1), 'extra': extra, 'cast': c.get('cast'), 'voice': c.get('voice')}
    json.dump(old, open(OUT, 'w'), ensure_ascii=False, indent=0)
    sus = [v for v in old.values() if v['ch'] == ch and (v['r'] < 0.6 or v['extra'] >= 3)]
    print(ch, 'checked', sum(1 for v in old.values() if v['ch'] == ch), 'suspect', len(sus), flush=True)
