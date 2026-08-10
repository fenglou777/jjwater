"""Config flow for Jinjiang Water integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JJWaterAPI, JJWaterAPIError
from .const import CONF_TOKEN, CONF_USER_KH, DEFAULT_SCAN_INTERVAL_HOURS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class JJWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jinjiang Water."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_kh = user_input[CONF_USER_KH].strip()
            token = user_input[CONF_TOKEN].strip()

            await self.async_set_unique_id(user_kh)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = JJWaterAPI(session, token)

            try:
                await api.get_overview(user_kh)
            except JJWaterAPIError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"晋江水务 ({user_kh})",
                    data={
                        CONF_USER_KH: user_kh,
                        CONF_TOKEN: token,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USER_KH): str,
                    vol.Required(CONF_TOKEN): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """注册选项流控制器 (这步会让前端出现齿轮按钮)."""
        return JJWaterOptionsFlowHandler(config_entry)


class JJWaterOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Jinjiang Water."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_token = self.config_entry.options.get(
            CONF_TOKEN, self.config_entry.data.get(CONF_TOKEN, "")
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOKEN, default=current_token): str,
                }
            ),
        )
