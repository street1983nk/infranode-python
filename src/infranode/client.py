"""Keyless Python client for the InfraNode open-data API.

InfraNode is a free, keyless REST API that unifies open public data for 84 German
cities behind one JSON envelope. No API key, no signup.

    from infranode import InfraNode

    api = InfraNode()
    rec = api.weather("berlin")
    print(rec.payload["temperature_c"], rec.attribution["text"])

Every single-city endpoint returns the same envelope; the values live under
``data.payload`` and each record carries its own source attribution and license,
which you must display to your users.

Docs:   https://infranode.dev
Source: https://github.com/street1983nk/infranode (Apache-2.0)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import quote

import httpx

DEFAULT_BASE_URL = "https://infranode.dev/api/v1"

__all__ = [
    "InfraNode",
    "AsyncInfraNode",
    "Record",
    "InfraNodeError",
    "DEFAULT_BASE_URL",
]


class InfraNodeError(Exception):
    """Raised when the API returns a structured error envelope."""

    def __init__(self, code: str, message: str, hint: Optional[str] = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


@dataclass(frozen=True)
class Record:
    """A single InfraNode city record (the ``data`` object of the envelope)."""

    city_slug: str
    payload: dict[str, Any]
    attribution: dict[str, Any]
    source: Optional[str]
    license_id: Optional[str]
    observed_at: Optional[str]
    retrieved_at: Optional[str]
    raw: dict[str, Any]

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "Record":
        return cls(
            city_slug=data.get("city_slug", ""),
            payload=data.get("payload", {}),
            attribution=data.get("attribution", {}),
            source=data.get("source"),
            license_id=data.get("license_id"),
            observed_at=data.get("observed_at"),
            retrieved_at=data.get("retrieved_at"),
            raw=data,
        )


def _slug(slug: str) -> str:
    return quote(slug.strip().lower(), safe="")


def _unwrap(body: dict[str, Any]) -> Any:
    error = body.get("error")
    if error:
        raise InfraNodeError(
            error.get("code", "error"),
            error.get("message", "InfraNode request failed"),
            error.get("hint"),
        )
    return body.get("data")


class _Endpoints:
    """Convenience accessors shared by the sync and async clients."""

    def _path(self, slug: str, endpoint: str) -> str:
        return f"/cities/{_slug(slug)}/{endpoint}"


class InfraNode(_Endpoints):
    """Synchronous client. Reuse one instance; it holds a pooled connection."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 15.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Accept": "application/json", "User-Agent": "infranode-python"},
        )

    def __enter__(self) -> "InfraNode":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        resp = self._client.get(path, params=params)
        return _unwrap(resp.json())

    def record(self, slug: str, endpoint: str) -> Record:
        """Fetch any single-city endpoint (e.g. ``record("berlin", "fuel-prices")``)."""
        return Record.from_data(self._get(self._path(slug, endpoint)))

    def cities(self) -> list[dict[str, Any]]:
        """List all covered German cities."""
        return self._get("/cities")

    def sources(self) -> list[dict[str, Any]]:
        """List all data sources with license and attribution."""
        return self._get("/sources")

    def weather(self, slug: str) -> Record:
        return self.record(slug, "weather")

    def air(self, slug: str) -> Record:
        return self.record(slug, "air")

    def power_price(self, slug: str) -> Record:
        return self.record(slug, "power-price")

    def charging(self, slug: str) -> Record:
        return self.record(slug, "charging")


class AsyncInfraNode(_Endpoints):
    """Asynchronous client backed by ``httpx.AsyncClient``."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 15.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Accept": "application/json", "User-Agent": "infranode-python"},
        )

    async def __aenter__(self) -> "AsyncInfraNode":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        resp = await self._client.get(path, params=params)
        return _unwrap(resp.json())

    async def record(self, slug: str, endpoint: str) -> Record:
        return Record.from_data(await self._get(self._path(slug, endpoint)))

    async def cities(self) -> list[dict[str, Any]]:
        return await self._get("/cities")

    async def sources(self) -> list[dict[str, Any]]:
        return await self._get("/sources")

    async def weather(self, slug: str) -> Record:
        return await self.record(slug, "weather")

    async def air(self, slug: str) -> Record:
        return await self.record(slug, "air")

    async def power_price(self, slug: str) -> Record:
        return await self.record(slug, "power-price")

    async def charging(self, slug: str) -> Record:
        return await self.record(slug, "charging")
