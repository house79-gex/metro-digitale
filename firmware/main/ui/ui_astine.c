#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include <stdio.h>

static lv_obj_t *label_value = NULL;
static lv_obj_t *label_astina = NULL;
static lv_obj_t *label_gruppo = NULL;

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MAIN);
}

static void btn_next_astina_clicked(lv_event_t *e) {
    if (g_config.astina_corrente_idx < g_config.num_astine - 1) {
        g_config.astina_corrente_idx++;
    } else {
        g_config.astina_corrente_idx = 0;
    }
}

static void btn_prev_astina_clicked(lv_event_t *e) {
    if (g_config.astina_corrente_idx > 0) {
        g_config.astina_corrente_idx--;
    } else {
        g_config.astina_corrente_idx = g_config.num_astine - 1;
    }
}

lv_obj_t* ui_astine_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "Modalità Astine");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Card gruppo
    lv_obj_t *card_gruppo = lv_obj_create(screen);
    lv_obj_set_size(card_gruppo, 700, 60);
    lv_obj_add_style(card_gruppo, &style_card, 0);
    lv_obj_align(card_gruppo, LV_ALIGN_TOP_MID, 0, 80);
    
    label_gruppo = lv_label_create(card_gruppo);
    lv_obj_center(label_gruppo);
    
    // Nome astina
    label_astina = lv_label_create(screen);
    lv_obj_set_style_text_font(label_astina, &lv_font_montserrat_28, 0);
    lv_obj_align(label_astina, LV_ALIGN_CENTER, 0, -60);
    
    // Valore misura
    label_value = lv_label_create(screen);
    lv_obj_add_style(label_value, &style_value_large, 0);
    lv_obj_align(label_value, LV_ALIGN_CENTER, 0, 20);
    
    // Pulsanti navigazione
    lv_obj_t *btn_prev = lv_btn_create(screen);
    lv_obj_set_size(btn_prev, 150, 60);
    lv_obj_add_style(btn_prev, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_prev, btn_prev_astina_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_prev, LV_ALIGN_BOTTOM_LEFT, 50, -100);
    lv_obj_t *lbl = lv_label_create(btn_prev);
    lv_label_set_text(lbl, "< Prec");
    lv_obj_center(lbl);
    
    lv_obj_t *btn_next = lv_btn_create(screen);
    lv_obj_set_size(btn_next, 150, 60);
    lv_obj_add_style(btn_next, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_next, btn_next_astina_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_next, LV_ALIGN_BOTTOM_RIGHT, -50, -100);
    lbl = lv_label_create(btn_next);
    lv_label_set_text(lbl, "Succ >");
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

void ui_astine_update(void) {
    if (g_config.num_astine == 0) {
        lv_label_set_text(label_astina, "Nessuna astina configurata");
        lv_label_set_text(label_value, "---");
        lv_label_set_text(label_gruppo, "");
        return;
    }
    
    AstinaConfig *astina = &g_config.astine[g_config.astina_corrente_idx];
    AstinaGruppo *gruppo = &g_config.gruppi_astine[astina->gruppo_idx];
    
    lv_label_set_text(label_astina, astina->nome);
    lv_label_set_text(label_gruppo, gruppo->nome);
    
    float raw_mm = encoder_get_position_mm();
    float taglio_mm = encoder_calc_astina_taglio(&g_config, raw_mm);
    
    char value_str[64];
    snprintf(value_str, sizeof(value_str), "%.2f mm\n(offset: %.1f)", taglio_mm, astina->offset_mm);
    lv_label_set_text(label_value, value_str);
}
