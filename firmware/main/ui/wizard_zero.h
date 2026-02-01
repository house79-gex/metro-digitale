#ifndef WIZARD_ZERO_H
#define WIZARD_ZERO_H

#include "lvgl.h"
#include <stdbool.h>

/**
 * @file wizard_zero.h
 * @brief Wizard azzeramento assistito calibro
 * 
 * Procedura guidata 5 step:
 * 1. WELCOME - Introduzione
 * 2. PREPARE - Preparazione puntali
 * 3. POSITION - Posizionamento zero
 * 4. VERIFY - Verifica tolleranza
 * 5. COMPLETE - Conferma successo
 */

typedef enum {
    WIZARD_STEP_WELCOME = 0,
    WIZARD_STEP_PREPARE,
    WIZARD_STEP_POSITION,
    WIZARD_STEP_VERIFY,
    WIZARD_STEP_COMPLETE,
    WIZARD_STEP_CANCELED
} wizard_zero_step_t;

/**
 * @brief Mostra wizard azzeramento
 */
void wizard_zero_show(void);

/**
 * @brief Chiudi wizard e ritorna a schermata precedente
 */
void wizard_zero_close(void);

/**
 * @brief Avanza a step successivo
 */
void wizard_zero_next_step(void);

/**
 * @brief Cancella wizard
 */
void wizard_zero_cancel(void);

/**
 * @brief Ottieni step corrente
 * 
 * @return Step corrente
 */
wizard_zero_step_t wizard_zero_get_current_step(void);

#endif // WIZARD_ZERO_H
