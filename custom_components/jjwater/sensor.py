"""Sensor platform for Jinjiang Water."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfVolume, CURRENCY_YUAN

from .const import DOMAIN
from .coordinator import JJWaterDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Jinjiang Water sensors from a config entry."""
    coordinator: JJWaterDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        JJWaterMeterReadingSensor(coordinator),
        JJWaterTodayUsageSensor(coordinator),
        JJWaterMonthUsageSensor(coordinator),
        JJWaterMonthBillSensor(coordinator),
        JJWaterYearUsageSensor(coordinator),
        JJWaterPaymentStatusSensor(coordinator),
    ]

    async_add_entities(sensors)


class JJWaterBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for Jinjiang Water."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator, sensor_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.user_kh = coordinator.user_kh
        self._sensor_type = sensor_type
        self._attr_unique_id = f"jjwater_{self.user_kh}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.user_kh)},
            "name": f"晋江水务 ({self.user_kh})",
            "manufacturer": "Jinjiang Water",
            "model": "Smart Water Meter",
        }


class JJWaterMeterReadingSensor(JJWaterBaseSensor):
    """水表总读数传感器 (专为 Home Assistant 能源仪表盘设计)."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "meter_reading")
        self._attr_name = "水表读数"
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float | None:
        """获取最新抄表表读数 bqds."""
        latest_day = self.coordinator.data.get("latest_day", {})
        ds = latest_day.get("bqds")
        return float(ds) if ds is not None else None


class JJWaterTodayUsageSensor(JJWaterBaseSensor):
    """今日实际用水量传感器."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "today_usage")
        self._attr_name = "今日用水量"
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        """获取最新一天的实际用水量 sl."""
        latest_day = self.coordinator.data.get("latest_day", {})
        sl = latest_day.get("sl")
        return float(sl) if sl is not None else None


class JJWaterMonthUsageSensor(JJWaterBaseSensor):
    """当月实际用水量传感器."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "month_usage")
        self._attr_name = "当月用水量"
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        """优先取每日接口的 zsl，无则取概览中的 BQSL."""
        zsl = self.coordinator.data.get("zsl")
        if zsl is not None and zsl > 0:
            return float(zsl)
        overview = self.coordinator.data.get("overview", {})
        bqsl = overview.get("BQSL")
        return float(bqsl) if bqsl is not None else None


class JJWaterMonthBillSensor(JJWaterBaseSensor):
    """当月水费/应缴金额传感器."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "month_bill")
        self._attr_name = "当月水费账单"
        self._attr_native_unit_of_measurement = CURRENCY_YUAN
        self._attr_device_class = SensorDeviceClass.MONETARY

    @property
    def native_value(self) -> float | None:
        """获取最新账单金额 DEBTL_STOTAL 或 BQJE."""
        overview = self.coordinator.data.get("overview", {})
        bqje = overview.get("BQJE")
        if bqje is not None:
            return float(bqje)
        latest_bill = self.coordinator.data.get("latest_bill", {})
        total = latest_bill.get("DEBTL_STOTAL")
        return float(total) if total is not None else None


class JJWaterYearUsageSensor(JJWaterBaseSensor):
    """年度累计用水量传感器."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "year_usage")
        self._attr_name = "年度累计用水量"
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
        self._attr_device_class = SensorDeviceClass.WATER

    @property
    def native_value(self) -> float | None:
        """获取概览中的 NDSL."""
        overview = self.coordinator.data.get("overview", {})
        ndsl = overview.get("NDSL")
        return float(ndsl) if ndsl is not None else None


class JJWaterPaymentStatusSensor(JJWaterBaseSensor):
    """缴费状态传感器."""

    def __init__(self, coordinator: JJWaterDataUpdateCoordinator) -> None:
        super().__init__(coordinator, "payment_status")
        self._attr_name = "缴费状态"
        self._attr_icon = "mdi:cash-check"

    @property
    def native_value(self) -> str | None:
        """获取概览中的 PAY_TAG 或账单中的 JFZT."""
        overview = self.coordinator.data.get("overview", {})
        tag = overview.get("PAY_TAG")
        if tag:
            return str(tag)
        latest_bill = self.coordinator.data.get("latest_bill", {})
        return latest_bill.get("JFZT")
