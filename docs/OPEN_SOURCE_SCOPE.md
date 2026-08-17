# Open-Source Scope

This repository contains the reusable, target-agnostic Weather X research system. Its history
begins at the public-release boundary and contains no private development history.

## Included

- target-agnostic sensor-fusion estimator;
- synthetic file-based PWS input;
- public NWS reference adapter;
- append-only evidence ledger and canonical hashes;
- causal delayed-label calibration utilities;
- CLI, FastAPI service, and browser dashboard;
- unit tests and release verification;
- aggregate, non-provider-owned case-study metrics;
- English documentation and publication boundaries.

## Excluded

- unrelated application, automation, account, and operational code;
- authentication, private databases, deployment, and operator infrastructure;
- provider-specific scraping implementations whose redistribution boundary is unclear;
- raw or derived provider payload archives;
- exact original target and household-station coordinates;
- unrelated product strategies and application code;
- private handoffs, internal blueprints, and operational incident notes.

## Why the Git history is new

Starting with a new history prevents deleted credentials, private paths, or restricted artifacts
from remaining recoverable in earlier commits.
