#!/usr/bin/env python3
"""Check SEO metadata, visible facts, links, schema and sitemap without dependencies."""
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "seo-config.json").read_text())
BASE = CONFIG["base_url"].rstrip("/") + "/"


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.ids = []
        self.h1_count = 0
        self.heading_levels = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.heading_levels.append(int(tag[1]))


docs = {p.name: (p.read_text(), Document(p.read_text())) for p in ROOT.glob("*.html")}
for name, (text, doc) in docs.items():
    assert doc.h1_count == 1, (name, "must have one H1")
    assert len(doc.ids) == len(set(doc.ids)), (name, "duplicate IDs")
    assert len(re.findall(r"<title>.+?</title>", text)) == 1, name
    assert all(b <= a + 1 for a, b in zip(doc.heading_levels, doc.heading_levels[1:])), (name, "heading level skipped")
    descriptions = [a for t, a in doc.tags if t == "meta" and a.get("name") == "description"]
    assert len(descriptions) == 1 and descriptions[0]["content"], name
    robots = [a["content"] for t, a in doc.tags if t == "meta" and a.get("name") == "robots"]
    assert len(robots) == 1, name
    canonicals = [a["href"] for t, a in doc.tags if t == "link" and a.get("rel") == "canonical"]
    if name == "404.html":
        assert "noindex" in robots[0] and not canonicals and "application/ld+json" not in text
    else:
        expected = BASE if name == "index.html" else BASE + name
        assert canonicals == [expected], (name, canonicals)
        assert "noindex" not in robots[0], name
        og = {a.get("property"): a.get("content") for t, a in doc.tags if t == "meta" and "property" in a}
        assert og["og:url"] == expected and og["og:image"].startswith(BASE)
    for tag, attrs in doc.tags:
        if tag == "img":
            assert "alt" in attrs and int(attrs["width"]) > 0 and int(attrs["height"]) > 0
        value = attrs.get("src") or (attrs.get("href") if tag in ("a", "link") else None)
        if not value:
            continue
        parsed = urlparse(value)
        if parsed.scheme or parsed.netloc:
            continue
        path = unquote(parsed.path)
        target = name if not path else "index.html" if path in (".", "./") else path.removeprefix("./")
        assert (ROOT / target).is_file(), (name, "missing local file", target)
        if parsed.fragment and target in docs:
            assert parsed.fragment in docs[target][1].ids, (name, "missing anchor", value)

source = docs["index.html"][0]
structured = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1])
nodes = {node["@type"]: node for node in structured["@graph"]}
salon = nodes["HairSalon"]
assert salon["address"]["addressLocality"] == "Hartford"
assert salon["address"] == CONFIG["address"]
assert salon["telephone"] == "+1-860-953-5838"
assert salon["openingHoursSpecification"] == CONFIG["opening_hours"]
assert {city["name"] for city in salon["areaServed"]} == {"Hartford, Connecticut", "West Hartford, Connecticut"}
assert "aggregateRating" not in source and '"review"' not in source
assert "Sunday is by appointment only with an additional $30 charge" in salon["description"]
visible_hours = dict(re.findall(r"<div><dt>(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)</dt><dd>(.*?)</dd></div>", source))
assert len(visible_hours) == 7
assert all(visible_hours[d] == "9 AM–7 PM" for d in ("Monday", "Tuesday", "Wednesday", "Thursday"))
assert all(visible_hours[d] == "8:30 AM–7 PM" for d in ("Friday", "Saturday"))
assert visible_hours["Sunday"] == "By appointment only"
offers = [offer for group in nodes["OfferCatalog"]["itemListElement"] for offer in group["itemListElement"]]
assert len(offers) == 21
by_name = {offer["itemOffered"]["name"]: offer for offer in offers}
assert by_name["Knotless braids"]["priceSpecification"]["minPrice"] == 220
assert "maxPrice" not in by_name["Knotless braids"]["priceSpecification"]
assert by_name["Crochet"]["priceSpecification"]["minPrice"] == 130
assert by_name["Crochet"]["priceSpecification"]["maxPrice"] == 160
assert by_name["Hair wash & blow-dry"]["priceSpecification"]["price"] == 35
for offer in offers:
    assert offer["itemOffered"]["provider"]["@id"] == salon["@id"]
    assert offer["priceSpecification"]["priceCurrency"] == "USD"
    assert offer["url"].split("#")[1] in docs["index.html"][1].ids
    name = offer["itemOffered"]["name"]
    assert name in unescape(re.sub(r"<script.*?</script>", "", source, flags=re.S))

sitemap = ElementTree.parse(ROOT / "sitemap.xml")
urls = [el.text for el in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
assert set(urls) == {BASE, BASE + "privacy.html", BASE + "terms.html"}
assert "Disallow:" not in (ROOT / "robots.txt").read_text()
assert "Sitemap: " + BASE + "sitemap.xml" in (ROOT / "robots.txt").read_text()
print("PASS: metadata, headings, local files/anchors, 21 service offers, hours, location, sitemap and crawler directives.")
