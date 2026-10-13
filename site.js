const toggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu() { navigation?.classList.remove('open'); toggle?.setAttribute('aria-expanded', 'false'); if(toggle) toggle.textContent = 'Menu'; }
toggle?.addEventListener('click', () => { const open = navigation.classList.toggle('open'); toggle.setAttribute('aria-expanded', String(open)); toggle.textContent = open ? 'Close' : 'Menu'; });
navigation?.addEventListener('click', event => { if(event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => { if(event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); } });
window.matchMedia('(max-width: 700px)').addEventListener('change', closeMenu);
document.addEventListener('click', event => { if (!event.target.closest('.header')) closeMenu(); });
document.querySelectorAll('[data-post]').forEach(button => {
  button.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.title = `${button.dataset.title} — Lorie’s on TikTok`;
    frame.src = `https://www.tiktok.com/player/v1/${button.dataset.post}?autoplay=0&rel=0&description=0&music_info=0`;
    frame.allow = 'fullscreen; picture-in-picture';
    frame.tabIndex = 0;
    frame.allowFullscreen = true;
    button.parentElement.append(frame);
    frame.focus();
    button.remove();
  }, { once: true });
});
window.addEventListener('message', event => {
  if (event.origin !== 'https://www.tiktok.com' || !event.data || event.data['x-tiktok-player'] !== true || event.data.type !== 'onPlayerError') return;
  document.querySelectorAll('.video-shell iframe').forEach(frame => {
    if (frame.contentWindow !== event.source) return;
    const notice = document.createElement('p');
    notice.className = 'embed-error';
    notice.textContent = 'This post couldn’t load here. Use “Open on TikTok” below to view it.';
    frame.replaceWith(notice);
  });
});
