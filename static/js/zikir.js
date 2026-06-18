function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

const ZIKIR_KEY = 'diyanet_zikir';

class ZikirCounter {
  constructor() {
    this.state = { count: 0, target: 33 };
    try {
      this.state = { ...this.state, ...JSON.parse(localStorage.getItem(ZIKIR_KEY) || '{}') };
    } catch (_) {}
    this.countEl = document.getElementById('zikirCount');
    this.targetEl = document.getElementById('zikirTarget');
    this.progressEl = document.getElementById('zikirProgress');
    this.btn = document.getElementById('zikirBtn');
    document.getElementById('zikirReset')?.addEventListener('click', () => this.reset());
    document.querySelectorAll('[data-zikir-target]').forEach((b) => {
      b.addEventListener('click', () => this.setTarget(parseInt(b.dataset.zikirTarget, 10)));
    });
    this.btn?.addEventListener('click', () => this.tap());
    this.render();
  }

  setTarget(n) {
    this.state.target = n;
    this.save();
    this.render();
  }

  tap() {
    this.state.count += 1;
    if (this.state.count >= this.state.target) {
      window.spiritualNotif?.toast(i18n('zikir_complete', 'Hedef tamamlandı!'), 'success');
      if (navigator.vibrate) navigator.vibrate(100);
    }
    this.save();
    this.render();
  }

  reset() {
    this.state.count = 0;
    this.save();
    this.render();
  }

  save() {
    localStorage.setItem(ZIKIR_KEY, JSON.stringify(this.state));
  }

  render() {
    if (this.countEl) this.countEl.textContent = this.state.count;
    if (this.targetEl) this.targetEl.textContent = this.state.target;
    const pct = Math.min(100, (this.state.count / this.state.target) * 100);
    if (this.progressEl) this.progressEl.style.width = `${pct}%`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('zikirBtn')) window.zikirCounter = new ZikirCounter();
});
