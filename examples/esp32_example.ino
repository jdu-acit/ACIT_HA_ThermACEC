/**
 * Exemple de code pour carte ACIT ThermACEC
 * Compatible ESP32 / ESP8266
 *
 * Ce code montre comment publier les données de température
 * et recevoir les commandes depuis Home Assistant via MQTT
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Configuration WiFi
const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_MOT_DE_PASSE";

// Configuration MQTT
const char* mqtt_server = "10.0.0.213";
const int mqtt_port = 1883;
const char* mqtt_user = "";  // Optionnel
const char* mqtt_password = "";  // Optionnel

// Topics MQTT
const char* topic_temperature = "acit/thermacec/temperature";
const char* topic_target_temperature = "acit/thermacec/target_temperature";
const char* topic_hvac_mode = "acit/thermacec/hvac_mode";
const char* topic_availability = "acit/thermacec/availability";
const char* topic_set_target = "acit/thermacec/set/target_temperature";
const char* topic_set_mode = "acit/thermacec/set/hvac_mode";

// Configuration capteur DHT
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Variables globales
WiFiClient espClient;
PubSubClient client(espClient);
float currentTemperature = 20.0;
float targetTemperature = 21.0;
String hvacMode = "heat";
unsigned long lastPublish = 0;
const long publishInterval = 10000;  // 10 secondes

void setup() {
  Serial.begin(115200);
  
  // Initialiser le capteur
  dht.begin();
  
  // Connexion WiFi
  setup_wifi();
  
  // Configuration MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
}

void loop() {
  // Maintenir la connexion MQTT
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  // Publier les données périodiquement
  unsigned long now = millis();
  if (now - lastPublish > publishInterval) {
    lastPublish = now;
    publish_data();
  }
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connexion à ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connecté");
  Serial.print("Adresse IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Connexion MQTT...");
    
    String clientId = "ACIT_ThermaControl_";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connecté");
      
      // Publier la disponibilité
      client.publish(topic_availability, "online", true);
      
      // S'abonner aux topics de commande
      client.subscribe(topic_set_target);
      client.subscribe(topic_set_mode);
      
      Serial.println("Abonné aux topics de commande");
    } else {
      Serial.print("échec, rc=");
      Serial.print(client.state());
      Serial.println(" nouvelle tentative dans 5 secondes");
      delay(5000);
    }
  }
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  // Convertir le payload en String
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("Message reçu [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);
  
  // Traiter les commandes
  if (strcmp(topic, topic_set_target) == 0) {
    // Nouvelle consigne de température
    targetTemperature = message.toFloat();
    Serial.print("Nouvelle consigne: ");
    Serial.print(targetTemperature);
    Serial.println("°C");
    
    // Republier immédiatement
    client.publish(topic_target_temperature, String(targetTemperature).c_str());
    
    // TODO: Activer/désactiver le chauffage selon la consigne
    control_heating();
  }
  else if (strcmp(topic, topic_set_mode) == 0) {
    // Nouveau mode HVAC
    hvacMode = message;
    Serial.print("Nouveau mode: ");
    Serial.println(hvacMode);
    
    // Republier immédiatement
    client.publish(topic_hvac_mode, hvacMode.c_str());
    
    // TODO: Gérer le mode (off, heat, cool, auto)
    control_heating();
  }
}

void publish_data() {
  // Lire la température du capteur
  currentTemperature = dht.readTemperature();
  
  if (isnan(currentTemperature)) {
    Serial.println("Erreur de lecture du capteur DHT!");
    return;
  }
  
  Serial.print("Température: ");
  Serial.print(currentTemperature);
  Serial.println("°C");
  
  // Publier les données
  client.publish(topic_temperature, String(currentTemperature, 1).c_str());
  client.publish(topic_target_temperature, String(targetTemperature, 1).c_str());
  client.publish(topic_hvac_mode, hvacMode.c_str());
  client.publish(topic_availability, "online");
}

void control_heating() {
  // Logique de contrôle du chauffage
  if (hvacMode == "off") {
    // Éteindre le chauffage
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("Chauffage: OFF");
  }
  else if (hvacMode == "heat") {
    // Mode chauffage
    if (currentTemperature < targetTemperature - 0.5) {
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("Chauffage: ON");
    }
    else if (currentTemperature > targetTemperature + 0.5) {
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("Chauffage: OFF");
    }
  }
  // TODO: Implémenter les modes cool et auto
}

