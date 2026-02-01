#ifndef BOTTOM_NAV_H
#define BOTTOM_NAV_H

#include "lvgl.h"

/**
 * @file bottom_nav.h
 * @brief Bottom navigation bar 5 pulsanti
 * 
 * Navigation items:
 * - 🏠 Home
 * - 📐 Calibro
 * - 🪟 Vetri
 * - 📏 Astine
 * - ⚙️ Settings
 */

typedef enum {
    NAV_HOME = 0,
    NAV_CALIBRO,
    NAV_VETRI,
    NAV_ASTINE,
    NAV_SETTINGS
} nav_item_t;

typedef void (*nav_callback_t)(nav_item_t item);

/**
 * @brief Crea bottom navigation bar
 * 
 * @param parent Parent LVGL object
 * @param callback Callback per cambio nav
 * @return Oggetto navigation bar
 */
lv_obj_t* bottom_nav_create(lv_obj_t *parent, nav_callback_t callback);

/**
 * @brief Imposta nav item attivo
 * 
 * @param item Item da attivare
 */
void bottom_nav_set_active(nav_item_t item);

/**
 * @brief Ottieni nav item attivo
 * 
 * @return Nav item corrente
 */
nav_item_t bottom_nav_get_active(void);

#endif // BOTTOM_NAV_H
