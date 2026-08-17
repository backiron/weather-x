"""Weather X: auditable local-temperature inference from crowd-sourced sensors."""

from weatherx.estimator import estimate_temperature
from weatherx.models import NetworkConfig, Observation, StationConfig, TargetConfig

__all__ = [
    "NetworkConfig",
    "Observation",
    "StationConfig",
    "TargetConfig",
    "estimate_temperature",
]

__version__ = "0.1.0"
