from __future__ import annotations

import heapq
import math
import random
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, median


@dataclass(frozen=True)
class ScoredPrediction:
    target_time: datetime
    group: str
    predicted_f: float
    truth_f: float


class DelayedResidualCalibrator:
    """Causal residual calibration with labels that become visible later.

    A target residual is queued at prediction time and cannot affect the state
    until its explicit reveal time has passed.
    """

    def __init__(self, *, maximum_history: int = 168) -> None:
        self.maximum_history = max(1, int(maximum_history))
        self._pending: list[tuple[datetime, float]] = []
        self._revealed: deque[float] = deque(maxlen=self.maximum_history)

    def release(self, prediction_time: datetime) -> None:
        while self._pending and self._pending[0][0] <= prediction_time:
            _, residual = heapq.heappop(self._pending)
            self._revealed.append(residual)

    def correction(self, prediction_time: datetime) -> float:
        self.release(prediction_time)
        return mean(self._revealed) if self._revealed else 0.0

    def predict(self, base_prediction_f: float, prediction_time: datetime) -> float:
        return float(base_prediction_f) + self.correction(prediction_time)

    def queue_truth(
        self,
        *,
        base_prediction_f: float,
        truth_f: float,
        target_time: datetime,
        reveal_delay: timedelta,
    ) -> None:
        reveal_at = target_time + reveal_delay
        heapq.heappush(self._pending, (reveal_at, float(truth_f) - float(base_prediction_f)))

    @property
    def revealed_count(self) -> int:
        return len(self._revealed)

    @property
    def pending_count(self) -> int:
        return len(self._pending)


def threshold_bin(value: float, width_f: float = 2.0) -> int:
    return math.floor(float(value) / float(width_f))


def score_predictions(
    rows: Iterable[ScoredPrediction],
    *,
    threshold_width_f: float = 2.0,
) -> dict[str, float | int]:
    values = list(rows)
    if not values:
        return {"n": 0, "group_count": 0}
    errors = [row.predicted_f - row.truth_f for row in values]
    absolute = [abs(value) for value in errors]
    sorted_absolute = sorted(absolute)
    p95_index = min(len(sorted_absolute) - 1, math.ceil(0.95 * len(sorted_absolute)) - 1)
    exact = [
        threshold_bin(row.predicted_f, threshold_width_f)
        == threshold_bin(row.truth_f, threshold_width_f)
        for row in values
    ]
    return {
        "n": len(values),
        "group_count": len({row.group for row in values}),
        "mae_f": mean(absolute),
        "median_absolute_error_f": median(absolute),
        "bias_f": mean(errors),
        "p95_absolute_error_f": sorted_absolute[p95_index],
        "threshold_accuracy": sum(exact) / len(exact),
        "cross_threshold_rate": 1.0 - sum(exact) / len(exact),
    }


def grouped_bootstrap_mae_interval(
    rows: Iterable[ScoredPrediction],
    *,
    iterations: int = 2000,
    seed: int = 20260813,
) -> tuple[float, float]:
    values = list(rows)
    groups: dict[str, list[ScoredPrediction]] = {}
    for row in values:
        groups.setdefault(row.group, []).append(row)
    keys = sorted(groups)
    if not keys:
        return (math.nan, math.nan)
    generator = random.Random(seed)
    scores = []
    for _ in range(max(100, int(iterations))):
        sample = [groups[generator.choice(keys)] for _ in keys]
        errors = [abs(row.predicted_f - row.truth_f) for group in sample for row in group]
        scores.append(mean(errors))
    scores.sort()
    lower = scores[int(0.025 * (len(scores) - 1))]
    upper = scores[int(0.975 * (len(scores) - 1))]
    return (lower, upper)
