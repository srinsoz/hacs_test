"""Platform for light integration."""

from __future__ import annotations

import logging
from pprint import pformat

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.const import CONF_NAME, CONF_URL
from homeassistant.core import HomeAssistant

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .yocto_api import *
from .yocto_colorledcluster import *

_LOGGER = logging.getLogger("yocto_led")

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Required(CONF_URL): cv.string,
    }
)


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
    """Representation of an Godox Light."""

    def __init__(self, light) -> None:
        """Initialize an GodoxLight."""
        _LOGGER.info(pformat(light))
        self._url = light["url"]
        self._name = light["name"]
        self._state = None
        self._brightness = None
        self._nb_leds = 2

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    async def async_setupYLib(self, hass: HomeAssistant) -> None:
        await hass.async_add_executor_job(self.setupYLib)

    def setupYLib(self) -> None:
        _LOGGER.info("Use Yoctolib version %s" % YAPI.GetAPIVersion())
        errmsg = YRefParam()
        _LOGGER.debug("Register hub %s", self._url)
        if YAPI.RegisterHub(self._url, errmsg) != YAPI.SUCCESS:
            _LOGGER.error("RegisterHub error" + errmsg.value)
            return
        self._leds = YColorLedCluster.FirstColorLedCluster()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        # if ATTR_BRIGHTNESS in kwargs:
        #    await self._leds.set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))
        if self._leds is not None and self._leds.isOnline():
            self._leds.rgb_move(0, self._nb_leds, 0xFFFFFF, 1000)
        else:
            _LOGGER.debug("Module not connected (check identification and USB cable)")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        # await self._leds.turn_off()
        if self._leds is not None and self._leds.isOnline():
            self._leds.rgb_move(0, self._nb_leds, 0, 1000)
        else:
            _LOGGER.debug("Module not connected (check identification and USB cable)")

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = False  # self._leds.is_on
        self._brightness = 0  # self._leds.brightness
