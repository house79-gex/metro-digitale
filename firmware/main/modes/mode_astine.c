#include "mode_astine.h"
#include "storage/storage_manager.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "MODE_ASTINE";

// Colori gruppi
#define COLOR_ANTA_RIBALTA    0x9D4EDD  // Viola
#define COLOR_PERSIANA        0x00AAFF  // Blu
#define COLOR_CREMONESE       0x00FF88  // Verde
#define COLOR_PERSONALIZZATO  0xFFAA00  // Giallo

// Profili predefiniti (10 profili)
astina_profile_t g_astine_profiles[10] = {
    // Gruppo Anta Ribalta (viola)
    {0, "Inferiore AR", GRUPPO_ANTA_RIBALTA, -15.0f, true, COLOR_ANTA_RIBALTA},
    {1, "Superiore AR", GRUPPO_ANTA_RIBALTA, -18.0f, true, COLOR_ANTA_RIBALTA},
    {2, "Laterale AR", GRUPPO_ANTA_RIBALTA, -12.0f, true, COLOR_ANTA_RIBALTA},
    {3, "Cremonese AR", GRUPPO_ANTA_RIBALTA, -25.0f, true, COLOR_ANTA_RIBALTA},
    
    // Gruppo Persiana (blu)
    {4, "Inferiore Persiana", GRUPPO_PERSIANA, -10.0f, true, COLOR_PERSIANA},
    {5, "Superiore Persiana", GRUPPO_PERSIANA, -10.0f, true, COLOR_PERSIANA},
    
    // Gruppo Cremonese (verde)
    {6, "Cremonese Std", GRUPPO_CREMONESE, -22.0f, true, COLOR_CREMONESE},
    {7, "Cremonese Corta", GRUPPO_CREMONESE, -16.0f, true, COLOR_CREMONESE},
    
    // Gruppo Personalizzato (giallo) - disattivi di default
    {8, "Custom 1", GRUPPO_PERSONALIZZATO, 0.0f, false, COLOR_PERSONALIZZATO},
    {9, "Custom 2", GRUPPO_PERSONALIZZATO, 0.0f, false, COLOR_PERSONALIZZATO}
};

void mode_astine_init(mode_astine_state_t *state) {
    if (!state) return;
    
    memset(state, 0, sizeof(mode_astine_state_t));
    state->selected_profile_id = 0; // Default: primo profilo
    
    ESP_LOGI(TAG, "Modalità astine inizializzata con %d profili", 10);
}

void mode_astine_select_profile(mode_astine_state_t *state, uint8_t profile_id) {
    if (!state || profile_id >= 10) return;
    
    state->selected_profile_id = profile_id;
    state->current_measure.profile = &g_astine_profiles[profile_id];
    
    ESP_LOGI(TAG, "Profilo selezionato: %s (offset: %.1fmm)",
             g_astine_profiles[profile_id].nome,
             g_astine_profiles[profile_id].offset_mm);
}

void mode_astine_measure(mode_astine_state_t *state, float encoder_mm) {
    if (!state || !state->current_measure.profile) return;
    
    state->current_measure.lunghezza_grezza_mm = encoder_mm;
    
    // Calcola lunghezza taglio con offset
    state->current_measure.lunghezza_taglio_mm = 
        encoder_mm + state->current_measure.profile->offset_mm;
    
    ESP_LOGI(TAG, "Astina misurata: grezza=%.1fmm → taglio=%.1fmm (offset=%.1fmm)",
             encoder_mm,
             state->current_measure.lunghezza_taglio_mm,
             state->current_measure.profile->offset_mm);
}

bool mode_astine_save_to_session(mode_astine_state_t *state) {
    if (!state || !state->current_measure.profile) {
        ESP_LOGE(TAG, "Misura incompleta, impossibile salvare");
        return false;
    }
    
    // Crea record per storage
    measurement_record_t record = storage_create_record(
        MEASURE_MODE_ASTINE,
        state->current_measure.lunghezza_taglio_mm,
        0.0f,  // No second value per astine
        NULL,  // No material per astine
        state->current_measure.profile->nome,
        state->current_measure.note
    );
    
    // Salva su SD card
    bool saved = storage_save_measurement(&record, STORAGE_TARGET_SD_CARD);
    
    if (saved) {
        state->measurement_saved = true;
        ESP_LOGI(TAG, "Misura astina salvata: %s = %.1fmm",
                 state->current_measure.profile->nome,
                 state->current_measure.lunghezza_taglio_mm);
    }
    
    return saved;
}

bool mode_astine_send_bluetooth(const mode_astine_state_t *state) {
    if (!state) return false;
    
    // TODO: Implementare invio BLE
    ESP_LOGW(TAG, "Invio Bluetooth non ancora implementato");
    return false;
}

uint8_t mode_astine_get_profiles(astina_gruppo_t gruppo,
                                astina_profile_t **profiles,
                                uint8_t max_profiles) {
    if (!profiles) return 0;
    
    uint8_t count = 0;
    for (uint8_t i = 0; i < 10 && count < max_profiles; i++) {
        if (g_astine_profiles[i].gruppo == gruppo && 
            g_astine_profiles[i].attivo) {
            profiles[count++] = &g_astine_profiles[i];
        }
    }
    
    return count;
}

astina_profile_t* mode_astine_get_profile_by_id(uint8_t profile_id) {
    if (profile_id >= 10) return NULL;
    
    return &g_astine_profiles[profile_id];
}

bool mode_astine_set_profile_offset(uint8_t profile_id, float offset_mm) {
    if (profile_id >= 10) return false;
    
    g_astine_profiles[profile_id].offset_mm = offset_mm;
    
    ESP_LOGI(TAG, "Offset profilo %s aggiornato a %.1fmm",
             g_astine_profiles[profile_id].nome,
             offset_mm);
    
    return true;
}

bool mode_astine_set_profile_active(uint8_t profile_id, bool attivo) {
    if (profile_id >= 10) return false;
    
    g_astine_profiles[profile_id].attivo = attivo;
    
    ESP_LOGI(TAG, "Profilo %s %s",
             g_astine_profiles[profile_id].nome,
             attivo ? "attivato" : "disattivato");
    
    return true;
}

void mode_astine_reset(mode_astine_state_t *state) {
    if (!state) return;
    
    memset(&state->current_measure, 0, sizeof(astina_measurement_t));
    state->measurement_saved = false;
    
    ESP_LOGI(TAG, "Misura astina resettata");
}

const char* mode_astine_get_gruppo_name(astina_gruppo_t gruppo) {
    switch (gruppo) {
        case GRUPPO_ANTA_RIBALTA:
            return "Anta Ribalta";
        case GRUPPO_PERSIANA:
            return "Persiana";
        case GRUPPO_CREMONESE:
            return "Cremonese";
        case GRUPPO_PERSONALIZZATO:
            return "Personalizzato";
        default:
            return "Sconosciuto";
    }
}

uint32_t mode_astine_get_gruppo_color(astina_gruppo_t gruppo) {
    switch (gruppo) {
        case GRUPPO_ANTA_RIBALTA:
            return COLOR_ANTA_RIBALTA;
        case GRUPPO_PERSIANA:
            return COLOR_PERSIANA;
        case GRUPPO_CREMONESE:
            return COLOR_CREMONESE;
        case GRUPPO_PERSONALIZZATO:
            return COLOR_PERSONALIZZATO;
        default:
            return 0xFFFFFF;
    }
}
