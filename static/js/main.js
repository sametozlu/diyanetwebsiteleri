function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initScrollTop();
  initCitySelect();
  loadHijriDate();
});

function initMobileMenu() {
  const toggle = document.getElementById('menuToggle');
  const nav = document.getElementById('nav');
  const header = document.getElementById('header');

  toggle?.addEventListener('click', () => {
    toggle.classList.toggle('active');
    nav?.classList.toggle('open');
  });

  nav?.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      toggle?.classList.remove('active');
      nav?.classList.remove('open');
    });
  });

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) header?.classList.add('scrolled');
    else header?.classList.remove('scrolled');
  });
}

function initScrollTop() {
  const btn = document.getElementById('scrollTop');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) btn?.classList.add('visible');
    else btn?.classList.remove('visible');
  });
  btn?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

function initCitySelect() {
  const select = document.getElementById('homeCitySelect');
  if (!select || select.dataset.redirect === 'false') {
    select?.addEventListener('change', async (e) => {
      const city = e.target.value;
      const res = await fetch(`/api/prayer/today?city=${encodeURIComponent(city)}`);
      const data = await res.json();
      updatePrayerCard(data);
    });
  }
}

async function loadHijriDate() {
  try {
    const res = await fetch('/api/content/daily');
    const data = await res.json();
    const el = document.getElementById('hijriDateText');
    if (el && data.hijri) el.textContent = data.hijri;
  } catch (_) {}
}

function updatePrayerCard(data) {
  const card = document.getElementById('homePrayerCard');
  if (!card) return;

  const dateEl = card.querySelector('.prayer-date');
  if (dateEl) dateEl.textContent = `${data.gregorian} · ${data.hijri}`;

  data.timings.forEach(t => {
    const item = card.querySelector(`[data-key="${t.key}"]`);
    if (item) {
      item.querySelector('.prayer-value').textContent = t.time;
      item.classList.toggle('active', t.key === data.active);
    }
  });

  const next = card.querySelector('.next-prayer');
  if (next && data.next) {
    const label = i18n('next_prayer', 'Sonraki');
    next.innerHTML = `<span>${label}: <strong>${data.next.label}</strong></span><span class="next-countdown">${data.next.remaining}</span>`;
  }
}
