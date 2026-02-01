#ifndef SCREEN_SETTINGS_H
#define SCREEN_SETTINGS_H

#include "lvgl.h"

/**
 * @file screen_settings.h
 * @brief Schermata impostazioni complete
 * 
 * Features:
 * - Panel Storage (SD/USB/BLE)
 * - Panel Puntali (calibrazione)
 * - Panel Batteria (livello/autonomia)
 * - Panel Buzzer (volume/test)
 * - Panel Display (luminosità/timeout)
 * - Panel Encoder (risoluzione)
 */

/**
 * @brief Crea schermata impostazioni
 */
void screen_settings_create(void);

/**
 * @brief Aggiorna valori impostazioni
 */
void screen_settings_update(void);

#endif // SCREEN_SETTINGS_H
