#include "sd_card.h"
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "driver/sdspi_host.h"
#include "driver/spi_common.h"
#include "sdmmc_cmd.h"
#include <sys/stat.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>

static const char *TAG = "SD_CARD";
static sdmmc_card_t *card = NULL;
static bool is_mounted = false;

esp_err_t sd_card_init(void) {
    ESP_LOGI(TAG, "Initializing SD card");
    
    esp_err_t ret;
    
    // Options for mounting the filesystem
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };
    
    // Initialize SD card using SPI mode
    sdmmc_host_t host = SDSPI_HOST_DEFAULT();
    
    spi_bus_config_t bus_cfg = {
        .mosi_io_num = SD_PIN_MOSI,
        .miso_io_num = SD_PIN_MISO,
        .sclk_io_num = SD_PIN_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4000,
    };
    
    ret = spi_bus_initialize(host.slot, &bus_cfg, SDSPI_DEFAULT_DMA);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize SPI bus: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Attach the SD card to the SPI bus
    sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot_config.gpio_cs = SD_PIN_CS;
    slot_config.host_id = host.slot;
    
    ret = esp_vfs_fat_sdspi_mount(SD_MOUNT_POINT, &host, &slot_config, &mount_config, &card);
    
    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Failed to mount filesystem. "
                     "If you want the card to be formatted, set format_if_mount_failed = true.");
        } else {
            ESP_LOGE(TAG, "Failed to initialize SD card: %s", esp_err_to_name(ret));
        }
        return ret;
    }
    
    is_mounted = true;
    
    // Print card info
    sdmmc_card_print_info(stdout, card);
    
    // Create standard directories
    sd_card_create_directories();
    
    ESP_LOGI(TAG, "SD card mounted successfully at %s", SD_MOUNT_POINT);
    return ESP_OK;
}

void sd_card_deinit(void) {
    if (is_mounted) {
        esp_vfs_fat_sdcard_unmount(SD_MOUNT_POINT, card);
        is_mounted = false;
        ESP_LOGI(TAG, "SD card unmounted");
    }
}

bool sd_card_is_mounted(void) {
    return is_mounted;
}

esp_err_t sd_card_create_directories(void) {
    const char *dirs[] = {
        SD_DIR_PUNTALI,
        SD_DIR_CONFIG,
        SD_DIR_CACHE,
        SD_DIR_THUMBNAILS
    };
    
    for (int i = 0; i < sizeof(dirs) / sizeof(dirs[0]); i++) {
        struct stat st;
        if (stat(dirs[i], &st) == -1) {
            ESP_LOGI(TAG, "Creating directory: %s", dirs[i]);
            if (mkdir(dirs[i], 0755) != 0) {
                ESP_LOGW(TAG, "Failed to create directory: %s", dirs[i]);
            }
        }
    }
    
    return ESP_OK;
}

bool sd_card_file_exists(const char *path) {
    struct stat st;
    return (stat(path, &st) == 0);
}

esp_err_t sd_card_read_file(const char *path, uint8_t **data, size_t *size) {
    FILE *f = fopen(path, "rb");
    if (f == NULL) {
        ESP_LOGE(TAG, "Failed to open file for reading: %s", path);
        return ESP_FAIL;
    }
    
    // Get file size
    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    if (file_size <= 0) {
        fclose(f);
        return ESP_FAIL;
    }
    
    // Allocate buffer
    *data = (uint8_t*)malloc(file_size);
    if (*data == NULL) {
        ESP_LOGE(TAG, "Failed to allocate memory for file");
        fclose(f);
        return ESP_ERR_NO_MEM;
    }
    
    // Read file
    size_t read_size = fread(*data, 1, file_size, f);
    fclose(f);
    
    if (read_size != file_size) {
        ESP_LOGE(TAG, "Failed to read complete file");
        free(*data);
        *data = NULL;
        return ESP_FAIL;
    }
    
    *size = file_size;
    return ESP_OK;
}

esp_err_t sd_card_write_file(const char *path, const uint8_t *data, size_t size) {
    FILE *f = fopen(path, "wb");
    if (f == NULL) {
        ESP_LOGE(TAG, "Failed to open file for writing: %s", path);
        return ESP_FAIL;
    }
    
    size_t written = fwrite(data, 1, size, f);
    fclose(f);
    
    if (written != size) {
        ESP_LOGE(TAG, "Failed to write complete file");
        return ESP_FAIL;
    }
    
    return ESP_OK;
}

esp_err_t sd_card_delete_file(const char *path) {
    if (remove(path) != 0) {
        ESP_LOGE(TAG, "Failed to delete file: %s", path);
        return ESP_FAIL;
    }
    return ESP_OK;
}

esp_err_t sd_card_list_files(const char *dir_path, char ***file_list, size_t *count) {
    DIR *dir = opendir(dir_path);
    if (dir == NULL) {
        ESP_LOGE(TAG, "Failed to open directory: %s", dir_path);
        return ESP_FAIL;
    }
    
    // Count files first
    *count = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            (*count)++;
        }
    }
    
    if (*count == 0) {
        closedir(dir);
        *file_list = NULL;
        return ESP_OK;
    }
    
    // Allocate array
    *file_list = (char**)malloc(*count * sizeof(char*));
    if (*file_list == NULL) {
        closedir(dir);
        return ESP_ERR_NO_MEM;
    }
    
    // Read filenames
    rewinddir(dir);
    size_t idx = 0;
    while ((entry = readdir(dir)) != NULL && idx < *count) {
        if (entry->d_type == DT_REG) {
            (*file_list)[idx] = strdup(entry->d_name);
            idx++;
        }
    }
    
    closedir(dir);
    return ESP_OK;
}

void sd_card_free_file_list(char **file_list, size_t count) {
    if (file_list != NULL) {
        for (size_t i = 0; i < count; i++) {
            if (file_list[i] != NULL) {
                free(file_list[i]);
            }
        }
        free(file_list);
    }
}
