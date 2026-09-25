/* ============================================================
   Nina Juresic Portfolio — app.js
   ============================================================ */

(function () {
  'use strict';

  /* ── Per-project locks ─────────────────────────────────── */
  const UNLOCK_PW  = 'SimbaisthebestCat';
  const UNLOCK_KEY = 'portfolio_unlocked';
  const LOCKED     = ['pitch', 'localization'];

  function getUnlocked() {
    try { return JSON.parse(sessionStorage.getItem(UNLOCK_KEY) || '[]'); } catch { return []; }
  }
  function saveUnlocked(list) {
    sessionStorage.setItem(UNLOCK_KEY, JSON.stringify(list));
  }
  function isUnlocked(name) {
    return !LOCKED.includes(name) || getUnlocked().includes(name);
  }
  function unlockProject(name) {
    const list = getUnlocked();
    if (!list.includes(name)) { list.push(name); saveUnlocked(list); }
    revealCard(name);
  }
  function revealCard(name) {
    const card = document.querySelector('[data-project="' + name + '"]');
    if (!card) return;
    card.querySelectorAll('.when-locked').forEach(function (el) { el.style.display = 'none'; });
    card.querySelectorAll('.when-unlocked').forEach(function (el) { el.style.removeProperty('display'); });
    card.classList.add('cursor-pointer');
  }

  /* Restore unlocked state on load */
  getUnlocked().forEach(function (name) { revealCard(name); });

  /* ── Unlock modal ──────────────────────────────────────── */
  var modal        = document.getElementById('unlock-modal');
  var unlockInput  = document.getElementById('unlock-input');
  var unlockError  = document.getElementById('unlock-error');
  var unlockSubmit = document.getElementById('unlock-submit');
  var unlockCancel = document.getElementById('unlock-cancel');
  var pendingProject = null;

  function openModal(name) {
    pendingProject = name;
    unlockInput.value = '';
    unlockError.textContent = '';
    unlockInput.style.borderColor = '';
    modal.style.display = 'flex';
    setTimeout(function () { unlockInput.focus(); }, 100);
  }
  function closeModal() {
    modal.style.display = 'none';
    pendingProject = null;
  }
  function tryUnlock() {
    if (unlockInput.value.trim() === UNLOCK_PW) {
      var name = pendingProject;
      unlockProject(name);
      closeModal();
      showPage(name);
    } else {
      unlockError.textContent = 'Incorrect password.';
      unlockInput.value = '';
      unlockInput.style.borderColor = '#ff3b30';
      setTimeout(function () { unlockInput.style.borderColor = ''; }, 800);
      unlockInput.focus();
    }
  }

  unlockSubmit.addEventListener('click', tryUnlock);
  unlockInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') tryUnlock();
    unlockError.textContent = '';
    unlockInput.style.borderColor = '';
  });
  unlockCancel.addEventListener('click', closeModal);
  modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });

  /* ── DOM refs ──────────────────────────────────────────── */
  var pages = {
    home:         document.getElementById('page-home'),
    healthtalk:   document.getElementById('page-healthtalk'),
    pitch:        document.getElementById('page-pitch'),
    localization: document.getElementById('page-localization'),
    kaphera:      document.getElementById('page-kaphera'),
    ion:          document.getElementById('page-ion'),
  };

  var hamburger  = document.getElementById('hamburger');
  var mobileMenu = document.getElementById('mobile-menu');

  /* ── Page routing ──────────────────────────────────────── */
  var currentPage = 'home';

  function showPage(name, scrollId) {
    Object.values(pages).forEach(function (p) { if (p) p.style.display = 'none'; });

    var target = pages[name];
    if (target) { target.style.display = 'block'; currentPage = name; }

    if (scrollId) {
      setTimeout(function () {
        var el = document.getElementById(scrollId);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
        else window.scrollTo({ top: 0, behavior: 'instant' });
      }, 50);
    } else {
      window.scrollTo({ top: 0, behavior: 'instant' });
    }

    closeMobileMenu();
  }

  /* ── Delegated clicks ──────────────────────────────────── */
  document.addEventListener('click', function (e) {
    /* Unlock button on locked card — must check before project card */
    var unlockBtn = e.target.closest('.unlock-btn');
    if (unlockBtn) {
      e.preventDefault();
      e.stopPropagation();
      openModal(unlockBtn.dataset.unlock);
      return;
    }

    /* Project cards */
    var proj = e.target.closest('[data-project]');
    if (proj) {
      e.preventDefault();
      var name = proj.dataset.project;
      if (!isUnlocked(name)) { openModal(name); return; }
      showPage(name);
      return;
    }

    /* Back / page links */
    var pg = e.target.closest('[data-page]');
    if (pg) {
      e.preventDefault();
      showPage(pg.dataset.page, pg.dataset.scroll);
      return;
    }

    /* Hamburger */
    if (e.target.closest('#hamburger')) { toggleMobileMenu(); return; }

    /* Nav home logo */
    if (e.target.closest('#nav-home')) { showPage('home'); return; }
  });

  /* ── Mobile menu ───────────────────────────────────────── */
  function toggleMobileMenu() { mobileMenu.classList.toggle('hidden'); }
  function closeMobileMenu()  { mobileMenu.classList.add('hidden'); }

  /* ── Nav scroll shadow ─────────────────────────────────── */
  var mainNav = document.getElementById('main-nav');
  window.addEventListener('scroll', function () {
    mainNav.classList.toggle('shadow-sm', window.scrollY > 8);
  }, { passive: true });

  /* ── Active sub-nav link on scroll ────────────────────── */
  var sectionObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var id = entry.target.id;
        document.querySelectorAll('.sticky a[href^="#"]').forEach(function (a) {
          var active = a.getAttribute('href') === '#' + id;
          a.classList.toggle('text-[#1d1d1f]', active);
          a.classList.toggle('font-medium', active);
          a.classList.toggle('text-[#86868b]', !active);
        });
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  document.querySelectorAll('[id^="ht-"], [id^="pv-"], [id^="loc-"], [id^="ion-"]').forEach(function (el) {
    sectionObserver.observe(el);
  });

  /* ── Click-to-play YouTube ─────────────────────────────── */
  document.addEventListener('click', function (e) {
    var player = e.target.closest('.yt-player');
    if (!player) return;
    var vid = player.dataset.vid;
    if (!vid) return;
    window.open('https://www.youtube.com/watch?v=' + vid, '_blank', 'noopener');
  });

  /* ── Init ──────────────────────────────────────────────── */
  showPage('home');

})();
