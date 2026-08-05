"""API Client for Jinjiang Water."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://wwt.jinjiangwater.com/jjapis"


class JJWaterAPIError(Exception):
    """General API Error."""


class JJWaterAuthError(JJWaterAPIError):
    """Authentication Error."""


class JJWaterAPI:
    """Client for Jinjiang Water API."""

    def __init__(self, session: aiohttp.ClientSession, token: str) -> None:
        """Initialize API."""
        self._session = session
        self._token = str(token).replace("Bearer ", "").strip()

    @property
    def headers(self) -> dict[str, str]:
        """Get standard request headers."""
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) MicroMessenger/8.0.70",
            "Origin": "https://wwt.jinjiangwater.com",
            "Referer": "https://wwt.jinjiangwater.com/mine/bill",
        }

    async def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Send POST request with form data."""
        url = f"{BASE_URL}/{path}"
        try:
            async with self._session.post(
                url, headers=self.headers, data=data, timeout=15
            ) as resp:
                if resp.status in (401, 403):
                    raise JJWaterAuthError("Token 已失效，请重新获取并配置")

                res_json = await resp.json()
                return res_json
        except aiohttp.ClientError as err:
            raise JJWaterAPIError(f"网络连接失败: {err}") from err

    async def get_overview(self, user_kh: str) -> dict[str, Any]:
        """获取水表基础概览信息 (findKhSl)."""
        res = await self._post("ysBase/findKhSl", {"USERB_KH": user_kh})
        if res.get("code") == 200 and "data" in res:
            return res["data"]
        msg = res.get("msg") or res.get("message") or "请求概览失败"
        raise JJWaterAPIError(msg)

    async def get_daily_usage(
        self, user_kh: str, year_month: str | None = None
    ) -> dict[str, Any]:
        """获取每日用量明细 (findEveryDayYsl)."""
        if not year_month:
            year_month = datetime.now().strftime("%Y%m")

        payload = {"USERB_KH": user_kh, "YEAR_MONTH": year_month}
        res = await self._post("ysBase/findEveryDayYsl", payload)

        if res.get("code") == 200 and isinstance(res.get("data"), dict):
            return res["data"]

        _LOGGER.debug(
            "户号 %s 获取 %s 每日用量提示: %s", user_kh, year_month, res.get("msg")
        )
        return {"zsl": 0.0, "everyDayYsl": []}

    async def get_year_bill(
        self, user_kh: str, year: str | None = None
    ) -> list[dict[str, Any]]:
        """获取年度账单明细 (findYearDz)."""
        if not year:
            year = datetime.now().strftime("%Y")

        payload = {"USERB_KH": user_kh, "DEBTL_YEAR": year}
        res = await self._post("ysBase/findYearDz", payload)

        if res.get("code") == 200 and isinstance(res.get("data"), list):
            return res["data"]

        _LOGGER.debug("户号 %s 获取 %s 年度账单提示: %s", user_kh, year, res.get("msg"))
        return []
