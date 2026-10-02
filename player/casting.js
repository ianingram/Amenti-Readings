/* ===========================================================================
   AMENTI READINGS · casting.js
   ---------------------------------------------------------------------------
   The director's desk. Opens before a reading, shows who is cast in every
   role, and lets a role be recast from the ledger.

   ── A DEFAULT, NOT A DECISION ─────────────────────────────────────────────
   cast.json is the house casting. This panel treats it as a starting point.
   An override is stored in localStorage under the work's key and applied at
   read time, so trying a different Van Helsing costs nothing and commits
   nothing. Export writes the current cast as JSON to paste into cast.json
   when a choice has earned permanence.

   ── RECASTING IS PER WORK, NOT PER EPISODE ────────────────────────────────
   Van Helsing is one man across twenty-seven chapters. A swap replaces him
   everywhere in the work, by instruction. Per-episode casting was considered
   and declined: it would let the same character arrive in two voices, which
   is not a staging choice, it is a mistake with a switch on it.

   ── A SWAP IS NOT FREE, AND THE PANEL SAYS SO ─────────────────────────────
   The R2 cache key is TTS_MODEL + voice + style + text. A role's voice and
   style are in that key, so recasting a role INVALIDATES EVERY LINE THAT ROLE
   HAS EVER SPOKEN. On an unrendered sheet that costs nothing. On a work with
   ten episodes in the archive it is a re-render of that character's entire
   part, at 5-16 seconds a cue, paid again.

   The panel counts the cues at risk and prints the number before the swap,
   because the alternative is finding out afterwards.

   ── IT CHANGES NO AUDIO PATH ──────────────────────────────────────────────
   This file picks names. It does not speak, does not chunk, does not compose
   a style, and never calls /speak. reader.js hands the chosen name to
   Amenti.throttle.speak exactly as before. One chunker, one style
   composition, one cache.
   =========================================================================== */
(function () {
  'use strict';

  var Amenti = window.Amenti = window.Amenti || {};
  var R = Amenti.reading;
  if (!R) {
    console.warn('Casting: Amenti.reading is not present. Load player/reader.js first.');
    return;
  }

  var KEY = 'amenti.casting.';          /* + work */
  /* THE POOL IS names.csv, THE FILE THE ENGINE RESOLVES AGAINST (2 Oct 2026).
     This read AMENTI_CONFIG.LEDGER_CSV_URL — the Google Sheet, and a
     DIFFERENT TAB (gid 1598709533) from the one the engine used
     (gid 1225210076). So the panel could offer a name the reading could not
     find. The engine publishes the URL it actually read; this uses that. */
  function poolUrl() {
    var T = window.Amenti && window.Amenti.throttle;
    return (T && T.rosterUrl) || 'https://ianingram.github.io/Amenti.live/names.csv';
  }

  var C = {
    pool: null,          /* the 1,011, loaded once */
    work: null,
    rows: [],

    /* ── overrides ─────────────────────────────────────────────────────── */
    overrides: function (work) {
      try { return JSON.parse(localStorage.getItem(KEY + work) || '{}'); }
      catch (e) { return {}; }
    },
    setOverride: function (work, role, name) {
      var o = C.overrides(work);
      if (name) o[role] = name; else delete o[role];
      try { localStorage.setItem(KEY + work, JSON.stringify(o)); } catch (e) {}
      return o;
    },
    clear: function (work) {
      try { localStorage.removeItem(KEY + (work || C.work)); } catch (e) {}
      console.log('Casting: overrides cleared for ' + (work || C.work) + '. House cast restored.');
    },

    /* ── the casting pool ──────────────────────────────────────────────────
       Parsed from the same ledger the engine resolves against, so a name
       chosen here is a name resolveVoice will find. Anything else would be
       a panel that offers voices the reading cannot use. */
    loadPool: function () {
      if (C.pool) return Promise.resolve(C.pool);
      var url = poolUrl();
      return fetch(url, { cache: 'no-store' })
        .then(function (r) {
          if (!r.ok) throw new Error('Casting: ' + url + ' -> ' + r.status);
          return r.text();
        })
        .then(function (text) {
          var rows = C._csv(text);
          var H = rows[0].map(function (h) { return String(h).toLowerCase().replace(/[^a-z0-9]/g, ''); });
          function ix() {
            for (var a = 0; a < arguments.length; a++) {
              var i = H.indexOf(arguments[a]); if (i >= 0) return i;
            } return -1;
          }
          var n = ix('fullname', 'name'), g = ix('gender'), d = ix('dialect'),
              v = ix('voice'), rg = ix('region'), t = ix('title'),
              gl = ix('glyph'), ac = ix('accent');
          C.pool = rows.slice(1).filter(function (r) { return r[n] && r[n].trim(); })
            .map(function (r) {
              return { name: r[n].trim(), gender: (r[g] || '').trim(),
                       dialect: (r[d] || '').trim(), voice: (r[v] || '').trim(),
                       region: (r[rg] || '').trim(), title: (r[t] || '').trim(),
                       /* Glyph and Accent are filled on 34 of 1,011 rows, so the
                          playbill cannot lean on them. They are read where present
                          and defaulted where not. */
                       glyph: (gl >= 0 ? (r[gl] || '').trim() : ''),
                       accent: (ac >= 0 ? (r[ac] || '').trim() : '') };
            });
          return C.pool;
        });
    },
    _csv: function (text) {
      if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);
      var rows = [], row = [], f = '', q = false, i = 0;
      while (i < text.length) {
        var c = text[i];
        if (q) {
          if (c === '"') { if (text[i + 1] === '"') { f += '"'; i += 2; continue; } q = false; i++; continue; }
          f += c; i++; continue;
        }
        if (c === '"') { q = true; i++; continue; }
        if (c === ',') { row.push(f); f = ''; i++; continue; }
        if (c === '\n') { row.push(f); rows.push(row); row = []; f = ''; i++; continue; }
        if (c === '\r') { i++; continue; }
        f += c; i++;
      }
      if (f.length || row.length) { row.push(f); rows.push(row); }
      return rows;
    },

    /* ── AUDITION ──────────────────────────────────────────────────────────
       Search the pool by dialect, region, name or manner. This is how a role
       is recast: type what the part needs and read what the ledger has. */
    audition: function (query, limit) {
      return C.loadPool().then(function (pool) {
        var q = String(query || '').toLowerCase();
        var hits = pool.filter(function (p) {
          return (p.name + ' ' + p.dialect + ' ' + p.region + ' ' + p.voice + ' ' + p.title)
                 .toLowerCase().indexOf(q) >= 0;
        }).slice(0, limit || 20);
        console.log('%c audition · "' + query + '" · ' + hits.length + ' of ' + pool.length + ' ',
                    'background:#d4a017;color:#000;padding:2px 6px');
        hits.forEach(function (p) {
          console.log('   ' + p.name.padEnd(26) + ' | ' + (p.dialect || '—').padEnd(44) + ' | ' + p.voice);
        });
        if (!hits.length) {
          console.log('   nothing. The ledger has no voice of that description — ' +
                      'add one rather than approximating. Yorkshire and Texan are ' +
                      'both known gaps, recorded in cast.json.');
        }
        return hits;
      });
    },

    /* ── THE SHEET ─────────────────────────────────────────────────────────
       The cast as it stands for a work: house casting, with any override
       applied and marked. */
    sheet: function (work) {
      work = work || (R.sheet && R.sheet.work);
      if (!work) return Promise.reject(new Error('no work — load a cue sheet first'));
      C.work = work;
      var load = R.cast ? Promise.resolve(R.cast) : R._json('cast.json').then(function (c) { R.cast = c; return c; });
      return Promise.all([load, C.loadPool()]).then(function (both) {
        var cast = both[0], pool = both[1];
        var roles = (cast.roles && cast.roles[work]) || {};
        var over = C.overrides(work);
        var byName = {};
        pool.forEach(function (p) { byName[p.name.toLowerCase()] = p; });
        C.rows = Object.keys(roles).map(function (slug) {
          var house = roles[slug].ledger_name;
          var now = over[slug] || house;
          var fig = byName[String(now).toLowerCase()];
          return { role: slug, house: house, cast: now,
                   swapped: !!over[slug], found: !!fig,
                   dialect: fig ? fig.dialect : '', voice: fig ? fig.voice : '',
                   why: roles[slug].why || '' };
        });
        C._print();
        return C.rows;
      });
    },

    _print: function () {
      console.log('%c CASTING · ' + C.work + ' ',
                  'background:#111;color:#d4a017;padding:3px 8px;font-weight:700');
      C.rows.forEach(function (r) {
        var mark = r.swapped ? ' *RECAST*' : '';
        var warn = r.found ? '' : '   << NOT IN LEDGER — will speak in a neutral voice';
        console.log('   ' + r.role.padEnd(18) + ' ' + r.cast.padEnd(24) +
                    ' | ' + (r.dialect || '—').padEnd(42) + mark + warn);
      });
      console.log('\n   Amenti.casting.audition("hungarian")        see who is available');
      console.log('   Amenti.casting.recast("van-helsing","Nikola Tesla")');
      console.log('   Amenti.casting.restore("van-helsing")       back to the house cast');
      console.log('   Amenti.casting.export()                     JSON for cast.json');
    },

    /* ── RECAST ────────────────────────────────────────────────────────────
       The cost warning is the point of this function. Everything else is a
       localStorage write. */
    recast: function (role, name) {
      if (!C.work) { console.warn('Casting: load a cue sheet first.'); return; }
      return C.loadPool().then(function (pool) {
        var fig = null;
        pool.forEach(function (p) { if (p.name.toLowerCase() === String(name).toLowerCase()) fig = p; });
        if (!fig) {
          console.warn('Casting: "' + name + '" is not in the ledger. resolveVoice would ' +
                       'fall back to a neutral voice RATHER THAN FAILING, so this would be ' +
                       'silent at runtime. Try Amenti.casting.audition("' +
                       String(name).split(' ').pop().toLowerCase() + '").');
          return null;
        }
        /* how much does this cost? count the cues this role speaks. */
        var cues = (R.sheet && R.sheet.cues) || [];
        var hit = cues.filter(function (c) {
          var s = String(c.role || '').toLowerCase().replace(/[^a-z0-9]+/g, '-');
          return s === role;
        });
        var chars = hit.reduce(function (a, c) { return a + c.text.length; }, 0);

        C.setOverride(C.work, role, fig.name);
        console.log('%c recast · ' + role + ' -> ' + fig.name + ' ',
                    'background:#0a2;color:#fff;padding:2px 6px');
        console.log('   ' + fig.dialect + '  ·  ' + fig.voice);
        console.log('   IN THIS EPISODE: ' + hit.length + ' cues, ' + chars + ' characters.');
        console.log('   THE STYLE IS PART OF THE CACHE KEY, so every line this role has ' +
                    'already rendered — in THIS episode and every other one in the work — ' +
                    'is now a miss and will render again at 5-16s a cue. Free if nothing ' +
                    'has been rendered yet.');
        return C.sheet(C.work);
      });
    },

    restore: function (role) {
      C.setOverride(C.work, role, null);
      return C.sheet(C.work);
    },

    /* ── export ────────────────────────────────────────────────────────────
       An override lives in one browser. This prints the block to paste into
       cast.json when a choice should outlive the session. */
    'export': function () {
      var out = {};
      C.rows.forEach(function (r) { out[r.role] = { ledger_name: r.cast }; });
      var json = JSON.stringify(out, null, 2);
      console.log('%c cast.json · roles.' + C.work + ' ',
                  'background:#111;color:#d4a017;padding:2px 6px');
      console.log(json);
      try { if (window.copy) window.copy(json); } catch (e) {}
      return json;
    }
  };

  Amenti.casting = C;

  /* ── the hook ──────────────────────────────────────────────────────────
     reader.js resolves a role through cast.json. This wraps that lookup so
     an override wins, and leaves the original in place beneath it: with no
     override, behaviour is byte-identical and the cache is untouched. */
  var houseNameFor = R.nameFor;
  R.nameFor = function (cue) {
    var work = R.sheet && R.sheet.work;
    if (work) {
      var o = C.overrides(work);
      var slug = String(cue.role || '').toLowerCase().replace(/[^a-z0-9]+/g, '-');
      if (o[slug]) return o[slug];
    }
    return houseNameFor.call(R, cue);
  };

  console.log('%c Amenti casting desk ready ', 'background:#d4a017;color:#000;padding:2px 6px',
              '· Amenti.casting.sheet() after loading a cue sheet');
})();
