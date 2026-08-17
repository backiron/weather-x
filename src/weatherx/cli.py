from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

from weatherx.estimator import estimate_temperature
from weatherx.evidence import write_estimate_evidence
from weatherx.models import load_network_config, load_observations, parse_utc
from weatherx.providers.generic_json import fetch_generic_json_observation, load_provider_config
from weatherx.providers.nws import fetch_nws_latest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weatherx",
        description="Auditable local-temperature inference from personal weather stations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    estimate = subparsers.add_parser("estimate", help="Estimate a target temperature from JSON")
    estimate.add_argument("--config", required=True, type=Path)
    estimate.add_argument("--observations", required=True, type=Path)
    estimate.add_argument("--as-of", default=None)
    estimate.add_argument("--output-dir", type=Path, default=None)
    estimate.add_argument("--pretty", action="store_true")

    reference = subparsers.add_parser("reference", help="Fetch a public NWS reference observation")
    reference.add_argument("--station", required=True)
    reference.add_argument(
        "--user-agent",
        default=os.getenv("WEATHERX_NWS_USER_AGENT"),
        help="Descriptive NWS user agent including contact information",
    )
    reference.add_argument("--pretty", action="store_true")

    collect = subparsers.add_parser(
        "collect-json",
        help="Normalize one observation from an authorized JSON weather endpoint",
    )
    collect.add_argument("--provider-config", required=True)
    collect.add_argument("--output", type=Path, default=None)
    collect.add_argument("--pretty", action="store_true")

    serve = subparsers.add_parser("serve", help="Run the JSON API and dashboard")
    serve.add_argument("--config", type=Path, default=None)
    serve.add_argument("--observations", type=Path, default=None)
    serve.add_argument("--as-of", default=None)
    serve.add_argument("--host", default=os.getenv("WEATHERX_HOST") or "127.0.0.1")
    serve.add_argument("--port", type=int, default=int(os.getenv("WEATHERX_PORT") or 8080))
    serve.add_argument("--reload", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "estimate":
        as_of = parse_utc(args.as_of) if args.as_of else datetime.now(UTC)
        estimate = estimate_temperature(
            load_network_config(args.config),
            load_observations(args.observations),
            as_of=as_of,
        )
        if args.output_dir:
            estimate["evidence"] = write_estimate_evidence(
                estimate,
                output_dir=args.output_dir,
            )
        print(json.dumps(estimate, indent=2 if args.pretty else None, sort_keys=True))
        return 0 if estimate.get("estimate") else 2

    if args.command == "reference":
        if not args.user_agent:
            raise SystemExit("--user-agent or WEATHERX_NWS_USER_AGENT is required")
        payload = fetch_nws_latest(args.station, user_agent=args.user_agent)
        print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
        return 0

    if args.command == "collect-json":
        capture = fetch_generic_json_observation(load_provider_config(args.provider_config))
        normalized = {
            "schema": "WEATHER_X_OBSERVATION_BATCH_V1",
            "capture": {key: value for key, value in capture.items() if key != "observation"},
            "observations": [capture["observation"]],
        }
        rendered = json.dumps(normalized, indent=2 if args.pretty else None, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0

    if args.command == "serve":
        if args.config:
            os.environ["WEATHERX_CONFIG"] = str(args.config.resolve())
        if args.observations:
            os.environ["WEATHERX_OBSERVATIONS"] = str(args.observations.resolve())
        if args.as_of:
            parsed_as_of = parse_utc(args.as_of)
            if parsed_as_of is None:
                raise SystemExit("--as-of must be an ISO-8601 timestamp")
            os.environ["WEATHERX_AS_OF"] = parsed_as_of.isoformat()
        uvicorn.run("weatherx.api:app", host=args.host, port=args.port, reload=args.reload)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
