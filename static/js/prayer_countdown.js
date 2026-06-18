function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

function pad(n) {
  return String(n).padStart(2, '0');
}

class PrayerCountdown {
  constructor() {
    this.el = document.querySelector('.next-countdown');
    this.card = document.getElementById('homePrayerCard');
    this.seconds = parseInt(this.el?.dataset.seconds || '0', 10);
    this.city = document.getElementById('homeCitySelect')?.value || 'Ankara';
    this.timer = null;
    if (this.el && this.seconds > 0) this.start();
    else if (this.el) this.refresh();
  }

  start() {
    this.render();
    this.timer = setInterval(() => {
      this.seconds -= 1;
      if (this.seconds <= 0) {
        this.refresh();
        return;
      }
      this.render();
    }, 1000);
  }

  render() {
    if (!this.el) return;
    const h = Math.floor(this.seconds / 3600);
    const m = Math.floor((this.seconds % 3600) / 60);
    const s = this.seconds % 60;
    const lang = window.LANG || 'tr';
    if (lang === 'en') {
      this.el.textContent = `${h}h ${pad(m)}m ${pad(s)}s`;
    } else if (lang === 'ar') {
      this.el.textContent = `${h}س ${pad(m)}د ${pad(s)}ث`;
    } else {
      this.el.textContent = `${h}s ${pad(m)}dk ${pad(s)}sn`;
    }
  }

  async refresh() {
    clearInterval(this.timer);
    const city = document.getElementById('homeCitySelect')?.value || this.city;
    try {
      const res = await fetch(`/api/prayer/today?city=${encodeURIComponent(city)}`);
      const data = await res.json();
      if (typeof updatePrayerCard === 'function') updatePrayerCard(data);
      if (data.next?.seconds_until) {
        this.seconds = data.next.seconds_until;
        this.el = document.querySelector('.next-countdown');
        if (this.el) {
          this.el.dataset.seconds = this.seconds;
          this.start();
        }
      }
      this.checkPrayerNotification(data);
    } catch (_) {}
  }

  checkPrayerNotification(data) {
    const settings = window.spiritualNotif?.settings;
    if (!settings?.enabled || !settings?.prayer || !data?.next) return;
    const key = `diyanet_prayer_${data.next.key}_${data.next.time}`;
    if (data.next.seconds_until <= 60 && data.next.seconds_until > 0 && localStorage.getItem(key) !== '1') {
      const body = i18n('notif_prayer_body', '{label} vakti')
        .replace('{label}', data.next.label)
        .replace('{time}', data.next.time);
      window.spiritualNotif?.notify(i18n('notif_prayer', 'Namaz vakti'), body);
      localStorage.setItem(key, '1');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.prayerCountdown = new PrayerCountdown();
  setInterval(() => window.prayerCountdown?.refresh(), 5 * 60 * 1000);
});
