from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from yoctopuce.yocto_api import YAPI, YRefParam
from yoctopuce.yocto_colorledcluster import YColorLedCluster

_LOGGER = logging.getLogger(__name__)


class Hub:
    """Dummy hub for Hello World example."""

    manufacturer = "Yoctopuce"

    def __init__(self, hass: HomeAssistant, url: str) -> None:
        """Init dummy hub."""
        self._url = url
        self._hass = hass
        self.leds = []
        self.online = True

    async def test_connection(self) -> bool:
        return await self._hass.async_add_executor_job(self.setupYLib)

    def setupYLib(self) -> bool:
        _LOGGER.info("Use Yoctolib version %s" % YAPI.GetAPIVersion())
        errmsg = YRefParam()
        _LOGGER.debug("Register hub %s", self._url)

        res = YAPI.RegisterHub(self._url, errmsg)
        if res == YAPI.DOUBLE_ACCES:
            _LOGGER.warning("RegisterHub warning :" + errmsg.value)
        elif res != YAPI.SUCCESS:
            _LOGGER.error("RegisterHub error" + errmsg.value)
            return False
        l: YColorLedCluster | None = YColorLedCluster.FirstColorLedCluster()
        while l is not None:
            hwid = l.get_hardwareId()
            self.leds.append(hwid)
            l = l.nextColorLedCluster()
        self.online = True
        return True

    def set_color(self, hwid: str, rgb_color) -> None:
        yled = YColorLedCluster.FindColorLedCluster(hwid)
        if yled.isOnline():
            nbled = yled.get_activeLedCount()
            _LOGGER.debug("Set %s to color 0x%x" % (hwid, rgb_color))
            yled.rgb_move(0, nbled, rgb_color, 1000)
        else:
            _LOGGER.warning("Module %s not offline" % hwid)
