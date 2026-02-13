"""Coordinateur de données pour ACIT ThermACEC."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

import paho.mqtt.client as mqtt

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    TOPIC_AVAILABILITY,
    TOPIC_HVAC_MODE,
    TOPIC_SET_HVAC_MODE,
    TOPIC_SET_TARGET_TEMPERATURE,
    TOPIC_TARGET_TEMPERATURE,
    TOPIC_TEMPERATURE,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class ACITThermaControlCoordinator(DataUpdateCoordinator):
    """Coordinateur pour gérer les données ACIT ThermACEC via MQTT."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialiser le coordinateur."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.entry = entry
        self.mqtt_client: mqtt.Client | None = None
        self._topic_prefix = entry.data.get("topic_prefix", "acit/thermacec")
        
        # Données de l'appareil
        self.data: dict[str, Any] = {
            "temperature": None,
            "target_temperature": None,
            "hvac_mode": "off",
            "available": False,
        }

    async def async_config_entry_first_refresh(self) -> None:
        """Première actualisation lors de la configuration."""
        await self._async_setup_mqtt()
        await super().async_config_entry_first_refresh()

    async def _async_setup_mqtt(self) -> None:
        """Configurer la connexion MQTT."""
        _LOGGER.debug("Configuration de la connexion MQTT")
        
        def on_connect(client, userdata, flags, rc):
            """Callback appelé lors de la connexion au broker MQTT."""
            if rc == 0:
                _LOGGER.info("Connecté au broker MQTT")
                # S'abonner aux topics
                topics = [
                    f"{self._topic_prefix}/{TOPIC_TEMPERATURE}",
                    f"{self._topic_prefix}/{TOPIC_TARGET_TEMPERATURE}",
                    f"{self._topic_prefix}/{TOPIC_HVAC_MODE}",
                    f"{self._topic_prefix}/{TOPIC_AVAILABILITY}",
                ]
                for topic in topics:
                    client.subscribe(topic)
                    _LOGGER.debug(f"Abonné au topic: {topic}")
            else:
                _LOGGER.error(f"Échec de connexion MQTT, code: {rc}")

        def on_message(client, userdata, msg):
            """Callback appelé lors de la réception d'un message MQTT."""
            topic = msg.topic.replace(f"{self._topic_prefix}/", "")
            payload = msg.payload.decode()
            
            _LOGGER.debug(f"Message reçu - Topic: {topic}, Payload: {payload}")
            
            # Mettre à jour les données
            if topic == TOPIC_TEMPERATURE:
                try:
                    self.data["temperature"] = float(payload)
                except ValueError:
                    _LOGGER.error(f"Valeur de température invalide: {payload}")
            elif topic == TOPIC_TARGET_TEMPERATURE:
                try:
                    self.data["target_temperature"] = float(payload)
                except ValueError:
                    _LOGGER.error(f"Valeur de consigne invalide: {payload}")
            elif topic == TOPIC_HVAC_MODE:
                self.data["hvac_mode"] = payload
            elif topic == TOPIC_AVAILABILITY:
                self.data["available"] = payload.lower() == "online"
            
            # Notifier les entités
            self.async_set_updated_data(self.data)

        # Créer le client MQTT
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        
        # Authentification si nécessaire
        username = self.entry.data.get(CONF_USERNAME)
        password = self.entry.data.get(CONF_PASSWORD)
        if username and password:
            self.mqtt_client.username_pw_set(username, password)
        
        # Connexion au broker
        host = self.entry.data[CONF_HOST]
        port = self.entry.data[CONF_PORT]
        
        try:
            await self.hass.async_add_executor_job(
                self.mqtt_client.connect, host, port, 60
            )
            await self.hass.async_add_executor_job(self.mqtt_client.loop_start)
            _LOGGER.info(f"Client MQTT démarré - {host}:{port}")
        except Exception as err:
            _LOGGER.error(f"Erreur de connexion MQTT: {err}")
            raise UpdateFailed(f"Erreur de connexion MQTT: {err}")

    async def _async_update_data(self) -> dict[str, Any]:
        """Mettre à jour les données."""
        # Les données sont mises à jour via les callbacks MQTT
        return self.data

    async def async_publish(self, topic: str, payload: str | float) -> None:
        """Publier un message MQTT."""
        if self.mqtt_client is None:
            _LOGGER.error("Client MQTT non initialisé")
            return
        
        full_topic = f"{self._topic_prefix}/{topic}"
        _LOGGER.debug(f"Publication MQTT - Topic: {full_topic}, Payload: {payload}")
        
        try:
            await self.hass.async_add_executor_job(
                self.mqtt_client.publish, full_topic, str(payload)
            )
        except Exception as err:
            _LOGGER.error(f"Erreur lors de la publication MQTT: {err}")

    async def async_set_target_temperature(self, temperature: float) -> None:
        """Définir la température cible."""
        await self.async_publish(TOPIC_SET_TARGET_TEMPERATURE, temperature)

    async def async_set_hvac_mode(self, mode: str) -> None:
        """Définir le mode HVAC."""
        await self.async_publish(TOPIC_SET_HVAC_MODE, mode)

    async def async_shutdown(self) -> None:
        """Arrêter le coordinateur."""
        if self.mqtt_client:
            _LOGGER.debug("Arrêt du client MQTT")
            await self.hass.async_add_executor_job(self.mqtt_client.loop_stop)
            await self.hass.async_add_executor_job(self.mqtt_client.disconnect)

