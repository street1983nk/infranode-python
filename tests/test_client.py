from __future__ import annotations

import httpx
import pytest
import respx

from infranode import AsyncInfraNode, InfraNode, InfraNodeError
from infranode.client import DEFAULT_BASE_URL
from infranode.integrations._core import get_city_data, list_cities

WEATHER = {
    "data": {
        "city_slug": "berlin",
        "observed_at": "2026-06-19T20:30:00Z",
        "retrieved_at": "2026-06-19T20:45:00Z",
        "source": "dwd",
        "license_id": "geonutzv",
        "attribution": {"text": "Deutscher Wetterdienst", "license_url": "https://dwd.de"},
        "payload": {"kind": "weather", "temperature_c": 23.6, "humidity": 74.0},
    },
    "meta": {"source_status": "ok"},
}

ERROR = {
    "error": {"code": "not_found", "message": "nicht gefunden", "hint": "Pfad pruefen"},
    "meta": {"correlation_id": "x"},
}

CITIES = {"data": [{"slug": "berlin", "name_de": "Berlin", "state": "BE"}]}


@respx.mock
def test_record_unwraps_payload():
    respx.get(f"{DEFAULT_BASE_URL}/cities/berlin/weather").mock(
        return_value=httpx.Response(200, json=WEATHER)
    )
    with InfraNode() as api:
        rec = api.weather("berlin")
    assert rec.city_slug == "berlin"
    assert rec.payload["temperature_c"] == 23.6
    assert rec.attribution["text"] == "Deutscher Wetterdienst"
    assert rec.observed_at == "2026-06-19T20:30:00Z"


@respx.mock
def test_slug_is_normalized():
    route = respx.get(f"{DEFAULT_BASE_URL}/cities/berlin/weather").mock(
        return_value=httpx.Response(200, json=WEATHER)
    )
    with InfraNode() as api:
        api.weather("  BERLIN  ")
    assert route.called


@respx.mock
def test_error_envelope_raises():
    respx.get(f"{DEFAULT_BASE_URL}/cities/essen/wetter").mock(
        return_value=httpx.Response(200, json=ERROR)
    )
    with InfraNode() as api:
        with pytest.raises(InfraNodeError) as exc:
            api.record("essen", "wetter")
    assert exc.value.code == "not_found"
    assert exc.value.hint == "Pfad pruefen"


@respx.mock
def test_cities_returns_list():
    respx.get(f"{DEFAULT_BASE_URL}/cities").mock(
        return_value=httpx.Response(200, json=CITIES)
    )
    with InfraNode() as api:
        cities = api.cities()
    assert cities[0]["slug"] == "berlin"


@respx.mock
async def test_async_record():
    respx.get(f"{DEFAULT_BASE_URL}/cities/berlin/weather").mock(
        return_value=httpx.Response(200, json=WEATHER)
    )
    async with AsyncInfraNode() as api:
        rec = await api.weather("berlin")
    assert rec.payload["humidity"] == 74.0


@respx.mock
def test_core_get_city_data_carries_attribution():
    respx.get(f"{DEFAULT_BASE_URL}/cities/berlin/weather").mock(
        return_value=httpx.Response(200, json=WEATHER)
    )
    out = get_city_data("berlin", "weather")
    assert out["payload"]["temperature_c"] == 23.6
    assert out["attribution"]["text"] == "Deutscher Wetterdienst"


@respx.mock
def test_core_get_city_data_handles_error():
    respx.get(f"{DEFAULT_BASE_URL}/cities/essen/weather").mock(
        return_value=httpx.Response(200, json=ERROR)
    )
    out = get_city_data("essen", "weather")
    assert out["error"] == "not_found"


@respx.mock
def test_core_list_cities():
    respx.get(f"{DEFAULT_BASE_URL}/cities").mock(
        return_value=httpx.Response(200, json=CITIES)
    )
    out = list_cities()
    assert out == [{"slug": "berlin", "name": "Berlin", "state": "BE"}]
