"""Sensors discovered from actual responses, including user-defined categories."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

CLASSES = {
    "kg": SensorDeviceClass.WEIGHT,
    "g": SensorDeviceClass.WEIGHT,
    "mg": SensorDeviceClass.WEIGHT,
    "cm": SensorDeviceClass.DISTANCE,
    "kcal": SensorDeviceClass.ENERGY,
    "s": SensorDeviceClass.DURATION,
    "min": SensorDeviceClass.DURATION,
    "h": SensorDeviceClass.DURATION,
    "mL": SensorDeviceClass.VOLUME,
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    known = set()

    @callback
    def discover():
        new = set(coordinator.data or {}) - known
        async_add_entities([SparkySensor(coordinator, entry, key) for key in sorted(new)])
        known.update(new)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))

    last_calendar_day = coordinator.today()

    async def check_day(now):
        nonlocal last_calendar_day
        today = coordinator.today()
        if last_calendar_day != today:
            last_calendar_day = today
            # Invalidate yesterday immediately, even if the new request fails.
            coordinator.async_update_listeners()
            await coordinator.async_request_refresh()

    # Minute boundary also supports user-selected zones different from HA's zone.
    entry.async_on_unload(async_track_time_change(hass, check_day, second=0))


class SparkySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self.key = key
        reading = coordinator.data[key]
        self._daily = reading.daily
        self._attr_unique_id = f"{entry.unique_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=entry.title,
            manufacturer="SparkyFitness",
            model="REST API account",
        )
        if key.startswith("custom_"):
            self._attr_name = reading.name
        else:
            self._attr_translation_key = key
        self._attr_native_unit_of_measurement = reading.unit
        if reading.numeric:
            self._attr_state_class = (
                None if reading.unit in ("kcal", "mL") else SensorStateClass.MEASUREMENT
            )
            self._attr_device_class = CLASSES.get(reading.unit)

    @property
    def available(self):
        return (
            super().available
            and self.key in (self.coordinator.data or {})
            and (not self._daily or self.coordinator.day == self.coordinator.today())
        )

    @property
    def native_value(self):
        reading = (self.coordinator.data or {}).get(self.key)
        return reading.value if reading else None

    @property
    def extra_state_attributes(self):
        reading = (self.coordinator.data or {}).get(self.key)
        if not reading:
            return {}
        return {
            "measurement_date": reading.date or (self.coordinator.day if reading.daily else None)
        }

    @callback
    def _handle_coordinator_update(self):
        reading = (self.coordinator.data or {}).get(self.key)
        if reading and self.key.startswith("custom_"):
            self._daily = reading.daily
            self._attr_name = reading.name
            self._attr_native_unit_of_measurement = reading.unit
            self._attr_state_class = (
                SensorStateClass.MEASUREMENT
                if reading.numeric and reading.unit not in ("kcal", "mL")
                else None
            )
            self._attr_device_class = CLASSES.get(reading.unit) if reading.numeric else None
        super()._handle_coordinator_update()
