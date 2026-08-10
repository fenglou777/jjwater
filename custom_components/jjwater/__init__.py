"""The Jinjiang Water integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JJWaterAPI
from .const import CONF_TOKEN, CONF_USER_KH, DOMAIN
from .coordinator import JJWaterCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jinjiang Water from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    user_kh = entry.data[CONF_USER_KH]
    # 优先使用 options 中的新 Token，没有则用初始创建时的 Token
    token = entry.options.get(CONF_TOKEN, entry.data[CONF_TOKEN])

    session = async_get_clientsession(hass)
    api = JJWaterAPI(session, token)

    coordinator = JJWaterCoordinator(hass, api, user_kh)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # 监听设置修改（如重新输入了新的 Token）
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
