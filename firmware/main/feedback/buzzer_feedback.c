#include "buzzer_feedback.h"
#include "../hardware/buzzer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "BUZZER_FB";

// Feedback patterns definition
// Success: C5-E5-G5 ascending (~310ms)
static const uint32_t pattern_success_freq[] = {NOTE_C5, NOTE_E5, NOTE_G5};
static const uint32_t pattern_success_dur[] = {100, 100, 110};

// Error: C5-C5-C5 repeated trill (~400ms)
static const uint32_t pattern_error_freq[] = {NOTE_C5, 0, NOTE_C5, 0, NOTE_C5};
static const uint32_t pattern_error_dur[] = {80, 20, 80, 20, 100};

// Mode change: D5-A5 double note (~250ms)
static const uint32_t pattern_mode_freq[] = {NOTE_D5, NOTE_A5};
static const uint32_t pattern_mode_dur[] = {120, 130};

// Button press: C6 short click (~30ms)
static const uint32_t pattern_button_freq[] = {NOTE_C6};
static const uint32_t pattern_button_dur[] = {30};

// BT connected: C5-D5-E5-G5 scale (~500ms)
static const uint32_t pattern_bt_conn_freq[] = {NOTE_C5, NOTE_D5, NOTE_E5, NOTE_G5};
static const uint32_t pattern_bt_conn_dur[] = {100, 100, 100, 200};

// BT disconnected: G5-E5-C5 descending (~400ms)
static const uint32_t pattern_bt_disc_freq[] = {NOTE_G5, NOTE_E5, NOTE_C5};
static const uint32_t pattern_bt_disc_dur[] = {100, 100, 200};

esp_err_t buzzer_feedback_init(void) {
    ESP_LOGI(TAG, "Buzzer feedback system initialized");
    return ESP_OK;
}

void buzzer_feedback_play_sequence(const uint32_t *frequencies, const uint32_t *durations, size_t count) {
    for (size_t i = 0; i < count; i++) {
        if (frequencies[i] == 0) {
            // Rest/pause
            buzzer_stop();
            vTaskDelay(pdMS_TO_TICKS(durations[i]));
        } else {
            buzzer_play_tone(frequencies[i], durations[i]);
        }
    }
    buzzer_stop();
}

void buzzer_feedback_play(FeedbackEvent event) {
    switch (event) {
        case FEEDBACK_SUCCESS:
            ESP_LOGI(TAG, "Playing SUCCESS pattern");
            buzzer_feedback_play_sequence(pattern_success_freq, pattern_success_dur, 3);
            break;
            
        case FEEDBACK_ERROR:
            ESP_LOGI(TAG, "Playing ERROR pattern");
            buzzer_feedback_play_sequence(pattern_error_freq, pattern_error_dur, 5);
            break;
            
        case FEEDBACK_MODE_CHANGE:
            ESP_LOGI(TAG, "Playing MODE_CHANGE pattern");
            buzzer_feedback_play_sequence(pattern_mode_freq, pattern_mode_dur, 2);
            break;
            
        case FEEDBACK_BUTTON_PRESS:
            ESP_LOGD(TAG, "Playing BUTTON_PRESS pattern");
            buzzer_feedback_play_sequence(pattern_button_freq, pattern_button_dur, 1);
            break;
            
        case FEEDBACK_BT_CONNECTED:
            ESP_LOGI(TAG, "Playing BT_CONNECTED pattern");
            buzzer_feedback_play_sequence(pattern_bt_conn_freq, pattern_bt_conn_dur, 4);
            break;
            
        case FEEDBACK_BT_DISCONNECTED:
            ESP_LOGI(TAG, "Playing BT_DISCONNECTED pattern");
            buzzer_feedback_play_sequence(pattern_bt_disc_freq, pattern_bt_disc_dur, 3);
            break;
            
        default:
            ESP_LOGW(TAG, "Unknown feedback event: %d", event);
            break;
    }
}

void buzzer_feedback_stop(void) {
    buzzer_stop();
}
