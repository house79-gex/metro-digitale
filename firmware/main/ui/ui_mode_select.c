#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"

static void btn_fermavetro_clicked(lv_event_t *e) {
    g_config.modalita_corrente = MODE_FERMAVETRO;
    ui_manager_show_screen(UI_SCREEN_MAIN);
}

static void btn_vetri_clicked(lv_event_t *e) {
    g_config.modalita_corrente = MODE_VETRO;
    ui_manager_show_screen(UI_SCREEN_VETRI);
}

static void btn_rilievi_speciali_clicked(lv_event_t *e) {
    g_config.modalita_corrente = MODE_RILIEVI_SPECIALI;
    ui_manager_show_screen(UI_SCREEN_RILIEVI_SPECIALI);
}

static void btn_calibro_clicked(lv_event_t *e) {
    g_config.modalita_corrente = MODE_CALIBRO;
    ui_manager_show_screen(UI_SCREEN_CALIBRO);
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MAIN);
}

lv_obj_t* ui_mode_select_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "Seleziona Modalità");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 30);
    
    // Container per pulsanti modalità
    lv_obj_t *container = lv_obj_create(screen);
    lv_obj_set_size(container, 700, 350);
    lv_obj_set_style_bg_opa(container, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(container, 0, 0);
    lv_obj_set_flex_flow(container, LV_FLEX_FLOW_ROW_WRAP);
    lv_obj_set_flex_align(container, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_align(container, LV_ALIGN_CENTER, 0, 0);
    
    // Pulsante Fermavetro
    lv_obj_t *btn_fermavetro = lv_btn_create(container);
    lv_obj_set_size(btn_fermavetro, 320, 150);
    lv_obj_add_style(btn_fermavetro, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_fermavetro, btn_fermavetro_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_t *lbl = lv_label_create(btn_fermavetro);
    lv_label_set_text(lbl, "Fermavetro");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_24, 0);
    lv_obj_center(lbl);
    
    // Pulsante Vetri
    lv_obj_t *btn_vetri = lv_btn_create(container);
    lv_obj_set_size(btn_vetri, 320, 150);
    lv_obj_add_style(btn_vetri, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_vetri, btn_vetri_clicked, LV_EVENT_CLICKED, NULL);
    lbl = lv_label_create(btn_vetri);
    lv_label_set_text(lbl, "Vetri");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_24, 0);
    lv_obj_center(lbl);
    
    // Pulsante Rilievi Speciali
    lv_obj_t *btn_rilievi = lv_btn_create(container);
    lv_obj_set_size(btn_rilievi, 320, 150);
    lv_obj_add_style(btn_rilievi, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_rilievi, btn_rilievi_speciali_clicked, LV_EVENT_CLICKED, NULL);
    lbl = lv_label_create(btn_rilievi);
    lv_label_set_text(lbl, "📐 Rilievi Speciali");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_24, 0);
    lv_obj_center(lbl);
    
    // Pulsante Calibro
    lv_obj_t *btn_calibro = lv_btn_create(container);
    lv_obj_set_size(btn_calibro, 320, 150);
    lv_obj_add_style(btn_calibro, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_calibro, btn_calibro_clicked, LV_EVENT_CLICKED, NULL);
    lbl = lv_label_create(btn_calibro);
    lv_label_set_text(lbl, "Calibro");
    lv_obj_set_style_text_font(lbl, &lv_font_montserrat_24, 0);
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
