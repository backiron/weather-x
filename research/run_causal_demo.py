from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from weatherx.evaluation import DelayedResidualCalibrator, ScoredPrediction, score_predictions


def main() -> int:
    calibrator = DelayedResidualCalibrator(maximum_history=3)
    start = datetime(2026, 8, 13, 15, 0, tzinfo=UTC)
    base_predictions = [80.0, 81.0, 82.0, 83.0]
    truths = [81.0, 82.0, 82.0, 84.0]
    rows = []
    trace = []
    for index, (base, truth) in enumerate(zip(base_predictions, truths, strict=True)):
        target_time = start + timedelta(hours=index)
        prediction = calibrator.predict(base, target_time)
        rows.append(
            ScoredPrediction(
                target_time=target_time,
                group=target_time.date().isoformat(),
                predicted_f=prediction,
                truth_f=truth,
            )
        )
        trace.append(
            {
                "target_time": target_time.isoformat(),
                "base_prediction_f": base,
                "causal_prediction_f": prediction,
                "truth_f": truth,
                "revealed_count_before_queue": calibrator.revealed_count,
                "pending_count_before_queue": calibrator.pending_count,
            }
        )
        calibrator.queue_truth(
            base_prediction_f=base,
            truth_f=truth,
            target_time=target_time,
            reveal_delay=timedelta(minutes=70),
        )
    print(json.dumps({"trace": trace, "metrics": score_predictions(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
