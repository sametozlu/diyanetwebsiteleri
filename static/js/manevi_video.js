function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

class ManeviVideo {
  constructor() {
    this.modal = document.getElementById('videoModal');
    this.bookModal = document.getElementById('bookModal');
    this.currentGuideId = null;
    this.bind();
  }

  bind() {
    document.querySelectorAll('.guide-video-btn').forEach((btn) => {
      btn.addEventListener('click', () => this.openPrejoin(btn.dataset.guideId, btn.dataset.guideName));
    });
    document.querySelectorAll('.guide-book-btn').forEach((btn) => {
      btn.addEventListener('click', () => this.openBooking(btn.dataset.guideId, btn.dataset.guideName));
    });

    document.getElementById('videoJoinBtn')?.addEventListener('click', () => this.joinSession());
    document.getElementById('videoEndBtn')?.addEventListener('click', () => this.closeVideo());
    document.getElementById('videoModalClose')?.addEventListener('click', () => this.closeVideo());
    document.getElementById('videoModalBackdrop')?.addEventListener('click', () => this.closeVideo());

    document.getElementById('bookModalClose')?.addEventListener('click', () => this.closeBooking());
    document.getElementById('bookModalBackdrop')?.addEventListener('click', () => this.closeBooking());
    document.getElementById('bookForm')?.addEventListener('submit', (e) => this.submitBooking(e));
  }

  openPrejoin(guideId, guideName) {
    this.currentGuideId = guideId;
    document.getElementById('videoModalTitle').textContent = guideName;
    document.getElementById('videoModalSubtitle').textContent = i18n('waiting_guide', 'Rehber bekleniyor...');
    document.getElementById('videoPrejoin').hidden = false;
    document.getElementById('videoFrameWrap').hidden = true;
    document.getElementById('videoFrame').src = '';
    this.modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  async joinSession() {
    if (!this.currentGuideId) return;
    const name = document.getElementById('visitorName')?.value?.trim() || 'Ziyaretçi';
    const btn = document.getElementById('videoJoinBtn');
    btn.disabled = true;

    try {
      const res = await fetch(`/api/guides/${this.currentGuideId}/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      const data = await res.json();
      if (!res.ok) {
        window.spiritualNotif?.toast(
          data.error === 'unavailable'
            ? i18n('guide_unavailable', 'Rehber müsait değil')
            : i18n('content_load_error', 'Hata'),
          'error'
        );
        return;
      }
      document.getElementById('videoPrejoin').hidden = true;
      document.getElementById('videoFrameWrap').hidden = false;
      document.getElementById('videoFrame').src = data.embed_url;
      document.getElementById('videoModalSubtitle').textContent = i18n('live_now', '● Canlı');
    } catch (_) {
      window.spiritualNotif?.toast(i18n('content_load_error', 'Bağlantı hatası'), 'error');
    } finally {
      btn.disabled = false;
    }
  }

  closeVideo() {
    document.getElementById('videoFrame').src = '';
    this.modal.hidden = true;
    document.body.style.overflow = '';
    this.currentGuideId = null;
  }

  openBooking(guideId, guideName) {
    document.getElementById('bookGuideId').value = guideId;
    document.getElementById('bookModal').querySelector('h3').textContent =
      `${i18n('book_appointment', 'Randevu')} — ${guideName}`;
    this.bookModal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  closeBooking() {
    this.bookModal.hidden = true;
    document.body.style.overflow = '';
    document.getElementById('bookForm')?.reset();
  }

  submitBooking(e) {
    e.preventDefault();
    this.closeBooking();
    window.spiritualNotif?.toast(i18n('booking_sent', 'Randevu talebi alındı'), 'success');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.maneviVideo = new ManeviVideo();
});
