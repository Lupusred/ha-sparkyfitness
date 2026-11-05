"""SparkyFitness for Home Assistant."""

from homeassistant.const import CONF_API_KEY, CONF_URL, Platform
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import SparkyClient
from .coordinator import SparkyCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry):
    # Dedicated cookie jar prevents an unrelated HA session changing user context.
    session = async_create_clientsession(hass, auto_cleanup=False)
    client = SparkyClient(session, entry.data[CONF_URL], entry.data[CONF_API_KEY])
    coordinator = SparkyCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        session.detach()
        raise
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_reload(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry.runtime_data.client.session.detach()
        return True
    return False
