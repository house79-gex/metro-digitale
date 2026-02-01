#ifndef DISPLAY_RGB_H
#define DISPLAY_RGB_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file display_rgb.h
 * @brief Driver display RGB parallelo 800×480
 * 
 * Supporto display integrato ESP32-S3 5" con RGB parallel interface.
 */

/**
 * @brief Inizializza driver display RGB
 * 
 * - Configura GPIO RGB parallelo (1-16, 39-42, 45, 48)
 * - Setup panel 800×480 @ 18MHz pixel clock
 * - Double buffering con framebuffer in PSRAM
 * - Integrazione con LVGL
 * 
 * @return true se inizializzazione OK, false altrimenti
 */
bool display_rgb_init(void);

/**
 * @brief Imposta luminosità backlight
 * 
 * Controlla PWM su GPIO 45.
 * 
 * @param brightness Luminosità 0-100%
 */
void display_backlight_set(uint8_t brightness);

/**
 * @brief Ottieni luminosità backlight corrente
 * 
 * @return Luminosità 0-100%
 */
uint8_t display_backlight_get(void);

/**
 * @brief Deinizializza driver display
 */
void display_rgb_deinit(void);

#endif // DISPLAY_RGB_H
