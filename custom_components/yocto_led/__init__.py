"""Yoctopuce Led Test"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .hub import Hub

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT]

type HubConfigEntry = ConfigEntry[Hub]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Set up Yoctopuce Color LEDs from a config entry."""

    entry.runtime_data = Hub(hass, entry.data["url"])

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: HubConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
