/**
 * ACIT ThermACEC - ESP32 Example with HTTP RPC + WebSocket
 * 
 * This example demonstrates the Shelly Gen2-style architecture:
 * - HTTP RPC (JSON-RPC 2.0) for commands
 * - WebSocket for real-time notifications
 * - mDNS for auto-discovery
 * 
 * Compatible with: ESP32
 * Required libraries:
 * - ESPAsyncWebServer
 * - AsyncTCP
 * - ArduinoJson
 * - ESPmDNS
 */

#include <WiFi.h>
#include <ESPmDNS.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Device Configuration
String deviceName = "acit-thermacec";
String macAddress = "";

// Temperature Control
float currentTemperature = 21.8;
float targetTemperature = 22.0;
int heaterLevel = 0;
int fanSpeed = 1;

// Web Server & WebSocket
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// RPC ID counter
int rpcId = 0;

void setup() {
  Serial.begin(115200);
  
  // Get MAC address
  macAddress = WiFi.macAddress();
  macAddress.replace(":", "");
  macAddress.toLowerCase();
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  // Setup mDNS
  String hostname = deviceName + "-" + macAddress;
  if (MDNS.begin(hostname.c_str())) {
    MDNS.addService("acit", "tcp", 80);
    Serial.println("mDNS started: " + hostname + ".local");
  }
  
  // Setup WebSocket
  ws.onEvent(onWsEvent);
  server.addHandler(&ws);
  
  // Setup HTTP RPC endpoint
  server.on("/rpc", HTTP_POST, handleRPC);
  
  // Start server
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  // Simulate temperature reading
  static unsigned long lastRead = 0;
  if (millis() - lastRead > 5000) {
    lastRead = millis();
    
    // Read your temperature sensor here
    // currentTemperature = readTemperatureSensor();
    
    // Simulate heating control
    if (currentTemperature < targetTemperature) {
      heaterLevel = 50;
      fanSpeed = 2;
    } else {
      heaterLevel = 0;
      fanSpeed = 1;
    }
    
    // Send WebSocket notification
    notifyStatus();
  }
  
  ws.cleanupClients();
}

void handleRPC(AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, data, len);
  
  if (error) {
    request->send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    return;
  }
  
  String method = doc["method"];
  int id = doc["id"];
  
  StaticJsonDocument<512> response;
  response["jsonrpc"] = "2.0";
  response["id"] = id;
  
  if (method == "Thermostat.GetStatus") {
    JsonObject result = response.createNestedObject("result");
    result["temperature"] = currentTemperature;
    result["target_temperature"] = targetTemperature;
    result["heater_level"] = heaterLevel;
    result["fan_speed"] = fanSpeed;
    
  } else if (method == "Thermostat.GetConfig") {
    JsonObject result = response.createNestedObject("result");
    result["model"] = "ThermACEC";
    result["version"] = "2.0.0";
    result["manufacturer"] = "ACIT";
    result["mac_address"] = macAddress;
    result["min_temp"] = 5;
    result["max_temp"] = 35;
    JsonArray features = result.createNestedArray("features");
    features.add("heating");
    features.add("fan");
    
  } else if (method == "Thermostat.SetTargetTemp") {
    float temp = doc["params"]["temperature"];
    if (temp >= 5 && temp <= 35) {
      targetTemperature = temp;
      JsonObject result = response.createNestedObject("result");
      result["success"] = true;
      result["target_temperature"] = targetTemperature;
      notifyStatus();
    } else {
      JsonObject error = response.createNestedObject("error");
      error["code"] = -32602;
      error["message"] = "Invalid temperature range";
    }

  } else {
    JsonObject error = response.createNestedObject("error");
    error["code"] = -32601;
    error["message"] = "Method not found";
  }

  String output;
  serializeJson(response, output);
  request->send(200, "application/json", output);
}

void notifyStatus() {
  StaticJsonDocument<256> doc;
  doc["jsonrpc"] = "2.0";
  doc["method"] = "NotifyStatus";

  JsonObject params = doc.createNestedObject("params");
  params["temperature"] = currentTemperature;
  params["target_temperature"] = targetTemperature;
  params["heater_level"] = heaterLevel;
  params["fan_speed"] = fanSpeed;

  String output;
  serializeJson(doc, output);
  ws.textAll(output);
}

void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
               AwsEventType type, void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    Serial.printf("WebSocket client #%u connected\n", client->id());
    // Send initial status
    notifyStatus();
  } else if (type == WS_EVT_DISCONNECT) {
    Serial.printf("WebSocket client #%u disconnected\n", client->id());
  }
}

