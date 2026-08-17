"""Provider adapters for public or user-supplied observations."""

from weatherx.providers.generic_json import fetch_generic_json_observation
from weatherx.providers.nws import fetch_nws_latest

__all__ = ["fetch_generic_json_observation", "fetch_nws_latest"]
