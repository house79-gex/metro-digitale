#include "measure_calculator.h"
#include "esp_log.h"
#include <string.h>
#include <stdio.h>

static const char *TAG = "MEASURE_CALC";

esp_err_t measure_calculator_calculate(const MeasurementInput *input, MeasurementResult *result) {
    if (input == NULL || result == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    
    // Initialize result
    memset(result, 0, sizeof(MeasurementResult));
    
    // Copy raw encoder value
    result->encoder_raw_mm = input->encoder_raw_mm;
    result->correction_factor = input->correction_factor;
    result->additional_offset_mm = input->additional_offset_mm;
    
    // Calculate range offsets
    result->range_offset_left_mm = (input->tip_left != NULL) ? input->tip_left->range_offset_mm : 0.0f;
    result->range_offset_right_mm = (input->tip_right != NULL) ? input->tip_right->range_offset_mm : 0.0f;
    
    // Calculate tip corrections based on reference type
    result->correction_left_mm = (input->tip_left != NULL) ? puntale_calculate_correction(input->tip_left) : 0.0f;
    result->correction_right_mm = (input->tip_right != NULL) ? puntale_calculate_correction(input->tip_right) : 0.0f;
    
    // Apply universal formula:
    // Net = (Encoder + RangeLeft + RangeRight + CorrLeft + CorrRight) * Factor + AdditionalOffset
    float net = input->encoder_raw_mm;
    net += result->range_offset_left_mm;
    net += result->range_offset_right_mm;
    net += result->correction_left_mm;
    net += result->correction_right_mm;
    net *= input->correction_factor;
    net += input->additional_offset_mm;
    
    result->net_measurement_mm = net;
    
    // Generate formula text
    measure_calculator_format_formula(input, result, result->formula_text, sizeof(result->formula_text));
    
    ESP_LOGD(TAG, "Calculation: Raw=%.2f, Left=[offset:%.2f, corr:%.2f], Right=[offset:%.2f, corr:%.2f], Net=%.2f",
             result->encoder_raw_mm,
             result->range_offset_left_mm, result->correction_left_mm,
             result->range_offset_right_mm, result->correction_right_mm,
             result->net_measurement_mm);
    
    return ESP_OK;
}

void measure_calculator_format_formula(const MeasurementInput *input, 
                                       const MeasurementResult *result,
                                       char *buffer, size_t buffer_size) {
    if (buffer == NULL || buffer_size == 0) {
        return;
    }
    
    char temp[256];
    int offset = 0;
    
    // Start with raw encoder
    offset += snprintf(buffer + offset, buffer_size - offset, "%.2f", result->encoder_raw_mm);
    
    // Add range offsets
    if (result->range_offset_left_mm != 0.0f) {
        offset += snprintf(buffer + offset, buffer_size - offset, " %+.2f", result->range_offset_left_mm);
    }
    if (result->range_offset_right_mm != 0.0f) {
        offset += snprintf(buffer + offset, buffer_size - offset, " %+.2f", result->range_offset_right_mm);
    }
    
    // Add tip corrections with explanations
    if (result->correction_left_mm != 0.0f && input->tip_left != NULL) {
        const char *ref_str = puntale_reference_to_string(input->tip_left->reference);
        offset += snprintf(buffer + offset, buffer_size - offset, " %+.2f[L:%s]", 
                          result->correction_left_mm, ref_str);
    }
    
    if (result->correction_right_mm != 0.0f && input->tip_right != NULL) {
        const char *ref_str = puntale_reference_to_string(input->tip_right->reference);
        offset += snprintf(buffer + offset, buffer_size - offset, " %+.2f[R:%s]", 
                          result->correction_right_mm, ref_str);
    }
    
    // Add correction factor if not 1.0
    if (result->correction_factor != 1.0f) {
        offset += snprintf(buffer + offset, buffer_size - offset, " × %.3f", result->correction_factor);
    }
    
    // Add additional offset
    if (result->additional_offset_mm != 0.0f) {
        offset += snprintf(buffer + offset, buffer_size - offset, " %+.2f", result->additional_offset_mm);
    }
    
    // Add result
    offset += snprintf(buffer + offset, buffer_size - offset, " = %.2f mm", result->net_measurement_mm);
}

bool measure_calculator_validate_range(float measurement_mm, float min_mm, float max_mm) {
    return (measurement_mm >= min_mm && measurement_mm <= max_mm);
}
