"""API client for Jinjiang Water integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp

from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)


class JJWaterAuthError(Exception):
    """Exception raised when authentication fails."""


class JJWaterAPIError(Exception):
    """Exception raised when API request fails."""


class JJWaterAPI:
    """Jinjiang Water API Wrapper."""

    def __init__(self, session: aiohttp.ClientSession, token: str) -> None:
        """Initialize the API client."""
        self._session = session
        self._token = token if token.startswith("Bearer ") else f"Bearer {token}"

    @property
    def headers(self) -> dict[str, str]:
        """Get standard request headers."""
        return {
            "Authorization": self._token,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
            ),
            "Origin": "https://wwt.jinjiangwater.com",
            "Referer": "https://wwt.jinjiangwater.com/mine/bill",
        }

    async def _async_post(self, endpoint: str, data: dict[str, Any]) -> Any:
        """Send a POST request to the API."""
        url = f"{BASE_URL}/{endpoint}"
        try:
            async with self._session.post(
                url, headers=self.headers, data=data, timeout=15
            ) as response:
                if response.status in (401, 403):
                    raise JJWaterAuthError("Token 过期或验证失败")
                if response.status != 200:
                    raise JJWaterAPIError(f"服务器返回异常状态码: {response.status}")

                res_json = await response.json()
                code = res_json.get("code")
                if code == 200:
                    return res_json.get("data")
                
                msg = res_json.get("msg", "未知错误")
                _LOGGER.error("API 响应错误 [%s]: %s", endpoint, msg)
                raise JJWaterAPIError(msg)

        except aiohttp.ClientError as err:
            raise JJWaterAPIError(f"网络连接异常: {err}") from err

    async def get_overview(self, user_kh: str) -> dict[str, Any]:
        """获取用户概览信息 (findKhSl)."""
        res = await self._async_post("ysBase/findKhSl", {"USERB_KH": user_kh})
        return res if isinstance(res, dict) else {}

    async def get_daily_usage(
        self, user_kh: str, year_month: str | None = None
    ) -> dict[str, Any]:
        """获取每日用水明细 (findEveryDayYsl)."""
        if not year_month:
            year_month = datetime.now().strftime("%Y%m")
        res = await self._async_post(
            "ysBase/findEveryDayYsl",
            {"USERB_KH": user_kh, "YEAR_MONTH": year_month},
        )
        return res if isinstance(res, dict) else {}

    async def get_year_bill(
        self, user_kh: str, year: str | None = None
    ) -> list[dict[str, Any]]:
        """获取年度账单列表 (findYearDz)."""
        if not year:
            year = datetime.now().strftime("%Y")
        res = await self._async_post(
            "ysBase/findYearDz",
            {"USERB_KH": user_kh, "DEBTL_YEAR": year},
        )
        return res if isinstance(res, list) else []
