# Firmware Tests - Metro Digitale

## Overview

This directory contains unit tests for the Metro Digitale firmware components.

## Test Files

### test_buzzer.c

Comprehensive unit tests for the passive buzzer audio feedback system.

**Test Coverage:**
- Basic initialization and deinitialization
- Single tone playback
- Pattern playback (10 predefined patterns)
- Volume control (0-100%)
- Custom melody playback
- Stop functionality
- Edge cases (double init, null melody, invalid patterns)

**Total Tests:** 15

## Running Tests

### Prerequisites

1. ESP-IDF v5.0 or later installed
2. ESP32-S3 development board
3. Passive buzzer connected to GPIO 46

### Build and Flash Tests

```bash
# Set up ESP-IDF environment
. $HOME/esp/esp-idf/export.sh

# Navigate to tests directory
cd firmware/tests

# Configure for tests
idf.py set-target esp32s3

# Build tests
idf.py build

# Flash and monitor
idf.py -p /dev/ttyUSB0 flash monitor
```

### Expected Output

```
=== BUZZER UNIT TESTS ===
Running test_buzzer_init...
Running test_buzzer_play_tone...
Running test_buzzer_pattern_click...
[... additional tests ...]
15 Tests 0 Failures 0 Ignored
=== TESTS COMPLETE ===
```

## Test Configuration

The tests use the Unity test framework (included with ESP-IDF).

### Test Execution

- Each test runs independently with setUp/tearDown
- Tests include delays to allow audio playback to complete
- Visual/audio verification possible during test runs

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
- name: Build and Test Firmware
  run: |
    cd firmware/tests
    idf.py build
    # Flash to device and capture results
```

## Manual Testing

In addition to automated tests, manual verification is recommended:

1. **Audio Quality Test**
   - Listen to each pattern
   - Verify distinct melodies
   - Check volume levels

2. **Volume Control Test**
   - Adjust volume slider in UI Settings
   - Verify volume changes smoothly
   - Test 0% (silent) and 100% (max)

3. **Integration Test**
   - Press SEND button → hear click
   - Send measurement → hear send_ok pattern
   - Trigger error → hear error pattern

## Hardware Test Checklist

Before running tests:

- [ ] Buzzer connected to GPIO 46 (+ terminal)
- [ ] Buzzer ground to GND
- [ ] 100Ω resistor in series (optional)
- [ ] Verify no other device using GPIO 46
- [ ] Check power supply (3.3V stable)
- [ ] Volume set >0% in settings

## Troubleshooting

**Tests fail with ESP_ERR_INVALID_STATE:**
- Check BUZZER_ENABLED is set to 1 in config.h
- Verify GPIO 46 is available (not used elsewhere)
- Check LEDC timer/channel not in conflict

**No audio during tests:**
- Verify buzzer polarity (+ on GPIO 46)
- Check buzzer type (must be passive, not active)
- Measure PWM signal with oscilloscope
- Verify 100Ω resistor if used

**Distorted audio:**
- Check power supply stability
- Reduce volume to 50%
- Verify buzzer specifications (3.3V compatible)

## Adding New Tests

To add new buzzer tests:

1. Create test function following Unity conventions:
   ```c
   void test_my_new_feature(void) {
       buzzer_init();
       // Your test code
       TEST_ASSERT_EQUAL(expected, actual);
       buzzer_deinit();
   }
   ```

2. Register test in app_main():
   ```c
   RUN_TEST(test_my_new_feature);
   ```

3. Build and run to verify

## Resources

- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
- [ESP-IDF Unit Testing](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/unit-tests.html)
- [LEDC Driver Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/ledc.html)
