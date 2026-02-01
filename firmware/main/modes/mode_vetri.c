#include "mode_vetri.h"
#include "storage/storage_manager.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "MODE_VETRI";

// Materiali predefiniti
const material_config_t g_materials[4] = {
    {
        .nome = "Alluminio",
        .gioco_mm = 6.0f,        // 6mm per lato = -12mm totale
        .color_hex = 0xC0C0C0,   // Silver
        .attivo = true
    },
    {
        .nome = "Legno",
        .gioco_mm = 3.0f,        // 3mm per lato = -6mm totale
        .color_hex = 0x8B4513,   // Brown
        .attivo = true
    },
    {
        .nome = "PVC",
        .gioco_mm = 5.0f,        // 5mm per lato = -10mm totale
        .color_hex = 0xFFFFFF,   // White
        .attivo = true
    },
    {
        .nome = "Custom",
        .gioco_mm = 0.0f,
        .color_hex = 0xFFAA00,   // Orange
        .attivo = true
    }
};

void mode_vetri_init(mode_vetri_state_t *state) {
    if (!state) return;
    
    memset(state, 0, sizeof(mode_vetri_state_t));
    state->current_step = WIZARD_STEP_SELECT_MATERIAL;
    state->selected_material = MATERIAL_ALLUMINIO; // Default
    
    ESP_LOGI(TAG, "Modalità vetri inizializzata");
}

void mode_vetri_set_material(mode_vetri_state_t *state, material_type_t material) {
    if (!state) return;
    
    state->selected_material = material;
    state->current_measure.materiale = material;
    
    ESP_LOGI(TAG, "Materiale selezionato: %s", 
             g_materials[material].nome);
}

void mode_vetri_measure_larghezza(mode_vetri_state_t *state, float encoder_mm) {
    if (!state) return;
    
    state->current_measure.larghezza_raw_mm = encoder_mm;
    
    // Calcola larghezza netta con gioco
    float gioco_totale = mode_vetri_get_total_gioco(state->selected_material);
    state->current_measure.larghezza_netta_mm = encoder_mm - gioco_totale;
    
    state->larghezza_saved = true;
    
    ESP_LOGI(TAG, "Larghezza misurata: raw=%.1fmm, netta=%.1fmm (gioco=%.1fmm)",
             encoder_mm,
             state->current_measure.larghezza_netta_mm,
             gioco_totale);
}

void mode_vetri_measure_altezza(mode_vetri_state_t *state, float encoder_mm) {
    if (!state) return;
    
    state->current_measure.altezza_raw_mm = encoder_mm;
    
    // Calcola altezza netta con gioco
    float gioco_totale = mode_vetri_get_total_gioco(state->selected_material);
    state->current_measure.altezza_netta_mm = encoder_mm - gioco_totale;
    
    state->altezza_saved = true;
    
    ESP_LOGI(TAG, "Altezza misurata: raw=%.1fmm, netta=%.1fmm (gioco=%.1fmm)",
             encoder_mm,
             state->current_measure.altezza_netta_mm,
             gioco_totale);
}

bool mode_vetri_save_to_session(mode_vetri_state_t *state) {
    if (!state || !state->larghezza_saved || !state->altezza_saved) {
        ESP_LOGE(TAG, "Misure incomplete, impossibile salvare");
        return false;
    }
    
    // Crea record per storage
    measurement_record_t record = storage_create_record(
        MEASURE_MODE_VETRI,
        state->current_measure.larghezza_netta_mm,
        state->current_measure.altezza_netta_mm,
        g_materials[state->selected_material].nome,
        NULL,  // No profile per vetri
        state->current_measure.note
    );
    
    // Salva su SD card
    bool saved = storage_save_measurement(&record, STORAGE_TARGET_SD_CARD);
    
    if (saved) {
        ESP_LOGI(TAG, "Misura vetro salvata: L=%.1f × H=%.1f mm (netto)",
                 state->current_measure.larghezza_netta_mm,
                 state->current_measure.altezza_netta_mm);
    }
    
    return saved;
}

bool mode_vetri_send_bluetooth(const mode_vetri_state_t *state) {
    if (!state) return false;
    
    // TODO: Implementare invio BLE
    // Formato JSON come specificato nel header
    
    ESP_LOGW(TAG, "Invio Bluetooth non ancora implementato");
    return false;
}

void mode_vetri_next_step(mode_vetri_state_t *state) {
    if (!state) return;
    
    if (state->current_step < WIZARD_STEP_SAVE) {
        state->current_step++;
        ESP_LOGI(TAG, "Wizard step avanzato a %d", state->current_step);
    }
}

void mode_vetri_prev_step(mode_vetri_state_t *state) {
    if (!state) return;
    
    if (state->current_step > WIZARD_STEP_SELECT_MATERIAL) {
        state->current_step--;
        ESP_LOGI(TAG, "Wizard step indietro a %d", state->current_step);
    }
}

void mode_vetri_reset(mode_vetri_state_t *state) {
    if (!state) return;
    
    memset(&state->current_measure, 0, sizeof(vetro_measurement_t));
    state->current_step = WIZARD_STEP_SELECT_MATERIAL;
    state->larghezza_saved = false;
    state->altezza_saved = false;
    
    ESP_LOGI(TAG, "Wizard vetri resettato");
}

const material_config_t* mode_vetri_get_material_config(material_type_t material) {
    if (material > MATERIAL_CUSTOM) {
        return &g_materials[0]; // Default Alluminio
    }
    
    return &g_materials[material];
}

float mode_vetri_get_total_gioco(material_type_t material) {
    const material_config_t *config = mode_vetri_get_material_config(material);
    return config->gioco_mm * 2.0f; // Gioco per due lati
}
