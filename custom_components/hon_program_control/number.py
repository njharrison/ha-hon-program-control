from __future__ import annotations
from homeassistant.components.number import NumberEntity, NumberMode
from .const import DOMAIN

EXTRA_RINSE_KEYS = ("extraRinse1", "extraRinse2", "extraRinse3")

async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DelayTimeNumber(c), ExtraRinsesNumber(c)])

class BaseProgramNumber(NumberEntity):
    _attr_has_entity_name = True
    def __init__(self, controller):
        self.controller = controller
        self._remove_listener = None
    @property
    def device_info(self):
        return self.controller.device.device_info
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._remove_listener = self.controller.add_listener(self.async_write_ha_state)
    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
        await super().async_will_remove_from_hass()

class DelayTimeNumber(BaseProgramNumber):
    _attr_name = "Delay Time"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = "min"
    _attr_mode = NumberMode.BOX
    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_delayTime"
    @property
    def available(self):
        return self.controller.parameter("delayTime") is not None
    @property
    def native_min_value(self):
        p = self.controller.parameter("delayTime")
        return float(getattr(p, "min", 0))
    @property
    def native_max_value(self):
        p = self.controller.parameter("delayTime")
        return float(getattr(p, "max", 0))
    @property
    def native_step(self):
        p = self.controller.parameter("delayTime")
        return float(getattr(p, "step", 1))
    @property
    def native_value(self):
        v = self.controller.parameter_value("delayTime")
        return None if v is None else float(v)
    async def async_set_native_value(self, value):
        self.controller.set_parameter("delayTime", str(int(value)))

class ExtraRinsesNumber(BaseProgramNumber):
    _attr_name = "Extra Rinses"
    _attr_icon = "mdi:water-plus"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_step = 1
    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_extra_rinses"
    @property
    def _supported_keys(self):
        return [key for key in EXTRA_RINSE_KEYS if self.controller.parameter(key) is not None]
    @property
    def available(self):
        return bool(self._supported_keys)
    @property
    def native_max_value(self):
        return float(len(self._supported_keys))
    @property
    def native_value(self):
        if not self._supported_keys:
            return None
        return float(sum(
            self.controller.parameter_value(key) == "1"
            for key in self._supported_keys
        ))
    async def async_set_native_value(self, value):
        count = int(value)
        for index, key in enumerate(self._supported_keys):
            self.controller.set_parameter(key, "1" if index < count else "0")
