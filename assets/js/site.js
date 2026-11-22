(function () {
  'use strict';

  var doc = document.documentElement;
  var MODES = ['academic', 'life'];
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---- Theme ------------------------------------------------------------- */
  var themeBtn = document.querySelector('.theme');

  function syncThemeLabel() {
    if (!themeBtn) return;
    var dark = doc.getAttribute('data-theme') === 'dark';
    themeBtn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
  }

  if (themeBtn) themeBtn.addEventListener('click', function () {
    var next = doc.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    doc.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    syncThemeLabel();
  });
  syncThemeLabel();

  /* ---- Signal trace -------------------------------------------------------
     Academic: an ECG, one PQRST complex per beat, with slight beat-to-beat
     variation. Life & developer: a square wave whose bits spell "henryk".
     Professional: the ECG runs into the bitstream halfway across. */
  var svg = document.querySelector('.trace svg');
  var line = document.querySelector('.trace__line');

  function f(n) { return Math.round(n * 10) / 10; }

  function ecgPath(w, h, xEnd) {
    if (xEnd == null) xEnd = w;
    var base = h * 0.6, amp = h * 0.42;
    var keys = [[0.26, 0], [0.285, 0.1], [0.315, -1], [0.345, 0.3], [0.375, 0]];

    function beat(t) {
      if (t >= 0.10 && t < 0.20) return -0.12 * Math.sin(Math.PI * (t - 0.10) / 0.10);
      if (t >= 0.48 && t < 0.66) return -0.24 * Math.sin(Math.PI * (t - 0.48) / 0.18);
      if (t < keys[0][0] || t >= keys[keys.length - 1][0]) return 0;
      for (var i = 1; i < keys.length; i++) {
        if (t < keys[i][0]) {
          var a = keys[i - 1], b = keys[i];
          return a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0]);
        }
      }
      return 0;
    }

    var d = 'M0 ' + f(base);
    var x = -70, seed = 7, step = 1.5;
    while (x < xEnd) {
      seed = (seed * 9301 + 49297) % 233280;
      var period = 250 * (0.96 + 0.08 * seed / 233280);
      for (var px = 0; px < period; px += step) {
        var X = x + px;
        if (X < 0 || X > xEnd) continue;
        d += 'L' + f(X) + ' ' + f(base + amp * beat(px / period));
      }
      x += period;
    }
    return d;
  }

  // Returns a path, or with xStart a continuation ("L…") to append to another path
  function bitsPath(w, h, xStart) {
    var word = 'henryk ', bits = '';
    for (var i = 0; i < word.length; i++) {
      bits += ('0000000' + word.charCodeAt(i).toString(2)).slice(-8);
    }
    var bw = 20, hi = h * 0.3, lo = h * 0.7, edge = 2;
    var x0 = xStart || 0;
    var y = bits[0] === '1' ? hi : lo;
    var d = (xStart ? 'L' : 'M') + f(x0) + ' ' + f(y);
    for (var n = 0, x = x0; x < w; n++, x += bw) {
      var ny = bits[n % bits.length] === '1' ? hi : lo;
      if (ny !== y) { d += 'L' + f(x) + ' ' + f(y) + 'L' + f(x + edge) + ' ' + f(ny); y = ny; }
    }
    return d + 'L' + f(w) + ' ' + f(y);
  }

  function drawTrace(animate) {
    var box = svg.getBoundingClientRect();
    var w = Math.max(1, Math.round(box.width)), h = Math.max(1, Math.round(box.height));
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    var mode = doc.getAttribute('data-mode'), d;
    if (mode === 'life') d = bitsPath(w, h);
    else if (mode === 'pro') d = ecgPath(w, h, w * 0.5) + bitsPath(w, h, Math.round(w * 0.5));
    else d = ecgPath(w, h);
    line.setAttribute('d', d);
    if (animate && !reduceMotion.matches) {
      svg.classList.remove('is-drawing');
      void svg.getBoundingClientRect(); // restart the animation
      svg.classList.add('is-drawing');
    }
  }

  var lastWidth = 0, resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (!svg) return;
      if (Math.round(svg.getBoundingClientRect().width) !== lastWidth) drawTrace(false);
      lastWidth = Math.round(svg.getBoundingClientRect().width);
    }, 120);
  });

  /* ---- Mode switch (ARIA tabs) ------------------------------------------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.switch__opt'));
  function modeOf(tab) { return tab.getAttribute('href').slice(1); }

  function setMode(mode, opts) {
    opts = opts || {};
    if (MODES.indexOf(mode) < 0) mode = 'academic';
    var changed = doc.getAttribute('data-mode') !== mode;
    doc.setAttribute('data-mode', mode);

    tabs.forEach(function (tab) {
      var on = modeOf(tab) === mode;
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.setAttribute('tabindex', on ? '0' : '-1');
    });

    if (opts.updateHash && location.hash !== '#' + mode) {
      history.replaceState(null, '', '#' + mode);
    }
    if (svg && (changed || opts.forceDraw)) drawTrace(opts.animate !== false);
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener('click', function (e) {
      e.preventDefault();
      setMode(modeOf(tab), { updateHash: true });
    });
    tab.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      var next = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      next.focus();
      setMode(modeOf(next), { updateHash: true });
    });
  });

  window.addEventListener('hashchange', function () {
    if (!tabs.length) return;
    var m = location.hash.slice(1);
    if (MODES.indexOf(m) >= 0) setMode(m);
  });

  if (tabs.length) {
    var initial = location.hash.slice(1);
    setMode(MODES.indexOf(initial) >= 0 ? initial : 'academic', { forceDraw: true });
  } else if (svg) {
    drawTrace(true); // pages with a fixed mode, e.g. /professional/
  }
  if (svg) lastWidth = Math.round(svg.getBoundingClientRect().width);

  /* ---- Live Google Scholar citations ------------------------------------- */
  var repo = document.currentScript && document.currentScript.getAttribute('data-repo');
  if (!repo) {
    var s = document.querySelector('script[data-repo]');
    repo = s && s.getAttribute('data-repo');
  }
  if (repo && window.fetch) {
    fetch('https://raw.githubusercontent.com/' + repo + '/google-scholar-stats/gs_data.json')
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        // Citation counts only go up, so stale live data (e.g. after a few weeks of
        // Scholar blocking the crawler) never replaces a newer snapshot in the HTML.
        function bump(el, live, render) {
          var snap = parseInt(el.getAttribute('data-snapshot'), 10) || 0;
          if (live > snap) el.textContent = render(live);
        }
        document.querySelectorAll('[data-citations]').forEach(function (el) {
          bump(el, data.citedby || 0, String);
        });
        document.querySelectorAll('[data-paper]').forEach(function (el) {
          var pub = data.publications && data.publications[el.getAttribute('data-paper')];
          bump(el, (pub && pub.num_citations) || 0, function (n) {
            return ', cited ' + n + (n === 1 ? ' time' : ' times');
          });
        });
      })
      .catch(function () { /* keep the snapshot numbers already on the page */ });
  }
})();
