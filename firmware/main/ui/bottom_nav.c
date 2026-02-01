#include "bottom_nav.h"
#include "ui_styles.h"
#include "esp_log.h"

static const char *TAG = "BOTTOM_NAV";

// Stato navigation
static struct {
    lv_obj_t *nav_bar;
    lv_obj_t *buttons[5];
    nav_item_t active_item;
    nav_callback_t callback;
} g_nav = {0};

// Icone navigation (emoji/simboli)
static const char *nav_icons[] = {
    "🏠",  // Home
    "📐",  // Calibro
    "🪟",  // Vetri
    "📏",  // Astine
    "⚙️"   // Settings
};

static const char *nav_labels[] = {
    "Home",
    "Calibro",
    "Vetri",
    "Astine",
    "Settings"
};

/**
 * @brief Callback pulsante navigation
 */
static void nav_button_clicked(lv_event_t *e) {
    lv_obj_t *btn = lv_event_get_target(e);
    
    // Trova indice pulsante
    nav_item_t item = NAV_HOME;
    for (int i = 0; i < 5; i++) {
        if (g_nav.buttons[i] == btn) {
            item = (nav_item_t)i;
            break;
        }
    }
    
    // Aggiorna active item
    bottom_nav_set_active(item);
    
    // Chiama callback
    if (g_nav.callback) {
        g_nav.callback(item);
    }
    
    ESP_LOGI(TAG, "Nav item selezionato: %d (%s)", item, nav_labels[item]);
}

lv_obj_t* bottom_nav_create(lv_obj_t *parent, nav_callback_t callback) {
    if (!parent) {
        ESP_LOGE(TAG, "Parent NULL");
        return NULL;
    }
    
    ESP_LOGI(TAG, "Crea bottom navigation");
    
    g_nav.callback = callback;
    g_nav.active_item = NAV_HOME;
    
    // Crea container navigation bar
    g_nav.nav_bar = lv_obj_create(parent);
    lv_obj_set_size(g_nav.nav_bar, LV_PCT(100), 60);
    lv_obj_align(g_nav.nav_bar, LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_obj_set_style_bg_color(g_nav.nav_bar, lv_color_hex(0x1a1a2e), 0);
    lv_obj_set_style_border_width(g_nav.nav_bar, 0, 0);
    lv_obj_set_style_pad_all(g_nav.nav_bar, 5, 0);
    lv_obj_clear_flag(g_nav.nav_bar, LV_OBJ_FLAG_SCROLLABLE);
    
    // Crea 5 pulsanti navigation
    int btn_width = 150;
    int btn_spacing = 10;
    int total_width = 5 * btn_width + 4 * btn_spacing;
    int start_x = -total_width / 2;
    
    for (int i = 0; i < 5; i++) {
        lv_obj_t *btn = lv_btn_create(g_nav.nav_bar);
        lv_obj_set_size(btn, btn_width, 50);
        lv_obj_align(btn, LV_ALIGN_CENTER, start_x + btn_width/2 + i * (btn_width + btn_spacing), 0);
        lv_obj_add_event_cb(btn, nav_button_clicked, LV_EVENT_CLICKED, NULL);
        
        // Stile pulsante
        lv_obj_set_style_bg_color(btn, lv_color_hex(0x2a2a3e), 0);
        lv_obj_set_style_border_width(btn, 0, 0);
        lv_obj_set_style_shadow_width(btn, 0, 0);
        
        // Label con icona + testo
        lv_obj_t *label = lv_label_create(btn);
        char text[64];
        snprintf(text, sizeof(text), "%s\n%s", nav_icons[i], nav_labels[i]);
        lv_label_set_text(label, text);
        lv_obj_set_style_text_align(label, LV_TEXT_ALIGN_CENTER, 0);
        lv_obj_set_style_text_font(label, &lv_font_montserrat_14, 0);
        lv_obj_center(label);
        
        g_nav.buttons[i] = btn;
    }
    
    // Imposta primo pulsante come attivo
    bottom_nav_set_active(NAV_HOME);
    
    ESP_LOGI(TAG, "Bottom navigation creata con 5 pulsanti");
    
    return g_nav.nav_bar;
}

void bottom_nav_set_active(nav_item_t item) {
    if (item >= 5) {
        ESP_LOGW(TAG, "Nav item invalido: %d", item);
        return;
    }
    
    g_nav.active_item = item;
    
    // Aggiorna stile pulsanti
    for (int i = 0; i < 5; i++) {
        lv_obj_t *btn = g_nav.buttons[i];
        lv_obj_t *label = lv_obj_get_child(btn, 0);
        
        if (i == item) {
            // Attivo - verde
            lv_obj_set_style_bg_color(btn, lv_color_hex(0x00ff88), 0);
            lv_obj_set_style_text_color(label, lv_color_hex(0x000000), 0);
        } else {
            // Inattivo - grigio
            lv_obj_set_style_bg_color(btn, lv_color_hex(0x2a2a3e), 0);
            lv_obj_set_style_text_color(label, lv_color_hex(0x888888), 0);
        }
    }
    
    ESP_LOGD(TAG, "Nav attivo: %s", nav_labels[item]);
}

nav_item_t bottom_nav_get_active(void) {
    return g_nav.active_item;
}
