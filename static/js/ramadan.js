function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

function pad(n) {
  return String(n).padStart(2, '0');
}

class RamadanCountdown {
  constructor() {
    this.iftarEl = document.getElementById('iftarCountdown');
    this.suhoorEl = document.getElementById('suhoorCountdown');
    this.city = document.getElementById('citySelect')?.value || 'Ankara';
    this.iftarSecs = 0;
    this.suhoorSecs = 0;
    this.init();
  }

  async init() {
    await this.fetch();
    setInterval(() => this.tick(), 1000);
    setInterval(() => this.fetch(), 5 * 60 * 1000);
  }

  async fetch() {
    const city = document.getElementById('citySelect')?.value || this.city;
    try {
      const res = await fetch(`/api/ramadan/status?city=${encodeURIComponent(city)}`);
      const data = await res.json();
      this.iftarSecs = data.iftar?.seconds_until || 0;
      this.suhoorSecs = data.suhoor?.seconds_until || 0;
      const dayEl = document.getElementById('fastingDay');
      if (dayEl && data.fasting_day) {
        dayEl.textContent = i18n('fasting_day', 'Ramazan {n}. gün').replace('{n}', data.fasting_day);
      }
      this.render();
    } catch (_) {}
  }

  tick() {
    if (this.iftarSecs > 0) this.iftarSecs -= 1;
    if (this.suhoorSecs > 0) this.suhoorSecs -= 1;
    this.render();
  }

  format(secs) {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    return `${pad(h)}:${pad(m)}:${pad(s)}`;
  }

  render() {
    if (this.iftarEl) this.iftarEl.textContent = this.format(this.iftarSecs);
    if (this.suhoorEl) this.suhoorEl.textContent = this.format(this.suhoorSecs);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('iftarCountdown')) window.ramadanCountdown = new RamadanCountdown();
});
