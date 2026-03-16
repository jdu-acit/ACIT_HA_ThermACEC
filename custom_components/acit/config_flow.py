"""Config flow for ACIT ThermaControl."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    RPC_ENDPOINT,
    RPC_METHOD_GET_CONFIG,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input by testing the RPC connection."""
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)

    url = f"http://{host}:{port}{RPC_ENDPOINT}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": RPC_METHOD_GET_CONFIG,
        "params": {},
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise ValueError(f"HTTP error {response.status}")

                result = await response.json()

                if "error" in result:
                    raise ValueError(f"RPC error: {result['error'].get('message')}")

                config = result.get("result", {})
                mac_address = config.get("mac_address", "")
                model = config.get("model", "ThermACEC")

                return {
                    "title": data[CONF_NAME],
                    "mac_address": mac_address,
                    "model": model,
                }

    except asyncio.TimeoutError as err:
        raise ValueError("Connection timeout") from err
    except aiohttp.ClientError as err:
        raise ValueError(f"Connection error: {err}") from err


class ACITThermaControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for ACIT ThermaControl."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, dict[str, Any]] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user-initiated step."""
        return await self.async_step_manual()

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manual configuration by IP address."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError as err:
                _LOGGER.error(f"Validation error: {err}")
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during validation")
                errors["base"] = "unknown"
            else:
                # Use MAC address as unique_id
                mac_address = info.get("mac_address", user_input[CONF_HOST])
                await self.async_set_unique_id(mac_address)
                self._abort_if_unique_id_configured()

                # Add device_name to data
                user_input["device_name"] = user_input[CONF_NAME]

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="manual",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "name": DEFAULT_NAME,
                "host": "10.0.0.41",
                "port": str(DEFAULT_PORT),
            },
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle Zeroconf/mDNS discovery."""
        _LOGGER.info(f"ACIT device discovered via mDNS: {discovery_info}")

        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        hostname = discovery_info.hostname

        # Extract device name from hostname
        device_name = hostname.replace(".local.", "").replace("_", " ").title()

        # Test connection and retrieve config
        try:
            info = await validate_input(
                self.hass,
                {
                    CONF_NAME: device_name,
                    CONF_HOST: host,
                    CONF_PORT: port,
                },
            )
        except Exception as err:
            _LOGGER.error(f"Error validating discovered device: {err}")
            return self.async_abort(reason="cannot_connect")

        # Use MAC address as unique_id
        mac_address = info.get("mac_address", host)
        await self.async_set_unique_id(mac_address)
        self._abort_if_unique_id_configured()

        # Store discovered device information
        self.context["title_placeholders"] = {"name": device_name}
        self._discovered_devices[mac_address] = {
            CONF_NAME: device_name,
            CONF_HOST: host,
            CONF_PORT: port,
            "device_name": device_name,
            "mac_address": mac_address,
            "model": info.get("model", "ThermACEC"),
        }

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        mac_address = self.unique_id
        discovered = self._discovered_devices.get(mac_address, {})

        if user_input is not None:
            return self.async_create_entry(
                title=discovered[CONF_NAME],
                data=discovered,
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={
                "name": discovered.get(CONF_NAME, "ACIT ThermACEC"),
                "host": discovered.get(CONF_HOST, ""),
                "model": discovered.get("model", "ThermACEC"),
            },
        )

