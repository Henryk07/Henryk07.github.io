"""Checks on the built site (_site): links, images, leftovers from templating, metadata."""
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest

PAGES = ["index.html", "professional/index.html"]


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.imgs, self.ids, self.jsonld, self._in_jsonld = [], [], set(), [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append((tag, a[key]))
        if tag == "img":
            self.imgs.append(a)
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False

    def handle_data(self, d):
        if self._in_jsonld and d.strip():
            self.jsonld.append(d)


def parse(site, page):
    c = Collector()
    c.feed((site / page).read_text())
    return c


@pytest.mark.parametrize("page", PAGES)
def test_page_exists_without_template_leftovers(site, page):
    html = (site / page).read_text()
    assert "{{" not in html and "{%" not in html, f"unrendered Liquid in {page}"
    assert re.search(r"<title>[^<]+</title>", html)


@pytest.mark.parametrize("page", PAGES)
def test_local_links_and_images_resolve(site, page):
    for tag, ref in parse(site, page).refs:
        parts = urlsplit(ref)
        if parts.scheme or ref.startswith(("#", "mailto:", "//")):
            continue
        path = parts.path
        target = site / path.lstrip("/") if path.startswith("/") else (site / page).parent / path
        if path.endswith("/") or target.is_dir():
            target = target / "index.html"
        assert target.exists(), f"{page}: <{tag}> points to missing {ref}"


@pytest.mark.parametrize("page", PAGES)
def test_images_have_alt(site, page):
    for img in parse(site, page).imgs:
        assert "alt" in img, f"{page}: image {img.get('src')} has no alt attribute"


@pytest.mark.parametrize("page", PAGES)
def test_external_links_use_https(site, page):
    for _, ref in parse(site, page).refs:
        assert not ref.startswith("http://"), f"{page}: insecure link {ref}"


def test_homepage_switch_controls_existing_panels(site):
    c = parse(site, "index.html")
    html = (site / "index.html").read_text()
    for panel in re.findall(r'aria-controls="([^"]+)"', html):
        assert panel in c.ids, f"switch controls #{panel}, which doesn't exist"
    # The mode hashes must not match an element id, or the browser scrolls past the hero
    assert "academic" not in c.ids and "life" not in c.ids


def test_homepage_json_ld_is_valid(site):
    blocks = parse(site, "index.html").jsonld
    assert blocks, "no JSON-LD on the homepage"
    for b in blocks:
        person = json.loads(b)
        assert person["@type"] == "Person" and person["name"]


def test_professional_page_metadata(site):
    html = (site / "professional/index.html").read_text()
    assert re.search(r'<link rel="canonical" href="https://cv\.henrykchan\.com/professional/">', html)
    assert 'data-mode="pro"' in html
    assert 'href="/professional/"' in (site / "index.html").read_text(), "homepage doesn't link to /professional/"


def test_custom_domain_is_published(site):
    assert (site / "CNAME").read_text().strip() == "cv.henrykchan.com"
