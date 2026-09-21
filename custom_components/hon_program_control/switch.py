from __future__ import annotations
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

SWITCH_PARAMETERS = {
    "prewash": ("Prewash", "mdi:washing-machine"),
    "hygiene": ("Hygiene", "mdi:shield-check"),
    "anticrease": ("Anti-crease", "mdi:tshirt-crew"),
    "goodNight": ("Good Night", "mdi:weather-night"),
    "acquaplus": ("Aqua Plus", "mdi:water-plus"),
    "extraRinse1": ("Extra Rinse 1", "mdi:water-plus"),
    "extraRinse2": ("Extra Rinse 2", "mdi:water-plus"),
    "extraRinse3": ("Extra Rinse 3", "mdi:water-plus"),
}

async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ParameterSwitch(c, key, name, icon)
                        for key, (name, icon) in SWITCH_PARAMETERS.items()])

class ParameterSwitch(SwitchEntity):
    _attr_has_entity_name = True
    def __init__(self, controller, key, name, icon):
        self.controller = controller
        self.key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_{key}"
        self._remove_listener = None
    @property
    def device_info(self):
        return self.controller.device.device_info
    @property
    def available(self):
        return self.controller.parameter(self.key) is not None
    @property
    def is_on(self):
        return self.controller.parameter_value(self.key) == "1"
    async def async_turn_on(self, **kwargs):
        self.controller.set_parameter(self.key, "1")
    async def async_turn_off(self, **kwargs):
        self.controller.set_parameter(self.key, "0")
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._remove_listener = self.controller.add_listener(self.async_write_ha_state)
    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
        await super().async_will_remove_from_hass()
