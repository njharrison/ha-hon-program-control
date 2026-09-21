from __future__ import annotations
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SavePresetButton(controller),
        DeletePresetButton(controller),
        StartProgramButton(controller),
    ])

class BaseProgramButton(ButtonEntity):
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

class SavePresetButton(BaseProgramButton):
    _attr_name = "Save preset"
    _attr_icon = "mdi:content-save"
    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_save_preset"
    async def async_press(self):
        await self.controller.async_save_preset()

class DeletePresetButton(BaseProgramButton):
    _attr_name = "Delete preset"
    _attr_icon = "mdi:delete"
    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_delete_preset"
    @property
    def available(self):
        return self.controller.selected_preset is not None
    async def async_press(self):
        await self.controller.async_delete_preset()

class StartProgramButton(BaseProgramButton):
    _attr_name = "Start selected program"
    _attr_icon = "mdi:play"
    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_start"
    async def async_press(self):
        await self.controller.async_start()
