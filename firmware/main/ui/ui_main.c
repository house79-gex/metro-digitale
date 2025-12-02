#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include <stdio.h>

static lv_obj_t *label_mode = NULL;
static lv_obj_t *label_value = NULL;
static lv_obj_t *label_status = NULL;

static void btn_mode_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

static void btn_zero_clicked(lv_event_t *e) {
    encoder_zero();
}

static void btn_settings_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_SETTINGS);
}

lv_obj_t* ui_main_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    // Titolo
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "Metro Digitale");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Modalità corrente
    label_mode = lv_label_create(screen);
    lv_obj_set_style_text_font(label_mode, &lv_font_montserrat_24, 0);
    lv_obj_align(label_mode, LV_ALIGN_TOP_MID, 0, 80);
    
    // Valore misura (grande)
    label_value = lv_label_create(screen);
    lv_obj_add_style(label_value, &style_value_large, 0);
    lv_obj_align(label_value, LV_ALIGN_CENTER, 0, 0);
    
    // Status bar
    label_status = lv_label_create(screen);
    lv_obj_set_style_text_color(label_status, COLOR_TEXT_SECONDARY, 0);
    lv_obj_align(label_status, LV_ALIGN_BOTTOM_MID, 0, -20);
    
    // Pulsanti in basso
    lv_obj_t *btn_container = lv_obj_create(screen);
    lv_obj_set_size(btn_container, 750, 80);
    lv_obj_set_style_bg_opa(btn_container, LV_OPA_TRANSP, 0);
    lv_obj_set_style_border_width(btn_container, 0, 0);
    lv_obj_set_flex_flow(btn_container, LV_FLEX_FLOW_ROW);
    lv_obj_set_flex_align(btn_container, LV_FLEX_ALIGN_SPACE_EVENLY, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    lv_obj_align(btn_container, LV_ALIGN_BOTTOM_MID, 0, -80);
    
    // Pulsante Modalità
    lv_obj_t *btn_mode = lv_btn_create(btn_container);
    lv_obj_set_size(btn_mode, 220, 60);
    lv_obj_add_style(btn_mode, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_mode, btn_mode_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_t *label_btn_mode = lv_label_create(btn_mode);
    lv_label_set_text(label_btn_mode, "Modalità");
    lv_obj_center(label_btn_mode);
    
    // Pulsante Zero
    lv_obj_t *btn_zero = lv_btn_create(btn_container);
    lv_obj_set_size(btn_zero, 220, 60);
    lv_obj_add_style(btn_zero, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_zero, btn_zero_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_t *label_btn_zero = lv_label_create(btn_zero);
    lv_label_set_text(label_btn_zero, "ZERO");
    lv_obj_center(label_btn_zero);
    
    // Pulsante Impostazioni
    lv_obj_t *btn_settings = lv_btn_create(btn_container);
    lv_obj_set_size(btn_settings, 220, 60);
    lv_obj_add_style(btn_settings, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_settings, btn_settings_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_t *label_btn_settings = lv_label_create(btn_settings);
    lv_label_set_text(label_btn_settings, "Impostazioni");
    lv_obj_center(label_btn_settings);
    
    return screen;
}

void ui_main_update(void) {
    // Aggiorna modalità
    const char *mode_str = "Sconosciuta";
    switch (g_config.modalita_corrente) {
        case MODE_FERMAVETRO:
            mode_str = "Modalità: Fermavetro";
            break;
        case MODE_VETRO:
            mode_str = "Modalità: Vetri";
            break;
        case MODE_ASTINA:
            mode_str = "Modalità: Astine";
            break;
        case MODE_CALIBRO:
            mode_str = "Modalità: Calibro";
            break;
    }
    lv_label_set_text(label_mode, mode_str);
    
    // Aggiorna valore misura
    char value_str[32];
    float value_mm = encoder_get_position_mm();
    
    if (g_config.modalita_corrente == MODE_FERMAVETRO) {
        value_mm = encoder_calc_fermavetro_netto(&g_config);
    } else if (g_config.modalita_corrente == MODE_ASTINA) {
        value_mm = encoder_calc_astina_taglio(&g_config, value_mm);
    }
    
    snprintf(value_str, sizeof(value_str), "%.2f mm", value_mm);
    lv_label_set_text(label_value, value_str);
    
    // Aggiorna status
    char status_str[64];
    if (g_state.bt_connected) {
        snprintf(status_str, sizeof(status_str), "🔵 BT Connesso | Zero: %s", 
                 g_state.is_zeroed ? "SI" : "NO");
    } else {
        snprintf(status_str, sizeof(status_str), "⚫ BT Disconnesso | Zero: %s", 
                 g_state.is_zeroed ? "SI" : "NO");
    }
    lv_label_set_text(label_status, status_str);
}
