#include "button_send.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "esp_timer.h"

static const char *TAG = "BUTTON_SEND";

// Configurazione timing
#define DEBOUNCE_TIME_MS        50      // Debouncing time
#define LONG_PRESS_TIME_MS      1000    // Tempo per long press
#define DOUBLE_CLICK_TIME_MS    400     // Tempo massimo tra due click

// Variabili globali
static gpio_num_t g_button_pin = GPIO_NUM_NC;
static button_event_callback_t g_callback = NULL;
static QueueHandle_t g_event_queue = NULL;
static TaskHandle_t g_task_handle = NULL;
static volatile bool g_enabled = true;
static volatile uint32_t g_event_count = 0;

// Stato pulsante per rilevamento eventi
static struct {
    bool pressed;
    uint64_t press_time_us;
    uint64_t release_time_us;
    uint64_t last_click_time_us;
    bool long_press_sent;
    uint8_t click_count;
} g_button_state = {0};

// ISR handler
static void IRAM_ATTR button_isr_handler(void *arg) {
    static uint64_t last_isr_time = 0;
    uint64_t now = esp_timer_get_time();
    
    // Debouncing
    if (now - last_isr_time < DEBOUNCE_TIME_MS * 1000) {
        return;
    }
    last_isr_time = now;
    
    // Invia evento alla queue
    button_event_type_t event;
    bool level = gpio_get_level(g_button_pin);
    
    if (!level) { // Pressed (active low con pull-up)
        event = BUTTON_EVENT_SINGLE_CLICK; // Placeholder
        xQueueSendFromISR(g_event_queue, &event, NULL);
    }
}

// Task per elaborazione eventi
static void button_task(void *arg) {
    button_event_type_t event;
    uint64_t now_us;
    
    ESP_LOGI(TAG, "Button task started");
    
    while (1) {
        // Polling stato pulsante per rilevare long press
        bool current_state = !gpio_get_level(g_button_pin); // Inverted (active low)
        now_us = esp_timer_get_time();
        
        if (current_state && !g_button_state.pressed) {
            // Transizione OFF -> ON (premuto)
            g_button_state.pressed = true;
            g_button_state.press_time_us = now_us;
            g_button_state.long_press_sent = false;
            
        } else if (!current_state && g_button_state.pressed) {
            // Transizione ON -> OFF (rilasciato)
            g_button_state.pressed = false;
            g_button_state.release_time_us = now_us;
            
            uint64_t press_duration_ms = (now_us - g_button_state.press_time_us) / 1000;
            
            if (press_duration_ms >= LONG_PRESS_TIME_MS) {
                // Long press rilasciato
                if (g_enabled && g_callback) {
                    g_callback(BUTTON_EVENT_LONG_RELEASE);
                    g_event_count++;
                }
                g_button_state.click_count = 0;
                
            } else {
                // Click normale
                g_button_state.click_count++;
                
                // Verifica double click
                if (g_button_state.click_count == 1) {
                    g_button_state.last_click_time_us = now_us;
                } else if (g_button_state.click_count == 2) {
                    uint64_t time_between_clicks_ms = 
                        (now_us - g_button_state.last_click_time_us) / 1000;
                    
                    if (time_between_clicks_ms < DOUBLE_CLICK_TIME_MS) {
                        // Double click rilevato!
                        if (g_enabled && g_callback) {
                            g_callback(BUTTON_EVENT_DOUBLE_CLICK);
                            g_event_count++;
                        }
                        g_button_state.click_count = 0;
                    } else {
                        // Troppo tempo tra click, resetta
                        g_button_state.click_count = 1;
                        g_button_state.last_click_time_us = now_us;
                    }
                }
            }
            
        } else if (current_state && g_button_state.pressed) {
            // Pulsante ancora premuto, verifica long press
            uint64_t press_duration_ms = (now_us - g_button_state.press_time_us) / 1000;
            
            if (press_duration_ms >= LONG_PRESS_TIME_MS && !g_button_state.long_press_sent) {
                // Long press rilevato!
                if (g_enabled && g_callback) {
                    g_callback(BUTTON_EVENT_LONG_PRESS);
                    g_event_count++;
                }
                g_button_state.long_press_sent = true;
                g_button_state.click_count = 0;
            }
        }
        
        // Timeout per single click
        if (g_button_state.click_count == 1 && !g_button_state.pressed) {
            uint64_t time_since_last_click_ms = (now_us - g_button_state.last_click_time_us) / 1000;
            
            if (time_since_last_click_ms >= DOUBLE_CLICK_TIME_MS) {
                // Single click confermato (nessun secondo click)
                if (g_enabled && g_callback) {
                    g_callback(BUTTON_EVENT_SINGLE_CLICK);
                    g_event_count++;
                }
                g_button_state.click_count = 0;
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(20)); // Poll ogni 20ms (ridotto da 10ms per efficienza)
    }
}

bool button_send_init(gpio_num_t gpio_pin, button_event_callback_t callback) {
    if (gpio_pin == GPIO_NUM_NC) {
        ESP_LOGE(TAG, "Invalid GPIO pin");
        return false;
    }
    
    g_button_pin = gpio_pin;
    g_callback = callback;
    
    // Configura GPIO con pull-up (active low)
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << gpio_pin),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_ANYEDGE
    };
    
    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore configurazione GPIO: %s", esp_err_to_name(err));
        return false;
    }
    
    // Crea queue eventi
    g_event_queue = xQueueCreate(10, sizeof(button_event_type_t));
    if (!g_event_queue) {
        ESP_LOGE(TAG, "Errore creazione queue");
        return false;
    }
    
    // Installa ISR handler
    err = gpio_install_isr_service(0);
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "Errore installazione ISR service: %s", esp_err_to_name(err));
        vQueueDelete(g_event_queue);
        return false;
    }
    
    err = gpio_isr_handler_add(gpio_pin, button_isr_handler, NULL);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore aggiunta ISR handler: %s", esp_err_to_name(err));
        vQueueDelete(g_event_queue);
        return false;
    }
    
    // Crea task elaborazione eventi
    BaseType_t ret = xTaskCreate(button_task, "button_send_task", 
                                  3072, NULL, 5, &g_task_handle);
    if (ret != pdPASS) {
        ESP_LOGE(TAG, "Errore creazione task");
        gpio_isr_handler_remove(gpio_pin);
        vQueueDelete(g_event_queue);
        return false;
    }
    
    ESP_LOGI(TAG, "Button SEND inizializzato su GPIO %d", gpio_pin);
    return true;
}

void button_send_register_callback(button_event_callback_t callback) {
    g_callback = callback;
}

bool button_send_is_pressed(void) {
    if (g_button_pin == GPIO_NUM_NC) return false;
    return !gpio_get_level(g_button_pin); // Inverted (active low)
}

void button_send_enable(bool enable) {
    g_enabled = enable;
    ESP_LOGI(TAG, "Button eventi %s", enable ? "abilitati" : "disabilitati");
}

void button_send_deinit(void) {
    if (g_task_handle) {
        vTaskDelete(g_task_handle);
        g_task_handle = NULL;
    }
    
    if (g_button_pin != GPIO_NUM_NC) {
        gpio_isr_handler_remove(g_button_pin);
    }
    
    if (g_event_queue) {
        vQueueDelete(g_event_queue);
        g_event_queue = NULL;
    }
    
    g_button_pin = GPIO_NUM_NC;
    g_callback = NULL;
    
    ESP_LOGI(TAG, "Button SEND deinizializzato");
}

uint32_t button_send_get_event_count(void) {
    return g_event_count;
}
