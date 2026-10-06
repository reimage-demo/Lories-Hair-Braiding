# Lorie’s African Hair Braiding & Beauty Salon

Plain HTML, CSS, and JavaScript website. All site files are in the project root.

- `index.html` — homepage, services and pricing, TikTok posts, hours and contact information
- `styles.css` — shared responsive styles
- `site.js` — mobile navigation and click-to-load TikTok embeds
- `privacy.html`, `terms.html` — legal pages
- `assets/` — supplied logo and images from the client’s TikTok posts

## Preview locally

Run `python3 -m http.server 4173` from the project root, then open http://localhost:4173.

## Deploy

GitHub Pages publishes the root of the `main` branch. No build step is needed. Relative asset and page links support both GitHub Pages and a custom domain.

Appointments are arranged by phone. Sundays are appointment only with an additional $30 charge. The website does not process deposits or payments.

TikTok videos load after a click. TikTok currently rejects the supplied photo post in its player; a direct link is provided when that happens.
