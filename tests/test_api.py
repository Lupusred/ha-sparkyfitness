from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.sparkyfitness.api import (
    ApiError,
    InvalidAuth,
    RateLimited,
    SparkyClient,
    normalize_url,
)


class Response:
    def __init__(self, status=200, data=None, headers=None):
        self.status, self.data, self.headers = status, data, headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def json(self):
        if isinstance(self.data, Exception):
            raise self.data
        return self.data


@pytest.mark.parametrize(
    "url",
    [
        "ftp://server",
        "https://user:secret@host",
        "https://host/?key=x",
        "https://host/#x",
        "http://host:bad",
        "blah",
    ],
)
def test_bad_url(url):
    with pytest.raises(ValueError, match="Invalid server URL"):
        normalize_url(url)


def test_url():
    assert normalize_url("HTTPS://Example.test/prefix/api/") == "https://example.test/prefix"


@pytest.mark.parametrize(
    "status,error",
    [(401, InvalidAuth), (403, InvalidAuth), (429, RateLimited), (500, ApiError), (302, ApiError)],
)
async def test_errors(status, error):
    session = MagicMock()
    session.get.return_value = Response(status, {"key": "synthetic-secret"})
    client = SparkyClient(session, "http://server", "synthetic-secret")
    with pytest.raises(error) as err:
        await client.identity()
    assert "synthetic-secret" not in str(err.value)
    assert session.get.call_args.kwargs["allow_redirects"] is False
    if status == 429:
        with pytest.raises(RateLimited):
            await client.identity()
        assert session.get.call_count == 1


async def test_identity_and_no_context_header():
    session = MagicMock()
    session.get.return_value = Response(data={"authenticatedUserId": "a", "activeUserId": "a"})
    assert await SparkyClient(session, "http://server", "test").identity() == "a"
    assert session.get.call_args.kwargs["headers"] == {
        "x-api-key": "test",
        "Accept": "application/json",
    }


@pytest.mark.parametrize(
    "data", [{}, [], {"authenticatedUserId": "a", "activeUserId": "b"}, ValueError("secret")]
)
async def test_bad_identity(data):
    session = MagicMock()
    session.get.return_value = Response(data=data)
    with pytest.raises(ApiError):
        await SparkyClient(session, "http://server", "test").identity()


async def test_network():
    session = MagicMock()
    session.get.side_effect = aiohttp.ClientConnectionError("sensitive")
    with pytest.raises(ApiError, match="Connection failed") as err:
        await SparkyClient(session, "http://server", "test").identity()
    assert "sensitive" not in str(err.value)


async def test_snapshot_optional_and_wrong_account():
    session = MagicMock()
    session.get.side_effect = [Response(data={"authenticatedUserId": "a", "activeUserId": "a"})] + [
        Response(404)
    ] * 5
    data = await SparkyClient(session, "http://server", "test").snapshot("2026-11-05", "a")
    assert data["summary"] is None
    session.get.side_effect = None
    session.get.return_value = Response(data={"authenticatedUserId": "b", "activeUserId": "b"})
    with pytest.raises(InvalidAuth):
        await SparkyClient(session, "http://server", "test").snapshot("2026-11-05", "a")


async def test_real_http_roundtrip(aiohttp_server, socket_enabled, snapshot):
    """Exercise the real aiohttp transport against an isolated synthetic server."""
    from aiohttp import web

    paths = []

    async def handler(request):
        assert request.method == "GET"
        assert request.headers["x-api-key"] == "synthetic-key"
        paths.append(request.path)
        responses = {
            "/api/identity/user": {"authenticatedUserId": "a", "activeUserId": "a"},
            "/api/daily-summary": snapshot["summary"],
            "/api/measurements/check-in/latest-on-or-before-date": snapshot["body"],
            "/api/measurements/custom-categories": snapshot["categories"],
            "/api/measurements/custom-entries/2026-11-05": [],
            "/api/measurements/custom-entries": snapshot["custom"],
            "/api/sleep": snapshot["sleep"],
        }
        return web.json_response(responses[request.path])

    app = web.Application()
    app.router.add_get("/{path:.*}", handler)
    server = await aiohttp_server(app)
    async with aiohttp.ClientSession() as session:
        client = SparkyClient(session, str(server.make_url("")), "synthetic-key")
        raw = await client.snapshot("2026-11-05", "a")
    assert raw["body"]["weight"] == "80.2"
    assert raw["custom"][0]["value"] == "32.5"
    assert len(paths) == 7
