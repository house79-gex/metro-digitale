#ifndef BUZZER_FEEDBACK_H
#define BUZZER_FEEDBACK_H

#include "esp_err.h"

// Musical note frequencies (Hz)
#define NOTE_C5     523
#define NOTE_D5     587
#define NOTE_E5     659
#define NOTE_G5     784
#define NOTE_A5     880
#define NOTE_C6     1047

// Feedback event types
typedef enum {
    FEEDBACK_SUCCESS = 0,      // Measurement sent successfully
    FEEDBACK_ERROR,            // Error occurred
    FEEDBACK_MODE_CHANGE,      // Mode switched
    FEEDBACK_BUTTON_PRESS,     // Button pressed
    FEEDBACK_BT_CONNECTED,     // Bluetooth connected
    FEEDBACK_BT_DISCONNECTED   // Bluetooth disconnected
} FeedbackEvent;

// Initialize buzzer feedback system
esp_err_t buzzer_feedback_init(void);

// Play feedback pattern for event
void buzzer_feedback_play(FeedbackEvent event);

// Custom tone sequence
void buzzer_feedback_play_sequence(const uint32_t *frequencies, const uint32_t *durations, size_t count);

// Stop any playing sound
void buzzer_feedback_stop(void);

#endif // BUZZER_FEEDBACK_H
