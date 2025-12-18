#ifndef MEASURE_CALCULATOR_H
#define MEASURE_CALCULATOR_H

#include "../puntali/puntale_types.h"
#include "esp_err.h"

// Measurement mode types
typedef enum {
    MEASURE_MODE_FERMAVETRO = 0,
    MEASURE_MODE_VETRI,
    MEASURE_MODE_ASTINE,
    MEASURE_MODE_CALIBRO,
    MEASURE_MODE_RILIEVI_SPECIALI
} MeasureMode;

// Mode configuration (which tips to use)
typedef struct {
    MeasureMode mode;
    char tip_left_id[PUNTALE_ID_MAX];
    char tip_right_id[PUNTALE_ID_MAX];
    float correction_factor;          // Multiplier (default 1.0)
    float additional_offset_mm;       // Additional offset to add
    bool enabled;
} ModeConfiguration;

// Measurement input
typedef struct {
    float encoder_raw_mm;             // Raw encoder reading
    Puntale *tip_left;                // Left tip (can be NULL)
    Puntale *tip_right;               // Right tip (can be NULL)
    float correction_factor;          // Correction multiplier
    float additional_offset_mm;       // Additional offset
} MeasurementInput;

// Measurement result
typedef struct {
    float encoder_raw_mm;             // Raw encoder value
    float range_offset_left_mm;       // Left tip range offset
    float range_offset_right_mm;      // Right tip range offset
    float correction_left_mm;         // Left tip correction (based on reference)
    float correction_right_mm;        // Right tip correction (based on reference)
    float correction_factor;          // Applied multiplier
    float additional_offset_mm;       // Additional offset applied
    float net_measurement_mm;         // Final calculated result
    char formula_text[256];           // Human-readable formula
} MeasurementResult;

// Calculate net measurement using universal formula
esp_err_t measure_calculator_calculate(const MeasurementInput *input, MeasurementResult *result);

// Generate human-readable formula description
void measure_calculator_format_formula(const MeasurementInput *input, 
                                       const MeasurementResult *result,
                                       char *buffer, size_t buffer_size);

// Validate measurement is within reasonable range
bool measure_calculator_validate_range(float measurement_mm, float min_mm, float max_mm);

#endif // MEASURE_CALCULATOR_H
