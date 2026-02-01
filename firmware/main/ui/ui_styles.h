#ifndef UI_STYLES_H
#define UI_STYLES_H

#include "lvgl.h"

// Colori tema dark
#define COLOR_BG_PRIMARY    lv_color_hex(0x1a1a2e)
#define COLOR_BG_SECONDARY  lv_color_hex(0x16213e)
#define COLOR_BG_CARD       lv_color_hex(0x0f3460)
#define COLOR_PRIMARY       lv_color_hex(0x00ff88)
#define COLOR_ACCENT        lv_color_hex(0xe94560)
#define COLOR_TEXT_PRIMARY  lv_color_hex(0xffffff)
#define COLOR_TEXT_SECONDARY lv_color_hex(0xb0b0b0)
#define COLOR_SUCCESS       lv_color_hex(0x2ecc71)
#define COLOR_WARNING       lv_color_hex(0xf1c40f)
#define COLOR_ERROR         lv_color_hex(0xe74c3c)

// Gruppi astine
#define COLOR_ANTA_RIBALTA      lv_color_hex(0x9b59b6)
#define COLOR_PERSIANA          lv_color_hex(0x3498db)
#define COLOR_CREMONESE         lv_color_hex(0x2ecc71)
#define COLOR_PERSONALIZZATI    lv_color_hex(0xf1c40f)

// Stili globali
extern lv_style_t style_screen;
extern lv_style_t style_title;
extern lv_style_t style_value_large;
extern lv_style_t style_button_primary;
extern lv_style_t style_button_secondary;
extern lv_style_t style_card;

// Inizializzazione stili
void ui_styles_init(void);

#endif // UI_STYLES_H
