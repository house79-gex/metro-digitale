#include "encoder.h"
#include "driver/pulse_cnt.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <math.h>

static const char *TAG = "ENCODER";

static pcnt_unit_handle_t pcnt_unit = NULL;
static int32_t accumulated_count = 0;
static float zero_offset_mm = 0.0f;

// Callback per overflow/underflow del contatore
static bool pcnt_on_reach(pcnt_unit_handle_t unit, const pcnt_watch_event_data_t *edata, void *user_ctx) {
    // Accumula il valore quando si raggiunge il limite
    if (edata->watch_point_value > 0) {
        accumulated_count += edata->watch_point_value;
    } else {
        accumulated_count += edata->watch_point_value;
    }
    return false;
}

esp_err_t encoder_init(void) {
    ESP_LOGI(TAG, "Inizializzazione encoder...");
    
    // Configurazione PCNT
    pcnt_unit_config_t unit_config = {
        .high_limit = 32767,
        .low_limit = -32768,
    };
    
    ESP_ERROR_CHECK(pcnt_new_unit(&unit_config, &pcnt_unit));
    
    // Configurazione filtro glitch
    pcnt_glitch_filter_config_t filter_config = {
        .max_glitch_ns = 1000,
    };
    ESP_ERROR_CHECK(pcnt_unit_set_glitch_filter(pcnt_unit, &filter_config));
    
    // Configurazione canale A
    pcnt_chan_config_t chan_a_config = {
        .edge_gpio_num = ENCODER_PIN_A,
        .level_gpio_num = ENCODER_PIN_B,
    };
    pcnt_channel_handle_t pcnt_chan_a = NULL;
    ESP_ERROR_CHECK(pcnt_new_channel(pcnt_unit, &chan_a_config, &pcnt_chan_a));
    
    // Configurazione canale B
    pcnt_chan_config_t chan_b_config = {
        .edge_gpio_num = ENCODER_PIN_B,
        .level_gpio_num = ENCODER_PIN_A,
    };
    pcnt_channel_handle_t pcnt_chan_b = NULL;
    ESP_ERROR_CHECK(pcnt_new_channel(pcnt_unit, &chan_b_config, &pcnt_chan_b));
    
    // Impostazione modalità quadratura x4
    ESP_ERROR_CHECK(pcnt_channel_set_edge_action(pcnt_chan_a,
                                                   PCNT_CHANNEL_EDGE_ACTION_DECREASE,
                                                   PCNT_CHANNEL_EDGE_ACTION_INCREASE));
    ESP_ERROR_CHECK(pcnt_channel_set_level_action(pcnt_chan_a,
                                                    PCNT_CHANNEL_LEVEL_ACTION_KEEP,
                                                    PCNT_CHANNEL_LEVEL_ACTION_INVERSE));
    
    ESP_ERROR_CHECK(pcnt_channel_set_edge_action(pcnt_chan_b,
                                                   PCNT_CHANNEL_EDGE_ACTION_INCREASE,
                                                   PCNT_CHANNEL_EDGE_ACTION_DECREASE));
    ESP_ERROR_CHECK(pcnt_channel_set_level_action(pcnt_chan_b,
                                                    PCNT_CHANNEL_LEVEL_ACTION_KEEP,
                                                    PCNT_CHANNEL_LEVEL_ACTION_INVERSE));
    
    // Registra callback per overflow
    pcnt_event_callbacks_t cbs = {
        .on_reach = pcnt_on_reach,
    };
    ESP_ERROR_CHECK(pcnt_unit_register_event_callbacks(pcnt_unit, &cbs, NULL));
    
    // Imposta watch points
    ESP_ERROR_CHECK(pcnt_unit_add_watch_point(pcnt_unit, 32767));
    ESP_ERROR_CHECK(pcnt_unit_add_watch_point(pcnt_unit, -32768));
    
    // Abilita il contatore
    ESP_ERROR_CHECK(pcnt_unit_enable(pcnt_unit));
    ESP_ERROR_CHECK(pcnt_unit_clear_count(pcnt_unit));
    ESP_ERROR_CHECK(pcnt_unit_start(pcnt_unit));
    
    ESP_LOGI(TAG, "Encoder inizializzato con successo");
    return ESP_OK;
}

int32_t encoder_get_count(void) {
    int count = 0;
    pcnt_unit_get_count(pcnt_unit, &count);
    return accumulated_count + count;
}

float encoder_get_position_mm(void) {
    int32_t count = encoder_get_count();
    float position = (float)count * g_config.encoder_resolution_mm;
    return position - zero_offset_mm;
}

void encoder_zero(void) {
    zero_offset_mm = (float)encoder_get_count() * g_config.encoder_resolution_mm;
    g_state.is_zeroed = true;
    g_state.zero_position_mm = zero_offset_mm;
    ESP_LOGI(TAG, "Zero impostato a: %.3f mm", zero_offset_mm);
}

void encoder_set_zero_position(float position_mm) {
    zero_offset_mm = position_mm;
    g_state.is_zeroed = true;
    g_state.zero_position_mm = position_mm;
}

// Calcola misura netta fermavetro con compensazione puntali
float encoder_calc_fermavetro_netto(const GlobalConfig *cfg) {
    float raw_mm = encoder_get_position_mm();
    
    if (cfg->puntale_corrente_idx >= cfg->num_puntali) {
        return raw_mm;
    }
    
    const PuntaleConfig *puntale = &cfg->puntali[cfg->puntale_corrente_idx];
    
    // Sottrai gli offset dei puntali
    float netto = raw_mm - puntale->offset_fisso_mm - puntale->offset_mobile_mm;
    
    // Verifica distanza minima
    if (netto < puntale->distanza_minima_mm) {
        ESP_LOGW(TAG, "Misura sotto distanza minima puntale: %.2f < %.2f", 
                 netto, puntale->distanza_minima_mm);
    }
    
    return netto;
}

// Calcola misura netta vetro con gioco materiale
float encoder_calc_vetro_netto(const GlobalConfig *cfg, float raw_mm) {
    if (cfg->materiale_corrente_idx >= cfg->num_materiali) {
        return raw_mm;
    }
    
    const MaterialeConfig *materiale = &cfg->materiali[cfg->materiale_corrente_idx];
    
    // Sottrai il gioco del materiale
    float netto = raw_mm - materiale->gioco_vetro_mm;
    
    return netto;
}

// Calcola misura taglio astina con offset profilo
float encoder_calc_astina_taglio(const GlobalConfig *cfg, float raw_mm) {
    if (cfg->astina_corrente_idx >= cfg->num_astine) {
        return raw_mm;
    }
    
    const AstinaConfig *astina = &cfg->astine[cfg->astina_corrente_idx];
    
    // Applica offset astina (generalmente negativo)
    float taglio = raw_mm + astina->offset_mm;
    
    return taglio;
}

// Task encoder (100Hz su Core 1)
void encoder_task(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(10); // 100Hz
    
    ESP_LOGI(TAG, "Task encoder avviato su core %d", xPortGetCoreID());
    
    while (1) {
        // Aggiorna stato encoder
        g_state.encoder_count = encoder_get_count();
        g_state.position_mm = encoder_get_position_mm();
        
        // Auto-zero se abilitato e posizione molto vicina a zero
        if (g_config.auto_zero_enabled && !g_state.is_zeroed) {
            if (fabsf(g_state.position_mm) < 0.5f) {
                encoder_zero();
            }
        }
        
        // Attendi prossimo ciclo
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}
