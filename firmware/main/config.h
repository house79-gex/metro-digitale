#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

// ============================================================================
// HARDWARE CONFIGURATION - ESP32-S3 5" Integrated Module
// ============================================================================

// Encoder pins (updated for ESP32-S3 integrated module)
#define ENCODER_PIN_A      GPIO_NUM_21   // Changed from GPIO_NUM_4
#define ENCODER_PIN_B      GPIO_NUM_43   // Changed from GPIO_NUM_5

// Physical SEND button
#define BUTTON_SEND_PIN    GPIO_NUM_47

// Display RGB Parallel (GPIO 1-16, 39-42, 45, 48)
#define LCD_PIN_R0         GPIO_NUM_1
#define LCD_PIN_R1         GPIO_NUM_2
#define LCD_PIN_R2         GPIO_NUM_3
#define LCD_PIN_R3         GPIO_NUM_4
#define LCD_PIN_R4         GPIO_NUM_5
#define LCD_PIN_G0         GPIO_NUM_6
#define LCD_PIN_G1         GPIO_NUM_7
#define LCD_PIN_G2         GPIO_NUM_8
#define LCD_PIN_G3         GPIO_NUM_9
#define LCD_PIN_G4         GPIO_NUM_10
#define LCD_PIN_G5         GPIO_NUM_11
#define LCD_PIN_B0         GPIO_NUM_12
#define LCD_PIN_B1         GPIO_NUM_13
#define LCD_PIN_B2         GPIO_NUM_14
#define LCD_PIN_B3         GPIO_NUM_15
#define LCD_PIN_B4         GPIO_NUM_16
#define LCD_PIN_HSYNC      GPIO_NUM_39
#define LCD_PIN_VSYNC      GPIO_NUM_40
#define LCD_PIN_DE         GPIO_NUM_41
#define LCD_PIN_PCLK       GPIO_NUM_42
#define LCD_PIN_BL         GPIO_NUM_45   // Backlight PWM
#define LCD_PIN_DISP       GPIO_NUM_48   // Display enable

// Touch GT911 I2C
#define TOUCH_I2C_SDA      GPIO_NUM_18
#define TOUCH_I2C_SCL      GPIO_NUM_8
#define TOUCH_I2C_INT      GPIO_NUM_4

// SD Card SPI (updated pins)
#define SD_PIN_CS          GPIO_NUM_10
#define SD_PIN_MOSI        GPIO_NUM_11
#define SD_PIN_MISO        GPIO_NUM_13
#define SD_PIN_CLK         GPIO_NUM_12

// Display resolution
#define LCD_WIDTH          800
#define LCD_HEIGHT         480
#define LCD_PIXEL_CLOCK_HZ (18 * 1000 * 1000)  // 18MHz

// ============================================================================

// Modalità operative
typedef enum {
    MODE_FERMAVETRO = 0,
    MODE_VETRO = 1,
    MODE_ASTINA = 2,
    MODE_CALIBRO = 3,
    MODE_RILIEVI_SPECIALI = 4
} OperatingMode;

// Configurazione puntale (per modalità fermavetro)
typedef struct {
    char nome[32];
    float offset_fisso_mm;
    float offset_mobile_mm;
    float distanza_minima_mm;
    bool attivo;
} PuntaleConfig;

// Configurazione materiale (per modalità vetri)
typedef struct {
    char nome[32];
    float gioco_vetro_mm;
    bool attivo;
} MaterialeConfig;

// Gruppo di astine
typedef struct {
    char nome[32];
    uint8_t colore_r;
    uint8_t colore_g;
    uint8_t colore_b;
} AstinaGruppo;

// Configurazione astina
#define MAX_ASTINE 32
#define MAX_GRUPPI_ASTINE 4

typedef struct {
    char nome[48];
    float offset_mm;
    uint8_t gruppo_idx;
    bool attivo;
} AstinaConfig;

// Variabile per formula (RILIEVI SPECIALI)
typedef struct {
    char nome[16];           // "L", "H", "B"
    char descrizione[48];    // "Larghezza", "Altezza", "Battuta"
    float valore;
    bool rilevato;
    bool obbligatorio;
} VariabileRilievo;

// Elemento calcolato (RILIEVI SPECIALI)
typedef struct {
    char nome[48];           // "Traversa Anta"
    char formula[64];        // "(L+6)/2"
    float risultato;
    uint8_t quantita_default;
    uint8_t quantita_attuale;
    bool inviato;
} ElementoCalcolato;

// Tipologia infisso (RILIEVI SPECIALI)
#define MAX_VARIABILI_RILIEVO 8
#define MAX_ELEMENTI_CALCOLATI 16
#define MAX_TIPOLOGIE_INFISSO 16

typedef struct {
    char nome[48];           // "Finestra 2 Ante"
    char icona[8];           // emoji
    char categoria[32];      // "Finestre"
    VariabileRilievo variabili[MAX_VARIABILI_RILIEVO];
    uint8_t num_variabili;
    ElementoCalcolato elementi[MAX_ELEMENTI_CALCOLATI];
    uint8_t num_elementi;
    bool attivo;
} TipologiaInfisso;

// Configurazione globale
#define MAX_PUNTALI 8
#define MAX_MATERIALI 8

typedef struct {
    // Generali
    OperatingMode modalita_corrente;
    bool auto_zero_enabled;
    float tolleranza_raggruppamento_mm;
    
    // Encoder
    float encoder_resolution_mm;
    int32_t encoder_pulses_per_mm;
    
    // Puntali
    uint8_t num_puntali;
    PuntaleConfig puntali[MAX_PUNTALI];
    uint8_t puntale_corrente_idx;
    
    // Materiali
    uint8_t num_materiali;
    MaterialeConfig materiali[MAX_MATERIALI];
    uint8_t materiale_corrente_idx;
    
    // Astine
    uint8_t num_gruppi_astine;
    AstinaGruppo gruppi_astine[MAX_GRUPPI_ASTINE];
    uint8_t num_astine;
    AstinaConfig astine[MAX_ASTINE];
    uint8_t astina_corrente_idx;
    
    // Tipologie Infisso (RILIEVI SPECIALI)
    uint8_t num_tipologie;
    TipologiaInfisso tipologie[MAX_TIPOLOGIE_INFISSO];
    uint8_t tipologia_corrente_idx;
    
    // Bluetooth
    bool bluetooth_enabled;
    char bt_device_name[32];
    bool auto_send_troncatrice;
    
    // Display
    uint8_t brightness;
    bool sleep_enabled;
    uint16_t sleep_timeout_sec;
    
} GlobalConfig;

// Stato runtime
typedef struct {
    // Encoder
    int32_t encoder_count;
    float position_mm;
    float zero_position_mm;
    bool is_zeroed;
    
    // Modalità Vetri
    bool vetro_larghezza_saved;
    float vetro_larghezza_mm;
    float vetro_altezza_mm;
    
    // Bluetooth
    bool bt_connected;
    char bt_peer_address[18];
    
    // UI
    bool screen_active;
    uint32_t last_activity_ms;
    
} RuntimeState;

// Funzioni di configurazione
void config_init_defaults(GlobalConfig *cfg);
void config_load_from_nvs(GlobalConfig *cfg);
void config_save_to_nvs(const GlobalConfig *cfg);

// Funzioni di gestione puntali
void config_add_puntale(GlobalConfig *cfg, const char *nome, float offset_fisso, 
                        float offset_mobile, float dist_min);
void config_set_puntale_corrente(GlobalConfig *cfg, uint8_t idx);

// Funzioni di gestione materiali
void config_add_materiale(GlobalConfig *cfg, const char *nome, float gioco);
void config_set_materiale_corrente(GlobalConfig *cfg, uint8_t idx);

// Funzioni di gestione astine
void config_add_gruppo_astine(GlobalConfig *cfg, const char *nome, 
                               uint8_t r, uint8_t g, uint8_t b);
void config_add_astina(GlobalConfig *cfg, const char *nome, 
                       float offset, uint8_t gruppo_idx);
void config_set_astina_corrente(GlobalConfig *cfg, uint8_t idx);
void config_remove_astina(GlobalConfig *cfg, uint8_t idx);

// Funzioni di gestione tipologie infisso
void config_add_tipologia(GlobalConfig *cfg, const char *nome, 
                          const char *icona, const char *categoria);
void config_add_variabile(TipologiaInfisso *tip, const char *nome,
                          const char *descrizione, bool obbligatorio);
void config_add_elemento(TipologiaInfisso *tip, const char *nome,
                         const char *formula, uint8_t quantita_default);
void config_set_tipologia_corrente(GlobalConfig *cfg, uint8_t idx);

// Variabili globali (extern)
extern GlobalConfig g_config;
extern RuntimeState g_state;

#endif // CONFIG_H
