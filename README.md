# Weather X

[![CI](https://github.com/backiron/weather-x/actions/workflows/ci.yml/badge.svg)](https://github.com/backiron/weather-x/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/backiron/weather-x)](https://github.com/backiron/weather-x/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/weatherx-local)](https://pypi.org/project/weatherx-local/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Current stable release: v1.0.2.** This release establishes the documented CLI, Python API,
JSON input contracts, and HTTP endpoints as the first stable public interface. Stable software
does not imply universal scientific validity; the case-study and responsible-use limits remain
part of the release contract.

Weather X estimates a local near-surface air temperature from a dense network of personal
weather stations. It combines spatial geometry, elevation adjustment, observation freshness,
wind direction, solar exposure, station reliability, historical bias, and correlated-sensor
controls. Every estimate includes uncertainty and per-station diagnostics.

The project began as an attempt to reconstruct a delayed, discretized reference value for a
threshold-sensitive downstream application. The exact-value hypothesis did not survive
out-of-time validation. The reusable result is an open, causal, and auditable sensor-fusion
system.

Read the full mathematical research note: [Weather X: Causal Reconstruction of Local Temperature
from a Dense Personal Weather Station Network](ARTICLE.md).

Release history is documented in [CHANGELOG.md](CHANGELOG.md).

Install the stable package from PyPI:

```bash
pip install weatherx-local
```

The PyPI distribution is named `weatherx-local`; the Python import package and command-line
program remain `weatherx`. The project and repository retain the human-facing name **Weather X**.

> Weather X does not replace an official weather station. It estimates a spatially filtered
> local temperature state from imperfect crowd-sourced sensors.

## What this repository demonstrates

- configurable target coordinates and station networks;
- physical and statistical station weighting;
- explicit observation-time and receipt-time handling;
- correlated-group and directional-sector controls;
- uncertainty, effective sample size, and station-level diagnostics;
- append-only evidence with canonical SHA-256 hashes;
- delayed-label evaluation without current-target leakage;
- a CLI, JSON API, and lightweight browser dashboard;
- an honest case study in which continuous error improved while threshold reliability remained
  insufficient for the original application.

## Five-minute demo

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
weatherx estimate \
  --config examples/network.example.json \
  --observations examples/observations.example.json \
  --as-of 2025-07-15T18:00:00Z \
  --pretty
pytest
```

Run the dashboard:

```bash
weatherx serve \
  --config examples/network.example.json \
  --observations examples/observations.example.json \
  --as-of 2025-07-15T18:00:00Z \
  --host 127.0.0.1 \
  --port 8080
```

Then open `http://127.0.0.1:8080`.

Docker is also supported:

```bash
docker compose up --build
```

## Input contract

The estimator accepts a network configuration and a set of observations. The included example
is synthetic and contains no private station coordinates or provider-owned historical payloads.

Each observation should retain three distinct times when they are available:

1. `observed_at`: when the sensor measured the atmosphere;
2. `received_at`: when the system first received the payload;
3. `generated_at`: when Weather X produced the estimate.

This distinction prevents a later provider revision from being treated as if it were available
at prediction time.

For a provider you are authorized to use, copy `examples/provider.example.json`, map its JSON
fields, keep credentials in environment variables, and run:

```bash
weatherx collect-json --provider-config my-provider.json --output observations.json --pretty
```

The normalized capture records request and receipt times plus a SHA-256 identity, but never writes
credential values.

## Case-study result

In the original single-location case study, a multi-year supervised adaptation reduced strict
reference-point MAE from `1.004 F` to `0.882 F` and increased two-degree threshold accuracy from
`57.87%` to `64.41%`. The remaining `35.59%` cross-threshold error was unacceptable for the
original threshold-sensitive use. See [Case Study](docs/CASE_STUDY.md) and
[Scientific Limitations](docs/LIMITATIONS.md).

These numbers describe one warm-season reference location. They are not a universal claim about
personal weather station networks.

## Repository map

```text
src/weatherx/      Core estimator, providers, evidence ledger, CLI, and API
web/               Dependency-free dashboard
examples/          Synthetic network and observations
research/          Causal evaluation utilities
tests/             Unit and contract tests
docs/              Method, case study, security, and publication boundaries
```

## Data and provider boundary

This repository does not redistribute third-party observation archives. Provider adapters must
be configured by the user under the provider's terms. The bundled live reference adapter uses the
public U.S. National Weather Service API; the PWS demo uses local synthetic JSON.

## Non-goals

- official, regulatory, climate, or safety-critical observations;
- deterministic reconstruction of a specific sensor;
- inference about people, private property, or operational activity;
- automated high-impact decision authority;
- claims of universal urban-temperature accuracy.

## License

Code is released under the MIT License. Data obtained from external providers remains subject to
the provider's terms and is not relicensed by this repository.

Repository: [github.com/backiron/weather-x](https://github.com/backiron/weather-x)
