#ifndef STL_PARSER_H
#define STL_PARSER_H

#include "puntale_types.h"
#include "esp_err.h"

// STL file header size (binary format)
#define STL_HEADER_SIZE     80
#define STL_TRIANGLE_SIZE   50  // 12 floats (4 bytes each) + 2 bytes attribute

// Parse STL binary file and load into model
esp_err_t stl_parser_load_file(const char *filepath, STLModel *model);

// Free STL model memory
void stl_parser_free_model(STLModel *model);

// Calculate bounding box for model
void stl_parser_calculate_bounds(STLModel *model);

// Normalize model to fit in unit cube (for display)
void stl_parser_normalize_model(STLModel *model, float target_size);

// Verify STL file is valid binary format
bool stl_parser_is_valid_binary(const char *filepath);

#endif // STL_PARSER_H
