#include "ui_styles.h"

// Definizione stili globali
lv_style_t style_screen;
lv_style_t style_title;
lv_style_t style_value_large;
lv_style_t style_button_primary;
lv_style_t style_button_secondary;
lv_style_t style_card;

void ui_styles_init(void) {
    // Style: Screen background
    lv_style_init(&style_screen);
    lv_style_set_bg_color(&style_screen, COLOR_BG_PRIMARY);
    lv_style_set_pad_all(&style_screen, 0);
    
    // Style: Title
    lv_style_init(&style_title);
    lv_style_set_text_color(&style_title, COLOR_TEXT_PRIMARY);
    lv_style_set_text_font(&style_title, &lv_font_montserrat_32);
    
    // Style: Large value display
    lv_style_init(&style_value_large);
    lv_style_set_text_color(&style_value_large, COLOR_ACCENT);
    lv_style_set_text_font(&style_value_large, &lv_font_montserrat_48);
    
    // Style: Primary button
    lv_style_init(&style_button_primary);
    lv_style_set_bg_color(&style_button_primary, COLOR_ACCENT);
    lv_style_set_bg_opa(&style_button_primary, LV_OPA_COVER);
    lv_style_set_radius(&style_button_primary, 8);
    lv_style_set_pad_all(&style_button_primary, 16);
    lv_style_set_text_color(&style_button_primary, COLOR_TEXT_PRIMARY);
    
    // Style: Secondary button
    lv_style_init(&style_button_secondary);
    lv_style_set_bg_color(&style_button_secondary, COLOR_BG_CARD);
    lv_style_set_bg_opa(&style_button_secondary, LV_OPA_COVER);
    lv_style_set_radius(&style_button_secondary, 8);
    lv_style_set_pad_all(&style_button_secondary, 16);
    lv_style_set_text_color(&style_button_secondary, COLOR_TEXT_PRIMARY);
    lv_style_set_border_color(&style_button_secondary, COLOR_ACCENT);
    lv_style_set_border_width(&style_button_secondary, 2);
    
    // Style: Card
    lv_style_init(&style_card);
    lv_style_set_bg_color(&style_card, COLOR_BG_CARD);
    lv_style_set_bg_opa(&style_card, LV_OPA_COVER);
    lv_style_set_radius(&style_card, 12);
    lv_style_set_pad_all(&style_card, 20);
    lv_style_set_border_color(&style_card, COLOR_BG_SECONDARY);
    lv_style_set_border_width(&style_card, 1);
}
