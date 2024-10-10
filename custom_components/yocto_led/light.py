"""Platform for light integration."""

from __future__ import annotations

import logging
from pprint import pformat

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import HomeAssistant

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import HubConfigEntry
from .hub import Hub
from .const import DOMAIN
from yoctopuce.yocto_api import *
from yoctopuce.yocto_colorledcluster import *

_LOGGER = logging.getLogger(__name__)


# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Required(CONF_URL): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yoctopuce Color LEDs from a config entry."""
    hub = config_entry.runtime_data

    new_devices = []
    for hwid in hub.leds:
        new_devices.append(YoctoColorLedLight(hub, hwid))
    if new_devices:
        async_add_entities(new_devices)

    return True


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Godox Light platform."""
    # Add devices
    _LOGGER.info(pformat(config))

    light = {"name": config[CONF_NAME], "url": config[CONF_URL]}
    yl = YoctoColorLedLight(light)
    await yl.async_setupYLib(hass)
    add_entities([yl])


class YoctoColorLedLight(LightEntity):
    """Representation of an Yocto-Color-V2 Light."""

    def __init__(self, hub: Hub, hwid: str) -> None:
        self._hub = hub
        self._name = hwid
        self._is_on = False
        self._color_mode = ColorMode.RGB
        self._rgb_color = (255, 255, 255)
        # self._hs_color = (255, 255)
        self._brightness = 0

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._is_on

    @property
    def color_mode(self):
        return self._color_mode

    @property
    def rgb_color(self):
        return self._rgb_color

    @property
    def brightness(self):
        return self._brightness

    @property
    def hs_color(self):
        return self._hs_color

    @property
    def supported_color_modes(self):
        return [ColorMode.RGB]

    @property
    def is_on(self):
        return self._is_on

    def set_on_off(self) -> None:
        if self._is_on:
            _LOGGER.debug(self._rgb_color)
            color = (
                (self._rgb_color[0] << 16)
                + (self._rgb_color[1] << 8)
                + self._rgb_color[2]
            )
            self._hub.set_color(self._name, color)
            self._is_on = True
        else:
            self._hub.set_color(self._name, 0)
            self._is_on = False

    def update_state_dbg(self) -> None:
        _LOGGER.info("update led status")
        if self._leds is not None and self._leds.isOnline():
            leds = self._leds.get_rgbColorArray(0, 1)
            if leds[0] != 0:
                self._is_on = True
            r = leds[0] >> 16
            g = (leds[0] >> 8) & 0xFF
            b = leds[0] & 0xFF
            self._rgb_color = (r, g, b)
            _LOGGER.info("update led status %x  to (%x %x %x)" % (leds[0], r, g, b))
        else:
            _LOGGER.warning("Module not connected (check identification and USB cable)")

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._is_on = True
        # Vérifier si un mode de couleur a été spécifié
        if ATTR_RGB_COLOR in kwargs:
            self._rgb_color = kwargs[ATTR_RGB_COLOR]
        if ATTR_HS_COLOR in kwargs:
            self._hs_color = kwargs[ATTR_HS_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        await self.hass.async_add_executor_job(self.set_on_off)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._is_on = False
        await self.hass.async_add_executor_job(self.set_on_off)

    # async def async_update(self) -> None:
    # await self.hass.async_add_executor_job(self.update_state)
