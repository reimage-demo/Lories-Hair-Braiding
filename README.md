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

TikTok videos load after a click. The photo-post cover opens the original photo post directly on TikTok, since the video player does not support it.

## Search visibility and domain changes

`seo-config.json` holds the public URL and confirmed business information. The current verified host is `https://reimage-demo.github.io/Lories-Hair-Braiding/`; a final custom domain has not been selected. Hartford is the physical location. West Hartford is an area served, not a second location.

After changing the domain, business facts, visible services or prices, run:

```sh
python3 scripts/update_seo.py
python3 scripts/check_seo.py
```

The generator updates canonical URLs, Open Graph and Twitter card metadata, the HairSalon/WebSite/WebPage/service-catalog JSON-LD, the sitemap and crawler rules. Offers are derived from the visible price list. Prices with a `+` have a minimum but no artificial maximum in schema. Sunday appointment-only availability is explained in text; no fixed Sunday opening window is invented. The visible hours were confirmed by the user on October 12, 2026; keep the visible hours and configuration synchronized when they change.

The 404 page is noindex and uses an absolute base URL so assets and home links work from missing nested paths. Its actual HTTP 404 response is supplied by GitHub Pages. The three compressed WebP logo/hero images retain their original PNG source files. Artwork is decorative; only actual salon-work images are used as business images in schema.

### Publishing and indexing

1. Publish the approved files to the GitHub Pages `main` branch. Local changes are not live until published. If a custom domain is chosen first, update `base_url`, regenerate metadata, and configure its DNS/Pages settings before publication. Preserve or redirect any older salon domain to avoid competing website identities.
2. Verify the final site in Google Search Console and Bing Webmaster Tools using the account owner's provided verification method. Submit `sitemap.xml` and inspect the canonical homepage. No verification tokens have been invented or added.
3. Check the live homepage in Google's Rich Results Test and URL Inspection, and check performance with PageSpeed Insights. The local check script verifies source consistency, not Google's acceptance, indexing or rankings.
4. Verify the Google Business Profile and use the same salon name, address, phone, hours and final website URL. Review its real service categories, list the offered services, upload genuine salon work, and request honest reviews from actual clients. Do not add a West Hartford address or claim a ranking, rating, award or certification without evidence.
5. Correct older website/directory listings that conflict with the confirmed hours and chosen domain. The existing `loriesafricanhairbraiding.com` homepage and Nextdoor listing currently show different hours; confirm control of older domains before arranging redirects. No external listings have been changed.
6. Track Search Console impressions, clicks and queries for Hartford/West Hartford and the individual services, plus calls and directions through the business profile. Keep prices, hours and original work photos current.

### Hosting and AI search notes

`robots.txt` is only authoritative at the origin root. On the current project host, `/Lories-Hair-Braiding/robots.txt` does not control crawling; the checked origin `/robots.txt` returned 404 (no rules). Submit the sitemap directly while using this subpath. The included robots file becomes effective when this repository is served at the root of its custom domain. Check any origin/CDN rules after migration.

GitHub Pages currently supplies HTTPS/HSTS, HTML content types and caching. Arbitrary HTTP response headers and server redirects cannot be configured with this site's HTML, so no ineffective `_headers` or `.htaccess` file has been added. On a future host, configure permanent old-domain redirects and appropriate caching there. HTML robots directives control indexability; `meta http-equiv` is not a substitute for real server response headers.

Important business facts, service descriptions, prices and FAQs are present in static HTML and available without JavaScript. No hidden keyword blocks, fabricated reviews, duplicate city pages or unsupported "AI ranking" files are used. Google's AI features follow the same search foundations and require no special AI schema. Rankings also depend on relevance, distance and prominence outside this website.

Reference guidance:
- https://developers.google.com/search/docs/appearance/ai-features
- https://developers.google.com/search/docs/appearance/structured-data/local-business
- https://support.google.com/business/answer/7091
- https://developers.google.com/search/docs/crawling-indexing/robots/intro


## Mobile layout and release checks

The phone hero stacks large equipment artwork above and below compact copy and paired booking/services buttons. The phone layout uses touch targets of at least 44px for primary controls, stacked contact details and social cards, readable service pricing, and safe-area spacing around the fixed call bar. Small responsive hero assets are selected with `srcset`/`sizes`; salon video covers also use compressed WebP files. Original source images remain available for future edits. The menu closes after navigation, Escape, outside clicks and breakpoint changes.

Before release, run `python3 scripts/check_seo.py`, `node --check site.js`, and `git diff --check`. Check 320, 375, 390, 430, 700, 701, 768, 1024 and 1470px viewport widths for overflow and overlapping prices. Verify the menu, FAQ toggles, call/directions links and photo-post link. Confirm the GitHub Pages build uses the pushed commit, then verify the live homepage, assets, sitemap and custom 404. Browser viewport checks do not replace testing on physical iOS/Android devices.
