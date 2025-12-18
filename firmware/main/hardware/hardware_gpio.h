#ifndef HARDWARE_GPIO_H
#define HARDWARE_GPIO_H

#include <stdbool.h>
#include "esp_err.h"
#include "driver/gpio.h"

// GPIO Pin Definitions
#define GPIO_SEND_BUTTON    25  // Physical SEND button (input, pull-up)
#define GPIO_STATUS_LED     27  // Status LED (output)
#define GPIO_BUZZER         14  // Buzzer PWM (output, LEDC channel 0)

// Button state
typedef enum {
    BUTTON_RELEASED = 0,
    BUTTON_PRESSED = 1
} ButtonState;

// Button callback type
typedef void (*button_callback_t)(void);

// Initialize hardware GPIO (button, LED)
esp_err_t hardware_gpio_init(void);

// Button functions
bool hardware_button_is_pressed(void);
void hardware_button_set_callback(button_callback_t callback);

// LED functions
void hardware_led_on(void);
void hardware_led_off(void);
void hardware_led_toggle(void);
void hardware_led_blink(uint8_t times, uint32_t duration_ms);

// Buzzer functions (basic control, patterns in buzzer_feedback.c)
esp_err_t hardware_buzzer_init(void);
void hardware_buzzer_tone(uint32_t frequency_hz, uint32_t duration_ms);
void hardware_buzzer_stop(void);

#endif // HARDWARE_GPIO_H
