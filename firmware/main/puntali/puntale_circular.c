#include "puntale_circular.h"
#include <string.h>
#include <time.h>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

static const char *TAG = "PUNTALE_CIRCULAR";

// Diametro default puntali circolari
#define DEFAULT_PUNTALE_DIAMETER_MM 30.0f

void puntale_init_defaults(puntale_pair_t *pair) {
    if (!pair) return;
    
    // Puntale fisso sinistro
    pair->fisso_sx.diametro_mm = DEFAULT_PUNTALE_DIAMETER_MM;
    pair->fisso_sx.offset_usura_mm = 0.0f;
    pair->fisso_sx.contatore_utilizzi = 0;
    strncpy(pair->fisso_sx.nome, "Fisso SX", sizeof(pair->fisso_sx.nome) - 1);
    pair->fisso_sx.attivo = true;
    
    // Puntale mobile destro
    pair->mobile_dx.diametro_mm = DEFAULT_PUNTALE_DIAMETER_MM;
    pair->mobile_dx.offset_usura_mm = 0.0f;
    pair->mobile_dx.contatore_utilizzi = 0;
    strncpy(pair->mobile_dx.nome, "Mobile DX", sizeof(pair->mobile_dx.nome) - 1);
    pair->mobile_dx.attivo = true;
    
    // Stato calibrazione
    pair->distanza_zero_mm = 0.0f;
    pair->calibrato = false;
    pair->timestamp_calibrazione = 0;
    
    ESP_LOGI(TAG, "Puntali inizializzati con diametro %.1fmm", DEFAULT_PUNTALE_DIAMETER_MM);
}

float puntale_calculate_external_distance(const puntale_pair_t *pair, float encoder_distance_mm) {
    if (!pair) return encoder_distance_mm;
    
    // Per misure esterne, la distanza è quella dell'encoder meno lo zero di calibrazione
    float distance = encoder_distance_mm - pair->distanza_zero_mm;
    
    // Applica compensazione usura
    distance += pair->fisso_sx.offset_usura_mm + pair->mobile_dx.offset_usura_mm;
    
    return distance;
}

float puntale_calculate_internal_distance(const puntale_pair_t *pair, float encoder_distance_mm) {
    if (!pair) return encoder_distance_mm;
    
    // Per misure interne, aggiungiamo i diametri di entrambi i puntali
    float distance = encoder_distance_mm - pair->distanza_zero_mm;
    
    // Aggiungi i diametri
    distance += pair->fisso_sx.diametro_mm + pair->mobile_dx.diametro_mm;
    
    // Applica compensazione usura
    distance += pair->fisso_sx.offset_usura_mm + pair->mobile_dx.offset_usura_mm;
    
    return distance;
}

bool puntale_calibrate_zero(puntale_pair_t *pair, float encoder_reading_mm) {
    if (!pair) return false;
    
    // Salva la distanza zero
    pair->distanza_zero_mm = encoder_reading_mm;
    pair->calibrato = true;
    pair->timestamp_calibrazione = (uint32_t)time(NULL);
    
    ESP_LOGI(TAG, "Calibrazione zero completata: %.3fmm (timestamp: %lu)", 
             encoder_reading_mm, pair->timestamp_calibrazione);
    
    return true;
}

bool puntale_save_to_nvs(const puntale_pair_t *pair, const char *nvs_namespace) {
    if (!pair || !nvs_namespace) return false;
    
    nvs_handle_t handle;
    esp_err_t err;
    
    err = nvs_open(nvs_namespace, NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore apertura NVS: %s", esp_err_to_name(err));
        return false;
    }
    
    // Salva configurazione puntale fisso
    err = nvs_set_blob(handle, "fisso_sx", &pair->fisso_sx, sizeof(puntale_config_t));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore salvataggio fisso_sx: %s", esp_err_to_name(err));
        nvs_close(handle);
        return false;
    }
    
    // Salva configurazione puntale mobile
    err = nvs_set_blob(handle, "mobile_dx", &pair->mobile_dx, sizeof(puntale_config_t));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore salvataggio mobile_dx: %s", esp_err_to_name(err));
        nvs_close(handle);
        return false;
    }
    
    // Salva stato calibrazione
    err = nvs_set_u8(handle, "calibrato", pair->calibrato ? 1 : 0);
    err |= nvs_set_blob(handle, "dist_zero", &pair->distanza_zero_mm, sizeof(float));
    err |= nvs_set_u32(handle, "ts_calib", pair->timestamp_calibrazione);
    
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore salvataggio calibrazione: %s", esp_err_to_name(err));
        nvs_close(handle);
        return false;
    }
    
    // Commit modifiche
    err = nvs_commit(handle);
    nvs_close(handle);
    
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore commit NVS: %s", esp_err_to_name(err));
        return false;
    }
    
    ESP_LOGI(TAG, "Configurazione puntali salvata su NVS");
    return true;
}

bool puntale_load_from_nvs(puntale_pair_t *pair, const char *nvs_namespace) {
    if (!pair || !nvs_namespace) return false;
    
    nvs_handle_t handle;
    esp_err_t err;
    
    err = nvs_open(nvs_namespace, NVS_READONLY, &handle);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Impossibile aprire NVS (forse prima volta): %s", esp_err_to_name(err));
        return false;
    }
    
    // Carica configurazione puntale fisso
    size_t size = sizeof(puntale_config_t);
    err = nvs_get_blob(handle, "fisso_sx", &pair->fisso_sx, &size);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Impossibile caricare fisso_sx: %s", esp_err_to_name(err));
        nvs_close(handle);
        return false;
    }
    
    // Carica configurazione puntale mobile
    size = sizeof(puntale_config_t);
    err = nvs_get_blob(handle, "mobile_dx", &pair->mobile_dx, &size);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Impossibile caricare mobile_dx: %s", esp_err_to_name(err));
        nvs_close(handle);
        return false;
    }
    
    // Carica stato calibrazione
    uint8_t calibrato_u8;
    err = nvs_get_u8(handle, "calibrato", &calibrato_u8);
    if (err == ESP_OK) {
        pair->calibrato = (calibrato_u8 != 0);
    }
    
    size = sizeof(float);
    nvs_get_blob(handle, "dist_zero", &pair->distanza_zero_mm, &size);
    nvs_get_u32(handle, "ts_calib", &pair->timestamp_calibrazione);
    
    nvs_close(handle);
    
    ESP_LOGI(TAG, "Configurazione puntali caricata da NVS (calibrato: %s)", 
             pair->calibrato ? "SI" : "NO");
    
    return true;
}

void puntale_increment_usage(puntale_pair_t *pair) {
    if (!pair) return;
    
    pair->fisso_sx.contatore_utilizzi++;
    pair->mobile_dx.contatore_utilizzi++;
}

bool puntale_is_calibrated(const puntale_pair_t *pair) {
    return pair ? pair->calibrato : false;
}

void puntale_reset_calibration(puntale_pair_t *pair) {
    if (!pair) return;
    
    pair->calibrato = false;
    pair->distanza_zero_mm = 0.0f;
    pair->timestamp_calibrazione = 0;
    
    ESP_LOGI(TAG, "Calibrazione resettata");
}

void puntale_set_fisso_wear_offset(puntale_pair_t *pair, float offset_mm) {
    if (!pair) return;
    
    pair->fisso_sx.offset_usura_mm = offset_mm;
    ESP_LOGI(TAG, "Offset usura fisso SX impostato a %.3fmm", offset_mm);
}

void puntale_set_mobile_wear_offset(puntale_pair_t *pair, float offset_mm) {
    if (!pair) return;
    
    pair->mobile_dx.offset_usura_mm = offset_mm;
    ESP_LOGI(TAG, "Offset usura mobile DX impostato a %.3fmm", offset_mm);
}
