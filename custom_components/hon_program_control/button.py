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
    async_add_entities([StartProgramButton(controller)])


class StartProgramButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Start selected program"
    _attr_icon = "mdi:play"

    def __init__(self, controller):
        self.controller = controller
        self._attr_unique_id = (
            f"{controller.entry.data['mac']}_program_control_start"
        )

    @property
    def device_info(self):
        return self.controller.device.device_info

    async def async_press(self) -> None:
        await self.controller.async_start()
