#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"

static void btn_save_clicked(lv_event_t *e) {
    config_save_to_nvs(&g_config);
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MAIN);
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
    lv_obj_align(label_info, LV_ALIGN_CENTER, 0, -50);
    
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
