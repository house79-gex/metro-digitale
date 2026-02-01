#include "storage_manager.h"
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "esp_crc.h"
#include "nvs_flash.h"
#include "nvs.h"
#include <sys/stat.h>
#include <string.h>
#include <stdio.h>
#include <dirent.h>

static const char *TAG = "STORAGE_MGR";

// Path directory SD card
#define SD_MOUNT_POINT      "/sd"
#define SD_SESSIONS_DIR     "/sd/sessions"
#define SD_EXPORTS_DIR      "/sd/exports"
#define SD_BACKUP_DIR       "/sd/backup"

// Stato storage
static struct {
    bool sd_mounted;
    bool usb_mounted;
    bool initialized;
} g_storage_state = {0};

// Helper: crea directory se non esiste
static bool ensure_directory_exists(const char *path) {
    struct stat st;
    if (stat(path, &st) == -1) {
        if (mkdir(path, 0775) == 0) {
            ESP_LOGI(TAG, "Directory creata: %s", path);
            return true;
        } else {
            ESP_LOGE(TAG, "Errore creazione directory %s", path);
            return false;
        }
    }
    return true; // Già esiste
}

// Helper: ottieni path file sessione giornaliero
static void get_daily_session_file(char *buffer, size_t buffer_size) {
    time_t now = time(NULL);
    struct tm timeinfo;
    localtime_r(&now, &timeinfo);
    snprintf(buffer, buffer_size, "%s/%04d%02d%02d.jsonl",
             SD_SESSIONS_DIR,
             timeinfo.tm_year + 1900,
             timeinfo.tm_mon + 1,
             timeinfo.tm_mday);
}

bool storage_manager_init(void) {
    ESP_LOGI(TAG, "Inizializzazione storage manager...");
    
    // Inizializza NVS
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "NVS cancellato e re-inizializzato");
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore init NVS: %s", esp_err_to_name(err));
        return false;
    }
    
    // Nota: Mount SD card è gestito dal modulo sd_card.c esistente
    // Verifichiamo solo se è montata
    struct stat st;
    g_storage_state.sd_mounted = (stat(SD_MOUNT_POINT, &st) == 0);
    
    if (g_storage_state.sd_mounted) {
        ESP_LOGI(TAG, "SD card rilevata");
        
        // Crea directory necessarie
        ensure_directory_exists(SD_SESSIONS_DIR);
        ensure_directory_exists(SD_EXPORTS_DIR);
        ensure_directory_exists(SD_BACKUP_DIR);
    } else {
        ESP_LOGW(TAG, "SD card non montata");
    }
    
    g_storage_state.initialized = true;
    ESP_LOGI(TAG, "Storage manager inizializzato");
    
    return true;
}

bool storage_is_available(storage_target_t target) {
    switch (target) {
        case STORAGE_TARGET_SD_CARD:
            return g_storage_state.sd_mounted;
        
        case STORAGE_TARGET_USB_OTG:
            return g_storage_state.usb_mounted;
        
        case STORAGE_TARGET_BLUETOOTH:
            // Verifica connessione BLE (stub per ora)
            return true; // TODO: check BLE connection
        
        case STORAGE_TARGET_INTERNAL_NVS:
            return true; // NVS sempre disponibile
        
        default:
            return false;
    }
}

bool storage_get_info(storage_target_t target, storage_info_t *info) {
    if (!info) return false;
    
    memset(info, 0, sizeof(storage_info_t));
    info->available = storage_is_available(target);
    
    // TODO: implementare calcolo spazio per ogni target
    // Per ora ritorniamo valori di base
    
    return info->available;
}

uint32_t storage_calculate_crc32(const measurement_record_t *record) {
    if (!record) return 0;
    
    // Calcola CRC su tutti i campi eccetto il CRC stesso
    uint32_t crc = 0;
    crc = esp_crc32_le(crc, (uint8_t*)&record->timestamp, sizeof(record->timestamp));
    crc = esp_crc32_le(crc, (uint8_t*)&record->mode, sizeof(record->mode));
    crc = esp_crc32_le(crc, (uint8_t*)&record->value_mm, sizeof(record->value_mm));
    crc = esp_crc32_le(crc, (uint8_t*)&record->value2_mm, sizeof(record->value2_mm));
    crc = esp_crc32_le(crc, (uint8_t*)record->material, strlen(record->material));
    crc = esp_crc32_le(crc, (uint8_t*)record->profile, strlen(record->profile));
    crc = esp_crc32_le(crc, (uint8_t*)record->notes, strlen(record->notes));
    
    return crc;
}

bool storage_verify_record(const measurement_record_t *record) {
    if (!record) return false;
    
    uint32_t calculated_crc = storage_calculate_crc32(record);
    return (calculated_crc == record->crc32);
}

measurement_record_t storage_create_record(measure_mode_t mode,
                                          float value_mm,
                                          float value2_mm,
                                          const char *material,
                                          const char *profile,
                                          const char *notes) {
    measurement_record_t record = {0};
    
    record.timestamp = (uint32_t)time(NULL);
    record.mode = mode;
    record.value_mm = value_mm;
    record.value2_mm = value2_mm;
    
    if (material) {
        strncpy(record.material, material, sizeof(record.material) - 1);
    }
    
    if (profile) {
        strncpy(record.profile, profile, sizeof(record.profile) - 1);
    }
    
    if (notes) {
        strncpy(record.notes, notes, sizeof(record.notes) - 1);
    }
    
    // Calcola CRC32
    record.crc32 = storage_calculate_crc32(&record);
    
    return record;
}

bool storage_save_measurement(const measurement_record_t *record, storage_target_t target) {
    if (!record) return false;
    
    if (target == STORAGE_TARGET_SD_CARD) {
        if (!g_storage_state.sd_mounted) {
            ESP_LOGE(TAG, "SD card non disponibile");
            return false;
        }
        
        // Ottieni path file giornaliero
        char filepath[128];
        get_daily_session_file(filepath, sizeof(filepath));
        
        // Apri file in append mode
        FILE *f = fopen(filepath, "a");
        if (!f) {
            ESP_LOGE(TAG, "Errore apertura file %s", filepath);
            return false;
        }
        
        // Scrivi record in formato JSONL (una riga JSON per record)
        const char *mode_str[] = {"calibro", "vetri", "astine", "fermavetri"};
        fprintf(f, "{\"timestamp\":%lu,\"mode\":\"%s\",\"value\":%.3f,\"value2\":%.3f,"
                   "\"material\":\"%s\",\"profile\":\"%s\",\"notes\":\"%s\",\"crc32\":%lu}\n",
                record->timestamp,
                mode_str[record->mode],
                record->value_mm,
                record->value2_mm,
                record->material,
                record->profile,
                record->notes,
                record->crc32);
        
        fclose(f);
        
        ESP_LOGI(TAG, "Misura salvata su %s", filepath);
        return true;
    }
    
    // Altri target TODO
    return false;
}

bool storage_export_csv(const measurement_session_t *session, const char *filename) {
    if (!session || !filename) return false;
    
    if (!g_storage_state.sd_mounted) {
        ESP_LOGE(TAG, "SD card non disponibile");
        return false;
    }
    
    char filepath[128];
    snprintf(filepath, sizeof(filepath), "%s/%s", SD_EXPORTS_DIR, filename);
    
    FILE *f = fopen(filepath, "w");
    if (!f) {
        ESP_LOGE(TAG, "Errore creazione file CSV %s", filepath);
        return false;
    }
    
    // Scrivi header CSV
    fprintf(f, "Timestamp,Mode,Value(mm),Value2(mm),Material,Profile,Notes\n");
    
    // Scrivi records
    const char *mode_str[] = {"Calibro", "Vetri", "Astine", "Fermavetri"};
    for (uint16_t i = 0; i < session->count; i++) {
        const measurement_record_t *r = &session->records[i];
        
        // Formatta timestamp
        struct tm timeinfo;
        time_t ts = r->timestamp;
        localtime_r(&ts, &timeinfo);
        char time_str[32];
        strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", &timeinfo);
        
        fprintf(f, "%s,%s,%.3f,%.3f,%s,%s,%s\n",
                time_str,
                mode_str[r->mode],
                r->value_mm,
                r->value2_mm,
                r->material,
                r->profile,
                r->notes);
    }
    
    fclose(f);
    
    ESP_LOGI(TAG, "Export CSV completato: %s (%d records)", filepath, session->count);
    return true;
}

bool storage_export_to_file(const measurement_session_t *session,
                            export_format_t format,
                            const char *filename,
                            storage_target_t target) {
    if (!session || !filename) return false;
    
    switch (format) {
        case EXPORT_FORMAT_CSV:
            return storage_export_csv(session, filename);
        
        case EXPORT_FORMAT_JSON:
            // TODO: implementare export JSON completo
            ESP_LOGW(TAG, "Export JSON non ancora implementato");
            return false;
        
        case EXPORT_FORMAT_BINARY:
            // TODO: implementare export binario
            ESP_LOGW(TAG, "Export binario non ancora implementato");
            return false;
        
        default:
            return false;
    }
}

bool storage_send_via_bluetooth(const measurement_session_t *session,
                                const char *device_address) {
    // TODO: implementare invio BLE chunked
    ESP_LOGW(TAG, "Invio Bluetooth non ancora implementato");
    return false;
}

uint32_t storage_list_files(const char *directory, char **files, uint32_t max_files) {
    if (!directory || !files) return 0;
    
    DIR *dir = opendir(directory);
    if (!dir) {
        ESP_LOGE(TAG, "Errore apertura directory %s", directory);
        return 0;
    }
    
    uint32_t count = 0;
    struct dirent *entry;
    
    while ((entry = readdir(dir)) != NULL && count < max_files) {
        if (entry->d_type == DT_REG) { // Solo file regolari
            if (files[count]) {
                strncpy(files[count], entry->d_name, 255);
                count++;
            }
        }
    }
    
    closedir(dir);
    
    ESP_LOGI(TAG, "Trovati %lu file in %s", count, directory);
    return count;
}

bool storage_usb_mount(void) {
    // TODO: implementare mount USB OTG
    ESP_LOGW(TAG, "Mount USB OTG non ancora implementato");
    g_storage_state.usb_mounted = false;
    return false;
}

bool storage_usb_unmount(void) {
    // TODO: implementare unmount USB OTG
    ESP_LOGW(TAG, "Unmount USB OTG non ancora implementato");
    g_storage_state.usb_mounted = false;
    return false;
}

void storage_manager_deinit(void) {
    // Cleanup
    g_storage_state.initialized = false;
    g_storage_state.sd_mounted = false;
    g_storage_state.usb_mounted = false;
    
    ESP_LOGI(TAG, "Storage manager deinizializzato");
}
