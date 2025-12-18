#include "measure_sender.h"
#include "esp_log.h"
#include <stdio.h>
#include <string.h>
#include <time.h>

static const char *TAG = "MEASURE_SENDER";

// Forward declaration - will be implemented in BLE multi-device module
extern esp_err_t ble_multi_device_send_to(uint8_t device_id, const char *json_data);
extern esp_err_t ble_multi_device_broadcast(const char *json_data);
extern bool ble_multi_device_is_any_connected(void);

esp_err_t measure_sender_send(MeasureMode mode, 
                               const MeasurementResult *result,
                               const Puntale *tip_left,
                               const Puntale *tip_right) {
    // Check if routing is broadcast
    if (mode_device_routing_is_broadcast(mode)) {
        return measure_sender_broadcast(mode, result, tip_left, tip_right);
    }
    
    // Get routing configuration
    DeviceType device_type;
    uint8_t device_id;
    
    esp_err_t ret = mode_device_routing_get(mode, &device_type, &device_id);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get routing for mode %d", mode);
        return ret;
    }
    
    // Send to specific device
    return measure_sender_send_to_device(device_id, mode, result, tip_left, tip_right);
}

esp_err_t measure_sender_send_to_device(uint8_t device_id,
                                        MeasureMode mode,
                                        const MeasurementResult *result,
                                        const Puntale *tip_left,
                                        const Puntale *tip_right) {
    // Generate JSON payload
    char json_buffer[1024];
    esp_err_t ret = measure_sender_create_json(mode, result, tip_left, tip_right, 
                                               json_buffer, sizeof(json_buffer));
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create JSON payload");
        return ret;
    }
    
    ESP_LOGI(TAG, "Sending measurement to device %d: %s", device_id, json_buffer);
    
    // Send via BLE
    ret = ble_multi_device_send_to(device_id, json_buffer);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to send to device %d", device_id);
        return ret;
    }
    
    return ESP_OK;
}

esp_err_t measure_sender_broadcast(MeasureMode mode,
                                   const MeasurementResult *result,
                                   const Puntale *tip_left,
                                   const Puntale *tip_right) {
    // Check if any device is connected
    if (!ble_multi_device_is_any_connected()) {
        ESP_LOGW(TAG, "No devices connected for broadcast");
        return ESP_ERR_NOT_FOUND;
    }
    
    // Generate JSON payload
    char json_buffer[1024];
    esp_err_t ret = measure_sender_create_json(mode, result, tip_left, tip_right,
                                               json_buffer, sizeof(json_buffer));
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create JSON payload");
        return ret;
    }
    
    ESP_LOGI(TAG, "Broadcasting measurement: %s", json_buffer);
    
    // Broadcast via BLE
    ret = ble_multi_device_broadcast(json_buffer);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to broadcast");
        return ret;
    }
    
    return ESP_OK;
}

esp_err_t measure_sender_create_json(MeasureMode mode,
                                     const MeasurementResult *result,
                                     const Puntale *tip_left,
                                     const Puntale *tip_right,
                                     char *json_buffer,
                                     size_t buffer_size) {
    if (json_buffer == NULL || buffer_size == 0) {
        return ESP_ERR_INVALID_ARG;
    }
    
    // Get mode name
    const char *mode_name = mode_device_routing_get_mode_name(mode);
    
    // Get Blitz mode
    BlitzMode blitz_mode = mode_device_routing_get_blitz_mode();
    const char *blitz_mode_str = mode_device_routing_get_blitz_mode_name(blitz_mode);
    
    // Get current timestamp
    time_t now = time(NULL);
    
    // Build JSON
    int offset = 0;
    offset += snprintf(json_buffer + offset, buffer_size - offset, "{");
    
    // Type (use mode name, lowercase)
    char type_lower[32];
    strncpy(type_lower, mode_name, sizeof(type_lower) - 1);
    for (char *p = type_lower; *p; p++) *p = tolower(*p);
    offset += snprintf(json_buffer + offset, buffer_size - offset, 
                      "\"type\":\"%s\",", type_lower);
    
    // Measurement value
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"misura_mm\":%.2f,", result->net_measurement_mm);
    
    // Auto start (for BLITZ)
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"auto_start\":%s,", 
                      (blitz_mode == BLITZ_MODE_AUTOMATICO) ? "true" : "false");
    
    // Blitz mode
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"mode\":\"%s\",", blitz_mode_str);
    
    // Timestamp
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"timestamp\":%ld,", (long)now);
    
    // Raw encoder value
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"encoder_raw\":%.2f,", result->encoder_raw_mm);
    
    // Corrections object
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"corrections\":{");
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"left\":%.2f,", result->correction_left_mm);
    offset += snprintf(json_buffer + offset, buffer_size - offset,
                      "\"right\":%.2f", result->correction_right_mm);
    offset += snprintf(json_buffer + offset, buffer_size - offset, "}");
    
    // Optional: tip info
    if (tip_left != NULL || tip_right != NULL) {
        offset += snprintf(json_buffer + offset, buffer_size - offset, ",\"tips\":{");
        
        if (tip_left != NULL) {
            offset += snprintf(json_buffer + offset, buffer_size - offset,
                              "\"left\":{\"id\":\"%s\",\"name\":\"%s\",\"ref\":\"%s\"}",
                              tip_left->id, tip_left->nome,
                              puntale_reference_to_string(tip_left->reference));
        }
        
        if (tip_left != NULL && tip_right != NULL) {
            offset += snprintf(json_buffer + offset, buffer_size - offset, ",");
        }
        
        if (tip_right != NULL) {
            offset += snprintf(json_buffer + offset, buffer_size - offset,
                              "\"right\":{\"id\":\"%s\",\"name\":\"%s\",\"ref\":\"%s\"}",
                              tip_right->id, tip_right->nome,
                              puntale_reference_to_string(tip_right->reference));
        }
        
        offset += snprintf(json_buffer + offset, buffer_size - offset, "}");
    }
    
    // Close JSON
    offset += snprintf(json_buffer + offset, buffer_size - offset, "}");
    
    return ESP_OK;
}

// Stub implementations for BLE functions (will be replaced by actual BLE module)
__attribute__((weak)) esp_err_t ble_multi_device_send_to(uint8_t device_id, const char *json_data) {
    ESP_LOGW(TAG, "BLE stub: would send to device %d: %s", device_id, json_data);
    return ESP_OK;
}

__attribute__((weak)) esp_err_t ble_multi_device_broadcast(const char *json_data) {
    ESP_LOGW(TAG, "BLE stub: would broadcast: %s", json_data);
    return ESP_OK;
}

__attribute__((weak)) bool ble_multi_device_is_any_connected(void) {
    return false; // No devices connected in stub
}
