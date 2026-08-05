"""DataUpdateCoordinator for Jinjiang Water."""
import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .api import JJWaterAPI

_LOGGER = logging.getLogger(__name__)

class JJWaterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Jinjiang Water data."""

    def __init__(self, hass: HomeAssistant, api: JJWaterAPI, user_kh: str) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"JJWater ({user_kh})",
            update_interval=timedelta(hours=2), # 水表数据更新频率不高，设为2小时
        )
        self.api = api
        self.user_kh = user_kh

    async def _async_update_data(self) -> dict:
        """Fetch data from API."""
        try:
            # 1. 获取概览
            overview = await self.api.get_overview(self.user_kh)
            # 2. 获取每日用量
            daily_data = await self.api.get_daily_usage(self.user_kh)
            # 3. 获取年度账单
            year_bills = await self.api.get_year_bill(self.user_kh)

            # 解析每日数据
            daily_list = daily_data.get("everyDayYsl", [])
            latest_day = daily_list[-1] if daily_list else {}

            # 解析最新账单 (取账单列表中最后一个月)
            latest_bill = year_bills[-1] if year_bills else {}

            return {
                "overview": overview,
                "daily_list": daily_list,
                "latest_day": latest_day,
                "latest_bill": latest_bill,
                "zsl": daily_data.get("zsl", 0.0),
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
