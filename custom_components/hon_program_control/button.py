from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SavePresetButton(controller),
        StartProgramButton(controller),
    ])


class BaseProgramButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, controller):
        self.controller = controller

    @property
    def device_info(self):
        return self.controller.device.device_info


class SavePresetButton(BaseProgramButton):
    _attr_name = "Save to preset"
    _attr_icon = "mdi:content-save"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = (
            f"{controller.entry.data['mac']}_program_control_save_preset"
        )

    async def async_press(self) -> None:
        await self.controller.async_save_preset()


class StartProgramButton(BaseProgramButton):
    _attr_name = "Start selected program"
    _attr_icon = "mdi:play"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = (
            f"{controller.entry.data['mac']}_program_control_start"
        )

    async def async_press(self) -> None:
        await self.controller.async_start()
