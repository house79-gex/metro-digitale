#include "stl_parser.h"
#include "../hardware/sd_card.h"
#include "esp_log.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

static const char *TAG = "STL_PARSER";

// Helper to read float from little-endian bytes
static float read_float_le(const uint8_t *data) {
    uint32_t value = data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24);
    return *((float*)&value);
}

// Helper to read uint32 from little-endian bytes
static uint32_t read_uint32_le(const uint8_t *data) {
    return data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24);
}

esp_err_t stl_parser_load_file(const char *filepath, STLModel *model) {
    ESP_LOGI(TAG, "Loading STL file: %s", filepath);
    
    if (model == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    
    // Initialize model
    memset(model, 0, sizeof(STLModel));
    strncpy(model->filename, filepath, sizeof(model->filename) - 1);
    
    // Read file from SD card
    uint8_t *data = NULL;
    size_t file_size = 0;
    
    esp_err_t ret = sd_card_read_file(filepath, &data, &file_size);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to read STL file");
        return ret;
    }
    
    // Check minimum size (header + triangle count)
    if (file_size < STL_HEADER_SIZE + 4) {
        ESP_LOGE(TAG, "STL file too small");
        free(data);
        return ESP_FAIL;
    }
    
    // Read triangle count (after 80-byte header)
    uint32_t triangle_count = read_uint32_le(data + STL_HEADER_SIZE);
    model->triangle_count = triangle_count;
    
    ESP_LOGI(TAG, "STL contains %lu triangles", (unsigned long)triangle_count);
    
    // Verify file size matches triangle count
    size_t expected_size = STL_HEADER_SIZE + 4 + (triangle_count * STL_TRIANGLE_SIZE);
    if (file_size < expected_size) {
        ESP_LOGE(TAG, "STL file size mismatch");
        free(data);
        return ESP_FAIL;
    }
    
    // Allocate memory for triangles
    model->triangles = (STLTriangle*)malloc(triangle_count * sizeof(STLTriangle));
    if (model->triangles == NULL) {
        ESP_LOGE(TAG, "Failed to allocate memory for triangles");
        free(data);
        return ESP_ERR_NO_MEM;
    }
    
    // Parse triangles
    const uint8_t *ptr = data + STL_HEADER_SIZE + 4;
    
    for (uint32_t i = 0; i < triangle_count; i++) {
        STLTriangle *tri = &model->triangles[i];
        
        // Read normal vector (3 floats)
        tri->normal.x = read_float_le(ptr); ptr += 4;
        tri->normal.y = read_float_le(ptr); ptr += 4;
        tri->normal.z = read_float_le(ptr); ptr += 4;
        
        // Read 3 vertices (9 floats total)
        for (int v = 0; v < 3; v++) {
            tri->vertices[v].x = read_float_le(ptr); ptr += 4;
            tri->vertices[v].y = read_float_le(ptr); ptr += 4;
            tri->vertices[v].z = read_float_le(ptr); ptr += 4;
        }
        
        // Skip attribute byte count (2 bytes)
        ptr += 2;
    }
    
    free(data);
    
    // Calculate bounding box
    stl_parser_calculate_bounds(model);
    
    ESP_LOGI(TAG, "STL loaded successfully: %lu triangles", (unsigned long)triangle_count);
    ESP_LOGI(TAG, "Bounds: X[%.2f, %.2f] Y[%.2f, %.2f] Z[%.2f, %.2f]",
             model->min_x, model->max_x,
             model->min_y, model->max_y,
             model->min_z, model->max_z);
    
    return ESP_OK;
}

void stl_parser_free_model(STLModel *model) {
    if (model != NULL && model->triangles != NULL) {
        free(model->triangles);
        model->triangles = NULL;
        model->triangle_count = 0;
    }
}

void stl_parser_calculate_bounds(STLModel *model) {
    if (model == NULL || model->triangles == NULL || model->triangle_count == 0) {
        return;
    }
    
    // Initialize with first vertex
    model->min_x = model->max_x = model->triangles[0].vertices[0].x;
    model->min_y = model->max_y = model->triangles[0].vertices[0].y;
    model->min_z = model->max_z = model->triangles[0].vertices[0].z;
    
    // Find min/max for all vertices
    for (uint32_t i = 0; i < model->triangle_count; i++) {
        for (int v = 0; v < 3; v++) {
            Vertex3D *vert = &model->triangles[i].vertices[v];
            
            if (vert->x < model->min_x) model->min_x = vert->x;
            if (vert->x > model->max_x) model->max_x = vert->x;
            if (vert->y < model->min_y) model->min_y = vert->y;
            if (vert->y > model->max_y) model->max_y = vert->y;
            if (vert->z < model->min_z) model->min_z = vert->z;
            if (vert->z > model->max_z) model->max_z = vert->z;
        }
    }
}

void stl_parser_normalize_model(STLModel *model, float target_size) {
    if (model == NULL || model->triangles == NULL) {
        return;
    }
    
    // Calculate current dimensions
    float width = model->max_x - model->min_x;
    float height = model->max_y - model->min_y;
    float depth = model->max_z - model->min_z;
    
    // Find largest dimension
    float max_dim = width;
    if (height > max_dim) max_dim = height;
    if (depth > max_dim) max_dim = depth;
    
    if (max_dim == 0.0f) {
        return; // Avoid division by zero
    }
    
    // Calculate scale factor
    float scale = target_size / max_dim;
    
    // Calculate center
    float center_x = (model->min_x + model->max_x) / 2.0f;
    float center_y = (model->min_y + model->max_y) / 2.0f;
    float center_z = (model->min_z + model->max_z) / 2.0f;
    
    // Transform all vertices
    for (uint32_t i = 0; i < model->triangle_count; i++) {
        for (int v = 0; v < 3; v++) {
            Vertex3D *vert = &model->triangles[i].vertices[v];
            
            // Center and scale
            vert->x = (vert->x - center_x) * scale;
            vert->y = (vert->y - center_y) * scale;
            vert->z = (vert->z - center_z) * scale;
        }
    }
    
    // Recalculate bounds
    stl_parser_calculate_bounds(model);
    
    ESP_LOGI(TAG, "Model normalized to size %.2f", target_size);
}

bool stl_parser_is_valid_binary(const char *filepath) {
    uint8_t *data = NULL;
    size_t file_size = 0;
    
    if (sd_card_read_file(filepath, &data, &file_size) != ESP_OK) {
        return false;
    }
    
    // Check minimum size
    if (file_size < STL_HEADER_SIZE + 4) {
        free(data);
        return false;
    }
    
    // Read triangle count
    uint32_t triangle_count = read_uint32_le(data + STL_HEADER_SIZE);
    
    // Verify file size
    size_t expected_size = STL_HEADER_SIZE + 4 + (triangle_count * STL_TRIANGLE_SIZE);
    bool valid = (file_size >= expected_size);
    
    free(data);
    return valid;
}
