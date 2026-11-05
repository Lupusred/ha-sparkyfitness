"""Read-only SparkyFitness transport. Never log credentials or response bodies."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from time import monotonic
from urllib.parse import urlsplit, urlunsplit

import aiohttp


class ApiError(Exception):
    """Safe, credential-free API failure."""


class InvalidAuth(ApiError):
    """Key invalid, expired, or lacks permission."""


class RateLimited(ApiError):
    """Server retry window is still active."""


def normalize_url(value: str) -> str:
    """Accept server origins and reverse-proxy prefixes, never embedded secrets."""
    try:
        parts = urlsplit(value.strip())
        _ = parts.port
        if (
            parts.scheme not in ("http", "https")
            or not parts.hostname
            or parts.username
            or parts.password
            or parts.query
            or parts.fragment
        ):
            raise ValueError
        path = parts.path.rstrip("/")
        if path.endswith("/api"):
            path = path[:-4]
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))
    except (ValueError, AttributeError):
        raise ValueError("Invalid server URL") from None


class SparkyClient:
    """One session and key per account; redirects cannot leak the key."""

    def __init__(self, session: aiohttp.ClientSession, url: str, key: str):
        self.session = session
        self.url = normalize_url(url)
        self._key = key
        self._retry_at = 0.0

    async def get(self, path: str, *, params=None, optional=False):
        if monotonic() < self._retry_at:
            raise RateLimited("API rate limit; waiting for retry window")
        try:
            async with self.session.get(
                f"{self.url}/api/{path}",
                params=params,
                headers={"x-api-key": self._key, "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30),
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise InvalidAuth("API key rejected or permission denied")
                if response.status == 429:
                    retry = response.headers.get("Retry-After", "60")
                    try:
                        seconds = float(retry)
                    except ValueError:
                        try:
                            seconds = (
                                parsedate_to_datetime(retry) - datetime.now(timezone.utc)
                            ).total_seconds()
                        except (ValueError, TypeError, OverflowError):
                            seconds = 60
                    self._retry_at = monotonic() + max(60, min(seconds, 86400))
                    raise RateLimited("API rate limit reached")
                if response.status == 404 and optional:
                    return None
                if response.status != 200:
                    raise ApiError(f"API returned HTTP {response.status}")
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            raise ApiError("Connection failed or invalid JSON response") from None

    async def identity(self) -> str:
        data = await self.get("identity/user")
        if (
            not isinstance(data, dict)
            or not isinstance(data.get("authenticatedUserId"), str)
            or not data["authenticatedUserId"]
            or data.get("activeUserId") != data["authenticatedUserId"]
        ):
            raise ApiError("Invalid or switched user identity")
        return data["authenticatedUserId"]

    async def snapshot(self, day: str, user_id: str) -> dict:
        # Revalidate each cycle: key rotation must never silently change accounts.
        if await self.identity() != user_id:
            raise InvalidAuth("API key belongs to a different account")
        result = {"day": day}
        requests = {
            "summary": ("daily-summary", {"date": day}, dict),
            "body": ("measurements/check-in/latest-on-or-before-date", {"date": day}, dict),
            "categories": ("measurements/custom-categories", None, list),
            "custom": (f"measurements/custom-entries/{day}", None, list),
            "sleep": ("sleep", {"startDate": day, "endDate": day}, list),
        }
        for name, (path, params, expected) in requests.items():
            data = await self.get(path, params=params, optional=True)
            if data is not None and not isinstance(data, expected):
                raise ApiError("Unexpected API response structure")
            if isinstance(data, list) and any(not isinstance(row, dict) for row in data):
                raise ApiError("Unexpected API row structure")
            result[name] = data
        # Non-daily custom body measurements persist until replaced. Daily/hourly
        # health values are deliberately restricted to the selected calendar day.
        for category in result["categories"] or []:
            if category.get("frequency") == "All" and isinstance(category.get("id"), str):
                rows = await self.get(
                    "measurements/custom-entries",
                    params={
                        "category_id": category["id"],
                        "limit": 1,
                        "orderBy": "entry_timestamp.desc",
                    },
                    optional=True,
                )
                if rows is not None and (
                    not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows)
                ):
                    raise ApiError("Unexpected custom measurement structure")
                result["custom"] = (result["custom"] or []) + (rows or [])
        return result
