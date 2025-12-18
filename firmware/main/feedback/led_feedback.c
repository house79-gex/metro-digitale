#include "led_feedback.h"
#include "../hardware/hardware_gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "LED_FB";
static uint8_t led_brightness = 100; // Default 100%
static TaskHandle_t led_pattern_task_handle = NULL;

// Task to handle LED patterns
static void led_pattern_task(void *pvParameters) {
    LEDPattern pattern = *(LEDPattern*)pvParameters;
    
    switch (pattern) {
        case LED_PATTERN_SUCCESS:
            // 3x blink
            for (int i = 0; i < 3; i++) {
                hardware_led_on();
                vTaskDelay(pdMS_TO_TICKS(150));
                hardware_led_off();
                vTaskDelay(pdMS_TO_TICKS(150));
            }
            break;
            
        case LED_PATTERN_ERROR:
            // 5x fast blink
            for (int i = 0; i < 5; i++) {
                hardware_led_on();
                vTaskDelay(pdMS_TO_TICKS(80));
                hardware_led_off();
                vTaskDelay(pdMS_TO_TICKS(80));
            }
            break;
            
        case LED_PATTERN_BUTTON_PRESS:
            // 1x short blink
            hardware_led_on();
            vTaskDelay(pdMS_TO_TICKS(50));
            hardware_led_off();
            break;
            
        case LED_PATTERN_BT_CONNECTED:
            // Steady on
            hardware_led_on();
            break;
            
        case LED_PATTERN_BT_DISCONNECTED:
            // Off
            hardware_led_off();
            break;
            
        case LED_PATTERN_WORKING:
            // Slow pulse (10 seconds)
            for (int i = 0; i < 10; i++) {
                hardware_led_on();
                vTaskDelay(pdMS_TO_TICKS(500));
                hardware_led_off();
                vTaskDelay(pdMS_TO_TICKS(500));
            }
            break;
            
        default:
            ESP_LOGW(TAG, "Unknown LED pattern: %d", pattern);
            break;
    }
    
    led_pattern_task_handle = NULL;
    vTaskDelete(NULL);
}

esp_err_t led_feedback_init(void) {
    ESP_LOGI(TAG, "LED feedback system initialized");
    return ESP_OK;
}

void led_feedback_play(LEDPattern pattern) {
    // Stop existing pattern if running
    if (led_pattern_task_handle != NULL) {
        vTaskDelete(led_pattern_task_handle);
        led_pattern_task_handle = NULL;
    }
    
    // For immediate patterns that don't need a task
    if (pattern == LED_PATTERN_BT_CONNECTED) {
        hardware_led_on();
        return;
    } else if (pattern == LED_PATTERN_BT_DISCONNECTED) {
        hardware_led_off();
        return;
    }
    
    // Create task for pattern
    static LEDPattern current_pattern;
    current_pattern = pattern;
    
    xTaskCreate(led_pattern_task, "led_pattern", 2048, &current_pattern, 5, &led_pattern_task_handle);
}

void led_feedback_stop(void) {
    if (led_pattern_task_handle != NULL) {
        vTaskDelete(led_pattern_task_handle);
        led_pattern_task_handle = NULL;
    }
    hardware_led_off();
}

void led_feedback_set_brightness(uint8_t brightness) {
    if (brightness > 100) {
        brightness = 100;
    }
    led_brightness = brightness;
    ESP_LOGI(TAG, "LED brightness set to %d%%", led_brightness);
    // Note: For simple on/off LED, brightness doesn't apply
    // For PWM-controlled LEDs, would adjust duty cycle here
}
