#include "bluetooth.h"
#include "config.h"
#include "esp_log.h"
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"
#include "esp_bt_main.h"
#include "esp_gatt_common_api.h"
#include <string.h>
#include <stdio.h>

static const char *TAG = "BLUETOOTH";

// Handle per servizio e caratteristiche
static uint16_t gatts_if_value = ESP_GATT_IF_NONE;
static uint16_t conn_id_value = 0xFFFF;
static uint16_t service_handle = 0;
static uint16_t char_tx_handle = 0;
static uint16_t char_rx_handle = 0;

static bool is_connected = false;
static char peer_addr[18] = {0};

// UUID conversions (simplified)
static uint8_t service_uuid[16] = {
    0xbc, 0x9a, 0x78, 0x56, 0x34, 0x12, 0x34, 0x12, 
    0x34, 0x12, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12
};

// GAP event handler
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param) {
    switch (event) {
        case ESP_GAP_BLE_ADV_DATA_SET_COMPLETE_EVT:
            ESP_LOGI(TAG, "Advertising data set complete");
            esp_ble_gap_start_advertising(&param->adv_data_cmpl.adv_data);
            break;
            
        case ESP_GAP_BLE_ADV_START_COMPLETE_EVT:
            if (param->adv_start_cmpl.status == ESP_BT_STATUS_SUCCESS) {
                ESP_LOGI(TAG, "Advertising started");
            } else {
                ESP_LOGE(TAG, "Advertising start failed");
            }
            break;
            
        default:
            break;
    }
}

// GATTS event handler
static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatts_if, 
                                 esp_ble_gatts_cb_param_t *param) {
    switch (event) {
        case ESP_GATTS_REG_EVT:
            ESP_LOGI(TAG, "GATT server registered");
            gatts_if_value = gatts_if;
            
            // Imposta device name
            esp_ble_gap_set_device_name(g_config.bt_device_name);
            
            // Configura advertising
            esp_ble_adv_data_t adv_data = {
                .set_scan_rsp = false,
                .include_name = true,
                .include_txpower = true,
                .min_interval = 0x20,
                .max_interval = 0x40,
                .appearance = 0x00,
                .manufacturer_len = 0,
                .p_manufacturer_data = NULL,
                .service_data_len = 0,
                .p_service_data = NULL,
                .service_uuid_len = sizeof(service_uuid),
                .p_service_uuid = service_uuid,
                .flag = (ESP_BLE_ADV_FLAG_GEN_DISC | ESP_BLE_ADV_FLAG_BREDR_NOT_SPT),
            };
            esp_ble_gap_config_adv_data(&adv_data);
            
            // Crea servizio (implementazione semplificata)
            ESP_LOGI(TAG, "Creating GATT service");
            break;
            
        case ESP_GATTS_CONNECT_EVT:
            ESP_LOGI(TAG, "Client connected, conn_id: %d", param->connect.conn_id);
            is_connected = true;
            conn_id_value = param->connect.conn_id;
            g_state.bt_connected = true;
            
            // Salva indirizzo peer
            snprintf(peer_addr, sizeof(peer_addr), 
                     "%02X:%02X:%02X:%02X:%02X:%02X",
                     param->connect.remote_bda[0], param->connect.remote_bda[1],
                     param->connect.remote_bda[2], param->connect.remote_bda[3],
                     param->connect.remote_bda[4], param->connect.remote_bda[5]);
            strncpy(g_state.bt_peer_address, peer_addr, sizeof(g_state.bt_peer_address) - 1);
            break;
            
        case ESP_GATTS_DISCONNECT_EVT:
            ESP_LOGI(TAG, "Client disconnected");
            is_connected = false;
            conn_id_value = 0xFFFF;
            g_state.bt_connected = false;
            memset(peer_addr, 0, sizeof(peer_addr));
            memset(g_state.bt_peer_address, 0, sizeof(g_state.bt_peer_address));
            
            // Riavvia advertising
            esp_ble_gap_start_advertising(&(esp_ble_adv_params_t){
                .adv_int_min = 0x20,
                .adv_int_max = 0x40,
                .adv_type = ADV_TYPE_IND,
                .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
                .channel_map = ADV_CHNL_ALL,
                .adv_filter_policy = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
            });
            break;
            
        default:
            break;
    }
}

esp_err_t bluetooth_init(void) {
    if (!g_config.bluetooth_enabled) {
        ESP_LOGI(TAG, "Bluetooth disabilitato in configurazione");
        return ESP_OK;
    }
    
    ESP_LOGI(TAG, "Inizializzazione Bluetooth...");
    
    // Release controller memory
    ESP_ERROR_CHECK(esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT));
    
    // Initialize BT controller
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    esp_err_t ret = esp_bt_controller_init(&bt_cfg);
    if (ret) {
        ESP_LOGE(TAG, "Errore init BT controller: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ret = esp_bt_controller_enable(ESP_BT_MODE_BLE);
    if (ret) {
        ESP_LOGE(TAG, "Errore enable BT controller: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ret = esp_bluedroid_init();
    if (ret) {
        ESP_LOGE(TAG, "Errore init Bluedroid: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ret = esp_bluedroid_enable();
    if (ret) {
        ESP_LOGE(TAG, "Errore enable Bluedroid: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Register callbacks
    esp_ble_gap_register_callback(gap_event_handler);
    esp_ble_gatts_register_callback(gatts_event_handler);
    esp_ble_gatts_app_register(0);
    
    // Set MTU
    esp_ble_gatt_set_local_mtu(500);
    
    ESP_LOGI(TAG, "Bluetooth inizializzato con successo");
    return ESP_OK;
}

bool bluetooth_is_connected(void) {
    return is_connected;
}

const char* bluetooth_get_peer_address(void) {
    return peer_addr;
}

esp_err_t bluetooth_send_json(const char *json_str) {
    if (!is_connected || conn_id_value == 0xFFFF) {
        ESP_LOGW(TAG, "Impossibile inviare: non connesso");
        return ESP_ERR_INVALID_STATE;
    }
    
    ESP_LOGI(TAG, "Invio JSON: %s", json_str);
    
    // Invio notifica BLE (implementazione semplificata)
    // In una implementazione completa, usare esp_ble_gatts_send_indicate()
    
    return ESP_OK;
}

esp_err_t bluetooth_send_fermavetro(float misura_mm, bool auto_start) {
    char json[256];
    snprintf(json, sizeof(json),
             "{\"type\":\"fermavetro\",\"misura_mm\":%.2f,\"auto_start\":%s,\"mode\":\"semi_auto\"}",
             misura_mm, auto_start ? "true" : "false");
    
    return bluetooth_send_json(json);
}

esp_err_t bluetooth_send_vetro(float larghezza_raw, float altezza_raw,
                                float larghezza_netta, float altezza_netta,
                                const char *materiale, uint32_t quantita, float gioco) {
    char json[512];
    snprintf(json, sizeof(json),
             "{\"larghezza_raw\":%.2f,\"altezza_raw\":%.2f,"
             "\"larghezza_netta\":%.2f,\"altezza_netta\":%.2f,"
             "\"materiale\":\"%s\",\"quantita\":%lu,\"gioco\":%.2f}",
             larghezza_raw, altezza_raw, larghezza_netta, altezza_netta,
             materiale, quantita, gioco);
    
    return bluetooth_send_json(json);
}

esp_err_t bluetooth_send_rilievo_speciale(const char *tipologia, const char *elemento,
                                          const char *formula, float misura_mm,
                                          uint8_t num_pezzi, bool auto_start) {
    char json[512];
    uint64_t timestamp = esp_timer_get_time() / 1000; // milliseconds
    
    snprintf(json, sizeof(json),
             "{\"type\":\"rilievo_speciale\",\"dest\":\"troncatrice\","
             "\"tipologia\":\"%s\",\"elemento\":\"%s\",\"formula\":\"%s\","
             "\"misura_mm\":%.1f,\"num_pezzi\":%u,\"auto_start\":%s,\"timestamp\":%llu}",
             tipologia, elemento, formula, misura_mm, num_pezzi,
             auto_start ? "true" : "false", timestamp);
    
    return bluetooth_send_json(json);
}

void bluetooth_task(void *pvParameters) {
    ESP_LOGI(TAG, "Task Bluetooth avviato su core %d", xPortGetCoreID());
    
    while (1) {
        // Gestione eventi Bluetooth
        // In una implementazione reale, gestire code messaggi, notifiche, ecc.
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
