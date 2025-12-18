#include "puntale_types.h"
#include <string.h>

const char* puntale_shape_to_string(PuntaleShape shape) {
    switch (shape) {
        case PUNTALE_SHAPE_FLAT:
            return "Flat";
        case PUNTALE_SHAPE_CIRCULAR:
            return "Circular";
        case PUNTALE_SHAPE_CONICAL:
            return "Conical";
        case PUNTALE_SHAPE_CUSTOM:
            return "Custom";
        default:
            return "Unknown";
    }
}

const char* puntale_reference_to_string(PuntaleReference ref) {
    switch (ref) {
        case PUNTALE_REF_EXTERNAL:
            return "EXTERNAL";
        case PUNTALE_REF_INTERNAL:
            return "INTERNAL";
        case PUNTALE_REF_CENTER:
            return "CENTER";
        default:
            return "UNKNOWN";
    }
}

float puntale_calculate_correction(const Puntale *tip) {
    if (tip == NULL) {
        return 0.0f;
    }
    
    switch (tip->reference) {
        case PUNTALE_REF_EXTERNAL:
            // External: subtract thickness
            return -tip->thickness_or_diameter_mm;
            
        case PUNTALE_REF_INTERNAL:
            // Internal: add diameter
            return tip->thickness_or_diameter_mm;
            
        case PUNTALE_REF_CENTER:
            // Center: no correction
            return 0.0f;
            
        default:
            return 0.0f;
    }
}
