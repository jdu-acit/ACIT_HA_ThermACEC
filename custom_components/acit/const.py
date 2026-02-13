"""Constantes pour l'intégration ACIT ThermACEC."""
from typing import Final

# Domaine de l'intégration
DOMAIN: Final = "acit"

# Configuration par défaut
DEFAULT_NAME: Final = "ACIT ThermACEC"
DEFAULT_PORT: Final = 1883
DEFAULT_TOPIC_PREFIX: Final = "acit"

# Topics MQTT
TOPIC_TEMPERATURE: Final = "temperature"
TOPIC_TARGET_TEMPERATURE: Final = "target_temperature"
TOPIC_HVAC_MODE: Final = "hvac_mode"
TOPIC_AVAILABILITY: Final = "availability"

# Topics de commande
TOPIC_SET_TARGET_TEMPERATURE: Final = "set/target_temperature"
TOPIC_SET_HVAC_MODE: Final = "set/hvac_mode"

# Limites de température
MIN_TEMP: Final = 5.0
MAX_TEMP: Final = 35.0
TEMP_STEP: Final = 0.1

# Modes HVAC
HVAC_MODE_OFF: Final = "off"
HVAC_MODE_HEAT: Final = "heat"
HVAC_MODE_COOL: Final = "cool"
HVAC_MODE_AUTO: Final = "auto"

# Intervalle de mise à jour (secondes)
UPDATE_INTERVAL: Final = 30

# Timeout de disponibilité (secondes)
AVAILABILITY_TIMEOUT: Final = 60

