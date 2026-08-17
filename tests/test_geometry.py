from __future__ import annotations

import pytest

from weatherx.geometry import (
    angular_distance_degrees,
    bearing_degrees,
    directional_sector,
    haversine_miles,
)


def test_geometry_helpers_are_stable() -> None:
    assert haversine_miles(0.0, 0.0, 0.01, 0.0) == pytest.approx(0.691, abs=0.01)
    assert bearing_degrees(0.0, 0.0, 0.01, 0.0) == pytest.approx(0.0, abs=0.1)
    assert angular_distance_degrees(350.0, 10.0) == 20.0
    assert directional_sector(359.0, 8) == 0
    assert directional_sector(90.0, 8) == 2
