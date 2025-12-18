#ifndef BLE_MULTI_DEVICE_H
#define BLE_MULTI_DEVICE_H

#include "../measurement/mode_device_routing.h"
#include "esp_err.h"
#include <stdint.h>
#include <stdbool.h>

#define MAX_DEVICES 3

// Initialize multi-device manager
esp_err_t ble_multi_device_init(void);

// Handle new connection
void ble_multi_device_on_connect(uint16_t conn_id, const uint8_t *mac_addr);

// Handle disconnection
void ble_multi_device_on_disconnect(uint16_t conn_id);

// Handle received data (identification, commands)
void ble_multi_device_on_data_received(uint16_t conn_id, const uint8_t *data, uint16_t len);

// Send data to specific device by ID
esp_err_t ble_multi_device_send_to(uint8_t device_id, const char *json_data);

// Broadcast data to all connected devices
esp_err_t ble_multi_device_broadcast(const char *json_data);

// Check if any device is connected
bool ble_multi_device_is_any_connected(void);

// Get device info by ID
DeviceInfo* ble_multi_device_get_device(uint8_t device_id);

// Get device info by connection ID
DeviceInfo* ble_multi_device_get_device_by_conn_id(uint16_t conn_id);

// Get all devices
const DeviceInfo* ble_multi_device_get_all_devices(uint8_t *count);

// Find device by type
DeviceInfo* ble_multi_device_find_by_type(DeviceType type);

// Save device database to NVS
esp_err_t ble_multi_device_save_to_nvs(void);

// Load device database from NVS
esp_err_t ble_multi_device_load_from_nvs(void);

#endif // BLE_MULTI_DEVICE_H
