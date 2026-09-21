from __future__ import annotations
from homeassistant.components.number import NumberEntity, NumberMode
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DelayTimeNumber(c)])

class DelayTimeNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Delay Time"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = "min"
    _attr_mode = NumberMode.BOX
    def __init__(self, controller):
        self.controller = controller
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_delayTime"
        self._remove_listener = None
    @property
    def device_info(self):
        return self.controller.device.device_info
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
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._remove_listener = self.controller.add_listener(self.async_write_ha_state)
    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
        await super().async_will_remove_from_hass()
