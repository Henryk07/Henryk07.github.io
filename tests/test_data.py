"""Checks on the YAML content in _data/: required fields, formats, files that must exist."""
import re
from datetime import date
from pathlib import Path

import pytest

from conftest import ROOT

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SCHOLAR_ID = re.compile(r"^[A-Za-z0-9_-]{12}:[A-Za-z0-9_-]{12}$")


def asset(path):
    return ROOT / path.lstrip("/")


def test_profile_basics(data):
    p = data["profile"]
    for key in ("name", "alt_name", "location", "avatar", "email", "coffee_url"):
        assert p.get(key), f"profile.{key} is missing"
    assert EMAIL.match(p["email"])
    assert asset(p["avatar"]).is_file()
    assert isinstance(p["citations_fallback"], int) and p["citations_fallback"] > 0
    for side in ("academic", "life"):
        assert p["tagline"][side]
        assert p["links"][side], f"no links for the {side} side"


def test_links_are_https_or_mailto(data):
    links = [l for side in data["profile"]["links"].values() for l in side]
    links += data["professional"]["contact"]
    for l in links:
        assert l["label"] and l["url"]
        assert l["url"].startswith(("https://", "mailto:")), l["url"]


def test_one_contact_email_everywhere(data):
    """Every mailto in the content uses the profile email, and the old Gmail address is gone."""
    email = data["profile"]["email"]
    sources = list((ROOT / "_data").glob("*.yml")) + [ROOT / "index.html", *ROOT.glob("_includes/*.html"),
                                                      ROOT / "professional/index.html"]
    for path in sources:
        text = path.read_text()
        assert "gmail.com" not in text, f"Gmail address found in {path.relative_to(ROOT)}"
        for addr in re.findall(r"mailto:([^\"'\s)}]+)", text):
            if "{{" not in addr:
                assert addr == email, f"{path.relative_to(ROOT)} links to {addr}, expected {email}"


def test_publications(data):
    pubs = data["academic"]["publications"]
    assert pubs, "no publications"
    seen = set()
    for pub in pubs:
        for key in ("title", "authors", "venue", "year", "url"):
            assert pub.get(key), f"{pub.get('title', '?')}: missing {key}"
        assert "Henryk Chan" in pub["authors"], f"{pub['title']}: author list doesn't include Henryk Chan"
        assert 2015 <= pub["year"] <= date.today().year + 1
        assert pub["url"].startswith("https://")
        if "scholar_id" in pub:
            assert SCHOLAR_ID.match(pub["scholar_id"]), pub["scholar_id"]
            assert isinstance(pub.get("citations"), int) and pub["citations"] >= 0
            assert pub["scholar_id"] not in seen, f"duplicate scholar_id {pub['scholar_id']}"
            seen.add(pub["scholar_id"])
        if "image" in pub:
            assert asset(pub["image"]).is_file(), pub["image"]
    years = [p["year"] for p in pubs]
    assert years == sorted(years, reverse=True), "publications should be newest first"


@pytest.mark.parametrize("section", ["research", "education"])
def test_timeline_entries_have_logos(data, section):
    for item in data["academic"][section]:
        assert item["date"] and item["title"] and item["place"]
        assert asset(item["logo"]).is_file(), item["logo"]


def test_dated_lists_have_dates_and_text(data):
    a, l, pro = data["academic"], data["life"], data["professional"]
    for item in a["news"]:
        assert item["date"] and item["text"]
    for item in a["honours"] + l["activities"] + pro["recognition"] + pro["leadership"] + pro["education"]:
        assert item["date"] and item["title"]


def test_projects(data):
    for pr in data["life"]["projects"]:
        assert pr["name"] and pr["summary"] and pr["stack"]
        assert pr.get("links") or pr.get("note"), f"{pr['name']}: needs links or a note"
        for link in pr.get("links", []):
            assert link["url"].startswith("https://")


def test_professional_page_content(data):
    pro = data["professional"]
    assert pro["headline"] and pro["open_to"] and pro["highlights"]
    for x in pro["experience"]:
        for key in ("date", "role", "org", "place"):
            assert x.get(key), f"experience entry missing {key}: {x}"
        assert x["points"], f"{x['role']} at {x['org']} has no bullet points"
    for s in pro["skills"]:
        assert s["group"] and s["items"]
