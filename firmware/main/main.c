#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "esp_system.h"

#include "config.h"
#include "storage.h"
#include "encoder.h"
#include "bluetooth.h"
#include "ui/ui_manager.h"

// New subsystems
#include "hardware/hardware_gpio.h"
#include "hardware/encoder_reader.h"
#include "hardware/sd_card.h"
#include "feedback/buzzer_feedback.h"
#include "feedback/led_feedback.h"
#include "puntali/puntale_database.h"
#include "measurement/measure_calculator.h"
#include "measurement/mode_device_routing.h"
#include "measurement/measure_sender.h"
#include "ble/ble_server.h"
#include "ble/ble_multi_device.h"

static const char *TAG = "MAIN";

// Mutex per proteggere configurazione e stato
static SemaphoreHandle_t config_mutex = NULL;
static SemaphoreHandle_t state_mutex = NULL;

// Current measurement state
static struct {
    MeasureMode current_mode;
    Puntale *tip_left;
    Puntale *tip_right;
    float encoder_position_mm;
    bool zeroed;
} measurement_state = {
    .current_mode = MEASURE_MODE_FERMAVETRO,
    .tip_left = NULL,
    .tip_right = NULL,
    .encoder_position_mm = 0.0f,
    .zeroed = false
};

// Button callback - triggered when physical SEND button is pressed
static void on_send_button_pressed(void) {
    ESP_LOGI(TAG, "SEND button pressed!");
    
    // Play button feedback
    buzzer_feedback_play(FEEDBACK_BUTTON_PRESS);
    led_feedback_play(LED_PATTERN_BUTTON_PRESS);
    
    // Prepare measurement input
    MeasurementInput input = {
        .encoder_raw_mm = measurement_state.encoder_position_mm,
        .tip_left = measurement_state.tip_left,
        .tip_right = measurement_state.tip_right,
        .correction_factor = 1.0f,
        .additional_offset_mm = 0.0f
    };
    
    // Calculate measurement
    MeasurementResult result;
    esp_err_t ret = measure_calculator_calculate(&input, &result);
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Measurement calculated: %.2f mm", result.net_measurement_mm);
        ESP_LOGI(TAG, "Formula: %s", result.formula_text);
        
        // Send measurement via BLE with routing
        ret = measure_sender_send(measurement_state.current_mode, 
                                 &result, 
                                 measurement_state.tip_left,
                                 measurement_state.tip_right);
        
        if (ret == ESP_OK) {
            // Success feedback
            buzzer_feedback_play(FEEDBACK_SUCCESS);
            led_feedback_play(LED_PATTERN_SUCCESS);
            ESP_LOGI(TAG, "Measurement sent successfully");
        } else {
            // Error feedback
            buzzer_feedback_play(FEEDBACK_ERROR);
            led_feedback_play(LED_PATTERN_ERROR);
            ESP_LOGE(TAG, "Failed to send measurement");
        }
    } else {
        // Error feedback
        buzzer_feedback_play(FEEDBACK_ERROR);
        led_feedback_play(LED_PATTERN_ERROR);
        ESP_LOGE(TAG, "Measurement calculation failed");
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "=== Metro Digitale Multifunzione - Complete Firmware ===");
    ESP_LOGI(TAG, "Avvio sistema...");
    
    // Crea mutex
    config_mutex = xSemaphoreCreateMutex();
    state_mutex = xSemaphoreCreateMutex();
    
    if (config_mutex == NULL || state_mutex == NULL) {
        ESP_LOGE(TAG, "Errore creazione mutex");
        return;
    }
    
    // Inizializza NVS
    ESP_LOGI(TAG, "Initializing NVS...");
    ESP_ERROR_CHECK(storage_init());
    
    // Initialize hardware GPIO (button, LED, buzzer)
    ESP_LOGI(TAG, "Initializing hardware GPIO...");
    ESP_ERROR_CHECK(hardware_gpio_init());
    
    // Register button callback
    hardware_button_set_callback(on_send_button_pressed);
    
    // Initialize feedback systems
    ESP_LOGI(TAG, "Initializing feedback systems...");
    ESP_ERROR_CHECK(buzzer_feedback_init());
    ESP_ERROR_CHECK(led_feedback_init());
    
    // Play startup tone
    buzzer_feedback_play(FEEDBACK_BT_CONNECTED);
    
    // Initialize AS5600 magnetic encoder
    ESP_LOGI(TAG, "Initializing AS5600 encoder...");
    esp_err_t ret = encoder_reader_init();
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "AS5600 encoder init failed, using fallback encoder");
        // Fallback to existing encoder implementation
        ESP_ERROR_CHECK(encoder_init());
    }
    
    // Initialize SD card
    ESP_LOGI(TAG, "Initializing SD card...");
    ret = sd_card_init();
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "SD card not available");
    }
    
    // Initialize tip database
    ESP_LOGI(TAG, "Initializing tip database...");
    ESP_ERROR_CHECK(puntale_database_init());
    
    // Load default tips for current mode
    measurement_state.tip_left = puntale_database_get_by_index(0);
    measurement_state.tip_right = puntale_database_get_by_index(0);
    
    // Initialize measurement routing
    ESP_LOGI(TAG, "Initializing mode-device routing...");
    ESP_ERROR_CHECK(mode_device_routing_init());
    
    // Initialize BLE system
    ESP_LOGI(TAG, "Initializing BLE system...");
    ESP_ERROR_CHECK(ble_server_init());
    ESP_ERROR_CHECK(ble_multi_device_init());
    
    // Start BLE advertising
    ESP_ERROR_CHECK(ble_server_start_advertising());
    
    // Inizializza configurazione (legacy)
    config_load_from_nvs(&g_config);
    
    // Inizializza stato runtime
    memset(&g_state, 0, sizeof(RuntimeState));
    g_state.screen_active = true;
    g_state.last_activity_ms = esp_log_timestamp();
    
    // Inizializza UI (richiede LVGL inizializzato prima - qui semplificato)
    // In una implementazione reale, prima va inizializzato LVGL con driver display
    // ESP_ERROR_CHECK(ui_manager_init());
    ESP_LOGI(TAG, "UI init placeholder (richiede LVGL driver)");
    
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "Sistema avviato con successo!");
    ESP_LOGI(TAG, "Modalità: %s", mode_device_routing_get_mode_name(measurement_state.current_mode));
    ESP_LOGI(TAG, "Tips loaded: %d", puntale_database_get_count());
    ESP_LOGI(TAG, "BLE advertising: %s", ble_server_is_advertising() ? "ACTIVE" : "INACTIVE");
    ESP_LOGI(TAG, "========================================");
    
    // Main loop
    while (1) {
        // Update encoder position
        uint16_t angle;
        if (encoder_reader_get_angle(&angle) == ESP_OK) {
            // Convert angle to mm (calibration factor should be configured)
            float calibration_factor = 0.1f; // Example: 0.1mm per encoder count
            measurement_state.encoder_position_mm = encoder_reader_angle_to_mm(angle, calibration_factor);
        } else {
            // Fallback to legacy encoder
            measurement_state.encoder_position_mm = g_state.position_mm;
        }
        
        // Log periodico dello stato
        if (esp_log_timestamp() % 5000 < 100) { // Every 5 seconds
            ESP_LOGI(TAG, "Status: Position=%.2f mm | BT devices=%d | Mode=%s",
                     measurement_state.encoder_position_mm,
                     ble_server_get_connection_count(),
                     mode_device_routing_get_mode_name(measurement_state.current_mode));
        }
        
        vTaskDelay(pdMS_TO_TICKS(100)); // 10Hz update
    }
}
