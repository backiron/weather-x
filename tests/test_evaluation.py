from __future__ import annotations

from datetime import UTC, datetime, timedelta

from weatherx.evaluation import (
    DelayedResidualCalibrator,
    ScoredPrediction,
    grouped_bootstrap_mae_interval,
    score_predictions,
)


def test_delayed_truth_cannot_update_state_before_reveal_time() -> None:
    calibrator = DelayedResidualCalibrator(maximum_history=5)
    target_time = datetime(2026, 8, 13, 15, 0, tzinfo=UTC)
    calibrator.queue_truth(
        base_prediction_f=80.0,
        truth_f=82.0,
        target_time=target_time,
        reveal_delay=timedelta(minutes=70),
    )

    assert calibrator.predict(81.0, target_time + timedelta(minutes=69)) == 81.0
    assert calibrator.revealed_count == 0
    assert calibrator.predict(81.0, target_time + timedelta(minutes=70)) == 83.0
    assert calibrator.revealed_count == 1


def test_scores_use_independent_groups_and_threshold_failures() -> None:
    rows = [
        ScoredPrediction(datetime(2026, 8, 1, tzinfo=UTC), "2026-08-01", 80.1, 80.4),
        ScoredPrediction(datetime(2026, 8, 1, 1, tzinfo=UTC), "2026-08-01", 81.9, 82.1),
        ScoredPrediction(datetime(2026, 8, 2, tzinfo=UTC), "2026-08-02", 79.0, 80.0),
    ]

    metrics = score_predictions(rows, threshold_width_f=2.0)
    interval = grouped_bootstrap_mae_interval(rows, iterations=200, seed=7)

    assert metrics["n"] == 3
    assert metrics["group_count"] == 2
    assert metrics["threshold_accuracy"] < 1.0
    assert interval[0] <= metrics["mae_f"] <= interval[1]
