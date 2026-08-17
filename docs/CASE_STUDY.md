# Case Study: A Threshold-Sensitive Reference Location

## Origin

Weather X began with a narrow threshold-sensitive question: could a dense network of personal
weather stations reconstruct the next temperature reported by a public reference location before
the delayed reference value became available?

The project initially treated natural daily maximum temperature as the target. Further data-lineage
work showed that the application depended on a specific public station-history record and its
integer display semantics. The problem changed from forecasting regional weather to reconstructing
the output of one point sensor.

## Engineering work

The private research system combined:

- a multi-station real-time collector;
- geographic and elevation metadata;
- station-specific residual histories;
- solar, wind, freshness, and temperature-trend features;
- correlated-neighbor and directional-sector controls;
- append-only input captures with SHA-256 identities;
- delayed-label state with 60-, 70-, and 90-minute sensitivity lanes;
- grouped out-of-time evaluation;
- a live diagnostic dashboard.

The public repository preserves the generic method. It does not publish provider-owned raw data,
private infrastructure, exact household coordinates, or unrelated application code.

## Frozen aggregate result

The strict single-location comparison used 413 reference points across 18 independent warm-season
dates. A multi-year supervised adaptation produced:

| Metric | Baseline | Adapted model | Change |
|---|---:|---:|---:|
| Mean absolute error | 1.004 F | 0.882 F | -0.122 F |
| Two-degree threshold accuracy | 57.87% | 64.41% | +6.54 percentage points |
| Cross-threshold error | 42.13% | 35.59% | -6.54 percentage points |
| 95th-percentile absolute error | 2.935 F | 2.698 F | -0.237 F |

Date-grouped bootstrap intervals supported a continuous-error improvement. The remaining
cross-threshold error did not support the original threshold-sensitive use.

## What the result means

The case study supports a limited claim:

> A dense, quality-controlled personal weather station network can improve a continuous local
> temperature estimate, while still failing to reproduce the exact discrete output of a reference
> instrument reliably enough for a threshold-sensitive application.

It does not establish universal accuracy, a city-scale temperature product, or a replacement for
official observations.

## Why publish a negative result

The most reusable output is not an automated decision rule. It is the separation of:

- atmospheric measurement time;
- system receipt time;
- label reveal time;
- continuous reconstruction accuracy;
- categorical threshold reliability;
- retrospective fit;
- downstream decision value.

Conflating any two of these can turn a technically strong temperature estimate into an invalid
decision system.
