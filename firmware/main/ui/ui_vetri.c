#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include "bluetooth.h"
#include <stdio.h>

static lv_obj_t *label_larghezza = NULL;
static lv_obj_t *label_altezza = NULL;
static lv_obj_t *label_materiale = NULL;

static void btn_salva_larghezza_clicked(lv_event_t *e) {
    g_state.vetro_larghezza_mm = encoder_get_position_mm();
    g_state.vetro_larghezza_saved = true;
    encoder_zero();
}

static void btn_salva_misura_clicked(lv_event_t *e) {
    if (!g_state.vetro_larghezza_saved) return;
    
    float altezza_raw = encoder_get_position_mm();
    float larghezza_netta = encoder_calc_vetro_netto(&g_config, g_state.vetro_larghezza_mm);
    float altezza_netta = encoder_calc_vetro_netto(&g_config, altezza_raw);
    
    MaterialeConfig *mat = &g_config.materiali[g_config.materiale_corrente_idx];
    
    bluetooth_send_vetro(g_state.vetro_larghezza_mm, altezza_raw,
                         larghezza_netta, altezza_netta,
                         mat->nome, 1, mat->gioco_vetro_mm);
    
    g_state.vetro_larghezza_saved = false;
    encoder_zero();
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MAIN);
}

lv_obj_t* ui_vetri_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "Modalità Vetri");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Card materiale
    lv_obj_t *card_mat = lv_obj_create(screen);
    lv_obj_set_size(card_mat, 700, 80);
    lv_obj_add_style(card_mat, &style_card, 0);
    lv_obj_align(card_mat, LV_ALIGN_TOP_MID, 0, 80);
    
    label_materiale = lv_label_create(card_mat);
    lv_obj_center(label_materiale);
    
    // Larghezza
    label_larghezza = lv_label_create(screen);
    lv_obj_set_style_text_font(label_larghezza, &lv_font_montserrat_32, 0);
    lv_obj_align(label_larghezza, LV_ALIGN_CENTER, 0, -40);
    
    // Altezza
    label_altezza = lv_label_create(screen);
    lv_obj_set_style_text_font(label_altezza, &lv_font_montserrat_32, 0);
    lv_obj_set_style_text_color(label_altezza, COLOR_ACCENT, 0);
    lv_obj_align(label_altezza, LV_ALIGN_CENTER, 0, 20);
    
    // Pulsanti
    lv_obj_t *btn_larghezza = lv_btn_create(screen);
    lv_obj_set_size(btn_larghezza, 300, 60);
    lv_obj_add_style(btn_larghezza, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_larghezza, btn_salva_larghezza_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_larghezza, LV_ALIGN_BOTTOM_LEFT, 50, -100);
    lv_obj_t *lbl = lv_label_create(btn_larghezza);
    lv_label_set_text(lbl, "Salva Larghezza");
    lv_obj_center(lbl);
    
    lv_obj_t *btn_misura = lv_btn_create(screen);
    lv_obj_set_size(btn_misura, 300, 60);
    lv_obj_add_style(btn_misura, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_misura, btn_salva_misura_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_misura, LV_ALIGN_BOTTOM_RIGHT, -50, -100);
    lbl = lv_label_create(btn_misura);
    lv_label_set_text(lbl, "Salva Misura");
    lv_obj_center(lbl);
    
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

void ui_vetri_update(void) {
    MaterialeConfig *mat = &g_config.materiali[g_config.materiale_corrente_idx];
    char str[64];
    snprintf(str, sizeof(str), "Materiale: %s (gioco: %.0fmm)", mat->nome, mat->gioco_vetro_mm);
    lv_label_set_text(label_materiale, str);
    
    if (g_state.vetro_larghezza_saved) {
        snprintf(str, sizeof(str), "L: %.2f mm", g_state.vetro_larghezza_mm);
        lv_label_set_text(label_larghezza, str);
        
        float altezza = encoder_get_position_mm();
        snprintf(str, sizeof(str), "H: %.2f mm", altezza);
        lv_label_set_text(label_altezza, str);
    } else {
        snprintf(str, sizeof(str), "Misura: %.2f mm", encoder_get_position_mm());
        lv_label_set_text(label_larghezza, str);
        lv_label_set_text(label_altezza, "");
    }
}
