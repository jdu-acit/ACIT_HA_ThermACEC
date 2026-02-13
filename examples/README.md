# Exemples de code pour carte ACIT ThermACEC

Ce dossier contient des exemples de code pour différentes plateformes matérielles.

## 📁 Fichiers disponibles

### esp32_example.ino
Code complet pour ESP32/ESP8266 avec :
- Connexion WiFi
- Client MQTT
- Lecture capteur DHT22
- Publication des données
- Réception des commandes
- Contrôle de relais

## 🔧 Prérequis

### Bibliothèques Arduino

Installez ces bibliothèques via le gestionnaire de bibliothèques Arduino :

```
- WiFi (incluse avec ESP32/ESP8266)
- PubSubClient by Nick O'Leary
- DHT sensor library by Adafruit
- Adafruit Unified Sensor
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
const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_MOT_DE_PASSE";
```

### 2. Modifier l'adresse MQTT

```cpp
const char* mqtt_server = "10.0.0.213";  // Votre broker
const int mqtt_port = 1883;
```

### 3. Modifier les topics (optionnel)

```cpp
const char* topic_temperature = "acit/thermacec/temperature";
// etc.
```

### 4. Configurer les GPIO

```cpp
#define DHTPIN 4      // GPIO pour DHT22
#define RELAY_PIN 5   // GPIO pour relais
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

### Publier une commande de test

```bash
# Changer la consigne
mosquitto_pub -h 10.0.0.213 -t acit/thermacec/set/target_temperature -m "22.5"

# Changer le mode
mosquitto_pub -h 10.0.0.213 -t acit/thermacec/set/hvac_mode -m "heat"
```

### Écouter les publications

```bash
mosquitto_sub -h 10.0.0.213 -t 'acit/thermacec/#' -v
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

### Pas de connexion MQTT

- Vérifiez l'adresse IP du broker
- Vérifiez que le port 1883 est ouvert
- Testez avec `mosquitto_pub` depuis un PC

### Température incorrecte

- Vérifiez le câblage du DHT22
- Vérifiez la résistance pull-up (10kΩ)
- Testez avec un exemple simple DHT22

## 💡 Améliorations possibles

- [ ] Ajouter un écran OLED
- [ ] Ajouter un bouton physique
- [ ] Implémenter OTA (mise à jour sans fil)
- [ ] Ajouter un mode deep sleep
- [ ] Implémenter MQTT Discovery
- [ ] Ajouter un watchdog

