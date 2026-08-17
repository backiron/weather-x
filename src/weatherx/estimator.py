from __future__ import annotations

import math
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from weatherx.geometry import (
    angular_distance_degrees,
    bearing_degrees,
    directional_sector,
    haversine_miles,
)
from weatherx.models import NetworkConfig, Observation


def _rounded(value: float | None, digits: int = 3) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(value, digits)


def _normal_cdf(value: float, mean: float, sigma: float) -> float:
    safe_sigma = max(float(sigma), 0.01)
    return 0.5 * (1.0 + math.erf((value - mean) / (safe_sigma * math.sqrt(2.0))))


def _threshold_distribution(mean: float, sigma: float, width: float) -> list[dict[str, float]]:
    safe_width = max(float(width), 0.25)
    center = math.floor(mean / safe_width) * safe_width
    rows = []
    for offset in range(-3, 4):
        lower = center + offset * safe_width
        upper = lower + safe_width
        probability = _normal_cdf(upper, mean, sigma) - _normal_cdf(lower, mean, sigma)
        if probability >= 0.002:
            rows.append(
                {
                    "lower_f": round(lower, 2),
                    "upper_f": round(upper, 2),
                    "probability": round(probability, 5),
                }
            )
    return sorted(rows, key=lambda row: row["probability"], reverse=True)


def estimate_temperature(
    network: NetworkConfig,
    observations: list[Observation],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    generated_at = (as_of or datetime.now(UTC)).astimezone(UTC)
    stations = {station.station_id: station for station in network.stations}
    latest: dict[str, Observation] = {}
    exclusions: list[dict[str, str]] = []

    for observation in observations:
        station = stations.get(observation.station_id)
        if station is None:
            exclusions.append(
                {"station_id": observation.station_id, "reason": "station_not_configured"}
            )
            continue
        if not observation.quality_control_passed:
            exclusions.append(
                {"station_id": observation.station_id, "reason": "provider_qc_failed"}
            )
            continue
        if observation.observed_at > generated_at:
            exclusions.append(
                {"station_id": observation.station_id, "reason": "future_observation"}
            )
            continue
        if observation.received_at and observation.received_at > generated_at:
            exclusions.append(
                {"station_id": observation.station_id, "reason": "not_received_by_as_of"}
            )
            continue
        prior = latest.get(observation.station_id)
        if prior is None or observation.observed_at > prior.observed_at:
            latest[observation.station_id] = observation

    provisional: list[dict[str, Any]] = []
    for station_id, observation in latest.items():
        station = stations[station_id]
        age_seconds = max(0.0, (generated_at - observation.observed_at).total_seconds())
        if age_seconds > network.estimator.maximum_age_seconds:
            exclusions.append({"station_id": station_id, "reason": "observation_too_old"})
            continue

        distance = haversine_miles(
            network.target.latitude,
            network.target.longitude,
            station.latitude,
            station.longitude,
        )
        bearing = bearing_degrees(
            network.target.latitude,
            network.target.longitude,
            station.latitude,
            station.longitude,
        )
        sector = directional_sector(bearing, network.estimator.sector_count)
        elevation_adjustment = (
            network.estimator.lapse_rate_f_per_1000ft
            * (station.elevation_ft - network.target.elevation_ft)
            / 1000.0
        )
        corrected_temperature = observation.temperature_f + elevation_adjustment - station.bias_f

        freshness_factor = max(
            0.15,
            1.0 - age_seconds / max(1.0, network.estimator.maximum_age_seconds),
        )
        distance_factor = 1.0 / (1.0 + distance / max(0.1, network.estimator.distance_scale_miles))

        wind_factor = 1.0
        upwind_score = None
        if network.wind.direction_from_deg is not None and (network.wind.speed_mph or 0.0) >= 3.0:
            angle = angular_distance_degrees(network.wind.direction_from_deg, bearing)
            upwind_score = math.cos(math.radians(angle))
            wind_factor = max(0.55, min(1.35, 1.0 + 0.30 * upwind_score))

        radiation_factor = 1.0
        radiation_regime = "unknown"
        if observation.solar_radiation_wm2 is not None:
            if (
                observation.solar_radiation_wm2 >= 750.0
                and (observation.wind_speed_mph or 0.0) < 4.0
            ):
                radiation_factor = 0.88
                radiation_regime = "strong_sun_low_ventilation"
            elif observation.solar_radiation_wm2 >= 750.0:
                radiation_factor = 0.96
                radiation_regime = "strong_sun_ventilated"
            elif observation.solar_radiation_wm2 <= 250.0:
                radiation_factor = 0.94
                radiation_regime = "low_solar_input"
            else:
                radiation_regime = "moderate_solar_input"

        raw_weight = (
            max(0.0, station.reliability)
            * freshness_factor
            * distance_factor
            * wind_factor
            * radiation_factor
            / max(0.5, station.residual_sigma_f)
        )
        provisional.append(
            {
                "station_id": station_id,
                "temperature_f": observation.temperature_f,
                "corrected_temperature_f": corrected_temperature,
                "observed_at": observation.observed_at.isoformat(),
                "received_at": (
                    observation.received_at.isoformat() if observation.received_at else None
                ),
                "age_seconds": age_seconds,
                "distance_miles": distance,
                "bearing_degrees": bearing,
                "sector": sector,
                "correlation_group": station.correlation_group,
                "elevation_adjustment_f": elevation_adjustment,
                "bias_removed_f": station.bias_f,
                "upwind_score": upwind_score,
                "radiation_regime": radiation_regime,
                "raw_weight": raw_weight,
                "weight_components": {
                    "reliability": station.reliability,
                    "freshness": freshness_factor,
                    "distance": distance_factor,
                    "wind": wind_factor,
                    "radiation": radiation_factor,
                    "inverse_residual_sigma": 1.0 / max(0.5, station.residual_sigma_f),
                },
            }
        )

    group_counts = Counter(row["correlation_group"] for row in provisional)
    sector_counts = Counter(row["sector"] for row in provisional)
    total_adjusted_weight = 0.0
    for row in provisional:
        group_penalty = group_counts[row["correlation_group"]] ** (
            -network.estimator.correlation_group_penalty_power
        )
        sector_penalty = sector_counts[row["sector"]] ** (-network.estimator.sector_penalty_power)
        row["correlation_group_penalty"] = group_penalty
        row["sector_penalty"] = sector_penalty
        row["adjusted_weight"] = row["raw_weight"] * group_penalty * sector_penalty
        total_adjusted_weight += row["adjusted_weight"]

    if total_adjusted_weight <= 0.0:
        return {
            "schema": "WEATHER_X_ESTIMATE_V1",
            "status": "NO_USABLE_STATIONS",
            "generated_at": generated_at.isoformat(),
            "target": network.target.target_id,
            "estimate": None,
            "station_contributions": [],
            "exclusions": exclusions,
            "authority": {"official_observation": False, "safety_critical": False},
        }

    for row in provisional:
        row["weight"] = row["adjusted_weight"] / total_adjusted_weight

    mean = sum(row["corrected_temperature_f"] * row["weight"] for row in provisional)
    variance = sum(
        row["weight"] * (row["corrected_temperature_f"] - mean) ** 2 for row in provisional
    )
    spread = math.sqrt(max(0.0, variance))
    effective_sample_size = 1.0 / sum(row["weight"] ** 2 for row in provisional)
    model_floor = network.estimator.base_sigma_f / math.sqrt(max(1.0, effective_sample_size))
    sigma = math.sqrt(spread**2 + model_floor**2)
    status = (
        "READY_EXPERIMENTAL"
        if len(provisional) >= network.estimator.minimum_stations
        else "LOW_STATION_COUNT"
    )

    station_rows = []
    for row in sorted(provisional, key=lambda value: value["weight"], reverse=True):
        station_rows.append(
            {
                key: (_rounded(value) if isinstance(value, float) else value)
                for key, value in row.items()
                if key not in {"raw_weight", "adjusted_weight"}
            }
        )

    return {
        "schema": "WEATHER_X_ESTIMATE_V1",
        "status": status,
        "generated_at": generated_at.isoformat(),
        "target": {
            "target_id": network.target.target_id,
            "description": network.target.description,
            "latitude": network.target.latitude,
            "longitude": network.target.longitude,
            "elevation_ft": network.target.elevation_ft,
        },
        "estimate": {
            "temperature_f": _rounded(mean, 2),
            "sigma_f": _rounded(sigma, 2),
            "interval_95_f": [_rounded(mean - 1.96 * sigma, 2), _rounded(mean + 1.96 * sigma, 2)],
            "network_spread_f": _rounded(spread, 2),
            "effective_sample_size": _rounded(effective_sample_size, 2),
            "configured_station_count": len(network.stations),
            "usable_station_count": len(provisional),
            "threshold_distribution": _threshold_distribution(
                mean, sigma, network.estimator.threshold_bin_width_f
            ),
        },
        "wind_context": {
            "direction_from_deg": network.wind.direction_from_deg,
            "speed_mph": network.wind.speed_mph,
            "source": network.wind.source,
        },
        "method": {
            "center": "weighted_mean_of_bias_and_elevation_adjusted_observations",
            "weight": (
                "reliability * freshness * distance * wind * radiation / residual_sigma "
                "* correlation_group_penalty * sector_penalty"
            ),
            "uncertainty": "weighted_network_spread_plus_effective_sample_model_floor",
        },
        "station_contributions": station_rows,
        "exclusions": exclusions,
        "authority": {
            "official_observation": False,
            "safety_critical_use": False,
            "automated_decision_authority": False,
        },
    }
