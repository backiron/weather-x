from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release-manifest.json"
EXCLUDED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", "dist", "build"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = payload.get("files")
    if payload.get("schema") != "WEATHER_X_RELEASE_MANIFEST_V1" or not isinstance(expected, dict):
        print("Release manifest has an invalid schema.")
        return 1

    actual: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        actual[path.relative_to(ROOT).as_posix()] = _sha256(path)

    failures: list[str] = []
    for missing in sorted(set(expected) - set(actual)):
        failures.append(f"missing:{missing}")
    for unexpected in sorted(set(actual) - set(expected)):
        failures.append(f"unexpected:{unexpected}")
    for relative in sorted(set(expected) & set(actual)):
        if expected[relative] != actual[relative]:
            failures.append(f"hash_mismatch:{relative}")

    if payload.get("file_count") != len(expected):
        failures.append("file_count_field_mismatch")

    if failures:
        print("Release-manifest verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Release manifest verified for {len(actual)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
