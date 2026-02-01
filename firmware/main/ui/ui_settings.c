#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "../hardware/buzzer.h"

// Static label for volume display
static lv_obj_t *label_volume_value = NULL;

static void btn_save_clicked(lv_event_t *e) {
    config_save_to_nvs(&g_config);
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MAIN);
}

// Event handler slider volume
static void slider_volume_changed(lv_event_t *e) {
    lv_obj_t *slider = lv_event_get_target(e);
    int32_t value = lv_slider_get_value(slider);
    
    // Aggiorna volume buzzer
    buzzer_set_volume((uint8_t)value);
    
    // Aggiorna label
    if (label_volume_value != NULL) {
        char buf[8];
        snprintf(buf, sizeof(buf), "%d%%", (int)value);
        lv_label_set_text(label_volume_value, buf);
    }
    
    // Feedback immediato
    buzzer_play_tone(NOTE_C5, 50);
}

// Event handler pulsante test
static void btn_test_buzzer_clicked(lv_event_t *e) {
    // Esegui test di tutti i pattern
    buzzer_test_all_patterns();
}

lv_obj_t* ui_settings_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "Impostazioni");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Placeholder per impostazioni
    lv_obj_t *label_info = lv_label_create(screen);
    lv_label_set_text(label_info, "Configurazione puntali, materiali,\nastine e parametri Bluetooth");
    lv_obj_set_style_text_align(label_info, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_align(label_info, LV_ALIGN_CENTER, 0, -150);
    
    // === PANEL BUZZER ===
    lv_obj_t *panel_buzzer = lv_obj_create(screen);
    lv_obj_set_size(panel_buzzer, 700, 80);
    lv_obj_align(panel_buzzer, LV_ALIGN_CENTER, 0, -30);
    lv_obj_set_style_bg_color(panel_buzzer, lv_color_hex(0x1a1a2e), 0);
    lv_obj_set_style_border_width(panel_buzzer, 1, 0);
    lv_obj_set_style_border_color(panel_buzzer, lv_color_hex(0x333333), 0);
    lv_obj_set_style_radius(panel_buzzer, 10, 0);
    
    // Titolo buzzer
    lv_obj_t *label_buzzer_title = lv_label_create(panel_buzzer);
    lv_label_set_text(label_buzzer_title, LV_SYMBOL_VOLUME_MAX " Buzzer");
    lv_obj_set_style_text_font(label_buzzer_title, &lv_font_montserrat_18, 0);
    lv_obj_set_style_text_color(label_buzzer_title, lv_color_hex(0xffffff), 0);
    lv_obj_set_pos(label_buzzer_title, 15, 15);
    
    // Slider volume
    lv_obj_t *slider_volume = lv_slider_create(panel_buzzer);
    lv_obj_set_width(slider_volume, 350);
    lv_obj_align(slider_volume, LV_ALIGN_LEFT_MID, 150, 0);
    lv_slider_set_range(slider_volume, 0, 100);
    lv_slider_set_value(slider_volume, 50, LV_ANIM_OFF);
    lv_obj_add_event_cb(slider_volume, slider_volume_changed, LV_EVENT_VALUE_CHANGED, NULL);
    
    // Label valore volume
    label_volume_value = lv_label_create(panel_buzzer);
    lv_label_set_text(label_volume_value, "50%");
    lv_obj_align(label_volume_value, LV_ALIGN_LEFT_MID, 520, 0);
    lv_obj_set_style_text_color(label_volume_value, lv_color_hex(0x00ff88), 0);
    lv_obj_set_style_text_font(label_volume_value, &lv_font_montserrat_16, 0);
    
    // Pulsante test
    lv_obj_t *btn_test = lv_btn_create(panel_buzzer);
    lv_obj_set_size(btn_test, 100, 50);
    lv_obj_align(btn_test, LV_ALIGN_RIGHT_MID, -10, 0);
    lv_obj_set_style_bg_color(btn_test, lv_color_hex(0x00aaff), 0);
    lv_obj_add_event_cb(btn_test, btn_test_buzzer_clicked, LV_EVENT_CLICKED, NULL);
    
    lv_obj_t *label_test = lv_label_create(btn_test);
    lv_label_set_text(label_test, LV_SYMBOL_AUDIO " Test");
    lv_obj_set_style_text_font(label_test, &lv_font_montserrat_16, 0);
    lv_obj_center(label_test);
    
    // Pulsante Salva
    lv_obj_t *btn_save = lv_btn_create(screen);
    lv_obj_set_size(btn_save, 250, 60);
    lv_obj_add_style(btn_save, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_save, btn_save_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_save, LV_ALIGN_CENTER, 0, 50);
    lv_obj_t *lbl = lv_label_create(btn_save);
    lv_label_set_text(lbl, "Salva Configurazione");
    lv_obj_center(lbl);
    
    // Pulsante Back
    lv_obj_t *btn_back = lv_btn_create(screen);
    lv_obj_set_size(btn_back, 200, 50);
    lv_obj_add_style(btn_back, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_back, btn_back_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_MID, 0, -30);
    lbl = lv_label_create(btn_back);
    lv_label_set_text(lbl, "Indietro");
    lv_obj_center(lbl);
    
    return screen;
}
