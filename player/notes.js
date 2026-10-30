/* ===========================================================================
   Amenti-Readings/player/notes.js — the production notepad (30 Oct 2026)

   Ian, watching a book: press N (or the NOTE button), type what works or
   doesn't, Save. The reading pauses while the pad is open and resumes after.

   Each note is saved as its own small JSON file on the Media Door:
     notes/<work>/<book>/<UTC stamp>-chNN-cNN.json
   using the upload key this browser already keeps for the Media Door page
   (localStorage 'amenti-media-key' — every repo shares ianingram.github.io).
   Claude reads them with GET /list?prefix=notes/ and GET /m/<path>.

   A note carries: chapter (episode), cue number, who is speaking, the first
   words of the cue, the picture on screen (file name), seconds into the cue,
   a quick tag, and the text. A copy stays in this browser so the pad can show
   your notes this session; if the upload fails the note waits there and is
   sent again next time.

   Load after reader.js and art.js:
     <script src="https://ianingram.github.io/Amenti-Readings/player/notes.js"
             data-book="book1"></script>
   =========================================================================== */
(function () {
  'use strict';
  var A = window.Amenti || {}, R = A.reading;
  if (!R) return;
  var me = document.currentScript;
  var BOOK = (me && me.getAttribute('data-book')) || 'book';
  var DOOR = 'https://amenti-media.ingram-ian.workers.dev';
  var TAGS = ['Works', 'Redo picture', 'Animate', 'Sound', 'Timing', 'Text'];
  var LS_KEY = 'amenti-media-key', LS_Q = 'amenti-notes-queue', LS_MINE = 'amenti-notes-mine';

  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function jget(k) { try { return JSON.parse(ls(k) || '[]'); } catch (e) { return []; } }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }

  var css = document.createElement('style');
  css.textContent =
      '#an-btn{position:fixed;right:16px;bottom:58px;z-index:1960;background:rgba(7,9,12,.6);border:1px solid rgba(212,160,23,.55);'
    + 'color:#d4a017;font:10px/1 Georgia,serif;letter-spacing:.24em;text-transform:uppercase;padding:9px 12px;cursor:pointer}'
    + '#an-btn b{font-weight:400;color:#e8dcc0;margin-left:6px}'
    + '#an-pad{position:fixed;right:16px;bottom:100px;z-index:1970;width:min(440px,calc(100vw - 32px));background:#f1e7cd;color:#22170b;'
    + 'border:1px solid #3b2a17;box-shadow:0 14px 40px rgba(0,0,0,.6);font:15px/1.45 Georgia,serif;display:grid;gap:10px;padding:14px 16px 16px}'
    + '#an-pad[hidden]{display:none}'
    + '#an-pad .ctx{font:12px/1.5 ui-monospace,Menlo,monospace;color:#5a4428;word-break:break-word}'
    + '#an-pad .ctx i{font:italic 13px/1.4 Georgia,serif;color:#3b2a17;display:block;margin-top:3px}'
    + '#an-pad .tags{display:flex;flex-wrap:wrap;gap:6px}'
    + '#an-pad .tags button{font:12px/1 Georgia,serif;padding:6px 9px;border:1px solid #3b2a17;background:#e6d8b4;color:#22170b;cursor:pointer}'
    + '#an-pad .tags button.on{background:#7d1410;color:#f1e7cd;border-color:#7d1410}'
    + '#an-pad textarea{width:100%;box-sizing:border-box;min-height:96px;font:15px/1.45 Georgia,serif;padding:8px;border:1px solid #3b2a17;background:#fbf6e8;color:#22170b;resize:vertical}'
    + '#an-pad .row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}'
    + '#an-pad .row button{font:13px/1 Georgia,serif;padding:9px 14px;border:1px solid #3b2a17;cursor:pointer;background:#e6d8b4;color:#22170b}'
    + '#an-pad .row .save{background:#22170b;color:#f1e7cd}'
    + '#an-pad .msg{font:12px/1.4 Georgia,serif;color:#7d1410;margin-left:auto}'
    + '#an-pad input{font:13px ui-monospace,Menlo,monospace;padding:6px;border:1px solid #3b2a17;width:100%;box-sizing:border-box}'
    + '#an-pad .keyrow[hidden]{display:none}';
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.id = 'an-btn'; btn.type = 'button'; btn.title = 'Production note (N)';
  btn.innerHTML = 'Note<b></b>';
  var pad = document.createElement('div');
  pad.id = 'an-pad'; pad.hidden = true;
  pad.innerHTML =
      '<div class="ctx"></div>'
    + '<div class="tags">' + TAGS.map(function (t) { return '<button type="button">' + t + '</button>'; }).join('') + '</div>'
    + '<textarea id="an-text" placeholder="What works, what doesn’t, what to change…"></textarea>'
    + '<div class="keyrow" hidden><input id="an-key" type="password" placeholder="Media Door upload key (asked once)"></div>'
    + '<div class="row"><button type="button" class="save">Save note</button><button type="button" class="cancel">Cancel</button><span class="msg"></span></div>';
  document.body.appendChild(btn); document.body.appendChild(pad);

  var ctxEl = pad.querySelector('.ctx'), ta = pad.querySelector('textarea'), msg = pad.querySelector('.msg');
  var keyRow = pad.querySelector('.keyrow'), keyIn = pad.querySelector('#an-key');
  var tag = '', snap = null, wasReading = false;

  pad.querySelectorAll('.tags button').forEach(function (b) {
    b.onclick = function () { var on = !b.classList.contains('on');
      pad.querySelectorAll('.tags button').forEach(function (x) { x.classList.remove('on'); });
      if (on) b.classList.add('on'); tag = on ? b.textContent : ''; ta.focus(); };
  });

  function picture() {
    var L = document.querySelectorAll('#amenti-art .art-l.in'), el = L[L.length - 1];
    if (document.getElementById('amenti-exhibit')) {
      var f = document.querySelector('#amenti-exhibit iframe'); if (f && f.src) return 'exhibit: ' + f.src.split('/').pop();
    }
    if (!el) return '';
    var v = el.querySelector('video'); if (v && v.src) return v.src.split('/').pop().split('?')[0];
    var m = /url\(["']?([^"')]+)/.exec(el.style.backgroundImage || ''); return m ? m[1].split('/').pop() : '';
  }
  function capture() {
    var s = R.sheet || {}, c = R.cue || (s.cues && s.cues[Math.max(0, (R.i || 1) - 1)]) || {};
    var a = R._audio, t = (a && !isNaN(a.currentTime)) ? Math.round(a.currentTime * 10) / 10 : null;
    return { work: s.work || 'dracula', book: BOOK, chapter: s.episode || null, cue: c.n || null,
             speaker: c.role || c.figure || '', words: (c.text || '').replace(/\s+/g, ' ').slice(0, 160),
             picture: picture(), t: t, page: location.pathname };
  }
  function count() { var n = jget(LS_MINE).length; btn.querySelector('b').textContent = n ? String(n) : ''; }

  function open() {
    snap = capture();
    wasReading = R.state === 'reading';
    if (wasReading && R.pause) R.pause();
    ctxEl.innerHTML = '';
    var line = 'Ch ' + (snap.chapter || '?') + ' · cue ' + (snap.cue || '?') + (snap.t != null ? ' · ' + snap.t + 's' : '')
      + (snap.picture ? ' · ' + snap.picture : '');
    ctxEl.appendChild(document.createTextNode(line));
    var i = document.createElement('i'); i.textContent = (snap.speaker ? snap.speaker + ': ' : '') + '“' + snap.words + (snap.words.length >= 160 ? '…' : '') + '”';
    ctxEl.appendChild(i);
    keyRow.hidden = !!ls(LS_KEY);
    msg.textContent = ''; ta.value = ''; tag = '';
    pad.querySelectorAll('.tags button').forEach(function (x) { x.classList.remove('on'); });
    pad.hidden = false; setTimeout(function () { ta.focus(); }, 30);
  }
  function close(resume) { pad.hidden = true; if (resume && wasReading && R.state === 'paused' && R.resume) R.resume(); wasReading = false; }

  function send(note) {
    var key = ls(LS_KEY);
    if (!key) return Promise.reject(new Error('no key'));
    var d = new Date(note.at), stamp = d.toISOString().replace(/[:.]/g, '-');
    var path = 'notes/' + note.work + '/' + note.book + '/' + stamp + '-ch' + pad2(note.chapter || 0) + '-c' + pad2(note.cue || 0) + '.json';
    return fetch(DOOR + '/upload/' + path, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'X-Upload-Key': key },
                                            body: JSON.stringify(note, null, 1) })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return path; });
  }
  function flush() {
    var q = jget(LS_Q); if (!q.length || !ls(LS_KEY)) return;
    var left = [];
    q.reduce(function (p, n) { return p.then(function () { return send(n).catch(function () { left.push(n); }); }); }, Promise.resolve())
      .then(function () { ls(LS_Q, JSON.stringify(left)); });
  }

  function save() {
    if (!ta.value.trim() && !tag) { msg.textContent = 'Write a note or pick a tag.'; return; }
    if (!keyRow.hidden && keyIn.value.trim()) ls(LS_KEY, keyIn.value.trim());
    var note = Object.assign({}, snap, { tag: tag, note: ta.value.trim(), at: Date.now() });
    var mine = jget(LS_MINE); mine.push(note); ls(LS_MINE, JSON.stringify(mine.slice(-300))); count();
    msg.textContent = 'Saving…';
    send(note).then(function () { msg.textContent = 'Saved.'; setTimeout(function () { close(true); }, 500); },
      function (e) { var q = jget(LS_Q); q.push(note); ls(LS_Q, JSON.stringify(q));
        msg.textContent = (e.message === 'no key' ? 'Needs the upload key — kept here, will send later.' : 'Not sent (' + e.message + ') — kept, will retry.');
        keyRow.hidden = !!ls(LS_KEY); setTimeout(function () { close(true); }, 1600); });
  }

  btn.onclick = function () { if (pad.hidden) open(); else close(true); };
  pad.querySelector('.save').onclick = save;
  pad.querySelector('.cancel').onclick = function () { close(true); };
  /* keys inside the pad stay in the pad (space must not pause the reading) */
  pad.addEventListener('keydown', function (e) {
    e.stopPropagation();
    if (e.key === 'Escape') close(true);
    else if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) save();
  });
  document.addEventListener('keydown', function (e) {
    if (!pad.hidden) return;
    var t = e.target && e.target.tagName; if (t === 'INPUT' || t === 'TEXTAREA' || (e.target && e.target.isContentEditable)) return;
    if ((e.key === 'n' || e.key === 'N') && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); open(); }
  });
  count(); flush();
})();
