# Changelog

All notable public changes to Weather X are documented here. The project follows Semantic
Versioning for its documented CLI, Python API, JSON input contracts, and HTTP endpoints.

## [1.0.2] - 2026-08-16

This packaging-only release publishes the project under the accepted PyPI distribution name
`weatherx-local`. The human-facing project name remains Weather X, and the Python import package
and CLI remain `weatherx`. There are no estimator, data-contract, API, or scientific-claim changes
from 1.0.0.

## [1.0.1] - 2026-08-16

This packaging-only GitHub release attempted to use the PyPI distribution name `weatherx`.
PyPI rejected that name under its project-name similarity protection, so version 1.0.1 was not
published to PyPI. There were no estimator, data-contract, API, or scientific-claim changes.

## [1.0.0] - 2026-08-16

Weather X 1.0.0 is the first stable, sanitized, and independently reproducible public release.

### Included

- a target-agnostic local-temperature estimator with geometry, freshness, wind, exposure,
  reliability, bias, correlation, and uncertainty controls;
- typed JSON configuration and observation contracts;
- a command-line interface, Python API, FastAPI service, and lightweight browser dashboard;
- append-only evidence records with canonical SHA-256 identities;
- causal delayed-label evaluation utilities and synthetic demonstration data;
- a mathematical research note, six vector figures, case-study metrics, and explicit scientific
  limitations;
- automated tests, formatting checks, public-boundary scanning, and a hashed release manifest;
- Docker and source-package distribution support.

### Validation boundary

The bundled case study improved continuous reference-point error but did not meet the reliability
requirement of the original threshold-sensitive downstream use. Version 1.0.0 stabilizes the
software interfaces and reproducible research artifact; it does not claim universal accuracy or
official-observation status.

[1.0.2]: https://github.com/backiron/weather-x/releases/tag/v1.0.2
[1.0.1]: https://github.com/backiron/weather-x/releases/tag/v1.0.1
[1.0.0]: https://github.com/backiron/weather-x/releases/tag/v1.0.0
