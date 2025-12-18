#ifndef SD_CARD_H
#define SD_CARD_H

#include "esp_err.h"
#include <stdbool.h>
#include <stddef.h>

// SD Card SPI pins
#define SD_PIN_MOSI     23
#define SD_PIN_MISO     19
#define SD_PIN_CLK      18
#define SD_PIN_CS       5

// Mount point
#define SD_MOUNT_POINT  "/sd"

// Standard directories
#define SD_DIR_PUNTALI      "/sd/puntali"
#define SD_DIR_CONFIG       "/sd/config"
#define SD_DIR_CACHE        "/sd/cache"
#define SD_DIR_THUMBNAILS   "/sd/cache/thumbnails"

// Initialize and mount SD card
esp_err_t sd_card_init(void);

// Unmount SD card
void sd_card_deinit(void);

// Check if SD card is mounted
bool sd_card_is_mounted(void);

// Create standard directory structure
esp_err_t sd_card_create_directories(void);

// File operations helpers
bool sd_card_file_exists(const char *path);
esp_err_t sd_card_read_file(const char *path, uint8_t **data, size_t *size);
esp_err_t sd_card_write_file(const char *path, const uint8_t *data, size_t size);
esp_err_t sd_card_delete_file(const char *path);

// Directory operations
esp_err_t sd_card_list_files(const char *dir_path, char ***file_list, size_t *count);
void sd_card_free_file_list(char **file_list, size_t count);

#endif // SD_CARD_H
