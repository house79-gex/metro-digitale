idf_component_register(
    SRCS 
        "main.c"
        "config.c"
        "encoder.c"
        "bluetooth.c"
        "storage.c"
        "formula_parser.c"
        # Hardware layer
        "hardware/hardware_gpio.c"
        "hardware/encoder_reader.c"
        "hardware/sd_card.c"
        "hardware/buzzer.c"
        # Feedback system
        "feedback/buzzer_feedback.c"
        "feedback/led_feedback.c"
        # Tip management (puntali)
        "puntali/puntale_types.c"
        "puntali/stl_parser.c"
        "puntali/puntale_database.c"
        "puntali/puntale_circular.c"
        # Measurement system
        "measurement/measure_calculator.c"
        "measurement/mode_device_routing.c"
        "measurement/measure_sender.c"
        # Storage system
        "storage/storage_manager.c"
        # Operational modes
        "modes/calibro_advanced.c"
        "modes/mode_vetri.c"
        "modes/mode_astine.c"
        "modes/mode_fermavetri.c"
        # Display drivers
        "display/display_rgb.c"
        "display/touch_gt911.c"
        # Hardware components
        "hardware/button_send.c"
        # BLE multi-device system
        "ble/ble_server.c"
        "ble/ble_multi_device.c"
        # UI components
        "ui/ui_manager.c"
        "ui/ui_styles.c"
        "ui/ui_main.c"
        "ui/ui_calibro.c"
        "ui/ui_vetri.c"
        "ui/ui_astine.c"
        "ui/ui_mode_select.c"
        "ui/ui_settings.c"
        "ui/ui_rilievi_speciali.c"
        "ui/ui_tipologie.c"
        "ui/ui_toast.c"
        # UI advanced components
        "ui/gesture_handler.c"
        "ui/wizard_zero.c"
        "ui/screen_calibro_advanced.c"
        "ui/screen_vetri_wizard.c"
        "ui/screen_astine.c"
        "ui/screen_settings.c"
        "ui/bottom_nav.c"
    INCLUDE_DIRS 
        "."
        "ui"
        "hardware"
        "feedback"
        "puntali"
        "ble"
        "measurement"
        "storage"
        "modes"
        "display"
    REQUIRES 
        nvs_flash 
        bt 
        driver 
        esp_timer
        lvgl
        fatfs
        spi_flash
)
