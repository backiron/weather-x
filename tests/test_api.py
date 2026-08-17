from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from weatherx.api import create_app

ROOT = Path(__file__).resolve().parents[1]


def test_api_serves_health_estimate_and_dashboard(monkeypatch) -> None:
    monkeypatch.setenv("WEATHERX_CONFIG", str(ROOT / "examples" / "network.example.json"))
    monkeypatch.setenv(
        "WEATHERX_OBSERVATIONS",
        str(ROOT / "examples" / "observations.example.json"),
    )
    monkeypatch.setenv("WEATHERX_AS_OF", "2025-07-15T18:00:00Z")
    monkeypatch.setenv("WEATHERX_WEB_DIR", str(ROOT / "web"))
    client = TestClient(create_app())

    health = client.get("/api/health")
    estimate = client.get("/api/estimate")
    dashboard = client.get("/")

    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": "weather-x"}
    assert estimate.status_code == 200
    assert estimate.json()["status"] == "READY_EXPERIMENTAL"
    assert estimate.json()["estimate"]["usable_station_count"] == 5
    assert dashboard.status_code == 200
    assert "Weather X" in dashboard.text
