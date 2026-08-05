"""The Jinjiang Water integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JJWaterAPI
from .const import CONF_TOKEN, CONF_USER_KH, DOMAIN
from .coordinator import JJWaterCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jinjiang Water from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    user_kh = entry.data[CONF_USER_KH]
    token = entry.data[CONF_TOKEN]

    session = async_get_clientsession(hass)
    api = JJWaterAPI(session, token)

    coordinator = JJWaterCoordinator(hass, api, user_kh)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
