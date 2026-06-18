function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

class MosqueMap {
  constructor() {
    this.mapEl = document.getElementById('mosqueMap');
    this.listEl = document.getElementById('mosqueList');
    this.citySelect = document.getElementById('mosqueCity');
    this.map = null;
    this.markers = [];
    document.getElementById('mosqueNearbyBtn')?.addEventListener('click', () => this.nearby());
    this.citySelect?.addEventListener('change', () => this.loadCity());
    if (this.mapEl && window.L) this.initMap();
    this.loadCity();
  }

  initMap() {
    this.map = L.map('mosqueMap').setView([39.92, 32.85], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
    }).addTo(this.map);
  }

  clearMarkers() {
    this.markers.forEach((m) => m.remove());
    this.markers = [];
  }

  renderList(items) {
    if (!this.listEl) return;
    this.listEl.innerHTML = items.map((m) => `
      <div class="mosque-list-item" data-lat="${m.lat}" data-lon="${m.lon}">
        <strong>${m.name}</strong>
        <span>${m.type === 'diyanet_center' ? i18n('diyanet_center_type', 'Diyanet') : i18n('mosque_type', 'Cami')}</span>
        <small>${m.address || m.city}${m.distance_km != null ? ` · ${m.distance_km} km` : ''}</small>
      </div>
    `).join('');
    this.listEl.querySelectorAll('.mosque-list-item').forEach((el) => {
      el.addEventListener('click', () => {
        if (this.map) this.map.setView([parseFloat(el.dataset.lat), parseFloat(el.dataset.lon)], 15);
      });
    });
  }

  addMarkers(items) {
    if (!this.map) return;
    this.clearMarkers();
    items.forEach((m) => {
      const marker = L.marker([m.lat, m.lon]).addTo(this.map).bindPopup(`<b>${m.name}</b><br>${m.address || ''}`);
      this.markers.push(marker);
    });
    if (items.length) this.map.setView([items[0].lat, items[0].lon], 12);
  }

  async loadCity() {
    const city = this.citySelect?.value || 'Ankara';
    const res = await fetch(`/api/mosques?city=${encodeURIComponent(city)}`);
    const data = await res.json();
    this.renderList(data);
    this.addMarkers(data);
  }

  nearby() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords;
      const res = await fetch(`/api/mosques?lat=${latitude}&lon=${longitude}`);
      const data = await res.json();
      this.renderList(data);
      this.addMarkers(data);
      if (this.map) this.map.setView([latitude, longitude], 11);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('mosqueMap')) window.mosqueMap = new MosqueMap();
});
