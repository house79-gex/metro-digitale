#include "mode_fermavetri.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "MODE_FERMAVETRI";

void mode_fermavetri_init(mode_fermavetri_state_t *state) {
    if (!state) return;
    
    memset(state, 0, sizeof(mode_fermavetri_state_t));
    
    // Default: semi-automatico abilitato
    state->semi_auto_enabled = true;
    state->current_measure.auto_start = false;
    state->current_measure.mode_blitz = true;
    
    ESP_LOGI(TAG, "Modalità fermavetri inizializzata (semi-auto: ON)");
}

void mode_fermavetri_measure(mode_fermavetri_state_t *state, float encoder_mm) {
    if (!state) return;
    
    state->current_measure.lunghezza_mm = encoder_mm;
    state->current_measure.timestamp = (uint32_t)time(NULL);
    
    ESP_LOGI(TAG, "Fermavetro misurato: %.1fmm", encoder_mm);
}

bool mode_fermavetri_send_to_blitz(const mode_fermavetri_state_t *state) {
    if (!state) return false;
    
    // TODO: Implementare invio BLE a dispositivo Blitz specifico
    // Formato JSON:
    // {
    //   "type": "fermavetro",
    //   "misura_mm": 1250.5,
    //   "auto_start": true,
    //   "mode": "semi_auto"
    // }
    
    ESP_LOGI(TAG, "Invio a Blitz: %.1fmm (auto_start=%d, semi_auto=%d)",
             state->current_measure.lunghezza_mm,
             state->current_measure.auto_start,
             state->semi_auto_enabled);
    
    // Per ora log only - implementazione BLE da completare
    ESP_LOGW(TAG, "Invio BLE a Blitz non ancora implementato");
    return false;
}

void mode_fermavetri_set_semi_auto(mode_fermavetri_state_t *state, bool enabled) {
    if (!state) return;
    
    state->semi_auto_enabled = enabled;
    ESP_LOGI(TAG, "Modalità semi-auto %s", enabled ? "abilitata" : "disabilitata");
}

void mode_fermavetri_set_auto_start(mode_fermavetri_state_t *state, bool auto_start) {
    if (!state) return;
    
    state->current_measure.auto_start = auto_start;
    ESP_LOGI(TAG, "Auto-start taglio %s", auto_start ? "abilitato" : "disabilitato");
}

void mode_fermavetri_reset(mode_fermavetri_state_t *state) {
    if (!state) return;
    
    memset(&state->current_measure, 0, sizeof(fermavetro_measurement_t));
    state->current_measure.mode_blitz = true;
    state->measurement_saved = false;
    
    ESP_LOGI(TAG, "Misura fermavetro resettata");
}
