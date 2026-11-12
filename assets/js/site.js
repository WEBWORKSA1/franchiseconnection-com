/* FranchiseConnection.com — site script (no dependencies) */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var ROOT = document.documentElement.getAttribute('data-root') || '';
  var REPO_RAW = 'https://raw.githubusercontent.com/WEBWORKSA1/franchiseconnection-com/main/';
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function money(n) { if (!isFinite(n)) return '—'; var a = Math.abs(n), s = n < 0 ? '-$' : '$'; if (a >= 1e6) return s + (a / 1e6).toFixed(a >= 1e7 ? 0 : 1).replace(/\.0$/, '') + 'M'; if (a >= 1e4) return s + Math.round(a / 1e3) + 'k'; return s + Math.round(a).toLocaleString(); }
  function moneyFull(n) { return isFinite(n) ? (n < 0 ? '-$' : '$') + Math.round(Math.abs(n)).toLocaleString() : '—'; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* ---------- Private inbox (never written in plain text anywhere on the site) ---------- */
  var _k = [122, 120, 116, 57, 123, 126, 118, 122, 112, 87, 38, 118, 100, 124, 101, 120, 96, 117, 114, 96];
  function inbox() { return _k.map(function (c) { return String.fromCharCode(c ^ 23); }).join('').split('').reverse().join(''); }
  function endpoint() { return 'https://formsubmit.co/ajax/' + inbox(); }
  $$('[data-mail]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      location.href = 'mailto:' + inbox() + '?subject=' + encodeURIComponent(a.getAttribute('data-mail') || 'Inquiry from FranchiseConnection.com');
    });
  });

  function send(data, subject) {
    data._subject = '[FranchiseConnection] ' + subject;
    data._template = 'table';
    data._captcha = 'false';
    data.page = location.href;
    data.submitted = new Date().toISOString();
    return fetch(endpoint(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data)
    }).then(function (r) { if (!r.ok) throw new Error('send'); return r.json().catch(function () { return {}; }); });
  }
  function formData(f) {
    var d = {};
    new FormData(f).forEach(function (v, k) { if (k === '_honey') return; d[k] = d[k] ? d[k] + ', ' + v : v; });
    return d;
  }

  /* ---------- Menu ---------- */
  var burger = $('#burger'), menu = $('#menu');
  if (burger && menu) burger.addEventListener('click', function () { var o = menu.classList.toggle('open'); burger.setAttribute('aria-expanded', o); });
  $$('.more>button').forEach(function (b) {
    b.addEventListener('click', function (e) { e.stopPropagation(); var li = b.parentNode, o = li.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
  });
  document.addEventListener('click', function () { $$('.more.open').forEach(function (li) { li.classList.remove('open'); $('button', li).setAttribute('aria-expanded', 'false'); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') $$('.more.open').forEach(function (li) { li.classList.remove('open'); }); });

  /* ---------- Cookie notice + year ---------- */
  var ck = $('#cookie');
  if (ck && !store('fc-cookie')) ck.classList.add('show');
  $$('[data-cookie]').forEach(function (b) { b.addEventListener('click', function () { store('fc-cookie', b.getAttribute('data-cookie')); ck.classList.remove('show'); }); });
  $$('.year').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- AdSense manual units: add slot IDs here after approval (Auto ads work without this) ---------- */
  var AD_SLOTS = { /* 'in-article': '1234567890', 'sidebar': '0987654321', 'footer': '1122334455' */ };
  $$('.ad-slot[data-slot]').forEach(function (box) {
    var id = AD_SLOTS[box.getAttribute('data-slot')];
    if (!id) return;
    box.innerHTML = '<div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6620975821265271" data-ad-slot="' + id + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
  });

  /* ---------- Generic forms ---------- */
  $$('form.js-form').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (f._honey && f._honey.value) return;
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var msg = $('.form-msg', f), btn = $('button[type=submit]', f), old = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      var d = formData(f);
      var subj = (f.getAttribute('data-subject') || 'Website form') + ' — ' + (d.name || d.brand || d.email || '');
      send(d, subj).then(function () {
        if (msg) { msg.className = 'form-msg ok'; msg.textContent = f.getAttribute('data-ok') || 'Received. We reply within one business day.'; }
        f.reset(); resetSteps(f);
      }).catch(function () {
        if (msg) { msg.className = 'form-msg err'; msg.textContent = 'Not sent — check your connection and try again.'; }
      }).then(function () { if (btn) { btn.disabled = false; btn.textContent = old; } });
    });
  });

  /* ---------- Multi-step forms ---------- */
  function resetSteps(f) {
    var st = $$('.step', f); if (!st.length) return;
    st.forEach(function (s, i) { s.classList.toggle('active', i === 0); });
    $$('.steps-bar span', f).forEach(function (s, i) { s.classList.toggle('on', i === 0); });
    f._step = 0;
  }
  function stepper(f, onChange) {
    var steps = $$('.step', f), bar = $$('.steps-bar span', f); f._step = 0;
    function valid(stepEl) {
      var bad = $$('input,select,textarea', stepEl).filter(function (x) { return !x.checkValidity(); });
      var groups = $$('[data-require-one]', stepEl).filter(function (g) { return !$$('input:checked', g).length; });
      if (bad.length) { bad[0].reportValidity(); return false; }
      if (groups.length) { var m = $('.form-msg', f); if (m) { m.className = 'form-msg err'; m.textContent = 'Pick at least one option to continue.'; } return false; }
      var m2 = $('.form-msg', f); if (m2 && m2.classList.contains('err')) { m2.textContent = ''; m2.className = 'form-msg'; }
      return true;
    }
    function go(n) {
      if (n > f._step && !valid(steps[f._step])) return;
      f._step = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.classList.toggle('active', k === f._step); });
      bar.forEach(function (s, k) { s.classList.toggle('on', k <= f._step); });
      var first = $('input,select,textarea,button', steps[f._step]); if (first && n > 0) first.focus({ preventScroll: true });
      if (onChange) onChange(f._step);
      var top = f.getBoundingClientRect().top; if (top < 0) f.scrollIntoView({ block: 'start' });
    }
    $$('[data-next]', f).forEach(function (b) { b.addEventListener('click', function () { go(f._step + 1); }); });
    $$('[data-prev]', f).forEach(function (b) { b.addEventListener('click', function () { go(f._step - 1); }); });
    f._go = go; f._valid = function () { return valid(steps[f._step]); };
    return go;
  }
  $$('form.multistep').forEach(function (f) { if (!f.hasAttribute('data-manual')) stepper(f); });

  /* ---------- YouTube facades ---------- */
  $$('.video[data-yt]').forEach(function (v) {
    var id = v.getAttribute('data-yt'), t = v.getAttribute('data-title') || 'Franchise video';
    v.setAttribute('role', 'button'); v.setAttribute('tabindex', '0'); v.setAttribute('aria-label', 'Play video: ' + t);
    v.innerHTML = '<img loading="lazy" alt="" src="https://i.ytimg.com/vi/' + id + '/hqdefault.jpg"><div class="play"><span></span></div>';
    function play() { v.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0" title="' + esc(t) + '" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture" allowfullscreen></iframe>'; }
    v.addEventListener('click', play, { once: true });
    v.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); } });
  });

  /* ---------- Data loaders ---------- */
  var conceptsP = null;
  function concepts() {
    if (!conceptsP) conceptsP = fetch(ROOT + 'data/concepts.json').then(function (r) { return r.json(); });
    return conceptsP;
  }
  function fetchFresh(path) {
    // Fresh copy straight from the repo (updated by the daily workflow); falls back to the deployed file.
    var ctrl = window.AbortController ? new AbortController() : null;
    var t = setTimeout(function () { if (ctrl) ctrl.abort(); }, 4000);
    return fetch(REPO_RAW + path, ctrl ? { signal: ctrl.signal, cache: 'no-store' } : {})
      .then(function (r) { clearTimeout(t); if (!r.ok) throw 0; return r.json(); })
      .catch(function () { return fetch(ROOT + path).then(function (r) { return r.json(); }); });
  }
  var ROLE_LABEL = { owner: 'Owner-operator', semi: 'Semi-absentee', exec: 'Executive / investor' };
  var TAG_LABEL = { home: 'Home-based', mobile: 'Mobile / van', recurring: 'Recurring revenue', b2b: 'B2B', sba: 'Often SBA-financed', multi: 'Multi-unit friendly', lowstaff: 'Low staff' };

  /* ---------- Home: budget dial ---------- */
  var dial = $('#dialRange');
  if (dial) {
    var STOPS = [25000, 50000, 75000, 100000, 150000, 200000, 250000, 350000, 500000, 750000, 1000000, 1500000, 2500000, 5000000];
    var out = $('#dialOut'), list = $('#dialList'), count = $('#dialCount'), cta = $('#dialCta');
    concepts().then(function (d) {
      function upd() {
        var v = STOPS[+dial.value];
        out.textContent = money(v) + (+dial.value === STOPS.length - 1 ? '+' : '');
        var fit = d.items.filter(function (c) { return c.min <= v; }).sort(function (a, b) { return b.min - a.min; });
        count.innerHTML = '<b>' + fit.length + '</b> of ' + d.items.length + ' franchise categories start at or below this budget.';
        list.innerHTML = fit.slice(0, 5).map(function (c) { return '<li><span>' + esc(c.name) + '</span><span>from ' + money(c.min) + '</span></li>'; }).join('') || '<li><span>Try a higher amount</span><span></span></li>';
        cta.href = ROOT + 'match.html?budget=' + v;
        $('#dialExplore').href = ROOT + 'explore.html?max=' + v;
      }
      dial.addEventListener('input', upd); upd();
    });
  }

  /* ---------- Explorer ---------- */
  var ex = $('#explorer');
  if (ex) {
    concepts().then(function (d) {
      var items = d.items, params = new URLSearchParams(location.search);
      var q = $('#fq'), maxSel = $('#fmax'), sortSel = $('#fsort'), list = $('#conceptList'), cnt = $('#resCount');
      var inds = Array.from(new Set(items.map(function (c) { return c.industry; }))).sort();
      $('#findustry').innerHTML = inds.map(function (i) { var n = items.filter(function (c) { return c.industry === i; }).length; return '<label class="check"><input type="checkbox" name="ind" value="' + esc(i) + '"><span>' + esc(i) + ' <span class="muted">(' + n + ')</span></span></label>'; }).join('');
      if (params.get('q')) q.value = params.get('q');
      if (params.get('max')) { var mv = params.get('max'); var opt = $$('option', maxSel).filter(function (o) { return +o.value >= +mv; })[0]; if (opt) maxSel.value = opt.value; }
      if (params.get('industry')) $$('#findustry input').forEach(function (i) { if (i.value === params.get('industry')) i.checked = true; });
      if (params.get('tag')) $$('#ftags input').forEach(function (i) { if (i.value === params.get('tag')) i.checked = true; });
      var favs = JSON.parse(store('fc-favs') || '[]'), basket = [];
      function checked(sel) { return $$(sel + ' input:checked').map(function (i) { return i.value; }); }
      function render() {
        var term = q.value.trim().toLowerCase(), max = +maxSel.value, ind = checked('#findustry'), tags = checked('#ftags'), roles = checked('#froles'), onlyFav = $('#ffav').checked;
        var res = items.filter(function (c) {
          if (max && c.min > max) return false;
          if (ind.length && ind.indexOf(c.industry) < 0) return false;
          if (tags.length && !tags.every(function (t) { return c.tags.indexOf(t) > -1; })) return false;
          if (roles.length && !roles.some(function (r) { return c.roles.indexOf(r) > -1; })) return false;
          if (onlyFav && favs.indexOf(c.id) < 0) return false;
          if (term && (c.name + ' ' + c.industry + ' ' + c.summary).toLowerCase().indexOf(term) < 0) return false;
          return true;
        });
        var s = sortSel.value;
        res.sort(function (a, b) { return s === 'high' ? b.max - a.max : s === 'name' ? a.name.localeCompare(b.name) : a.min - b.min; });
        cnt.textContent = res.length + ' categor' + (res.length === 1 ? 'y' : 'ies');
        list.innerHTML = res.length ? res.map(function (c) {
          var fav = favs.indexOf(c.id) > -1, inB = basket.indexOf(c.id) > -1;
          return '<li class="concept" id="' + c.id + '"><div><h3>' + esc(c.name) + '</h3><div class="meta"><span><b>' + esc(c.industry) + '</b></span><span>Franchise fee <b>' + esc(c.fee) + '</b></span><span>Royalty <b>' + esc(c.royalty) + '</b></span><span>' + c.roles.map(function (r) { return ROLE_LABEL[r]; }).join(', ') + '</span></div><p>' + esc(c.summary) + '</p><p class="watch">Watch out: ' + esc(c.watch) + '</p><div class="tags">' + c.tags.map(function (t) { return '<span class="tag">' + TAG_LABEL[t] + '</span>'; }).join('') + '</div></div>' +
            '<div class="acts"><div class="range">' + money(c.min) + ' – ' + money(c.max) + '</div><span class="small muted">typical total investment</span><button type="button" data-fav="' + c.id + '" aria-pressed="' + fav + '">' + (fav ? 'Saved' : 'Save') + '</button><button type="button" data-cmp="' + c.id + '" aria-pressed="' + inB + '">' + (inB ? 'Selected' : 'Compare / request info') + '</button></div></li>';
        }).join('') : '<li class="empty">No categories match every filter. Raise the budget or clear a filter.</li>';
      }
      function updBasket() {
        var b = $('#basket'); b.classList.toggle('show', basket.length > 0); document.body.classList.toggle('has-basket', basket.length > 0);
        $('#basketCount').textContent = basket.length + ' selected';
        $('#cmpBtn').disabled = basket.length < 2;
      }
      [q, maxSel, sortSel].forEach(function (el) { el.addEventListener('input', render); });
      ex.addEventListener('change', function (e) { if (e.target.matches('.filters input')) render(); });
      $('#fclear').addEventListener('click', function () { $$('.filters input[type=checkbox]').forEach(function (i) { i.checked = false; }); q.value = ''; maxSel.value = '0'; render(); });
      list.addEventListener('click', function (e) {
        var f = e.target.closest('[data-fav]'), c = e.target.closest('[data-cmp]');
        if (f) { var id = f.getAttribute('data-fav'), i = favs.indexOf(id); if (i > -1) favs.splice(i, 1); else favs.push(id); store('fc-favs', JSON.stringify(favs)); render(); }
        if (c) { var id2 = c.getAttribute('data-cmp'), j = basket.indexOf(id2); if (j > -1) basket.splice(j, 1); else if (basket.length < 3) basket.push(id2); else { alertBox('You can compare up to 3 categories.'); } render(); updBasket(); }
      });
      function alertBox(t) { var m = $('#basketMsg'); m.textContent = t; setTimeout(function () { m.textContent = ''; }, 3000); }
      var dlg = $('#cmpDialog');
      $('#cmpBtn').addEventListener('click', function () {
        var sel = basket.map(function (id) { return items.filter(function (c) { return c.id === id; })[0]; });
        var rows = [['Industry', 'industry'], ['Typical investment', function (c) { return money(c.min) + ' – ' + money(c.max); }], ['Franchise fee', 'fee'], ['Royalty', 'royalty'], ['Owner role', function (c) { return c.roles.map(function (r) { return ROLE_LABEL[r]; }).join(', '); }], ['Traits', function (c) { return c.tags.map(function (t) { return TAG_LABEL[t]; }).join(', '); }], ['Why people buy', 'summary'], ['Watch out', 'watch']];
        $('#cmpBody').innerHTML = '<div class="table-scroll"><table class="compare-table"><tr><th></th>' + sel.map(function (c) { return '<th style="width:auto">' + esc(c.name) + '</th>'; }).join('') + '</tr>' + rows.map(function (r) { return '<tr><th>' + r[0] + '</th>' + sel.map(function (c) { return '<td>' + esc(typeof r[1] === 'function' ? r[1](c) : c[r[1]]) + '</td>'; }).join('') + '</tr>'; }).join('') + '</table></div>';
        if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
      });
      $$('[data-close]').forEach(function (b) { b.addEventListener('click', function () { var d2 = b.closest('dialog'); if (d2.close) d2.close(); else d2.removeAttribute('open'); }); });
      var rq = $('#reqDialog'), rf = $('#reqForm');
      $('#reqBtn').addEventListener('click', function () {
        $('#reqList').textContent = basket.map(function (id) { return items.filter(function (c) { return c.id === id; })[0].name; }).join('; ');
        rf.categories.value = $('#reqList').textContent;
        if (rq.showModal) rq.showModal(); else rq.setAttribute('open', '');
      });
      stepper(rf);
      rf.addEventListener('submit', function (e) {
        e.preventDefault();
        if (rf._honey.value) return;
        if (!rf.checkValidity()) { rf.reportValidity(); return; }
        var msg = $('.form-msg', rf), btn = $('button[type=submit]', rf);
        btn.disabled = true;
        var dd = formData(rf); dd.lead_type = 'Explorer request-info basket';
        send(dd, 'Lead: request info — ' + (dd.name || dd.email)).then(function () {
          msg.className = 'form-msg ok'; msg.textContent = 'Request sent. Expect your category briefing and matched opportunities by email within one business day.';
          basket = []; render(); updBasket(); rf.reset(); setTimeout(function () { if (rq.close) rq.close(); resetSteps(rf); msg.textContent = ''; }, 3500);
        }).catch(function () { msg.className = 'form-msg err'; msg.textContent = 'Not sent — check your connection and try again.'; }).then(function () { btn.disabled = false; });
      });
      render();
    });
  }

  /* ---------- Get Matched quiz ---------- */
  var mf = $('#matchForm');
  if (mf) {
    var p = new URLSearchParams(location.search), pre = +p.get('budget');
    if (pre) { var opts = $$('input[name=capital]', mf); var pick = opts.filter(function (o) { return +o.getAttribute('data-max') >= pre; })[0] || opts[opts.length - 1]; pick.checked = true; }
    var resultsBox = $('#matchResults');
    var goM = stepper(mf, function (i) { if (i === $$('.step', mf).length - 1) previewMatches(); });
    var scored = [];
    function answers() { return formData(mf); }
    function score(d) {
      var a = answers();
      var cap = +($('input[name=capital]:checked', mf) || { getAttribute: function () { return 0; } }).getAttribute('data-max');
      var budget = cap * 3.3; // liquid capital is typically ~20–30% of total project cost with financing
      var wantInd = $$('input[name=industries]:checked', mf).map(function (i) { return i.value; });
      var role = (a.role || '').split(',')[0];
      var roleKey = /Owner/.test(role) ? 'owner' : /Semi/.test(role) ? 'semi' : /Passive|Executive/.test(role) ? 'exec' : '';
      var prefs = $$('input[name=prefs]:checked', mf).map(function (i) { return i.value; });
      return d.items.map(function (c) {
        var s = 0;
        if (c.min <= budget) s += 40; else s -= Math.min(40, (c.min - budget) / budget * 40);
        if (c.max <= budget * 1.4) s += 10;
        if (wantInd.length && wantInd.indexOf(c.industry) > -1) s += 30;
        if (!wantInd.length || wantInd.indexOf('Open to anything') > -1) s += 12;
        if (roleKey && c.roles.indexOf(roleKey) > -1) s += 15;
        prefs.forEach(function (t) { if (c.tags.indexOf(t) > -1) s += 6; });
        var maxS = 50 + (wantInd.length && wantInd.indexOf('Open to anything') < 0 ? 30 : 12) + (roleKey ? 15 : 0) + prefs.length * 6;
        return { c: c, s: Math.max(1, Math.min(99, Math.round(s / maxS * 100))) };
      }).sort(function (x, y) { return y.s - x.s; }).slice(0, 6);
    }
    function previewMatches() {
      concepts().then(function (d) {
        scored = score(d);
        $('#matchPreview').innerHTML = scored.slice(0, 3).map(function (m) { return '<div class="match-card"><span class="fit">' + m.s + '% fit</span><b>' + esc(m.c.name) + '</b><div class="small muted">' + esc(m.c.industry) + ', typical ' + money(m.c.min) + '–' + money(m.c.max) + '</div></div>'; }).join('') + '<p class="small muted">Your full report adds three more categories, financing math and validation questions.</p>';
      });
    }
    mf.addEventListener('submit', function (e) {
      e.preventDefault();
      if (mf._honey.value) return;
      if (!mf.checkValidity()) { mf.reportValidity(); return; }
      var btn = $('button[type=submit]', mf), msg = $('.form-msg', mf);
      btn.disabled = true; btn.textContent = 'Building your report…';
      concepts().then(function (d) {
        scored = score(d);
        var a = answers();
        var capEl = $('input[name=capital]:checked', mf), capMax = capEl ? +capEl.getAttribute('data-max') : 0;
        var tl = a.timeline || '';
        var leadScore = (capMax >= 250000 ? 40 : capMax >= 100000 ? 30 : capMax >= 50000 ? 18 : 8) + (/0–3|3–6/.test(tl) ? 35 : /6–12/.test(tl) ? 22 : 8) + (a.phone ? 15 : 0) + (/Yes/.test(a.credit || '') ? 10 : 0);
        a.lead_type = 'Get Matched quiz';
        a.lead_score = leadScore + '/100 ' + (leadScore >= 70 ? '(HOT)' : leadScore >= 45 ? '(WARM)' : '(NURTURE)');
        a.top_matches = scored.map(function (m) { return m.c.name + ' (' + m.s + '%)'; }).join('; ');
        return send(a, 'Lead: Match report — ' + (a.name || a.email) + ' — score ' + leadScore);
      }).then(function () {
        mf.hidden = true;
        resultsBox.hidden = false;
        $('#resultsList').innerHTML = scored.map(function (m) {
          return '<div class="match-card"><span class="fit">' + m.s + '% fit</span><h3 style="margin:0 0 4px">' + esc(m.c.name) + '</h3><div class="small muted">' + esc(m.c.industry) + ', typical total investment ' + money(m.c.min) + '–' + money(m.c.max) + ', royalty ' + esc(m.c.royalty) + '</div><p style="margin:8px 0 4px">' + esc(m.c.summary) + '</p><p class="small muted" style="margin:0">Watch out: ' + esc(m.c.watch) + '</p></div>';
        }).join('');
        resultsBox.scrollIntoView({ block: 'start' });
      }).catch(function () {
        msg.className = 'form-msg err'; msg.textContent = 'Not sent — check your connection and try again.';
      }).then(function () { btn.disabled = false; btn.textContent = 'Send my free match report'; });
    });
  }

  /* ---------- Calculators ---------- */
  var tabs = $$('.tabs [role=tab]');
  if (tabs.length) {
    function show(id) {
      tabs.forEach(function (t) { var on = t.getAttribute('aria-controls') === id; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; });
      $$('.tool').forEach(function (p) { p.classList.toggle('on', p.id === id); });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(t.getAttribute('aria-controls')); history.replaceState(null, '', '#' + t.getAttribute('aria-controls')); });
      t.addEventListener('keydown', function (e) { var n = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : null; if (n === null) return; n = (n + tabs.length) % tabs.length; tabs[n].focus(); tabs[n].click(); });
    });
    if (location.hash && $('#' + location.hash.slice(1) + '.tool')) show(location.hash.slice(1));
  }
  function num(id) { var el = document.getElementById(id); return el ? parseFloat(el.value) || 0 : 0; }
  function bind(ids, fn) { ids.forEach(function (id) { var el = document.getElementById(id); if (el) el.addEventListener('input', fn); }); fn(); }
  function set(id, v) { var el = document.getElementById(id); if (el) el.textContent = v; }
  function pmt(rate, n, pv) { var r = rate / 12; return r ? pv * r / (1 - Math.pow(1 + r, -n)) : pv / n; }
  function meter(id, pct) { var el = document.getElementById(id); if (el) el.style.width = Math.max(0, Math.min(100, pct)) + '%'; }

  if ($('#t-invest')) bind(['i-fee', 'i-build', 'i-equip', 'i-inv', 'i-open', 'i-train', 'i-pro', 'i-wc', 'i-cont'], function () {
    var base = num('i-fee') + num('i-build') + num('i-equip') + num('i-inv') + num('i-open') + num('i-train') + num('i-pro') + num('i-wc');
    var total = base * (1 + num('i-cont') / 100);
    set('i-total', moneyFull(total)); set('i-cash', moneyFull(total * 0.25)); set('i-loan', moneyFull(total * 0.75)); set('i-contv', moneyFull(total - base));
    set('i-verdict', total < 150000 ? 'Entry-level investment. Many home-based and mobile service franchises live here — check whether your working capital covers 6–12 months of owner pay.' : total < 600000 ? 'Mid-range. Typical for studios, service franchises with a shop, and small-format food. Lenders will usually expect 20–30% cash injection.' : 'Large project. Expect real-estate negotiation, longer ramp-up, and lenders asking for experience plus strong liquidity.');
  });
  if ($('#t-loan')) bind(['l-amt', 'l-rate', 'l-years', 'l-down'], function () {
    var proj = num('l-amt'), down = proj * num('l-down') / 100, loan = proj - down, n = num('l-years') * 12;
    var m = pmt(num('l-rate') / 100, n, loan);
    set('l-pay', moneyFull(m) + '/mo'); set('l-loanv', moneyFull(loan)); set('l-downv', moneyFull(down)); set('l-int', moneyFull(m * n - loan)); set('l-annual', moneyFull(m * 12));
    set('l-dscr', 'To meet a typical 1.15x debt-service coverage test, the business should produce at least ' + moneyFull(m * 12 * 1.15) + ' a year in cash flow before debt payments.');
  });
  if ($('#t-afford')) bind(['a-liquid', 'a-net', 'a-target', 'a-live', 'a-months'], function () {
    var liquid = num('a-liquid'), net = num('a-net'), target = num('a-target'), reserve = num('a-live') * num('a-months');
    var avail = liquid - reserve, need = target * 0.25, ratio = need ? avail / need : 0;
    set('a-avail', moneyFull(avail)); set('a-need', moneyFull(need)); set('a-reserve', moneyFull(reserve));
    set('a-pct', Math.round(Math.max(0, ratio) * 100) + '%'); meter('a-meter', ratio * 100);
    set('a-verdict', ratio >= 1.2 && net >= target * 0.5 ? 'Comfortable. You can cover a typical 25% cash injection and keep a living reserve. Lenders like this profile.' : ratio >= 1 ? 'Tight but workable. You can fund the injection, with little cushion. Consider a lower-cost category or a partner.' : 'Short. After your living reserve, you cannot cover a typical 25% injection for this project size. Lower the target, add a partner, or explore ROBS or home-equity options with a professional.');
  });
  if ($('#t-break')) bind(['b-invest', 'b-rev', 'b-cogs', 'b-labor', 'b-rent', 'b-other', 'b-roy', 'b-ad', 'b-pay'], function () {
    var rev = num('b-rev'), fees = rev * (num('b-roy') + num('b-ad')) / 100;
    var costs = rev * num('b-cogs') / 100 + num('b-labor') + num('b-rent') + num('b-other') + fees + num('b-pay');
    var profit = rev - costs, inv = num('b-invest');
    var fixed = num('b-labor') + num('b-rent') + num('b-other') + num('b-pay'), cm = 1 - (num('b-cogs') + num('b-roy') + num('b-ad')) / 100;
    var be = cm > 0 ? fixed / cm : Infinity;
    set('b-profit', moneyFull(profit) + '/mo'); set('b-be', moneyFull(be) + '/mo'); set('b-fees', moneyFull(fees) + '/mo');
    set('b-payback', profit > 0 ? (inv / (profit * 12)).toFixed(1) + ' years' : 'Never at these numbers');
    set('b-roi', inv ? Math.round(profit * 12 / inv * 100) + '% / yr' : '—');
    set('b-verdict', profit <= 0 ? 'Loss-making at these inputs. Find the gap: revenue, labor, or rent.' : (inv / (profit * 12)) <= 3 ? 'Strong payback under 3 years — verify the revenue figure against Item 19 and franchisee calls.' : 'Positive but slow payback. Make sure the revenue assumption is not the optimistic top quartile.');
  });
  if ($('#t-fees')) bind(['f-rev', 'f-growth', 'f-roy', 'f-ad', 'f-tech', 'f-years'], function () {
    var rev = num('f-rev'), g = num('f-growth') / 100, roy = 0, ad = 0, tech = num('f-tech') * 12 * num('f-years');
    for (var y = 0; y < num('f-years'); y++) { var r = rev * Math.pow(1 + g, y); roy += r * num('f-roy') / 100; ad += r * num('f-ad') / 100; }
    set('f-total', moneyFull(roy + ad + tech)); set('f-royv', moneyFull(roy)); set('f-adv', moneyFull(ad)); set('f-techv', moneyFull(tech));
    set('f-verdict', 'Over a ' + num('f-years') + '-year term you would pay about ' + moneyFull(roy + ad + tech) + ' in ongoing fees. Ask each franchisor what that buys: purchasing discounts, technology, brand traffic and support that you could not get alone.');
  });
  if ($('#t-multi')) bind(['m-units', 'm-cost', 'm-gap', 'm-profit', 'm-ramp'], function () {
    var u = num('m-units'), cost = num('m-cost'), gap = num('m-gap'), prof = num('m-profit'), ramp = num('m-ramp');
    var months = (u - 1) * gap + ramp + 12, capital = 0, cum = 0, minCum = 0;
    for (var m = 0; m <= Math.max(months, 60); m++) {
      for (var k = 0; k < u; k++) { var open = k * gap; if (m === open) cum -= cost; if (m > open) cum += m - open < ramp ? prof * (m - open) / ramp : prof; }
      if (cum < minCum) minCum = cum;
    }
    set('m-peak', moneyFull(-minCum)); set('m-total', moneyFull(u * cost)); set('m-steady', moneyFull(u * prof) + '/mo');
    set('m-verdict', 'Peak cash needed is about ' + moneyFull(-minCum) + ' — that, not the total build cost, is what your financing plan must cover.');
  });

  /* ---------- News feed (self-updating) ---------- */
  var nl = $('#newsList');
  if (nl) {
    fetchFresh('data/news.json').then(function (d) {
      var items = d.items || [], cats = ['All'].concat(Array.from(new Set(items.map(function (i) { return i.topic; }))).filter(Boolean));
      var limit = +nl.getAttribute('data-limit') || 999, chips = $('#newsChips'), cur = 'All';
      if ($('#newsUpdated') && d.updated) $('#newsUpdated').textContent = new Date(d.updated).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
      function draw() {
        var f = items.filter(function (i) { return cur === 'All' || i.topic === cur; }).slice(0, limit);
        nl.innerHTML = f.length ? f.map(function (i) { var dt = i.date ? new Date(i.date) : null; return '<li><a href="' + esc(i.link) + '" target="_blank" rel="noopener nofollow">' + esc(i.title) + '</a><span class="src">' + esc(i.source || '') + (dt && !isNaN(dt) ? ', ' + dt.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : '') + (i.topic ? '<span class="tag">' + esc(i.topic) + '</span>' : '') + '</span></li>'; }).join('') : '<li class="empty">No headlines in this topic yet. Check back tomorrow — the feed refreshes daily.</li>';
      }
      if (chips) {
        chips.innerHTML = cats.map(function (c) { return '<button type="button" aria-pressed="' + (c === cur) + '">' + esc(c) + '</button>'; }).join('');
        chips.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; cur = b.textContent; $$('button', chips).forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); draw(); });
      }
      draw();
    }).catch(function () { nl.innerHTML = '<li class="empty">Headlines are refreshing. Try again in a minute.</li>'; });
  }

  /* ---------- Events: hide past, show countdown ---------- */
  var ev = $('#eventList');
  if (ev) {
    var now = new Date(), lis = $$('li[data-end]', ev), next = null;
    lis.forEach(function (li) {
      var end = new Date(li.getAttribute('data-end') + 'T23:59:59');
      if (end < now) { li.remove(); return; }
      var start = new Date(li.getAttribute('data-start') + 'T09:00:00');
      if (!next || start < next.start) next = { start: start, li: li };
      var days = Math.ceil((start - now) / 864e5);
      var s = $('.soon', li); if (s) s.textContent = days <= 0 ? 'Happening now' : days === 1 ? 'Tomorrow' : 'In ' + days + ' days';
    });
    if (!$$('li[data-end]', ev).length) ev.innerHTML = '<li class="empty">New dates are being added. Suggest an event with the form below.</li>';
    var cd = $('#nextEvent');
    if (cd && next) {
      $('#nextEventName').textContent = $('h3', next.li).textContent;
      (function tick() { var ms = Math.max(0, next.start - new Date()); var d = Math.floor(ms / 864e5), h = Math.floor(ms % 864e5 / 36e5), m = Math.floor(ms % 36e5 / 6e4); cd.textContent = d + 'd ' + h + 'h ' + m + 'm'; setTimeout(tick, 30000); })();
    }
  }

  /* ---------- Contests: auto-rolling deadlines ---------- */
  $$('[data-deadline]').forEach(function (el) {
    var kind = el.getAttribute('data-deadline'), now = new Date(), end;
    if (kind === 'month') end = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);
    else { var q = Math.floor(now.getMonth() / 3); end = new Date(now.getFullYear(), q * 3 + 3, 0, 23, 59, 59); }
    var label = el.getAttribute('data-label-target'); if (label && $(label)) $(label).textContent = end.toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' });
    (function tick() { var ms = Math.max(0, end - new Date()); var d = Math.floor(ms / 864e5), h = Math.floor(ms % 864e5 / 36e5), m = Math.floor(ms % 36e5 / 6e4); el.textContent = d + 'd ' + h + 'h ' + m + 'm'; setTimeout(tick, 30000); })();
  });

  /* ---------- Monthly quiz (contest) ---------- */
  var iq = $('#iqForm');
  if (iq) {
    iq.addEventListener('change', function () {
      var right = $$('input[type=radio]:checked', iq).filter(function (r) { return r.hasAttribute('data-right'); }).length;
      iq.score.value = right + ' / ' + $$('.iq-q', iq).length; iq.quiz_score.value = iq.score.value;
    });
  }

  /* ---------- Article table of contents ---------- */
  var toc = $('#tocList'), prose = $('.prose');
  if (toc && prose) {
    toc.innerHTML = $$('h2', prose).map(function (h, i) { if (!h.id) h.id = 's' + (i + 1) + '-' + h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40); return '<li><a href="#' + h.id + '">' + esc(h.textContent) + '</a></li>'; }).join('');
  }

  /* ---------- Glossary search ---------- */
  var gq = $('#glossQ');
  if (gq) gq.addEventListener('input', function () {
    var t = gq.value.toLowerCase(), shown = 0;
    $$('.gloss .term').forEach(function (div) { var hit = div.textContent.toLowerCase().indexOf(t) > -1; div.hidden = !hit; if (hit) shown++; });
    set('glossCount', shown + ' terms');
  });

  /* ---------- Copy link ---------- */
  $$('[data-share]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = location.href;
      if (navigator.share) { navigator.share({ title: document.title, url: url }).catch(function () {}); return; }
      try { navigator.clipboard.writeText(url); b.textContent = 'Link copied'; } catch (e) {}
    });
  });
})();
