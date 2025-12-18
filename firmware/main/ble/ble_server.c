#include "ble_server.h"
#include "ble_multi_device.h"
#include "esp_log.h"
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"
#include "esp_bt_main.h"
#include "esp_gatt_common_api.h"
#include <string.h>

static const char *TAG = "BLE_SERVER";

// GATT service and characteristic handles
static uint16_t service_handle = 0;
static uint16_t char_tx_handle = 0;
static uint16_t char_rx_handle = 0;

// Advertising state
static bool is_advertising = false;

// Connection tracking
static uint16_t conn_ids[3] = {0xFFFF, 0xFFFF, 0xFFFF};
static uint8_t conn_count = 0;

// Forward declarations
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param);
static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if, esp_ble_gatts_cb_param_t *param);

// Advertising parameters
static esp_ble_adv_params_t adv_params = {
    .adv_int_min = 0x20,
    .adv_int_max = 0x40,
    .adv_type = ADV_TYPE_IND,
    .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
    .channel_map = ADV_CHNL_ALL,
    .adv_filter_policy = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

// Advertising data
static uint8_t adv_service_uuid128[16] = {
    0xbc, 0x9a, 0x78, 0x56, 0x34, 0x12, 0x34, 0x12,
    0x34, 0x12, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12
};

static esp_ble_adv_data_t adv_data = {
    .set_scan_rsp = false,
    .include_name = true,
    .include_txpower = true,
    .min_interval = 0x0006,
    .max_interval = 0x0010,
    .appearance = 0x00,
    .manufacturer_len = 0,
    .p_manufacturer_data = NULL,
    .service_data_len = 0,
    .p_service_data = NULL,
    .service_uuid_len = sizeof(adv_service_uuid128),
    .p_service_uuid = adv_service_uuid128,
    .flag = (ESP_BLE_ADV_FLAG_GEN_DISC | ESP_BLE_ADV_FLAG_BREDR_NOT_SPT),
};

esp_err_t ble_server_init(void) {
    ESP_LOGI(TAG, "Initializing BLE server");
    
    // Initialize NVS (required for BT)
    // nvs_flash_init() should be called in main
    
    // Release classic BT memory
    ESP_ERROR_CHECK(esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT));
    
    // Initialize BT controller
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    esp_err_t ret = esp_bt_controller_init(&bt_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "BT controller init failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Enable BT controller in BLE mode
    ret = esp_bt_controller_enable(ESP_BT_MODE_BLE);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "BT controller enable failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Initialize Bluedroid
    ret = esp_bluedroid_init();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Bluedroid init failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ret = esp_bluedroid_enable();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Bluedroid enable failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Register GAP callback
    ret = esp_ble_gap_register_callback(gap_event_handler);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "GAP register failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Register GATT callback
    ret = esp_ble_gatts_register_callback(gatts_event_handler);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "GATTS register failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Set device name
    ret = esp_ble_gap_set_device_name(BLE_DEVICE_NAME);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Set device name failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Configure advertising data
    ret = esp_ble_gap_config_adv_data(&adv_data);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Config adv data failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ESP_LOGI(TAG, "BLE server initialized successfully");
    return ESP_OK;
}

esp_err_t ble_server_start_advertising(void) {
    if (is_advertising) {
        ESP_LOGW(TAG, "Already advertising");
        return ESP_OK;
    }
    
    esp_err_t ret = esp_ble_gap_start_advertising(&adv_params);
    if (ret == ESP_OK) {
        is_advertising = true;
        ESP_LOGI(TAG, "Started BLE advertising");
    } else {
        ESP_LOGE(TAG, "Start advertising failed: %s", esp_err_to_name(ret));
    }
    
    return ret;
}

esp_err_t ble_server_stop_advertising(void) {
    if (!is_advertising) {
        return ESP_OK;
    }
    
    esp_err_t ret = esp_ble_gap_stop_advertising();
    if (ret == ESP_OK) {
        is_advertising = false;
        ESP_LOGI(TAG, "Stopped BLE advertising");
    }
    
    return ret;
}

bool ble_server_is_advertising(void) {
    return is_advertising;
}

uint8_t ble_server_get_connection_count(void) {
    return conn_count;
}

esp_err_t ble_server_notify(uint16_t conn_id, const uint8_t *data, uint16_t len) {
    // TODO: Implement notification to specific connection
    ESP_LOGD(TAG, "Notifying conn_id %d with %d bytes", conn_id, len);
    return ESP_OK;
}

esp_err_t ble_server_notify_all(const uint8_t *data, uint16_t len) {
    // TODO: Implement broadcast notification
    ESP_LOGD(TAG, "Broadcasting %d bytes to all connections", len);
    return ESP_OK;
}

// GAP event handler
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param) {
    switch (event) {
        case ESP_GAP_BLE_ADV_DATA_SET_COMPLETE_EVT:
            ESP_LOGI(TAG, "Advertising data set complete");
            ble_server_start_advertising();
            break;
            
        case ESP_GAP_BLE_ADV_START_COMPLETE_EVT:
            if (param->adv_start_cmpl.status == ESP_BT_STATUS_SUCCESS) {
                ESP_LOGI(TAG, "Advertising started successfully");
            } else {
                ESP_LOGE(TAG, "Advertising start failed");
            }
            break;
            
        case ESP_GAP_BLE_ADV_STOP_COMPLETE_EVT:
            if (param->adv_stop_cmpl.status == ESP_BT_STATUS_SUCCESS) {
                ESP_LOGI(TAG, "Advertising stopped successfully");
            }
            break;
            
        default:
            break;
    }
}

// GATTS event handler
static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if, esp_ble_gatts_cb_param_t *param) {
    switch (event) {
        case ESP_GATTS_REG_EVT:
            ESP_LOGI(TAG, "GATT server registered");
            // Create service, characteristics, etc.
            break;
            
        case ESP_GATTS_CONNECT_EVT:
            ESP_LOGI(TAG, "Client connected: conn_id=%d", param->connect.conn_id);
            if (conn_count < 3) {
                conn_ids[conn_count] = param->connect.conn_id;
                conn_count++;
                
                // Notify multi-device manager
                ble_multi_device_on_connect(param->connect.conn_id, param->connect.remote_bda);
            }
            break;
            
        case ESP_GATTS_DISCONNECT_EVT:
            ESP_LOGI(TAG, "Client disconnected: conn_id=%d", param->disconnect.conn_id);
            // Remove from connection list
            for (int i = 0; i < conn_count; i++) {
                if (conn_ids[i] == param->disconnect.conn_id) {
                    // Shift remaining connections
                    for (int j = i; j < conn_count - 1; j++) {
                        conn_ids[j] = conn_ids[j + 1];
                    }
                    conn_count--;
                    break;
                }
            }
            
            // Notify multi-device manager
            ble_multi_device_on_disconnect(param->disconnect.conn_id);
            
            // Restart advertising if not at max connections
            if (conn_count < 3) {
                ble_server_start_advertising();
            }
            break;
            
        case ESP_GATTS_WRITE_EVT:
            ESP_LOGD(TAG, "Write event: conn_id=%d, handle=%d", 
                     param->write.conn_id, param->write.handle);
            // Handle incoming data (device identification, etc.)
            ble_multi_device_on_data_received(param->write.conn_id, 
                                             param->write.value, 
                                             param->write.len);
            break;
            
        default:
            break;
    }
}
