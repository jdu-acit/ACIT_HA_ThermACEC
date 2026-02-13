"""Entité Climate pour ACIT ThermACEC."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MAX_TEMP, MIN_TEMP, TEMP_STEP
from .coordinator import ACITThermaControlCoordinator

_LOGGER = logging.getLogger(__name__)

# Mapping des modes HVAC
HVAC_MODE_MAP = {
    "off": HVACMode.OFF,
    "heat": HVACMode.HEAT,
    "cool": HVACMode.COOL,
    "auto": HVACMode.AUTO,
}

HVAC_MODE_REVERSE_MAP = {v: k for k, v in HVAC_MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurer l'entité climate ACIT ThermaControl."""
    coordinator: ACITThermaControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        ACITThermaControlClimate(coordinator, entry),
    ])


class ACITThermaControlClimate(CoordinatorEntity, ClimateEntity):
    """Entité Climate pour ACIT ThermaControl."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.AUTO,
    ]
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ACITThermaControlCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser l'entité climate."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_name = "Contrôle température"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data.get("device_name", "ACIT ThermaControl"),
            "manufacturer": "ACIT",
            "model": "ThermaControl v1.0",
            "sw_version": "1.0.0",
        }

    @property
    def current_temperature(self) -> float | None:
        """Retourner la température actuelle."""
        return self.coordinator.data.get("temperature")

    @property
    def target_temperature(self) -> float | None:
        """Retourner la température cible."""
        return self.coordinator.data.get("target_temperature")

    @property
    def hvac_mode(self) -> HVACMode:
        """Retourner le mode HVAC actuel."""
        mode = self.coordinator.data.get("hvac_mode", "off")
        return HVAC_MODE_MAP.get(mode, HVACMode.OFF)

    @property
    def available(self) -> bool:
        """Retourner si l'entité est disponible."""
        return self.coordinator.data.get("available", False)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Définir la température cible."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        _LOGGER.debug(f"Définition de la température cible: {temperature}°C")
        await self.coordinator.async_set_target_temperature(temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Définir le mode HVAC."""
        mode = HVAC_MODE_REVERSE_MAP.get(hvac_mode, "off")
        _LOGGER.debug(f"Définition du mode HVAC: {mode}")
        await self.coordinator.async_set_hvac_mode(mode)

    @property
    def icon(self) -> str:
        """Retourner l'icône de l'entité."""
        if self.hvac_mode == HVACMode.HEAT:
            return "mdi:radiator"
        elif self.hvac_mode == HVACMode.COOL:
            return "mdi:snowflake"
        elif self.hvac_mode == HVACMode.AUTO:
            return "mdi:thermostat-auto"
        return "mdi:thermostat"

