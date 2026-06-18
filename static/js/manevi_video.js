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

  prepPayload() {
    return {
      topic: document.getElementById('sessionTopic')?.value?.trim() || '',
      urgency: document.getElementById('sessionUrgency')?.value || 'normal',
      notes: document.getElementById('sessionNotes')?.value?.trim() || '',
      privacy_accepted: !!document.getElementById('sessionPrivacy')?.checked,
    };
  }

  async joinSession() {
    if (!this.currentGuideId) return;
    const name = document.getElementById('visitorName')?.value?.trim() || 'Ziyaretçi';
    const prep = this.prepPayload();
    if (!prep.privacy_accepted) {
      window.spiritualNotif?.toast(i18n('session_privacy_required', 'Gizlilik onayı gerekli'), 'error');
      return;
    }
    const btn = document.getElementById('videoJoinBtn');
    btn.disabled = true;

    try {
      const res = await fetch(`/api/guides/${this.currentGuideId}/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, prep }),
      });
      const data = await res.json();
      if (!res.ok) {
        window.spiritualNotif?.toast(
          data.error === 'unavailable'
            ? i18n('guide_unavailable', 'Rehber müsait değil')
            : data.message || i18n('content_load_error', 'Hata'),
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

  async openBooking(guideId, guideName) {
    document.getElementById('bookGuideId').value = guideId;
    document.getElementById('bookModal').querySelector('h3').textContent =
      `${i18n('book_appointment', 'Randevu')} — ${guideName}`;
    const slotSelect = document.getElementById('bookSlot');
    if (slotSelect) {
      slotSelect.innerHTML = `<option value="">${i18n('select_slot', 'Saat seçin')}</option>`;
      try {
        const res = await fetch(`/api/guides/${guideId}/slots`);
        const data = await res.json();
        (data.slots || []).filter((s) => s.available).forEach((s) => {
          const opt = document.createElement('option');
          opt.value = s.id;
          opt.textContent = `${s.date} ${s.time}`;
          slotSelect.appendChild(opt);
        });
      } catch (_) {}
    }
    this.bookModal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  closeBooking() {
    this.bookModal.hidden = true;
    document.body.style.overflow = '';
    document.getElementById('bookForm')?.reset();
  }

  async submitBooking(e) {
    e.preventDefault();
    const guideId = document.getElementById('bookGuideId').value;
    const payload = {
      name: document.getElementById('bookName')?.value?.trim(),
      topic: document.getElementById('bookTopic')?.value?.trim(),
      slot_id: document.getElementById('bookSlot')?.value,
      preferred_lang: document.getElementById('bookLang')?.value,
      notes: document.getElementById('bookNotes')?.value?.trim(),
      privacy_accepted: !!document.getElementById('bookPrivacy')?.checked,
    };
    try {
      const res = await fetch(`/api/guides/${guideId}/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        window.spiritualNotif?.toast(data.message || i18n('booking_validation', 'Eksik alan'), 'error');
        return;
      }
      this.closeBooking();
      window.spiritualNotif?.toast(
        `${i18n('booking_sent', 'Alındı')} · ${i18n('reference_no', 'Ref')}: ${data.reference}`,
        'success'
      );
    } catch (_) {
      window.spiritualNotif?.toast(i18n('content_load_error', 'Hata'), 'error');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.maneviVideo = new ManeviVideo();
});
