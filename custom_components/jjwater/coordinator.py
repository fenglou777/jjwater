"""晋江水务 数据更新协调器"""
from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import JJWaterAPI
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class JJWaterCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, token: str, accounts: list[str]) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL))
        self.api = JJWaterAPI(async_get_clientsession(hass), token)
        self.accounts = accounts

    async def _async_update_data(self) -> dict[str, dict]:
        data = {acc: await self.api.fetch_account_data(acc) for acc in self.accounts}
        if not any(data.values()):
            raise UpdateFailed("获取数据失败")
        return data
