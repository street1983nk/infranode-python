"""Plain, framework-agnostic functions that the LangChain and LlamaIndex tools wrap.

Keeping the actual work here means both integrations share one tested code path and
return LLM-friendly, attribution-carrying dicts.
"""

from __future__ import annotations

from typing import Any

from infranode.client import DEFAULT_BASE_URL, InfraNode, InfraNodeError

# Datasets an LLM may request. Mirrors the InfraNode per-city endpoints.
DATASETS = (
    "weather",
    "air",
    "power-price",
    "power-load",
    "charging",
    "sharing",
    "fuel-prices",
    "pollen-uv",
    "water-level",
    "transit",
    "station-departures",
    "demographics",
    "land-values",
    "election",
    "tourism",
    "accidents",
)

TOOL_DESCRIPTION = (
    "Get live open public data for a German city from InfraNode (keyless, 84 cities). "
    "Pass the city as a lowercase slug (e.g. 'berlin', 'muenchen', 'koeln') and a "
    "dataset. Valid datasets: " + ", ".join(DATASETS) + ". Returns the data payload "
    "plus the source attribution, which must be shown to the user."
)


def get_city_data(city: str, dataset: str, *, base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    """Fetch one dataset for one German city. Returns payload + attribution."""
    with InfraNode(base_url=base_url) as api:
        try:
            rec = api.record(city, dataset)
        except InfraNodeError as exc:
            return {"error": exc.code, "message": exc.message, "hint": exc.hint}
        return {
            "city": rec.city_slug,
            "dataset": dataset,
            "payload": rec.payload,
            "observed_at": rec.observed_at,
            "attribution": rec.attribution,
        }


def list_cities(*, base_url: str = DEFAULT_BASE_URL) -> list[dict[str, Any]]:
    """List covered German cities with slug, name and state."""
    with InfraNode(base_url=base_url) as api:
        return [
            {"slug": c["slug"], "name": c.get("name_de"), "state": c.get("state")}
            for c in api.cities()
        ]
