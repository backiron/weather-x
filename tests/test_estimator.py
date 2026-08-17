from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from weatherx.estimator import estimate_temperature
from weatherx.models import (
    EstimatorConfig,
    NetworkConfig,
    Observation,
    StationConfig,
    TargetConfig,
    WindContext,
    load_network_config,
    load_observations,
)

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_example_produces_explainable_estimate() -> None:
    estimate = estimate_temperature(
        load_network_config(ROOT / "examples" / "network.example.json"),
        load_observations(ROOT / "examples" / "observations.example.json"),
        as_of=datetime(2025, 7, 15, 18, 0, tzinfo=UTC),
    )

    assert estimate["status"] == "READY_EXPERIMENTAL"
    assert estimate["estimate"]["usable_station_count"] == 5
    assert 87.0 < estimate["estimate"]["temperature_f"] < 90.0
    assert estimate["estimate"]["effective_sample_size"] < 5.0
    assert sum(row["weight"] for row in estimate["station_contributions"]) == pytest.approx(1.0)
    assert not estimate["authority"]["official_observation"]


def _network(*stations: StationConfig) -> NetworkConfig:
    return NetworkConfig(
        target=TargetConfig("target", 0.0, 0.0, 1000.0),
        stations=tuple(stations),
        estimator=EstimatorConfig(minimum_stations=1),
        wind=WindContext(),
    )


def test_future_and_not_yet_received_observations_are_excluded() -> None:
    now = datetime(2026, 8, 13, 18, 0, tzinfo=UTC)
    station = StationConfig("A", 0.01, 0.0, 1000.0)
    observations = [
        Observation("A", 80.0, now + timedelta(minutes=1), now + timedelta(minutes=1)),
        Observation("A", 79.0, now - timedelta(minutes=1), now + timedelta(seconds=1)),
    ]

    estimate = estimate_temperature(_network(station), observations, as_of=now)

    assert estimate["status"] == "NO_USABLE_STATIONS"
    assert {row["reason"] for row in estimate["exclusions"]} == {
        "future_observation",
        "not_received_by_as_of",
    }


def test_correlated_group_reduces_duplicate_sensor_influence() -> None:
    now = datetime(2026, 8, 13, 18, 0, tzinfo=UTC)
    station_a = StationConfig("A", 0.01, 0.0, 1000.0, correlation_group="shared")
    station_b = StationConfig("B", 0.01, 0.0, 1000.0, correlation_group="shared")
    station_c = StationConfig("C", -0.01, 0.0, 1000.0, correlation_group="independent")
    observations = [
        Observation("A", 90.0, now - timedelta(minutes=1)),
        Observation("B", 90.0, now - timedelta(minutes=1)),
        Observation("C", 80.0, now - timedelta(minutes=1)),
    ]
    correlated = estimate_temperature(
        _network(station_a, station_b, station_c),
        observations,
        as_of=now,
    )
    independent = estimate_temperature(
        _network(
            station_a,
            StationConfig("B", 0.01, 0.0, 1000.0, correlation_group="other"),
            station_c,
        ),
        observations,
        as_of=now,
    )

    assert correlated["estimate"]["temperature_f"] < independent["estimate"]["temperature_f"]
