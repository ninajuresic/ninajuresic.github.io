/* ============================================================
   Nina Juresic Portfolio — app.js
   ============================================================ */

(function () {
  'use strict';

  const PASSWORD   = 'SimbaisthebestCat';
  const SESSION_KEY = 'portfolio_authenticated';

  /* ── DOM refs ── */
  const passwordScreen = document.getElementById('password-screen');
  const app            = document.getElementById('app');
  const pwInput        = document.getElementById('pw-input');
  const pwSubmit       = document.getElementById('pw-submit');
  const pwError        = document.getElementById('pw-error');

  const pages = {
    home:         document.getElementById('page-home'),
    healthtalk:   document.getElementById('page-healthtalk'),
    pitch:        document.getElementById('page-pitch'),
    localization: document.getElementById('page-localization'),
    kaphera:      document.getElementById('page-kaphera'),
    ion:          document.getElementById('page-ion'),
  };

  const navHome    = document.getElementById('nav-home');
  const hamburger  = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');

  /* ── Auth ── */
  function isAuth() {
    return sessionStorage.getItem(SESSION_KEY) === 'true';
  }

  function authenticate(pw) {
    if (pw === PASSWORD) {
      sessionStorage.setItem(SESSION_KEY, 'true');
      showApp();
    } else {
      pwError.textContent = 'Incorrect password. Please try again.';
      pwInput.value = '';
      pwInput.focus();
      pwInput.style.borderColor = '#ff3b30';
      setTimeout(() => { pwInput.style.borderColor = ''; }, 800);
    }
  }

  function showApp() {
    passwordScreen.style.display = 'none';
    app.style.display = 'block';
    showPage('home');
  }

  /* ── Password events ── */
  pwSubmit.addEventListener('click', () => authenticate(pwInput.value.trim()));
  pwInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') authenticate(pwInput.value.trim());
    pwError.textContent = '';
    pwInput.style.borderColor = '';
  });

  /* ── Page routing ── */
  let currentPage = 'home';

  function showPage(name, scrollId) {
    Object.values(pages).forEach(p => { if (p) p.style.display = 'none'; });

    const target = pages[name];
    if (target) {
      target.style.display = 'block';
      currentPage = name;
    }

    if (scrollId) {
      setTimeout(() => {
        const el = document.getElementById(scrollId);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
        else window.scrollTo({ top: 0, behavior: 'instant' });
      }, 50);
    } else {
      window.scrollTo({ top: 0, behavior: 'instant' });
    }

    closeMobileMenu();
  }

  /* ── Delegated clicks ── */
  document.addEventListener('click', (e) => {
    /* Project cards → case study */
    const proj = e.target.closest('[data-project]');
    if (proj) { e.preventDefault(); showPage(proj.dataset.project); return; }

    /* Back / page links */
    const pg = e.target.closest('[data-page]');
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

  /* ── Mobile menu ── */
  function toggleMobileMenu() {
    mobileMenu.classList.toggle('hidden');
  }

  function closeMobileMenu() {
    mobileMenu.classList.add('hidden');
  }

  /* ── Nav scroll shadow ── */
  const mainNav = document.getElementById('main-nav');
  window.addEventListener('scroll', () => {
    mainNav.classList.toggle('shadow-sm', window.scrollY > 8);
  }, { passive: true });

  /* ── Active sub-nav link on scroll ── */
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        document.querySelectorAll('.sticky a[href^="#"]').forEach(a => {
          const active = a.getAttribute('href') === `#${id}`;
          a.classList.toggle('text-[#1d1d1f]', active);
          a.classList.toggle('font-medium', active);
          a.classList.toggle('text-[#86868b]', !active);
        });
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  document.querySelectorAll('[id^="ht-"], [id^="pv-"], [id^="loc-"], [id^="ion-"]').forEach(el => {
    sectionObserver.observe(el);
  });

  /* ── Click-to-play YouTube ── */
  document.addEventListener('click', (e) => {
    const player = e.target.closest('.yt-player');
    if (!player) return;
    const vid = player.dataset.vid;
    if (!vid) return;
    window.open('https://www.youtube.com/watch?v=' + vid, '_blank', 'noopener');
  });

  /* ── Init ── */
  if (isAuth()) {
    showApp();
  } else {
    passwordScreen.style.display = 'flex';
    app.style.display = 'none';
    setTimeout(() => pwInput.focus(), 150);
  }

})();
