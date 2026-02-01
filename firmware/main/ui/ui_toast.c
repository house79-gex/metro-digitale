#include "ui_toast.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "UI_TOAST";

// Stub implementation - requires LVGL integration
// In a full implementation, this would create an lv_obj with:
// - Position: bottom-center (y = screen_height - 120px)
// - Style: dark background, colored border, padding
// - Animation: fade in/out
// - Auto-delete after duration

void ui_show_toast(const char *message) {
    if (!message) return;
    
    ESP_LOGI(TAG, "Toast: %s", message);
    
    // TODO: Implement LVGL toast UI
    // lv_obj_t *toast = lv_obj_create(lv_scr_act());
    // lv_obj_set_size(toast, 300, 60);
    // lv_obj_align(toast, LV_ALIGN_BOTTOM_MID, 0, -80);
    // ... style setup ...
    // lv_timer to auto-delete after 2s
}

void ui_show_toast_duration(const char *message, uint32_t duration_ms) {
    if (!message) return;
    
    ESP_LOGI(TAG, "Toast (%lums): %s", duration_ms, message);
    
    // TODO: Implement with custom duration
}

void ui_show_toast_success(const char *message) {
    if (!message) return;
    
    char buf[128];
    snprintf(buf, sizeof(buf), "✓ %s", message);
    
    ESP_LOGI(TAG, "Toast Success: %s", message);
    
    // TODO: Implement with green border
}

void ui_show_toast_error(const char *message) {
    if (!message) return;
    
    char buf[128];
    snprintf(buf, sizeof(buf), "✗ %s", message);
    
    ESP_LOGE(TAG, "Toast Error: %s", message);
    
    // TODO: Implement with red border
}

void ui_show_toast_warning(const char *message) {
    if (!message) return;
    
    char buf[128];
    snprintf(buf, sizeof(buf), "⚠ %s", message);
    
    ESP_LOGW(TAG, "Toast Warning: %s", message);
    
    // TODO: Implement with orange border
}
