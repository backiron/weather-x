from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any

import requests

from weatherx.models import parse_utc


def _lookup(payload: Any, path: str) -> Any:
    value = payload
    for segment in str(path).split("."):
        if isinstance(value, list):
            value = value[int(segment)]
        elif isinstance(value, dict):
            value = value[segment]
        else:
            raise KeyError(path)
    return value


def _optional(payload: Any, path: str | None) -> Any:
    if not path:
        return None
    try:
        return _lookup(payload, path)
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def _secret_values(mapping: dict[str, str] | None) -> dict[str, str]:
    values = {}
    for output_name, environment_name in (mapping or {}).items():
        value = os.getenv(environment_name)
        if not value:
            raise ValueError(f"Required environment variable is missing: {environment_name}")
        values[str(output_name)] = value
    return values


def _as_boolean(value: Any, *, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "pass", "passed"}:
            return True
        if normalized in {"false", "0", "no", "fail", "failed"}:
            return False
    raise ValueError(f"Unsupported quality-control value: {value!r}")


def fetch_generic_json_observation(
    config: dict[str, Any],
    *,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Normalize one authorized JSON endpoint without persisting credential values."""

    endpoint = str(config["endpoint"])
    station_id = str(config["station_id"])
    fields = config.get("fields") or {}
    headers = {str(key): str(value) for key, value in (config.get("headers") or {}).items()}
    headers.update(_secret_values(config.get("headers_from_env")))
    params = {str(key): str(value) for key, value in (config.get("params") or {}).items()}
    params.update(_secret_values(config.get("params_from_env")))

    request_started_at = datetime.now(UTC)
    response = requests.get(
        endpoint,
        headers=headers,
        params=params,
        timeout=max(5, int(timeout_seconds)),
    )
    received_at = datetime.now(UTC)
    response.raise_for_status()
    raw_payload = response.content
    payload = response.json()
    observed_at = parse_utc(_lookup(payload, fields["observed_at"]))
    if observed_at is None:
        raise ValueError("Provider response has no valid observation time")

    observation = {
        "station_id": station_id,
        "temperature_f": float(_lookup(payload, fields["temperature_f"])),
        "observed_at": observed_at.isoformat(),
        "received_at": received_at.isoformat(),
        "solar_radiation_wm2": _optional(payload, fields.get("solar_radiation_wm2")),
        "wind_speed_mph": _optional(payload, fields.get("wind_speed_mph")),
        "quality_control_passed": _as_boolean(
            _optional(payload, fields.get("quality_control_passed")),
            default=True,
        ),
        "source_revision": hashlib.sha256(raw_payload).hexdigest(),
    }
    return {
        "schema": "WEATHER_X_NORMALIZED_PROVIDER_CAPTURE_V1",
        "provider_name": str(config.get("provider_name") or "generic_json"),
        "endpoint_origin": endpoint.split("?", 1)[0],
        "request_started_at": request_started_at.isoformat(),
        "received_at": received_at.isoformat(),
        "source_payload_sha256": observation["source_revision"],
        "observation": observation,
        "credential_values_persisted": False,
    }


def load_provider_config(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Provider configuration must be a JSON object")
    return payload
