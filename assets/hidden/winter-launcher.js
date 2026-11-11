(() => {
  'use strict';
  const logo = document.querySelector('.hero img[src*="logo"]');
  if (!logo) return;

  let taps = 0;
  let lastTap = 0;
  let overlay = null;
  let previousFocus = null;

  function closeWinter() {
    if (!overlay) return;
    overlay.remove();
    overlay = null;
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    if (previousFocus && previousFocus.isConnected) previousFocus.focus();
  }

  function openWinter() {
    if (overlay) return;
    previousFocus = document.activeElement;
    overlay = document.createElement('div');
    overlay.id = 'winter-easter-egg';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '2147483647',
      background: '#080d1e', width: '100vw', height: '100dvh'
    });

    const frame = document.createElement('iframe');
    frame.src = 'assets/hidden/winter.html';
    frame.title = 'Winter';
    frame.setAttribute('allow', 'fullscreen; autoplay; gamepad');
    frame.setAttribute('allowfullscreen', '');
    Object.assign(frame.style, {
      display: 'block', width: '100%', height: '100%', border: '0', background: '#080d1e'
    });

    const back = document.createElement('button');
    back.type = 'button';
    back.textContent = '← Back to Home';
    back.setAttribute('aria-label', 'Close Winter and return to homepage');
    Object.assign(back.style, {
      position: 'absolute', top: 'max(16px, env(safe-area-inset-top))',
      left: 'max(16px, env(safe-area-inset-left))', zIndex: '2',
      padding: '12px 18px', border: '1px solid rgba(255,255,255,.24)',
      borderRadius: '12px', color: '#fff', font: '700 15px system-ui, sans-serif',
      background: 'linear-gradient(110deg, #29a8e8, #7e5fe5)',
      boxShadow: '0 6px 24px rgba(0,0,0,.45)', cursor: 'pointer',
      touchAction: 'manipulation'
    });
    back.addEventListener('click', closeWinter);
    overlay.append(frame, back);
    document.body.appendChild(overlay);
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    back.focus({ preventScroll: true });
  }

  logo.addEventListener('click', () => {
    const now = performance.now();
    taps = (now - lastTap <= 650) ? taps + 1 : 1;
    lastTap = now;
    if (taps >= 3) { taps = 0; openWinter(); }
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay) closeWinter();
  });
})();
