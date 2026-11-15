#!/usr/bin/env python3
"""Cut A Tale of Two Cities into cue sheets · 14 Nov 2026.
Cue boundaries fall only on paragraph breaks and on the quotation marks of speech;
every cue's text is a byte-identical slice of the library file. Speech is given to
the speaker Dickens names in his tag ('said Mr. Lorry', 'returned Carton'); failing
that, the name or pronoun in the sentence that leads into the quote; failing that,
the alternation of the exchange (marked INFERRED). Hand corrections go in OVR.
Every quote is listed in REVIEW.md. Minor speakers are Dickens's (the narrator).
usage: cut.py <Amenti.live library dir> <out dir (a-tale-of-two-cities/)>"""
import re, json, sys, os
LIB = sys.argv[1].rstrip('/') + '/charles-dickens/a-tale-of-two-cities/ch{:02d}.md'
OUT = sys.argv[2].rstrip('/') + '/'

CAST = {  # key: (role, ledger figure) — Ian approved 14 Nov 2026
    'narrator': ('Narrator', 'Charles Dickens'), 'carton': ('Sydney Carton', 'Christopher Hitchens'),
    'darnay': ('Charles Darnay', 'Louis Philippe I'), 'lucie': ('Lucie Manette', 'Jane Goodall'),
    'manette': ('Doctor Manette', 'Nostradamus'), 'lorry': ('Jarvis Lorry', 'Isaac Newton'),
    'pross': ('Miss Pross', 'Emmeline Pankhurst'), 'stryver': ('Stryver', 'Pompey'),
    'barsad': ('John Barsad', 'Richard III of England'), 'jerry': ('Jerry Cruncher', 'Plautus'),
    'mrs_cruncher': ('Mrs Cruncher', 'Mary I of England'), 'young_jerry': ('Young Jerry', 'Charlie Chaplin'),
    'attorney': ('Attorney-General', 'Edward Gibbon'), 'madame': ('Madame Defarge', 'Coco Chanel'),
    'defarge': ('Ernest Defarge', 'Victor Hugo'), 'marquis': ('The Marquis St. Evrémonde', 'Marquis de Sade'),
    'vengeance': ('The Vengeance', 'Edith Piaf'), 'jacques3': ('Jacques Three', 'Philip IV of France'),
    'mender': ('The mender of roads', 'Louis Pasteur'), 'seamstress': ('The seamstress', 'Marie Antoinette'),
}
FEMALE = {'lucie', 'pross', 'mrs_cruncher', 'madame', 'vengeance', 'seamstress', 'minor_f'}
BOOK = {**{n: 1 for n in range(1, 7)}, **{n: 2 for n in range(7, 31)}, **{n: 3 for n in range(31, 46)}}

def names_for(ch):
    """who a name means depends on the book: 'Evrémonde' is the Marquis in Book II, Darnay in Book III"""
    b = BOOK[ch]
    N = [
        (r"Sydney|Carton|the jackal", 'carton'),
        (r"Darnay|Charles(?! Evrémonde)|the prisoner|the nephew" if b < 3 else r"Darnay|Charles|Evrémonde|the prisoner", 'darnay'),
        (r"Lucie|Miss Manette|Mrs\.? Darnay|Ladybird|the young lady|her mistress", 'lucie'),
        (r"Doctor Manette|Dr\.? Manette|the Doctor|Manette|the shoemaker|her father", 'manette'),
        (r"Jarvis|Lorry", 'lorry'), (r"Miss Pross|Pross", 'pross'), (r"Stryver", 'stryver'),
        (r"Barsad|Solomon|the spy", 'barsad'), (r"Mrs\.? Cruncher", 'mrs_cruncher'),
        (r"young Jerry|Young Jerry|his son|the boy", 'young_jerry'), (r"Jerry|Cruncher", 'jerry'),
        (r"Attorney-General|Mr\.? Attorney", 'attorney'),
        (r"Madame Defarge|madame", 'madame'), (r"Defarge|Jacques Four|the keeper of the wine-shop|the wine-shop keeper", 'defarge'),
        (r"Monsieur the Marquis|the Marquis|Marquis|the uncle" + (r"|Evrémonde" if b == 2 else ""), 'marquis'),
        (r"The Vengeance|the Vengeance|Vengeance", 'vengeance'), (r"Jacques Three", 'jacques3'),
        (r"mender of roads|the wood-sawyer|wood-sawyer", 'mender'), (r"the seamstress|the poor little seamstress|the girl", 'seamstress' if b == 3 else 'minor_f'),
        (r"Gabelle|Cly|Jacques One|Jacques Two|Jacques Five|Jacques|the judge|the President|the guard|the coachman|the driver|"
         r"Monseigneur|the gaoler|the turnkey|Tom|Joe|the clerk|the waiter|a voice|the man|the woman|the other", 'minor'),
    ]
    return N

VERB = (r"(?:said|says|cried|returned|replied|asked|exclaimed|observed|rejoined|pursued|repeated|continued|answered|"
        r"inquired|resumed|added|whispered|faltered|pleaded|retorted|demanded|interposed|muttered|growled|urged|"
        r"stammered|sobbed|panted|began|interrupted|called|shouted|groaned|sighed|declared|went on|echoed|remarked|"
        r"screamed|laughed|murmured|broke in|bawled|gasped|struck in|put in|grumbled|snarled|thundered|explained|"
        r"agreed|protested|wailed|bellowed|yelled|hissed|swore|ventured|recommended|suggested|assented|sneered|"
        r"proceeded|concluded|retorted|cautioned|reasoned|pursued|smiled|nodded|rejoined|demanded|exclaimed)")

def spans(p):
    out, i = [], 0
    for m in re.finditer(r'“[^”]*”', p):
        if m.start() > i: out.append([i, m.start(), 'n'])
        out.append([m.start(), m.end(), 's']); i = m.end()
    if i < len(p):
        rest = p[i:]
        if rest.count('“') > rest.count('”'):
            j = i + rest.find('“')
            if j > i: out.append([i, j, 'n'])
            out.append([j, len(p), 's'])
        else: out.append([i, len(p), 'n'])
    return out

def key_of(text, N):
    for rx, k in N:
        if re.search(r"(?<![\w-])(?:" + rx + r")(?![\w-])", text): return k
    return None

def attribute(ch, paras, heads):
    """speaker per speech paragraph: (speaker, how)"""
    N = names_for(ch); res = {}; last = prev = None; last_m = last_f = None
    NRX = re.compile(r"(?<![\w-])(" + '|'.join('(?:' + rx + ')' for rx, _ in N) + r")(?![\w-])")
    def note(text):
        nonlocal last_m, last_f
        for m in NRX.finditer(text):
            k = key_of(m.group(1), N)
            if k in FEMALE: last_f = k
            elif k and k not in ('minor',): last_m = k
    for pi, p in enumerate(paras):
        if pi in heads: note(p); continue
        ss = spans(p)
        if not any(k == 's' for _, _, k in ss): note(p); continue
        speaker, how = None, 'tag'
        for k_, (a, b, kind) in enumerate(ss):                       # a tag after a quote: “…,” said Mr. Lorry
            if kind != 'n' or k_ == 0: continue
            seg = re.sub(r'\b(Mrs?|Mr|Dr|St)\.', r'\1', p[a:b].replace('\n', ' '))
            m = re.match(r"\W*" + VERB + r"\s+(?:the\s+)?([^,.;:!?—]{1,45})", seg)
            if m:
                tgt = m.group(1)
                if re.match(r"(he|she)\b", tgt): speaker = (last_f if tgt.startswith('she') else last_m); how = 'tag-pronoun'
                else: speaker = key_of(tgt, N) or key_of(m.group(0), N)
            if not speaker:
                m2 = re.match(r"\W*((?:[A-Z][\w.’-]*\s?){1,3}|[Hh]e|[Ss]he|I)\s+" + VERB + r"\b", seg)
                if m2:
                    w = m2.group(1).strip()
                    if w.lower() == 'he': speaker, how = last_m, 'tag-pronoun'
                    elif w.lower() == 'she': speaker, how = last_f, 'tag-pronoun'
                    else: speaker = key_of(w, N)
            if speaker: break
        if not speaker:                                                # narration before the first quote
            a0 = next(a for a, b, kind in ss if kind == 's'); before = re.sub(r'\b(Mrs?|Mr|Dr|St)\.', r'\1', p[:a0].replace('\n', ' '))
            if before.strip():
                cut = max(before.rfind('. '), before.rfind('! '), before.rfind('? '))
                sentence = before[cut + 1:]
                if re.search(VERB + r"[^“]{0,40}$", sentence) or re.search(r"[,:]\s*$", sentence):
                    ms = [key_of(m.group(1), N) for m in NRX.finditer(sentence)]
                    ms = [k for k in ms if k]
                    pv = re.search(r"\b(he|she)\b", sentence, re.I)
                    if ms: speaker, how = ms[0], 'NAMED'
                    elif pv: speaker, how = ((last_f if pv.group(1).lower() == 'she' else last_m), 'PRONOUN')
        if not speaker:
            speaker, how = ((prev, 'INFERRED') if prev and prev != last else (last, 'INFERRED'))
            if speaker is None: speaker, how = 'minor', 'INFERRED'
        speaker = {'minor_f': 'minor', 'minor_m': 'minor'}.get(speaker, speaker)
        res[pi] = (speaker, how)
        note(p)
        if speaker in FEMALE: last_f = speaker
        elif speaker not in ('minor', 'narrator'): last_m = speaker
        if speaker != last: prev, last = last, speaker
    return res

REVIEWED = set(range(1, 46))   # every chapter read and set quote by quote (14 Nov 2026)
OVR = {}   # (chapter, paragraph) -> speaker key, or a list per quote in the paragraph; set by hand
if os.path.exists(OUT + 'tools/ovr.json'):
    for k, v in json.load(open(OUT + 'tools/ovr.json')).items():
        c, p = k.split(':'); OVR[(int(c), int(p))] = v

ROMAN = 'I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII XXIV'.split()
BOOKNAME = {1: 'BOOK THE FIRST · RECALLED TO LIFE', 2: 'BOOK THE SECOND · THE GOLDEN THREAD', 3: 'BOOK THE THIRD · THE TRACK OF A STORM'}
index = {'work': 'a-tale-of-two-cities', 'title': 'A Tale of Two Cities', 'author': 'Charles Dickens', 'first_published': 1859,
         'source': 'library/charles-dickens/a-tale-of-two-cities/ch01.md … ch45.md in Amenti.live · Project Gutenberg #98 · public domain',
         'note': 'Forty-five chapters in three books. Dickens narrates and speaks the minor parts; the principals are cast from the ledger. Attributions are in REVIEW.md.',
         'chapters': []}
review = ['# A Tale of Two Cities — speech attributions to confirm', '',
          'Every quotation and the voice it was given. **tag**: Dickens’s own tag (“said Mr. Lorry”); **NAMED/PRONOUN**: the sentence leading into the quote; '
          '**INFERRED**: untagged, the exchange alternates — check these; **corrected**: set by hand. Minor speakers are Dickens’s.', '']
stats = {}
for ch in range(1, 46):
    raw = open(LIB.format(ch), encoding='utf-8').read()
    paras = [p for p in re.split(r'\n{2,}', raw) if p.strip()]
    b = BOOK[ch]; nb = ch - {1: 0, 2: 6, 3: 30}[b]
    heads = set()
    for i, p in enumerate(paras[:3]):
        if p.startswith('Book the '): heads.add(i)
        elif re.match(r'^CHAPTER [IVXL]+\.$', p): heads |= {i, i + 1}
    title = paras[max(heads)] if heads else ''
    att = attribute(ch, paras, heads)
    cues = []; n = 0
    review += ['## Book %d, Chapter %s — %s' % (b, ROMAN[nb - 1], title), '']
    pos = 0
    for pi, p in enumerate(paras):
        start = raw.index(p, pos); pos = start + len(p)
        ss = spans(p); spk = att.get(pi); ov = OVR.get((ch, pi)); qi = 0
        for a, bb, kind in ss:
            seg = p[a:bb]; s = seg.strip()
            if not s or not re.search(r'\w', s):
                continue
            if kind == 's':
                who, how = spk if spk else ('narrator', '?')
                if ov is not None:
                    who = ov[qi] if isinstance(ov, list) else ov; how = 'corrected'
                qi += 1
                review.append('- ¶%d · **%s** · *%s* · %s' % (pi, CAST.get(who, ('Narrator',))[0] if who != 'minor' else 'Narrator (minor)', how, s[:100].replace('\n', ' ')))
                stats[how] = stats.get(how, 0) + 1
            else:
                who = 'narrator'
            role, cast = CAST.get(who, CAST['narrator'])
            n += 1; cues.append({'n': n, 'para': pi, 'role': role, 'cast': cast, 'text': s})
            assert s in raw
    review.append('')
    roles = []
    for c in cues:
        if (c['role'], c['cast']) not in roles: roles.append((c['role'], c['cast']))
    ep = {'work': 'a-tale-of-two-cities', 'episode': ch, 'chapter': ch, 'title': title,
          'document': '%s · CHAPTER %s' % (BOOKNAME[b], ROMAN[nb - 1]),
          'source': {'library': 'library/charles-dickens/a-tale-of-two-cities/ch%02d.md' % ch,
                     'text': 'Charles Dickens, A Tale of Two Cities (1859) · Project Gutenberg #98 · public domain'},
          'note': 'Chapter complete. Cue boundaries fall on paragraph breaks and on the quotation marks of speech; every cue is byte-identical to the library file. Attributions are in REVIEW.md.',
          'cast': [{'role': r, 'cast_as': c} for r, c in roles], 'cues': cues}
    open(OUT + 'ep%02d.json' % ch, 'w').write(json.dumps(ep, indent=1, ensure_ascii=False) + '\n')
    index['chapters'].append({'n': ch, 'file': 'a-tale-of-two-cities/ep%02d.json' % ch, 'document': ep['document'], 'summary': title, 'status': 'scripted' if ch in REVIEWED else 'draft'})
open(OUT + 'index.json', 'w').write(json.dumps(index, indent=1, ensure_ascii=False) + '\n')
open(OUT + 'REVIEW.md', 'w').write('\n'.join(review) + '\n')
print('45 chapters ·', sum(1 for _ in index['chapters']), 'sheets ·', stats)
