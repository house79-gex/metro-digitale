#include "puntale_database.h"
#include "stl_parser.h"
#include "../hardware/sd_card.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string.h>
#include <stdlib.h>

static const char *TAG = "PUNTALE_DB";
static const char *NVS_NAMESPACE = "puntali";

// Global tip database (in-memory)
static Puntale tip_database[MAX_PUNTALI];
static size_t tip_count = 0;

esp_err_t puntale_database_init(void) {
    ESP_LOGI(TAG, "Initializing tip database");
    
    memset(tip_database, 0, sizeof(tip_database));
    tip_count = 0;
    
    // Scan NVS for saved tips
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs_handle);
    
    if (ret == ESP_OK) {
        // Iterate through all keys (this is simplified - in practice, need to track tip IDs)
        nvs_close(nvs_handle);
    }
    
    // Scan SD card for STL files
    if (sd_card_is_mounted()) {
        puntale_database_scan_sd_card();
    }
    
    ESP_LOGI(TAG, "Tip database initialized with %d tips", tip_count);
    return ESP_OK;
}

esp_err_t puntale_database_scan_sd_card(void) {
    char **file_list = NULL;
    size_t count = 0;
    
    esp_err_t ret = sd_card_list_files(SD_DIR_PUNTALI, &file_list, &count);
    if (ret != ESP_OK || count == 0) {
        ESP_LOGI(TAG, "No STL files found in directory %s (error: %s)", 
                 SD_DIR_PUNTALI, esp_err_to_name(ret));
        return ESP_OK;
    }
    
    ESP_LOGI(TAG, "Found %d files in puntali directory", count);
    
    for (size_t i = 0; i < count && tip_count < MAX_PUNTALI; i++) {
        const char *filename = file_list[i];
        
        // Check if .stl file
        size_t len = strlen(filename);
        if (len > 4 && strcmp(&filename[len - 4], ".stl") == 0) {
            // Extract ID from filename (remove .stl extension)
            char id[PUNTALE_ID_MAX];
            strncpy(id, filename, len - 4);
            id[len - 4] = '\0';
            
            // Check if tip already exists
            Puntale *existing = puntale_database_get_by_id(id);
            if (existing == NULL) {
                // Create new tip entry
                Puntale tip;
                memset(&tip, 0, sizeof(Puntale));
                
                strncpy(tip.id, id, PUNTALE_ID_MAX - 1);
                strncpy(tip.nome, id, PUNTALE_NAME_MAX - 1); // Use ID as default name
                snprintf(tip.stl_filename, sizeof(tip.stl_filename), "%s/%s", SD_DIR_PUNTALI, filename);
                
                tip.shape = PUNTALE_SHAPE_CUSTOM;
                tip.reference = PUNTALE_REF_EXTERNAL;
                tip.has_stl = true;
                tip.active = true;
                
                // Try to load config from NVS
                puntale_database_load_from_nvs(id, &tip);
                
                // Add to database
                memcpy(&tip_database[tip_count], &tip, sizeof(Puntale));
                tip_count++;
                
                ESP_LOGI(TAG, "Added tip: %s", id);
            }
        }
    }
    
    sd_card_free_file_list(file_list, count);
    return ESP_OK;
}

size_t puntale_database_get_count(void) {
    return tip_count;
}

Puntale* puntale_database_get_by_index(size_t index) {
    if (index >= tip_count) {
        return NULL;
    }
    return &tip_database[index];
}

Puntale* puntale_database_get_by_id(const char *id) {
    for (size_t i = 0; i < tip_count; i++) {
        if (strcmp(tip_database[i].id, id) == 0) {
            return &tip_database[i];
        }
    }
    return NULL;
}

esp_err_t puntale_database_add_or_update(const Puntale *tip) {
    if (tip == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    
    // Check if tip exists
    Puntale *existing = puntale_database_get_by_id(tip->id);
    
    if (existing != NULL) {
        // Update existing
        memcpy(existing, tip, sizeof(Puntale));
        ESP_LOGI(TAG, "Updated tip: %s", tip->id);
    } else {
        // Add new
        if (tip_count >= MAX_PUNTALI) {
            ESP_LOGE(TAG, "Tip database full");
            return ESP_ERR_NO_MEM;
        }
        
        memcpy(&tip_database[tip_count], tip, sizeof(Puntale));
        tip_count++;
        ESP_LOGI(TAG, "Added new tip: %s", tip->id);
    }
    
    // Save to NVS
    return puntale_database_save_to_nvs(tip);
}

esp_err_t puntale_database_delete(const char *id) {
    for (size_t i = 0; i < tip_count; i++) {
        if (strcmp(tip_database[i].id, id) == 0) {
            // Unload STL if loaded
            puntale_database_unload_stl(&tip_database[i]);
            
            // Shift remaining tips
            for (size_t j = i; j < tip_count - 1; j++) {
                memcpy(&tip_database[j], &tip_database[j + 1], sizeof(Puntale));
            }
            tip_count--;
            
            ESP_LOGI(TAG, "Deleted tip: %s", id);
            return ESP_OK;
        }
    }
    
    return ESP_ERR_NOT_FOUND;
}

esp_err_t puntale_database_save_to_nvs(const Puntale *tip) {
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &nvs_handle);
    
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to open NVS");
        return ret;
    }
    
    // Save tip configuration (using tip ID as key prefix)
    char key[32];
    
    snprintf(key, sizeof(key), "%s_shape", tip->id);
    nvs_set_u8(nvs_handle, key, (uint8_t)tip->shape);
    
    snprintf(key, sizeof(key), "%s_thick", tip->id);
    uint32_t thick_bits = *((uint32_t*)&tip->thickness_or_diameter_mm);
    nvs_set_u32(nvs_handle, key, thick_bits);
    
    snprintf(key, sizeof(key), "%s_ref", tip->id);
    nvs_set_u8(nvs_handle, key, (uint8_t)tip->reference);
    
    snprintf(key, sizeof(key), "%s_offset", tip->id);
    uint32_t offset_bits = *((uint32_t*)&tip->range_offset_mm);
    nvs_set_u32(nvs_handle, key, offset_bits);
    
    snprintf(key, sizeof(key), "%s_name", tip->id);
    nvs_set_str(nvs_handle, key, tip->nome);
    
    nvs_commit(nvs_handle);
    nvs_close(nvs_handle);
    
    ESP_LOGI(TAG, "Saved tip config to NVS: %s", tip->id);
    return ESP_OK;
}

esp_err_t puntale_database_load_from_nvs(const char *id, Puntale *tip) {
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs_handle);
    
    if (ret != ESP_OK) {
        return ret;
    }
    
    char key[32];
    uint8_t u8_val;
    uint32_t u32_val;
    size_t str_len;
    
    // Load shape
    snprintf(key, sizeof(key), "%s_shape", id);
    if (nvs_get_u8(nvs_handle, key, &u8_val) == ESP_OK) {
        tip->shape = (PuntaleShape)u8_val;
    }
    
    // Load thickness/diameter
    snprintf(key, sizeof(key), "%s_thick", id);
    if (nvs_get_u32(nvs_handle, key, &u32_val) == ESP_OK) {
        tip->thickness_or_diameter_mm = *((float*)&u32_val);
    }
    
    // Load reference
    snprintf(key, sizeof(key), "%s_ref", id);
    if (nvs_get_u8(nvs_handle, key, &u8_val) == ESP_OK) {
        tip->reference = (PuntaleReference)u8_val;
    }
    
    // Load offset
    snprintf(key, sizeof(key), "%s_offset", id);
    if (nvs_get_u32(nvs_handle, key, &u32_val) == ESP_OK) {
        tip->range_offset_mm = *((float*)&u32_val);
    }
    
    // Load name
    snprintf(key, sizeof(key), "%s_name", id);
    str_len = PUNTALE_NAME_MAX;
    nvs_get_str(nvs_handle, key, tip->nome, &str_len);
    
    nvs_close(nvs_handle);
    return ESP_OK;
}

esp_err_t puntale_database_load_stl(Puntale *tip) {
    if (tip == NULL || !tip->has_stl) {
        return ESP_ERR_INVALID_ARG;
    }
    
    if (tip->stl_model != NULL) {
        // Already loaded
        return ESP_OK;
    }
    
    // Allocate STL model
    tip->stl_model = (STLModel*)malloc(sizeof(STLModel));
    if (tip->stl_model == NULL) {
        ESP_LOGE(TAG, "Failed to allocate STL model");
        return ESP_ERR_NO_MEM;
    }
    
    // Load STL file
    esp_err_t ret = stl_parser_load_file(tip->stl_filename, tip->stl_model);
    if (ret != ESP_OK) {
        free(tip->stl_model);
        tip->stl_model = NULL;
        return ret;
    }
    
    // Normalize for display
    stl_parser_normalize_model(tip->stl_model, 100.0f); // 100 units
    
    ESP_LOGI(TAG, "Loaded STL model for tip: %s", tip->id);
    return ESP_OK;
}

void puntale_database_unload_stl(Puntale *tip) {
    if (tip != NULL && tip->stl_model != NULL) {
        stl_parser_free_model(tip->stl_model);
        free(tip->stl_model);
        tip->stl_model = NULL;
        ESP_LOGI(TAG, "Unloaded STL model for tip: %s", tip->id);
    }
}

esp_err_t puntale_database_backup_to_sd(void) {
    // TODO: Implement JSON backup
    ESP_LOGW(TAG, "Backup to SD not yet implemented");
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t puntale_database_restore_from_sd(void) {
    // TODO: Implement JSON restore
    ESP_LOGW(TAG, "Restore from SD not yet implemented");
    return ESP_ERR_NOT_SUPPORTED;
}

esp_err_t puntale_database_list_stl_files(char ***file_list, size_t *count) {
    return sd_card_list_files(SD_DIR_PUNTALI, file_list, count);
}
