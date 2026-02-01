#include "gesture_handler.h"
#include "esp_log.h"
#include "esp_timer.h"
#include <math.h>

static const char *TAG = "GESTURE";

// Configurazione gesture
#define SWIPE_THRESHOLD_PX      50      // Distanza minima per swipe
#define SWIPE_MAX_TIME_MS       500     // Tempo massimo per swipe veloce
#define LONG_PRESS_TIME_MS      800     // Tempo per long press
#define TAP_MAX_MOVE_PX         10      // Movimento massimo per considerare tap

// Stato gesture
static struct {
    bool enabled;
    gesture_callback_t callback;
    gesture_type_t last_gesture;
    
    // Dati touch
    bool touch_active;
    lv_coord_t start_x;
    lv_coord_t start_y;
    lv_coord_t current_x;
    lv_coord_t current_y;
    uint64_t press_time_us;
    bool long_press_sent;
} g_gesture_state = {
    .enabled = true,
    .callback = NULL,
    .last_gesture = GESTURE_NONE,
    .touch_active = false,
    .long_press_sent = false
};

/**
 * @brief Calcola distanza euclidea
 */
static float calculate_distance(lv_coord_t x1, lv_coord_t y1, lv_coord_t x2, lv_coord_t y2) {
    float dx = x2 - x1;
    float dy = y2 - y1;
    return sqrtf(dx * dx + dy * dy);
}

/**
 * @brief Rileva tipo di swipe da vettore
 */
static gesture_type_t detect_swipe_direction(lv_coord_t dx, lv_coord_t dy) {
    float abs_dx = fabsf(dx);
    float abs_dy = fabsf(dy);
    
    // Determina direzione predominante
    if (abs_dx > abs_dy) {
        // Swipe orizzontale
        return (dx > 0) ? GESTURE_SWIPE_RIGHT : GESTURE_SWIPE_LEFT;
    } else {
        // Swipe verticale
        return (dy > 0) ? GESTURE_SWIPE_DOWN : GESTURE_SWIPE_UP;
    }
}

/**
 * @brief Event handler LVGL
 */
static void gesture_event_handler(lv_event_t *e) {
    lv_event_code_t code = lv_event_get_code(e);
    lv_obj_t *obj = lv_event_get_target(e);
    
    if (!g_gesture_state.enabled) {
        return;
    }
    
    if (code == LV_EVENT_PRESSED) {
        // Inizio touch
        lv_point_t point;
        lv_indev_get_point(lv_indev_get_act(), &point);
        
        g_gesture_state.touch_active = true;
        g_gesture_state.start_x = point.x;
        g_gesture_state.start_y = point.y;
        g_gesture_state.current_x = point.x;
        g_gesture_state.current_y = point.y;
        g_gesture_state.press_time_us = esp_timer_get_time();
        g_gesture_state.long_press_sent = false;
        
        ESP_LOGD(TAG, "Touch iniziato: (%d, %d)", point.x, point.y);
        
    } else if (code == LV_EVENT_PRESSING) {
        // Touch in corso
        if (!g_gesture_state.touch_active) return;
        
        lv_point_t point;
        lv_indev_get_point(lv_indev_get_act(), &point);
        
        g_gesture_state.current_x = point.x;
        g_gesture_state.current_y = point.y;
        
        // Verifica long press
        uint64_t now_us = esp_timer_get_time();
        uint64_t press_duration_ms = (now_us - g_gesture_state.press_time_us) / 1000;
        
        if (press_duration_ms >= LONG_PRESS_TIME_MS && !g_gesture_state.long_press_sent) {
            float move_dist = calculate_distance(g_gesture_state.start_x, g_gesture_state.start_y,
                                                g_gesture_state.current_x, g_gesture_state.current_y);
            
            if (move_dist < TAP_MAX_MOVE_PX) {
                // Long press rilevato!
                g_gesture_state.last_gesture = GESTURE_LONG_PRESS;
                g_gesture_state.long_press_sent = true;
                
                ESP_LOGI(TAG, "Long press rilevato");
                
                if (g_gesture_state.callback) {
                    g_gesture_state.callback(GESTURE_LONG_PRESS);
                }
            }
        }
        
    } else if (code == LV_EVENT_RELEASED) {
        // Fine touch
        if (!g_gesture_state.touch_active) return;
        
        lv_point_t point;
        lv_indev_get_point(lv_indev_get_act(), &point);
        
        g_gesture_state.current_x = point.x;
        g_gesture_state.current_y = point.y;
        
        uint64_t now_us = esp_timer_get_time();
        uint64_t press_duration_ms = (now_us - g_gesture_state.press_time_us) / 1000;
        
        // Calcola movimento
        lv_coord_t dx = g_gesture_state.current_x - g_gesture_state.start_x;
        lv_coord_t dy = g_gesture_state.current_y - g_gesture_state.start_y;
        float move_dist = calculate_distance(g_gesture_state.start_x, g_gesture_state.start_y,
                                            g_gesture_state.current_x, g_gesture_state.current_y);
        
        ESP_LOGD(TAG, "Touch rilasciato: dx=%d, dy=%d, dist=%.1f, time=%llu ms",
                 dx, dy, move_dist, press_duration_ms);
        
        gesture_type_t gesture = GESTURE_NONE;
        
        if (g_gesture_state.long_press_sent) {
            // Long press già inviato, ignora rilascio
            gesture = GESTURE_NONE;
            
        } else if (move_dist >= SWIPE_THRESHOLD_PX && press_duration_ms <= SWIPE_MAX_TIME_MS) {
            // Swipe veloce
            gesture = detect_swipe_direction(dx, dy);
            ESP_LOGI(TAG, "Swipe rilevato: %d", gesture);
            
        } else if (move_dist < TAP_MAX_MOVE_PX) {
            // Tap singolo
            gesture = GESTURE_TAP;
            ESP_LOGI(TAG, "Tap rilevato");
        }
        
        if (gesture != GESTURE_NONE) {
            g_gesture_state.last_gesture = gesture;
            
            if (g_gesture_state.callback) {
                g_gesture_state.callback(gesture);
            }
        }
        
        g_gesture_state.touch_active = false;
    }
}

void gesture_handler_init(lv_obj_t *screen, gesture_callback_t callback) {
    if (!screen) {
        ESP_LOGE(TAG, "Screen NULL");
        return;
    }
    
    g_gesture_state.callback = callback;
    g_gesture_state.enabled = true;
    g_gesture_state.last_gesture = GESTURE_NONE;
    
    // Aggiungi event handler allo screen
    lv_obj_add_event_cb(screen, gesture_event_handler, LV_EVENT_PRESSED, NULL);
    lv_obj_add_event_cb(screen, gesture_event_handler, LV_EVENT_PRESSING, NULL);
    lv_obj_add_event_cb(screen, gesture_event_handler, LV_EVENT_RELEASED, NULL);
    
    ESP_LOGI(TAG, "Gesture handler inizializzato (threshold %d px, long press %d ms)",
             SWIPE_THRESHOLD_PX, LONG_PRESS_TIME_MS);
}

void gesture_handler_enable(bool enable) {
    g_gesture_state.enabled = enable;
    ESP_LOGI(TAG, "Gesture %s", enable ? "abilitati" : "disabilitati");
}

gesture_type_t gesture_handler_get_last(void) {
    return g_gesture_state.last_gesture;
}
