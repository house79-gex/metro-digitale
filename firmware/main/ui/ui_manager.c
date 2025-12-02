#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "UI_MANAGER";

static lv_obj_t *screen_main = NULL;
static lv_obj_t *screen_mode_select = NULL;
static lv_obj_t *screen_calibro = NULL;
static lv_obj_t *screen_vetri = NULL;
static lv_obj_t *screen_astine = NULL;
static lv_obj_t *screen_settings = NULL;

static UIScreen current_screen = UI_SCREEN_MAIN;

esp_err_t ui_manager_init(void) {
    ESP_LOGI(TAG, "Inizializzazione UI Manager...");
    
    // Inizializza stili
    ui_styles_init();
    
    // Crea tutte le schermate
    screen_main = ui_main_create();
    screen_mode_select = ui_mode_select_create();
    screen_calibro = ui_calibro_create();
    screen_vetri = ui_vetri_create();
    screen_astine = ui_astine_create();
    screen_settings = ui_settings_create();
    
    // Mostra schermata principale in base alla modalità
    if (g_config.modalita_corrente == MODE_CALIBRO) {
        ui_manager_show_screen(UI_SCREEN_CALIBRO);
    } else {
        ui_manager_show_screen(UI_SCREEN_MAIN);
    }
    
    ESP_LOGI(TAG, "UI Manager inizializzato");
    return ESP_OK;
}

void ui_manager_show_screen(UIScreen screen) {
    lv_obj_t *target = NULL;
    
    switch (screen) {
        case UI_SCREEN_MAIN:
            target = screen_main;
            break;
        case UI_SCREEN_MODE_SELECT:
            target = screen_mode_select;
            break;
        case UI_SCREEN_CALIBRO:
            target = screen_calibro;
            break;
        case UI_SCREEN_VETRI:
            target = screen_vetri;
            break;
        case UI_SCREEN_ASTINE:
            target = screen_astine;
            break;
        case UI_SCREEN_SETTINGS:
            target = screen_settings;
            break;
    }
    
    if (target != NULL) {
        lv_scr_load(target);
        current_screen = screen;
        ESP_LOGI(TAG, "Schermata caricata: %d", screen);
    }
}

UIScreen ui_manager_get_current_screen(void) {
    return current_screen;
}

void ui_manager_update(void) {
    // Aggiorna la schermata corrente
    switch (current_screen) {
        case UI_SCREEN_MAIN:
            ui_main_update();
            break;
        case UI_SCREEN_CALIBRO:
            ui_calibro_update();
            break;
        case UI_SCREEN_VETRI:
            ui_vetri_update();
            break;
        case UI_SCREEN_ASTINE:
            ui_astine_update();
            break;
        default:
            break;
    }
}

void ui_task(void *pvParameters) {
    ESP_LOGI(TAG, "Task UI avviato su core %d", xPortGetCoreID());
    
    while (1) {
        // Aggiorna UI
        lv_timer_handler();
        ui_manager_update();
        
        // 20ms per 50fps
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
