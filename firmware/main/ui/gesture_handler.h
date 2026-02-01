#ifndef GESTURE_HANDLER_H
#define GESTURE_HANDLER_H

#include "lvgl.h"
#include <stdbool.h>

/**
 * @file gesture_handler.h
 * @brief Gesture detection per UI touch
 * 
 * Supporta:
 * - Swipe left/right/up/down
 * - Tap singolo
 * - Long press
 */

typedef enum {
    GESTURE_NONE = 0,
    GESTURE_SWIPE_LEFT,
    GESTURE_SWIPE_RIGHT,
    GESTURE_SWIPE_UP,
    GESTURE_SWIPE_DOWN,
    GESTURE_TAP,
    GESTURE_LONG_PRESS
} gesture_type_t;

typedef void (*gesture_callback_t)(gesture_type_t gesture);

/**
 * @brief Inizializza gesture handler su schermo
 * 
 * @param screen Oggetto LVGL screen
 * @param callback Funzione callback per eventi gesture
 */
void gesture_handler_init(lv_obj_t *screen, gesture_callback_t callback);

/**
 * @brief Abilita/disabilita rilevamento gesture
 * 
 * @param enable true per abilitare, false per disabilitare
 */
void gesture_handler_enable(bool enable);

/**
 * @brief Ottieni ultimo gesture rilevato
 * 
 * @return Tipo di gesture
 */
gesture_type_t gesture_handler_get_last(void);

#endif // GESTURE_HANDLER_H
