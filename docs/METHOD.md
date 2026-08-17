# Method

## Estimand

Weather X estimates a spatially filtered near-surface air temperature at a configurable target
point. It does not attempt to reproduce the internal sampling, averaging, or reporting behavior
of a specific official sensor.

This distinction matters. A point observation, an area-average temperature, and the exact value
reported by a reference instrument are different estimands.

## Causal input contract

Every sensor record may contain:

- `observed_at`: when the sensor measured the atmosphere;
- `received_at`: when the system first received that payload;
- `source_revision`: the provider revision or capture identifier.

An estimate generated at time `t` rejects observations with `observed_at > t` or
`received_at > t`. Later provider revisions must not be treated as if they were available during
an earlier prediction.

## Per-station correction

For station `i`, the corrected target-equivalent temperature is:

```text
corrected_i = raw_i + elevation_adjustment_i - historical_bias_i
```

The default elevation adjustment uses a configurable lapse rate. It is a modeling assumption,
not a universal physical constant. Local boundary-layer state, solar exposure, ventilation, and
terrain can reverse or weaken the expected gradient.

## Weighting

The unnormalized station weight is:

```text
reliability
* freshness
* distance
* wind_advection
* radiation
/ residual_sigma
* correlation_group_penalty
* directional_sector_penalty
```

- **Reliability** is a frozen prior or independently estimated out-of-sample score.
- **Freshness** decays with observation age.
- **Distance** uses a smooth inverse-distance factor.
- **Wind advection** increases the influence of an upwind station when wind is meaningful.
- **Radiation** reduces the influence of a high-solar, poorly ventilated station.
- **Residual sigma** discounts historically noisy stations.
- **Correlation groups** prevent multiple nearby sensors from being counted as independent.
- **Directional sectors** reduce repeated information from one side of the target.

The current open implementation uses soft penalties for correlated groups and sectors. It does
not claim that these heuristics are optimal.

## Center and uncertainty

The center is a normalized weighted mean of corrected observations. Uncertainty combines:

1. weighted disagreement among corrected stations; and
2. a model floor discounted by the effective sample size.

Effective sample size is:

```text
N_eff = 1 / sum(normalized_weight_i ^ 2)
```

This exposes the difference between the number of reporting stations and the amount of
independent information.

## Threshold diagnostics

Weather X may publish a probability distribution across configurable temperature bins. These
bins are diagnostic. A useful continuous estimate can still be unreliable near an arbitrary
decision threshold.

## Delayed labels

`DelayedResidualCalibrator` queues a target residual until its explicit reveal time. A queued
label cannot alter the model state before `reveal_at <= prediction_time`. Evaluation should use
independent dates or events as sampling units rather than treating many same-day sensor snapshots
as independent evidence.
