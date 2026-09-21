from __future__ import annotations
from homeassistant.components.text import TextEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    c = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PresetNameText(c)])

class PresetNameText(TextEntity):
    _attr_has_entity_name = True
    _attr_name = "Preset Name"
    _attr_icon = "mdi:form-textbox"
    _attr_native_min = 1
    _attr_native_max = 64
    def __init__(self, controller):
        self.controller = controller
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_preset_name"
        self._remove_listener = None
    @property
    def device_info(self):
        return self.controller.device.device_info
    @property
    def native_value(self):
        return self.controller.preset_name
    async def async_set_value(self, value):
        self.controller.set_preset_name(value)
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._remove_listener = self.controller.add_listener(self.async_write_ha_state)
    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
        await super().async_will_remove_from_hass()
