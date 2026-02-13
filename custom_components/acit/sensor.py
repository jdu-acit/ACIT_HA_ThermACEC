"""Capteurs pour ACIT ThermaControl."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ACITThermaControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configurer les capteurs ACIT ThermACEC."""
    coordinator: ACITThermaControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        ACITTemperatureSensor(coordinator, entry),
    ])


class ACITTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Capteur de température ambiante ACIT ThermaControl."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ACITThermaControlCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialiser le capteur de température."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temperature"
        self._attr_name = "Température ambiante"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data.get("device_name", "ACIT ThermACEC"),
            "manufacturer": "ACIT",
            "model": "ThermACEC v1.0",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> float | None:
        """Retourner la température actuelle."""
        return self.coordinator.data.get("temperature")

    @property
    def available(self) -> bool:
        """Retourner si l'entité est disponible."""
        return self.coordinator.data.get("available", False)

    @property
    def icon(self) -> str:
        """Retourner l'icône du capteur."""
        return "mdi:thermometer"

