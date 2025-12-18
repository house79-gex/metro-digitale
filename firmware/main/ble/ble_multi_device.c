#include "ble_multi_device.h"
#include "ble_server.h"
#include "../feedback/buzzer_feedback.h"
#include "../feedback/led_feedback.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string.h>
#include <stdio.h>

static const char *TAG = "BLE_MULTI_DEV";
static const char *NVS_NAMESPACE = "devices";

// Device database
static DeviceInfo devices[MAX_DEVICES];
static uint8_t device_count = 0;

// Connection ID to device ID mapping
static struct {
    uint16_t conn_id;
    uint8_t device_id;
} conn_map[MAX_DEVICES];

esp_err_t ble_multi_device_init(void) {
    ESP_LOGI(TAG, "Initializing multi-device manager");
    
    memset(devices, 0, sizeof(devices));
    memset(conn_map, 0xFF, sizeof(conn_map));
    device_count = 0;
    
    // Load saved devices from NVS
    ble_multi_device_load_from_nvs();
    
    ESP_LOGI(TAG, "Multi-device manager initialized");
    return ESP_OK;
}

void ble_multi_device_on_connect(uint16_t conn_id, const uint8_t *mac_addr) {
    ESP_LOGI(TAG, "New device connected: conn_id=%d", conn_id);
    
    if (device_count >= MAX_DEVICES) {
        ESP_LOGW(TAG, "Maximum devices reached, ignoring connection");
        return;
    }
    
    // Find available device slot
    uint8_t device_id = 0;
    for (device_id = 0; device_id < MAX_DEVICES; device_id++) {
        if (!devices[device_id].is_connected) {
            break;
        }
    }
    
    if (device_id >= MAX_DEVICES) {
        ESP_LOGW(TAG, "No available device slot");
        return;
    }
    
    // Initialize device info
    devices[device_id].device_id = device_id;
    devices[device_id].is_connected = true;
    devices[device_id].device_type = DEVICE_TYPE_NONE; // Unknown until identified
    devices[device_id].last_activity_timestamp = esp_log_timestamp();
    
    // Store MAC address
    snprintf(devices[device_id].mac_address, sizeof(devices[device_id].mac_address),
             "%02X:%02X:%02X:%02X:%02X:%02X",
             mac_addr[0], mac_addr[1], mac_addr[2],
             mac_addr[3], mac_addr[4], mac_addr[5]);
    
    snprintf(devices[device_id].device_name, sizeof(devices[device_id].device_name),
             "Device-%d", device_id);
    
    // Map connection ID to device ID
    for (int i = 0; i < MAX_DEVICES; i++) {
        if (conn_map[i].conn_id == 0xFFFF) {
            conn_map[i].conn_id = conn_id;
            conn_map[i].device_id = device_id;
            break;
        }
    }
    
    device_count++;
    
    // Play connection feedback
    buzzer_feedback_play(FEEDBACK_BT_CONNECTED);
    led_feedback_play(LED_PATTERN_BT_CONNECTED);
    
    ESP_LOGI(TAG, "Device assigned ID %d (MAC: %s)", device_id, devices[device_id].mac_address);
}

void ble_multi_device_on_disconnect(uint16_t conn_id) {
    ESP_LOGI(TAG, "Device disconnected: conn_id=%d", conn_id);
    
    // Find device by connection ID
    uint8_t device_id = 0xFF;
    for (int i = 0; i < MAX_DEVICES; i++) {
        if (conn_map[i].conn_id == conn_id) {
            device_id = conn_map[i].device_id;
            conn_map[i].conn_id = 0xFFFF;
            conn_map[i].device_id = 0xFF;
            break;
        }
    }
    
    if (device_id == 0xFF) {
        ESP_LOGW(TAG, "Device not found for conn_id %d", conn_id);
        return;
    }
    
    // Mark device as disconnected
    devices[device_id].is_connected = false;
    device_count--;
    
    // Play disconnection feedback
    buzzer_feedback_play(FEEDBACK_BT_DISCONNECTED);
    if (device_count == 0) {
        led_feedback_play(LED_PATTERN_BT_DISCONNECTED);
    }
    
    ESP_LOGI(TAG, "Device %d disconnected (remaining: %d)", device_id, device_count);
}

void ble_multi_device_on_data_received(uint16_t conn_id, const uint8_t *data, uint16_t len) {
    ESP_LOGD(TAG, "Data received: conn_id=%d, len=%d", conn_id, len);
    
    // Find device
    DeviceInfo *device = ble_multi_device_get_device_by_conn_id(conn_id);
    if (device == NULL) {
        ESP_LOGW(TAG, "Device not found for conn_id %d", conn_id);
        return;
    }
    
    // Update last activity
    device->last_activity_timestamp = esp_log_timestamp();
    
    // Parse JSON for device identification
    // Expected format: {"command":"identify","device_type":"blitz","device_name":"...","version":"..."}
    
    // Simple JSON parsing (for full implementation, use cJSON)
    char *data_str = (char*)malloc(len + 1);
    if (data_str == NULL) {
        ESP_LOGE(TAG, "Failed to allocate memory for received data (%d bytes)", len);
        return;
    }
    memcpy(data_str, data, len);
    data_str[len] = '\0';
    
    ESP_LOGI(TAG, "Received: %s", data_str);
    
    // Check for "identify" command
    if (strstr(data_str, "\"command\":\"identify\"") != NULL) {
        ESP_LOGI(TAG, "Device identification request received");
        
        // Parse device type
        if (strstr(data_str, "\"device_type\":\"blitz\"") != NULL) {
            device->device_type = DEVICE_TYPE_BLITZ;
        } else if (strstr(data_str, "\"device_type\":\"smartphone\"") != NULL) {
            device->device_type = DEVICE_TYPE_SMARTPHONE;
        } else if (strstr(data_str, "\"device_type\":\"pc\"") != NULL) {
            device->device_type = DEVICE_TYPE_PC;
        } else {
            device->device_type = DEVICE_TYPE_CUSTOM;
        }
        
        // TODO: Parse device_name and version
        
        ESP_LOGI(TAG, "Device %d identified as %s", 
                 device->device_id,
                 mode_device_routing_get_device_type_name(device->device_type));
        
        // Send acknowledgment
        char response[128];
        snprintf(response, sizeof(response),
                "{\"status\":\"identified\",\"assigned_id\":%d,\"message\":\"Device registered as %s\"}",
                device->device_id,
                mode_device_routing_get_device_type_name(device->device_type));
        
        ble_multi_device_send_to(device->device_id, response);
        
        // Save to NVS
        ble_multi_device_save_to_nvs();
    }
    
    free(data_str);
}

esp_err_t ble_multi_device_send_to(uint8_t device_id, const char *json_data) {
    if (device_id >= MAX_DEVICES) {
        return ESP_ERR_INVALID_ARG;
    }
    
    if (!devices[device_id].is_connected) {
        ESP_LOGW(TAG, "Device %d not connected", device_id);
        return ESP_ERR_NOT_FOUND;
    }
    
    // Find connection ID
    uint16_t conn_id = 0xFFFF;
    for (int i = 0; i < MAX_DEVICES; i++) {
        if (conn_map[i].device_id == device_id) {
            conn_id = conn_map[i].conn_id;
            break;
        }
    }
    
    if (conn_id == 0xFFFF) {
        ESP_LOGE(TAG, "Connection ID not found for device %d", device_id);
        return ESP_ERR_NOT_FOUND;
    }
    
    ESP_LOGI(TAG, "Sending to device %d (conn_id %d): %s", device_id, conn_id, json_data);
    
    // Send via BLE server
    return ble_server_notify(conn_id, (const uint8_t*)json_data, strlen(json_data));
}

esp_err_t ble_multi_device_broadcast(const char *json_data) {
    if (device_count == 0) {
        ESP_LOGW(TAG, "No devices connected for broadcast");
        return ESP_ERR_NOT_FOUND;
    }
    
    ESP_LOGI(TAG, "Broadcasting to %d devices: %s", device_count, json_data);
    
    // Send to all connected devices
    for (uint8_t i = 0; i < MAX_DEVICES; i++) {
        if (devices[i].is_connected) {
            ble_multi_device_send_to(i, json_data);
        }
    }
    
    return ESP_OK;
}

bool ble_multi_device_is_any_connected(void) {
    return (device_count > 0);
}

DeviceInfo* ble_multi_device_get_device(uint8_t device_id) {
    if (device_id >= MAX_DEVICES) {
        return NULL;
    }
    return &devices[device_id];
}

DeviceInfo* ble_multi_device_get_device_by_conn_id(uint16_t conn_id) {
    for (int i = 0; i < MAX_DEVICES; i++) {
        if (conn_map[i].conn_id == conn_id) {
            return &devices[conn_map[i].device_id];
        }
    }
    return NULL;
}

const DeviceInfo* ble_multi_device_get_all_devices(uint8_t *count) {
    if (count != NULL) {
        *count = MAX_DEVICES;
    }
    return devices;
}

DeviceInfo* ble_multi_device_find_by_type(DeviceType type) {
    for (uint8_t i = 0; i < MAX_DEVICES; i++) {
        if (devices[i].is_connected && devices[i].device_type == type) {
            return &devices[i];
        }
    }
    return NULL;
}

esp_err_t ble_multi_device_save_to_nvs(void) {
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &nvs_handle);
    
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to open NVS");
        return ret;
    }
    
    // Save each device
    for (uint8_t i = 0; i < MAX_DEVICES; i++) {
        char key[32];
        
        snprintf(key, sizeof(key), "dev%d_type", i);
        nvs_set_u8(nvs_handle, key, (uint8_t)devices[i].device_type);
        
        snprintf(key, sizeof(key), "dev%d_name", i);
        nvs_set_str(nvs_handle, key, devices[i].device_name);
        
        snprintf(key, sizeof(key), "dev%d_mac", i);
        nvs_set_str(nvs_handle, key, devices[i].mac_address);
    }
    
    nvs_commit(nvs_handle);
    nvs_close(nvs_handle);
    
    ESP_LOGI(TAG, "Device database saved to NVS");
    return ESP_OK;
}

esp_err_t ble_multi_device_load_from_nvs(void) {
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs_handle);
    
    if (ret != ESP_OK) {
        ESP_LOGI(TAG, "No saved device database found");
        return ESP_OK;
    }
    
    // Load each device
    for (uint8_t i = 0; i < MAX_DEVICES; i++) {
        char key[32];
        uint8_t u8_val;
        size_t str_len;
        
        snprintf(key, sizeof(key), "dev%d_type", i);
        if (nvs_get_u8(nvs_handle, key, &u8_val) == ESP_OK) {
            devices[i].device_type = (DeviceType)u8_val;
        }
        
        snprintf(key, sizeof(key), "dev%d_name", i);
        str_len = sizeof(devices[i].device_name);
        nvs_get_str(nvs_handle, key, devices[i].device_name, &str_len);
        
        snprintf(key, sizeof(key), "dev%d_mac", i);
        str_len = sizeof(devices[i].mac_address);
        nvs_get_str(nvs_handle, key, devices[i].mac_address, &str_len);
    }
    
    nvs_close(nvs_handle);
    
    ESP_LOGI(TAG, "Device database loaded from NVS");
    return ESP_OK;
}
