from __future__ import annotations

from scripts import verify_public_release


def test_sensitive_source_fingerprints_are_detected_without_literal_leaks() -> None:
    patterns = verify_public_release._patterns()

    assert patterns["source_target_identifier"].search("".join(["KB", "KF"]))
    assert patterns["source_station_identifier"].search("".join(["KCO", "AUROR", "945"]))
    assert patterns["source_timezone"].search("".join(["America/", "Den", "ver"]))
    assert patterns["legacy_application_context"].search("".join(["trad", "ing"]))


def test_verifier_rejects_sensitive_text_in_any_scanned_file(tmp_path, monkeypatch) -> None:
    marker = "".join(["KB", "KF"])
    (tmp_path / "README.md").write_text(f"target={marker}\n", encoding="utf-8")
    monkeypatch.setattr(verify_public_release, "ROOT", tmp_path)

    assert verify_public_release.main() == 1


def test_verifier_accepts_a_minimal_safe_tree(tmp_path, monkeypatch) -> None:
    (tmp_path / "README.md").write_text("Weather X synthetic example\n", encoding="utf-8")
    monkeypatch.setattr(verify_public_release, "ROOT", tmp_path)

    assert verify_public_release.main() == 0
