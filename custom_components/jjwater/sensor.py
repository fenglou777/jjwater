"""晋江水务 传感器定义"""
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import JJWaterCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: JJWaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for acc in coordinator.accounts:
        entities.extend([
            JJWaterReadingSensor(coordinator, acc), JJWaterMonthUsageSensor(coordinator, acc),
            JJWaterBillStatusSensor(coordinator, acc), JJWaterLastBillSensor(coordinator, acc)
        ])
    async_add_entities(entities)

class JJWaterBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: JJWaterCoordinator, account: str) -> None:
        super().__init__(coordinator)
        self._account = account

    @property
    def account_data(self) -> dict:
        return self.coordinator.data.get(self._account, {}) if self.coordinator.data else {}

    @property
    def device_info(self) -> dict:
        name = f"晋江水务 {self._account}" + (f" ({self.account_data.get('user_name')})" if self.account_data.get('user_name') else "")
        return {"identifiers": {(DOMAIN, self._account)}, "name": name, "manufacturer": "晋江自来水股份有限公司", "model": f"户号: {self._account}"}

class JJWaterReadingSensor(JJWaterBaseSensor):
    _attr_name = "水表总抄表数"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:water-pump"
    @property
    def unique_id(self) -> str: return f"{DOMAIN}_{self._account}_total_reading"
    @property
    def native_value(self) -> float: return self.account_data.get("total_reading", 0.0)
    @property
    def extra_state_attributes(self) -> dict: return {"抄表日期": self.account_data.get("latest_cb_date", ""), "户名": self.account_data.get("user_name", "")}

class JJWaterMonthUsageSensor(JJWaterBaseSensor):
    _attr_name = "本月用水量"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_native_unit_of_measurement = "m³"
    _attr_icon = "mdi:water"
    @property
    def unique_id(self) -> str: return f"{DOMAIN}_{self._account}_month_usage"
    @property
    def native_value(self) -> float: return self.account_data.get("current_month_usage", 0.0)

class JJWaterBillStatusSensor(JJWaterBaseSensor):
    _attr_name = "账单状态"
    @property
    def unique_id(self) -> str: return f"{DOMAIN}_{self._account}_bill_status"
    @property
    def native_value(self) -> str: return self.account_data.get("current_bill_status", "正常")
    @property
    def icon(self) -> str: return "mdi:water-alert" if self.native_value == "未缴" else "mdi:water-check"

class JJWaterLastBillSensor(JJWaterBaseSensor):
    _attr_name = "账单金额"
    _attr_native_unit_of_measurement = "元"
    _attr_icon = "mdi:currency-cnf"
    @property
    def unique_id(self) -> str: return f"{DOMAIN}_{self._account}_last_bill"
    @property
    def native_value(self) -> float: return self.account_data.get("last_bill_amount", 0.0)
