#include <stdio.h>
#include <string.h>
#include "unity.h"
#include "esp_system.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "../main/hardware/buzzer.h"

static const char *TAG = "TEST_BUZZER";

// Test setup function
void setUp(void) {
    ESP_LOGI(TAG, "Setting up test...");
}

// Test teardown function
void tearDown(void) {
    ESP_LOGI(TAG, "Tearing down test...");
}

// Test 1: Buzzer Initialization
void test_buzzer_init(void) {
    ESP_LOGI(TAG, "Test: Buzzer Initialization");
    
    esp_err_t ret = buzzer_init();
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    // Cleanup
    buzzer_deinit();
}

// Test 2: Play Single Tone
void test_buzzer_play_tone(void) {
    ESP_LOGI(TAG, "Test: Play Single Tone");
    
    buzzer_init();
    
    // Test valid tone
    esp_err_t ret = buzzer_play_tone(NOTE_C5, 100);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(150));
    
    // Test rest/pause (frequency = 0)
    ret = buzzer_play_tone(NOTE_REST, 50);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    buzzer_deinit();
}

// Test 3: Play Pattern - Click
void test_buzzer_pattern_click(void) {
    ESP_LOGI(TAG, "Test: Pattern CLICK");
    
    buzzer_init();
    
    esp_err_t ret = buzzer_play_pattern(BUZZER_PATTERN_CLICK);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(200));
    
    buzzer_deinit();
}

// Test 4: Play Pattern - Success
void test_buzzer_pattern_success(void) {
    ESP_LOGI(TAG, "Test: Pattern SUCCESS");
    
    buzzer_init();
    
    esp_err_t ret = buzzer_play_pattern(BUZZER_PATTERN_SUCCESS);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(500));
    
    buzzer_deinit();
}

// Test 5: Play Pattern - Error
void test_buzzer_pattern_error(void) {
    ESP_LOGI(TAG, "Test: Pattern ERROR");
    
    buzzer_init();
    
    esp_err_t ret = buzzer_play_pattern(BUZZER_PATTERN_ERROR);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(400));
    
    buzzer_deinit();
}

// Test 6: Play Pattern - Warning
void test_buzzer_pattern_warning(void) {
    ESP_LOGI(TAG, "Test: Pattern WARNING");
    
    buzzer_init();
    
    esp_err_t ret = buzzer_play_pattern(BUZZER_PATTERN_WARNING);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(500));
    
    buzzer_deinit();
}

// Test 7: Play Pattern - Startup
void test_buzzer_pattern_startup(void) {
    ESP_LOGI(TAG, "Test: Pattern STARTUP");
    
    buzzer_init();
    
    esp_err_t ret = buzzer_play_pattern(BUZZER_PATTERN_STARTUP);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(600));
    
    buzzer_deinit();
}

// Test 8: Volume Control
void test_buzzer_volume_control(void) {
    ESP_LOGI(TAG, "Test: Volume Control");
    
    buzzer_init();
    
    // Test various volume levels
    uint8_t volumes[] = {0, 25, 50, 75, 100};
    
    for (int i = 0; i < 5; i++) {
        buzzer_set_volume(volumes[i]);
        buzzer_play_tone(NOTE_C5, 100);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
    
    // Test volume clamping (>100 should clamp to 100)
    buzzer_set_volume(150);
    buzzer_play_tone(NOTE_C5, 100);
    vTaskDelay(pdMS_TO_TICKS(200));
    
    buzzer_deinit();
}

// Test 9: Play Custom Melody
void test_buzzer_custom_melody(void) {
    ESP_LOGI(TAG, "Test: Custom Melody");
    
    buzzer_init();
    
    // Define a simple melody
    buzzer_note_t melody[] = {
        {NOTE_C5, 100},
        {NOTE_D5, 100},
        {NOTE_E5, 100},
        {NOTE_G5, 150}
    };
    
    esp_err_t ret = buzzer_play_melody(melody, 4);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(600));
    
    buzzer_deinit();
}

// Test 10: Stop Function
void test_buzzer_stop(void) {
    ESP_LOGI(TAG, "Test: Stop Function");
    
    buzzer_init();
    
    // Start a long tone
    buzzer_play_tone(NOTE_C5, 0);  // Non-blocking
    vTaskDelay(pdMS_TO_TICKS(100));
    
    // Stop it
    esp_err_t ret = buzzer_stop();
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    vTaskDelay(pdMS_TO_TICKS(100));
    
    buzzer_deinit();
}

// Test 11: Test All Patterns (integration test)
void test_buzzer_all_patterns(void) {
    ESP_LOGI(TAG, "Test: All Patterns");
    
    buzzer_init();
    
    // This will test all 10 patterns sequentially
    buzzer_test_all_patterns();
    
    // Wait for all patterns to complete
    vTaskDelay(pdMS_TO_TICKS(6000));
    
    buzzer_deinit();
}

// Test 12: Double Initialization (edge case)
void test_buzzer_double_init(void) {
    ESP_LOGI(TAG, "Test: Double Initialization");
    
    esp_err_t ret1 = buzzer_init();
    TEST_ASSERT_EQUAL(ESP_OK, ret1);
    
    // Second init should return OK but log a warning
    esp_err_t ret2 = buzzer_init();
    TEST_ASSERT_EQUAL(ESP_OK, ret2);
    
    buzzer_deinit();
}

// Test 13: Play Without Initialization (edge case)
void test_buzzer_play_without_init(void) {
    ESP_LOGI(TAG, "Test: Play Without Initialization");
    
    // Ensure buzzer is not initialized
    buzzer_deinit();
    
    // Try to play - should return error
    esp_err_t ret = buzzer_play_tone(NOTE_C5, 100);
    TEST_ASSERT_EQUAL(ESP_ERR_INVALID_STATE, ret);
}

// Test 14: Invalid Pattern (edge case)
void test_buzzer_invalid_pattern(void) {
    ESP_LOGI(TAG, "Test: Invalid Pattern");
    
    buzzer_init();
    
    // Try to play invalid pattern
    esp_err_t ret = buzzer_play_pattern(999);  // Invalid pattern ID
    TEST_ASSERT_EQUAL(ESP_ERR_INVALID_ARG, ret);
    
    buzzer_deinit();
}

// Test 15: NULL Melody (edge case)
void test_buzzer_null_melody(void) {
    ESP_LOGI(TAG, "Test: NULL Melody");
    
    buzzer_init();
    
    // Try to play NULL melody
    esp_err_t ret = buzzer_play_melody(NULL, 0);
    TEST_ASSERT_EQUAL(ESP_ERR_INVALID_ARG, ret);
    
    buzzer_deinit();
}

// Main test runner
void app_main(void) {
    ESP_LOGI(TAG, "=== BUZZER UNIT TESTS ===");
    
    // Wait for system to stabilize
    vTaskDelay(pdMS_TO_TICKS(2000));
    
    UNITY_BEGIN();
    
    // Basic functionality tests
    RUN_TEST(test_buzzer_init);
    RUN_TEST(test_buzzer_play_tone);
    
    // Pattern tests
    RUN_TEST(test_buzzer_pattern_click);
    RUN_TEST(test_buzzer_pattern_success);
    RUN_TEST(test_buzzer_pattern_error);
    RUN_TEST(test_buzzer_pattern_warning);
    RUN_TEST(test_buzzer_pattern_startup);
    
    // Advanced functionality tests
    RUN_TEST(test_buzzer_volume_control);
    RUN_TEST(test_buzzer_custom_melody);
    RUN_TEST(test_buzzer_stop);
    
    // Integration test
    RUN_TEST(test_buzzer_all_patterns);
    
    // Edge case tests
    RUN_TEST(test_buzzer_double_init);
    RUN_TEST(test_buzzer_play_without_init);
    RUN_TEST(test_buzzer_invalid_pattern);
    RUN_TEST(test_buzzer_null_melody);
    
    UNITY_END();
    
    ESP_LOGI(TAG, "=== TESTS COMPLETE ===");
}
