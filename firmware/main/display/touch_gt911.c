#include "touch_gt911.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "TOUCH_GT911";

// GT911 I2C address
#define GT911_I2C_ADDR          0x5D

// GT911 Registers
#define GT911_REG_STATUS        0x814E
#define GT911_REG_CONFIG        0x8047
#define GT911_REG_POINT1        0x8150
#define GT911_REG_POINT2        0x8158
#define GT911_REG_POINT3        0x8160
#define GT911_REG_POINT4        0x8168
#define GT911_REG_POINT5        0x8170

// Stato touch
static bool g_touch_initialized = false;
static uint8_t g_point_count = 0;
static lv_coord_t g_last_x = 0;
static lv_coord_t g_last_y = 0;

/**
 * @brief Scrivi registro GT911
 */
static esp_err_t gt911_write_reg(uint16_t reg, uint8_t *data, size_t len) {
    uint8_t buffer[len + 2];
    buffer[0] = (reg >> 8) & 0xFF;
    buffer[1] = reg & 0xFF;
    memcpy(&buffer[2], data, len);
    
    return i2c_master_write_to_device(TOUCH_I2C_NUM, GT911_I2C_ADDR, 
                                      buffer, len + 2, pdMS_TO_TICKS(100));
}

/**
 * @brief Leggi registro GT911
 */
static esp_err_t gt911_read_reg(uint16_t reg, uint8_t *data, size_t len) {
    uint8_t reg_addr[2];
    reg_addr[0] = (reg >> 8) & 0xFF;
    reg_addr[1] = reg & 0xFF;
    
    return i2c_master_write_read_device(TOUCH_I2C_NUM, GT911_I2C_ADDR,
                                       reg_addr, 2, data, len, pdMS_TO_TICKS(100));
}

bool touch_gt911_init(void) {
    ESP_LOGI(TAG, "Inizializzazione touch GT911...");
    
    // Configura I2C master
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = TOUCH_I2C_SDA,
        .scl_io_num = TOUCH_I2C_SCL,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = TOUCH_I2C_FREQ_HZ,
    };
    
    esp_err_t err = i2c_param_config(TOUCH_I2C_NUM, &conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore configurazione I2C: %s", esp_err_to_name(err));
        return false;
    }
    
    err = i2c_driver_install(TOUCH_I2C_NUM, conf.mode, 0, 0, 0);
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "Errore installazione driver I2C: %s", esp_err_to_name(err));
        return false;
    }
    
    // Verifica presenza GT911
    uint8_t test_data;
    err = gt911_read_reg(GT911_REG_CONFIG, &test_data, 1);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "GT911 non rilevato su I2C (potrebbe essere normale)");
        // Non ritornare false, continua comunque
    } else {
        ESP_LOGI(TAG, "GT911 rilevato correttamente");
    }
    
    // Reset stato touch
    uint8_t clear = 0;
    gt911_write_reg(GT911_REG_STATUS, &clear, 1);
    
    g_touch_initialized = true;
    ESP_LOGI(TAG, "Touch GT911 inizializzato (%dx%d)", TOUCH_MAX_X, TOUCH_MAX_Y);
    
    return true;
}

bool touch_gt911_read(lv_indev_data_t *data) {
    if (!g_touch_initialized || !data) {
        return false;
    }
    
    // Leggi stato touch
    uint8_t status;
    esp_err_t err = gt911_read_reg(GT911_REG_STATUS, &status, 1);
    if (err != ESP_OK) {
        data->state = LV_INDEV_STATE_RELEASED;
        return false;
    }
    
    // Verifica se ci sono touch validi
    g_point_count = status & 0x0F;
    bool buffer_status = (status & 0x80) != 0;
    
    if (!buffer_status || g_point_count == 0) {
        // Nessun touch attivo
        data->state = LV_INDEV_STATE_RELEASED;
        data->point.x = g_last_x;
        data->point.y = g_last_y;
        
        // Clear status
        uint8_t clear = 0;
        gt911_write_reg(GT911_REG_STATUS, &clear, 1);
        
        return false;
    }
    
    // Leggi primo punto touch
    uint8_t point_data[8];
    err = gt911_read_reg(GT911_REG_POINT1, point_data, 8);
    if (err != ESP_OK) {
        data->state = LV_INDEV_STATE_RELEASED;
        return false;
    }
    
    // Estrai coordinate (little endian)
    uint16_t x = point_data[1] | (point_data[2] << 8);
    uint16_t y = point_data[3] | (point_data[4] << 8);
    
    // Limita coordinate al range display
    if (x > TOUCH_MAX_X) x = TOUCH_MAX_X;
    if (y > TOUCH_MAX_Y) y = TOUCH_MAX_Y;
    
    // Aggiorna dati LVGL
    data->state = LV_INDEV_STATE_PRESSED;
    data->point.x = x;
    data->point.y = y;
    
    // Salva ultime coordinate
    g_last_x = x;
    g_last_y = y;
    
    // Clear status
    uint8_t clear = 0;
    gt911_write_reg(GT911_REG_STATUS, &clear, 1);
    
    return true;
}

void touch_gt911_deinit(void) {
    if (g_touch_initialized) {
        i2c_driver_delete(TOUCH_I2C_NUM);
        g_touch_initialized = false;
        ESP_LOGI(TAG, "Touch GT911 deinizializzato");
    }
}

uint8_t touch_gt911_get_point_count(void) {
    return g_point_count;
}
