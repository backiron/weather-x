from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def write_estimate_evidence(
    estimate: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, str | bool]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    target = estimate.get("target") or {}
    target_id = (
        str(target.get("target_id") or "target")
        if isinstance(target, dict)
        else str(target or "target")
    )
    safe_target = "".join(
        character for character in target_id if character.isalnum() or character in "-_"
    )
    safe_target = safe_target or "target"
    target_dir = root / safe_target
    target_dir.mkdir(parents=True, exist_ok=True)

    digest = canonical_sha256(estimate)
    record = {
        "schema": "WEATHER_X_EVIDENCE_V1",
        "estimate_sha256": digest,
        "estimate": estimate,
    }
    latest_path = target_dir / "latest.json"
    ledger_path = target_dir / "ledger.jsonl"
    latest_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    appended = True
    if ledger_path.exists():
        last_line = ""
        with ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last_line = line
        if last_line:
            try:
                prior = json.loads(last_line)
                appended = prior.get("estimate_sha256") != digest
            except json.JSONDecodeError:
                appended = True
    if appended:
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(record) + "\n")

    return {
        "latest_path": str(latest_path),
        "ledger_path": str(ledger_path),
        "estimate_sha256": digest,
        "ledger_appended": appended,
    }
