#include "screen_vetri_wizard.h"
#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include "esp_log.h"
#include <stdio.h>

static const char *TAG = "SCREEN_VETRI";

// Stato schermata
static struct {
    lv_obj_t *screen;
    lv_obj_t *label_L;
    lv_obj_t *label_H;
    lv_obj_t *label_material;
    uint8_t material_idx;
    float larghezza_mm;
    float altezza_mm;
    bool L_saved;
} g_screen = {0};

// Callback
static void btn_measure_L_clicked(lv_event_t *e) {
    g_screen.larghezza_mm = encoder_get_position_mm();
    g_screen.L_saved = true;
    
    char buf[32];
    snprintf(buf, sizeof(buf), "L: %.2f mm", g_screen.larghezza_mm);
    lv_label_set_text(g_screen.label_L, buf);
    
    ESP_LOGI(TAG, "Larghezza salvata: %.2f mm", g_screen.larghezza_mm);
}

static void btn_measure_H_clicked(lv_event_t *e) {
    g_screen.altezza_mm = encoder_get_position_mm();
    
    char buf[32];
    snprintf(buf, sizeof(buf), "H: %.2f mm", g_screen.altezza_mm);
    lv_label_set_text(g_screen.label_H, buf);
    
    ESP_LOGI(TAG, "Altezza salvata: %.2f mm", g_screen.altezza_mm);
}

static void btn_save_clicked(lv_event_t *e) {
    if (g_screen.L_saved && g_screen.altezza_mm > 0) {
        ESP_LOGI(TAG, "Vetro salvato: L=%.2f H=%.2f", 
                g_screen.larghezza_mm, g_screen.altezza_mm);
        // TODO: Salva su storage
    }
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

void screen_vetri_wizard_create(void) {
    ESP_LOGI(TAG, "Crea schermata wizard vetri");
    
    g_screen.screen = lv_obj_create(NULL);
    lv_obj_add_style(g_screen.screen, &style_screen, 0);
    
    // Titolo
    lv_obj_t *label_title = lv_label_create(g_screen.screen);
    lv_label_set_text(label_title, "VETRI L×H");
    lv_obj_set_style_text_font(label_title, &lv_font_montserrat_28, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 10);
    
    // Materiale
    g_screen.label_material = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_material, "Materiale: Alluminio");
    lv_obj_set_style_text_font(g_screen.label_material, &lv_font_montserrat_18, 0);
    lv_obj_align(g_screen.label_material, LV_ALIGN_TOP_MID, 0, 60);
    
    // Display doppio L e H
    g_screen.label_L = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_L, "L: -- mm");
    lv_obj_set_style_text_font(g_screen.label_L, &lv_font_montserrat_32, 0);
    lv_obj_set_style_text_color(g_screen.label_L, COLOR_PRIMARY, 0);
    lv_obj_align(g_screen.label_L, LV_ALIGN_CENTER, -150, -40);
    
    g_screen.label_H = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_H, "H: -- mm");
    lv_obj_set_style_text_font(g_screen.label_H, &lv_font_montserrat_32, 0);
    lv_obj_set_style_text_color(g_screen.label_H, COLOR_SUCCESS, 0);
    lv_obj_align(g_screen.label_H, LV_ALIGN_CENTER, 150, -40);
    
    // Pulsanti misura
    lv_obj_t *btn_L = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_L, 200, 70);
    lv_obj_add_style(btn_L, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_L, btn_measure_L_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_L, LV_ALIGN_CENTER, -150, 60);
    lv_obj_t *lbl_L = lv_label_create(btn_L);
    lv_label_set_text(lbl_L, "MISURA L");
    lv_obj_center(lbl_L);
    
    lv_obj_t *btn_H = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_H, 200, 70);
    lv_obj_add_style(btn_H, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_H, btn_measure_H_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_H, LV_ALIGN_CENTER, 150, 60);
    lv_obj_t *lbl_H = lv_label_create(btn_H);
    lv_label_set_text(lbl_H, "MISURA H");
    lv_obj_center(lbl_H);
    
    // Pulsante SALVA
    lv_obj_t *btn_save = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_save, 250, 60);
    lv_obj_add_style(btn_save, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_save, btn_save_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_save, LV_ALIGN_BOTTOM_MID, 0, -80);
    lv_obj_t *lbl_save = lv_label_create(btn_save);
    lv_label_set_text(lbl_save, "SALVA");
    lv_obj_set_style_text_font(lbl_save, &lv_font_montserrat_24, 0);
    lv_obj_center(lbl_save);
    
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
    
    g_screen.material_idx = 0;
    g_screen.L_saved = false;
    
    ESP_LOGI(TAG, "Schermata vetri wizard creata");
}

void screen_vetri_wizard_update(void) {
    // Aggiorna display in real-time se necessario
}

void screen_vetri_set_material(uint8_t material_idx) {
    g_screen.material_idx = material_idx;
    ESP_LOGI(TAG, "Materiale impostato: %d", material_idx);
}
