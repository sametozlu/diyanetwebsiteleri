class RadioPlayer {
  constructor() {
    this.audio = document.getElementById('globalRadioPlayer');
    this.widget = document.getElementById('radioWidget');
    this.hls = null;
    this.stations = {};
    this.currentStation = null;
    this.isPlaying = false;
    this.retryCount = 0;

    if (!this.audio) return;
    this.init();
  }

  t(key, fallback = '') {
    return (window.I18N && window.I18N[key]) || fallback;
  }

  async init() {
    await this.loadStations();
    this.bindWidget();
    this.bindRadioPage();
    this.bindAudioEvents();
  }

  async loadStations() {
    try {
      const res = await fetch('/api/radio/stations');
      this.stations = await res.json();
    } catch (_) {
      this.stations = {};
    }
  }

  bindAudioEvents() {
    this.audio.addEventListener('playing', () => {
      this.isPlaying = true;
      this.retryCount = 0;
      this.onStateChange(true);
    });
    this.audio.addEventListener('pause', () => this.onStateChange(false));
    this.audio.addEventListener('waiting', () => this.setStatus(this.t('connecting', 'Bağlanıyor...')));
    this.audio.addEventListener('error', () => this.handleError());
  }

  handleError() {
    this.setStatus(this.t('reconnecting', 'Bağlantı kesildi, yeniden deneniyor...'));
    if (this.retryCount < 3 && this.currentStation) {
      this.retryCount += 1;
      setTimeout(() => this.play(this.currentStation, this.currentName, true), 2000);
    } else {
      this.setStatus(this.t('stream_error', 'Yayın hatası — lütfen tekrar deneyin'));
    }
  }

  destroyHls() {
    if (this.hls) {
      this.hls.destroy();
      this.hls = null;
    }
  }

  async play(station, name, isRetry = false) {
    if (!this.audio) return;

    const info = this.stations[station];
    if (!info) {
      this.setStatus(this.t('station_not_found', 'İstasyon bulunamadı'));
      return;
    }

    this.currentStation = station;
    this.currentName = name || info.name;
    const playlistUrl = info.playlist || `/api/radio/playlist/${station}`;

    this.destroyHls();
    this.audio.pause();
    this.audio.removeAttribute('src');
    this.audio.load();

    this.setStatus(this.t('connecting', 'Bağlanıyor...'));
    this.updateUI(this.currentName);
    this.widget?.classList.add('visible');
    this.highlightStation(station);

    const volume = (document.getElementById('volumeSlider')?.value || 80) / 100;
    this.audio.volume = volume;

    if (window.Hls && Hls.isSupported()) {
      this.hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        maxBufferLength: 30,
        manifestLoadingMaxRetry: 4,
        fragLoadingMaxRetry: 6,
      });
      this.hls.loadSource(playlistUrl);
      this.hls.attachMedia(this.audio);
      this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
        this.audio.play().catch(() => this.setStatus(this.t('playback_failed', 'Oynatma başlatılamadı — tıklayın')));
      });
      this.hls.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) {
          if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
            this.hls.startLoad();
          } else {
            this.handleError();
          }
        }
      });
    } else if (this.audio.canPlayType('application/vnd.apple.mpegurl')) {
      this.audio.src = playlistUrl;
      this.audio.play().catch(() => this.setStatus('Oynatma başlatılamadı'));
    } else {
      this.setStatus(this.t('hls_unsupported', 'Tarayıcınız HLS yayını desteklemiyor'));
    }
  }

  pause() {
    this.audio?.pause();
    this.isPlaying = false;
    this.onStateChange(false);
  }

  toggle() {
    if (this.isPlaying) this.pause();
    else if (this.currentStation) this.play(this.currentStation, this.currentName);
    else this.play('diyanet', 'Diyanet Radyo');
  }

  onStateChange(playing) {
    this.isPlaying = playing;
    this.setStatus(playing ? this.t('live_now', '● Canlı yayın') : this.t('stopped', 'Durduruldu'));
    this.updatePlayButtons(playing);
  }

  updatePlayButtons(playing) {
    document.querySelectorAll('#widgetPlayBtn, #playerPlayPause').forEach(btn => {
      btn?.querySelector('.icon-play')?.toggleAttribute('hidden', playing);
      btn?.querySelector('.icon-pause')?.toggleAttribute('hidden', !playing);
    });
    document.querySelectorAll('.radio-play-btn').forEach(btn => {
      const active = btn.dataset.station === this.currentStation && playing;
      btn.querySelector('.btn-play-text').textContent = active ? this.t('stop', 'Durdur') : this.t('listen', 'Dinle');
    });
  }

  setStatus(text) {
    const el = document.getElementById('playerStatus');
    if (el) el.textContent = text;
  }

  updateUI(name) {
    document.getElementById('widgetStationName') && (document.getElementById('widgetStationName').textContent = name);
    document.getElementById('nowPlayingName') && (document.getElementById('nowPlayingName').textContent = name);
    const card = document.querySelector(`.radio-station-card[data-station="${this.currentStation}"]`);
    const tagline = card?.querySelector('.radio-station-badge')?.textContent;
    const tagEl = document.getElementById('nowPlayingTagline');
    if (tagEl && tagline) tagEl.textContent = tagline;
  }

  highlightStation(station) {
    document.querySelectorAll('.radio-station-card').forEach(c => {
      c.classList.toggle('playing', c.dataset.station === station && this.isPlaying);
      c.classList.toggle('active', c.dataset.station === station);
    });
  }

  bindWidget() {
    document.getElementById('widgetPlayBtn')?.addEventListener('click', () => this.toggle());
    document.getElementById('widgetCloseBtn')?.addEventListener('click', () => {
      this.pause();
      this.destroyHls();
      this.widget?.classList.remove('visible');
    });
    document.getElementById('widgetExpandBtn')?.addEventListener('click', () => {
      window.location.href = '/radyo';
    });
  }

  bindRadioPage() {
    document.querySelectorAll('.radio-play-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const station = btn.dataset.station;
        const card = btn.closest('.radio-station-card');
        const name = card?.dataset.name || station;
        if (this.currentStation === station && this.isPlaying) this.pause();
        else this.play(station, name);
      });
    });

    document.getElementById('playerPlayPause')?.addEventListener('click', () => this.toggle());
    document.getElementById('volumeSlider')?.addEventListener('input', (e) => {
      if (this.audio) this.audio.volume = e.target.value / 100;
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.diyanetRadio = new RadioPlayer();
});
