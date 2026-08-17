from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from weatherx.estimator import estimate_temperature
from weatherx.evidence import write_estimate_evidence
from weatherx.models import load_network_config, load_observations, parse_utc


def _path(name: str, default: str) -> Path:
    return Path(os.getenv(name) or default).resolve()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Weather X",
        version="0.1.0",
        description="Experimental local-temperature inference from personal weather stations.",
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "weather-x"}

    @app.get("/api/estimate")
    def current_estimate(write_evidence: bool = False) -> dict:
        config_path = _path("WEATHERX_CONFIG", "examples/network.example.json")
        observations_path = _path("WEATHERX_OBSERVATIONS", "examples/observations.example.json")
        if not config_path.exists() or not observations_path.exists():
            raise HTTPException(
                status_code=503,
                detail="Example configuration or observations missing",
            )
        configured_as_of = parse_utc(os.getenv("WEATHERX_AS_OF"))
        estimate = estimate_temperature(
            load_network_config(config_path),
            load_observations(observations_path),
            as_of=configured_as_of or datetime.now(UTC),
        )
        if write_evidence:
            estimate["evidence"] = write_estimate_evidence(
                estimate,
                output_dir=_path("WEATHERX_EXPORT_DIR", "exports"),
            )
        return estimate

    web_dir = _path("WEATHERX_WEB_DIR", "web")
    if web_dir.exists():
        assets = web_dir / "assets"
        if assets.exists():
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(web_dir / "index.html")

    return app


app = create_app()
