function i18n(key, fallback = '') {
  return (window.I18N && window.I18N[key]) || fallback;
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('fetvaSearch');
  const results = document.getElementById('fetvaResults');
  if (!input || !results) return;

  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const q = input.value.trim();
      const res = await fetch(`/api/fetva/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!data.length) {
        results.innerHTML = `<p class="fetva-empty">${i18n('fetva_no_results', 'Sonuç yok')}</p>`;
        return;
      }
      results.innerHTML = data.map((item) => `
        <details class="faq-item">
          <summary>${item.question}</summary>
          <p>${item.answer}</p>
        </details>
      `).join('');
    }, 300);
  });
});
