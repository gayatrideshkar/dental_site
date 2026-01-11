document.addEventListener('DOMContentLoaded', function(){
  // Treatments Dropdown Logic
  const dropdown = document.getElementById("treatmentsDropdown");
  const button = document.getElementById("treatments-button");

  if (dropdown && button) {
    // ensure default aria state
    button.setAttribute('aria-expanded', 'false');

    button.addEventListener("click", (e) => {
      e.stopPropagation();
      dropdown.classList.toggle("open");
      button.setAttribute(
        "aria-expanded",
        dropdown.classList.contains("open").toString()
      );
    });

    // Close on outside click
    document.addEventListener("click", () => {
      dropdown.classList.remove("open");
      button.setAttribute("aria-expanded", "false");
    });

    // Keyboard support (ESC to close)
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        dropdown.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
      }
    });
  }

  // Reveal on scroll (Intersection Observer)
  const revealElems = document.querySelectorAll('.reveal-on-scroll');
  if ('IntersectionObserver' in window && revealElems.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          io.unobserve(entry.target);
        }
      });
    }, {threshold: 0.15});

    revealElems.forEach(el => io.observe(el));
  } else {
    // fallback: reveal all
    revealElems.forEach(el => el.classList.add('revealed'));
  }

  // Lazy load images with data-src
  const lazyImages = document.querySelectorAll('img[data-src]');
  if ('IntersectionObserver' in window && lazyImages.length) {
    const imgIo = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.getAttribute('data-src');
          img.removeAttribute('data-src');
          imgIo.unobserve(img);
        }
      });
    }, {rootMargin: '100px'});
    lazyImages.forEach(img => imgIo.observe(img));
  } else {
    lazyImages.forEach(img => {
      img.src = img.getAttribute('data-src');
      img.removeAttribute('data-src');
    });
  }

  // Parallax hero effect (subtle)
  const heroEl = document.getElementById('hero');
  if (heroEl) {
    let raf = null;
    window.addEventListener('scroll', () => {
      if (raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const offset = Math.min(window.scrollY, window.innerHeight);
        heroEl.style.backgroundPosition = `center ${offset * 0.2}px`;
      });
    }, {passive: true});
  }

  // Simple lightbox for gallery
  const lightbox = document.getElementById('lightbox');
  const lbImg = lightbox ? lightbox.querySelector('.lightbox-content img') : null;
  const lbClose = lightbox ? lightbox.querySelector('.lightbox-close') : null;
  const lbPrev = lightbox ? lightbox.querySelector('.lightbox-prev') : null;
  const lbNext = lightbox ? lightbox.querySelector('.lightbox-next') : null;
  const thumbs = Array.from(document.querySelectorAll('.gallery .thumb'));
  let currentIndex = -1;

  function openLightbox(index) {
    if (!lightbox || !lbImg) return;
    const src = thumbs[index].getAttribute('data-src') || thumbs[index].querySelector('img')?.src;
    lbImg.src = src;
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    currentIndex = index;
    // update aria and control visibility
    if (lbPrev) lbPrev.style.display = (currentIndex > 0) ? 'block' : 'none';
    if (lbNext) lbNext.style.display = (currentIndex < thumbs.length - 1) ? 'block' : 'none';
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    lbImg.src = '';
    currentIndex = -1;
  }

  thumbs.forEach((t, idx) => {
    t.addEventListener('click', (e) => {
      e.preventDefault();
      openLightbox(idx);
    });
  });

  if (lbClose) lbClose.addEventListener('click', closeLightbox);
  if (lbPrev) lbPrev.addEventListener('click', (e) => { e.stopPropagation(); if (currentIndex > 0) openLightbox(--currentIndex); });
  if (lbNext) lbNext.addEventListener('click', (e) => { e.stopPropagation(); if (currentIndex < thumbs.length - 1) openLightbox(++currentIndex); });
  if (lightbox) lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox || !lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') {
      if (currentIndex < thumbs.length - 1) openLightbox(++currentIndex);
    }
    if (e.key === 'ArrowLeft') {
      if (currentIndex > 0) openLightbox(--currentIndex);
    }
  });

});
