"""Config flow for Jinjiang Water integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JJWaterAPI, JJWaterAPIError, JJWaterAuthError
from .const import CONF_TOKEN, CONF_USER_KH, DOMAIN

_LOGGER = logging.getLogger(__name__)


class JJWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jinjiang Water."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_kh = user_input[CONF_USER_KH].strip()
            token = user_input[CONF_TOKEN].strip()

            await self.async_set_unique_id(f"jjwater_{user_kh}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = JJWaterAPI(session, token)

            try:
                overview = await api.get_overview(user_kh)
                # 获取户名作为显示标题（如未获取到则回退显示户号）
                customer_name = overview.get("USERB_NAME", user_kh) if isinstance(overview, dict) else user_kh
            except JJWaterAuthError:
                errors["base"] = "invalid_auth"
            except JJWaterAPIError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"晋江水务 ({customer_name})",
                    data={
                        CONF_USER_KH: user_kh,
                        CONF_TOKEN: token,
                    },
                )

        # 描述配置表单
        data_schema = vol.Schema(
            {
                vol.Required(CONF_USER_KH): str,
                vol.Required(CONF_TOKEN): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
