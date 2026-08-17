# Scientific Limitations

Weather X is an experimental engineering project. Its limitations are part of the result.

## External validity

- The frozen strict case study covers one reference location and 18 warm-season dates.
- Results do not establish performance in winter, complex terrain, coastal climates, or other
  cities.
- The same reference year was inspected repeatedly during development and must not be reused as a
  new promotion holdout.

## Sensor metadata

- Personal weather station siting, mounting height, shielding, ventilation, maintenance, and
  sensor replacement are often unknown.
- Provider quality flags do not make a household installation equivalent to a professional site.
- Exact household coordinates are not distributed by this repository.

## Availability

- Historical provider observations may contain measurement time without reliable first-receipt
  time.
- Retrospective reconstruction accuracy is not proof that the same payload was available in real
  time.
- The open-source example is synthetic and cannot establish live provider latency.

## Model scope

- Elevation, radiation, wind, and correlation adjustments are testable assumptions, not immutable
  physical laws.
- A weighted center can hide multi-modal local temperature structure.
- Soft correlation and sector penalties do not recover truly independent information.
- The uncertainty interval is empirical and should be recalibrated for every new network.

## Application boundary

Weather X must not be used as:

- an official observation;
- a regulatory or safety-critical input;
- a climate record;
- a deterministic reconstruction of a named sensor;
- an operational-activity monitoring system;
- automated high-impact decision authority.

## Required evidence for a broader claim

A city-scale or general-purpose claim would require multiple independent reference sites, spatial
leave-one-location-out validation, cold- and warm-season coverage, professional-network baselines,
pre-registered evaluation, and legally redistributable receipt-time data.
