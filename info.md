# ACIT ThermACEC

Home Assistant custom integration for ACIT ThermACEC electronic board - Smart ambient temperature and setpoint management.

## 🌟 Key Features

- **🌡️ Temperature Sensor** - Real-time ambient temperature reading
- **🎯 Setpoint Control** - Complete climate entity with HVAC modes
- **🔄 Native MQTT** - Uses your existing MQTT infrastructure
- **🌍 Multi-language Interface** - Complete FR/EN translations
- **⚙️ UI Configuration** - No need to edit configuration.yaml
- **📊 Lovelace Compatible** - Native thermostat cards

## 📦 Quick Installation

1. Install via HACS
2. Restart Home Assistant
3. Add the integration via the interface
4. Configure your MQTT broker
5. You're ready! 🎉

## 🔧 Requirements

- Home Assistant 2024.1.0+
- MQTT Broker (Mosquitto recommended)
- ACIT ThermACEC board configured

## 📚 Documentation

- [Complete Installation Guide](https://github.com/jdu-acit/ACIT_HA_ThermACEC/blob/main/INSTALLATION.md)
- [Usage Examples](https://github.com/jdu-acit/ACIT_HA_ThermACEC/blob/main/EXAMPLES.md)
- [Troubleshooting](https://github.com/jdu-acit/ACIT_HA_ThermACEC/blob/main/TROUBLESHOOTING.md)

## 🎨 Lovelace Card Example

```yaml
type: thermostat
entity: climate.acit_ThermACEC_controle_temperature
```

## 🤖 Automation Example

```yaml
automation:
  - alias: "Thermostat - Night Mode"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.acit_ThermACEC_controle_temperature
        data:
          temperature: 18
```

## 🆘 Support

- [GitHub Issues](https://github.com/jdu-acit/ACIT_HA_ThermACEC/issues)
- [Discussions](https://github.com/jdu-acit/ACIT_HA_ThermACEC/discussions)

## 📝 License

MIT License - See [LICENSE](https://github.com/jdu-acit/ACIT_HA_ThermACEC/blob/main/LICENSE)

