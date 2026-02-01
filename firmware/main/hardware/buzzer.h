#ifndef BUZZER_H
#define BUZZER_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/ledc.h"
#include "esp_err.h"

// Note musicali (frequenze in Hz)
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_D5  587
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_G5  784
#define NOTE_A5  880
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_REST 0  // Pausa

// Pattern sonori predefiniti
typedef enum {
    BUZZER_PATTERN_NONE = 0,
    BUZZER_PATTERN_CLICK,           // Click breve (30ms)
    BUZZER_PATTERN_SUCCESS,         // Successo (C5-E5-G5)
    BUZZER_PATTERN_ERROR,           // Errore (C5-C5-C5 veloce)
    BUZZER_PATTERN_WARNING,         // Warning (A4-A4)
    BUZZER_PATTERN_MODE_CHANGE,     // Cambio modalità (D5-A5)
    BUZZER_PATTERN_LONG_PRESS,      // Long press (F5 lungo)
    BUZZER_PATTERN_STARTUP,         // Avvio (C4-E4-G4-C5)
    BUZZER_PATTERN_SEND_OK,         // Invio misura OK (G5-C6 veloce)
    BUZZER_PATTERN_BLUETOOTH,       // BT connesso (C5-D5-E5-G5)
    BUZZER_PATTERN_LOW_BATTERY      // Batteria scarica (A4 3× lento)
} buzzer_pattern_t;

// Struttura nota per melodie
typedef struct {
    uint16_t frequency;  // Frequenza in Hz (0 = pausa)
    uint16_t duration;   // Durata in ms
} buzzer_note_t;

// Funzioni base
esp_err_t buzzer_init(void);
esp_err_t buzzer_deinit(void);

// Controllo tono singolo
esp_err_t buzzer_play_tone(uint16_t frequency, uint16_t duration_ms);
esp_err_t buzzer_stop(void);

// Pattern predefiniti
esp_err_t buzzer_play_pattern(buzzer_pattern_t pattern);

// Melodia custom
esp_err_t buzzer_play_melody(const buzzer_note_t *notes, uint8_t count);

// Controllo volume (duty cycle)
void buzzer_set_volume(uint8_t volume_percent);

// Test
void buzzer_test_all_patterns(void);

#endif // BUZZER_H
