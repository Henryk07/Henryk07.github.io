import os
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    return yaml.safe_load((ROOT / "_data" / f"{name}.yml").read_text())


@pytest.fixture(scope="session")
def data():
    return {n: load(n) for n in ("profile", "academic", "life", "professional")}


@pytest.fixture(scope="session")
def site():
    """The built site. CI builds it with GitHub Pages' Jekyll; locally run `bundle exec jekyll build`."""
    path = ROOT / os.environ.get("SITE_DIR", "_site")
    if not (path / "index.html").exists():
        pytest.skip(f"no built site at {path}; run `bundle exec jekyll build` first")
    return path
