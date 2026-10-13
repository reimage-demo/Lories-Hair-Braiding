#!/usr/bin/env python3
"""Regenerate metadata, service schema, sitemap and robots from local content.

Edit seo-config.json when the production domain is chosen, then run this script.
Service names and prices are read from index.html to prevent a second price list.
Uses only the Python standard library. Does not publish or contact any service.
"""
import html
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "seo-config.json").read_text())
BASE = CONFIG["base_url"].rstrip("/") + "/"
if urlparse(BASE).scheme != "https" or not urlparse(BASE).netloc:
    raise ValueError("base_url must be an absolute HTTPS address")


def plain(value):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def service_catalog(source):
    catalogs = []
    groups = re.findall(r'<section class="service-group" id="([^"]+)"[^>]*>(.*?)</section>', source, re.S)
    for anchor, body in groups:
        name = plain(re.search(r"<h3[^>]*>(.*?)</h3>", body, re.S)[1])
        offers = []
        for term, price in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", body, re.S):
            service_name = plain(term.split("<small>")[0])
            note = re.search(r"<small>(.*?)</small>", term)
            price_text = plain(price)
            description = f"Listed price: {price_text}. Confirm the final price with the salon before service."
            if note:
                description += " " + plain(note[1]) + "."
            amounts = [float(n.replace(",", "")) for n in re.findall(r"\$([\d,]+(?:\.\d+)?)", price_text)]
            specification = {"@type": "PriceSpecification", "priceCurrency": "USD"}
            if "+" in price_text:
                specification["minPrice"] = amounts[0]
                description += " A plus sign means the price can exceed the displayed amount or range."
            elif len(amounts) > 1:
                specification.update(minPrice=amounts[0], maxPrice=amounts[-1])
            else:
                specification["price"] = amounts[0]
            offers.append({
                "@type": "Offer", "url": BASE + "#" + anchor,
                "description": description, "priceSpecification": specification,
                "itemOffered": {
                    "@type": "Service", "name": service_name,
                    "serviceType": service_name, "provider": {"@id": BASE + "#salon"},
                    "url": BASE + "#" + anchor,
                },
            })
        catalogs.append({"@type": "OfferCatalog", "name": name, "itemListElement": offers})
    if not catalogs or any(not c["itemListElement"] for c in catalogs):
        raise ValueError("Could not read the visible service groups and prices")
    return {"@type": "OfferCatalog", "@id": BASE + "#service-catalog", "name": "Hair braiding services and prices", "itemListElement": catalogs}


def graph(source):
    catalog = service_catalog(source)
    salon = {
        "@type": "HairSalon", "@id": BASE + "#salon", "url": BASE,
        "name": CONFIG["business_name"], "description": CONFIG["description"] + " " + CONFIG["appointment_note"],
        "telephone": CONFIG["phone"], "address": CONFIG["address"],
        "areaServed": [{"@type": "City", "name": city + ", Connecticut"} for city in CONFIG["areas_served"]],
        "openingHoursSpecification": CONFIG["opening_hours"],
        "sameAs": CONFIG["same_as"], "hasOfferCatalog": {"@id": BASE + "#service-catalog"},
        "logo": {"@type": "ImageObject", "url": urljoin(BASE, "assets/lories-logo.png"), "width": 1774, "height": 887},
        "image": [urljoin(BASE, "assets/salon-work.jpg"), urljoin(BASE, "assets/boho-braids.jpg")],
        "hasMap": "https://www.google.com/maps/search/?api=1&query=875+New+Britain+Avenue+Hartford+CT+06106",
    }
    return {"@context": "https://schema.org", "@graph": [
        salon,
        {"@type": "WebSite", "@id": BASE + "#website", "url": BASE, "name": CONFIG["business_name"], "publisher": {"@id": BASE + "#salon"}, "inLanguage": "en-US"},
        {"@type": "WebPage", "@id": BASE + "#webpage", "url": BASE, "name": CONFIG["title"], "description": CONFIG["description"], "isPartOf": {"@id": BASE + "#website"}, "mainEntity": {"@id": BASE + "#salon"}, "inLanguage": "en-US"},
        catalog,
    ]}


def metadata(filename, source):
    home = filename == "index.html"
    missing = filename == "404.html"
    title = CONFIG["title"] if home else plain(re.search(r"<title>(.*?)</title>", source, re.S)[1])
    description = CONFIG["description"] if home else html.unescape(re.search(r'<meta name="description" content="([^"]*)"', source)[1])
    if missing:
        title = "Page Not Found | Lorie’s African Hair Braiding"
        description = "This page could not be found. Visit Lorie’s homepage for hair braiding services, prices and contact information."
    source = re.sub(r"<title>.*?</title>", "<title>" + html.escape(title) + "</title>", source, count=1, flags=re.S)
    source = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + html.escape(description, quote=True) + '">', source, count=1)
    source = re.sub(r'\s*<!-- SEO:START -->.*?<!-- SEO:END -->', '', source, flags=re.S)
    source = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', source, flags=re.S)
    lines = ['<!-- SEO:START -->']

    def meta(key, value, attribute="name"):
        lines.append(f'<meta {attribute}="{key}" content="{html.escape(value, quote=True)}">')

    meta("robots", "noindex, follow" if missing else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
    if not missing:
        canonical = BASE if home else urljoin(BASE, filename)
        lines.append(f'<link rel="canonical" href="{canonical}">')
        for key, value in {"og:type": "website", "og:locale": "en_US", "og:site_name": CONFIG["business_name"], "og:title": title, "og:description": description, "og:url": canonical, "og:image": urljoin(BASE, "assets/lories-logo.png"), "og:image:width": "1774", "og:image:height": "887", "og:image:alt": CONFIG["business_name"] + " logo"}.items():
            meta(key, value, "property")
        for key, value in {"twitter:card": "summary_large_image", "twitter:title": title, "twitter:description": description, "twitter:image": urljoin(BASE, "assets/lories-logo.png"), "twitter:image:alt": CONFIG["business_name"] + " logo"}.items():
            meta(key, value)
        lines.append(f'<link rel="sitemap" type="application/xml" href="{urljoin(BASE, "sitemap.xml")}">')
    if home:
        lines.append('<script type="application/ld+json">\n' + json.dumps(graph(source), indent=2, ensure_ascii=False).replace("</", "<\\/") + '\n</script>')
    lines.append('<!-- SEO:END -->')
    return re.sub(r"\s*</head>", lambda _: "\n" + "\n".join(lines) + "\n</head>", source, count=1)


def main():
    for path in ROOT.glob("*.html"):
        source = metadata(path.name, path.read_text())
        # New HTML must not reuse a browser's cached pre-release CSS or script.
        for asset in ("styles.css", "site.js"):
            version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:12]
            source = re.sub(r'"' + re.escape(asset) + r'(?:\?v=[a-f0-9]+)?"', '"' + asset + '?v=' + version + '"', source)
        # Normalize home links to the canonical directory URL instead of index.html.
        source = source.replace('href="index.html', 'href="./')
        if path.name == "404.html":
            # GitHub Pages serves this document at arbitrary nested missing URLs.
            source = re.sub(r'<base href="[^"]*">\s*', '', source)
            source = source.replace('<head>', '<head>\n  <base href="' + BASE + '">', 1)
        path.write_text(source)
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    register_namespace("", ns)
    root = Element("{" + ns + "}urlset")
    for relative in ("", "privacy.html", "terms.html"):
        node = SubElement(root, "{" + ns + "}url")
        SubElement(node, "{" + ns + "}loc").text = urljoin(BASE, relative)
    ElementTree(root).write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: " + urljoin(BASE, "sitemap.xml") + "\n")
    print("Updated HTML metadata, service schema, sitemap.xml and robots.txt for " + BASE)


if __name__ == "__main__":
    main()
