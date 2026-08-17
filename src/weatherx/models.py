from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def parse_utc(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


@dataclass(frozen=True)
class TargetConfig:
    target_id: str
    latitude: float
    longitude: float
    elevation_ft: float
    timezone: str = "UTC"
    description: str = "Local reference point"


@dataclass(frozen=True)
class StationConfig:
    station_id: str
    latitude: float
    longitude: float
    elevation_ft: float
    reliability: float = 0.8
    bias_f: float = 0.0
    residual_sigma_f: float = 1.5
    correlation_group: str = "independent"
    note: str = ""


@dataclass(frozen=True)
class WindContext:
    direction_from_deg: float | None = None
    speed_mph: float | None = None
    source: str = "none"


@dataclass(frozen=True)
class EstimatorConfig:
    lapse_rate_f_per_1000ft: float = 3.57
    distance_scale_miles: float = 2.0
    maximum_age_seconds: int = 900
    base_sigma_f: float = 1.2
    minimum_stations: int = 3
    correlation_group_penalty_power: float = 0.5
    sector_penalty_power: float = 0.35
    sector_count: int = 8
    threshold_bin_width_f: float = 2.0


@dataclass(frozen=True)
class NetworkConfig:
    target: TargetConfig
    stations: tuple[StationConfig, ...]
    estimator: EstimatorConfig = field(default_factory=EstimatorConfig)
    wind: WindContext = field(default_factory=WindContext)


@dataclass(frozen=True)
class Observation:
    station_id: str
    temperature_f: float
    observed_at: datetime
    received_at: datetime | None = None
    solar_radiation_wm2: float | None = None
    wind_speed_mph: float | None = None
    quality_control_passed: bool = True
    source_revision: str | None = None


def _target(value: dict[str, Any]) -> TargetConfig:
    return TargetConfig(
        target_id=str(value["target_id"]),
        latitude=float(value["latitude"]),
        longitude=float(value["longitude"]),
        elevation_ft=float(value["elevation_ft"]),
        timezone=str(value.get("timezone") or "UTC"),
        description=str(value.get("description") or "Local reference point"),
    )


def _station(value: dict[str, Any]) -> StationConfig:
    return StationConfig(
        station_id=str(value["station_id"]),
        latitude=float(value["latitude"]),
        longitude=float(value["longitude"]),
        elevation_ft=float(value["elevation_ft"]),
        reliability=float(value.get("reliability", 0.8)),
        bias_f=float(value.get("bias_f", 0.0)),
        residual_sigma_f=float(value.get("residual_sigma_f", 1.5)),
        correlation_group=str(value.get("correlation_group") or "independent"),
        note=str(value.get("note") or ""),
    )


def load_network_config(path: str | Path) -> NetworkConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    estimator_payload = payload.get("estimator") or {}
    wind_payload = payload.get("wind") or {}
    return NetworkConfig(
        target=_target(payload["target"]),
        stations=tuple(_station(row) for row in payload.get("stations") or []),
        estimator=EstimatorConfig(
            lapse_rate_f_per_1000ft=float(estimator_payload.get("lapse_rate_f_per_1000ft", 3.57)),
            distance_scale_miles=float(estimator_payload.get("distance_scale_miles", 2.0)),
            maximum_age_seconds=int(estimator_payload.get("maximum_age_seconds", 900)),
            base_sigma_f=float(estimator_payload.get("base_sigma_f", 1.2)),
            minimum_stations=int(estimator_payload.get("minimum_stations", 3)),
            correlation_group_penalty_power=float(
                estimator_payload.get("correlation_group_penalty_power", 0.5)
            ),
            sector_penalty_power=float(estimator_payload.get("sector_penalty_power", 0.35)),
            sector_count=int(estimator_payload.get("sector_count", 8)),
            threshold_bin_width_f=float(estimator_payload.get("threshold_bin_width_f", 2.0)),
        ),
        wind=WindContext(
            direction_from_deg=(
                float(wind_payload["direction_from_deg"])
                if wind_payload.get("direction_from_deg") is not None
                else None
            ),
            speed_mph=(
                float(wind_payload["speed_mph"])
                if wind_payload.get("speed_mph") is not None
                else None
            ),
            source=str(wind_payload.get("source") or "configuration"),
        ),
    )


def load_observations(path: str | Path) -> list[Observation]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("observations") if isinstance(payload, dict) else payload
    observations = []
    for row in rows or []:
        observed_at = parse_utc(row.get("observed_at"))
        if observed_at is None:
            raise ValueError(f"Observation {row.get('station_id')} has no valid observed_at")
        observations.append(
            Observation(
                station_id=str(row["station_id"]),
                temperature_f=float(row["temperature_f"]),
                observed_at=observed_at,
                received_at=parse_utc(row.get("received_at")),
                solar_radiation_wm2=(
                    float(row["solar_radiation_wm2"])
                    if row.get("solar_radiation_wm2") is not None
                    else None
                ),
                wind_speed_mph=(
                    float(row["wind_speed_mph"]) if row.get("wind_speed_mph") is not None else None
                ),
                quality_control_passed=bool(row.get("quality_control_passed", True)),
                source_revision=(
                    str(row["source_revision"]) if row.get("source_revision") is not None else None
                ),
            )
        )
    return observations
