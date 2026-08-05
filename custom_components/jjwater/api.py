"""API client for Jinjiang Water integration."""
import logging
from datetime import datetime
import aiohttp

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://wwt.jinjiangwater.com/jjapis"

class JJWaterAPI:
    """Jinjiang Water API Wrapper."""

    def __init__(self, session: aiohttp.ClientSession, token: str) -> None:
        """Initialize the API."""
        self._session = session
        # 保证 token 前缀正确
        if not token.startswith("Bearer "):
            self._token = f"Bearer {token}"
        else:
            self._token = token

    @property
    def headers(self) -> dict:
        """Get standard request headers."""
        return {
            "Authorization": self._token,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            "Origin": "https://wwt.jinjiangwater.com",
            "Referer": "https://wwt.jinjiangwater.com/mine/bill",
        }

    async def async_post(self, endpoint: str, data: dict) -> dict:
        """Send POST request to API."""
        url = f"{BASE_URL}/{endpoint}"
        try:
            async with self._session.post(url, headers=self.headers, data=data, timeout=15) as response:
                if response.status != 200:
                    _LOGGER.error("API call failed with status %s", response.status)
                    return {}
                res_json = await response.json()
                if res_json.get("code") == 200:
                    return res_json.get("data", {})
                _LOGGER.error("API responded with error: %s", res_json.get("msg"))
                return {}
        except Exception as err:
            _LOGGER.error("Error communicating with Jinjiang Water API: %s", err)
            return {}

    async def get_overview(self, user_kh: str) -> dict:
        """获取用户概览信息 (findKhSl)."""
        return await self.async_post("ysBase/findKhSl", {"USERB_KH": user_kh})

    async def get_daily_usage(self, user_kh: str, year_month: str = None) -> dict:
        """获取每日用水明细 (findEveryDayYsl)."""
        if not year_month:
            year_month = datetime.now().strftime("%Y%m")
        return await self.async_post(
            "ysBase/findEveryDayYsl",
            {"USERB_KH": user_kh, "YEAR_MONTH": year_month}
        )

    async def get_year_bill(self, user_kh: str, year: str = None) -> list:
        """获取年度账单列表 (findYearDz)."""
        if not year:
            year = datetime.now().strftime("%Y")
        res = await self.async_post(
            "ysBase/findYearDz",
            {"USERB_KH": user_kh, "DEBTL_YEAR": year}
        )
        return res if isinstance(res, list) else []
