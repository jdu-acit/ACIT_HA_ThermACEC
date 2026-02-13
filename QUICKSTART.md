# 🚀 Quick Start - ACIT ThermACEC

Ultra-fast guide to get up and running in 5 minutes!

## ⚡ Express Installation

### 1. Install via HACS (2 minutes)

```
HACS → Integrations → ⋮ → Custom repositories
URL: https://github.com/jdu-acit/ACIT_HA_ThermACEC
Category: Integration
```

### 2. Restart Home Assistant (1 minute)

```
Settings → System → Restart
```

### 3. Add the integration (2 minutes)

```
Settings → Devices & Services → + Add Integration
Search: ACIT ThermACEC
```

**Minimal configuration:**
- Name: `My Thermostat`
- MQTT Broker: `10.0.0.213`
- Port: `1883`
- Topic: `acit`

## 🔌 Board Configuration (ESP32)

### Minimal Code

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* mqtt_server = "10.0.0.213";
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  WiFi.begin("SSID", "PASSWORD");
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // Publish temperature every 10s
  static unsigned long last = 0;
  if (millis() - last > 10000) {
    last = millis();
    float temp = 21.5; // Read your sensor here
    client.publish("acit/temperature", String(temp).c_str());
    client.publish("acit/availability", "online");
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ACIT_Board")) {
      client.subscribe("acit/set/#");
    } else {
      delay(5000);
    }
  }
}
```

## 🎨 First Lovelace Card

Add this card to your dashboard:

```yaml
type: thermostat
entity: climate.acit_ThermACEC_controle_temperature
name: My Thermostat
```

## ✅ Quick Test

### Test with MQTT

```bash
# Publish a test temperature
mosquitto_pub -h 10.0.0.213 -t acit/temperature -m "22.5"

# Check in Home Assistant
# Temperature should display immediately
```

## 🎯 First Automation

```yaml
automation:
  - alias: "Morning Heating"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: climate.set_temperature
      target:
        entity_id: climate.acit_ThermACEC_controle_temperature
      data:
        temperature: 21
```

## 🆘 Problem?

### Temperature not displaying?

```bash
# Check MQTT topics
mosquitto_sub -h 10.0.0.213 -t 'acit/#' -v
```

### Integration doesn't appear?

1. Clear cache: `Ctrl + F5`
2. Check: `config/custom_components/acit/`
3. Restart Home Assistant

## 📚 Go Further

- [Complete Installation](INSTALLATION.md)
- [Advanced Examples](EXAMPLES.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Total time: ~5 minutes** ⏱️

You're now ready to use ACIT ThermACEC! 🎉

