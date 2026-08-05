"""DataUpdateCoordinator for Jinjiang Water."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import JJWaterAPI, JJWaterAPIError, JJWaterAuthError
from .const import DEFAULT_SCAN_INTERVAL_HOURS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class JJWaterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Jinjiang Water data."""

    def __init__(self, hass: HomeAssistant, api: JJWaterAPI, user_kh: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{user_kh}",
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL_HOURS),
        )
        self.api = api
        self.user_kh = str(user_kh)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            overview = await self.api.get_overview(self.user_kh)
            daily_data = await self.api.get_daily_usage(self.user_kh)
            year_bills = await self.api.get_year_bill(self.user_kh)

            daily_list = daily_data.get("everyDayYsl", [])
            latest_day = daily_list[-1] if daily_list else {}
            latest_bill = year_bills[-1] if year_bills else {}

            return {
                "overview": overview,
                "daily_list": daily_list,
                "latest_day": latest_day,
                "latest_bill": latest_bill,
                "zsl": daily_data.get("zsl", 0.0),
            }
        except JJWaterAuthError as err:
            raise UpdateFailed(f"身份验证失效，请重新配置 Token: {err}") from err
        except JJWaterAPIError as err:
            raise UpdateFailed(f"请求水务接口错误: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"未预期的数据刷新失败: {err}") from err
