#ifndef UI_MANAGER_H
#define UI_MANAGER_H

#include "lvgl.h"
#include "esp_err.h"

// Schermate UI
typedef enum {
    UI_SCREEN_MAIN = 0,
    UI_SCREEN_MODE_SELECT,
    UI_SCREEN_CALIBRO,
    UI_SCREEN_VETRI,
    UI_SCREEN_ASTINE,
    UI_SCREEN_SETTINGS,
    UI_SCREEN_RILIEVI_SPECIALI,
    UI_SCREEN_TIPOLOGIE
} UIScreen;

// Inizializzazione UI
esp_err_t ui_manager_init(void);

// Navigazione schermate
void ui_manager_show_screen(UIScreen screen);
UIScreen ui_manager_get_current_screen(void);

// Aggiornamento UI
void ui_manager_update(void);

// Task UI LVGL (da eseguire su Core 0)
void ui_task(void *pvParameters);

// Dichiarazioni funzioni creazione schermate (da ui_*.c)
lv_obj_t* ui_main_create(void);
lv_obj_t* ui_calibro_create(void);
lv_obj_t* ui_vetri_create(void);
lv_obj_t* ui_astine_create(void);
lv_obj_t* ui_mode_select_create(void);
lv_obj_t* ui_settings_create(void);
lv_obj_t* ui_rilievi_speciali_create(void);
lv_obj_t* ui_tipologie_create(void);

// Funzioni aggiornamento schermate
void ui_main_update(void);
void ui_calibro_update(void);
void ui_vetri_update(void);
void ui_astine_update(void);
void ui_rilievi_speciali_update(void);
void ui_tipologie_update(void);

#endif // UI_MANAGER_H
