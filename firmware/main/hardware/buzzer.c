#include "buzzer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "../config.h"

static const char *TAG = "BUZZER";

// Volume corrente (0-100%)
static uint8_t current_volume = 50;

// Flag di inizializzazione
static bool initialized = false;

// Melodie predefinite
static const buzzer_note_t melody_click[] = {
    {NOTE_C6, 30}
};

static const buzzer_note_t melody_success[] = {
    {NOTE_C5, 100}, {NOTE_E5, 100}, {NOTE_G5, 150}
};

static const buzzer_note_t melody_error[] = {
    {NOTE_C5, 80}, {NOTE_C5, 80}, {NOTE_C5, 80}
};

static const buzzer_note_t melody_warning[] = {
    {NOTE_A4, 150}, {NOTE_REST, 50}, {NOTE_A4, 150}
};

static const buzzer_note_t melody_mode_change[] = {
    {NOTE_D5, 100}, {NOTE_A5, 120}
};

static const buzzer_note_t melody_long_press[] = {
    {NOTE_F5, 150}
};

static const buzzer_note_t melody_startup[] = {
    {NOTE_C4, 100}, {NOTE_E4, 100}, {NOTE_G4, 100}, {NOTE_C5, 150}
};

static const buzzer_note_t melody_send_ok[] = {
    {NOTE_G5, 80}, {NOTE_C6, 120}
};

static const buzzer_note_t melody_bluetooth[] = {
    {NOTE_C5, 100}, {NOTE_D5, 100}, {NOTE_E5, 100}, {NOTE_G5, 150}
};

static const buzzer_note_t melody_low_battery[] = {
    {NOTE_A4, 200}, {NOTE_REST, 100}, {NOTE_A4, 200}, 
    {NOTE_REST, 100}, {NOTE_A4, 200}
};

esp_err_t buzzer_init(void) {
    if (initialized) {
        ESP_LOGW(TAG, "Buzzer già inizializzato");
        return ESP_OK;
    }

#ifndef BUZZER_PIN
    ESP_LOGE(TAG, "BUZZER_PIN non definito in config.h");
    return ESP_FAIL;
#endif

#if BUZZER_ENABLED == 0
    ESP_LOGW(TAG, "Buzzer disabilitato in config.h");
    return ESP_OK;
#endif

    ESP_LOGI(TAG, "Inizializzazione buzzer su GPIO %d", BUZZER_PIN);

    // Configura timer LEDC
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = BUZZER_MODE,
        .timer_num        = BUZZER_TIMER,
        .duty_resolution  = BUZZER_RESOLUTION,
        .freq_hz          = 1000,  // Frequenza iniziale
        .clk_cfg          = LEDC_AUTO_CLK
    };
    esp_err_t ret = ledc_timer_config(&ledc_timer);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Errore configurazione timer LEDC: %s", esp_err_to_name(ret));
        return ret;
    }

    // Configura canale LEDC
    ledc_channel_config_t ledc_channel = {
        .speed_mode     = BUZZER_MODE,
        .channel        = BUZZER_CHANNEL,
        .timer_sel      = BUZZER_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = BUZZER_PIN,
        .duty           = 0,  // Buzzer spento inizialmente
        .hpoint         = 0
    };
    ret = ledc_channel_config(&ledc_channel);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Errore configurazione canale LEDC: %s", esp_err_to_name(ret));
        return ret;
    }

    initialized = true;
    ESP_LOGI(TAG, "Buzzer inizializzato con successo");

    // Test tono iniziale C5 per 50ms
    buzzer_play_tone(NOTE_C5, 50);

    return ESP_OK;
}

esp_err_t buzzer_deinit(void) {
    if (!initialized) {
        return ESP_OK;
    }

    buzzer_stop();
    initialized = false;
    ESP_LOGI(TAG, "Buzzer deinizializzato");
    return ESP_OK;
}

esp_err_t buzzer_play_tone(uint16_t frequency, uint16_t duration_ms) {
    if (!initialized) {
        ESP_LOGW(TAG, "Buzzer non inizializzato");
        return ESP_ERR_INVALID_STATE;
    }

#if BUZZER_ENABLED == 0
    return ESP_OK;
#endif

    if (frequency == 0) {
        // Pausa - ferma il buzzer
        buzzer_stop();
        if (duration_ms > 0) {
            vTaskDelay(pdMS_TO_TICKS(duration_ms));
        }
        return ESP_OK;
    }

    // Imposta frequenza
    esp_err_t ret = ledc_set_freq(BUZZER_MODE, BUZZER_TIMER, frequency);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Errore impostazione frequenza: %s", esp_err_to_name(ret));
        return ret;
    }

    // Calcola duty cycle in base al volume
    uint32_t max_duty = (1 << BUZZER_RESOLUTION);
    uint32_t duty = (max_duty * current_volume) / 100;

    // Applica duty cycle
    ret = ledc_set_duty(BUZZER_MODE, BUZZER_CHANNEL, duty);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Errore impostazione duty: %s", esp_err_to_name(ret));
        return ret;
    }

    ret = ledc_update_duty(BUZZER_MODE, BUZZER_CHANNEL);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Errore update duty: %s", esp_err_to_name(ret));
        return ret;
    }

    // Delay per la durata del tono
    if (duration_ms > 0) {
        vTaskDelay(pdMS_TO_TICKS(duration_ms));
        buzzer_stop();
    }

    return ESP_OK;
}

esp_err_t buzzer_stop(void) {
    if (!initialized) {
        return ESP_ERR_INVALID_STATE;
    }

    // Imposta duty cycle a 0
    esp_err_t ret = ledc_set_duty(BUZZER_MODE, BUZZER_CHANNEL, 0);
    if (ret == ESP_OK) {
        ret = ledc_update_duty(BUZZER_MODE, BUZZER_CHANNEL);
    }

    return ret;
}

esp_err_t buzzer_play_melody(const buzzer_note_t *notes, uint8_t count) {
    if (!initialized) {
        ESP_LOGW(TAG, "Buzzer non inizializzato");
        return ESP_ERR_INVALID_STATE;
    }

    if (notes == NULL || count == 0) {
        ESP_LOGW(TAG, "Melodia non valida");
        return ESP_ERR_INVALID_ARG;
    }

    for (uint8_t i = 0; i < count; i++) {
        buzzer_play_tone(notes[i].frequency, notes[i].duration);
        // Piccola pausa tra note
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    return ESP_OK;
}

esp_err_t buzzer_play_pattern(buzzer_pattern_t pattern) {
    if (!initialized) {
        ESP_LOGW(TAG, "Buzzer non inizializzato");
        return ESP_ERR_INVALID_STATE;
    }

    esp_err_t ret = ESP_OK;

    switch (pattern) {
        case BUZZER_PATTERN_CLICK:
            ESP_LOGD(TAG, "Pattern: CLICK");
            ret = buzzer_play_melody(melody_click, sizeof(melody_click) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_SUCCESS:
            ESP_LOGI(TAG, "Pattern: SUCCESS");
            ret = buzzer_play_melody(melody_success, sizeof(melody_success) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_ERROR:
            ESP_LOGI(TAG, "Pattern: ERROR");
            ret = buzzer_play_melody(melody_error, sizeof(melody_error) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_WARNING:
            ESP_LOGI(TAG, "Pattern: WARNING");
            ret = buzzer_play_melody(melody_warning, sizeof(melody_warning) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_MODE_CHANGE:
            ESP_LOGI(TAG, "Pattern: MODE_CHANGE");
            ret = buzzer_play_melody(melody_mode_change, sizeof(melody_mode_change) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_LONG_PRESS:
            ESP_LOGI(TAG, "Pattern: LONG_PRESS");
            ret = buzzer_play_melody(melody_long_press, sizeof(melody_long_press) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_STARTUP:
            ESP_LOGI(TAG, "Pattern: STARTUP");
            ret = buzzer_play_melody(melody_startup, sizeof(melody_startup) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_SEND_OK:
            ESP_LOGI(TAG, "Pattern: SEND_OK");
            ret = buzzer_play_melody(melody_send_ok, sizeof(melody_send_ok) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_BLUETOOTH:
            ESP_LOGI(TAG, "Pattern: BLUETOOTH");
            ret = buzzer_play_melody(melody_bluetooth, sizeof(melody_bluetooth) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_LOW_BATTERY:
            ESP_LOGI(TAG, "Pattern: LOW_BATTERY");
            ret = buzzer_play_melody(melody_low_battery, sizeof(melody_low_battery) / sizeof(buzzer_note_t));
            break;

        case BUZZER_PATTERN_NONE:
        default:
            ESP_LOGW(TAG, "Pattern non riconosciuto: %d", pattern);
            ret = ESP_ERR_INVALID_ARG;
            break;
    }

    return ret;
}

void buzzer_set_volume(uint8_t volume_percent) {
    // Limita volume a 0-100
    if (volume_percent > 100) {
        volume_percent = 100;
    }

    current_volume = volume_percent;
    ESP_LOGI(TAG, "Volume impostato a: %d%%", current_volume);
}

void buzzer_test_all_patterns(void) {
    ESP_LOGI(TAG, "=== Test di tutti i pattern ===");

    const buzzer_pattern_t patterns[] = {
        BUZZER_PATTERN_CLICK,
        BUZZER_PATTERN_SUCCESS,
        BUZZER_PATTERN_ERROR,
        BUZZER_PATTERN_WARNING,
        BUZZER_PATTERN_MODE_CHANGE,
        BUZZER_PATTERN_LONG_PRESS,
        BUZZER_PATTERN_STARTUP,
        BUZZER_PATTERN_SEND_OK,
        BUZZER_PATTERN_BLUETOOTH,
        BUZZER_PATTERN_LOW_BATTERY
    };

    const char *pattern_names[] = {
        "CLICK",
        "SUCCESS",
        "ERROR",
        "WARNING",
        "MODE_CHANGE",
        "LONG_PRESS",
        "STARTUP",
        "SEND_OK",
        "BLUETOOTH",
        "LOW_BATTERY"
    };

    for (int i = 0; i < sizeof(patterns) / sizeof(buzzer_pattern_t); i++) {
        ESP_LOGI(TAG, "Testando pattern %d: %s", i + 1, pattern_names[i]);
        buzzer_play_pattern(patterns[i]);
        vTaskDelay(pdMS_TO_TICKS(500));  // Pausa tra pattern
    }

    ESP_LOGI(TAG, "=== Test completato ===");
}
