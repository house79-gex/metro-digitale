#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include <stdio.h>

static lv_obj_t *label_value = NULL;

static void btn_zero_clicked(lv_event_t *e) {
    encoder_zero();
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

lv_obj_t* ui_calibro_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    // Titolo minimale
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "CALIBRO");
    lv_obj_set_style_text_font(label_title, &lv_font_montserrat_28, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Valore MOLTO grande
    label_value = lv_label_create(screen);
    lv_obj_set_style_text_font(label_value, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(label_value, COLOR_SUCCESS, 0);
    lv_obj_align(label_value, LV_ALIGN_CENTER, 0, 0);
    
    // Pulsante ZERO grande
    lv_obj_t *btn_zero = lv_btn_create(screen);
    lv_obj_set_size(btn_zero, 300, 80);
    lv_obj_add_style(btn_zero, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_zero, btn_zero_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_zero, LV_ALIGN_BOTTOM_MID, 0, -120);
    lv_obj_t *label_btn_zero = lv_label_create(btn_zero);
    lv_label_set_text(label_btn_zero, "ZERO");
    lv_obj_set_style_text_font(label_btn_zero, &lv_font_montserrat_32, 0);
    lv_obj_center(label_btn_zero);
    
    // Pulsante Back piccolo
    lv_obj_t *btn_back = lv_btn_create(screen);
    lv_obj_set_size(btn_back, 150, 50);
    lv_obj_add_style(btn_back, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_back, btn_back_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_MID, 0, -40);
    lv_obj_t *label_btn_back = lv_label_create(btn_back);
    lv_label_set_text(label_btn_back, "Indietro");
    lv_obj_center(label_btn_back);
    
    return screen;
}

void ui_calibro_update(void) {
    char value_str[32];
    float value_mm = encoder_get_position_mm();
    snprintf(value_str, sizeof(value_str), "%.2f mm", value_mm);
    lv_label_set_text(label_value, value_str);
}
