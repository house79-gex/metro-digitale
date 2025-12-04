#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"

static void btn_astine_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_ASTINE);
}

static void btn_tipologie_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_TIPOLOGIE);
}

static void btn_fermavetri_clicked(lv_event_t *e) {
    g_config.modalita_corrente = MODE_FERMAVETRO;
    ui_manager_show_screen(UI_SCREEN_MAIN);
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

lv_obj_t* ui_rilievi_speciali_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "📐 RILIEVI SPECIALI");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Container per pulsanti menu
    lv_obj_t *container = lv_obj_create(screen);
    lv_obj_set_size(container, 700, 350);
    lv_obj_set_style_bg_opa(container, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(container, 0, 0);
    lv_obj_set_flex_flow(container, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(container, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_align(container, LV_ALIGN_CENTER, 0, 0);
    
    // Pulsante ASTINE
    lv_obj_t *btn_astine = lv_btn_create(container);
    lv_obj_set_size(btn_astine, 600, 70);
    lv_obj_add_style(btn_astine, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_astine, btn_astine_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_t *lbl = lv_label_create(btn_astine);
    lv_label_set_text(lbl, "🔩 ASTINE\nAnta Ribalta | Persiana | Cremonese");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_20, 0);
    lv_obj_center(lbl);
    
    // Pulsante TIPOLOGIE INFISSO
    lv_obj_t *btn_tipologie = lv_btn_create(container);
    lv_obj_set_size(btn_tipologie, 600, 70);
    lv_obj_add_style(btn_tipologie, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_tipologie, btn_tipologie_clicked, LV_EVENT_CLICKED, NULL);
    lbl = lv_label_create(btn_tipologie);
    lv_label_set_text(lbl, "🪟 TIPOLOGIE INFISSO\nCon formule e calcoli automatici");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_20, 0);
    lv_obj_center(lbl);
    
    // Pulsante FERMAVETRI
    lv_obj_t *btn_fermavetri = lv_btn_create(container);
    lv_obj_set_size(btn_fermavetri, 600, 70);
    lv_obj_add_style(btn_fermavetri, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_fermavetri, btn_fermavetri_clicked, LV_EVENT_CLICKED, NULL);
    lbl = lv_label_create(btn_fermavetri);
    lv_label_set_text(lbl, "🔲 FERMAVETRI\nCon offset battute per materiale");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_20, 0);
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

void ui_rilievi_speciali_update(void) {
    // No dynamic updates needed for this menu screen
}
