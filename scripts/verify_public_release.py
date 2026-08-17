from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".css",
    ".cff",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", "dist", "build"}
ALLOWED_SPECIAL_NAMES = {
    ".dockerignore",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    "Dockerfile",
    "LICENSE",
    "PKG-INFO",
}
FORBIDDEN_SUFFIXES = {
    ".7z",
    ".db",
    ".gz",
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".sqlite",
    ".tar",
    ".zip",
}


def _joined(*parts: str) -> str:
    return "".join(parts)


def _patterns() -> dict[str, re.Pattern[str]]:
    api_query = "api" + "Key" + r"=[A-Za-z0-9_-]{12,}"
    private_key = "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    source_project = _joined("odd", "sora")
    source_host = _joined("dev", "790")
    source_path = _joined("/", "srv", "/", "projects", "/")
    source_target = _joined("KB", "KF")
    source_station = _joined("KCO", "AUROR") + r"\d+"
    source_zone = _joined("America/", "Den", "ver")
    source_places = [
        _joined("Buck", "ley"),
        _joined("Den", "ver"),
        _joined("Au", "rora"),
    ]
    legacy_context = [
        _joined("poly", "mar", "ket"),
        _joined("mar", "ket"),
        _joined("trad", "e"),
        _joined("trad", "ing"),
        _joined("wal", "let"),
        _joined("order", "book"),
        _joined("C", "LOB"),
        _joined("sett", "led"),
        _joined("settle", "ment"),
        _joined("mili", "tary"),
        _joined("avia", "tion"),
        _joined("air", "port"),
        _joined("fl", "ight"),
        _joined("finan", "cial"),
        _joined("civ", "ilian"),
        _joined("facil", "ity"),
    ]
    return {
        "cjk_character": re.compile(r"[\u3400-\u9fff]"),
        "hardcoded_api_query": re.compile(api_query),
        "private_key": re.compile(private_key),
        "cloud_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
        "github_token": re.compile(r"\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}\b"),
        "generic_secret_token": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
        "hex_account_address": re.compile(r"\b0x[a-fA-F0-9]{40}\b"),
        "non_example_email": re.compile(
            r"\b[A-Z0-9._%+-]+@(?!(?:example\.com)\b)[A-Z0-9.-]+\.[A-Z]{2,}\b",
            re.IGNORECASE,
        ),
        "absolute_private_path": re.compile(r"(?:\b[A-Z]:[\\/]|/(?:srv|home|Users)/)"),
        "source_project_or_host": re.compile(
            rf"(?i)(?:{re.escape(source_project)}|{re.escape(source_host)}|{re.escape(source_path)})"
        ),
        "source_target_identifier": re.compile(rf"(?i)\b{re.escape(source_target)}\b"),
        "source_station_identifier": re.compile(rf"(?i)\b{source_station}\b"),
        "source_location_name": re.compile(
            rf"(?i)\b(?:{'|'.join(re.escape(value) for value in source_places)})\b"
        ),
        "source_timezone": re.compile(re.escape(source_zone), re.IGNORECASE),
        "source_latitude_band": re.compile(r"\b" + "39" + r"\.7\d+\b"),
        "source_longitude_band": re.compile("-" + "104" + r"\.\d+\b"),
        "legacy_application_context": re.compile(
            rf"(?i)\b(?:{'|'.join(re.escape(value) for value in legacy_context)})\b"
        ),
    }


def main() -> int:
    failures: list[str] = []
    scanned = 0
    patterns = _patterns()
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.is_symlink():
            failures.append(f"forbidden_symlink:{relative}")
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            failures.append(f"forbidden_file:{relative}")
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden_file:{relative}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in ALLOWED_SPECIAL_NAMES:
            failures.append(f"unreviewed_file_type:{relative}")
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"non_utf8_text:{relative}")
            continue
        for name, pattern in patterns.items():
            if pattern.search(text):
                failures.append(f"{name}:{relative}")

    if failures:
        print("Public-release verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Public-release verification passed for {scanned} text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
