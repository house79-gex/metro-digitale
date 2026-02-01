#include "screen_calibro_advanced.h"
#include "ui_manager.h"
#include "ui_styles.h"
#include "wizard_zero.h"
#include "encoder.h"
#include "esp_log.h"
#include <stdio.h>
#include <math.h>

static const char *TAG = "SCREEN_CALIBRO_ADV";

// Stato schermata
static struct {
    lv_obj_t *screen;
    lv_obj_t *label_value;
    lv_obj_t *label_unit;
    lv_obj_t *label_type;
    lv_obj_t *panel_stats;
    lv_obj_t *label_stats;
    
    float current_value;
    bool stats_visible;
    
    // Statistiche
    float min_value;
    float max_value;
    float sum_values;
    float sum_squared;
    uint32_t count;
    bool hold_active;
} g_screen = {0};

// Callback pulsanti
static void btn_zero_clicked(lv_event_t *e) {
    wizard_zero_show();
}

static void btn_hold_clicked(lv_event_t *e) {
    g_screen.hold_active = !g_screen.hold_active;
    ESP_LOGI(TAG, "Hold: %s", g_screen.hold_active ? "ON" : "OFF");
}

static void btn_stats_clicked(lv_event_t *e) {
    screen_calibro_toggle_stats(!g_screen.stats_visible);
}

static void btn_reset_clicked(lv_event_t *e) {
    screen_calibro_reset_stats();
}

static void btn_back_clicked(lv_event_t *e) {
    ui_manager_show_screen(UI_SCREEN_MODE_SELECT);
}

void screen_calibro_advanced_create(void) {
    ESP_LOGI(TAG, "Crea schermata calibro avanzata");
    
    // Crea screen
    g_screen.screen = lv_obj_create(NULL);
    lv_obj_add_style(g_screen.screen, &style_screen, 0);
    
    // Titolo
    lv_obj_t *label_title = lv_label_create(g_screen.screen);
    lv_label_set_text(label_title, "CALIBRO DIGITALE");
    lv_obj_set_style_text_font(label_title, &lv_font_montserrat_24, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 10);
    
    // Valore principale GRANDE (48px verde)
    g_screen.label_value = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_value, "0.00");
    lv_obj_set_style_text_font(g_screen.label_value, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(g_screen.label_value, COLOR_SUCCESS, 0);
    lv_obj_align(g_screen.label_value, LV_ALIGN_CENTER, 0, -40);
    
    // Unità di misura
    g_screen.label_unit = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_unit, "mm");
    lv_obj_set_style_text_font(g_screen.label_unit, &lv_font_montserrat_20, 0);
    lv_obj_align_to(g_screen.label_unit, g_screen.label_value, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
    
    // Tipo misura
    g_screen.label_type = lv_label_create(g_screen.screen);
    lv_label_set_text(g_screen.label_type, "Esterna");
    lv_obj_set_style_text_font(g_screen.label_type, &lv_font_montserrat_18, 0);
    lv_obj_align(g_screen.label_type, LV_ALIGN_CENTER, 0, 40);
    
    // Pulsanti 4x in riga
    int btn_width = 150;
    int btn_spacing = 20;
    int total_width = 4 * btn_width + 3 * btn_spacing;
    int start_x = -total_width / 2;
    
    // ZERO
    lv_obj_t *btn_zero = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_zero, btn_width, 60);
    lv_obj_add_style(btn_zero, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_zero, btn_zero_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_zero, LV_ALIGN_BOTTOM_MID, start_x + btn_width/2, -80);
    lv_obj_t *lbl_zero = lv_label_create(btn_zero);
    lv_label_set_text(lbl_zero, "ZERO");
    lv_obj_center(lbl_zero);
    
    // HOLD
    lv_obj_t *btn_hold = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_hold, btn_width, 60);
    lv_obj_add_style(btn_hold, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_hold, btn_hold_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_hold, LV_ALIGN_BOTTOM_MID, start_x + btn_width*3/2 + btn_spacing, -80);
    lv_obj_t *lbl_hold = lv_label_create(btn_hold);
    lv_label_set_text(lbl_hold, "HOLD");
    lv_obj_center(lbl_hold);
    
    // STATS
    lv_obj_t *btn_stats = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_stats, btn_width, 60);
    lv_obj_add_style(btn_stats, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_stats, btn_stats_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_stats, LV_ALIGN_BOTTOM_MID, start_x + btn_width*5/2 + btn_spacing*2, -80);
    lv_obj_t *lbl_stats = lv_label_create(btn_stats);
    lv_label_set_text(lbl_stats, "STATS");
    lv_obj_center(lbl_stats);
    
    // RESET
    lv_obj_t *btn_reset = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_reset, btn_width, 60);
    lv_obj_add_style(btn_reset, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_reset, btn_reset_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_reset, LV_ALIGN_BOTTOM_MID, start_x + btn_width*7/2 + btn_spacing*3, -80);
    lv_obj_t *lbl_reset = lv_label_create(btn_reset);
    lv_label_set_text(lbl_reset, "RESET");
    lv_obj_center(lbl_reset);
    
    // Pulsante Back
    lv_obj_t *btn_back = lv_btn_create(g_screen.screen);
    lv_obj_set_size(btn_back, 150, 50);
    lv_obj_add_style(btn_back, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_back, btn_back_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_MID, 0, -10);
    lv_obj_t *lbl_back = lv_label_create(btn_back);
    lv_label_set_text(lbl_back, "INDIETRO");
    lv_obj_center(lbl_back);
    
    // Panel statistiche (inizialmente nascosto)
    g_screen.panel_stats = lv_obj_create(g_screen.screen);
    lv_obj_set_size(g_screen.panel_stats, 350, 200);
    lv_obj_align(g_screen.panel_stats, LV_ALIGN_TOP_RIGHT, -10, 50);
    lv_obj_add_flag(g_screen.panel_stats, LV_OBJ_FLAG_HIDDEN);
    
    g_screen.label_stats = lv_label_create(g_screen.panel_stats);
    lv_label_set_text(g_screen.label_stats, "STATISTICHE\n\nMin: -\nMax: -\nAvg: -\nCount: 0");
    lv_obj_set_style_text_font(g_screen.label_stats, &lv_font_montserrat_16, 0);
    lv_obj_align(g_screen.label_stats, LV_ALIGN_TOP_LEFT, 10, 10);
    
    // Mostra screen
    lv_scr_load(g_screen.screen);
    
    // Reset statistiche
    screen_calibro_reset_stats();
    
    ESP_LOGI(TAG, "Schermata calibro avanzata creata");
}

void screen_calibro_update_value(float value_mm) {
    if (!g_screen.screen || g_screen.hold_active) {
        return;
    }
    
    g_screen.current_value = value_mm;
    
    // Aggiorna label valore
    char buf[32];
    snprintf(buf, sizeof(buf), "%.2f", value_mm);
    lv_label_set_text(g_screen.label_value, buf);
    
    // Aggiorna statistiche
    if (g_screen.count == 0) {
        g_screen.min_value = value_mm;
        g_screen.max_value = value_mm;
    } else {
        if (value_mm < g_screen.min_value) g_screen.min_value = value_mm;
        if (value_mm > g_screen.max_value) g_screen.max_value = value_mm;
    }
    
    g_screen.sum_values += value_mm;
    g_screen.sum_squared += value_mm * value_mm;
    g_screen.count++;
    
    // Aggiorna display statistiche se visibile
    if (g_screen.stats_visible) {
        float avg = g_screen.sum_values / g_screen.count;
        float variance = (g_screen.sum_squared / g_screen.count) - (avg * avg);
        float stddev = sqrtf(fabsf(variance));
        
        snprintf(buf, sizeof(buf), 
                "STATISTICHE\n\nMin: %.2f mm\nMax: %.2f mm\nAvg: %.2f mm\nStdDev: %.3f mm\nCount: %u",
                g_screen.min_value, g_screen.max_value, avg, stddev, (unsigned)g_screen.count);
        lv_label_set_text(g_screen.label_stats, buf);
    }
}

void screen_calibro_toggle_stats(bool show) {
    g_screen.stats_visible = show;
    
    if (show) {
        lv_obj_clear_flag(g_screen.panel_stats, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_add_flag(g_screen.panel_stats, LV_OBJ_FLAG_HIDDEN);
    }
    
    ESP_LOGI(TAG, "Stats %s", show ? "mostrate" : "nascoste");
}

void screen_calibro_reset_stats(void) {
    g_screen.min_value = 0;
    g_screen.max_value = 0;
    g_screen.sum_values = 0;
    g_screen.sum_squared = 0;
    g_screen.count = 0;
    
    lv_label_set_text(g_screen.label_stats, "STATISTICHE\n\nMin: -\nMax: -\nAvg: -\nCount: 0");
    
    ESP_LOGI(TAG, "Statistiche resettate");
}
