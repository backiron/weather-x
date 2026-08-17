from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests


def _celsius_to_fahrenheit(value: float | None) -> float | None:
    return value * 9.0 / 5.0 + 32.0 if value is not None else None


def fetch_nws_latest(
    station_id: str,
    *,
    user_agent: str,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    """Fetch the latest public NWS observation for validation, not estimation authority."""

    if not user_agent or "@" not in user_agent:
        raise ValueError("NWS requests require a descriptive user agent with contact information")
    station = str(station_id).strip().upper()
    url = f"https://api.weather.gov/stations/{station}/observations/latest"
    received_at = datetime.now(UTC)
    response = requests.get(
        url,
        headers={"User-Agent": user_agent, "Accept": "application/geo+json"},
        timeout=max(5, int(timeout_seconds)),
    )
    response.raise_for_status()
    payload = response.json()
    properties = payload.get("properties") if isinstance(payload, dict) else {}
    temperature = properties.get("temperature") if isinstance(properties, dict) else {}
    temperature_c = temperature.get("value") if isinstance(temperature, dict) else None
    return {
        "schema": "WEATHER_X_REFERENCE_OBSERVATION_V1",
        "station_id": station,
        "source": "U.S. National Weather Service API",
        "source_url": url,
        "observed_at": properties.get("timestamp") if isinstance(properties, dict) else None,
        "received_at": received_at.isoformat(),
        "temperature_f": (
            round(_celsius_to_fahrenheit(float(temperature_c)), 2)
            if temperature_c is not None
            else None
        ),
        "raw_text": properties.get("rawMessage") if isinstance(properties, dict) else None,
        "authority": {
            "validation_reference": True,
            "weather_x_input": False,
        },
    }
