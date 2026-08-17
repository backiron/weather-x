from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release-manifest.json"
EXCLUDED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", "dist", "build"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    files = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        files[path.relative_to(ROOT).as_posix()] = _sha256(path)
    payload = {
        "schema": "WEATHER_X_RELEASE_MANIFEST_V1",
        "file_count": len(files),
        "files": files,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(files)} file hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
