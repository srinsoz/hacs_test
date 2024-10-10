from __future__ import annotations

from homeassistant.core import HomeAssistant


class Hub:
    """Dummy hub for Hello World example."""

    manufacturer = "Yoctopuce"

    def __init__(self, hass: HomeAssistant, url: str) -> None:
        """Init dummy hub."""
        self._url = url
        self._hass = hass
        self._leds = []
        self.online = True

    async def test_connection(self) -> bool:
        """Test connectivity to the Dummy hub is OK."""
        return True
