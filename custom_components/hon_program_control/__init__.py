from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, PLATFORMS, HON_DOMAIN, CONF_MAC, CONF_HON_ENTRY

STORAGE_VERSION = 2
PRESET_NAMES = ["Linen", "Reds", "Greys", "Whites", "Delicate"]


def _hon_connections(hass: HomeAssistant):
    data = hass.data.get(HON_DOMAIN, {})
    return {
        key: value
        for key, value in data.items()
        if key != "service_registry" and hasattr(value, "_coordinator_dict")
    }


def get_hon_device(hass: HomeAssistant, entry: ConfigEntry):
    connections = _hon_connections(hass)
    hon_key = entry.data.get(CONF_HON_ENTRY)
    connection = connections.get(hon_key)

    if connection is None and len(connections) == 1:
        connection = next(iter(connections.values()))

    if connection is None:
        return None

    coordinator = connection._coordinator_dict.get(entry.data[CONF_MAC])
    if coordinator is None:
        return None
    return getattr(coordinator, "device", None)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    device = get_hon_device(hass, entry)
    if device is None or "startProgram" not in device.commands:
        return False

    controller = ProgramController(hass, entry, device)
    await controller.async_initialize()
    hass.data[DOMAIN][entry.entry_id] = controller
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return ok


class ProgramController:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, device):
        self.hass = hass
        self.entry = entry
        self.device = device
        self.listeners = set()
        self.recent_programs = []
        self.presets = {}
        self.selected_preset = PRESET_NAMES[0]
        self.store = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.{entry.data[CONF_MAC]}.settings",
        )

        command = self.command
        programs = list(command.get_programs().keys())
        self.program = programs[0] if programs else None
        if self.program is not None:
            command.set_program(self.program)

    async def async_initialize(self):
        stored = await self.store.async_load() or {}
        valid = set(self.programs)
        self.recent_programs = [
            program
            for program in stored.get("recent_programs", [])
            if program in valid
        ][:3]
        self.presets = {
            name: preset
            for name, preset in stored.get("presets", {}).items()
            if name in PRESET_NAMES and preset.get("program") in valid
        }
        selected = stored.get("selected_preset")
        if selected in PRESET_NAMES:
            self.selected_preset = selected

    async def _async_save_settings(self):
        await self.store.async_save({
            "recent_programs": self.recent_programs,
            "presets": self.presets,
            "selected_preset": self.selected_preset,
        })

    @property
    def command(self):
        return self.device.commands["startProgram"]

    @property
    def programs(self):
        return list(self.command.get_programs().keys())

    @property
    def parameters(self):
        return self.command.parameters

    def select_program(self, program: str):
        if program not in self.programs:
            raise ValueError(f"Unknown program: {program}")
        self.command.set_program(program)
        self.program = program
        self._notify()

    def parameter(self, key: str):
        return self.parameters.get(key)

    @staticmethod
    def _options(parameter):
        if parameter is None:
            return []
        values = getattr(parameter, "values", None)
        if values is not None:
            return [str(v) for v in values]

        minimum = getattr(parameter, "min", None)
        maximum = getattr(parameter, "max", None)
        step = getattr(parameter, "step", None)
        if minimum is None or maximum is None or not step:
            return []

        result = []
        value = minimum
        while value <= maximum and len(result) < 500:
            result.append(str(value))
            value += step
        return result

    def parameter_options(self, key: str):
        return self._options(self.parameter(key))

    def parameter_value(self, key: str):
        parameter = self.parameter(key)
        if parameter is None:
            return None
        return str(parameter.value)

    def set_parameter(self, key: str, value: str):
        parameter = self.parameter(key)
        if parameter is None:
            raise ValueError(f"Parameter {key} is not available for {self.program}")
        parameter.value = value
        self._notify()

    async def async_select_preset(self, name: str):
        if name not in PRESET_NAMES:
            raise ValueError(f"Unknown preset: {name}")
        self.selected_preset = name
        preset = self.presets.get(name)
        if preset is not None:
            self.select_program(preset["program"])
            for key, value in preset.get("parameters", {}).items():
                parameter = self.parameter(key)
                if parameter is not None:
                    try:
                        parameter.value = value
                    except ValueError:
                        pass
        await self._async_save_settings()
        self._notify()

    async def async_save_preset(self):
        if self.program is None:
            raise ValueError("No program selected")
        self.presets[self.selected_preset] = {
            "program": self.program,
            "parameters": {
                key: parameter.value
                for key, parameter in self.parameters.items()
            },
        }
        await self._async_save_settings()
        self._notify()

    async def async_start(self):
        if self.program is None:
            raise ValueError("No program selected")

        command = self.device.start_command(self.program, {
            key: parameter.value for key, parameter in self.parameters.items()
        })
        result = await command.send()

        if result:
            self.recent_programs = [
                self.program,
                *[p for p in self.recent_programs if p != self.program],
            ][:3]
            await self._async_save_settings()
            self._notify()

        return result

    def add_listener(self, callback):
        self.listeners.add(callback)
        return lambda: self.listeners.discard(callback)

    def _notify(self):
        for callback in list(self.listeners):
            callback()
