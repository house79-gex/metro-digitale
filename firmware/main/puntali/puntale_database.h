#ifndef PUNTALE_DATABASE_H
#define PUNTALE_DATABASE_H

#include "puntale_types.h"
#include "esp_err.h"

// Initialize tip database (load from NVS)
esp_err_t puntale_database_init(void);

// Scan SD card for STL files and create/update tip database
esp_err_t puntale_database_scan_sd_card(void);

// Get tip count
size_t puntale_database_get_count(void);

// Get tip by index
Puntale* puntale_database_get_by_index(size_t index);

// Get tip by ID
Puntale* puntale_database_get_by_id(const char *id);

// Add or update tip
esp_err_t puntale_database_add_or_update(const Puntale *tip);

// Delete tip
esp_err_t puntale_database_delete(const char *id);

// Save tip configuration to NVS
esp_err_t puntale_database_save_to_nvs(const Puntale *tip);

// Load tip configuration from NVS
esp_err_t puntale_database_load_from_nvs(const char *id, Puntale *tip);

// Load STL model for tip (lazy loading)
esp_err_t puntale_database_load_stl(Puntale *tip);

// Unload STL model from memory
void puntale_database_unload_stl(Puntale *tip);

// Backup database to SD card (JSON format)
esp_err_t puntale_database_backup_to_sd(void);

// Restore database from SD card
esp_err_t puntale_database_restore_from_sd(void);

// Get list of available STL files on SD card
esp_err_t puntale_database_list_stl_files(char ***file_list, size_t *count);

#endif // PUNTALE_DATABASE_H
