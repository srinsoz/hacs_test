"""Config flow for yxcv integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from yoctopuce.yocto_api import YAPI, YRefParam
from yoctopuce.yocto_colorledcluster import YColorLedCluster
from yoctopuce.yocto_network import YNetwork

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
    }
)


def validate_config(url: str) -> dict:
    _LOGGER.info("Use Yoctolib version %s" % YAPI.GetAPIVersion())
    errmsg = YRefParam()
    _LOGGER.debug("Register hub %s", url)
    yres = YAPI.TestHub(url, 5000, errmsg)
    if yres != YAPI.SUCCESS:
        return {"error": errmsg.value}

    yres = YAPI.RegisterHub(url, errmsg)
    if yres != YAPI.SUCCESS:
        return {"error": errmsg.value}
    leds = []
    _LOGGER.debug(
        "List color leds:",
    )
    l = YColorLedCluster.FirstColorLedCluster()
    while l is not None:
        hwid = l.get_hardwareId()
        _LOGGER.debug("- %s", hwid)
        leds.append(hwid)
        l = l.nextColorLedCluster()
    # fixme handle multiples hub and usb
    ynet = YNetwork.FirstNetwork()
    return {"leds": leds, "hub": ynet.get_logicalName()}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for yxcv."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                res = await self.hass.async_add_executor_job(
                    validate_config, user_input[CONF_URL]
                )
                if "error" in res:
                    errors["base"] = res["error"]
                elif len(res["leds"]) > 0:
                    return self.async_create_entry(title=res["hub"], data=user_input)
                else:
                    errors["base"] = "No ColorLed found on " + user_input[CONF_URL]
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
