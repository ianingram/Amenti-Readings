#!/usr/bin/env python3
"""Cut Treasure Island chapters into cues. Speech is attributed from Stevenson's own
tags ('said the doctor', 'cried Silver', 'says I'); 'the captain' is Billy Bones in
Part One and Captain Smollett after. Untagged lines in an exchange alternate and are
marked INFERRED; every line goes to REVIEW.md. Chapters XVI–XVIII are the doctor's
narrative, so there the narrator — and 'I' — is Livesey."""
import re
LIB = '/tmp/qv/out/library/henryk-sienkiewicz/ch{:02d}.md'
CAST = {
 'narrator': ('Narrator', 'Henryk Sienkiewicz'),
 'petronius': ('Petronius', 'Petronius'), 'vinicius': ('Marcus Vinicius', 'Mark Antony'), 'lygia': ('Lygia', 'Helen Keller'),
 'nero': ('Nero', 'Nero'), 'seneca': ('Seneca', 'Seneca the Younger'), 'peter': ('Peter', 'Saint Peter'), 'paul': ('Paul of Tarsus', 'Paul the Apostle'),
 'lucan': ('Lucan', 'Lucan'), 'chilo': ('Chilo Chilonides', 'Diogenes'), 'ursus': ('Ursus', 'Spartacus'), 'poppaea': ('Poppæa', 'Cleopatra VII'),
 'tigellinus': ('Tigellinus', 'Caligula'), 'eunice': ('Eunice', 'Sappho'), 'aulus': ('Aulus Plautius', 'Vespasian'), 'pomponia': ('Pomponia Græcina', 'Hypatia'),
 'crispus': ('Crispus', 'Galba'),
}
DOCTOR_CHAPTERS = set()
def narrator(ch): return 'narrator'
VERB = (r"(?:said|says|cried|cries|returned|replied|asked|exclaimed|observed|rejoined|pursued|repeated|continued|answered|"
        r"inquired|resumed|added|whispered|faltered|pleaded|retorted|demanded|interposed|muttered|growled|roared|urged|"
        r"stammered|sobbed|panted|began|inquired|asked|answered|exclaimed|whispered|cried|said|added|replied|interrupted|continued|called|shouted|groaned|sighed|muttered|repeated|declared|went on|echoed|remarked|called|shouted|screamed|laughed|groaned|murmured|"
        r"interrupted|broke in|bawled|gasped|hailed|sang out|struck in|put in|chimed in|grumbled|snarled|whined|"
        r"thundered|explained|agreed|protested|declared|wailed|bellowed|yelled|hissed|swore|cursed|ventured|piped)")
def who_from(tag, ch):
    t = ' ' + tag.lower() + ' '
    rules = [
        (r"petronius|the arbiter", 'petronius'), (r"vinicius|marcus|the young tribune|the tribune|the young man|the young patrician", 'vinicius'),
        (r"lygia|callina|the maiden|the girl", 'lygia'), (r"\bnero\b|cæsar|caesar|ahenobarbus|bronzebeard", 'nero'), (r"seneca", 'seneca'),
        (r"\bpeter\b|the apostle|the old fisherman", 'peter'), (r"\bpaul\b", 'paul'), (r"lucan", 'lucan'),
        (r"chilo|chilonides|the greek", 'chilo'), (r"ursus|the lygian|the giant", 'ursus'), (r"poppæa|poppaea|augusta", 'poppaea'),
        (r"tigellinus", 'tigellinus'), (r"eunice", 'eunice'), (r"aulus|plautius|the old soldier|the old general", 'aulus'),
        (r"pomponia", 'pomponia'), (r"crispus", 'crispus'),
        (r"acte|glaucus|vitelius|vatinius|chrysothemis|tullius|senecio|nerva|nigidia|calvia|pythagoras|teiresias|demas|miriam|nazarius|linus|euricius|"
         r"atacinus|the slave|the freedman|the centurion|the soldier|one of|another|someone|a voice|the old man|the old woman|the woman|the boy|the child|"
         r"the physician|the prefect|the steward|the overseer|the crowd|the people", 'minor'),
    ]
    if re.search(r"\b(i|me)\b", t) and not re.search(r"\b(he|she|they|the)\b", t): return 'narrator'
    for rx, k in rules:
        if re.search(rx, t): return k
    return None
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

def paras_of(ch):
    return [p.strip() for p in re.split(r'\n{2,}', open(LIB.format(ch), encoding='utf-8').read()) if p.strip()]

def attribute(ch, paras, heads):
    res = {}; last = prev = None
    for pi, p in enumerate(paras):
        if pi in heads: continue
        ss = spans(p)
        if not any(k == 's' for _, _, k in ss): continue
        speaker = None
        for k, (a, b, kind) in enumerate(ss):
            if kind != 'n': continue
            seg = re.sub(r'\b(Mrs?|Mr|Dr)\.', r'\1', p[a:b]).replace('\n', ' ')
            m = re.match(r"\W*" + VERB + r"\s+([^,.;:!?—]{1,40})", seg)
            if m and k > 0: speaker = who_from(m.group(1), ch)
            if speaker is None:
                m2 = re.search(r"((?:the |The |old |Old |my |My |Mr |Dr |Long |Captain |Cap’n )?[A-Z][\w’.]*(?: [A-Z][\w’]*)?|the [a-z-]+(?: [a-z-]+)?|\bI\b)\s*,?\s*" + VERB + r"\b", seg)
                if m2: speaker = who_from(m2.group(1), ch)
            if speaker: break
        how = 'tag'
        if speaker is None:
            speaker, how = ((prev, 'INFERRED') if prev and prev != last else (last, 'INFERRED'))
            if speaker is None: speaker, how = 'minor', 'INFERRED'
        res[pi] = [(a, b, speaker, how) for a, b, kind in ss if kind == 's']
        if speaker != last: prev, last = last, speaker
    return res

# ── Curtin puts the speaker in the narration before the quote: "Seneca … laughed bitterly, and said,--“…”".
#    So: the nearest name before the quote in its own paragraph; failing that, a pronoun resolved to the
#    most recent character of that sex; failing that, the alternation of the exchange.
NAMES = [(r"Petronius", 'petronius'), (r"Vinicius|Marcus", 'vinicius'), (r"Lygia|Callina", 'lygia'), (r"Nero|Cæsar|Ahenobarbus|Bronzebeard", 'nero'),
         (r"Seneca", 'seneca'), (r"Peter|the Apostle", 'peter'), (r"Paul\b", 'paul'), (r"Lucan", 'lucan'), (r"Chilo|Chilonides", 'chilo'),
         (r"Ursus", 'ursus'), (r"Poppæa|Augusta", 'poppaea'), (r"Tigellinus", 'tigellinus'), (r"Eunice", 'eunice'), (r"Aulus|Plautius|the old general|the general|the old soldier", 'aulus'),
         (r"Pomponia", 'pomponia'), (r"Crispus", 'crispus'),
         (r"Acte|Chrysothemis|Nigidia|Calvia|Miriam|Rubria|Lilith", 'minor_f'),
         (r"Glaucus|Vitelius|Vatinius|Tullius|Senecio|Vestinius|Nerva|Pythagoras|Teiresias|Demas|Nazarius|Linus|Euricius|Atacinus|Hasta|Gulo|Iras|Aiton|Croton|Fabricius|Sporus|Terpnos|Diodorus|Aliturus|Pythagoras|the centurion|the slave|the freedman|the overseer|the physician", 'minor_m')]
FEMALE = {'lygia', 'pomponia', 'poppaea', 'eunice', 'minor_f'}
NAME_RX = re.compile('|'.join('(' + rx + ')' for rx, _ in NAMES))
def name_key(m):
    for i, (rx, k) in enumerate(NAMES):
        if m.group(i + 1): return k
def attribute2(ch, paras, heads):
    base = attribute(ch, paras, heads)
    last_m = last_f = None; out = {}
    def note(text):
        nonlocal last_m, last_f
        for m in NAME_RX.finditer(text):
            k = name_key(m)
            if k in FEMALE: last_f = k
            else: last_m = k
    for pi, p in enumerate(paras):
        if pi in base:
            first = base[pi][0]; spk, how = first[2], first[3]
            a0 = first[0]
            before = p[:a0]
            if how == 'INFERRED' and before.strip():                       # narration leads into the quote
                # the clause that carries the speech verb: after the last full stop before the quote
                cut = max(before.rfind('. '), before.rfind('! '), before.rfind('? '))
                sentence = before[cut + 1:] if cut >= 0 else before                     # the sentence that leads into the quote
                if not sentence.strip():                                                 # the quote opens its own sentence: look back one
                    prev = before[:cut + 1].rstrip()
                    c2 = max(prev[:-1].rfind('. '), prev[:-1].rfind('! '), prev[:-1].rfind('? '))
                    sentence = prev[c2 + 1:]
                semi = sentence.rfind('; ')
                clause = sentence[semi + 1:] if semi >= 0 else sentence
                sm = [name_key(m) for m in NAME_RX.finditer(sentence)]
                subj_m = next((k for k in sm if k not in FEMALE), None)                  # the sentence's first man, its usual subject
                subj_f = next((k for k in sm if k in FEMALE), None)
                head = re.sub(r"^[\s,—-]*(but|and|then|meanwhile|at last|after a while|here|now|so|when|finally|again|at that|on this|hereupon|therefore)\b[\s,]*", "", clause.strip(), flags=re.I)
                pv = re.search(r"\b(he|she)\b[^“”]{0,60}?\b(said|answered|replied|began|continued|inquired|asked|exclaimed|cried|added|whispered|repeated|burst out|called|spoke)\b", clause, re.I)
                m0 = NAME_RX.search(head)
                if pv:                                                                   # "…, he said": the pronoun carries it
                    if pv.group(1).lower() == 'he': spk, how = (subj_m or last_m or spk), 'PRONOUN'
                    else: spk, how = (subj_f or last_f or spk), 'PRONOUN'
                elif m0 and m0.start() < 40: spk = name_key(m0); how = 'NAMED'
                elif re.match(r"(he|his)\b", head, re.I): spk, how = (subj_m or last_m or spk), 'PRONOUN'
                elif re.match(r"(she|her)\b", head, re.I): spk, how = (subj_f or last_f or spk), 'PRONOUN'
                elif sm: spk = sm[0]; how = 'NAMED?'
            spk = {'minor_f': 'minor', 'minor_m': 'minor'}.get(spk, spk)
            out[pi] = [(a, b, spk, how) for a, b, _, _ in base[pi]]
            note(p)
            if spk in FEMALE: last_f = spk
            elif spk not in ('minor', 'narrator'): last_m = spk
        else:
            note(p)
    return out
