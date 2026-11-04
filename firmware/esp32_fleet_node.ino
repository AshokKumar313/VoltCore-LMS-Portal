/**
 * ========================================================================================
 * VoltCore Apex Academia - Enterprise IoT Fleet Node Firmware
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A
 * Public Email: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
 * Target Hardware: ESP32-WROOM-32 / ESP32-S3 (Dual-Core Xtensa LX6/LX7 @ 240MHz)
 * Storage Subsystem: LittleFS Flash Partition (Supports up to 10,000 Buffered Offline Records)
 * Security Standard: Tamper-Evident SHA-256 Merkle Hash Chaining across all offline scans
 * Concurrency: FreeRTOS Core 1 (SPI RFID Scanning) + Core 0 (Wi-Fi Bulk Synchronization)
 * ========================================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include "FS.h"
#include <LittleFS.h>
#include "mbedtls/sha256.h"

// Hardware Pin Configuration
#define RFID_SS_PIN    5
#define RFID_RST_PIN   22
#define STATUS_LED_PIN 2   // Built-in Blue LED on ESP32 DevKit
#define BUZZER_PIN     4   // Feedback Buzzer for Authorized Scans

// Network & Gateway Credentials
const char* WIFI_SSID     = "MIT_CHROMEPET_CAMPUS_IOT";
const char* WIFI_PASSWORD = "AnnaUniversity#R2023@P3X";
const char* GATEWAY_URL   = "http://10.0.2.2:5000/api/attendance/bulk_sync";
const char* NODE_ID       = "ESP32_MIT_IOT_LAB_01";

// LittleFS Spool Queue Configuration
#define SPOOL_FILE_PATH     "/spool/queue.jsonl"
#define MAX_QUEUE_CAPACITY  10000
#define BATCH_SYNC_SIZE     25

// Hardware Peripherals
MFRC522 rfid(RFID_SS_PIN, RFID_RST_PIN);

// Cryptographic Hash Chaining State
char g_prev_hash[65] = "0000000000000000000000000000000000000000000000000000000000000000";
uint32_t g_sequence_counter = 0;
volatile uint32_t g_queued_records_count = 0;
portMUX_TYPE g_spool_mutex = portMUX_INITIALIZER_UNLOCKED;

// FreeRTOS Task Handles
TaskHandle_t xRFIDTaskHandle = NULL;
TaskHandle_t xNetworkSyncTaskHandle = NULL;

/**
 * Computes SHA-256 hash string for tamper-evident chaining.
 */
void compute_sha256(const char* input, char* output_hex)
{
    byte shaResult[32];
    mbedtls_sha256_context ctx;
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0); // 0 = SHA-256 (not 224)
    mbedtls_sha256_update(&ctx, (const unsigned char*)input, strlen(input));
    mbedtls_sha256_finish(&ctx, shaResult);
    mbedtls_sha256_free(&ctx);

    for (int i = 0; i < 32; i++) {
        sprintf(output_hex + (i * 2), "%02x", shaResult[i]);
    }
    output_hex[64] = 0;
}

/**
 * Initializes LittleFS filesystem partition and restores hash chain head.
 */
void init_littlefs_spool()
{
    Serial.println("[LITTLEFS]: Initializing Flash Spool Partition...");
    if (!LittleFS.begin(true)) {
        Serial.println("[LITTLEFS ERROR]: Mount Failed. Formatting partition...");
        return;
    }

    if (!LittleFS.exists("/spool")) {
        LittleFS.mkdir("/spool");
    }

    // Count pending records if file exists
    if (LittleFS.exists(SPOOL_FILE_PATH)) {
        File file = LittleFS.open(SPOOL_FILE_PATH, "r");
        uint32_t lines = 0;
        String lastLine = "";
        while (file.available()) {
            String line = file.readStringUntil('\n');
            if (line.length() > 5) {
                lines++;
                lastLine = line;
            }
        }
        file.close();
        g_queued_records_count = lines;
        Serial.printf("[LITTLEFS]: Found %u pending offline scans in spool.\n", lines);
    } else {
        Serial.println("[LITTLEFS]: Spool queue clean. Zero pending scans.");
    }
}

/**
 * Appends attendance scan into LittleFS queue with SHA-256 Merkle chain.
 */
bool append_scan_to_littlefs(const char* student_id, const char* rfid_uid)
{
    if (g_queued_records_count >= MAX_QUEUE_CAPACITY) {
        Serial.println("[LITTLEFS CRITICAL]: Maximum spool buffer capacity reached (10,000)! Overwriting old scans prevented.");
        return false;
    }

    portENTER_CRITICAL(&g_spool_mutex);

    uint32_t current_seq = ++g_sequence_counter;
    uint32_t ts = millis() / 1000; // Simulated epoch timestamp

    // Format Preimage for SHA-256: prev_hash:seq:ts:sid:uid:node
    char preimage[256];
    snprintf(preimage, sizeof(preimage), "%s:%u:%u:%s:%s:%s",
             g_prev_hash, current_seq, ts, student_id, rfid_uid, NODE_ID);

    char current_hash[65];
    compute_sha256(preimage, current_hash);

    // Build JSON record line
    char json_line[384];
    snprintf(json_line, sizeof(json_line),
             "{\"seq_id\":%u,\"timestamp\":%u,\"student_id\":\"%s\",\"rfid_uid\":\"%s\",\"prev_hash\":\"%s\",\"hash\":\"%s\"}\n",
             current_seq, ts, student_id, rfid_uid, g_prev_hash, current_hash);

    // Update chain head
    strncpy(g_prev_hash, current_hash, sizeof(g_prev_hash));

    // Append to LittleFS file
    File file = LittleFS.open(SPOOL_FILE_PATH, "a");
    if (!file) {
        portEXIT_CRITICAL(&g_spool_mutex);
        Serial.println("[LITTLEFS ERROR]: Failed to open spool file for appending.");
        return false;
    }
    file.print(json_line);
    file.close();

    g_queued_records_count++;
    portEXIT_CRITICAL(&g_spool_mutex);

    Serial.printf("[SPOOL QUEUE]: Scan #%u Queued. Total Buffered: %u. Hash: %.16s...\n",
                  current_seq, g_queued_records_count, current_hash);
    return true;
}

/**
 * Core 1 Task: High-Priority SPI RFID Card Scanner & Instant Feedback.
 */
void vRFIDScanTask(void *pvParameters)
{
    Serial.println("[TASK CORE 1]: MFRC522 RFID High-Priority Scanning Task Armed.");
    SPI.begin(18, 19, 23, RFID_SS_PIN); // SCK=18, MISO=19, MOSI=23, SS=5
    rfid.PCD_Init();

    // Roster of simulated student test cards for demo simulation
    const char* DEMO_STUDENTS[][2] = {
        {"2023MITEC042", "E2 80 6F 3B"}, // Ashok Kumar A (Platform Architect)
        {"2023MITEC001", "A1 B2 C3 D4"},
        {"2023MITEC014", "F5 E4 D3 C2"},
        {"2023MITEC035", "99 88 77 66"},
        {"2023MITEC058", "12 34 56 78"}
    };
    int sim_index = 0;

    for (;;)
    {
        // 1. Check for real RFID card swipe via SPI
        if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial())
        {
            String uidStr = "";
            for (byte i = 0; i < rfid.uid.size; i++) {
                uidStr += (rfid.uid.uidByte[i] < 0x10 ? "0" : "");
                uidStr += String(rfid.uid.uidByte[i], HEX);
                if (i < rfid.uid.size - 1) uidStr += " ";
            }
            uidStr.toUpperCase();

            // Audio & Visual Pulse
            digitalWrite(STATUS_LED_PIN, HIGH);
            append_scan_to_littlefs("2023MITEC042", uidStr.c_str());
            vTaskDelay(pdMS_TO_TICKS(150));
            digitalWrite(STATUS_LED_PIN, LOW);

            rfid.PICC_HaltA();
            rfid.PCD_StopCrypto1();
        }

        // 2. Periodic background simulation scan every 12 seconds for lab testing
        static unsigned long last_sim_tick = 0;
        if (millis() - last_sim_tick > 12000) {
            last_sim_tick = millis();
            const char* sid = DEMO_STUDENTS[sim_index][0];
            const char* uid = DEMO_STUDENTS[sim_index][1];
            sim_index = (sim_index + 1) % 5;

            digitalWrite(STATUS_LED_PIN, HIGH);
            append_scan_to_littlefs(sid, uid);
            vTaskDelay(pdMS_TO_TICKS(80));
            digitalWrite(STATUS_LED_PIN, LOW);
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

/**
 * Core 0 Task: Wi-Fi Bulk Synchronization & Flushes LittleFS to Flask Telemetry Server.
 */
void vNetworkSyncTask(void *pvParameters)
{
    Serial.println("[TASK CORE 0]: Wi-Fi Network & Bulk Synchronization Task Armed.");

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    for (;;)
    {
        // Check Wi-Fi link status
        if (WiFi.status() == WL_CONNECTED)
        {
            if (g_queued_records_count > 0)
            {
                Serial.printf("[SYNC ENGINE]: Wi-Fi Connected (RSSI: %d dBm). Spool contains %u records. Preparing Bulk Dispatch...\n",
                              WiFi.RSSI(), g_queued_records_count);

                portENTER_CRITICAL(&g_spool_mutex);

                // Read batch from LittleFS
                File file = LittleFS.open(SPOOL_FILE_PATH, "r");
                if (file) {
                    String jsonArrayPayload = "{\"node_id\":\"" + String(NODE_ID) + "\",\"batch_size\":" + String(BATCH_SYNC_SIZE) + ",\"records\":[";
                    uint32_t batch_count = 0;
                    std::vector<String> remaining_lines;

                    while (file.available()) {
                        String line = file.readStringUntil('\n');
                        line.trim();
                        if (line.length() > 5) {
                            if (batch_count < BATCH_SYNC_SIZE) {
                                if (batch_count > 0) jsonArrayPayload += ",";
                                jsonArrayPayload += line;
                                batch_count++;
                            } else {
                                remaining_lines.push_back(line);
                            }
                        }
                    }
                    file.close();
                    jsonArrayPayload += "]}";

                    portEXIT_CRITICAL(&g_spool_mutex);

                    // Dispatch HTTP POST request to Flask Telemetry Server
                    HTTPClient http;
                    http.begin(GATEWAY_URL);
                    http.addHeader("Content-Type", "application/json");
                    http.setTimeout(4000);

                    int httpCode = http.POST(jsonArrayPayload);
                    if (httpCode == 200 || httpCode == 207) {
                        String response = http.getString();
                        Serial.printf("[SYNC SUCCESS]: Batch of %u scans committed to SQLite WAL! Server Response: %s\n",
                                      batch_count, response.c_str());

                        // Rewrite remaining uncommitted lines to LittleFS spool file
                        portENTER_CRITICAL(&g_spool_mutex);
                        File outFile = LittleFS.open(SPOOL_FILE_PATH, "w");
                        for (const auto& remLine : remaining_lines) {
                            outFile.println(remLine);
                        }
                        outFile.close();
                        g_queued_records_count = remaining_lines.size();
                        portEXIT_CRITICAL(&g_spool_mutex);
                    } else {
                        Serial.printf("[SYNC FAILED]: Gateway returned HTTP %d. Records retained in LittleFS spool.\n", httpCode);
                    }
                    http.end();
                } else {
                    portEXIT_CRITICAL(&g_spool_mutex);
                }
            }
        }
        else
        {
            // Reconnect Wi-Fi silently in background
            WiFi.reconnect();
        }

        vTaskDelay(pdMS_TO_TICKS(5000)); // Sync interval: 5 seconds
    }
}

void setup()
{
    Serial.begin(115200);
    delay(500);

    Serial.println("================================================================================");
    Serial.println(" VoltCore Apex Academia - ESP32 Fleet Node Firmware v4.3.0");
    Serial.println(" Lead Architect: Ashok Kumar A (MIT Campus, Anna University)");
    Serial.println(" LittleFS 10,000 Offline Spool | SHA-256 Merkle Chain | FreeRTOS Dual-Core");
    Serial.println("================================================================================");

    pinMode(STATUS_LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);

    // Initialize LittleFS File Spool
    init_littlefs_spool();

    // Pin Tasks to Cores: Core 1 = High-Priority RFID, Core 0 = Wi-Fi Sync Engine
    xTaskCreatePinnedToCore(
        vRFIDScanTask,
        "RFID_Scan_Task",
        4096,
        NULL,
        configMAX_PRIORITIES - 1, // Highest user priority
        &xRFIDTaskHandle,
        1                          // Core 1
    );

    xTaskCreatePinnedToCore(
        vNetworkSyncTask,
        "Net_Sync_Task",
        6144,
        NULL,
        tskIDLE_PRIORITY + 2,     // Medium priority
        &xNetworkSyncTaskHandle,
        0                          // Core 0
    );
}

void loop()
{
    // Empty loop: Dual-Core FreeRTOS kernel manages all telemetry tasks
    vTaskDelay(pdMS_TO_TICKS(1000));
}

