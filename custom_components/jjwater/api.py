"""晋江水务 API 通信模块"""
from __future__ import annotations
import logging
from datetime import datetime
import aiohttp
import async_timeout
from .const import API_URL_DAILY, API_URL_YEAR

_LOGGER = logging.getLogger(__name__)

class JJWaterAPI:
    def __init__(self, session: aiohttp.ClientSession, token: str) -> None:
        self._session = session
        token_str = token.strip()
        self._token = token_str if token_str.startswith("Bearer ") else f"Bearer {token_str}"

    async def fetch_account_data(self, account: str) -> dict:
        headers = {
            "Host": "wwt.jinjiangwater.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._token,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
            "Referer": "https://wwt.jinjiangwater.com/mine/bill",
        }
        now = datetime.now()
        current_ym, current_year, current_month = now.strftime("%Y%m"), str(now.year), now.month
        
        result = {
            "account": account, "user_name": "", "total_reading": 0.0,
            "latest_cb_date": "", "current_month_usage": 0.0,
            "current_bill_status": "正常", "current_bill_amount": 0.0, "last_bill_amount": 0.0,
        }

        try:
            async with async_timeout.timeout(12):
                payload_daily = f"USERB_KH={account}&YEAR_MONTH={current_ym}"
                async with self._session.post(API_URL_DAILY, data=payload_daily, headers=headers) as resp:
                    res_d = await resp.json()
                    if res_d.get("code") == 200 and "data" in res_d:
                        result["current_month_usage"] = float(res_d["data"].get("zsl", 0.0))
                        if days := res_d["data"].get("everyDayYsl", []):
                            result["total_reading"] = float(days[-1].get("bqds", 0.0))
                            result["latest_cb_date"] = days[-1].get("cbsj", "")
                            result["user_name"] = days[-1].get("hm", "")

                payload_year = f"USERB_KH={account}&DEBTL_YEAR={current_year}"
                async with self._session.post(API_URL_YEAR, data=payload_year, headers=headers) as resp:
                    res_y = await resp.json()
                    if res_y.get("code") == 200 and "data" in res_y:
                        for bill in res_y["data"]:
                            mon = bill.get("DEBTL_MON")
                            if mon == current_month:
                                result["current_bill_status"] = bill.get("JFZT", "未知")
                                result["current_bill_amount"] = float(bill.get("DEBTL_STOTAL", 0.0))
                            elif mon == current_month - 1 or (current_month == 1 and mon == 12):
                                result["last_bill_amount"] = float(bill.get("DEBTL_STOTAL", 0.0))
        except Exception as err:
            _LOGGER.error("拉取户号 %s 数据异常: %s", account, err)
        return result
