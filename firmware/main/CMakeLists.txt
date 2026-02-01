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
        "hardware/button_send.c"
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
    REQUIRES 
        nvs_flash 
        bt 
        driver 
        esp_timer
        lvgl
        fatfs
        spi_flash
)
