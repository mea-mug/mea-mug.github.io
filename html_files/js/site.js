/* ==========================================================================
   MEA — Mughrabi Engineering Agencies
   Shared behaviour for every page.

     1. Theme (dark / light), remembered between visits
     2. Language (English / Arabic) with right-to-left switching
     3. Mobile navigation
     4. Current year in the footer
     5. Scroll reveal + sticky-header shadow + back-to-top
     6. Equipment filtering
     7. Lightbox for photos
   ========================================================================== */
(function () {
  'use strict';

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- 1. Theme ---------------------------------------------------- */
  var THEME_KEY = 'mea-theme';

  function applyTheme(mode) {
    // mode is "dark", "light", or null meaning "follow the operating system"
    if (mode) {
      document.documentElement.setAttribute('data-theme', mode);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var isDark = mode ? mode === 'dark' : systemDark;
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.textContent = isDark ? '☀' : '☾';
      btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
      btn.setAttribute('title', isDark ? 'Light mode' : 'Dark mode');
    });
  }

  applyTheme(store.get(THEME_KEY));

  // If the visitor never chose, follow the OS live.
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
    if (!store.get(THEME_KEY)) applyTheme(null);
  });

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    var current = document.documentElement.getAttribute('data-theme');
    if (!current) {
      current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    var next = current === 'dark' ? 'light' : 'dark';
    store.set(THEME_KEY, next);
    applyTheme(next);
  });

  /* ---------- 2. Language -------------------------------------------------
     Every translatable element carries data-en and data-ar. Switching swaps
     the text, the page direction, and the <html lang> attribute.
     ---------------------------------------------------------------------- */
  var LANG_KEY = 'mea-lang';

  function applyLang(lang) {
    var ar = lang === 'ar';
    var html = document.documentElement;
    html.setAttribute('lang', ar ? 'ar' : 'en');
    html.setAttribute('dir', ar ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-en]').forEach(function (el) {
      var val = ar ? el.getAttribute('data-ar') : el.getAttribute('data-en');
      if (val === null) return;
      // Keep any markup-free swap simple; \n becomes a line break.
      if (val.indexOf('\n') > -1) {
        el.innerHTML = val.split('\n').map(escapeHtml).join('<br>');
      } else {
        el.textContent = val;
      }
    });

    // Placeholders on form fields
    document.querySelectorAll('[data-ph-en]').forEach(function (el) {
      el.setAttribute('placeholder', ar ? el.getAttribute('data-ph-ar') : el.getAttribute('data-ph-en'));
    });

    document.querySelectorAll('[data-lang-toggle]').forEach(function (btn) {
      btn.textContent = ar ? 'EN' : 'ع';
      btn.setAttribute('aria-label', ar ? 'Switch to English' : 'التبديل إلى العربية');
      btn.setAttribute('title', ar ? 'English' : 'العربية');
    });
  }

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  applyLang(store.get(LANG_KEY) || 'en');

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-lang-toggle]');
    if (!btn) return;
    var next = document.documentElement.getAttribute('lang') === 'ar' ? 'en' : 'ar';
    store.set(LANG_KEY, next);
    applyLang(next);
  });

  /* ---------- 3. Mobile navigation ---------------------------------------- */
  var navToggle = document.querySelector('[data-nav-toggle]');
  var navLinks = document.getElementById('nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      navToggle.textContent = open ? '✕' : '☰';
    });
    navLinks.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.textContent = '☰';
      }
    });
  }

  /* ---------- 4. Current year --------------------------------------------- */
  var year = new Date().getFullYear();
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = year; });

  /* ---------- 5. Scroll behaviour ------------------------------------------ */
  var header = document.querySelector('.site-header');
  var toTop = document.querySelector('.to-top');

  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle('scrolled', y > 8);
    if (toTop) toTop.classList.toggle('show', y > 500);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (toTop) {
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  var revealables = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealables.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- 6. Equipment filtering ---------------------------------------- */
  var filterBar = document.querySelector('.filter-bar');
  if (filterBar) {
    var items = Array.prototype.slice.call(document.querySelectorAll('.equip'));
    var emptyNote = document.querySelector('.empty-note');

    function applyFilter(cat) {
      var target = filterBar.querySelector('[data-filter="' + cat + '"]');
      if (!target) return false;

      filterBar.querySelectorAll('.filter-btn').forEach(function (b) {
        b.classList.toggle('active', b === target);
        b.setAttribute('aria-pressed', b === target ? 'true' : 'false');
      });

      var shown = 0;
      items.forEach(function (item) {
        var match = cat === 'all' || item.getAttribute('data-cat') === cat;
        item.classList.toggle('hide', !match);
        if (match) shown++;
      });
      if (emptyNote) emptyNote.classList.toggle('show', shown === 0);
      return true;
    }

    filterBar.addEventListener('click', function (e) {
      var btn = e.target.closest('.filter-btn');
      if (!btn) return;
      applyFilter(btn.getAttribute('data-filter'));
      // Drop a stale #category from the address bar so it does not fight the click.
      if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname);
      }
    });

    // Links such as /equipment#concrete arrive pre-filtered.
    function fromHash() {
      var h = window.location.hash.replace('#', '');
      if (h) applyFilter(h);
    }
    fromHash();
    window.addEventListener('hashchange', fromHash);
  }

  /* ---------- 7. Lightbox ---------------------------------------------------- */
  var lightbox = document.querySelector('.lightbox');
  if (lightbox) {
    var lbImg = lightbox.querySelector('img');
    var lbCap = lightbox.querySelector('.lightbox-cap');
    var sources = [];
    var index = 0;

    function collect() {
      sources = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'))
        .filter(function (el) { return !el.closest('.hide'); });
    }

    function show(i) {
      if (!sources.length) return;
      index = (i + sources.length) % sources.length;
      var el = sources[index];
      lbImg.src = el.getAttribute('data-full') || el.getAttribute('src');
      lbImg.alt = el.getAttribute('alt') || '';
      if (lbCap) lbCap.textContent = el.getAttribute('data-caption') || el.getAttribute('alt') || '';
    }

    function open(el) {
      collect();
      var i = sources.indexOf(el);
      show(i < 0 ? 0 : i);
      lightbox.classList.add('open');
      document.body.style.overflow = 'hidden';
    }

    function close() {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
      lbImg.src = '';
    }

    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-lightbox]');
      if (trigger) { e.preventDefault(); open(trigger); return; }

      if (e.target.closest('.lightbox-close')) { close(); return; }
      if (e.target.closest('.lightbox-prev')) { show(index - 1); return; }
      if (e.target.closest('.lightbox-next')) { show(index + 1); return; }
      // Click on the dark backdrop closes it
      if (e.target === lightbox) close();
    });

    document.addEventListener('keydown', function (e) {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') show(index + 1);
      if (e.key === 'ArrowLeft') show(index - 1);
    });
  }

})();
