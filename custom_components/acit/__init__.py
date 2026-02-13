"""ACIT ThermaControl Integration pour Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import ACITThermaControlCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurer l'intégration ACIT ThermaControl à partir d'une entrée de configuration."""
    _LOGGER.debug("Configuration de l'intégration ACIT ThermaControl")
    
    # Créer le coordinateur de données
    coordinator = ACITThermaControlCoordinator(hass, entry)
    
    # Initialiser la connexion MQTT
    await coordinator.async_config_entry_first_refresh()
    
    # Stocker le coordinateur
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Enregistrer l'appareil
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="ACIT",
        name=entry.data.get("device_name", "ACIT ThermACEC"),
        model="ThermACEC v1.0",
        sw_version="1.0.0",
    )

    # Configurer les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Intégration ACIT ThermACEC configurée avec succès")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharger une entrée de configuration."""
    _LOGGER.debug("Déchargement de l'intégration ACIT ThermaControl")
    
    # Décharger les plateformes
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Arrêter le coordinateur
        coordinator: ACITThermaControlCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_shutdown()
        
        # Supprimer les données
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Recharger l'entrée de configuration."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

