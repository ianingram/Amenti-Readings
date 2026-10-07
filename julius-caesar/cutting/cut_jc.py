#!/usr/bin/env python3
"""Julius Caesar (adapted from the Romeo and Juliet cutter) — the play is already a cast recording: every speech carries its
speaker's name. So nothing is inferred. Each speech becomes one cue in its speaker's
voice; every stage direction — the scene headings, 'Enter…', and the bracketed
directions inside speeches — becomes a cue for Shakespeare, who reads them as the
Chorus reads the prologue. One episode per scene. Every cue is a byte-identical slice
of the library file."""
import re, json
LIB = '/tmp/claude-0/-home-claude/c002dc02-d023-5c73-9437-2a1012982e23/scratchpad/al/library/shakespeare-william/17-julius-caesar.md'
T = open(LIB, encoding='utf-8').read()
START = T.index('\n## ACT I\n') + 1
SP = re.compile(r'^([A-Z][A-Z’\' ]+)\.$')
DIRECTION = re.compile(r'^(Enter|Exit|Exeunt|Re-enter|Thunder and lightning|Drum\. |Alarum|Sennet|Flourish|Low march|A crowd of people|Caesar enters the Capitol)')
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cast_jc import CAST
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
        if p.strip() == 'VARRO. CLAUDIUS.':
            flush(); speaker = 'VARRO'; continue
        m = SP.match(p)
        if m and m.group(1) in CAST:
            flush(); speaker = m.group(1)
            if speaker == 'CINNA' and ep['act'] == 'ACT III' and (ep['scene'] or '').startswith('SCENE III'): speaker = 'CINNA_POET'
            continue
        if m and len(p) < 40: print('UNKNOWN HEADING', repr(p), ep['act'], ep['scene'][:20])
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
