function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

class QiblaCompass {
  constructor() {
    this.bearing = 0;
    this.heading = 0;
    this.compass = document.getElementById('qiblaCompass');
    this.arrow = document.getElementById('qiblaArrow');
    this.bearingEl = document.getElementById('qiblaBearing');
    this.distanceEl = document.getElementById('qiblaDistance');
    document.getElementById('qiblaLocateBtn')?.addEventListener('click', () => this.locate());
    if (window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientationabsolute', (e) => this.onOrient(e), true);
      window.addEventListener('deviceorientation', (e) => this.onOrient(e), true);
    }
  }

  async locate() {
    if (!navigator.geolocation) {
      window.spiritualNotif?.toast(i18n('location_denied', 'Konum yok'), 'error');
      return;
    }
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords;
      const res = await fetch(`/api/qibla?lat=${latitude}&lon=${longitude}`);
      const data = await res.json();
      this.bearing = data.bearing;
      if (this.bearingEl) {
        this.bearingEl.textContent = `${data.bearing}${i18n('degrees', '°')}`;
      }
      if (this.distanceEl) {
        this.distanceEl.textContent = `${data.distance_km} ${i18n('km', 'km')}`;
      }
      this.updateArrow();
    }, () => window.spiritualNotif?.toast(i18n('location_denied', 'Konum izni gerekli'), 'error'));
  }

  onOrient(e) {
    const h = e.webkitCompassHeading ?? (360 - (e.alpha || 0));
    if (h != null) {
      this.heading = h;
      this.updateArrow();
    }
  }

  updateArrow() {
    if (!this.arrow) return;
    const rot = this.bearing - this.heading;
    this.arrow.style.transform = `rotate(${rot}deg)`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('qiblaCompass')) {
    window.qiblaCompass = new QiblaCompass();
  }
});
