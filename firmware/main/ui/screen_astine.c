#include "screen_astine.h"
#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include "esp_log.h"
#include <stdio.h>

static const char *TAG = "SCREEN_ASTINE";

// Stato schermata
static struct {
    lv_obj_t *screen;
    lv_obj_t *label_grezza;
    lv_obj_t *label_taglio;
    lv_obj_t *tabview;
    uint8_t current_group;
    uint8_t current_astina;
} g_screen = {0};

static void btn_measure_clicked(lv_event_t *e) {
    float value = encoder_get_position_mm();
    
    char buf[32];
    snprintf(buf, sizeof(buf), "Grezza: %.2f mm", value);
    lv_label_set_text(g_screen.label_grezza, buf);
    
    // Calcola taglio con offset (esempio: -3mm)
    float taglio = value - 3.0f;
    snprintf(buf, sizeof(buf), "Taglio: %.2f mm", taglio);
    lv_label_set_text(g_screen.label_taglio, buf);
    
    ESP_LOGI(TAG, "Astina misurata: %.2f mm → %.2f mm", value, taglio);
}

static void btn_save_clicked(lv_event_t *e) {
    ESP_LOGI(TAG, "Astina salvata");
    // TODO: Salva su storage
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

void screen_astine_create(void) {
    ESP_LOGI(TAG, "Crea schermata astine");
    
    g_screen.screen = lv_obj_create(NULL);
    lv_obj_add_style(g_screen.screen, &style_screen, 0);
    
    // Titolo
    lv_obj_t *label_title = lv_label_create(g_screen.screen);
    lv_label_set_text(label_title, "ASTINE");
    lv_obj_set_style_text_font(label_title, &lv_font_montserrat_28, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 10);
    
    // Tabs gruppi (semplificato - 3 gruppi)
    g_screen.tabview = lv_tabview_create(g_screen.screen, LV_DIR_TOP, 50);
    lv_obj_set_size(g_screen.tabview, 780, 150);
    lv_obj_align(g_screen.tabview, LV_ALIGN_TOP_MID, 0, 50);
    
    lv_obj_t *tab1 = lv_tabview_add_tab(g_screen.tabview, "Anta Ribalta");
    lv_obj_t *tab2 = lv_tabview_add_tab(g_screen.tabview, "Persiana");
    lv_obj_t *tab3 = lv_tabview_add_tab(g_screen.tabview, "Cremonese");
    
    // Display doppio: Grezza → Taglio
    g_screen.label_grezza = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_grezza, "Grezza: -- mm");
    lv_obj_set_style_text_font(g_screen.label_grezza, &lv_font_montserrat_32, 0);
    lv_obj_set_style_text_color(g_screen.label_grezza, COLOR_PRIMARY, 0);
    lv_obj_align(g_screen.label_grezza, LV_ALIGN_CENTER, -150, 0);
    
    // Freccia
    lv_obj_t *label_arrow = lv_label_create(g_screen.screen);
    lv_label_set_text(label_arrow, "→");
    lv_obj_set_style_text_font(label_arrow, &lv_font_montserrat_48, 0);
    lv_obj_align(label_arrow, LV_ALIGN_CENTER, 0, 0);
    
    g_screen.label_taglio = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_taglio, "Taglio: -- mm");
    lv_obj_set_style_text_font(g_screen.label_taglio, &lv_font_montserrat_32, 0);
    lv_obj_set_style_text_color(g_screen.label_taglio, COLOR_SUCCESS, 0);
    lv_obj_align(g_screen.label_taglio, LV_ALIGN_CENTER, 150, 0);
    
    // Pulsanti
    lv_obj_t *btn_measure = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_measure, 200, 70);
    lv_obj_add_style(btn_measure, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_measure, btn_measure_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_measure, LV_ALIGN_BOTTOM_MID, -120, -80);
    lv_obj_t *lbl_measure = lv_label_create(btn_measure);
    lv_label_set_text(lbl_measure, "MISURA");
    lv_obj_set_style_text_font(lbl_measure, &lv_font_montserrat_24, 0);
    lv_obj_center(lbl_measure);
    
    lv_obj_t *btn_save = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_save, 200, 70);
    lv_obj_add_style(btn_save, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_save, btn_save_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_save, LV_ALIGN_BOTTOM_MID, 120, -80);
    lv_obj_t *lbl_save = lv_label_create(btn_save);
    lv_label_set_text(lbl_save, "SALVA");
    lv_obj_set_style_text_font(lbl_save, &lv_font_montserrat_24, 0);
    lv_obj_center(lbl_save);
    
    lv_obj_t *btn_back = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_back, 150, 50);
    lv_obj_add_style(btn_back, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_back, btn_back_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_MID, 0, -10);
    lv_obj_t *lbl_back = lv_label_create(btn_back);
    lv_label_set_text(lbl_back, "INDIETRO");
    lv_obj_center(lbl_back);
    
    lv_scr_load(g_screen.screen);
    
    g_screen.current_group = 0;
    
    ESP_LOGI(TAG, "Schermata astine creata");
}

void screen_astine_update(void) {
    // Aggiorna display in real-time se necessario
}

void screen_astine_select_group(uint8_t group_idx) {
    g_screen.current_group = group_idx;
    lv_tabview_set_act(g_screen.tabview, group_idx, LV_ANIM_ON);
    ESP_LOGI(TAG, "Gruppo selezionato: %d", group_idx);
}
