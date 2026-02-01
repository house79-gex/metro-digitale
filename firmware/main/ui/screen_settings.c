#include "screen_settings.h"
#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "display/display_rgb.h"
#include "hardware/buzzer.h"
#include "esp_log.h"
#include <stdio.h>

static const char *TAG = "SCREEN_SETTINGS";

// Stato schermata
static struct {
    lv_obj_t *screen;
    lv_obj_t *label_storage;
    lv_obj_t *label_battery;
    lv_obj_t *slider_brightness;
    lv_obj_t *slider_volume;
} g_screen = {0};

static void slider_brightness_changed(lv_event_t *e) {
    lv_obj_t *slider = lv_event_get_target(e);
    int32_t value = lv_slider_get_value(slider);
    
    display_backlight_set((uint8_t)value);
    
    ESP_LOGI(TAG, "Luminosità: %d%%", (int)value);
}

static void slider_volume_changed(lv_event_t *e) {
    lv_obj_t *slider = lv_event_get_target(e);
    int32_t value = lv_slider_get_value(slider);
    
    // TODO: Imposta volume buzzer
    
    ESP_LOGI(TAG, "Volume: %d%%", (int)value);
}

static void btn_test_buzzer_clicked(lv_event_t *e) {
    buzzer_beep(1000, 200); // 1000Hz per 200ms
    ESP_LOGI(TAG, "Test buzzer");
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

void screen_settings_create(void) {
    ESP_LOGI(TAG, "Crea schermata impostazioni");
    
    g_screen.screen = lv_obj_create(NULL);
    lv_obj_add_style(g_screen.screen, &style_screen, 0);
    
    // Titolo
    lv_obj_t *label_title = lv_label_create(g_screen.screen);
    lv_label_set_text(label_title, "IMPOSTAZIONI");
    lv_obj_set_style_text_font(label_title, &lv_font_montserrat_28, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 10);
    
    // Panel Storage
    lv_obj_t *panel_storage = lv_obj_create(g_screen.screen);
    lv_obj_set_size(panel_storage, 350, 120);
    lv_obj_align(panel_storage, LV_ALIGN_TOP_LEFT, 20, 60);
    
    lv_obj_t *label_storage_title = lv_label_create(panel_storage);
    lv_label_set_text(label_storage_title, "STORAGE");
    lv_obj_set_style_text_font(label_storage_title, &lv_font_montserrat_18, 0);
    lv_obj_align(label_storage_title, LV_ALIGN_TOP_LEFT, 10, 5);
    
    g_screen.label_storage = lv_label_create(panel_storage);
    lv_label_set_text(g_screen.label_storage, "SD: OK\nBLE: Connesso\nUSB: Non presente");
    lv_obj_set_style_text_font(g_screen.label_storage, &lv_font_montserrat_14, 0);
    lv_obj_align(g_screen.label_storage, LV_ALIGN_TOP_LEFT, 10, 35);
    
    // Panel Batteria
    lv_obj_t *panel_battery = lv_obj_create(g_screen.screen);
    lv_obj_set_size(panel_battery, 350, 120);
    lv_obj_align(panel_battery, LV_ALIGN_TOP_RIGHT, -20, 60);
    
    lv_obj_t *label_battery_title = lv_label_create(panel_battery);
    lv_label_set_text(label_battery_title, "BATTERIA");
    lv_obj_set_style_text_font(label_battery_title, &lv_font_montserrat_18, 0);
    lv_obj_align(label_battery_title, LV_ALIGN_TOP_LEFT, 10, 5);
    
    g_screen.label_battery = lv_label_create(panel_battery);
    lv_label_set_text(g_screen.label_battery, "Livello: 85%\nVoltaggio: 3.9V\nAutonomia: 8h");
    lv_obj_set_style_text_font(g_screen.label_battery, &lv_font_montserrat_14, 0);
    lv_obj_align(g_screen.label_battery, LV_ALIGN_TOP_LEFT, 10, 35);
    
    // Panel Display
    lv_obj_t *panel_display = lv_obj_create(g_screen.screen);
    lv_obj_set_size(panel_display, 350, 150);
    lv_obj_align(panel_display, LV_ALIGN_TOP_LEFT, 20, 200);
    
    lv_obj_t *label_display_title = lv_label_create(panel_display);
    lv_label_set_text(label_display_title, "DISPLAY");
    lv_obj_set_style_text_font(label_display_title, &lv_font_montserrat_18, 0);
    lv_obj_align(label_display_title, LV_ALIGN_TOP_LEFT, 10, 5);
    
    lv_obj_t *label_brightness = lv_label_create(panel_display);
    lv_label_set_text(label_brightness, "Luminosità:");
    lv_obj_align(label_brightness, LV_ALIGN_TOP_LEFT, 10, 40);
    
    g_screen.slider_brightness = lv_slider_create(panel_display);
    lv_obj_set_width(g_screen.slider_brightness, 250);
    lv_slider_set_range(g_screen.slider_brightness, 10, 100);
    lv_slider_set_value(g_screen.slider_brightness, display_backlight_get(), LV_ANIM_OFF);
    lv_obj_add_event_cb(g_screen.slider_brightness, slider_brightness_changed, LV_EVENT_VALUE_CHANGED, NULL);
    lv_obj_align(label_brightness, LV_ALIGN_TOP_LEFT, 10, 70);
    lv_obj_align_to(g_screen.slider_brightness, label_brightness, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 10);
    
    // Panel Buzzer
    lv_obj_t *panel_buzzer = lv_obj_create(g_screen.screen);
    lv_obj_set_size(panel_buzzer, 350, 150);
    lv_obj_align(panel_buzzer, LV_ALIGN_TOP_RIGHT, -20, 200);
    
    lv_obj_t *label_buzzer_title = lv_label_create(panel_buzzer);
    lv_label_set_text(label_buzzer_title, "BUZZER");
    lv_obj_set_style_text_font(label_buzzer_title, &lv_font_montserrat_18, 0);
    lv_obj_align(label_buzzer_title, LV_ALIGN_TOP_LEFT, 10, 5);
    
    lv_obj_t *label_volume = lv_label_create(panel_buzzer);
    lv_label_set_text(label_volume, "Volume:");
    lv_obj_align(label_volume, LV_ALIGN_TOP_LEFT, 10, 40);
    
    g_screen.slider_volume = lv_slider_create(panel_buzzer);
    lv_obj_set_width(g_screen.slider_volume, 180);
    lv_slider_set_range(g_screen.slider_volume, 0, 100);
    lv_slider_set_value(g_screen.slider_volume, 80, LV_ANIM_OFF);
    lv_obj_add_event_cb(g_screen.slider_volume, slider_volume_changed, LV_EVENT_VALUE_CHANGED, NULL);
    lv_obj_align_to(g_screen.slider_volume, label_volume, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 10);
    
    lv_obj_t *btn_test = lv_btn_create(panel_buzzer);
    lv_obj_set_size(btn_test, 120, 40);
    lv_obj_add_style(btn_test, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_test, btn_test_buzzer_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_test, LV_ALIGN_BOTTOM_RIGHT, -10, -10);
    lv_obj_t *lbl_test = lv_label_create(btn_test);
    lv_label_set_text(lbl_test, "TEST");
    lv_obj_center(lbl_test);
    
    // Versione firmware footer
    lv_obj_t *label_version = lv_label_create(g_screen.screen);
    lv_label_set_text(label_version, "Metro Digitale v2.0 - Firmware Build 2026.02");
    lv_obj_set_style_text_font(label_version, &lv_font_montserrat_12, 0);
    lv_obj_align(label_version, LV_ALIGN_BOTTOM_MID, 0, -80);
    
    // Pulsante Back
    lv_obj_t *btn_back = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_back, 150, 50);
    lv_obj_add_style(btn_back, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_back, btn_back_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_MID, 0, -10);
    lv_obj_t *lbl_back = lv_label_create(btn_back);
    lv_label_set_text(lbl_back, "INDIETRO");
    lv_obj_center(lbl_back);
    
    lv_scr_load(g_screen.screen);
    
    ESP_LOGI(TAG, "Schermata impostazioni creata");
}

void screen_settings_update(void) {
    // Aggiorna valori in real-time se necessario
}
