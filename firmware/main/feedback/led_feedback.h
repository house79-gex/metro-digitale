#ifndef LED_FEEDBACK_H
#define LED_FEEDBACK_H

#include "esp_err.h"
#include <stdint.h>

// LED pattern types
typedef enum {
    LED_PATTERN_SUCCESS = 0,    // 3x blink (green)
    LED_PATTERN_ERROR,          // 5x fast blink (red)
    LED_PATTERN_BUTTON_PRESS,   // 1x short blink
    LED_PATTERN_BT_CONNECTED,   // Steady on
    LED_PATTERN_BT_DISCONNECTED,// Off
    LED_PATTERN_WORKING         // Slow pulse
} LEDPattern;

// Initialize LED feedback system
esp_err_t led_feedback_init(void);

// Play LED pattern
void led_feedback_play(LEDPattern pattern);

// Stop any pattern and turn off LED
void led_feedback_stop(void);

// Set LED brightness (0-100%)
void led_feedback_set_brightness(uint8_t brightness);

#endif // LED_FEEDBACK_H
