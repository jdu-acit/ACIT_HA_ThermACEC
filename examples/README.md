# Exemples de code pour carte ACIT ThermACEC

Ce dossier contient un exemple de code pour ESP32 avec l'architecture Shelly Gen2.

## 📁 Fichier disponible

### esp32_example.ino
Code complet pour ESP32 avec architecture Shelly Gen2 :
- **HTTP RPC** (JSON-RPC 2.0) pour les commandes
- **WebSocket** pour les notifications temps réel
- **mDNS** pour l'auto-découverte
- Compatible avec Home Assistant v2.0+

## 🔧 Prérequis

### Bibliothèques Arduino

Installez ces bibliothèques via le gestionnaire de bibliothèques Arduino :

```
- WiFi (incluse avec ESP32)
- ESPmDNS (incluse avec ESP32)
- ESPAsyncWebServer by me-no-dev
- AsyncTCP by me-no-dev
- ArduinoJson by Benoit Blanchon (v6.x)
```

### Matériel requis

- ESP32 ou ESP8266
- Capteur DHT22 (ou DHT11)
- Relais 5V (optionnel)
- Résistance 10kΩ (pull-up pour DHT22)

## 🔌 Schéma de câblage

### ESP32 + DHT22

```
DHT22 VCC  → ESP32 3.3V
DHT22 GND  → ESP32 GND
DHT22 DATA → ESP32 GPIO4 (avec résistance 10kΩ vers 3.3V)
```

### ESP32 + Relais

```
Relais VCC → ESP32 5V
Relais GND → ESP32 GND
Relais IN  → ESP32 GPIO5
```

## ⚙️ Configuration

### 1. Modifier les paramètres WiFi

```cpp
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
```

### 2. Personnaliser le nom de l'appareil (optionnel)

```cpp
String deviceName = "acit-thermacec";  // Sera: acit-thermacec-<MAC>.local
```

### 3. Adapter la lecture de température

Remplacez la simulation par votre capteur réel :

```cpp
// Dans loop(), remplacez:
// currentTemperature = readTemperatureSensor();

// Par exemple avec DHT22:
#include <DHT.h>
DHT dht(4, DHT22);
currentTemperature = dht.readTemperature();
```

## 📤 Upload du code

1. Ouvrez le fichier `.ino` dans Arduino IDE
2. Sélectionnez votre carte (ESP32 Dev Module / NodeMCU 1.0)
3. Sélectionnez le port COM
4. Cliquez sur "Téléverser"

## 🔍 Débogage

### Moniteur série

Ouvrez le moniteur série (115200 baud) pour voir :
- Connexion WiFi
- Connexion MQTT
- Messages reçus/envoyés
- Température lue

### Exemple de sortie

```
Connexion à MonWiFi...
WiFi connecté
Adresse IP: 192.168.1.100
Connexion MQTT...connecté
Abonné aux topics de commande
Température: 21.5°C
Message reçu [acit/thermacec/set/target_temperature]: 22.0
Nouvelle consigne: 22.0°C
Chauffage: ON
```

## 🧪 Test rapide

### Tester la découverte mDNS

```bash
# Linux/Mac
dns-sd -B _acit._tcp local

# Windows (avec Bonjour Print Services)
dns-sd -B _acit._tcp local
```

### Tester l'API RPC

```bash
# Obtenir le statut
curl -X POST http://acit-thermacec-<MAC>.local/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"Thermostat.GetStatus","params":{}}'

# Changer la consigne
curl -X POST http://acit-thermacec-<MAC>.local/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"Thermostat.SetTargetTemp","params":{"temperature":22.5}}'
```

### Tester le WebSocket

```bash
# Installer wscat: npm install -g wscat
wscat -c ws://acit-thermacec-<MAC>.local/ws

# Vous devriez recevoir des notifications NotifyStatus
```

## 🎯 Personnalisation

### Changer l'intervalle de publication

```cpp
const long publishInterval = 10000;  // 10 secondes (en millisecondes)
```

### Ajouter un hystérésis

```cpp
if (currentTemperature < targetTemperature - 0.5) {
    // Allumer le chauffage
}
else if (currentTemperature > targetTemperature + 0.5) {
    // Éteindre le chauffage
}
```

### Ajouter un capteur d'humidité

```cpp
float humidity = dht.readHumidity();
client.publish("acit/thermacec/humidity", String(humidity, 1).c_str());
```

## 🔐 Sécurité

### Ajouter une authentification MQTT

```cpp
const char* mqtt_user = "votre_utilisateur";
const char* mqtt_password = "votre_mot_de_passe";
```

### Utiliser TLS/SSL (avancé)

```cpp
WiFiClientSecure espClient;
// Configuration du certificat...
```

## 📚 Ressources

- [Documentation ESP32](https://docs.espressif.com/)
- [PubSubClient Library](https://pubsubclient.knolleary.net/)
- [DHT Sensor Library](https://github.com/adafruit/DHT-sensor-library)

## 🆘 Problèmes courants

### La carte ne se connecte pas au WiFi

- Vérifiez le SSID et le mot de passe
- Vérifiez que le WiFi est en 2.4GHz (pas 5GHz)
- Vérifiez la portée du signal

### mDNS ne fonctionne pas

- Vérifiez que votre routeur supporte mDNS/Bonjour
- Essayez d'accéder par IP directement
- Sur Windows, installez Bonjour Print Services

### Home Assistant ne découvre pas l'appareil

- Vérifiez que Home Assistant et l'ESP32 sont sur le même réseau/VLAN
- Vérifiez les logs série de l'ESP32
- Essayez la configuration manuelle avec l'IP

### WebSocket se déconnecte

- Normal si aucun client n'est connecté
- Home Assistant se reconnecte automatiquement
- Vérifiez les logs pour les erreurs

## 💡 Améliorations possibles

- [ ] Ajouter un écran OLED pour affichage local
- [ ] Ajouter des boutons physiques pour contrôle manuel
- [ ] Implémenter OTA (mise à jour sans fil)
- [ ] Ajouter la persistance des paramètres (EEPROM/SPIFFS)
- [ ] Implémenter un mode AP pour configuration initiale
- [ ] Ajouter un watchdog pour redémarrage automatique
- [ ] Implémenter TLS/SSL pour sécurité accrue

