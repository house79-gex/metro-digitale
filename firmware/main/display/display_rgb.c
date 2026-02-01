#include "display_rgb.h"
#include "config.h"
#include "esp_log.h"
#include "driver/ledc.h"

static const char *TAG = "DISPLAY_RGB";

static uint8_t g_backlight_brightness = 80; // Default 80%

bool display_rgb_init(void) {
    ESP_LOGI(TAG, "Inizializzazione display RGB 800×480...");
    
    // TODO: Implementare setup panel RGB parallelo
    // Richiede:
    // - esp_lcd APIs per RGB parallel
    // - Configurazione timing LCD
    // - Double buffering PSRAM
    // - Integrazione LVGL disp_drv
    
    // Per ora: setup solo backlight PWM
    
    // Configura PWM backlight su GPIO 45
    ledc_timer_config_t ledc_timer = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .timer_num = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,
        .freq_hz = 5000,
        .clk_cfg = LEDC_AUTO_CLK
    };
    esp_err_t err = ledc_timer_config(&ledc_timer);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore config timer PWM: %s", esp_err_to_name(err));
        return false;
    }
    
    ledc_channel_config_t ledc_channel = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .timer_sel = LEDC_TIMER_0,
        .intr_type = LEDC_INTR_DISABLE,
        .gpio_num = LCD_PIN_BL,
        .duty = 0,
        .hpoint = 0
    };
    err = ledc_channel_config(&ledc_channel);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Errore config canale PWM: %s", esp_err_to_name(err));
        return false;
    }
    
    // Imposta luminosità iniziale
    display_backlight_set(g_backlight_brightness);
    
    ESP_LOGI(TAG, "Display RGB inizializzato (backlight %d%%)", g_backlight_brightness);
    ESP_LOGW(TAG, "NOTA: RGB panel setup non ancora implementato (richiede esp_lcd)");
    
    return true;
}

void display_backlight_set(uint8_t brightness) {
    if (brightness > 100) brightness = 100;
    
    g_backlight_brightness = brightness;
    
    // Converti percentuale in duty cycle (0-255)
    uint32_t duty = (brightness * 255) / 100;
    
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    
    ESP_LOGD(TAG, "Backlight impostato a %d%% (duty %lu/255)", brightness, duty);
}

uint8_t display_backlight_get(void) {
    return g_backlight_brightness;
}

void display_rgb_deinit(void) {
    // Spegni backlight
    display_backlight_set(0);
    
    // TODO: Deinit panel RGB
    
    ESP_LOGI(TAG, "Display RGB deinizializzato");
}
