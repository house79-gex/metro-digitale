#include "ui_manager.h"
#include "ui_styles.h"
#include "config.h"
#include "encoder.h"
#include "bluetooth.h"
#include "formula_parser.h"
#include <stdio.h>

static lv_obj_t *label_tipologia = NULL;
static lv_obj_t *label_variabili = NULL;
static lv_obj_t *label_elementi = NULL;
static lv_obj_t *label_status = NULL;

// Stato attuale rilievo
static uint8_t variabile_corrente_idx = 0;
static bool modalita_rilievo = true; // true = rileva variabili, false = mostra elementi

static void calcola_elementi(void) {
    if (g_config.num_tipologie == 0) return;
    
    TipologiaInfisso *tip = &g_config.tipologie[g_config.tipologia_corrente_idx];
    
    // Calcola tutti gli elementi usando le formule
    for (uint8_t i = 0; i < tip->num_elementi; i++) {
        ElementoCalcolato *elem = &tip->elementi[i];
        
        ParseResult result = formula_parser_evaluate(
            elem->formula,
            tip->variabili,
            tip->num_variabili
        );
        
        if (result.success) {
            elem->risultato = result.value;
        } else {
            elem->risultato = 0.0f;
        }
    }
}

static void btn_rileva_clicked(lv_event_t *e) {
    if (g_config.num_tipologie == 0) return;
    
    TipologiaInfisso *tip = &g_config.tipologie[g_config.tipologia_corrente_idx];
    
    if (variabile_corrente_idx < tip->num_variabili) {
        // Rileva valore corrente encoder
        float valore = encoder_get_position_mm();
        
        VariabileRilievo *var = &tip->variabili[variabile_corrente_idx];
        var->valore = valore;
        var->rilevato = true;
        
        // Passa alla prossima variabile
        variabile_corrente_idx++;
        
        // Se tutte rilevate, calcola elementi e passa a modalità elementi
        if (variabile_corrente_idx >= tip->num_variabili) {
            calcola_elementi();
            modalita_rilievo = false;
            variabile_corrente_idx = 0;
        }
    }
}

static void btn_invia_clicked(lv_event_t *e) {
    if (g_config.num_tipologie == 0) return;
    
    TipologiaInfisso *tip = &g_config.tipologie[g_config.tipologia_corrente_idx];
    
    if (!modalita_rilievo && variabile_corrente_idx < tip->num_elementi) {
        ElementoCalcolato *elem = &tip->elementi[variabile_corrente_idx];
        
        if (elem->quantita_attuale > 0) {
            // Invia via Bluetooth
            bluetooth_send_rilievo_speciale(
                tip->nome,
                elem->nome,
                elem->formula,
                elem->risultato,
                elem->quantita_attuale,
                g_config.auto_send_troncatrice
            );
            
            elem->inviato = true;
        }
        
        // Passa al prossimo elemento
        variabile_corrente_idx++;
    }
}

static void btn_reset_clicked(lv_event_t *e) {
    if (g_config.num_tipologie == 0) return;
    
    TipologiaInfisso *tip = &g_config.tipologie[g_config.tipologia_corrente_idx];
    
    // Reset tutte le variabili
    for (uint8_t i = 0; i < tip->num_variabili; i++) {
        tip->variabili[i].rilevato = false;
        tip->variabili[i].valore = 0.0f;
    }
    
    // Reset tutti gli elementi
    for (uint8_t i = 0; i < tip->num_elementi; i++) {
        tip->elementi[i].risultato = 0.0f;
        tip->elementi[i].quantita_attuale = tip->elementi[i].quantita_default;
        tip->elementi[i].inviato = false;
    }
    
    variabile_corrente_idx = 0;
    modalita_rilievo = true;
}

static void btn_next_tipologia_clicked(lv_event_t *e) {
    if (g_config.tipologia_corrente_idx < g_config.num_tipologie - 1) {
        g_config.tipologia_corrente_idx++;
    } else {
        g_config.tipologia_corrente_idx = 0;
    }
    btn_reset_clicked(NULL);
}

static void btn_prev_tipologia_clicked(lv_event_t *e) {
    if (g_config.tipologia_corrente_idx > 0) {
        g_config.tipologia_corrente_idx--;
    } else {
        g_config.tipologia_corrente_idx = g_config.num_tipologie - 1;
    }
    btn_reset_clicked(NULL);
}

static void btn_back_clicked(lv_event_t *e) {
    btn_reset_clicked(NULL);
    ui_manager_show_screen(UI_SCREEN_RILIEVI_SPECIALI);
}

lv_obj_t* ui_tipologie_create(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_add_style(screen, &style_screen, 0);
    
    lv_obj_t *label_title = lv_label_create(screen);
    lv_label_set_text(label_title, "🪟 Tipologie Infisso");
    lv_obj_add_style(label_title, &style_title, 0);
    lv_obj_align(label_title, LV_ALIGN_TOP_MID, 0, 10);
    
    // Nome tipologia
    label_tipologia = lv_label_create(screen);
    lv_obj_set_style_text_font(label_tipologia, &lv_font_montserrat_24, 0);
    lv_obj_align(label_tipologia, LV_ALIGN_TOP_MID, 0, 50);
    
    // Status
    label_status = lv_label_create(screen);
    lv_obj_set_style_text_font(label_status, &lv_font_montserrat_16, 0);
    lv_obj_align(label_status, LV_ALIGN_TOP_MID, 0, 85);
    
    // Card variabili
    lv_obj_t *card_var = lv_obj_create(screen);
    lv_obj_set_size(card_var, 350, 200);
    lv_obj_add_style(card_var, &style_card, 0);
    lv_obj_align(card_var, LV_ALIGN_LEFT_MID, 20, 0);
    
    lv_obj_t *lbl_var_title = lv_label_create(card_var);
    lv_label_set_text(lbl_var_title, "VARIABILI");
    lv_obj_set_style_text_font(lbl_var_title, &lv_font_montserrat_18, 0);
    lv_obj_align(lbl_var_title, LV_ALIGN_TOP_MID, 0, 10);
    
    label_variabili = lv_label_create(card_var);
    lv_obj_set_style_text_font(label_variabili, &lv_font_montserrat_14, 0);
    lv_obj_align(label_variabili, LV_ALIGN_CENTER, 0, 10);
    
    // Card elementi
    lv_obj_t *card_elem = lv_obj_create(screen);
    lv_obj_set_size(card_elem, 350, 200);
    lv_obj_add_style(card_elem, &style_card, 0);
    lv_obj_align(card_elem, LV_ALIGN_RIGHT_MID, -20, 0);
    
    lv_obj_t *lbl_elem_title = lv_label_create(card_elem);
    lv_label_set_text(lbl_elem_title, "ELEMENTI");
    lv_obj_set_style_text_font(lbl_elem_title, &lv_font_montserrat_18, 0);
    lv_obj_align(lbl_elem_title, LV_ALIGN_TOP_MID, 0, 10);
    
    label_elementi = lv_label_create(card_elem);
    lv_obj_set_style_text_font(label_elementi, &lv_font_montserrat_14, 0);
    lv_obj_align(label_elementi, LV_ALIGN_CENTER, 0, 10);
    
    // Pulsanti controllo
    lv_obj_t *btn_rileva = lv_btn_create(screen);
    lv_obj_set_size(btn_rileva, 150, 50);
    lv_obj_add_style(btn_rileva, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_rileva, btn_rileva_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_rileva, LV_ALIGN_BOTTOM_LEFT, 30, -80);
    lv_obj_t *lbl = lv_label_create(btn_rileva);
    lv_label_set_text(lbl, "Rileva");
    lv_obj_center(lbl);
    
    lv_obj_t *btn_invia = lv_btn_create(screen);
    lv_obj_set_size(btn_invia, 150, 50);
    lv_obj_add_style(btn_invia, &style_button_primary, 0);
    lv_obj_add_event_cb(btn_invia, btn_invia_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_invia, LV_ALIGN_BOTTOM_MID, 0, -80);
    lbl = lv_label_create(btn_invia);
    lv_label_set_text(lbl, "📤 Invia");
    lv_obj_center(lbl);
    
    lv_obj_t *btn_reset = lv_btn_create(screen);
    lv_obj_set_size(btn_reset, 150, 50);
    lv_obj_add_style(btn_reset, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_reset, btn_reset_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_reset, LV_ALIGN_BOTTOM_RIGHT, -30, -80);
    lbl = lv_label_create(btn_reset);
    lv_label_set_text(lbl, "Reset");
    lv_obj_center(lbl);
    
    // Pulsanti navigazione tipologie
    lv_obj_t *btn_prev = lv_btn_create(screen);
    lv_obj_set_size(btn_prev, 100, 40);
    lv_obj_add_style(btn_prev, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_prev, btn_prev_tipologia_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_prev, LV_ALIGN_BOTTOM_LEFT, 30, -20);
    lbl = lv_label_create(btn_prev);
    lv_label_set_text(lbl, "< Prec");
    lv_obj_center(lbl);
    
    lv_obj_t *btn_next = lv_btn_create(screen);
    lv_obj_set_size(btn_next, 100, 40);
    lv_obj_add_style(btn_next, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_next, btn_next_tipologia_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_next, LV_ALIGN_BOTTOM_LEFT, 145, -20);
    lbl = lv_label_create(btn_next);
    lv_label_set_text(lbl, "Succ >");
    lv_obj_center(lbl);
    
    lv_obj_t *btn_back = lv_btn_create(screen);
    lv_obj_set_size(btn_back, 150, 40);
    lv_obj_add_style(btn_back, &style_button_secondary, 0);
    lv_obj_add_event_cb(btn_back, btn_back_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_RIGHT, -30, -20);
    lbl = lv_label_create(btn_back);
    lv_label_set_text(lbl, "Indietro");
    lv_obj_center(lbl);
    
    return screen;
}

void ui_tipologie_update(void) {
    if (g_config.num_tipologie == 0) {
        lv_label_set_text(label_tipologia, "Nessuna tipologia configurata");
        lv_label_set_text(label_variabili, "");
        lv_label_set_text(label_elementi, "");
        lv_label_set_text(label_status, "");
        return;
    }
    
    TipologiaInfisso *tip = &g_config.tipologie[g_config.tipologia_corrente_idx];
    
    // Aggiorna nome tipologia
    char nome_str[64];
    snprintf(nome_str, sizeof(nome_str), "%s %s", tip->icona, tip->nome);
    lv_label_set_text(label_tipologia, nome_str);
    
    // Aggiorna status
    if (modalita_rilievo) {
        char status_str[128];
        snprintf(status_str, sizeof(status_str), "Rileva variabili: %u/%u",
                 variabile_corrente_idx, tip->num_variabili);
        lv_label_set_text(label_status, status_str);
    } else {
        char status_str[128];
        snprintf(status_str, sizeof(status_str), "Invia elementi: %u/%u",
                 variabile_corrente_idx, tip->num_elementi);
        lv_label_set_text(label_status, status_str);
    }
    
    // Aggiorna lista variabili
    char var_str[256] = "";
    for (uint8_t i = 0; i < tip->num_variabili; i++) {
        VariabileRilievo *var = &tip->variabili[i];
        char line[64];
        
        if (i == variabile_corrente_idx && modalita_rilievo) {
            snprintf(line, sizeof(line), "▶ %s: %.1f mm\n", 
                    var->descrizione, encoder_get_position_mm());
        } else if (var->rilevato) {
            snprintf(line, sizeof(line), "✅ %s: %.1f mm\n", 
                    var->descrizione, var->valore);
        } else {
            snprintf(line, sizeof(line), "⭕ %s: ---\n", var->descrizione);
        }
        
        strcat(var_str, line);
    }
    lv_label_set_text(label_variabili, var_str);
    
    // Aggiorna lista elementi
    char elem_str[512] = "";
    for (uint8_t i = 0; i < tip->num_elementi; i++) {
        ElementoCalcolato *elem = &tip->elementi[i];
        char line[96];
        
        if (i == variabile_corrente_idx && !modalita_rilievo) {
            snprintf(line, sizeof(line), "▶ %s\n  %.1f mm × %u pz\n", 
                    elem->nome, elem->risultato, elem->quantita_attuale);
        } else if (elem->inviato) {
            snprintf(line, sizeof(line), "✅ %s: %.1f mm\n", 
                    elem->nome, elem->risultato);
        } else if (!modalita_rilievo) {
            snprintf(line, sizeof(line), "⭕ %s: %.1f mm\n", 
                    elem->nome, elem->risultato);
        } else {
            snprintf(line, sizeof(line), "⭕ %s\n", elem->nome);
        }
        
        strcat(elem_str, line);
    }
    lv_label_set_text(label_elementi, elem_str);
}
