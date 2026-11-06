"""Direct editing of today's body measurements through the guarded write service."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ENABLE_WRITES, DOMAIN

FIELDS = {
    "weight": (0.1, 999.99, 0.01, "kg"),
    "neck": (0.1, 300, 0.1, "cm"),
    "waist": (0.1, 500, 0.1, "cm"),
    "hips": (0.1, 500, 0.1, "cm"),
    "height": (1, 300, 0.1, "cm"),
    "body_fat_percentage": (0, 100, 0.1, "%"),
    "muscle_mass_kg": (0, 999.99, 0.01, "kg"),
    "bone_mass_kg": (0, 999.99, 0.01, "kg"),
    "body_water_percentage": (0, 100, 0.1, "%"),
    "steps": (0, 1000000, 1, None),
    "resting_heart_rate": (1, 300, 1, "bpm"),
    "bmr": (600, 6000, 1, "kcal"),
}


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SparkyNumber(entry, key) for key in FIELDS])


class SparkyNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(self, entry, key):
        super().__init__(entry.runtime_data)
        self.entry = entry
        self.key = key
        self._attr_unique_id = f"{entry.unique_id}_write_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.unique_id)})
        (
            self._attr_native_min_value,
            self._attr_native_max_value,
            self._attr_native_step,
            self._attr_native_unit_of_measurement,
        ) = FIELDS[key]

    @property
    def available(self):
        return super().available and self.entry.options.get(CONF_ENABLE_WRITES, False)

    @property
    def native_value(self):
        reading = (self.coordinator.data or {}).get(self.key)
        if reading and (not reading.daily or self.coordinator.day == self.coordinator.today()):
            return reading.value
        return None

    async def async_set_native_value(self, value):
        # Forward the original user context: the existing admin check still applies.
        # No optimistic state or retry; only the server refresh updates the value.
        await self.hass.services.async_call(
            DOMAIN,
            "set_body_measurements",
            {"config_entry_id": self.entry.entry_id, self.key: value},
            blocking=True,
            context=self._context,
        )
