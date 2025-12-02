#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>
#include <stdbool.h>

// Modalità operative
typedef enum {
    MODE_FERMAVETRO = 0,
    MODE_VETRO = 1,
    MODE_ASTINA = 2,
    MODE_CALIBRO = 3
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

// Variabili globali (extern)
extern GlobalConfig g_config;
extern RuntimeState g_state;

#endif // CONFIG_H
