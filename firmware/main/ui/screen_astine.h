#ifndef SCREEN_ASTINE_H
#define SCREEN_ASTINE_H

#include "lvgl.h"

/**
 * @file screen_astine.h
 * @brief Schermata astine con profili e gruppi
 * 
 * Features:
 * - Tabs gruppi (Anta/Persiana/Cremonese)
 * - Grid profili 2 colonne
 * - Display doppio: Grezza → Taglio
 * - Colori border per gruppo
 * - Pulsanti: MISURA, SALVA
 */

/**
 * @brief Crea schermata astine
 */
void screen_astine_create(void);

/**
 * @brief Aggiorna display astine
 */
void screen_astine_update(void);

/**
 * @brief Seleziona gruppo astine
 * 
 * @param group_idx Indice gruppo
 */
void screen_astine_select_group(uint8_t group_idx);

#endif // SCREEN_ASTINE_H
