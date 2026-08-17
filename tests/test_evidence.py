from __future__ import annotations

import json

from weatherx.evidence import canonical_sha256, write_estimate_evidence


def test_evidence_is_canonical_and_deduplicates_identical_tail(tmp_path) -> None:
    first = {"target": {"target_id": "demo"}, "estimate": {"temperature_f": 80.0}}
    second = {"estimate": {"temperature_f": 80.0}, "target": {"target_id": "demo"}}

    first_write = write_estimate_evidence(first, output_dir=tmp_path)
    second_write = write_estimate_evidence(second, output_dir=tmp_path)

    assert canonical_sha256(first) == canonical_sha256(second)
    assert first_write["ledger_appended"] is True
    assert second_write["ledger_appended"] is False
    rows = (tmp_path / "demo" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    assert json.loads(rows[0])["estimate_sha256"] == first_write["estimate_sha256"]
