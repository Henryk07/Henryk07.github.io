"""Unit test for google_scholar_crawler/update_snapshot.py using a fake Scholar result."""
import json
import shutil
import subprocess
import sys

import yaml

from conftest import ROOT


def make_copy(tmp_path):
    (tmp_path / "google_scholar_crawler/results").mkdir(parents=True)
    shutil.copytree(ROOT / "_data", tmp_path / "_data")
    shutil.copy(ROOT / "google_scholar_crawler/update_snapshot.py", tmp_path / "google_scholar_crawler/")
    return tmp_path


def test_updates_counts_and_keeps_comments(tmp_path):
    repo = make_copy(tmp_path)
    academic = yaml.safe_load((repo / "_data/academic.yml").read_text())
    tracked = [p for p in academic["publications"] if "scholar_id" in p]
    first, rest = tracked[0], tracked[1:]

    fake = {
        "citedby": 9999,
        "publications": {first["scholar_id"]: {"num_citations": 4242},
                         "someone:else": {"num_citations": 1}},
    }
    (repo / "google_scholar_crawler/results/gs_data.json").write_text(json.dumps(fake))

    before = (repo / "_data/academic.yml").read_text()
    subprocess.run([sys.executable, "-I", str(repo / "google_scholar_crawler/update_snapshot.py")], check=True)
    after_text = (repo / "_data/academic.yml").read_text()
    after = yaml.safe_load(after_text)

    counts = {p["scholar_id"]: p["citations"] for p in after["publications"] if "scholar_id" in p}
    assert counts[first["scholar_id"]] == 4242
    for p in rest:  # papers missing from the Scholar data keep their snapshot
        assert counts[p["scholar_id"]] == p["citations"]

    profile = yaml.safe_load((repo / "_data/profile.yml").read_text())
    assert profile["citations_fallback"] == 9999

    # Only numbers change: same line count, comments still there
    assert len(after_text.splitlines()) == len(before.splitlines())
    assert after_text.count("#") == before.count("#")
