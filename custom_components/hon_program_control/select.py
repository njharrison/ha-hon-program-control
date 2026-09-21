from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from . import PRESET_NAMES


PARAMETERS = {
    "temp": ("Temperature", "mdi:thermometer"),
    "spinSpeed": ("Spin Speed", "mdi:rotate-right"),
    "dirtyLevel": ("Soil Level", "mdi:brightness-6"),
}


def program_label(program: str) -> str:
    """Turn an hOn program ID into a human-friendly display label."""
    if program.lower().startswith("iot_"):
        program = program[4:]
    return " ".join(word.capitalize() for word in program.split("_"))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = hass.data[DOMAIN][entry.entry_id]
    entities = [PresetSelect(controller), ProgramSelect(controller)]
    entities.extend(
        ParameterSelect(controller, key, name, icon)
        for key, (name, icon) in PARAMETERS.items()
    )
    async_add_entities(entities)


class BaseProgramSelect(SelectEntity):
    _attr_has_entity_name = True

    def __init__(self, controller):
        self.controller = controller
        self._remove_listener = None

    @property
    def device_info(self):
        return self.controller.device.device_info

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._remove_listener = self.controller.add_listener(
            self.async_write_ha_state
        )

    async def async_will_remove_from_hass(self):
        if self._remove_listener:
            self._remove_listener()
        await super().async_will_remove_from_hass()


class PresetSelect(BaseProgramSelect):
    _attr_name = "Preset"
    _attr_icon = "mdi:washing-machine-alert"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_preset"

    @property
    def options(self):
        return PRESET_NAMES

    @property
    def current_option(self):
        return self.controller.selected_preset

    @property
    def extra_state_attributes(self):
        return {
            "saved": sorted(self.controller.presets.keys()),
            "configured": self.controller.selected_preset in self.controller.presets,
        }

    async def async_select_option(self, option: str) -> None:
        await self.controller.async_select_preset(option)


class ProgramSelect(BaseProgramSelect):
    _attr_name = "Program"
    _attr_icon = "mdi:washing-machine"

    def __init__(self, controller):
        super().__init__(controller)
        self._attr_unique_id = f"{controller.entry.data['mac']}_program_control_program"

    @property
    def _program_labels(self):
        return {program_label(program): program for program in self.controller.programs}

    @property
    def options(self):
        labels = self._program_labels
        recent_labels = [
            program_label(program)
            for program in self.controller.recent_programs
            if program_label(program) in labels
        ]
        recent_set = set(recent_labels)
        remaining = sorted(
            (label for label in labels if label not in recent_set),
            key=str.casefold,
        )
        return recent_labels + remaining

    @property
    def current_option(self):
        if self.controller.program is None:
            return None
        return program_label(self.controller.program)

    async def async_select_option(self, option: str) -> None:
        program = self._program_labels.get(option)
        if program is None:
            raise ValueError(f"Unknown program label: {option}")
        self.controller.select_program(program)


class ParameterSelect(BaseProgramSelect):
    def __init__(self, controller, key, name, icon):
        super().__init__(controller)
        self.key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = (
            f"{controller.entry.data['mac']}_program_control_{key}"
        )

    @property
    def available(self):
        return bool(self.controller.parameter_options(self.key))

    @property
    def options(self):
        options = self.controller.parameter_options(self.key)
        if self.key == "spinSpeed":
            try:
                options = sorted(options, key=lambda value: float(value))
            except (TypeError, ValueError):
                pass
        return options or ["Unavailable"]

    @property
    def current_option(self):
        value = self.controller.parameter_value(self.key)
        if value is None:
            return "Unavailable"
        return value

    async def async_select_option(self, option: str) -> None:
        if option == "Unavailable":
            return
        self.controller.set_parameter(self.key, option)
