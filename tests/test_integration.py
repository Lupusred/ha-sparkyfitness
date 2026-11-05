from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sparkyfitness.api import ApiError, InvalidAuth
from custom_components.sparkyfitness.config_flow import account_id
from custom_components.sparkyfitness.const import DOMAIN
from custom_components.sparkyfitness.coordinator import SparkyCoordinator


def entry(user="a"):
    return MockConfigEntry(
        domain=DOMAIN,
        title="SparkyFitness " + user,
        unique_id=account_id("http://server", user),
        data={CONF_URL: "http://server", CONF_API_KEY: "synthetic-key", "user_id": user},
    )


async def test_flow_and_duplicate(hass):
    with (
        patch(
            "custom_components.sparkyfitness.config_flow.SparkyClient.identity", return_value="a"
        ),
        patch("custom_components.sparkyfitness.async_setup_entry", return_value=True),
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        assert result["type"] == FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_URL: "http://server/", CONF_API_KEY: "synthetic-key"}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={CONF_URL: "http://server", CONF_API_KEY: "another-key"},
        )
        assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    "exc,code", [(InvalidAuth(), "invalid_auth"), (ApiError(), "cannot_connect")]
)
async def test_flow_fail(hass, exc, code):
    with patch(
        "custom_components.sparkyfitness.config_flow.SparkyClient.identity", side_effect=exc
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={CONF_URL: "http://server", CONF_API_KEY: "test"},
        )
        assert result["errors"]["base"] == code


async def test_setup_dynamic_users_recovery(hass, snapshot):
    registry = er.async_get(hass)
    entries = [entry("a"), entry("b")]
    with patch("custom_components.sparkyfitness.api.SparkyClient.snapshot", return_value=snapshot):
        for config in entries:
            config.add_to_hass(hass)
            assert await hass.config_entries.async_setup(config.entry_id)
        await hass.async_block_till_done()
        for config in entries:
            coordinator = config.runtime_data
            coordinator.day = coordinator.today()
            entity_id = registry.async_get_entity_id("sensor", DOMAIN, config.unique_id + "_weight")
            assert entity_id
            assert hass.states.get(entity_id).state == "80.2"
            assert hass.states.get(entity_id).attributes["unit_of_measurement"] == "kg"
        coordinator = entries[0].runtime_data
        snapshot["categories"].append(
            {"id": "new", "name": "New metric", "measurement_type": "%", "frequency": "Daily"}
        )
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert registry.async_get_entity_id("sensor", DOMAIN, entries[0].unique_id + "_custom_new")
        assert not registry.async_get_entity_id(
            "sensor", DOMAIN, entries[1].unique_id + "_custom_new"
        )
        with patch.object(coordinator.client, "snapshot", side_effect=ApiError("Offline")):
            await coordinator.async_refresh()
            assert not coordinator.last_update_success
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        for config in entries:
            session = config.runtime_data.client.session
            assert await hass.config_entries.async_unload(config.entry_id)
            assert session.closed


async def test_timezone_and_auth(hass, snapshot, freezer):
    config = entry()
    config.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config, options={"time_zone": "Europe/Berlin", "update_interval": 15}
    )
    client = AsyncMock()
    client.snapshot.return_value = snapshot
    coordinator = SparkyCoordinator(hass, config, client)
    freezer.move_to("2026-03-28T23:30:00Z")
    assert coordinator.today() == "2026-03-29"
    await coordinator._async_update_data()
    client.snapshot.assert_awaited_with("2026-03-29", "a")
    freezer.move_to("2026-03-29T22:30:00Z")
    assert coordinator.today() == "2026-03-30"
    client.snapshot.side_effect = InvalidAuth("Expired")
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()
    client.snapshot.side_effect = ApiError("Offline")
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_options(hass):
    config = entry()
    config.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(config.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"update_interval": 30, "time_zone": "Europe/Berlin"}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert config.options["update_interval"] == 30


async def test_reauth_rejects_other_account_then_renews(hass):
    config = entry()
    config.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "reauth", "entry_id": config.entry_id}, data=config.data
    )
    with patch(
        "custom_components.sparkyfitness.config_flow.SparkyClient.identity", return_value="b"
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: "other"}
        )
        assert result["errors"]["base"] == "wrong_account"
    with (
        patch(
            "custom_components.sparkyfitness.config_flow.SparkyClient.identity", return_value="a"
        ),
        patch.object(hass.config_entries, "async_reload", return_value=True),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: "renewed"}
        )
        assert result["reason"] == "reauth_successful"
        assert config.data[CONF_API_KEY] == "renewed"


async def test_polling_midnight_and_stable_rename(hass, snapshot, freezer):
    from datetime import timedelta

    from homeassistant.util import dt as dt_util
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    freezer.move_to("2026-11-05T22:40:00Z")
    config = entry()
    config.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config, options={"time_zone": "Europe/Berlin", "update_interval": 15}
    )
    with patch(
        "custom_components.sparkyfitness.api.SparkyClient.snapshot", return_value=snapshot
    ) as fetch:
        assert await hass.config_entries.async_setup(config.entry_id)
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        uid = config.unique_id + "_custom_arm"
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, uid)
        assert fetch.await_count == 1
        snapshot["categories"][0]["display_name"] = "Renamed arm"
        freezer.tick(timedelta(minutes=16))
        async_fire_time_changed(hass, dt_util.utcnow())
        await hass.async_block_till_done()
        assert fetch.await_count >= 2
        assert registry.async_get_entity_id("sensor", DOMAIN, uid) == entity_id
        steps_id = registry.async_get_entity_id("sensor", DOMAIN, config.unique_id + "_steps")
        with patch.object(config.runtime_data.client, "snapshot", side_effect=ApiError("Offline")):
            freezer.move_to("2026-11-05T23:00:01Z")
            async_fire_time_changed(hass, dt_util.utcnow())
            await hass.async_block_till_done()
            assert hass.states.get(steps_id).state == "unavailable"
        await hass.config_entries.async_unload(config.entry_id)
