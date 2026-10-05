#!/usr/bin/env python3
"""Dracula, Chapters VIII onward — the same doctrine as I–VII.

THE BOOK IS ALREADY CAST. Every section is a document with a writer named at its head:
a journal, a diary, a letter, a telegram, a memorandum, a newspaper. Stoker reads the
chapter number and each document's heading; the writer reads the document. Inside a
journal or diary, the principal characters speak their own words; a brief quotation from
anyone else — a maid, a keeper, an attendant, Renfield, Mrs Westenra — is spoken by the
document's writer. Letters, telegrams and memoranda are read whole by their writers.
Every cue is a byte-identical slice of the library file."""
import re, json, importlib.util
spec = importlib.util.spec_from_file_location('c', '/tmp/dr/cut_dr.py'); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
ws = lambda x: re.sub(r'\s+', ' ', x)
# (heading pattern, writer, kind) — order matters: "to Van Helsing" is Mina writing, not Van Helsing
HEADS = [
 (r"^(MINA MURRAY’S JOURNAL|Mina Murray’s Journal)", 'mina', 'journal'),
 (r"^(MINA HARKER’S JOURNAL|Mina Harker’s Journal)", 'mina', 'journal'),
 (r"^Mina Harker’s Memorandum", 'mina', 'journal'),
 (r"^(Letter|Telegram)[^.]*(Mina Harker|Mrs\. Harker) to", 'mina', 'letter'),
 (r"^DR\. SEWARD’S PHONOGRAPH DIARY, SPOKEN BY VAN HELSING", 'vanhelsing', 'journal'),
 (r"^(DR\. SEWARD’S DIARY|Dr\. Seward’s Diary)", 'seward', 'journal'),
 (r"^(Letter|Telegram)[^.]*(Dr\. Seward|Seward, London|from Dr\. Seward)", 'seward', 'letter'),
 (r"^(Memorandum by Abraham Van Helsing|Dr\. Van Helsing’s Memorandum)", 'vanhelsing', 'journal'),
 (r"^(Letter|Telegram|Note left)[^.]*Van Helsing", 'vanhelsing', 'letter'),
 (r"^Letter \(by hand\), Van Helsing", 'vanhelsing', 'letter'),
 (r"^(JONATHAN HARKER’S JOURNAL|Jonathan Harker’s Journal)", 'jonathan', 'journal'),
 (r"^(Lucy Westenra’s Diary|LUCY WESTENRA’S DIARY)", 'lucy', 'journal'),
 (r"^(Memorandum left by Lucy Westenra|Letter, Lucy Westenra)", 'lucy', 'letter'),
 (r"^(Letter|Telegram), Arthur Holmwood", 'arthur', 'letter'),
 (r"^Letter, Sister Agatha", 'agatha', 'letter'),
 (r"^PERILOUS ADVENTURE OF OUR INTERVIEWER", 'correspondent', 'journal'),
 (r"^(Letter|Report|Telegram)[ ,]", 'narrator', 'letter'),            # solicitors, carriers, house agents, a doctor's report, a telegram
 (r"^28 October\. —Telegram\. Rufus Smith", 'narrator', 'letter'),
]
def heading(p):
    q = ws(p).strip()
    if len(q) > 175 or q.startswith('“'): return None
    for rx, w, k in HEADS:
        if re.search(rx, q): return (w, k)
    return None
MINA = lambda ch: ('Mina Murray', 'Agatha Christie') if ch <= 8 else ('Mina Harker', 'Agatha Christie')
def role_of(key, ch):
    if key == 'mina': return MINA(ch)
    return c.CAST[key]
def build(ch, ovr=None, first_writer='narrator', first_kind='journal'):
    ovr = ovr or {}
    paras = c.paras_of(ch); res = c.attribute2(ch, paras, {0})
    writer, kind = first_writer, first_kind
    cues, review = [], []
    for pi, p in enumerate(paras):
        h = heading(p) if pi > 0 else None
        if pi == 0 or h:
            if h: writer, kind = h
            cues.append({'para': pi, 'role': 'Narrator', 'cast': 'Bram Stoker', 'text': p.strip()}); continue
        sp = res.get(pi, []); o = ovr.get(pi); roles = []; si = 0
        W = role_of(writer, ch)
        for a, b, k in c.spans(p):
            if k == 's':
                who, how = (sp[si][2], sp[si][3]) if si < len(sp) else ('narrator', 'INFERRED')
                if o is not None: who, how = (o[si] if isinstance(o, list) else o), 'CONFIRMED'
                if kind == 'letter': who, how = writer, 'LETTER'
                if who in ('narrator', 'minor', None): spk = W; label = W[0] if who != 'minor' else W[0] + ' (minor speaker)'
                else: spk = role_of(who, ch); label = spk[0]
                review.append((pi, label, how, p[a:b])); si += 1
            else: spk = W
            roles.append([a, b, spk])
        merged = []
        for a, b, k in roles:
            if merged and merged[-1][2] == k: merged[-1][1] = b
            else: merged.append([a, b, k])
        for a, b, k in merged:
            t = p[a:b].strip()
            if t: cues.append({'para': pi, 'role': k[0], 'cast': k[1], 'text': t})
    for i, q in enumerate(cues): q['n'] = i + 1
    return cues, review, paras
