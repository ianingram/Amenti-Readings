/* ===========================================================================
   AMENTI READINGS · cut.js
   ---------------------------------------------------------------------------
   Takes a primary source out of the Amenti library and proposes a cue sheet.

   ── IT PROPOSES. IT DOES NOT DECIDE. ──────────────────────────────────────
   Splitting text on quotation marks is mechanical and a machine should do it.
   Deciding WHO IS SPEAKING inside those marks is not, and a machine that
   guesses will be wrong quietly.

   Cutting episode one by hand produced exactly one error of this kind:
   a splitter marked "Count Dracula?" as the Count, when it is Harker asking.
   Nothing in the punctuation says otherwise. One scene, one mistake. Across
   twenty-seven chapters, seven speakers and six document types, that is the
   whole job rather than a footnote.

   So this tool attributes what it can defend and FLAGS WHAT IT CANNOT, and
   prints the flagged cues first. An unattributed cue is not a failure of the
   tool; it is the tool declining to invent something.

   A WRONG ATTRIBUTION IS SILENT. It renders, it sounds plausible, and the
   wrong character has said the line. That is worse than a gap, and it is why
   confidence is reported per cue rather than averaged away.

   ── IT RUNS IN THE BROWSER ────────────────────────────────────────────────
   Paste the output into the repo through the GitHub web editor. No build
   step, no terminal, no local checkout.

     Amenti.cut.propose('bram-stoker/03-the-three-sisters.md', {
       work: 'dracula', episode: 3,
       narrator: 'Jonathan Harker',          // whose document this is
       speakers: ['Count Dracula']           // who else is in the scene
     });

   ── THE TEXT IS NEVER TOUCHED ─────────────────────────────────────────────
   Cue boundaries fall on quotation marks and nowhere else. The text inside a
   cue is byte-identical to the library file: not trimmed, not normalised, not
   re-wrapped. chunkText is deterministic and the R2 cache key contains the
   text, so a single changed character orphans every measure that cue has ever
   rendered.
   =========================================================================== */
(function () {
  'use strict';

  var Amenti = window.Amenti = window.Amenti || {};
  var LIB = 'https://raw.githubusercontent.com/ianingram/Amenti.live/main/library/';

  /* Verbs Stoker actually uses to attribute speech. Kept small on purpose:
     a long list invites false positives, and a false positive here is a
     wrong voice, which is the failure this tool exists to prevent. */
  var SAID = /\b(said|replied|answered|cried|asked|exclaimed|murmured|whispered|continued|went on|added|remarked)\b/i;

  var Cut = {

    /* ── the split ───────────────────────────────────────────────────────
       Paragraphs first, then quoted spans inside them. Everything outside a
       quotation is narration and belongs to whoever is keeping the document. */
    split: function (text) {
      var paras = text.split(/\n{2,}/).map(function (p) { return p.trim(); })
                      .filter(Boolean);
      var out = [];
      paras.forEach(function (p, pi) {
        var i = 0, any = false;
        var re = /[""]([^""]*)[""]|"([^"]*)"/g, m;
        while ((m = re.exec(p))) {
          any = true;
          if (m.index > i) {
            var pre = p.slice(i, m.index).trim();
            if (pre) out.push({ para: pi, kind: 'narration', text: pre });
          }
          out.push({ para: pi, kind: 'speech', text: m[0].trim() });
          i = m.index + m[0].length;
        }
        if (i < p.length) {
          var rest = p.slice(i).trim();
          if (rest) {
            /* AN UNTERMINATED QUOTATION IS STILL SPEECH.
               A passage cut out of a longer work can end inside a line of
               dialogue, and the closing mark never arrives. A splitter that
               requires a pair silently files that as narration — which is
               how the last line of episode one, spoken by the Count, was
               attributed to Harker and marked CERTAIN. It survived two
               rounds of attribution tuning because it was never classified
               as speech in the first place.

               The diagnosis matters as much as the fix: it looked like a
               bad guess and it was a bad split. */
            var opens = (rest.match(/[""]|"/g) || []).length;
            out.push({ para: pi,
                       kind: (opens % 2 === 1) ? 'speech' : 'narration',
                       text: rest,
                       unterminated: (opens % 2 === 1) || undefined });
          }
        }
        if (!any && !out.some(function (c) { return c.para === pi; })) {
          out.push({ para: pi, kind: 'narration', text: p });
        }
      });
      return out;
    },

    /* ── attribution ─────────────────────────────────────────────────────
       Narration is the document's keeper — that is certain, because the
       document says whose it is.

       Speech is the hard part, and the evidence is ranked:

         named     an attribution verb beside the speech names a speaker
         vocative  the speech addresses someone BY NAME, so the speaker is
                   somebody else — with two people in a scene that settles it
         other     a document's keeper is WRITING, not talking. In a journal
                   the speech is overwhelmingly somebody else's.
         none      flagged. Not guessed.

       TWO RULES WERE REMOVED AFTER THE FIRST RUN, and both are worth
       recording because they were plausible and wrong.

       ALTERNATION. 'the previous speaker was the other one' assumes speech
       alternates. It does not: the cue before a line of speech is almost
       always narration, so the rule read a stale speaker and flipped the
       wrong way. It scored 3 of 5 wrong on episode one.

       NO LINE OF SPEECH IS EVER 'CERTAIN', AND THAT IS THE DESIGN.
       The first version awarded 'certain' to a name beside an attribution
       verb. Tightening the rule to require the verb BETWEEN the name and the
       quotation raised the score from 20 of 24 to 23 — and the remaining
       error stayed 'certain', because the narration there genuinely names
       the wrong person beside a genuine verb. The evidence is real and it
       points the wrong way.

       That is not a regex that needs more work. A name near a verb near a
       quotation is ambiguous in English, and no amount of tuning resolves
       it. So the tool stops claiming otherwise: NARRATION is certain,
       because the document says whose it is, and EVERY LINE OF SPEECH caps
       at 'likely' and is listed for review.

       Eight lines to confirm costs a minute. Finding out at episode fourteen
       that the Count has been speaking in Harker's voice costs the archive. */
    attribute: function (cues, opt) {
      var narrator = opt.narrator || 'Narrator';
      var others = (opt.speakers || []).slice();
      var last = null;

      cues.forEach(function (c, i) {
        if (c.unterminated) {
          /* flagged by construction: the mark that would settle it is absent */
          c.role = (others.length === 1) ? others[0] : null;
          c.confidence = 'weak';
          c.why = 'UNTERMINATED QUOTATION \u2014 the passage ends inside this line, '
                + 'so there is no closing mark to split on. Confirm the speaker.';
          return;
        }
        if (c.kind === 'narration') {
          c.role = narrator; c.why = 'narration — this is their document';
          c.confidence = 'certain';
          return;
        }
        var before = (cues[i - 1] && cues[i - 1].kind === 'narration') ? cues[i - 1].text : '';
        var after  = (cues[i + 1] && cues[i + 1].kind === 'narration') ? cues[i + 1].text : '';
        var near   = before + ' \u00b6 ' + after;

        /* 1 · named, with an attribution verb between the name and the
               speech. Checked on each side separately: "the Count said:" in
               front is evidence; a name loose in the paragraph after is not. */
        var named = null, tight = false;
        others.concat([narrator]).forEach(function (who) {
          var sn = esc(who.split(' ').pop()), wn = esc(who);
          /* name ... verb ... <speech> */
          if (new RegExp('(' + wn + '|' + sn + ')[^.!?]{0,40}' + SAID.source, 'i').test(before)) {
            named = who; tight = true;
          }
          /* <speech> ... verb ... name */
          else if (new RegExp('^[^.!?]{0,40}' + SAID.source + '[^.!?]{0,30}(' + wn + '|' + sn + ')', 'i').test(after)) {
            named = who; tight = true;
          }
          else if (!named && new RegExp('(' + wn + '|' + sn + ')', 'i').test(near) && SAID.test(near)) {
            named = who;
          }
        });
        if (named) {
          c.role = named;
          c.confidence = tight ? 'likely' : 'weak';
          c.why = tight ? 'named, with an attribution verb between the name and the line'
                        : 'named somewhere nearby with an attribution verb \u2014 weak';
          last = named; return;
        }

        /* 2 · the speech addresses someone by name -> the speaker is not them */
        var addressed = null;
        others.concat([narrator]).forEach(function (who) {
          var surname = who.split(' ').pop();
          if (new RegExp('\\b(Mr\\.|Mrs\\.|Miss|Madam|' + esc(surname) + ')\\b').test(c.text)
              && new RegExp('\\b' + esc(surname) + '\\b').test(c.text)) addressed = who;
        });
        if (addressed) {
          var rest = others.concat([narrator]).filter(function (w) { return w !== addressed; });
          if (rest.length === 1) {
            c.role = rest[0]; c.confidence = 'likely';
            c.why = 'the line addresses ' + addressed + ' by name, so it is not theirs';
            last = c.role; return;
          }
        }

        /* 3 · THE KEEPER IS WRITING, NOT TALKING. This is the rule that
               replaced alternation. A journal, a letter, a phonograph diary
               — the person keeping it narrates, and the quoted speech in it
               is overwhelmingly somebody else's. With one other speaker in
               the scene, that settles it. Harker DOES speak aloud, rarely,
               and those are the cues to read. */
        if (others.length === 1) {
          c.role = others[0]; c.confidence = 'likely';
          c.why = 'the keeper of this document is writing, not talking \u2014 '
                + 'the only other speaker in the scene';
          last = others[0]; return;
        }

        /* 5 · decline */
        c.role = null; c.confidence = 'none';
        c.why = 'CANNOT ATTRIBUTE \u2014 name the speaker by hand';
      });
      return cues;
    },

    /* ── registers ───────────────────────────────────────────────────────
       Defaulted, never decided. The Speech Doctrine's six are a reading of a
       moment and a machine has no business choosing one. 'grave' for a
       document written after the fact, 'cool' for speech, and the proprietor
       changes what is wrong. */
    REG_DEFAULT: { narration: 'grave', speech: 'cool' },

    /* ── propose ─────────────────────────────────────────────────────────── */
    propose: function (libPath, opt) {
      opt = opt || {};
      return fetch(LIB + libPath, { cache: 'no-store' })
        .then(function (r) {
          if (!r.ok) throw new Error(libPath + ' -> ' + r.status);
          return r.text();
        })
        .then(function (text) {
          var cues = Cut.attribute(Cut.split(text.trim()), opt);
          var sheet = {
            work: opt.work || '', episode: opt.episode || 0,
            title: opt.title || '', document: opt.document || '',
            source: { library: 'library/' + libPath, text: opt.sourceText || '' },
            note: 'PROPOSED by tools/cut.js. Every cue marked low or none is a '
                + 'judgment the tool declined to make — read those first. The text '
                + 'is byte-identical to the library file and must stay so: the R2 '
                + 'cache key contains it.',
            cues: cues.map(function (c, i) {
              return { n: i + 1, para: c.para, role: c.role,
                       register: Cut.REG_DEFAULT[c.kind],
                       confidence: c.confidence, why: c.why, text: c.text };
            })
          };
          Cut.report(sheet);
          Cut.last = sheet;
          return sheet;
        });
    },

    report: function (sheet) {
      var cues = sheet.cues;
      /* EVERY LINE OF SPEECH IS LISTED. Not only the doubtful ones — the
         error that survived two rounds of tuning was marked 'certain', so
         'the tool is confident' is not a reason to skip a line. */
      var flag = cues.filter(function (c) {
        return c.confidence !== 'certain';
      });
      console.log('%c cut · ' + (sheet.source.library || '') + ' ',
                  'background:#d4a017;color:#000;padding:3px 8px;font-weight:700');
      console.log('   ' + cues.length + ' cues \u00b7 '
                  + cues.reduce(function (a, c) { return a + c.text.length; }, 0) + ' chars');
      var by = {};
      cues.forEach(function (c) { by[c.confidence] = (by[c.confidence] || 0) + 1; });
      console.log('   confidence:', JSON.stringify(by));

      if (flag.length) {
        console.log('\n%c CONFIRM ' + flag.length + ' LINE(S) OF SPEECH ',
                    'background:#c8102e;color:#fff;padding:2px 6px');
        console.log('   Narration is settled \u2014 the document says whose it is. Speech is not,');
        console.log('   and a wrong attribution is SILENT: it renders, it sounds right, and the');
        console.log('   wrong character has said the line. Read these; correct what is wrong.\n');
        flag.forEach(function (c) {
          console.log('   cue ' + c.n + '  [' + c.confidence + ']  ' + (c.role || '???'));
          console.log('      ' + c.why);
          console.log('      ' + c.text.slice(0, 90) + (c.text.length > 90 ? '\u2026' : ''));
        });
        console.log('\n   Amenti.cut.set(7, "Jonathan Harker")   to correct one');
      } else {
        console.log('\n   nothing flagged. Read it anyway — "certain" means the tool');
        console.log('   found evidence, not that the evidence was right.');
      }
      console.log('\n   Amenti.cut.json()     the sheet, ready to paste');
    },

    set: function (n, role) {
      var c = (Cut.last && Cut.last.cues || []).filter(function (x) { return x.n === n; })[0];
      if (!c) { console.warn('no cue ' + n); return; }
      c.role = role; c.confidence = 'set by hand'; c.why = 'attributed by the director';
      console.log('   cue ' + n + ' -> ' + role);
      return c;
    },

    register: function (n, reg) {
      var c = (Cut.last && Cut.last.cues || []).filter(function (x) { return x.n === n; })[0];
      if (!c) { console.warn('no cue ' + n); return; }
      c.register = reg;
      console.log('   cue ' + n + ' register -> ' + reg);
      return c;
    },

    /* The sheet as it will live in the repo. Working fields are dropped —
       confidence and why are scaffolding for the cut, not provenance. */
    json: function () {
      if (!Cut.last) { console.warn('nothing cut yet'); return; }
      var open = Cut.last.cues.filter(function (c) {
        return c.confidence === 'none' || c.confidence === 'low';
      });
      if (open.length) {
        console.warn(open.length + ' cue(s) are still unresolved. Printing anyway — '
                   + 'but a low-confidence attribution will speak in the wrong voice.');
      }
      var out = JSON.parse(JSON.stringify(Cut.last));
      out.cues = out.cues.map(function (c) {
        return { n: c.n, role: c.role, register: c.register, text: c.text };
      });
      var s = JSON.stringify(out, null, 2);
      console.log(s);
      return s;
    }
  };

  function esc(s) { return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  Amenti.cut = Cut;
  console.log('%c Amenti cut ready ', 'background:#d4a017;color:#000;padding:2px 6px',
              '\u00b7 Amenti.cut.propose("bram-stoker/03-the-three-sisters.md", {work:"dracula",episode:3,narrator:"Jonathan Harker",speakers:["Count Dracula"]})');
})();
