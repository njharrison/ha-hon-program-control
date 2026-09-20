from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, HON_DOMAIN, CONF_MAC, CONF_HON_ENTRY


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

    # Fallback for an hOn entry whose unique_id changed.
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

    hass.data[DOMAIN][entry.entry_id] = ProgramController(hass, entry, device)
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

        command = self.command
        programs = list(command.get_programs().keys())
        self.program = programs[0] if programs else None
        if self.program is not None:
            command.set_program(self.program)

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
        # Guard against malformed ranges.
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

    async def async_start(self):
        if self.program is None:
            raise ValueError("No program selected")
        # start_command applies current context and preserves the values selected
        # on the current program before sending the existing hOn command.
        command = self.device.start_command(self.program, {
            key: parameter.value for key, parameter in self.parameters.items()
        })
        await command.send()

    def add_listener(self, callback):
        self.listeners.add(callback)
        return lambda: self.listeners.discard(callback)

    def _notify(self):
        for callback in list(self.listeners):
            callback()
