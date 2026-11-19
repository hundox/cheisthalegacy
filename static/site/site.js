(() => {
  const toggle = document.querySelector('.menu-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? '×' : '☰';
  });
  document.querySelectorAll('.nav-links a').forEach(link => link.addEventListener('click', () => {
    links?.classList.remove('open');
    toggle?.setAttribute('aria-expanded', 'false');
  }));
  const dialog = document.querySelector('#photo-dialog');
  if (dialog) {
    const image = dialog.querySelector('img');
    const caption = dialog.querySelector('p');
    document.querySelectorAll('.photo-open').forEach(button => button.addEventListener('click', () => {
      image.src = button.dataset.full || button.querySelector('img')?.src || '';
      image.alt = button.dataset.alt || '';
      caption.textContent = image.alt;
      dialog.showModal();
    }));
    dialog.querySelector('.dialog-close')?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  }
  const slides = [...document.querySelectorAll('.quote-slide')];
  if (slides.length) {
    let current = 0;
    const count = document.querySelector('.quote-current');
    const show = index => {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => slide.classList.toggle('active', i === current));
      if (count) count.textContent = String(current + 1);
    };
    document.querySelector('.quote-prev')?.addEventListener('click', () => show(current - 1));
    document.querySelector('.quote-next')?.addEventListener('click', () => show(current + 1));
    window.setInterval(() => show(current + 1), 6000);
  }
})();
