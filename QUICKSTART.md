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

**Option A: Automatic Discovery (Easiest)**
```
Settings → Devices & Services
Look for "Discovered" section
Click "Configure" on ACIT ThermACEC
Confirm the device
```

**Option B: Manual Configuration**
```
Settings → Devices & Services → + Add Integration
Search: ACIT ThermACEC
```

**Configuration:**
- Name: `My Thermostat`
- IP Address: `10.0.0.41` (your device IP)
- Port: `80` (default)

## 🔌 Board Configuration (ESP32)

### Architecture Overview

The ACIT ThermACEC uses a **Shelly Gen2-style architecture**:
- **HTTP RPC** (JSON-RPC 2.0) for commands
- **WebSocket** for real-time notifications
- **mDNS** for auto-discovery

### Required Features

Your ESP32 firmware must implement:

1. **mDNS Service**
   - Service type: `_acit._tcp.local.`
   - Hostname: `acit-thermacec-<MAC>.local`

2. **HTTP RPC Endpoint** (`/rpc`)
   - `Thermostat.GetStatus` - Return current state
   - `Thermostat.GetConfig` - Return device info
   - `Thermostat.SetTargetTemp` - Set temperature setpoint

3. **WebSocket Endpoint** (`/ws`)
   - Push `NotifyStatus` when state changes

### Example RPC Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "temperature": 21.8,
    "target_temperature": 22.0,
    "heater_level": 0,
    "fan_speed": 1
  },
  "id": 1
}
```

See [examples/esp32_example.ino](examples/esp32_example.ino) for complete implementation.

## 🎨 First Lovelace Card

Add this card to your dashboard:

```yaml
type: thermostat
entity: climate.acit_ThermACEC_controle_temperature
name: My Thermostat
```

## ✅ Quick Test

### Test RPC Connection

```bash
# Test GetStatus method
curl -X POST http://10.0.0.41/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "Thermostat.GetStatus",
    "params": {}
  }'

# Expected response:
# {"jsonrpc":"2.0","result":{"temperature":21.8,"target_temperature":22.0,...},"id":1}
```

### Test WebSocket Notifications

```bash
# Install wscat: npm install -g wscat
wscat -c ws://10.0.0.41/ws

# You should receive NotifyStatus messages when state changes
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

### Device not discovered?

1. Check device is on same network as Home Assistant
2. Try manual configuration with IP address
3. Verify mDNS is not blocked by firewall

### Temperature not displaying?

```bash
# Test RPC connection
curl http://10.0.0.41/rpc -X POST \
  -d '{"jsonrpc":"2.0","id":1,"method":"Thermostat.GetStatus","params":{}}'
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

