# ACIT ThermACEC

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/jdu-acit/ACIT_HA_ThermACEC.svg)](https://github.com/jdu-acit/ACIT_HA_ThermACEC/releases)
[![License](https://img.shields.io/github/license/jdu-acit/ACIT_HA_ThermACEC.svg)](LICENSE)

Home Assistant custom integration for ACIT ThermACEC electronic board - Ambient temperature and setpoint management.

## 🌟 Features

- 🌡️ **Ambient temperature sensor** - Real-time reading
- 🎯 **Temperature setpoint control** - Complete climate entity
- 🔄 **MQTT support** - Uses your existing Mosquitto broker
- � **Multi-language interface** - Complete translations (FR/EN)
- ⚙️ **UI configuration** - No manual YAML editing
- 🔍 **Auto-discovery** - Automatic device detection

## 📋 Prerequisites

- Home Assistant 2024.1.0 or higher
- Configured MQTT broker (Mosquitto recommended)
- ACIT ThermACEC electronic board configured

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click on the ⋮ menu in the top right
4. Select "Custom repositories"
5. Add the URL: `https://github.com/jdu-acit/ACIT_HA_ThermACEC`
6. Select category "Integration"
7. Click on "ACIT ThermACEC" in the list
8. Click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest version from [Releases](https://github.com/jdu-acit/ACIT_HA_ThermACEC/releases)
2. Copy the `custom_components/acit` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

### 1. Add the integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **ACIT ThermACEC**
4. Follow the on-screen instructions

### 2. MQTT Configuration

During configuration, you will need to provide:

- **MQTT Broker**: Your broker address (e.g., `10.0.0.213`)
- **Port**: MQTT port (default: `1883`)
- **Base Topic**: MQTT topic prefix (e.g., `acit`)
- **Device Name**: Custom name for your board

### 3. Expected MQTT Topics

The integration subscribes to the following topics:

```
acit/temperature        # Ambient temperature (°C)
acit/target_temperature # Temperature setpoint (°C)
acit/hvac_mode          # Mode: off, heat, cool, auto
acit/availability       # online/offline
```

Command topics (publish):

```
acit/set/target_temperature  # Set the setpoint
acit/set/hvac_mode           # Change the mode
```

## 📊 Created Entities

### Temperature Sensor
- **Type**: `sensor`
- **Class**: `temperature`
- **Unit**: °C
- **Update**: Real-time via MQTT

### Temperature Control
- **Type**: `climate`
- **Modes**: Off, Heat, Cool, Auto
- **Temperature Range**: 5°C - 35°C
- **Precision**: 0.1°C

## 🔧 Board Configuration Example

Your ACIT board must publish to MQTT in this format:

```json
{
  "temperature": 21.5,
  "target_temperature": 22.0,
  "hvac_mode": "heat"
}
```

## 🐛 Troubleshooting

### Integration doesn't appear

1. Verify the folder is in `custom_components/acit`
2. Restart Home Assistant
3. Clear your browser cache (Ctrl+F5)

### No data received

1. Verify your MQTT broker is running
2. Check MQTT topics with MQTT Explorer
3. Check logs: **Settings** → **System** → **Logs**

### Detailed Logs

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.acit: debug
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**ACIT** - [jdu-acit](https://github.com/jdu-acit)

## 🙏 Acknowledgments

- Home Assistant Community
- HACS for easy distribution
- Mosquitto MQTT Broker

