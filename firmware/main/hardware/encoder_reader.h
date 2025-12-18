#ifndef ENCODER_READER_H
#define ENCODER_READER_H

#include <stdint.h>
#include "esp_err.h"

// AS5600 I2C Address
#define AS5600_I2C_ADDR     0x36

// AS5600 Registers
#define AS5600_REG_ANGLE_H  0x0E
#define AS5600_REG_ANGLE_L  0x0F
#define AS5600_REG_STATUS   0x0B
#define AS5600_REG_AGC      0x1A
#define AS5600_REG_MAGNITUDE_H 0x1B
#define AS5600_REG_MAGNITUDE_L 0x1C

// I2C Configuration
#define I2C_MASTER_NUM      I2C_NUM_0
#define I2C_MASTER_SDA_IO   21
#define I2C_MASTER_SCL_IO   22
#define I2C_MASTER_FREQ_HZ  400000
#define I2C_MASTER_TIMEOUT_MS 1000

// Encoder resolution (12-bit = 4096 positions per revolution)
#define AS5600_RESOLUTION   4096

// Initialize AS5600 encoder
esp_err_t encoder_reader_init(void);

// Read raw angle (0-4095)
esp_err_t encoder_reader_get_angle(uint16_t *angle);

// Read angle in degrees (0-360)
esp_err_t encoder_reader_get_angle_degrees(float *angle_deg);

// Read status register
esp_err_t encoder_reader_get_status(uint8_t *status);

// Check if magnet detected
bool encoder_reader_is_magnet_detected(void);

// Get AGC value (Automatic Gain Control)
esp_err_t encoder_reader_get_agc(uint8_t *agc);

// Get magnitude (magnetic field strength)
esp_err_t encoder_reader_get_magnitude(uint16_t *magnitude);

// Convert angle to linear position (mm) based on gear ratio/pulley diameter
// This should be calibrated based on mechanical setup
float encoder_reader_angle_to_mm(uint16_t angle, float calibration_factor);

#endif // ENCODER_READER_H
