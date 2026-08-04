"""晋江水务 UI 配置流"""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_TOKEN, CONF_ACCOUNTS

class JJWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            token = user_input[CONF_TOKEN].strip()
            acc_list = [a.strip() for a in user_input[CONF_ACCOUNTS].replace("，", ",").split(",") if a.strip()]
            if acc_list:
                return self.async_create_entry(title=f"晋江水务 ({len(acc_list)}户)", data={CONF_TOKEN: token, CONF_ACCOUNTS: acc_list})
            return self.async_show_form(step_id="user", errors={"base": "invalid_auth"})
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str, vol.Required(CONF_ACCOUNTS): str})
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return JJWaterOptionsFlowHandler(config_entry)

class JJWaterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input:
            token = user_input[CONF_TOKEN].strip()
            acc_list = [a.strip() for a in user_input[CONF_ACCOUNTS].replace("，", ",").split(",") if a.strip()]
            self.hass.config_entries.async_update_entry(self.config_entry, data={CONF_TOKEN: token, CONF_ACCOUNTS: acc_list})
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN, default=self.config_entry.data.get(CONF_TOKEN, "")): str,
                vol.Required(CONF_ACCOUNTS, default=",".join(self.config_entry.data.get(CONF_ACCOUNTS, []))): str,
            })
        )
