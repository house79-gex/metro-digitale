#include "hardware_gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"
#include <string.h>

static const char *TAG = "HW_GPIO";

// Button state
static button_callback_t button_callback = NULL;
static bool last_button_state = false;
static uint32_t last_debounce_time = 0;
#define DEBOUNCE_DELAY_MS 50

// LED blink task handle
static TaskHandle_t led_blink_task_handle = NULL;

// Buzzer LEDC configuration
#define LEDC_TIMER              LEDC_TIMER_0
#define LEDC_MODE               LEDC_LOW_SPEED_MODE
#define LEDC_CHANNEL            LEDC_CHANNEL_0
#define LEDC_DUTY_RES           LEDC_TIMER_10_BIT
#define LEDC_DUTY               512  // 50% duty cycle
#define LEDC_FREQUENCY          2000 // Default frequency

// ISR handler for button press
static void IRAM_ATTR gpio_isr_handler(void* arg) {
    uint32_t gpio_num = (uint32_t) arg;
    
    if (gpio_num == GPIO_SEND_BUTTON) {
        // Read button state
        int level = gpio_get_level(GPIO_SEND_BUTTON);
        
        // Button pressed (active low due to pull-up)
        if (level == 0 && !last_button_state) {
            uint32_t now = xTaskGetTickCountFromISR();
            if ((now - last_debounce_time) > pdMS_TO_TICKS(DEBOUNCE_DELAY_MS)) {
                last_button_state = true;
                last_debounce_time = now;
                
                // Trigger callback if registered
                if (button_callback) {
                    // Call from ISR - should be quick
                    button_callback();
                }
            }
        } else if (level == 1) {
            last_button_state = false;
        }
    }
}

// LED blink task
static void led_blink_task(void *pvParameters) {
    uint8_t blink_count = *((uint8_t*)pvParameters);
    uint32_t duration_ms = 100; // Default duration
    
    for (uint8_t i = 0; i < blink_count; i++) {
        hardware_led_on();
        vTaskDelay(pdMS_TO_TICKS(duration_ms));
        hardware_led_off();
        vTaskDelay(pdMS_TO_TICKS(duration_ms));
    }
    
    led_blink_task_handle = NULL;
    vTaskDelete(NULL);
}

esp_err_t hardware_gpio_init(void) {
    ESP_LOGI(TAG, "Initializing hardware GPIO");
    
    // Configure SEND button (input with pull-up)
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_ANYEDGE,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = (1ULL << GPIO_SEND_BUTTON),
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_ENABLE
    };
    ESP_ERROR_CHECK(gpio_config(&io_conf));
    
    // Install GPIO ISR service
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    
    // Hook ISR handler for SEND button
    ESP_ERROR_CHECK(gpio_isr_handler_add(GPIO_SEND_BUTTON, gpio_isr_handler, (void*) GPIO_SEND_BUTTON));
    
    // Configure STATUS LED (output)
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << GPIO_STATUS_LED);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    ESP_ERROR_CHECK(gpio_config(&io_conf));
    
    // Turn off LED initially
    hardware_led_off();
    
    // Initialize buzzer
    ESP_ERROR_CHECK(hardware_buzzer_init());
    
    ESP_LOGI(TAG, "Hardware GPIO initialized");
    return ESP_OK;
}

bool hardware_button_is_pressed(void) {
    return (gpio_get_level(GPIO_SEND_BUTTON) == 0);
}

void hardware_button_set_callback(button_callback_t callback) {
    button_callback = callback;
    ESP_LOGI(TAG, "Button callback registered");
}

void hardware_led_on(void) {
    gpio_set_level(GPIO_STATUS_LED, 1);
}

void hardware_led_off(void) {
    gpio_set_level(GPIO_STATUS_LED, 0);
}

void hardware_led_toggle(void) {
    uint32_t level = gpio_get_level(GPIO_STATUS_LED);
    gpio_set_level(GPIO_STATUS_LED, !level);
}

void hardware_led_blink(uint8_t times, uint32_t duration_ms) {
    // Cancel existing blink task if running
    if (led_blink_task_handle != NULL) {
        vTaskDelete(led_blink_task_handle);
        led_blink_task_handle = NULL;
    }
    
    // Create blink task
    static uint8_t blink_params = 0;
    blink_params = times;
    
    xTaskCreate(led_blink_task, "led_blink", 2048, &blink_params, 5, &led_blink_task_handle);
}

esp_err_t hardware_buzzer_init(void) {
    ESP_LOGI(TAG, "Initializing buzzer (LEDC)");
    
    // Prepare and set configuration of timer
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = LEDC_MODE,
        .timer_num        = LEDC_TIMER,
        .duty_resolution  = LEDC_DUTY_RES,
        .freq_hz          = LEDC_FREQUENCY,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ESP_ERROR_CHECK(ledc_timer_config(&ledc_timer));
    
    // Prepare and set configuration of channel
    ledc_channel_config_t ledc_channel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LEDC_CHANNEL,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = GPIO_BUZZER,
        .duty           = 0, // Start with buzzer off
        .hpoint         = 0
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ledc_channel));
    
    ESP_LOGI(TAG, "Buzzer initialized on GPIO %d", GPIO_BUZZER);
    return ESP_OK;
}

void hardware_buzzer_tone(uint32_t frequency_hz, uint32_t duration_ms) {
    if (frequency_hz == 0) {
        hardware_buzzer_stop();
        return;
    }
    
    // Set frequency
    ledc_set_freq(LEDC_MODE, LEDC_TIMER, frequency_hz);
    
    // Set duty cycle (50%)
    ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, LEDC_DUTY);
    ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
    
    // Note: duration_ms parameter controls blocking behavior:
    // - If duration_ms > 0: blocks calling task (use from non-critical tasks only)
    // - If duration_ms == 0: non-blocking, caller must call hardware_buzzer_stop()
    // Consider using buzzer_feedback.c for non-blocking patterns
    if (duration_ms > 0) {
        vTaskDelay(pdMS_TO_TICKS(duration_ms));
        hardware_buzzer_stop();
    }
}

void hardware_buzzer_stop(void) {
    ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, 0);
    ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
}
