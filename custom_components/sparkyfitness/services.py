"""Explicit admin actions; no reverse syncing of derived sensor states."""

from datetime import date, datetime
from math import isfinite
from uuid import UUID

import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import SupportsResponse, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.service import async_register_admin_service

from .api import ApiError, WriteUncertain
from .const import CONF_ENABLE_WRITES, DOMAIN


def bounded(minimum, maximum, *, integer=False):
    def validate(value):
        if isinstance(value, bool):
            raise vol.Invalid("A numeric value is required")
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise vol.Invalid("A numeric value is required") from None
        if (
            not isfinite(value)
            or not minimum <= value <= maximum
            or (integer and not value.is_integer())
        ):
            raise vol.Invalid("Numeric value outside the supported range")
        return int(value) if integer else value

    return validate


def uuid_value(value):
    try:
        return str(UUID(str(value)))
    except ValueError:
        raise vol.Invalid("A valid UUID is required") from None


def day_value(value):
    try:
        if not isinstance(value, str) or len(value) != 10:
            raise ValueError
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise vol.Invalid("Use a valid YYYY-MM-DD date") from None


def timestamp(value):
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError
        return dt.isoformat()
    except (ValueError, TypeError):
        raise vol.Invalid("Use an ISO timestamp with an explicit UTC offset") from None


BODY_FIELDS = {
    "weight": bounded(0.1, 999.99),
    "neck": bounded(0.1, 300),
    "waist": bounded(0.1, 500),
    "hips": bounded(0.1, 500),
    "height": bounded(1, 300),
    "body_fat_percentage": bounded(0, 100),
    "muscle_mass_kg": bounded(0, 999.99),
    "bone_mass_kg": bounded(0, 999.99),
    "body_water_percentage": bounded(0, 100),
    "steps": bounded(0, 1000000, integer=True),
    "resting_heart_rate": bounded(1, 300),
    "bmr": bounded(600, 6000),
}
COMMON = {vol.Required("config_entry_id"): str, vol.Optional("date"): day_value}
SCHEMAS = {
    "set_body_measurements": vol.Schema(
        {**COMMON, **{vol.Optional(k): v for k, v in BODY_FIELDS.items()}}
    ),
    "record_custom_measurement": vol.Schema(
        {
            **COMMON,
            vol.Required("category_id"): uuid_value,
            vol.Required("value"): vol.Any(str, int, float),
            vol.Optional("hour"): bounded(0, 23, integer=True),
        }
    ),
    "record_water": vol.Schema(
        {
            **COMMON,
            vol.Required("amount_ml"): bounded(1, 20000),
            vol.Required("record_id"): vol.All(str, vol.Match(r"^[A-Za-z0-9_-]{1,64}$")),
        }
    ),
    "record_sleep": vol.Schema(
        {
            **COMMON,
            vol.Required("bedtime"): timestamp,
            vol.Required("wake_time"): timestamp,
        }
    ),
    "log_food": vol.Schema(
        {
            **COMMON,
            vol.Required("food_id"): uuid_value,
            vol.Required("variant_id"): uuid_value,
            vol.Required("quantity"): bounded(0.001, 100000),
            vol.Required("unit"): vol.All(str, vol.Length(min=1, max=32)),
            vol.Required("meal_type"): vol.All(str, vol.Length(min=1, max=80)),
        }
    ),
    "log_exercise": vol.Schema(
        {
            **COMMON,
            vol.Required("exercise_id"): uuid_value,
            vol.Required("duration_minutes"): bounded(0.01, 1440),
            vol.Required("calories_burned"): bounded(0, 30000),
        }
    ),
}


async def build_write(service, data, coordinator, entry):
    """Return a whitelisted endpoint and payload. Never forward arbitrary input."""
    day = data.get("date", coordinator.today())
    if day > coordinator.today():
        raise ServiceValidationError("Future dates are not supported")
    if service == "set_body_measurements":
        fields = {k: data[k] for k in BODY_FIELDS if k in data}
        if not fields:
            raise ServiceValidationError("Provide at least one measured value")
        return "measurements/check-in", {"entry_date": day, **fields}
    if service == "record_custom_measurement":
        # Fetch the current account's catalogue, never trust client-supplied ownership.
        categories = await coordinator.client.get("measurements/custom-categories")
        if not isinstance(categories, list) or any(not isinstance(c, dict) for c in categories):
            raise ServiceValidationError("Invalid measurement category catalogue")
        category = next((c for c in categories if c.get("id") == data["category_id"]), None)
        if category is None:
            raise ServiceValidationError("Category does not belong to this account")
        frequency = category.get("frequency")
        if frequency not in ("Daily", "Hourly", "All", "Unlimited"):
            raise ServiceValidationError("Unsupported category frequency")
        value = data["value"]
        if category.get("data_type") == "text":
            if not isinstance(value, str) or not value.strip() or len(value) > 255:
                raise ServiceValidationError("Text measurement must contain 1–255 characters")
        else:
            try:
                value = bounded(-1e9, 1e9, integer=category.get("data_type") == "integer")(value)
            except vol.Invalid:
                raise ServiceValidationError("Invalid numeric measurement") from None
        payload = {
            "category_id": category["id"],
            "value": value,
            "entry_date": day,
            "source": "Home Assistant",
        }
        if frequency == "Hourly":
            if "hour" not in data:
                raise ServiceValidationError("Hourly categories require hour (0–23)")
            payload["entry_hour"] = data["hour"]
        elif "hour" in data:
            raise ServiceValidationError("Hour is only valid for hourly categories")
        return "measurements/custom-entries", payload
    if service == "record_water":
        # Stable source ID updates only this integration's sample, never a day's total.
        return "measurements/health-data", [
            {
                "type": "water",
                "value": data["amount_ml"],
                "unit": "ml",
                "date": day,
                "source": "Home Assistant",
                "source_id": f"ha-sparkyfitness:{entry.unique_id}:{data['record_id']}",
            }
        ]
    if service == "record_sleep":
        bedtime = datetime.fromisoformat(data["bedtime"])
        wake = datetime.fromisoformat(data["wake_time"])
        seconds = (wake - bedtime).total_seconds()
        if not 0 < seconds <= 86400 or wake > datetime.now(wake.tzinfo):
            raise ServiceValidationError("Sleep must end in the past and last at most 24 hours")
        wake_day = wake.astimezone(coordinator.zone).date().isoformat()
        if "date" in data and day != wake_day:
            raise ServiceValidationError(
                "Sleep date must match the wake date in the configured time zone"
            )
        return "sleep/manual_entry", {
            "entry_date": wake_day,
            "bedtime": bedtime.isoformat(),
            "wake_time": wake.isoformat(),
            "duration_in_seconds": int(seconds),
            "record_timezone": str(coordinator.zone),
        }
    if service == "log_food":
        return "food-entries", {
            "entry_date": day,
            **{k: data[k] for k in ("food_id", "variant_id", "quantity", "unit", "meal_type")},
        }
    if service == "log_exercise":
        return "exercise-entries", {
            "entry_date": day,
            **{k: data[k] for k in ("exercise_id", "duration_minutes", "calories_burned")},
        }
    raise ServiceValidationError("Unsupported action")


@callback
def async_register_services(hass):
    """Register once; handlers resolve the current loaded entry on every call."""

    async def handle(call):
        entry = hass.config_entries.async_get_entry(call.data["config_entry_id"])
        if entry is None or entry.domain != DOMAIN or entry.state != ConfigEntryState.LOADED:
            raise ServiceValidationError("Select a loaded SparkyFitness account")
        if not entry.options.get(CONF_ENABLE_WRITES, False):
            raise ServiceValidationError(
                "Enable write access in this account's integration options first"
            )
        coordinator = entry.runtime_data
        async with coordinator.write_lock:
            # An entry may have unloaded or write access may have changed while queued.
            if entry.state != ConfigEntryState.LOADED or not entry.options.get(
                CONF_ENABLE_WRITES, False
            ):
                raise ServiceValidationError("This account is no longer available for writing")
            try:
                if await coordinator.client.identity() != coordinator.user_id:
                    raise ServiceValidationError("API key belongs to a different account")
                path, payload = await build_write(call.service, call.data, coordinator, entry)
                result = await coordinator.client.write(path, payload, coordinator.user_id)
                if not isinstance(result, dict):
                    raise WriteUncertain(
                        "Write response invalid; inspect SparkyFitness before retrying"
                    )
                if path == "measurements/health-data":
                    processed = result.get("processed")
                    if (
                        result.get("errors")
                        or result.get("skipped")
                        or not isinstance(processed, list)
                        or len(processed) != 1
                        or not isinstance(processed[0], dict)
                        or processed[0].get("status") != "success"
                    ):
                        raise WriteUncertain(
                            "Write not confirmed; inspect SparkyFitness before retrying"
                        )
            except ApiError as err:
                raise ServiceValidationError(str(err)) from None
            # A successful write must not appear failed just because refresh failed.
            await coordinator.async_refresh()
            return {"saved": True, "refresh_successful": coordinator.last_update_success}

    for name, schema in SCHEMAS.items():
        if not hass.services.has_service(DOMAIN, name):
            async_register_admin_service(
                hass,
                DOMAIN,
                name,
                handle,
                schema=schema,
                supports_response=SupportsResponse.OPTIONAL,
            )
