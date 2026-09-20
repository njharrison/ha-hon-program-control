from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, HON_DOMAIN, CONF_MAC, CONF_HON_ENTRY


def _washing_machines(hass):
    found = {}
    data = hass.data.get(HON_DOMAIN, {})
    for hon_key, connection in data.items():
        if hon_key == "service_registry" or not hasattr(connection, "_coordinator_dict"):
            continue
        for mac, coordinator in connection._coordinator_dict.items():
            device = getattr(coordinator, "device", None)
            if device is None or "startProgram" not in getattr(device, "commands", {}):
                continue
            appliance = getattr(device, "appliance", {})
            type_name = str(appliance.get("applianceTypeName", "")).strip().lower()
            # hOn commonly reports a washing machine as "WM"; accept descriptive
            # names too, but don't expose startProgram controls for other appliances.
            if type_name != "wm" and "wash" not in type_name:
                continue
            name = (
                getattr(device, "name", None)
                or appliance.get("nickName")
                or "Washing Machine"
            )
            found[f"{hon_key}|{mac}"] = (str(name), hon_key, mac)
    return found


class HonProgramControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        machines = _washing_machines(self.hass)
        if not machines:
            return self.async_abort(reason="no_washing_machines")

        if user_input is not None:
            key = user_input["washing_machine"]
            name, hon_key, mac = machines[key]
            await self.async_set_unique_id(mac)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"{name} Program Control",
                data={CONF_MAC: mac, CONF_HON_ENTRY: hon_key},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("washing_machine"): vol.In({
                    key: value[0] for key, value in machines.items()
                })
            }),
        )
