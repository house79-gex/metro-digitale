#ifndef SCREEN_CALIBRO_ADVANCED_H
#define SCREEN_CALIBRO_ADVANCED_H

#include "lvgl.h"

/**
 * @file screen_calibro_advanced.h
 * @brief Schermata calibro avanzata con statistiche
 * 
 * Features:
 * - Display misura principale grande
 * - Conversione unità (mm/cm/inch/1-64")
 * - LED tolleranza con animazione
 * - Tipo misura (Esterna/Interna)
 * - Statistiche (Min/Max/Avg/StdDev/Count)
 * - Pulsanti: ZERO, HOLD, STATS, RESET
 */

/**
 * @brief Crea schermata calibro avanzata
 */
void screen_calibro_advanced_create(void);

/**
 * @brief Aggiorna valore misura
 * 
 * @param value_mm Valore in millimetri
 */
void screen_calibro_update_value(float value_mm);

/**
 * @brief Mostra/nascondi panel statistiche
 * 
 * @param show true per mostrare, false per nascondere
 */
void screen_calibro_toggle_stats(bool show);

/**
 * @brief Reset statistiche
 */
void screen_calibro_reset_stats(void);

#endif // SCREEN_CALIBRO_ADVANCED_H
