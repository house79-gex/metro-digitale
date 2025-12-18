#ifndef BLE_SERVER_H
#define BLE_SERVER_H

#include "esp_err.h"
#include <stdbool.h>

// BLE service UUIDs (from protocol documentation)
#define BLE_SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define BLE_CHAR_TX_UUID        "12345678-1234-1234-1234-123456789abd"  // Metro → Device
#define BLE_CHAR_RX_UUID        "12345678-1234-1234-1234-123456789abe"  // Device → Metro

// BLE advertising name
#define BLE_DEVICE_NAME         "Metro-Digitale"

// Initialize BLE server
esp_err_t ble_server_init(void);

// Start BLE advertising
esp_err_t ble_server_start_advertising(void);

// Stop BLE advertising
esp_err_t ble_server_stop_advertising(void);

// Check if advertising is active
bool ble_server_is_advertising(void);

// Get connection count
uint8_t ble_server_get_connection_count(void);

// Notify data to a specific connection
esp_err_t ble_server_notify(uint16_t conn_id, const uint8_t *data, uint16_t len);

// Notify data to all connections
esp_err_t ble_server_notify_all(const uint8_t *data, uint16_t len);

#endif // BLE_SERVER_H
