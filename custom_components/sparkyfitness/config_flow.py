"""UI configuration, account verification, options and key renewal."""

from hashlib import sha256
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import ApiError, InvalidAuth, SparkyClient, normalize_url
from .const import CONF_ENABLE_WRITES, CONF_INTERVAL, CONF_TIME_ZONE, DEFAULT_INTERVAL, DOMAIN


def account_id(url, user_id):
    return sha256(f"{url}|{user_id}".encode()).hexdigest()


class SparkyFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            session = async_create_clientsession(
                self.hass, auto_cleanup=False, cookie_jar=aiohttp.DummyCookieJar()
            )
            try:
                url = normalize_url(user_input[CONF_URL])
                key = user_input[CONF_API_KEY].strip()
                if not key:
                    raise InvalidAuth("Empty key")
                user_id = await SparkyClient(session, url, key).identity()
                await self.async_set_unique_id(account_id(url, user_id))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"SparkyFitness {user_id[:8]}",
                    data={CONF_URL: url, CONF_API_KEY: key, "user_id": user_id},
                )
            except ValueError:
                errors["base"] = "invalid_url"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            finally:
                session.detach()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): str,
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input is not None:
            entry = self._get_reauth_entry()
            session = async_create_clientsession(
                self.hass, auto_cleanup=False, cookie_jar=aiohttp.DummyCookieJar()
            )
            try:
                key = user_input[CONF_API_KEY].strip()
                user_id = await SparkyClient(session, entry.data[CONF_URL], key).identity()
                if user_id != entry.data["user_id"]:
                    errors["base"] = "wrong_account"
                else:
                    return self.async_update_reload_and_abort(
                        entry, data_updates={CONF_API_KEY: key}
                    )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            finally:
                session.detach()
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        errors = {}
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            session = async_create_clientsession(
                self.hass, auto_cleanup=False, cookie_jar=aiohttp.DummyCookieJar()
            )
            try:
                key = user_input[CONF_API_KEY].strip()
                if not key:
                    raise InvalidAuth("Empty key")
                user_id = await SparkyClient(session, entry.data[CONF_URL], key).identity()
                if user_id != entry.data["user_id"]:
                    errors["base"] = "wrong_account"
                else:
                    return self.async_update_reload_and_abort(
                        entry, data_updates={CONF_API_KEY: key}
                    )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            finally:
                session.detach()
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SparkyOptions()


class SparkyOptions(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                ZoneInfo(user_input[CONF_TIME_ZONE])
            except (ZoneInfoNotFoundError, ValueError):
                errors["base"] = "invalid_timezone"
            else:
                return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ENABLE_WRITES,
                        default=self.config_entry.options.get(CONF_ENABLE_WRITES, False),
                    ): bool,
                    vol.Required(
                        CONF_INTERVAL,
                        default=self.config_entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
                    vol.Required(
                        CONF_TIME_ZONE,
                        default=self.config_entry.options.get(
                            CONF_TIME_ZONE, self.hass.config.time_zone
                        ),
                    ): str,
                }
            ),
            errors=errors,
        )
