# Amenti-Readings

Staged readings of public-domain works, voiced by figures drawn from the
Amenti ledger. Scripts and a thin player live here. **The voice does not.**

---

## What this repo is

A reading is a **cue sheet**: an ordered list of `{role, register, text}`.
Each cue names a role, the role names a ledger figure by full name, and the
Amenti engine resolves that name into a voice and a style. The repo holds the
scripts. The speaking is done by Amenti.live.

    cast.json              one cast, every work — roles mapped to ledger names
    dracula/index.json     the chapter map
    dracula/ep01.json      a cue sheet
    player/reader.js       walks a cue sheet, calls the engine in order

---

## The rule that governs everything here

**ONE CHUNKER, ONE STYLE COMPOSITION, ONE CACHE.**

The reader calls back into Amenti.live's existing speech engine. It never
carries its own. Page1 has already retired its separate read-aloud pipeline —
every voice call on that page goes through `Amenti.throttle.speak`, chunking at
320 and streaming, with one shared cache behind it. A second speech path here
would mean a second cache namespace, which is exactly the Page2 condition the
Voice Path brief says to retire rather than reproduce.

    Amenti.throttle.speak(text, { style, voice })
    resolveVoice(fullName) -> { voice, style }

Readings run on **Page1 only** until Page2 is unified onto the throttle.

---

## Three constraints, all load-bearing

**The text is passed through unchanged.** `chunkText` is deterministic — the
same text always splits into the same measures — and the R2 cache key is
`TTS_MODEL + voice + style + text`. Reformat a passage between renders and
every stored measure it produced is orphaned. Cue boundaries fall on quotation
marks; the text inside a cue is byte-identical to the library file it came
from. **The script splits. It never rewrites.**

**Punctuation is the score.** `restFor` reads the last character of each
measure and chooses the silence: 0.85s at a paragraph end, 0.38s after a
sentence, 0.16s after a comma. The author's own pointing sets the pacing, which
is one more reason not to touch the text.

**Pace is asked in words, never by resampling.** Raising the playback rate
raises the pitch and every figure speaks like a chipmunk. Tempo goes into the
style string — and the style string is part of the cache key, so it is decided
once.

---

## Casting

Roles resolve **by full name** against the ledger, which carries `Gender`,
`Dialect`, `Voice` and `Region` filled on all 1,011 rows. `resolveVoice` joins
on name lower-cased and falls back to a neutral voice when a figure is absent
**rather than failing** — so a mistyped name is silent, not loud. Every name in
`cast.json` was verified against the live ledger.

Registers are the Speech Doctrine's six — warm, cool, sharp, grave, danger,
humour — and are chosen **per cue, not per role**. A character does not have a
register; a moment does.

---

## Why Dracula is first

It is epistolary, and Stoker names the document type at the head of every
chapter: a journal, a letter, a ship's log, a phonograph diary, a newspaper
cutting. **The book is already written as a cast recording.** The entrances and
exits are on the page and a staged reading does not have to invent them.

*A Christmas Carol* is second, and for the mirror reason: one narrator, five
staves, a complete arc in 28,000 words — and Dickens toured it as a staged
reading for fifteen years, performing his own cut.

---

Ingram Manor LLC · 2026 · All Rights Reserved
