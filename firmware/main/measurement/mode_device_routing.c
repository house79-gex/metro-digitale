#include "mode_device_routing.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "MODE_ROUTING";
static const char *NVS_NAMESPACE = "mode_routing";
static const char *NVS_UI_NAMESPACE = "ui_settings";

// Routing table (in-memory)
static RoutingConfig routing_table[5]; // One for each mode
static BlitzMode current_blitz_mode = BLITZ_MODE_SEMI_AUTO;

esp_err_t mode_device_routing_init(void) {
    ESP_LOGI(TAG, "Initializing mode-device routing");
    
    // Initialize with defaults
    routing_table[MEASURE_MODE_FERMAVETRO].mode = MEASURE_MODE_FERMAVETRO;
    routing_table[MEASURE_MODE_FERMAVETRO].target_device_type = DEVICE_TYPE_BLITZ;
    routing_table[MEASURE_MODE_FERMAVETRO].target_device_id = 0;
    routing_table[MEASURE_MODE_FERMAVETRO].broadcast_to_all = false;
    
    routing_table[MEASURE_MODE_VETRI].mode = MEASURE_MODE_VETRI;
    routing_table[MEASURE_MODE_VETRI].target_device_type = DEVICE_TYPE_SMARTPHONE;
    routing_table[MEASURE_MODE_VETRI].target_device_id = 0;
    routing_table[MEASURE_MODE_VETRI].broadcast_to_all = false;
    
    routing_table[MEASURE_MODE_ASTINE].mode = MEASURE_MODE_ASTINE;
    routing_table[MEASURE_MODE_ASTINE].target_device_type = DEVICE_TYPE_BLITZ;
    routing_table[MEASURE_MODE_ASTINE].target_device_id = 0;
    routing_table[MEASURE_MODE_ASTINE].broadcast_to_all = false;
    
    routing_table[MEASURE_MODE_CALIBRO].mode = MEASURE_MODE_CALIBRO;
    routing_table[MEASURE_MODE_CALIBRO].target_device_type = DEVICE_TYPE_BLITZ;
    routing_table[MEASURE_MODE_CALIBRO].target_device_id = 0;
    routing_table[MEASURE_MODE_CALIBRO].broadcast_to_all = false;
    
    routing_table[MEASURE_MODE_RILIEVI_SPECIALI].mode = MEASURE_MODE_RILIEVI_SPECIALI;
    routing_table[MEASURE_MODE_RILIEVI_SPECIALI].target_device_type = DEVICE_TYPE_BLITZ;
    routing_table[MEASURE_MODE_RILIEVI_SPECIALI].target_device_id = 0;
    routing_table[MEASURE_MODE_RILIEVI_SPECIALI].broadcast_to_all = false;
    
    // Load from NVS
    mode_device_routing_load_from_nvs();
    
    ESP_LOGI(TAG, "Mode-device routing initialized");
    return ESP_OK;
}

esp_err_t mode_device_routing_set(MeasureMode mode, DeviceType device_type, uint8_t device_id) {
    if (mode >= 5) {
        return ESP_ERR_INVALID_ARG;
    }
    
    routing_table[mode].target_device_type = device_type;
    routing_table[mode].target_device_id = device_id;
    
    ESP_LOGI(TAG, "Set routing: %s -> %s (ID: %d)", 
             mode_device_routing_get_mode_name(mode),
             mode_device_routing_get_device_type_name(device_type),
             device_id);
    
    return ESP_OK;
}

esp_err_t mode_device_routing_get(MeasureMode mode, DeviceType *device_type, uint8_t *device_id) {
    if (mode >= 5 || device_type == NULL || device_id == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    
    *device_type = routing_table[mode].target_device_type;
    *device_id = routing_table[mode].target_device_id;
    
    return ESP_OK;
}

esp_err_t mode_device_routing_set_broadcast(MeasureMode mode, bool broadcast) {
    if (mode >= 5) {
        return ESP_ERR_INVALID_ARG;
    }
    
    routing_table[mode].broadcast_to_all = broadcast;
    ESP_LOGI(TAG, "Set broadcast for %s: %s", 
             mode_device_routing_get_mode_name(mode),
             broadcast ? "enabled" : "disabled");
    
    return ESP_OK;
}

bool mode_device_routing_is_broadcast(MeasureMode mode) {
    if (mode >= 5) {
        return false;
    }
    return routing_table[mode].broadcast_to_all;
}

esp_err_t mode_device_routing_save_to_nvs(void) {
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &nvs_handle);
    
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to open NVS");
        return ret;
    }
    
    // Save routing for each mode
    const char *mode_keys[] = {
        "route_fermavetro",
        "route_vetri",
        "route_astine",
        "route_calibro",
        "route_rilievi"
    };
    
    for (int i = 0; i < 5; i++) {
        uint8_t packed = (routing_table[i].target_device_type & 0x0F) | 
                        ((routing_table[i].target_device_id & 0x0F) << 4);
        nvs_set_u8(nvs_handle, mode_keys[i], packed);
    }
    
    nvs_commit(nvs_handle);
    nvs_close(nvs_handle);
    
    // Save Blitz mode
    ret = nvs_open(NVS_UI_NAMESPACE, NVS_READWRITE, &nvs_handle);
    if (ret == ESP_OK) {
        nvs_set_u8(nvs_handle, "blitz_mode", (uint8_t)current_blitz_mode);
        nvs_commit(nvs_handle);
        nvs_close(nvs_handle);
    }
    
    ESP_LOGI(TAG, "Routing configuration saved to NVS");
    return ESP_OK;
}

esp_err_t mode_device_routing_load_from_nvs(void) {
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs_handle);
    
    if (ret != ESP_OK) {
        ESP_LOGI(TAG, "No saved routing configuration found");
        return ESP_OK; // Use defaults
    }
    
    const char *mode_keys[] = {
        "route_fermavetro",
        "route_vetri",
        "route_astine",
        "route_calibro",
        "route_rilievi"
    };
    
    for (int i = 0; i < 5; i++) {
        uint8_t packed;
        if (nvs_get_u8(nvs_handle, mode_keys[i], &packed) == ESP_OK) {
            routing_table[i].target_device_type = (DeviceType)(packed & 0x0F);
            routing_table[i].target_device_id = (packed >> 4) & 0x0F;
        }
    }
    
    nvs_close(nvs_handle);
    
    // Load Blitz mode
    ret = nvs_open(NVS_UI_NAMESPACE, NVS_READONLY, &nvs_handle);
    if (ret == ESP_OK) {
        uint8_t mode_val;
        if (nvs_get_u8(nvs_handle, "blitz_mode", &mode_val) == ESP_OK) {
            current_blitz_mode = (BlitzMode)mode_val;
        }
        nvs_close(nvs_handle);
    }
    
    ESP_LOGI(TAG, "Routing configuration loaded from NVS");
    return ESP_OK;
}

const char* mode_device_routing_get_mode_name(MeasureMode mode) {
    switch (mode) {
        case MEASURE_MODE_FERMAVETRO:
            return "Fermavetro";
        case MEASURE_MODE_VETRI:
            return "Vetri";
        case MEASURE_MODE_ASTINE:
            return "Astine";
        case MEASURE_MODE_CALIBRO:
            return "Calibro";
        case MEASURE_MODE_RILIEVI_SPECIALI:
            return "Rilievi Speciali";
        default:
            return "Unknown";
    }
}

const char* mode_device_routing_get_device_type_name(DeviceType type) {
    switch (type) {
        case DEVICE_TYPE_NONE:
            return "None";
        case DEVICE_TYPE_BLITZ:
            return "BLITZ";
        case DEVICE_TYPE_SMARTPHONE:
            return "Smartphone";
        case DEVICE_TYPE_PC:
            return "PC";
        case DEVICE_TYPE_CUSTOM:
            return "Custom";
        default:
            return "Unknown";
    }
}

esp_err_t mode_device_routing_set_blitz_mode(BlitzMode mode) {
    current_blitz_mode = mode;
    ESP_LOGI(TAG, "Blitz mode set to: %s", mode_device_routing_get_blitz_mode_name(mode));
    return ESP_OK;
}

BlitzMode mode_device_routing_get_blitz_mode(void) {
    return current_blitz_mode;
}

const char* mode_device_routing_get_blitz_mode_name(BlitzMode mode) {
    switch (mode) {
        case BLITZ_MODE_SEMI_AUTO:
            return "semi_auto";
        case BLITZ_MODE_AUTOMATICO:
            return "automatico";
        default:
            return "unknown";
    }
}
