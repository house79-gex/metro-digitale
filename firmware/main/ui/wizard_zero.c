#include "wizard_zero.h"
#include "ui_manager.h"
#include "ui_styles.h"
#include "encoder.h"
#include "hardware/buzzer.h"
#include "feedback/buzzer_feedback.h"
#include "esp_log.h"
#include <stdio.h>

static const char *TAG = "WIZARD_ZERO";

// Stato wizard
static struct {
    lv_obj_t *screen;
    lv_obj_t *label_title;
    lv_obj_t *label_instructions;
    lv_obj_t *progress_bar;
    lv_obj_t *btn_next;
    lv_obj_t *btn_cancel;
    wizard_zero_step_t current_step;
    bool active;
} g_wizard = {0};

// Testi per ogni step
static const char *step_titles[] = {
    "Azzeramento - Benvenuto",
    "Preparazione",
    "Posizionamento Zero",
    "Verifica",
    "Completato!"
};

static const char *step_instructions[] = {
    "Questa procedura guidata ti aiuterà\nad azzerare il calibro digitale.\n\nPremi AVANTI per iniziare.",
    
    "1. Pulisci accuratamente i puntali\n2. Assicurati che siano integri\n3. Rimuovi eventuali residui\n\nPremi AVANTI quando pronto.",
    
    "Chiudi completamente i puntali\nfino al contatto.\n\nQuando sei sicuro della posizione,\npremi AZZERA per impostare lo zero.",
    
    "Verifica della calibrazione in corso...\n\nControllo tolleranza 0.1mm",
    
    "Azzeramento completato con successo!\n\nIl calibro è ora pronto all'uso."
};

// Callback pulsanti
static void btn_next_clicked(lv_event_t *e) {
    wizard_zero_next_step();
}

static void btn_cancel_clicked(lv_event_t *e) {
    wizard_zero_cancel();
}

static void btn_zero_clicked(lv_event_t *e) {
    // Esegui azzeramento encoder
    encoder_zero();
    
    // Feedback buzzer
    buzzer_feedback_play(FEEDBACK_SUCCESS);
    
    ESP_LOGI(TAG, "Encoder azzerato");
    
    // Avanza automaticamente a verifica
    wizard_zero_next_step();
}

/**
 * @brief Aggiorna UI per step corrente
 */
static void update_wizard_ui(void) {
    if (!g_wizard.active || !g_wizard.screen) return;
    
    // Aggiorna titolo
    lv_label_set_text(g_wizard.label_title, step_titles[g_wizard.current_step]);
    
    // Aggiorna istruzioni
    lv_label_set_text(g_wizard.label_instructions, step_instructions[g_wizard.current_step]);
    
    // Aggiorna progress bar (0-100%)
    int32_t progress = (g_wizard.current_step * 100) / (WIZARD_STEP_COMPLETE);
    lv_bar_set_value(g_wizard.progress_bar, progress, LV_ANIM_ON);
    
    // Gestisci pulsanti per ogni step
    switch (g_wizard.current_step) {
        case WIZARD_STEP_WELCOME:
        case WIZARD_STEP_PREPARE:
            // Mostra solo Next e Cancel
            lv_obj_clear_flag(g_wizard.btn_next, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(g_wizard.btn_cancel, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(lv_obj_get_child(g_wizard.btn_next, 0), "AVANTI");
            break;
            
        case WIZARD_STEP_POSITION:
            // Cambia Next in AZZERA
            lv_obj_clear_flag(g_wizard.btn_next, LV_OBJ_FLAG_HIDDEN);
            lv_obj_clear_flag(g_wizard.btn_cancel, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(lv_obj_get_child(g_wizard.btn_next, 0), "AZZERA");
            // Cambia callback
            lv_obj_remove_event_cb(g_wizard.btn_next, btn_next_clicked);
            lv_obj_add_event_cb(g_wizard.btn_next, btn_zero_clicked, LV_EVENT_CLICKED, NULL);
            break;
            
        case WIZARD_STEP_VERIFY:
            // Nascondi pulsanti durante verifica
            lv_obj_add_flag(g_wizard.btn_next, LV_OBJ_FLAG_HIDDEN);
            lv_obj_add_flag(g_wizard.btn_cancel, LV_OBJ_FLAG_HIDDEN);
            
            // Simula verifica (2 secondi)
            // In implementazione reale, qui si controllerebbe la tolleranza
            // Per ora avanza automaticamente dopo delay
            break;
            
        case WIZARD_STEP_COMPLETE:
            // Mostra solo pulsante CHIUDI
            lv_obj_clear_flag(g_wizard.btn_next, LV_OBJ_FLAG_HIDDEN);
            lv_obj_add_flag(g_wizard.btn_cancel, LV_OBJ_FLAG_HIDDEN);
            lv_label_set_text(lv_obj_get_child(g_wizard.btn_next, 0), "CHIUDI");
            // Cambia callback a close
            lv_obj_remove_event_cb(g_wizard.btn_next, btn_zero_clicked);
            lv_obj_add_event_cb(g_wizard.btn_next, btn_cancel_clicked, LV_EVENT_CLICKED, NULL);
            break;
            
        default:
            break;
    }
    
    // Feedback buzzer ad ogni step
    buzzer_feedback_play(FEEDBACK_BUTTON_PRESS);
}

/**
 * @brief Timer callback per auto-avanzamento verifica
 */
static void verify_timer_callback(lv_timer_t *timer) {
    if (g_wizard.current_step == WIZARD_STEP_VERIFY) {
        wizard_zero_next_step();
    }
    lv_timer_del(timer);
}

void wizard_zero_show(void) {
    if (g_wizard.active) {
        ESP_LOGW(TAG, "Wizard già attivo");
        return;
    }
    
    ESP_LOGI(TAG, "Mostra wizard azzeramento");
    
    // Crea screen
    g_wizard.screen = lv_obj_create(NULL);
    lv_obj_add_style(g_wizard.screen, &style_screen, 0);
    
    // Titolo
    g_wizard.label_title = lv_label_create(g_wizard.screen);
    lv_obj_set_style_text_font(g_wizard.label_title, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(g_wizard.label_title, COLOR_PRIMARY, 0);
    lv_obj_align(g_wizard.label_title, LV_ALIGN_TOP_MID, 0, 20);
    
    // Progress bar
    g_wizard.progress_bar = lv_bar_create(g_wizard.screen);
    lv_obj_set_size(g_wizard.progress_bar, 600, 20);
    lv_obj_align(g_wizard.progress_bar, LV_ALIGN_TOP_MID, 0, 80);
    lv_bar_set_value(g_wizard.progress_bar, 0, LV_ANIM_OFF);
    
    // Istruzioni
    g_wizard.label_instructions = lv_label_create(g_wizard.screen);
    lv_obj_set_width(g_wizard.label_instructions, 700);
    lv_label_set_long_mode(g_wizard.label_instructions, LV_LABEL_LONG_WRAP);
    lv_obj_set_style_text_align(g_wizard.label_instructions, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_style_text_font(g_wizard.label_instructions, &lv_font_montserrat_20, 0);
    lv_obj_align(g_wizard.label_instructions, LV_ALIGN_CENTER, 0, 0);
    
    // Pulsante Next/Azzera
    g_wizard.btn_next = lv_btn_create(g_wizard.screen);
    lv_obj_set_size(g_wizard.btn_next, 250, 70);
    lv_obj_add_style(g_wizard.btn_next, &style_button_primary, 0);
    lv_obj_add_event_cb(g_wizard.btn_next, btn_next_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(g_wizard.btn_next, LV_ALIGN_BOTTOM_MID, 100, -40);
    
    lv_obj_t *label_next = lv_label_create(g_wizard.btn_next);
    lv_label_set_text(label_next, "AVANTI");
    lv_obj_set_style_text_font(label_next, &lv_font_montserrat_24, 0);
    lv_obj_center(label_next);
    
    // Pulsante Cancel
    g_wizard.btn_cancel = lv_btn_create(g_wizard.screen);
    lv_obj_set_size(g_wizard.btn_cancel, 200, 60);
    lv_obj_add_style(g_wizard.btn_cancel, &style_button_secondary, 0);
    lv_obj_add_event_cb(g_wizard.btn_cancel, btn_cancel_clicked, LV_EVENT_CLICKED, NULL);
    lv_obj_align(g_wizard.btn_cancel, LV_ALIGN_BOTTOM_MID, -180, -45);
    
    lv_obj_t *label_cancel = lv_label_create(g_wizard.btn_cancel);
    lv_label_set_text(label_cancel, "ANNULLA");
    lv_obj_set_style_text_font(label_cancel, &lv_font_montserrat_20, 0);
    lv_obj_center(label_cancel);
    
    // Inizializza stato
    g_wizard.current_step = WIZARD_STEP_WELCOME;
    g_wizard.active = true;
    
    // Mostra schermata
    lv_scr_load(g_wizard.screen);
    
    // Aggiorna UI
    update_wizard_ui();
}

void wizard_zero_close(void) {
    if (!g_wizard.active) return;
    
    ESP_LOGI(TAG, "Chiudi wizard");
    
    // Cleanup screen
    if (g_wizard.screen) {
        lv_obj_del(g_wizard.screen);
        g_wizard.screen = NULL;
    }
    
    g_wizard.active = false;
    
    // Torna a schermata calibro
    ui_manager_show_screen(UI_SCREEN_CALIBRO);
}

void wizard_zero_next_step(void) {
    if (!g_wizard.active) return;
    
    // Avanza step
    if (g_wizard.current_step < WIZARD_STEP_COMPLETE) {
        g_wizard.current_step++;
        
        ESP_LOGI(TAG, "Avanzamento a step %d", g_wizard.current_step);
        
        // Aggiorna UI
        update_wizard_ui();
        
        // Se siamo in verifica, avvia timer auto-avanzamento
        if (g_wizard.current_step == WIZARD_STEP_VERIFY) {
            lv_timer_create(verify_timer_callback, 2000, NULL);
        }
        
    } else {
        // Ultimo step, chiudi wizard
        wizard_zero_close();
    }
}

void wizard_zero_cancel(void) {
    ESP_LOGI(TAG, "Wizard cancellato");
    g_wizard.current_step = WIZARD_STEP_CANCELED;
    wizard_zero_close();
}

wizard_zero_step_t wizard_zero_get_current_step(void) {
    return g_wizard.current_step;
}
