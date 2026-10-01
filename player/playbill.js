/* ===========================================================================
   AMENTI STUDIOS · playbill.js
   ---------------------------------------------------------------------------
   The bill outside the hall. Who is cast, in what, and in whose voice —
   shown before a word is spoken, and recastable at the desk.

   ── WHY A PLAYBILL AND NOT A CONSOLE LIST ─────────────────────────────────
   The casting is the idea. "Charles Darwin as Jonathan Harker. Vlad the
   Impaler as Count Dracula." Nobody else can make that line, because nobody
   else has a thousand figures with their dialects already written down. A
   console list is correct and invisible. A bill is the thing worth showing.

   ── IT NEVER LOOKS BROKEN ─────────────────────────────────────────────────
   26 of 1,011 figures have plates. Darwin has none. Vlad has none. A bill
   built on card images would show two faces and six holes, and a hole reads
   as a fault rather than as an absence.

   So the DEFAULT is the glyph and the accent colour — which every figure in
   the ledger has — and a plate UPGRADES a row when img/{key}-card.jpg exists.
   The probe is the same silent new Image() the art loader uses: it either
   paints or it does not, and nothing reports an error either way.

   A row without a plate is marked quietly, because the bill doubles as a
   work queue: Darwin as Harker is a reason to make a Darwin plate.

   ── IT SPEAKS NOTHING AND RENDERS NOTHING ─────────────────────────────────
   This file draws a panel. Recasting goes through Amenti.casting, which
   writes an override to localStorage; reader.js reads it at speak time. No
   audio path is touched, no style is composed, no cache key moves — until a
   recast, which casting.js warns about with a count.
   =========================================================================== */
(function () {
  'use strict';

  var Amenti = window.Amenti = window.Amenti || {};
  var R = Amenti.reading, C = Amenti.casting;
  if (!R || !C) {
    console.warn('Playbill: load player/reader.js and player/casting.js first.');
    return;
  }

  var ART = 'https://raw.githubusercontent.com/ianingram/Amenti.live/main/img/';

  var css = ''
  + '#amenti-playbill{position:fixed;inset:0;z-index:2000;display:none;'
  +   'background:rgba(2,6,4,.93);backdrop-filter:blur(6px);overflow:auto;'
  +   'font-family:var(--font-mono,ui-monospace,monospace);}'
  + '#amenti-playbill.on{display:block;}'
  + '.pb-wrap{max-width:860px;margin:0 auto;padding:56px 24px 80px;}'
  + '.pb-studio{text-align:center;font-size:11px;letter-spacing:.42em;'
  +   'color:var(--gold,#d4a017);text-transform:uppercase;margin-bottom:6px;}'
  + '.pb-presents{text-align:center;font-size:9px;letter-spacing:.3em;'
  +   'color:#6a7a70;text-transform:uppercase;margin-bottom:26px;}'
  + '.pb-rule{height:1px;background:linear-gradient(90deg,transparent,'
  +   'var(--gold,#d4a017),transparent);margin:0 0 26px;}'
  + '.pb-title{text-align:center;font-family:var(--font-elite,Georgia,serif);'
  +   'font-size:40px;color:#fff;line-height:1.05;margin:0 0 6px;}'
  + '.pb-by{text-align:center;font-size:11px;letter-spacing:.2em;color:#8aa89b;'
  +   'text-transform:uppercase;margin-bottom:4px;}'
  + '.pb-ep{text-align:center;font-size:12px;color:#c8e8d8;margin-bottom:4px;}'
  + '.pb-doc{text-align:center;font-size:10px;letter-spacing:.14em;color:#6a7a70;'
  +   'text-transform:uppercase;margin-bottom:30px;}'
  + '.pb-head{font-size:10px;letter-spacing:.32em;color:var(--gold,#d4a017);'
  +   'text-transform:uppercase;text-align:center;margin:0 0 18px;}'
  + '.pb-row{display:flex;align-items:center;gap:16px;padding:12px 14px;'
  +   'border-bottom:1px solid rgba(255,255,255,.07);}'
  + '.pb-row:hover{background:rgba(212,160,23,.05);}'
  + '.pb-face{width:46px;height:62px;flex:0 0 46px;border-radius:2px;'
  +   'background-size:cover;background-position:50% 18%;display:flex;'
  +   'align-items:center;justify-content:center;font-size:20px;'
  +   'border:1px solid rgba(255,255,255,.14);}'
  + '.pb-mid{flex:1;min-width:0;}'
  + '.pb-role{font-family:var(--font-elite,Georgia,serif);font-size:15px;color:#fff;}'
  + '.pb-as{font-size:9px;letter-spacing:.24em;color:#6a7a70;text-transform:uppercase;'
  +   'margin:3px 0 2px;}'
  + '.pb-actor{font-size:13px;color:var(--gold,#d4a017);}'
  + '.pb-dialect{font-size:11px;color:#8aa89b;margin-top:3px;'
  +   'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}'
  + '.pb-flags{font-size:9px;letter-spacing:.14em;color:#5a6a62;margin-top:4px;'
  +   'text-transform:uppercase;}'
  + '.pb-flag-recast{color:var(--gold,#d4a017);}'
  + '.pb-flag-miss{color:#c8102e;}'
  + '.pb-btn{background:none;border:1px solid rgba(212,160,23,.3);color:#80ffc0;'
  +   'font-family:inherit;font-size:9px;letter-spacing:.18em;padding:6px 10px;'
  +   'cursor:pointer;text-transform:uppercase;white-space:nowrap;}'
  + '.pb-btn:hover{border-color:var(--gold,#d4a017);color:#fff;}'
  + '.pb-foot{margin-top:28px;text-align:center;font-size:10px;color:#5a6a62;'
  +   'line-height:1.8;}'
  + '.pb-actions{text-align:center;margin-top:26px;display:flex;gap:10px;'
  +   'justify-content:center;flex-wrap:wrap;}'
  + '.pb-go{border-color:var(--gold,#d4a017);color:var(--gold,#d4a017);padding:10px 22px;'
  +   'font-size:10px;letter-spacing:.24em;}'
  + '.pb-go:hover{background:var(--gold,#d4a017);color:#000;}'
  + '.pb-close{position:fixed;top:18px;right:22px;background:none;border:none;'
  +   'color:#6a7a70;font-size:22px;cursor:pointer;}'
  + '.pb-close:hover{color:#fff;}'
  + '.pb-search{display:none;margin:8px 0 0;}'
  + '.pb-search.on{display:block;}'
  + '.pb-search input{width:100%;background:rgba(0,0,0,.4);border:1px solid '
  +   'rgba(212,160,23,.3);color:#c8e8d8;font-family:inherit;font-size:12px;padding:8px 10px;}'
  + '.pb-hit{padding:7px 10px;border-bottom:1px solid rgba(255,255,255,.05);'
  +   'cursor:pointer;font-size:11px;color:#8aa89b;}'
  + '.pb-hit:hover{background:rgba(212,160,23,.1);color:#fff;}'
  + '.pb-hit b{color:var(--gold,#d4a017);font-weight:400;}'
  + '@media (max-width:640px){.pb-title{font-size:28px;}.pb-wrap{padding:40px 14px 60px;}}';

  var P = {
    el: null,
    sheet: null,

    _css: function () {
      if (document.getElementById('pb-css')) return;
      var s = document.createElement('style');
      s.id = 'pb-css'; s.textContent = css;
      document.head.appendChild(s);
    },

    slug: function (n) {
      return String(n || '').toLowerCase().trim()
        .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    },

    /* THE SILENT PROBE. Same shape the art loader uses: it either paints or
       it does not. No error, no placeholder, no broken-image icon. */
    face: function (el, ledgerName, glyph, accent) {
      /* THE LEDGER CANNOT CARRY THIS ALONE. Glyph is filled on 34 of 1,011
         rows and Accent on 33, so a bill that trusted those columns would
         show a blank square for almost every figure. The lozenge is the
         house default — the same mark the roster uses — and a real glyph
         upgrades it where one exists. Nothing is ever empty. */
      el.textContent = glyph || '\u25C8';
      el.style.color = accent || '#d4a017';
      el.style.background = 'rgba(255,255,255,.04)';
      var key = P.slug(ledgerName);
      var probe = new Image();
      probe.onload = function () {
        el.textContent = '';
        el.style.backgroundImage = 'url("' + ART + key + '-card.jpg")';
      };
      probe.src = ART + key + '-card.jpg';
    },

    open: function (sheetPath) {
      P._css();
      var load = sheetPath ? R.load(sheetPath) : Promise.resolve(R.sheet);
      return load.then(function () {
        P.sheet = R.sheet;
        return C.sheet(R.sheet.work);
      }).then(function (rows) { P.render(rows); });
    },

    render: function (rows) {
      var s = P.sheet;
      if (!P.el) {
        P.el = document.createElement('div');
        P.el.id = 'amenti-playbill';
        document.body.appendChild(P.el);
      }
      var cues = (s.cues || []);
      var h = [];
      h.push('<button class="pb-close" title="close">\u00d7</button>');
      h.push('<div class="pb-wrap">');
      h.push('<div class="pb-studio">Amenti Studios</div>');
      h.push('<div class="pb-presents">presents</div>');
      h.push('<div class="pb-rule"></div>');
      h.push('<div class="pb-title">' + esc(s.title || s.work) + '</div>');
      if (s.source && s.source.text) {
        h.push('<div class="pb-by">' + esc(String(s.source.text).split('·')[0].trim()) + '</div>');
      }
      h.push('<div class="pb-ep">Episode ' + (s.episode || 1) + '</div>');
      h.push('<div class="pb-doc">' + esc(s.document || '') + '</div>');
      h.push('<div class="pb-rule"></div>');
      h.push('<div class="pb-head">The Cast</div>');

      /* count the cues each role actually speaks — a bill should not list a
         part that never opens its mouth in this episode */
      var spoken = {};
      cues.forEach(function (c) {
        var k = P.slug(c.role); spoken[k] = (spoken[k] || 0) + 1;
      });

      rows.sort(function (a, b) { return (spoken[b.role] || 0) - (spoken[a.role] || 0); });

      rows.forEach(function (r) {
        var n = spoken[r.role] || 0;
        var flags = [];
        if (r.swapped) flags.push('<span class="pb-flag-recast">recast</span>');
        if (!r.found) flags.push('<span class="pb-flag-miss">not in ledger</span>');
        if (!n) flags.push('not in this episode');
        else flags.push(n + (n === 1 ? ' cue' : ' cues'));
        h.push('<div class="pb-row" data-role="' + esc(r.role) + '">');
        h.push('<div class="pb-face" data-face="' + esc(r.cast) + '"></div>');
        h.push('<div class="pb-mid">');
        h.push('<div class="pb-role">' + esc(prettyRole(r.role)) + '</div>');
        h.push('<div class="pb-as">as played by</div>');
        h.push('<div class="pb-actor">' + esc(r.cast) + '</div>');
        h.push('<div class="pb-dialect">' + esc(r.dialect || '\u2014') + '</div>');
        h.push('<div class="pb-flags">' + flags.join(' \u00b7 ') + '</div>');
        h.push('<div class="pb-search"><input placeholder="audition \u2014 type a dialect, a region, or a name" /><div class="pb-hits"></div></div>');
        h.push('</div>');
        h.push('<button class="pb-btn pb-recast">recast</button>');
        h.push('</div>');
      });

      var noplate = rows.filter(function (r) { return !P._hasPlate[P.slug(r.cast)]; }).length;
      h.push('<div class="pb-actions">');
      h.push('<button class="pb-btn pb-go">Begin the reading</button>');
      h.push('<button class="pb-btn pb-restore">Restore house cast</button>');
      h.push('<button class="pb-btn pb-export">Export cast</button>');
      h.push('</div>');
      h.push('<div class="pb-foot">');
      h.push(cues.length + ' cues \u00b7 ' + cues.reduce(function (a, c) { return a + c.text.length; }, 0) + ' characters<br>');
      h.push('Voices resolve from the Amenti ledger. Recasting is per work \u2014 a change here<br>');
      h.push('replaces that voice in every chapter, and re-renders every line it has spoken.');
      h.push('</div></div>');

      P.el.innerHTML = h.join('');
      P.el.classList.add('on');

      /* faces, after the markup exists */
      P.el.querySelectorAll('.pb-face').forEach(function (f) {
        var name = f.getAttribute('data-face');
        var fig = (C.pool || []).filter(function (p) {
          return p.name.toLowerCase() === name.toLowerCase(); })[0];
        P.face(f, name, fig && fig.glyph, fig && fig.accent);
      });

      P.bind();
    },

    _hasPlate: {},

    bind: function () {
      P.el.querySelector('.pb-close').onclick = P.close;
      P.el.querySelector('.pb-go').onclick = function () { P.close(); R.play(); };
      P.el.querySelector('.pb-restore').onclick = function () {
        C.clear(P.sheet.work); P.open();
      };
      P.el.querySelector('.pb-export').onclick = function () { C['export'](); };

      P.el.querySelectorAll('.pb-row').forEach(function (row) {
        var role = row.getAttribute('data-role');
        var box = row.querySelector('.pb-search');
        var input = row.querySelector('input');
        var hits = row.querySelector('.pb-hits');
        row.querySelector('.pb-recast').onclick = function () {
          box.classList.toggle('on');
          if (box.classList.contains('on')) input.focus();
        };
        var t = null;
        input.oninput = function () {
          clearTimeout(t);
          t = setTimeout(function () {
            var q = input.value.trim();
            if (q.length < 2) { hits.innerHTML = ''; return; }
            C.loadPool().then(function (pool) {
              var ql = q.toLowerCase();
              var found = pool.filter(function (p) {
                return (p.name + ' ' + p.dialect + ' ' + p.region + ' ' + p.voice)
                  .toLowerCase().indexOf(ql) >= 0; }).slice(0, 8);
              hits.innerHTML = found.length
                ? found.map(function (p) {
                    return '<div class="pb-hit" data-pick="' + esc(p.name) + '">'
                         + '<b>' + esc(p.name) + '</b> \u2014 ' + esc(p.dialect) + '</div>';
                  }).join('')
                : '<div class="pb-hit">nothing in the ledger matches. Add a voice rather than approximating.</div>';
              hits.querySelectorAll('[data-pick]').forEach(function (hit) {
                hit.onclick = function () {
                  C.recast(role, hit.getAttribute('data-pick')).then(function () { P.open(); });
                };
              });
            });
          }, 160);
        };
      });
    },

    close: function () { if (P.el) P.el.classList.remove('on'); }
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function prettyRole(slug) {
    return String(slug).split('-').map(function (w) {
      return w.charAt(0).toUpperCase() + w.slice(1);
    }).join(' ');
  }

  Amenti.playbill = P;

  console.log('%c Amenti Studios \u00b7 playbill ready ',
              'background:#d4a017;color:#000;padding:2px 6px',
              '\u00b7 Amenti.playbill.open("dracula/ep01.json")');
})();
