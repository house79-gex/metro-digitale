#ifndef SCREEN_VETRI_WIZARD_H
#define SCREEN_VETRI_WIZARD_H

#include "lvgl.h"

/**
 * @file screen_vetri_wizard.h
 * @brief Wizard vetri L×H assistito
 * 
 * Features:
 * - Selezione materiale (cards)
 * - Display doppio L e H
 * - Wizard: materiale → L → H → review → save
 * - Calcolo gioco materiale
 * - Display raw e netto
 */

/**
 * @brief Crea schermata wizard vetri
 */
void screen_vetri_wizard_create(void);

/**
 * @brief Aggiorna display wizard
 */
void screen_vetri_wizard_update(void);

/**
 * @brief Imposta materiale selezionato
 * 
 * @param material_idx Indice materiale
 */
void screen_vetri_set_material(uint8_t material_idx);

#endif // SCREEN_VETRI_WIZARD_H
