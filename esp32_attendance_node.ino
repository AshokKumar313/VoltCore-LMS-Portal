/**
 * ========================================================================================
 * VoltCore Apex Academia - ESP32 Smart Lab Attendance Node
 * Anna University / MIT Campus - Department of Electronics Engineering
 * ----------------------------------------------------------------------------------------
 * File: esp32_attendance_node.ino
 * Target: ESP32 Dev Module (WROOM-32 / ESP32-S3)
 * Compatible with: Physical Hardware (MFRC522 SPI) & Wokwi Online Simulation
 * Features:
 *   - Auto Wi-Fi Connection (supports Wokwi-GUEST for simulator & campus LAN)
 *   - Simulated Student RFID Card Cycles (Ashok Kumar A, Kavitha Raman, etc.)
 *   - Physical MFRC522 SPI pinout mapping (GPIO 5, 18, 19, 22, 23)
 *   - Non-blocking FreeRTOS / millis() scan dispatch engine
 *   - HTTP POST REST Client with structured JSON payloads
 *   - On-board Status LED diagnostics (GPIO 2)
 * ========================================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>

// ==========================================
// 1. NETWORK & TELEMETRY CONFIGURATION
// ==========================================
// Note: For Wokwi Simulation, SSID "Wokwi-GUEST" with empty password works automatically.
const char* WIFI_SSID     = "Wokwi-GUEST"; 
const char* WIFI_PASSWORD = ""; 

// IP Address of the host machine running attendance_server.py (Port 5000)
// In Wokwi simulation, use your public IP or ngrok/local bridge, or test against local LAN
const char* SERVER_ENDPOINT = "http://10.0.2.2:5000/api/attendance"; // Wokwi NAT gateway to localhost

// Node Hardware Identifier
const char* NODE_ID = "ESP32_MIT_IOT_LAB_01";
const char* LAB_LOCATION = "MIT Chromepet - Embedded Systems Lab 304";

// ==========================================
// 2. PIN DEFINITIONS
// ==========================================
#define STATUS_LED_PIN    2   // Built-in Blue LED on ESP32 Dev Module
#define MANUAL_SCAN_BTN   0   // Boot button on GPIO 0 for instant manual scan trigger

// MFRC522 Hardware SPI Pins (when attached)
#define SS_PIN            5   // SPI Chip Select (SDA)
#define RST_PIN           22  // Reset pin
#define SCK_PIN           18  // SPI Clock
#define MOSI_PIN          23  // SPI Master Out Slave In
#define MISO_PIN          19  // SPI Master In Slave Out

// ==========================================
// 3. STUDENT ROSTER SIMULATION DATA
// ==========================================
struct StudentCard {
    const char* student_id;
    const char* student_name;
    const char* rfid_uid;
    const char* department;
};

const StudentCard ROSTER[] = {
    {
        "2023MITEC042",
        "Ashok Kumar A",
        "E2 80 6F 3B",
        "Dept of Electronics Engg"
    },
    {
        "2023MITEC015",
        "Kavitha Raman",
        "C3 4D 8A 11",
        "Dept of Electronics Engg"
    },
    {
        "MIT-FAC-019",
        "Dr. K. S. Parthasarathy",
        "A4 12 99 F0",
        "Faculty / Mentor"
    },
    {
        "UNKNOWN-TAG-99",
        "Unregistered Visitor",
        "FF FF FF FF",
        "Guest"
    }
};

const int ROSTER_SIZE = sizeof(ROSTER) / sizeof(ROSTER[0]);
int current_card_index = 0;

// Non-blocking timer variables
unsigned long lastScanTime = 0;
const unsigned long SCAN_INTERVAL_MS = 15000; // Auto-simulate tap every 15 seconds

// ==========================================
// 4. FUNCTION PROTOTYPES
// ==========================================
void connectToWiFi();
bool dispatchAttendanceRecord(const StudentCard& card);
void flashLed(int times, int delayMs);
void printBanner();

// ==========================================
// 5. SETUP ROUTINE
// ==========================================
void setup() {
    Serial.begin(115200);
    delay(1000);

    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);

    pinMode(MANUAL_SCAN_BTN, INPUT_PULLUP);

    printBanner();
    connectToWiFi();

    Serial.println(F("[SYSTEM] Initialization complete. Scan simulation loop active."));
    Serial.println(F("[SYSTEM] Tip: Press the onboard BOOT button (GPIO 0) for an instant tap."));
    Serial.println(F("----------------------------------------------------------------------\n"));
}

// ==========================================
// 6. MAIN LOOP
// ==========================================
void loop() {
    unsigned long currentMillis = millis();

    // Check Wi-Fi link health
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println(F("[WIFI WARN] Connection lost. Attempting reconnection..."));
        connectToWiFi();
    }

    // Check if manual trigger button pressed
    bool manualTrigger = (digitalRead(MANUAL_SCAN_BTN) == LOW);

    if (manualTrigger || (currentMillis - lastScanTime >= SCAN_INTERVAL_MS)) {
        lastScanTime = currentMillis;

        // Select student card
        const StudentCard& activeCard = ROSTER[current_card_index];
        Serial.println(F("\n========================================================"));
        Serial.printf("[CARD DETECTED] Simulated RFID Tap: %s\n", activeCard.rfid_uid);
        Serial.printf("  Student Name : %s\n", activeCard.student_name);
        Serial.printf("  Roll Number  : %s\n", activeCard.student_id);
        Serial.printf("  Department   : %s\n", activeCard.department);
        Serial.println(F("========================================================"));

        // Transmit HTTP POST payload
        bool success = dispatchAttendanceRecord(activeCard);

        if (success) {
            flashLed(2, 80); // Quick double flash for success
        } else {
            flashLed(5, 50); // Rapid blink for network warning
        }

        // Advance to next card in roster
        current_card_index = (current_card_index + 1) % ROSTER_SIZE;

        // Debounce if button was held
        if (manualTrigger) {
            delay(400);
        }
    }

    delay(50); // Low CPU power pause
}

// ==========================================
// 7. WI-FI CONNECTION HANDLER
// ==========================================
void connectToWiFi() {
    Serial.printf("[WIFI] Connecting to SSID: '%s' ...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 25) {
        digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN)); // Toggle LED
        delay(400);
        Serial.print(F("."));
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        digitalWrite(STATUS_LED_PIN, HIGH);
        Serial.println(F("\n[WIFI] Connected Successfully!"));
        Serial.printf("  IP Address   : %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("  Subnet Mask  : %s\n", WiFi.subnetMask().toString().c_str());
        Serial.printf("  Gateway IP   : %s\n", WiFi.gatewayIP().toString().c_str());
        Serial.printf("  RSSI Signal  : %d dBm\n", WiFi.RSSI());
        Serial.printf("  MAC Address  : %s\n", WiFi.macAddress().c_str());
    } else {
        digitalWrite(STATUS_LED_PIN, LOW);
        Serial.println(F("\n[WIFI ERROR] Failed to connect to access point. Will retry in loop."));
    }
}

// ==========================================
// 8. HTTP REST DISPATCH LOGIC
// ==========================================
bool dispatchAttendanceRecord(const StudentCard& card) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println(F("[HTTP ERROR] Cannot dispatch. Wi-Fi not connected."));
        return false;
    }

    HTTPClient http;
    http.begin(SERVER_ENDPOINT);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Node-ID", NODE_ID);
    http.setTimeout(4000); // 4 second timeout

    // Construct JSON payload
    char jsonBuffer[384];
    snprintf(
        jsonBuffer,
        sizeof(jsonBuffer),
        "{\"student_id\":\"%s\",\"node_id\":\"%s\",\"rfid_uid\":\"%s\",\"rssi\":%d}",
        card.student_id,
        NODE_ID,
        card.rfid_uid,
        WiFi.RSSI()
    );

    Serial.printf("[HTTP POST] Target: %s\n", SERVER_ENDPOINT);
    Serial.printf("[PAYLOAD]   %s\n", jsonBuffer);

    int httpResponseCode = http.POST((uint8_t*)jsonBuffer, strlen(jsonBuffer));

    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.printf("[HTTP RES]  Code: %d | Response: %s\n", httpResponseCode, response.c_str());
        http.end();
        return (httpResponseCode == 200 || httpResponseCode == 201);
    } else {
        Serial.printf("[HTTP FAIL] Connection error: %s (Code: %d)\n", 
            http.errorToString(httpResponseCode).c_str(), 
            httpResponseCode
        );
        http.end();
        return false;
    }
}

// ==========================================
// 9. HELPER FUNCTIONS
// ==========================================
void flashLed(int times, int delayMs) {
    for (int i = 0; i < times; i++) {
        digitalWrite(STATUS_LED_PIN, HIGH);
        delay(delayMs);
        digitalWrite(STATUS_LED_PIN, LOW);
        delay(delayMs);
    }
}

void printBanner() {
    Serial.println(F("\n"));
    Serial.println(F("======================================================================"));
    Serial.println(F("       VOLTCORE APEX ACADEMIA - ESP32 IOT ATTENDANCE NODE             "));
    Serial.println(F("     Madras Institute of Technology (MIT) Campus, Anna University     "));
    Serial.println(F("              Department of Electronics Engineering                   "));
    Serial.println(F("======================================================================"));
    Serial.printf("  Target Node ID  : %s\n", NODE_ID);
    Serial.printf("  Lab Facility    : %s\n", LAB_LOCATION);
    Serial.println(F("======================================================================\n"));
}

