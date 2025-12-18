#ifndef PUNTALE_TYPES_H
#define PUNTALE_TYPES_H

#include <stdint.h>
#include <stdbool.h>

// Maximum dimensions
#define PUNTALE_NAME_MAX        48
#define PUNTALE_ID_MAX          32
#define MAX_PUNTALI             32
#define MAX_STL_VERTICES        2048
#define MAX_STL_TRIANGLES       2048

// Tip shape types
typedef enum {
    PUNTALE_SHAPE_FLAT = 0,     // Flat tip (thickness)
    PUNTALE_SHAPE_CIRCULAR,     // Circular tip (diameter)
    PUNTALE_SHAPE_CONICAL,      // Conical tip (no offset)
    PUNTALE_SHAPE_CUSTOM        // Custom 3D shape from STL
} PuntaleShape;

// Tip reference type (measurement direction)
typedef enum {
    PUNTALE_REF_EXTERNAL = 0,   // External measurement (subtract thickness)
    PUNTALE_REF_INTERNAL,       // Internal measurement (add diameter)
    PUNTALE_REF_CENTER          // Center reference (no correction)
} PuntaleReference;

// 3D vertex (for STL rendering)
typedef struct {
    float x;
    float y;
    float z;
} Vertex3D;

// STL triangle
typedef struct {
    Vertex3D normal;
    Vertex3D vertices[3];
} STLTriangle;

// STL model data
typedef struct {
    char filename[64];
    uint32_t triangle_count;
    STLTriangle *triangles;  // Dynamic allocation
    
    // Bounding box (for scaling/centering)
    float min_x, max_x;
    float min_y, max_y;
    float min_z, max_z;
} STLModel;

// Tip configuration
typedef struct {
    char id[PUNTALE_ID_MAX];           // Unique identifier (e.g., "fermavetro_20x30")
    char nome[PUNTALE_NAME_MAX];       // Display name
    
    PuntaleShape shape;                // Shape type
    float thickness_or_diameter_mm;    // Thickness (flat) or diameter (circular)
    PuntaleReference reference;        // Measurement reference type
    float range_offset_mm;             // Encoder base adjustment
    
    bool has_stl;                      // Has 3D model
    char stl_filename[64];             // STL file path
    STLModel *stl_model;               // Loaded STL data (NULL if not loaded)
    
    bool active;                       // Is tip active/enabled
    uint32_t last_used_timestamp;      // Last usage timestamp
} Puntale;

// Measurement correction calculation result
typedef struct {
    float correction_left_mm;          // Left tip correction
    float correction_right_mm;         // Right tip correction
    float net_measurement_mm;          // Final calculated measurement
    char formula_description[128];     // Human-readable formula
} MeasurementCorrection;

// Convert shape enum to string
const char* puntale_shape_to_string(PuntaleShape shape);

// Convert reference enum to string  
const char* puntale_reference_to_string(PuntaleReference ref);

// Calculate correction for a tip based on reference type
float puntale_calculate_correction(const Puntale *tip);

#endif // PUNTALE_TYPES_H
