const NOTIF_KEY = 'diyanet_notif_settings';
const LAST_HOURLY_KEY = 'diyanet_last_hourly';
const LAST_DAILY_KEY = 'diyanet_last_daily';

const defaultSettings = {
  enabled: false,
  hourlyHadith: true,
  dailyVerse: true,
  dailyHadith: true,
  esma: true,
  prayer: false,
  toast: true,
  sound: false,
};

class SpiritualNotifications {
  constructor() {
    this.settings = this.loadSettings();
    this.panel = document.getElementById('notifPanel');
    this.badge = document.getElementById('notifBadge');
    this.list = document.getElementById('notifList');
    this.init();
  }

  loadSettings() {
    try {
      return { ...defaultSettings, ...JSON.parse(localStorage.getItem(NOTIF_KEY) || '{}') };
    } catch {
      return { ...defaultSettings };
    }
  }

  saveSettings() {
    localStorage.setItem(NOTIF_KEY, JSON.stringify(this.settings));
  }

  init() {
    this.bindUI();
    this.renderSettings();
    this.startSchedulers();
    this.fetchAndUpdate(true);
  }

  bindUI() {
    document.getElementById('notifBell')?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.panel?.classList.toggle('open');
    });

    document.addEventListener('click', () => this.panel?.classList.remove('open'));
    this.panel?.addEventListener('click', (e) => e.stopPropagation());

    document.getElementById('notifEnableBtn')?.addEventListener('click', async () => {
      const i18n = (k, fb) => (window.I18N && window.I18N[k]) || fb;
      if (!('Notification' in window)) {
        this.toast(i18n('notif_unsupported', 'Tarayıcınız bildirim desteklemiyor'), 'error');
        return;
      }
      const perm = await Notification.requestPermission();
      if (perm === 'granted') {
        this.settings.enabled = true;
        this.saveSettings();
        this.toast(i18n('notif_enabled', 'Bildirimler etkinleştirildi'), 'success');
        this.renderSettings();
        new Notification('Diyanet Portal', {
          body: 'Günlük ayet ve hadis bildirimleri aktif.',
        });
      }
    });

    document.querySelectorAll('[data-notif-setting]').forEach(input => {
      input.addEventListener('change', () => {
        this.settings[input.dataset.notifSetting] = input.type === 'checkbox' ? input.checked : input.value;
        this.saveSettings();
      });
    });
  }

  renderSettings() {
    document.querySelectorAll('[data-notif-setting]').forEach(input => {
      const key = input.dataset.notifSetting;
      if (input.type === 'checkbox') input.checked = !!this.settings[key];
    });
    if (this.badge) {
      this.badge.hidden = !this.settings.enabled;
    }
  }

  startSchedulers() {
    setInterval(() => this.fetchAndUpdate(), 60 * 60 * 1000);
    setInterval(() => this.fetchAndUpdate(), 5 * 60 * 1000);
  }

  async fetchAndUpdate(silent = false) {
    const city = document.getElementById('homeCitySelect')?.value || 'Ankara';
    try {
      const res = await fetch(`/api/content/bundle?city=${encodeURIComponent(city)}`);
      const data = await res.json();
      this.updateHomeCards(data);
      this.processNotifications(data, silent);
      this.renderFeed(data);
    } catch (_) {
      if (!silent) this.toast((window.I18N && window.I18N.content_load_error) || 'İçerik yüklenemedi', 'error');
    }
  }

  updateHomeCards(data) {
    const verseEl = document.querySelector('.daily-verse .daily-text');
    const hadithEl = document.querySelector('.daily-hadith .daily-text');
    const esmaEl = document.querySelector('.daily-name-title');
    const verseRef = document.querySelector('.daily-verse .daily-ref');
    const hadithRef = document.querySelector('.daily-hadith .daily-ref');

    const verseText = data.verse?.text || data.verse?.turkish || data.daily?.verse;
    const hadithText = data.hadith?.text || data.daily?.hadith;
    const esmaAr = document.querySelector('.esma-arabic');
    const esmaMeaning = document.querySelector('.daily-name .daily-text');

    if (verseEl && verseText) verseEl.textContent = verseText;
    if (hadithEl && hadithText) hadithEl.textContent = `"${hadithText}"`;
    if (esmaEl && data.esma?.name) esmaEl.textContent = data.esma.name;
    if (esmaAr && data.esma?.ar) esmaAr.textContent = data.esma.ar;
    if (esmaMeaning && data.esma?.meaning) esmaMeaning.textContent = data.esma.meaning;
    if (verseRef && data.verse?.ref) {
      verseRef.textContent = data.verse.ref;
    } else if (verseRef && data.verse?.chapter) {
      verseRef.textContent = `Sure ${data.verse.chapter}, ${data.verse.verse}. ayet`;
    }
    if (hadithRef && data.hadith?.collection) {
      hadithRef.textContent = data.hadith.number
        ? `${data.hadith.collection} · No: ${data.hadith.number}`
        : data.hadith.collection;
    }

    const hijriEl = document.getElementById('hijriDateText');
    if (hijriEl && data.hijri) hijriEl.textContent = data.hijri;
  }

  processNotifications(data, silent) {
    if (!this.settings.enabled || silent) return;

    const hourKey = data.hourly?.updated || new Date().toISOString().slice(0, 13);
    const dayKey = data.daily?.date || new Date().toISOString().slice(0, 10);

    if (this.settings.hourlyHadith && hourKey !== localStorage.getItem(LAST_HOURLY_KEY)) {
      const text = data.hourly?.hadith || data.hadith?.text;
      if (text) {
        this.notify('Saatlik Hadis', text);
        localStorage.setItem(LAST_HOURLY_KEY, hourKey);
      }
    }

    if (dayKey !== localStorage.getItem(LAST_DAILY_KEY)) {
      if (this.settings.dailyVerse && data.verse?.turkish) {
        this.notify('Günün Ayeti', data.verse.turkish.slice(0, 180));
      }
      if (this.settings.dailyHadith && data.hadith?.text) {
        this.notify('Günün Hadisi', data.hadith.text.slice(0, 180));
      }
      if (this.settings.esma && data.esma?.name) {
        this.notify('Esma-ül Hüsna', data.esma.name);
      }
      localStorage.setItem(LAST_DAILY_KEY, dayKey);
    }
  }

  notify(title, body) {
    if (this.settings.toast) this.toast(`${title}: ${body.slice(0, 120)}...`, 'info', 8000);
    if (this.settings.enabled && Notification.permission === 'granted') {
      new Notification(title, { body: body.slice(0, 200), tag: title });
    }
  }

  renderFeed(data) {
    if (!this.list) return;
    const items = [
      { type: 'Ayet', text: data.verse?.turkish, time: 'Günlük' },
      { type: 'Hadis', text: data.hadith?.text, time: 'Günlük' },
      { type: 'Esma', text: data.esma?.name, time: data.esma?.source === 'hourly' ? 'Saatlik' : 'Günlük' },
      { type: 'Namaz', text: data.prayer?.next ? `Sonraki: ${data.prayer.next.label} (${data.prayer.next.remaining})` : '', time: data.prayer?.city },
    ].filter(i => i.text);

    this.list.innerHTML = items.map(i => `
      <div class="notif-item">
        <span class="notif-type">${i.type}</span>
        <p>${i.text.slice(0, 100)}${i.text.length > 100 ? '...' : ''}</p>
        <small>${i.time || ''}</small>
      </div>
    `).join('');
  }

  toast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer') || this.createToastContainer();
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.classList.add('show'), 10);
    setTimeout(() => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  createToastContainer() {
    const c = document.createElement('div');
    c.id = 'toastContainer';
    c.className = 'toast-container';
    document.body.appendChild(c);
    return c;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.spiritualNotif = new SpiritualNotifications();
  document.getElementById('refreshHourly')?.addEventListener('click', () => {
    window.spiritualNotif?.fetchAndUpdate();
    window.spiritualNotif?.toast((window.I18N && window.I18N.content_updated) || 'İçerik güncellendi', 'success');
  });
});
