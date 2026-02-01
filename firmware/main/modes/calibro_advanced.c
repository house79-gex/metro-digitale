#include "calibro_advanced.h"
#include <string.h>
#include <math.h>
#include <stdio.h>

// Fattori di conversione
#define MM_TO_CM        0.1f
#define MM_TO_INCH      0.0393700787f
#define INCH_TO_64THS   64.0f

void calibro_mode_init(calibro_state_t *state) {
    if (!state) return;
    
    memset(state, 0, sizeof(calibro_state_t));
    state->measure_type = CALIBRO_MEASURE_EXTERNAL;
    state->unit = UNIT_MM;
    state->tolerance_plus_mm = 0.1f;
    state->tolerance_minus_mm = 0.1f;
    state->tolerance_enabled = false;
}

void calibro_set_measure_type(calibro_state_t *state, calibro_measure_type_t type) {
    if (!state) return;
    state->measure_type = type;
}

void calibro_set_unit(calibro_state_t *state, measurement_unit_t unit) {
    if (!state) return;
    state->unit = unit;
}

float calibro_get_current_value(calibro_state_t *state, float encoder_mm) {
    if (!state) return encoder_mm;
    
    // Il calcolo offset puntali è gestito dal modulo puntale_circular
    // Qui ritorniamo il valore encoder diretto
    state->current_value_mm = encoder_mm;
    return encoder_mm;
}

void calibro_toggle_hold(calibro_state_t *state) {
    if (!state) return;
    
    state->hold_active = !state->hold_active;
    
    if (state->hold_active) {
        // Salva valore corrente
        state->hold_value_mm = state->current_value_mm;
        
        // Aggiungi automaticamente alle statistiche
        calibro_add_to_stats(state, state->hold_value_mm);
    }
}

void calibro_add_to_stats(calibro_state_t *state, float value_mm) {
    if (!state) return;
    
    calibro_statistics_t *stats = &state->stats;
    
    // Prima misura
    if (stats->count == 0) {
        stats->min_mm = value_mm;
        stats->max_mm = value_mm;
        stats->avg_mm = value_mm;
        stats->std_dev_mm = 0.0f;
    } else {
        // Aggiorna min/max
        if (value_mm < stats->min_mm) stats->min_mm = value_mm;
        if (value_mm > stats->max_mm) stats->max_mm = value_mm;
    }
    
    // Aggiorna somme per calcolo incrementale
    stats->sum_mm += value_mm;
    stats->sum_squares_mm += (value_mm * value_mm);
    stats->count++;
    
    // Calcola media
    stats->avg_mm = stats->sum_mm / stats->count;
    
    // Calcola deviazione standard (formula incrementale)
    if (stats->count > 1) {
        float variance = (stats->sum_squares_mm / stats->count) - 
                        (stats->avg_mm * stats->avg_mm);
        stats->std_dev_mm = sqrtf(fabsf(variance));
    }
    
    // Aggiungi allo storico
    state->history[state->history_index] = value_mm;
    state->history_index = (state->history_index + 1) % 100;
}

void calibro_reset_stats(calibro_state_t *state) {
    if (!state) return;
    
    memset(&state->stats, 0, sizeof(calibro_statistics_t));
    memset(state->history, 0, sizeof(state->history));
    state->history_index = 0;
}

void calibro_format_value(const calibro_state_t *state, float value_mm,
                         char *buffer, size_t buffer_size) {
    if (!state || !buffer) return;
    
    switch (state->unit) {
        case UNIT_MM:
            snprintf(buffer, buffer_size, "%.2f mm", value_mm);
            break;
        
        case UNIT_CM:
            snprintf(buffer, buffer_size, "%.3f cm", value_mm * MM_TO_CM);
            break;
        
        case UNIT_INCH:
            snprintf(buffer, buffer_size, "%.4f in", value_mm * MM_TO_INCH);
            break;
        
        case UNIT_FRACTIONAL_INCH: {
            float inches = value_mm * MM_TO_INCH;
            int whole = (int)inches;
            float frac = (inches - whole) * INCH_TO_64THS;
            int numerator = (int)(frac + 0.5f);
            
            // Semplifica frazione
            if (numerator == 64) {
                whole++;
                numerator = 0;
            }
            
            if (numerator == 0) {
                snprintf(buffer, buffer_size, "%d\"", whole);
            } else {
                snprintf(buffer, buffer_size, "%d %d/64\"", whole, numerator);
            }
            break;
        }
        
        default:
            snprintf(buffer, buffer_size, "%.2f mm", value_mm);
            break;
    }
}

bool calibro_check_tolerance(const calibro_state_t *state, float value_mm) {
    if (!state || !state->tolerance_enabled) return true;
    
    float nominal = state->hold_value_mm; // Usa hold come riferimento
    float upper = nominal + state->tolerance_plus_mm;
    float lower = nominal - state->tolerance_minus_mm;
    
    return (value_mm >= lower && value_mm <= upper);
}

void calibro_set_tolerance(calibro_state_t *state, float plus_mm, float minus_mm) {
    if (!state) return;
    
    state->tolerance_plus_mm = plus_mm;
    state->tolerance_minus_mm = minus_mm;
}

void calibro_enable_tolerance(calibro_state_t *state, bool enabled) {
    if (!state) return;
    
    state->tolerance_enabled = enabled;
}

const char* calibro_get_measure_type_name(calibro_measure_type_t type) {
    switch (type) {
        case CALIBRO_MEASURE_EXTERNAL:
            return "Esterna";
        case CALIBRO_MEASURE_INTERNAL:
            return "Interna";
        default:
            return "Sconosciuta";
    }
}

const char* calibro_get_unit_symbol(measurement_unit_t unit) {
    switch (unit) {
        case UNIT_MM:
            return "mm";
        case UNIT_CM:
            return "cm";
        case UNIT_INCH:
            return "in";
        case UNIT_FRACTIONAL_INCH:
            return "in (fraz)";
        default:
            return "?";
    }
}
