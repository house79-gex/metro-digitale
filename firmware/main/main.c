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

static const char *TAG = "MAIN";

// Mutex per proteggere configurazione e stato
static SemaphoreHandle_t config_mutex = NULL;
static SemaphoreHandle_t state_mutex = NULL;

void app_main(void) {
    ESP_LOGI(TAG, "=== Metro Digitale Multifunzione ===");
    ESP_LOGI(TAG, "Avvio sistema...");
    
    // Crea mutex
    config_mutex = xSemaphoreCreateMutex();
    state_mutex = xSemaphoreCreateMutex();
    
    if (config_mutex == NULL || state_mutex == NULL) {
        ESP_LOGE(TAG, "Errore creazione mutex");
        return;
    }
    
    // Inizializza NVS
    ESP_ERROR_CHECK(storage_init());
    
    // Inizializza configurazione
    config_load_from_nvs(&g_config);
    
    // Inizializza stato runtime
    memset(&g_state, 0, sizeof(RuntimeState));
    g_state.screen_active = true;
    g_state.last_activity_ms = esp_log_timestamp();
    
    // Inizializza encoder
    ESP_ERROR_CHECK(encoder_init());
    
    // Inizializza Bluetooth
    if (g_config.bluetooth_enabled) {
        ESP_ERROR_CHECK(bluetooth_init());
    } else {
        ESP_LOGI(TAG, "Bluetooth disabilitato");
    }
    
    // Inizializza UI (richiede LVGL inizializzato prima - qui semplificato)
    // In una implementazione reale, prima va inizializzato LVGL con driver display
    // ESP_ERROR_CHECK(ui_manager_init());
    ESP_LOGI(TAG, "UI init placeholder (richiede LVGL driver)");
    
    // Task encoder su Core 1 (100Hz)
    xTaskCreatePinnedToCore(
        encoder_task,
        "encoder_task",
        4096,
        NULL,
        10,
        NULL,
        1  // Core 1
    );
    
    // Task Bluetooth su Core 0
    if (g_config.bluetooth_enabled) {
        xTaskCreatePinnedToCore(
            bluetooth_task,
            "bluetooth_task",
            4096,
            NULL,
            5,
            NULL,
            0  // Core 0
        );
    }
    
    // Task UI su Core 0 (50fps)
    // xTaskCreatePinnedToCore(
    //     ui_task,
    //     "ui_task",
    //     8192,
    //     NULL,
    //     5,
    //     NULL,
    //     0  // Core 0
    // );
    
    ESP_LOGI(TAG, "Sistema avviato con successo");
    ESP_LOGI(TAG, "Modalità: %d", g_config.modalita_corrente);
    ESP_LOGI(TAG, "Puntali: %d, Materiali: %d, Astine: %d", 
             g_config.num_puntali, g_config.num_materiali, g_config.num_astine);
    
    // Main loop
    while (1) {
        // Qui si possono gestire task di sistema, watchdog, ecc.
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // Log periodico dello stato
        ESP_LOGI(TAG, "Posizione: %.2f mm | BT: %s | Zero: %s",
                 g_state.position_mm,
                 g_state.bt_connected ? "CONN" : "DISC",
                 g_state.is_zeroed ? "SI" : "NO");
    }
}
