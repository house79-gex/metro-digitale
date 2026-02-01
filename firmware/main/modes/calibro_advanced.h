#ifndef CALIBRO_ADVANCED_H
#define CALIBRO_ADVANCED_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file calibro_advanced.h
 * @brief Modalità calibro professionale con statistiche
 * 
 * Supporta:
 * - Misure esterne e interne (NO profondità)
 * - Conversione unità (mm, cm, inch, frazionari)
 * - Statistiche real-time (min, max, avg, std dev)
 * - Hold, Zero assistito, Tolleranza
 */

// Tipo di misura supportati
typedef enum {
    CALIBRO_MEASURE_EXTERNAL = 0,  // Misura esterna
    CALIBRO_MEASURE_INTERNAL       // Misura interna
    // DEPTH e STEP rimossi in v2.0
} calibro_measure_type_t;

// Unità di misura
typedef enum {
    UNIT_MM = 0,              // Millimetri
    UNIT_CM,                  // Centimetri
    UNIT_INCH,                // Pollici decimali
    UNIT_FRACTIONAL_INCH      // Pollici frazionari (1/64")
} measurement_unit_t;

// Statistiche misure
typedef struct {
    float min_mm;             // Valore minimo
    float max_mm;             // Valore massimo
    float avg_mm;             // Media
    float std_dev_mm;         // Deviazione standard
    uint32_t count;           // Numero misure
    float sum_mm;             // Somma (per calcolo media incrementale)
    float sum_squares_mm;     // Somma quadrati (per std dev)
} calibro_statistics_t;

// Stato modalità calibro
typedef struct {
    calibro_measure_type_t measure_type;  // Tipo misura corrente
    measurement_unit_t unit;               // Unità di misura corrente
    bool hold_active;                      // Hold attivo
    float hold_value_mm;                   // Valore in hold
    float current_value_mm;                // Valore corrente
    calibro_statistics_t stats;            // Statistiche
    float history[100];                    // Storico ultime 100 misure
    uint16_t history_index;                // Indice circolare history
    float tolerance_plus_mm;               // Tolleranza superiore
    float tolerance_minus_mm;              // Tolleranza inferiore
    bool tolerance_enabled;                // Tolleranza abilitata
} calibro_state_t;

/**
 * @brief Inizializza modalità calibro
 * 
 * @param state Struttura stato (output)
 */
void calibro_mode_init(calibro_state_t *state);

/**
 * @brief Imposta tipo di misura
 * 
 * Cambia tra misura esterna/interna con calcolo automatico offset puntali.
 * 
 * @param state Stato calibro
 * @param type Tipo misura
 */
void calibro_set_measure_type(calibro_state_t *state, calibro_measure_type_t type);

/**
 * @brief Imposta unità di misura
 * 
 * @param state Stato calibro
 * @param unit Unità di misura
 */
void calibro_set_unit(calibro_state_t *state, measurement_unit_t unit);

/**
 * @brief Ottieni valore corrente con offset e correzioni
 * 
 * Applica:
 * - Offset puntali (esterno/interno)
 * - Compensazione usura
 * - Calibrazione zero
 * 
 * @param state Stato calibro
 * @param encoder_mm Lettura encoder in mm
 * @return Valore corretto in mm
 */
float calibro_get_current_value(calibro_state_t *state, float encoder_mm);

/**
 * @brief Toggle hold misura
 * 
 * Attiva/disattiva hold. Quando attivo, salva automaticamente in statistiche.
 * 
 * @param state Stato calibro
 */
void calibro_toggle_hold(calibro_state_t *state);

/**
 * @brief Aggiungi misura a statistiche
 * 
 * Calcola automaticamente min, max, avg, std dev.
 * 
 * @param state Stato calibro
 * @param value_mm Valore da aggiungere
 */
void calibro_add_to_stats(calibro_state_t *state, float value_mm);

/**
 * @brief Resetta statistiche
 * 
 * @param state Stato calibro
 */
void calibro_reset_stats(calibro_state_t *state);

/**
 * @brief Formatta valore con conversione unità
 * 
 * Converte da mm all'unità selezionata e formatta come stringa.
 * 
 * @param state Stato calibro
 * @param value_mm Valore in mm
 * @param buffer Buffer output
 * @param buffer_size Dimensione buffer
 */
void calibro_format_value(const calibro_state_t *state, float value_mm,
                         char *buffer, size_t buffer_size);

/**
 * @brief Verifica tolleranza
 * 
 * @param state Stato calibro
 * @param value_mm Valore da verificare
 * @return true se dentro tolleranza, false se fuori
 */
bool calibro_check_tolerance(const calibro_state_t *state, float value_mm);

/**
 * @brief Imposta tolleranza
 * 
 * @param state Stato calibro
 * @param plus_mm Tolleranza superiore (mm)
 * @param minus_mm Tolleranza inferiore (mm)
 */
void calibro_set_tolerance(calibro_state_t *state, float plus_mm, float minus_mm);

/**
 * @brief Abilita/disabilita tolleranza
 * 
 * @param state Stato calibro
 * @param enabled true per abilitare
 */
void calibro_enable_tolerance(calibro_state_t *state, bool enabled);

/**
 * @brief Ottieni nome tipo misura
 * 
 * @param type Tipo misura
 * @return Stringa nome
 */
const char* calibro_get_measure_type_name(calibro_measure_type_t type);

/**
 * @brief Ottieni simbolo unità
 * 
 * @param unit Unità di misura
 * @return Stringa simbolo (es. "mm", "cm", "in")
 */
const char* calibro_get_unit_symbol(measurement_unit_t unit);

#endif // CALIBRO_ADVANCED_H
