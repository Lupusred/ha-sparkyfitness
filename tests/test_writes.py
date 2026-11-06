"""Synthetic write/security regressions, never production data."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import voluptuous as vol
from homeassistant.core import Context
from homeassistant.exceptions import ServiceValidationError, Unauthorized
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sparkyfitness.api import (
    InvalidAuth,
    SparkyClient,
    WriteRejected,
    WriteUncertain,
)
from custom_components.sparkyfitness.const import DOMAIN
from custom_components.sparkyfitness.services import SCHEMAS, build_write

ID = "00000000-0000-4000-8000-000000000001"


class Response:
    def __init__(self, status=200, data=None):
        self.status, self.data, self.headers = status, data, {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def json(self):
        return self.data


@pytest.fixture
def entry(hass):
    config = MockConfigEntry(
        domain=DOMAIN,
        unique_id="account-a",
        title="Synthetic account",
        data={"url": "http://server", "api_key": "synthetic-secret", "user_id": "a"},
        options={"enable_writes": True, "time_zone": "Europe/Berlin"},
    )
    config.add_to_hass(hass)
    return config


@pytest.fixture
async def loaded(hass, entry, snapshot):
    with patch("custom_components.sparkyfitness.api.SparkyClient.snapshot", return_value=snapshot):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield entry
        await hass.config_entries.async_unload(entry.entry_id)


async def invoke(hass, entry, service="set_body_measurements", **kwargs):
    return await hass.services.async_call(
        DOMAIN,
        service,
        {"config_entry_id": entry.entry_id, **kwargs},
        blocking=True,
        return_response=True,
    )


async def test_body_subset_and_refresh(hass, loaded):
    client = loaded.runtime_data.client
    with (
        patch.object(client, "identity", return_value="a"),
        patch.object(client, "write", return_value={"id": ID}) as write,
    ):
        result = await invoke(hass, loaded, weight=80, waist=90, date="2026-01-01")
    assert result == {"saved": True, "refresh_successful": True}
    write.assert_awaited_once_with(
        "measurements/check-in", {"entry_date": "2026-01-01", "weight": 80.0, "waist": 90.0}, "a"
    )


async def test_disabled_and_wrong_account(hass, loaded):
    client = loaded.runtime_data.client
    with patch.object(client, "identity", return_value="b"), patch.object(client, "write") as write:
        with pytest.raises(ServiceValidationError, match="different account"):
            await invoke(hass, loaded, weight=80)
        write.assert_not_called()
    # Options updates are read at call time, even before the queued reload.
    with patch("custom_components.sparkyfitness._async_reload", new_callable=AsyncMock):
        hass.config_entries.async_update_entry(loaded, options={"enable_writes": False})
        with pytest.raises(ServiceValidationError, match="Enable write"):
            await invoke(hass, loaded, weight=80)


@pytest.mark.parametrize(
    "field,value",
    [
        ("weight", float("nan")),
        ("weight", True),
        ("steps", 1.5),
        ("weight", -1),
        ("body_fat_percentage", 101),
        ("bmr", 10),
    ],
)
def test_bad_measurements(field, value):
    with pytest.raises(vol.Invalid):
        SCHEMAS["set_body_measurements"]({"config_entry_id": "a", field: value})


@pytest.mark.parametrize(
    "field", ["user_id", "source", "calories_remaining", "calories_goal", "url", "api_key"]
)
def test_no_arbitrary_fields(field):
    with pytest.raises(vol.Invalid):
        SCHEMAS["set_body_measurements"]({"config_entry_id": "a", field: "x"})


async def test_custom_ownership_types(hass, loaded):
    client = loaded.runtime_data.client
    category = {"id": ID, "data_type": "numeric", "frequency": "Hourly"}
    with (
        patch.object(client, "identity", return_value="a"),
        patch.object(client, "get", return_value=[category]),
        patch.object(client, "write", return_value={"id": ID}) as write,
    ):
        with pytest.raises(ServiceValidationError, match="require hour"):
            await invoke(hass, loaded, "record_custom_measurement", category_id=ID, value="12")
        await invoke(hass, loaded, "record_custom_measurement", category_id=ID, value="12", hour=5)
        assert write.call_args.args[1]["source"] == "Home Assistant"
        assert write.call_args.args[1]["entry_hour"] == 5
        with pytest.raises(ServiceValidationError, match="does not belong"):
            await invoke(
                hass,
                loaded,
                "record_custom_measurement",
                category_id="00000000-0000-4000-8000-000000000002",
                value=2,
            )
        category["data_type"] = "text"
        await invoke(
            hass, loaded, "record_custom_measurement", category_id=ID, value="Rested", hour=5
        )
        assert write.call_args.args[1]["value"] == "Rested"


async def test_water_partial_result_not_success(hass, loaded):
    client = loaded.runtime_data.client
    with (
        patch.object(client, "identity", return_value="a"),
        patch.object(
            client, "write", return_value={"processed": [], "errors": [{"error": "private body"}]}
        ) as write,
    ):
        with pytest.raises(ServiceValidationError, match="not confirmed") as err:
            await invoke(hass, loaded, "record_water", amount_ml=250, record_id="glass-1")
        assert "private body" not in str(err.value)
        payload = write.call_args.args[1][0]
        assert payload["source_id"] == "ha-sparkyfitness:account-a:glass-1"
        assert payload["value"] == 250


async def test_sleep_offset_and_no_calculated_fields(hass, loaded):
    client = loaded.runtime_data.client
    with (
        patch.object(client, "identity", return_value="a"),
        patch.object(client, "write", return_value={"id": ID}) as write,
    ):
        await invoke(
            hass,
            loaded,
            "record_sleep",
            bedtime="2026-03-28T23:00:00+01:00",
            wake_time="2026-03-29T08:00:00+02:00",
        )
        payload = write.call_args.args[1]
        assert payload["duration_in_seconds"] == 8 * 3600
        assert payload["entry_date"] == "2026-03-29"
        assert "stage_events" not in payload and "sleep_score" not in payload


@pytest.mark.parametrize(
    "service,values,path",
    [
        (
            "log_food",
            {"food_id": ID, "variant_id": ID, "quantity": 100, "unit": "g", "meal_type": "snacks"},
            "food-entries",
        ),
        (
            "log_exercise",
            {"exercise_id": ID, "duration_minutes": 30, "calories_burned": 200},
            "exercise-entries",
        ),
    ],
)
async def test_diary_actions(hass, loaded, service, values, path):
    with (
        patch.object(loaded.runtime_data.client, "identity", return_value="a"),
        patch.object(loaded.runtime_data.client, "write", return_value={"id": ID}) as write,
    ):
        await invoke(hass, loaded, service, **values)
        assert write.call_args.args[0] == path
        assert "user_id" not in write.call_args.args[1]


async def test_nonadmin_denied(hass, loaded, hass_read_only_user):
    with patch.object(loaded.runtime_data.client, "write") as write:
        with pytest.raises(Unauthorized):
            await hass.services.async_call(
                DOMAIN,
                "set_body_measurements",
                {"config_entry_id": loaded.entry_id, "weight": 80},
                blocking=True,
                context=Context(user_id=hass_read_only_user.id),
            )
        write.assert_not_called()


@pytest.mark.parametrize(
    "status,error", [(403, WriteRejected), (500, WriteUncertain), (503, WriteUncertain)]
)
async def test_transport_write_failure(status, error):
    session = MagicMock()
    session.get.return_value = Response(data={"authenticatedUserId": "a", "activeUserId": "a"})
    session.post.return_value = Response(status, {"key": "secret"})
    with pytest.raises(error) as err:
        await SparkyClient(session, "http://server", "secret").write(
            "measurements/check-in", {"weight": 80}, "a"
        )
    assert "secret" not in str(err.value)
    assert session.post.call_count == 1
    assert session.post.call_args.kwargs["allow_redirects"] is False


async def test_transport_timeout_not_retried():
    session = MagicMock()
    session.get.return_value = Response(data={"authenticatedUserId": "a", "activeUserId": "a"})
    session.post.side_effect = asyncio.TimeoutError()
    with pytest.raises(WriteUncertain):
        await SparkyClient(session, "http://server", "secret").write(
            "measurements/check-in", {"weight": 80}, "a"
        )
    assert session.post.call_count == 1


async def test_transport_identity_changed():
    session = MagicMock()
    session.get.return_value = Response(data={"authenticatedUserId": "b", "activeUserId": "b"})
    with pytest.raises(InvalidAuth):
        await SparkyClient(session, "http://server", "secret").write(
            "measurements/check-in", {}, "a"
        )
    session.post.assert_not_called()


async def test_future_date_and_empty(hass, loaded):
    with pytest.raises(ServiceValidationError, match="Future"):
        await build_write(
            "set_body_measurements",
            {"date": "2999-01-01", "weight": 1},
            loaded.runtime_data,
            loaded,
        )
    with pytest.raises(ServiceValidationError, match="at least"):
        await build_write("set_body_measurements", {}, loaded.runtime_data, loaded)


async def test_post_roundtrip(aiohttp_server, socket_enabled):
    from aiohttp import web

    received = []

    async def identity(request):
        return web.json_response({"authenticatedUserId": "a", "activeUserId": "a"})

    async def write(request):
        received.append(await request.json())
        assert request.headers["x-api-key"] == "synthetic-secret"
        return web.json_response({"id": ID}, status=201)

    app = web.Application()
    app.router.add_get("/api/identity/user", identity)
    app.router.add_post("/api/measurements/custom-entries", write)
    server = await aiohttp_server(app)
    async with aiohttp.ClientSession() as session:
        client = SparkyClient(session, str(server.make_url("")), "synthetic-secret")
        result = await client.write(
            "measurements/custom-entries", {"category_id": ID, "value": 12}, "a"
        )
    assert result["id"] == ID and received == [{"category_id": ID, "value": 12}]


async def test_successful_water_and_refresh_failure(hass, loaded):
    from custom_components.sparkyfitness.api import ApiError

    client = loaded.runtime_data.client
    with (
        patch.object(client, "identity", return_value="a"),
        patch.object(
            client,
            "write",
            return_value={
                "processed": [{"status": "success", "data": {"id": ID}}],
                "errors": [],
                "skipped": [],
            },
        ),
        patch.object(client, "snapshot", side_effect=ApiError("Offline")),
    ):
        response = await invoke(hass, loaded, "record_water", amount_ml=250, record_id="test")
        assert response == {"saved": True, "refresh_successful": False}


@pytest.mark.parametrize("result", [{}, {"error": "sensitive"}, [], None])
async def test_unconfirmed_write_not_success(hass, loaded, result):
    with (
        patch.object(loaded.runtime_data.client, "identity", return_value="a"),
        patch.object(loaded.runtime_data.client, "write", return_value=result),
    ):
        with pytest.raises(ServiceValidationError) as err:
            await invoke(hass, loaded, weight=80)
        assert "sensitive" not in str(err.value)


async def test_write_after_unload_rejected(hass, loaded):
    config_id = loaded.entry_id
    await hass.config_entries.async_unload(config_id)
    with pytest.raises(ServiceValidationError, match="loaded"):
        await invoke(hass, loaded, weight=80)


async def test_reconfigure_key_preserves_account(hass, loaded):
    from homeassistant.data_entry_flow import FlowResultType

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "reconfigure", "entry_id": loaded.entry_id}
    )
    assert result["type"] == FlowResultType.FORM
    with patch(
        "custom_components.sparkyfitness.config_flow.SparkyClient.identity", return_value="other"
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"api_key": "test-wrong"}
        )
        assert result["errors"]["base"] == "wrong_account"
    with (
        patch(
            "custom_components.sparkyfitness.config_flow.SparkyClient.identity", return_value="a"
        ),
        patch.object(hass.config_entries, "async_reload", return_value=True),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"api_key": "test-write-key"}
        )
        assert result["reason"] == "reconfigure_successful"
        assert loaded.data["api_key"] == "test-write-key"
        assert loaded.unique_id == "account-a"


async def test_redirect_does_not_forward_key(aiohttp_server, socket_enabled):
    from aiohttp import web

    from custom_components.sparkyfitness.api import ApiError

    received = []

    async def trap(request):
        received.append(dict(request.headers))
        return web.json_response({})

    target = web.Application()
    target.router.add_route("*", "/trap", trap)
    target_server = await aiohttp_server(target)

    async def identity(request):
        return web.json_response({"authenticatedUserId": "a", "activeUserId": "a"})

    async def redirect(request):
        raise web.HTTPTemporaryRedirect(str(target_server.make_url("/trap")))

    source = web.Application()
    source.router.add_get("/api/identity/user", identity)
    source.router.add_post("/api/measurements/check-in", redirect)
    server = await aiohttp_server(source)
    async with aiohttp.ClientSession() as session:
        client = SparkyClient(session, str(server.make_url("")), "test-secret")
        with pytest.raises(ApiError):
            await client.write("measurements/check-in", {"weight": 80}, "a")
    assert received == []


async def test_number_write_uses_guarded_service(hass, loaded):
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("number", DOMAIN, "account-a_write_weight")
    assert entity_id
    assert len([s for s in hass.states.async_all("number")]) == 12
    client = loaded.runtime_data.client
    with (
        patch.object(client, "identity", return_value="a"),
        patch.object(client, "write", return_value={"id": ID}) as write,
    ):
        await hass.services.async_call(
            "number", "set_value", {"entity_id": entity_id, "value": 81.2}, blocking=True
        )
        write.assert_awaited_once_with(
            "measurements/check-in",
            {"entry_date": loaded.runtime_data.today(), "weight": 81.2},
            "a",
        )
    # The fixture's refreshed server value wins; no optimistic 81.2 state.
    assert float(hass.states.get(entity_id).state) == 80.2


async def test_number_preserves_nonadmin_context(hass, loaded, hass_admin_user):
    from homeassistant.helpers import entity_registry as er

    user = await hass.auth.async_create_user("Synthetic user", group_ids=["system-users"])
    entity_id = er.async_get(hass).async_get_entity_id("number", DOMAIN, "account-a_write_weight")
    with patch.object(loaded.runtime_data.client, "write") as write:
        with pytest.raises(Unauthorized):
            await hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": entity_id, "value": 81},
                blocking=True,
                context=Context(user_id=user.id),
            )
        write.assert_not_called()
