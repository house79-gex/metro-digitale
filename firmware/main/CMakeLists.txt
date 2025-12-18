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
        # Feedback system
        "feedback/buzzer_feedback.c"
        "feedback/led_feedback.c"
        # Tip management (puntali)
        "puntali/puntale_types.c"
        "puntali/stl_parser.c"
        "puntali/puntale_database.c"
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
    REQUIRES 
        nvs_flash 
        bt 
        driver 
        esp_timer
        lvgl
        fatfs
        spi_flash
)
