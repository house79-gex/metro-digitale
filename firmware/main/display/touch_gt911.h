#ifndef TOUCH_GT911_H
#define TOUCH_GT911_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/i2c.h"
#include "lvgl.h"

/**
 * @file touch_gt911.h
 * @brief Driver touch capacitivo GT911 per display 800×480
 * 
 * Supporta:
 * - Multi-touch fino a 5 punti
 * - I2C 400kHz
 * - Coordinate mapping automatico
 * - Integrazione LVGL
 */

// Configurazione I2C touch
#define TOUCH_I2C_NUM           I2C_NUM_0
#define TOUCH_I2C_SDA           GPIO_NUM_18
#define TOUCH_I2C_SCL           GPIO_NUM_8
#define TOUCH_I2C_INT           GPIO_NUM_4
#define TOUCH_I2C_FREQ_HZ       400000

// Risoluzione touch
#define TOUCH_MAX_X             800
#define TOUCH_MAX_Y             480
#define TOUCH_MAX_POINTS        5

/**
 * @brief Inizializza driver touch GT911
 * 
 * @return true se inizializzazione OK, false altrimenti
 */
bool touch_gt911_init(void);

/**
 * @brief Leggi coordinate touch per LVGL
 * 
 * @param data Struttura dati LVGL da riempire
 * @return true se touch premuto, false altrimenti
 */
bool touch_gt911_read(lv_indev_data_t *data);

/**
 * @brief Deinizializza driver touch
 */
void touch_gt911_deinit(void);

/**
 * @brief Ottieni numero punti touch attivi
 * 
 * @return Numero di punti touch (0-5)
 */
uint8_t touch_gt911_get_point_count(void);

#endif // TOUCH_GT911_H
