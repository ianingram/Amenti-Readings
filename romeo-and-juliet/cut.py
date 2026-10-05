#!/usr/bin/env python3
"""Romeo and Juliet — the play is already a cast recording: every speech carries its
speaker's name. So nothing is inferred. Each speech becomes one cue in its speaker's
voice; every stage direction — the scene headings, 'Enter…', and the bracketed
directions inside speeches — becomes a cue for Shakespeare, who reads them as the
Chorus reads the prologue. One episode per scene. Every cue is a byte-identical slice
of the library file."""
import re, json
LIB = '/tmp/repos/Amenti.live/library/shakespeare-william/30-romeo-and-juliet.md'
T = open(LIB, encoding='utf-8').read()
START = T.index('### THE PROLOGUE')
SP = re.compile(r'^([A-Z][A-Z’\' ]+)\.$')
DIRECTION = re.compile(r'^(Enter|Exit|Exeunt|Re-enter|Musicians waiting)\b')
CAST = {
 'DIRECTIONS': ('Stage directions', 'William Shakespeare'), 'CHORUS': ('Chorus', 'William Shakespeare'), 'THE PROLOGUE': ('Chorus', 'William Shakespeare'),
 'ROMEO': ('Romeo', 'Romulus'), 'JULIET': ('Juliet', 'Saint Joan of Arc'), 'NURSE': ('Nurse', 'Sophia Loren'),
 'MERCUTIO': ('Mercutio', 'Giacomo Casanova'), 'FRIAR LAWRENCE': ('Friar Lawrence', 'Francis of Assisi'), 'BENVOLIO': ('Benvolio', 'Guglielmo Marconi'),
 'TYBALT': ('Tybalt', 'Caravaggio'), 'CAPULET': ('Capulet', 'Luciano Pavarotti'), 'LADY CAPULET': ('Lady Capulet', "Catherine de' Medici"),
 'PARIS': ('Paris', 'Titian'), 'PRINCE': ('Prince Escalus', 'Dante Alighieri'), 'MONTAGUE': ('Montague', 'Leonardo da Vinci'),
 'LADY MONTAGUE': ('Lady Montague', 'Maria Montessori'),
 # the small parts, doubled as in Shakespeare's own company
 'SAMPSON': ('Sampson', 'Giuseppe Garibaldi'), 'GREGORY': ('Gregory', 'Umberto Eco'), 'PETER': ('Peter', 'Umberto Eco'),
 'ABRAM': ('Abram', 'Amerigo Vespucci'), 'BALTHASAR': ('Balthasar', 'Amerigo Vespucci'), 'FRIAR JOHN': ('Friar John', 'Amerigo Vespucci'),
 'PAGE': ('Page', 'Amerigo Vespucci'), 'SERVANT': ('Servant', 'Umberto Eco'), 'FIRST SERVANT': ('First Servant', 'Giuseppe Garibaldi'),
 'SECOND SERVANT': ('Second Servant', 'Amerigo Vespucci'), 'FIRST MUSICIAN': ('First Musician', 'Giuseppe Garibaldi'),
 'SECOND MUSICIAN': ('Second Musician', 'Amerigo Vespucci'), 'THIRD MUSICIAN': ('Third Musician', 'Umberto Eco'),
 'FIRST WATCH': ('First Watch', 'Giuseppe Garibaldi'), 'SECOND WATCH': ('Second Watch', 'Amerigo Vespucci'), 'THIRD WATCH': ('Third Watch', 'Umberto Eco'),
 'FIRST CITIZEN': ('First Citizen', 'Giuseppe Garibaldi'), 'APOTHECARY': ('Apothecary', 'Caravaggio'),
 'CAPULET’S COUSIN': ('Capulet’s Cousin', 'Pope John XXIII'),
}
def paragraphs():
    """(start, end) offsets of every paragraph after the cast list"""
    out = []; i = START
    for m in re.finditer(r'\n\s*\n', T[START:]):
        j = START + m.start()
        if T[i:j].strip(): out.append((i + (len(T[i:j]) - len(T[i:j].lstrip())), j))
        i = START + m.end()
    if T[i:].strip(): out.append((i, len(T.rstrip())))
    return out
def cut():
    eps = []; ep = None; speaker = None; pending = None              # pending: an open speech cue [start, end, speaker]
    def flush():
        nonlocal pending
        if pending: ep['cues'].append({'role': pending[2], 'span': (pending[0], pending[1])}); pending = None
    def direction(a, b):
        flush(); ep['cues'].append({'role': 'DIRECTIONS', 'span': (a, b)})
    act = None
    for a, b in paragraphs():
        p = T[a:b]
        if p.startswith('### THE PROLOGUE'):                     # the prologue opens the first episode
            ep = {'act': 'PROLOGUE', 'scene': None, 'cues': []}; eps.append(ep); speaker = None
            ep['cues'].append({'role': 'DIRECTIONS', 'span': (a + 4, b), 'heading': True}); continue
        if p.startswith('## ACT'):
            flush(); act = p.replace('## ', '').strip()
            if not (ep and ep['scene'] is None):                  # an act opens a new episode, unless the prologue is waiting for it
                ep = {'act': act, 'scene': None, 'cues': []}; eps.append(ep)
            ep['act'] = act if ep['act'] == 'PROLOGUE' and act == 'ACT I' else ep['act']
            ep['cues'].append({'role': 'DIRECTIONS', 'span': (a + 3, b), 'heading': True}); speaker = None; continue
        if p.startswith('### SCENE'):
            flush()
            if not (ep and ep['scene'] is None):
                ep = {'act': act, 'scene': None, 'cues': []}; eps.append(ep)
            ep['scene'] = p.replace('### ', '').strip(); ep['act'] = act
            ep['cues'].append({'role': 'DIRECTIONS', 'span': (a + 4, b), 'heading': True}); speaker = None; continue
        if ep is None: continue
        m = SP.match(p)
        if m and m.group(1) in CAST:
            flush(); speaker = m.group(1); continue
        if DIRECTION.match(p) or (p.startswith('[*') and p.endswith('*]')):
            direction(a, b); continue
        # speech text — split around any bracketed direction inside it
        pos = a
        for d in re.finditer(r'\[\*.*?\*\]', p, re.S):
            da, db = a + d.start(), a + d.end()
            if T[pos:da].strip():
                s0 = pos + (len(T[pos:da]) - len(T[pos:da].lstrip())); e0 = pos + len(T[pos:da].rstrip())
                if pending and pending[2] == speaker: pending[1] = e0
                else: flush(); pending = [s0, e0, speaker or 'DIRECTIONS']
            direction(da, db); pos = db
        if T[pos:b].strip():
            s0 = pos + (len(T[pos:b]) - len(T[pos:b].lstrip())); e0 = b
            if pending and pending[2] == speaker: pending[1] = e0
            else: flush(); pending = [s0, e0, speaker or 'DIRECTIONS']
    flush()
    return eps
if __name__ == '__main__':
    eps = cut()
    for e in eps:
        roles = {}
        for q in e['cues']: roles[q['role']] = roles.get(q['role'], 0) + 1
        print(e['act'], '|', e['scene'][:50], '|', len(e['cues']), 'cues |', ', '.join(f'{k}:{v}' for k, v in sorted(roles.items(), key=lambda x: -x[1])[:6]))
