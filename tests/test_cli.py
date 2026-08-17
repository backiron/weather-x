from __future__ import annotations

import os

from weatherx import cli


def test_serve_cli_maps_explicit_demo_inputs_to_api_environment(tmp_path, monkeypatch) -> None:
    config = tmp_path / "network.json"
    observations = tmp_path / "observations.json"
    calls: list[tuple[tuple, dict]] = []
    monkeypatch.setattr(cli.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

    result = cli.main(
        [
            "serve",
            "--config",
            str(config),
            "--observations",
            str(observations),
            "--as-of",
            "2025-07-15T18:00:00Z",
            "--host",
            "127.0.0.1",
            "--port",
            "8081",
        ]
    )

    assert result == 0
    assert os.environ["WEATHERX_CONFIG"] == str(config.resolve())
    assert os.environ["WEATHERX_OBSERVATIONS"] == str(observations.resolve())
    assert os.environ["WEATHERX_AS_OF"] == "2025-07-15T18:00:00+00:00"
    assert calls == [(("weatherx.api:app",), {"host": "127.0.0.1", "port": 8081, "reload": False})]
