#include "encoder_reader.h"
#include "driver/i2c.h"
#include "esp_log.h"
#include <math.h>

static const char *TAG = "ENC_READER";

// I2C read register
static esp_err_t i2c_read_reg(uint8_t reg_addr, uint8_t *data, size_t len) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (AS5600_I2C_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg_addr, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (AS5600_I2C_ADDR << 1) | I2C_MASTER_READ, true);
    if (len > 1) {
        i2c_master_read(cmd, data, len - 1, I2C_MASTER_ACK);
    }
    i2c_master_read_byte(cmd, data + len - 1, I2C_MASTER_NACK);
    i2c_master_stop(cmd);
    
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(I2C_MASTER_TIMEOUT_MS));
    i2c_cmd_link_delete(cmd);
    
    return ret;
}

esp_err_t encoder_reader_init(void) {
    ESP_LOGI(TAG, "Initializing AS5600 encoder");
    
    // Configure I2C master
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ
    };
    
    esp_err_t ret = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2C param config failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ret = i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "I2C driver install failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Test communication by reading status
    uint8_t status;
    ret = encoder_reader_get_status(&status);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "AS5600 communication test failed");
        return ret;
    }
    
    ESP_LOGI(TAG, "AS5600 encoder initialized, status: 0x%02X", status);
    
    // Check if magnet is detected
    if (!encoder_reader_is_magnet_detected()) {
        ESP_LOGW(TAG, "Warning: Magnet not detected or out of range");
    }
    
    return ESP_OK;
}

esp_err_t encoder_reader_get_angle(uint16_t *angle) {
    uint8_t data[2];
    esp_err_t ret = i2c_read_reg(AS5600_REG_ANGLE_H, data, 2);
    
    if (ret == ESP_OK) {
        *angle = ((uint16_t)data[0] << 8) | data[1];
        *angle &= 0x0FFF; // 12-bit value
    }
    
    return ret;
}

esp_err_t encoder_reader_get_angle_degrees(float *angle_deg) {
    uint16_t angle_raw;
    esp_err_t ret = encoder_reader_get_angle(&angle_raw);
    
    if (ret == ESP_OK) {
        *angle_deg = (float)angle_raw * 360.0f / (float)AS5600_RESOLUTION;
    }
    
    return ret;
}

esp_err_t encoder_reader_get_status(uint8_t *status) {
    return i2c_read_reg(AS5600_REG_STATUS, status, 1);
}

bool encoder_reader_is_magnet_detected(void) {
    uint8_t status;
    esp_err_t ret = encoder_reader_get_status(&status);
    
    if (ret != ESP_OK) {
        return false;
    }
    
    // Check MD (Magnet Detected) bit (bit 5)
    // And check if magnet is not too weak (bit 4) or too strong (bit 3)
    bool magnet_detected = (status & 0x20) != 0;
    bool magnet_too_weak = (status & 0x10) != 0;
    bool magnet_too_strong = (status & 0x08) != 0;
    
    return magnet_detected && !magnet_too_weak && !magnet_too_strong;
}

esp_err_t encoder_reader_get_agc(uint8_t *agc) {
    return i2c_read_reg(AS5600_REG_AGC, agc, 1);
}

esp_err_t encoder_reader_get_magnitude(uint16_t *magnitude) {
    uint8_t data[2];
    esp_err_t ret = i2c_read_reg(AS5600_REG_MAGNITUDE_H, data, 2);
    
    if (ret == ESP_OK) {
        *magnitude = ((uint16_t)data[0] << 8) | data[1];
        *magnitude &= 0x0FFF; // 12-bit value
    }
    
    return ret;
}

float encoder_reader_angle_to_mm(uint16_t angle, float calibration_factor) {
    // Convert angle to linear position
    // calibration_factor should be set based on mechanical setup
    // For example: pulley_diameter_mm * PI / 4096
    return (float)angle * calibration_factor;
}
