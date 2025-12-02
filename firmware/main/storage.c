#include "storage.h"
#include "nvs_flash.h"
#include "esp_log.h"

static const char *TAG = "STORAGE";

esp_err_t storage_init(void) {
    ESP_LOGI(TAG, "Inizializzazione NVS...");
    
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        // NVS partition was truncated and needs to be erased
        ESP_LOGW(TAG, "NVS partition necessita di essere cancellata");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Errore init NVS: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ESP_LOGI(TAG, "NVS inizializzato con successo");
    return ESP_OK;
}
