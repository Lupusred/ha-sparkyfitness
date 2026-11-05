"""Account-isolated polling and local calendar-day handling."""

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, InvalidAuth
from .const import CONF_INTERVAL, CONF_TIME_ZONE, DEFAULT_INTERVAL, DOMAIN
from .data import parse_snapshot


class SparkyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        super().__init__(
            hass,
            logging.getLogger(__name__),
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL)),
        )
        self.client = client
        self.user_id = entry.data["user_id"]
        self.zone = ZoneInfo(entry.options.get(CONF_TIME_ZONE, hass.config.time_zone))
        self.day = None
        self.write_lock = asyncio.Lock()

    def today(self):
        return datetime.now(self.zone).date().isoformat()

    async def _async_update_data(self):
        day = self.today()
        try:
            raw = await self.client.snapshot(day, self.user_id)
            data = parse_snapshot(raw)
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed(str(err)) from None
        except ApiError as err:
            raise UpdateFailed(str(err)) from None
        except (ValueError, TypeError, KeyError, AttributeError):
            raise UpdateFailed("Unexpected API data") from None
        self.day = day
        return data
