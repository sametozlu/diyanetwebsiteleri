function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

class QuranReader {
  constructor() {
    this.select = document.getElementById('surahSelect');
    this.body = document.getElementById('surahBody');
    this.audio = document.getElementById('quranAudio');
    this.playBtn = document.getElementById('quranPlayBtn');
    this.select?.addEventListener('change', () => this.loadSurah(this.select.value));
    this.playBtn?.addEventListener('click', () => this.toggleAudio());
    if (this.select?.value) this.loadSurah(this.select.value);
  }

  async loadSurah(num) {
    if (!this.body) return;
    this.body.innerHTML = '<p class="loading-text">...</p>';
    const res = await fetch(`/api/quran/surah/${num}`);
    const data = await res.json();
    if (this.audio) this.audio.src = data.audio;
    this.body.innerHTML = data.ayahs.map((a) => `
      <div class="ayah-row">
        <span class="ayah-num">${a.number}</span>
        <p class="ayah-arabic">${a.arabic}</p>
        <p class="ayah-translation">${a.translation}</p>
      </div>
    `).join('') || '<p>—</p>';
  }

  toggleAudio() {
    if (!this.audio) return;
    if (this.audio.paused) {
      this.audio.play();
      this.playBtn.textContent = i18n('pause_audio', 'Durdur');
    } else {
      this.audio.pause();
      this.playBtn.textContent = i18n('play_audio', 'Dinle');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('surahSelect')) window.quranReader = new QuranReader();
});
