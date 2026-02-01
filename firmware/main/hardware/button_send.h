#ifndef BUTTON_SEND_H
#define BUTTON_SEND_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

/**
 * @file button_send.h
 * @brief Driver pulsante fisico SEND con funzionalità avanzate
 * 
 * Supporta:
 * - Debouncing hardware (50ms)
 * - Click singolo
 * - Long press (>1000ms)
 * - Double click (<400ms tra click)
 * - Callback personalizzabili
 */

// Tipi di evento pulsante
typedef enum {
    BUTTON_EVENT_SINGLE_CLICK,   // Click singolo
    BUTTON_EVENT_DOUBLE_CLICK,   // Double click
    BUTTON_EVENT_LONG_PRESS,     // Long press (>1s)
    BUTTON_EVENT_LONG_RELEASE    // Rilascio dopo long press
} button_event_type_t;

// Callback evento pulsante
typedef void (*button_event_callback_t)(button_event_type_t event);

/**
 * @brief Inizializza driver pulsante SEND
 * 
 * @param gpio_pin Pin GPIO del pulsante
 * @param callback Callback per eventi (opzionale, può essere NULL)
 * @return true se inizializzazione OK, false altrimenti
 */
bool button_send_init(gpio_num_t gpio_pin, button_event_callback_t callback);

/**
 * @brief Registra callback per eventi pulsante
 * 
 * @param callback Funzione callback
 */
void button_send_register_callback(button_event_callback_t callback);

/**
 * @brief Ottieni stato corrente pulsante
 * 
 * @return true se premuto, false se rilasciato
 */
bool button_send_is_pressed(void);

/**
 * @brief Abilita/disabilita rilevamento eventi
 * 
 * @param enable true per abilitare, false per disabilitare
 */
void button_send_enable(bool enable);

/**
 * @brief Deinizializza driver pulsante
 */
void button_send_deinit(void);

/**
 * @brief Ottieni numero eventi processati (per debug)
 * 
 * @return Numero totale eventi
 */
uint32_t button_send_get_event_count(void);

#endif // BUTTON_SEND_H
