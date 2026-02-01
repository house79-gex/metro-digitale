#ifndef MODE_FERMAVETRI_H
#define MODE_FERMAVETRI_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/**
 * @file mode_fermavetri.h
 * @brief Modalità fermavetri con invio diretto a troncatrice Blitz CNC
 * 
 * Misura rapida fermavetri con trigger automatico taglio su Blitz.
 */

// Misura fermavetro
typedef struct {
    float lunghezza_mm;          // Lunghezza misurata
    uint32_t timestamp;          // Timestamp misura
    bool auto_start;             // Auto-start taglio su Blitz
    bool mode_blitz;             // Modalità Blitz attiva
    char note[64];               // Note aggiuntive
} fermavetro_measurement_t;

// Stato modalità fermavetri
typedef struct {
    fermavetro_measurement_t current_measure;
    bool semi_auto_enabled;      // Modalità semi-automatica
    bool measurement_saved;
} mode_fermavetri_state_t;

/**
 * @brief Inizializza modalità fermavetri
 * 
 * Setup default: semi_auto enabled
 * 
 * @param state Stato modalità (output)
 */
void mode_fermavetri_init(mode_fermavetri_state_t *state);

/**
 * @brief Misura fermavetro
 * 
 * Lettura encoder diretta.
 * 
 * @param state Stato modalità
 * @param encoder_mm Lettura encoder
 */
void mode_fermavetri_measure(mode_fermavetri_state_t *state, float encoder_mm);

/**
 * @brief Invia misura a troncatrice Blitz via BLE
 * 
 * Formato JSON specifico per Blitz:
 * {
 *   "type": "fermavetro",
 *   "misura_mm": 1250.5,
 *   "auto_start": true,
 *   "mode": "semi_auto"
 * }
 * 
 * @param state Stato modalità
 * @return true se invio OK, false altrimenti
 */
bool mode_fermavetri_send_to_blitz(const mode_fermavetri_state_t *state);

/**
 * @brief Abilita/disabilita modalità semi-automatica
 * 
 * @param state Stato modalità
 * @param enabled true per abilitare
 */
void mode_fermavetri_set_semi_auto(mode_fermavetri_state_t *state, bool enabled);

/**
 * @brief Imposta auto-start taglio
 * 
 * @param state Stato modalità
 * @param auto_start true per auto-start
 */
void mode_fermavetri_set_auto_start(mode_fermavetri_state_t *state, bool auto_start);

/**
 * @brief Resetta misura corrente
 * 
 * @param state Stato modalità
 */
void mode_fermavetri_reset(mode_fermavetri_state_t *state);

#endif // MODE_FERMAVETRI_H
