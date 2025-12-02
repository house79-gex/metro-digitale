#include "config.h"
#include <string.h>
#include <stdio.h>
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"

static const char *TAG = "CONFIG";

// Variabili globali
GlobalConfig g_config;
RuntimeState g_state;

// Inizializza la configurazione con valori di default
void config_init_defaults(GlobalConfig *cfg) {
    memset(cfg, 0, sizeof(GlobalConfig));
    
    // Generali
    cfg->modalita_corrente = MODE_FERMAVETRO;
    cfg->auto_zero_enabled = true;
    cfg->tolleranza_raggruppamento_mm = 2.0f;
    
    // Encoder
    cfg->encoder_resolution_mm = 0.005f;
    cfg->encoder_pulses_per_mm = 200;
    
    // Puntali default
    cfg->num_puntali = 3;
    config_add_puntale(cfg, "Standard", 50.0f, 50.0f, 100.0f);
    config_add_puntale(cfg, "Lungo", 80.0f, 80.0f, 160.0f);
    config_add_puntale(cfg, "Custom", 0.0f, 0.0f, 0.0f);
    cfg->puntale_corrente_idx = 0;
    
    // Materiali default
    cfg->num_materiali = 3;
    config_add_materiale(cfg, "Alluminio", 12.0f);
    config_add_materiale(cfg, "Legno", 6.0f);
    config_add_materiale(cfg, "PVC", 10.0f);
    cfg->materiale_corrente_idx = 0;
    
    // Gruppi astine default
    cfg->num_gruppi_astine = 4;
    config_add_gruppo_astine(cfg, "Anta Ribalta", 155, 89, 182);   // #9b59b6 viola
    config_add_gruppo_astine(cfg, "Persiana", 52, 152, 219);       // #3498db blu
    config_add_gruppo_astine(cfg, "Cremonese Normale", 46, 204, 113); // #2ecc71 verde
    config_add_gruppo_astine(cfg, "Personalizzati", 241, 196, 15); // #f1c40f giallo
    
    // Astine default
    cfg->num_astine = 0;
    // Gruppo 0: Anta Ribalta
    config_add_astina(cfg, "Inferiore AR", -65.0f, 0);
    config_add_astina(cfg, "Superiore AR", -65.0f, 0);
    config_add_astina(cfg, "Laterale AR", -45.0f, 0);
    config_add_astina(cfg, "Cremonese AR", -30.0f, 0);
    // Gruppo 1: Persiana
    config_add_astina(cfg, "Inferiore Persiana", -55.0f, 1);
    config_add_astina(cfg, "Superiore Persiana", -55.0f, 1);
    // Gruppo 2: Cremonese Normale
    config_add_astina(cfg, "Cremonese Std", -25.0f, 2);
    config_add_astina(cfg, "Cremonese Corta", -20.0f, 2);
    // Gruppo 3: Personalizzati
    config_add_astina(cfg, "Custom 1", -40.0f, 3);
    
    cfg->astina_corrente_idx = 0;
    
    // Bluetooth
    cfg->bluetooth_enabled = true;
    strncpy(cfg->bt_device_name, "Metro-Digitale", sizeof(cfg->bt_device_name) - 1);
    cfg->auto_send_troncatrice = true;
    
    // Display
    cfg->brightness = 80;
    cfg->sleep_enabled = true;
    cfg->sleep_timeout_sec = 300; // 5 minuti
    
    ESP_LOGI(TAG, "Configurazione inizializzata con valori di default");
}

// Carica configurazione da NVS
void config_load_from_nvs(GlobalConfig *cfg) {
    nvs_handle_t nvs_handle;
    esp_err_t err;
    
    err = nvs_open("metro_cfg", NVS_READONLY, &nvs_handle);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Impossibile aprire NVS per lettura, uso default");
        config_init_defaults(cfg);
        return;
    }
    
    size_t required_size = sizeof(GlobalConfig);
    err = nvs_get_blob(nvs_handle, "config", cfg, &required_size);
    
    if (err != ESP_OK || required_size != sizeof(GlobalConfig)) {
        ESP_LOGW(TAG, "Configurazione NVS non valida, uso default");
        config_init_defaults(cfg);
    } else {
        ESP_LOGI(TAG, "Configurazione caricata da NVS");
    }
    
    nvs_close(nvs_handle);
}

// Salva configurazione in NVS
void config_save_to_nvs(const GlobalConfig *cfg) {
    nvs_handle_t nvs_handle;
    esp_err_t err;
    
    err = nvs_open("metro_cfg", NVS_READWRITE, &nvs_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore apertura NVS per scrittura: %s", esp_err_to_name(err));
        return;
    }
    
    err = nvs_set_blob(nvs_handle, "config", cfg, sizeof(GlobalConfig));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore scrittura configurazione: %s", esp_err_to_name(err));
    }
    
    err = nvs_commit(nvs_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore commit NVS: %s", esp_err_to_name(err));
    } else {
        ESP_LOGI(TAG, "Configurazione salvata in NVS");
    }
    
    nvs_close(nvs_handle);
}

// Gestione puntali
void config_add_puntale(GlobalConfig *cfg, const char *nome, float offset_fisso, 
                        float offset_mobile, float dist_min) {
    if (cfg->num_puntali >= MAX_PUNTALI) {
        ESP_LOGW(TAG, "Raggiunto limite massimo puntali");
        return;
    }
    
    PuntaleConfig *p = &cfg->puntali[cfg->num_puntali];
    strncpy(p->nome, nome, sizeof(p->nome) - 1);
    p->offset_fisso_mm = offset_fisso;
    p->offset_mobile_mm = offset_mobile;
    p->distanza_minima_mm = dist_min;
    p->attivo = true;
    
    cfg->num_puntali++;
}

void config_set_puntale_corrente(GlobalConfig *cfg, uint8_t idx) {
    if (idx < cfg->num_puntali) {
        cfg->puntale_corrente_idx = idx;
        ESP_LOGI(TAG, "Puntale corrente: %s", cfg->puntali[idx].nome);
    }
}

// Gestione materiali
void config_add_materiale(GlobalConfig *cfg, const char *nome, float gioco) {
    if (cfg->num_materiali >= MAX_MATERIALI) {
        ESP_LOGW(TAG, "Raggiunto limite massimo materiali");
        return;
    }
    
    MaterialeConfig *m = &cfg->materiali[cfg->num_materiali];
    strncpy(m->nome, nome, sizeof(m->nome) - 1);
    m->gioco_vetro_mm = gioco;
    m->attivo = true;
    
    cfg->num_materiali++;
}

void config_set_materiale_corrente(GlobalConfig *cfg, uint8_t idx) {
    if (idx < cfg->num_materiali) {
        cfg->materiale_corrente_idx = idx;
        ESP_LOGI(TAG, "Materiale corrente: %s", cfg->materiali[idx].nome);
    }
}

// Gestione gruppi astine
void config_add_gruppo_astine(GlobalConfig *cfg, const char *nome, 
                               uint8_t r, uint8_t g, uint8_t b) {
    if (cfg->num_gruppi_astine >= MAX_GRUPPI_ASTINE) {
        ESP_LOGW(TAG, "Raggiunto limite massimo gruppi astine");
        return;
    }
    
    AstinaGruppo *gruppo = &cfg->gruppi_astine[cfg->num_gruppi_astine];
    strncpy(gruppo->nome, nome, sizeof(gruppo->nome) - 1);
    gruppo->colore_r = r;
    gruppo->colore_g = g;
    gruppo->colore_b = b;
    
    cfg->num_gruppi_astine++;
}

// Gestione astine
void config_add_astina(GlobalConfig *cfg, const char *nome, 
                       float offset, uint8_t gruppo_idx) {
    if (cfg->num_astine >= MAX_ASTINE) {
        ESP_LOGW(TAG, "Raggiunto limite massimo astine");
        return;
    }
    
    AstinaConfig *astina = &cfg->astine[cfg->num_astine];
    strncpy(astina->nome, nome, sizeof(astina->nome) - 1);
    astina->offset_mm = offset;
    astina->gruppo_idx = gruppo_idx;
    astina->attivo = true;
    
    cfg->num_astine++;
}

void config_set_astina_corrente(GlobalConfig *cfg, uint8_t idx) {
    if (idx < cfg->num_astine) {
        cfg->astina_corrente_idx = idx;
        ESP_LOGI(TAG, "Astina corrente: %s", cfg->astine[idx].nome);
    }
}

void config_remove_astina(GlobalConfig *cfg, uint8_t idx) {
    if (idx >= cfg->num_astine) {
        return;
    }
    
    // Sposta tutte le astine successive
    for (uint8_t i = idx; i < cfg->num_astine - 1; i++) {
        cfg->astine[i] = cfg->astine[i + 1];
    }
    
    cfg->num_astine--;
    
    // Aggiusta l'indice corrente se necessario
    if (cfg->astina_corrente_idx >= cfg->num_astine && cfg->num_astine > 0) {
        cfg->astina_corrente_idx = cfg->num_astine - 1;
    }
    
    ESP_LOGI(TAG, "Astina rimossa, totale: %d", cfg->num_astine);
}
