from __future__ import annotations

import json

from weatherx.providers.generic_json import fetch_generic_json_observation


class _FakeResponse:
    content = b'{"observation":{"time":"2025-07-15T18:00:00Z","temp_f":88.7,"qc":"false"}}'

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return json.loads(self.content)


def test_generic_json_adapter_normalizes_without_persisting_credentials(
    monkeypatch,
) -> None:
    captured_request = {}

    def fake_get(endpoint, *, headers, params, timeout):
        captured_request.update(
            {
                "endpoint": endpoint,
                "headers": headers,
                "params": params,
                "timeout": timeout,
            }
        )
        return _FakeResponse()

    monkeypatch.setenv("DEMO_WEATHER_TOKEN", "test-only-secret")
    monkeypatch.setattr("weatherx.providers.generic_json.requests.get", fake_get)

    capture = fetch_generic_json_observation(
        {
            "provider_name": "authorized_example",
            "endpoint": "https://example.invalid/current",
            "station_id": "PWS-NORTH",
            "params_from_env": {"access_token": "DEMO_WEATHER_TOKEN"},
            "fields": {
                "observed_at": "observation.time",
                "temperature_f": "observation.temp_f",
                "quality_control_passed": "observation.qc",
            },
        }
    )

    assert captured_request["params"]["access_token"] == "test-only-secret"
    assert capture["observation"]["temperature_f"] == 88.7
    assert capture["observation"]["quality_control_passed"] is False
    assert capture["credential_values_persisted"] is False
    assert "test-only-secret" not in json.dumps(capture)
    assert len(capture["source_payload_sha256"]) == 64
