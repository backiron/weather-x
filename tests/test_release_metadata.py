from __future__ import annotations

import re
import tomllib
from pathlib import Path

from weatherx import __version__
from weatherx.api import create_app

ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = "1.0.0"


def test_stable_release_metadata_is_consistent() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert project["version"] == STABLE_VERSION
    assert __version__ == STABLE_VERSION
    assert create_app().version == STABLE_VERSION
    assert "Development Status :: 5 - Production/Stable" in project["classifiers"]
    assert re.search(rf"^version: {re.escape(STABLE_VERSION)}$", citation, re.MULTILINE)
    assert f"## [{STABLE_VERSION}]" in changelog
