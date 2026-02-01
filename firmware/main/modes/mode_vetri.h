#ifndef MODE_VETRI_H
#define MODE_VETRI_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/**
 * @file mode_vetri.h
 * @brief Modalità vetri L×H con wizard
 * 
 * Misura Larghezza × Altezza con gestione giochi materiali.
 */

// Tipi di materiale supportati
typedef enum {
    MATERIAL_ALLUMINIO = 0,
    MATERIAL_LEGNO,
    MATERIAL_PVC,
    MATERIAL_CUSTOM
} material_type_t;

// Configurazione materiale
typedef struct {
    char nome[32];               // Nome materiale
    float gioco_mm;              // Gioco per lato (totale = gioco_mm * 2)
    uint32_t color_hex;          // Colore UI (RGB hex)
    bool attivo;                 // Materiale attivo
} material_config_t;

// Misura vetro completa
typedef struct {
    float larghezza_raw_mm;      // Larghezza grezza misurata
    float altezza_raw_mm;        // Altezza grezza misurata
    float larghezza_netta_mm;    // Larghezza netta (raw - gioco)
    float altezza_netta_mm;      // Altezza netta (raw - gioco)
    material_type_t materiale;   // Materiale selezionato
    uint32_t timestamp;          // Timestamp misura
    char note[64];               // Note aggiuntive
} vetro_measurement_t;

// Step wizard
typedef enum {
    WIZARD_STEP_SELECT_MATERIAL = 0,
    WIZARD_STEP_MEASURE_L,
    WIZARD_STEP_MEASURE_H,
    WIZARD_STEP_REVIEW,
    WIZARD_STEP_SAVE
} vetri_wizard_step_t;

// Stato modalità vetri
typedef struct {
    vetri_wizard_step_t current_step;
    material_type_t selected_material;
    vetro_measurement_t current_measure;
    bool larghezza_saved;
    bool altezza_saved;
} mode_vetri_state_t;

// Array materiali predefiniti
extern const material_config_t g_materials[4];

/**
 * @brief Inizializza modalità vetri
 * 
 * @param state Stato modalità (output)
 */
void mode_vetri_init(mode_vetri_state_t *state);

/**
 * @brief Imposta materiale selezionato
 * 
 * @param state Stato modalità
 * @param material Materiale da selezionare
 */
void mode_vetri_set_material(mode_vetri_state_t *state, material_type_t material);

/**
 * @brief Misura larghezza
 * 
 * Calcola automaticamente larghezza netta con gioco materiale.
 * 
 * @param state Stato modalità
 * @param encoder_mm Lettura encoder
 */
void mode_vetri_measure_larghezza(mode_vetri_state_t *state, float encoder_mm);

/**
 * @brief Misura altezza
 * 
 * Calcola automaticamente altezza netta con gioco materiale.
 * 
 * @param state Stato modalità
 * @param encoder_mm Lettura encoder
 */
void mode_vetri_measure_altezza(mode_vetri_state_t *state, float encoder_mm);

/**
 * @brief Salva misura su storage
 * 
 * @param state Stato modalità
 * @return true se salvato OK, false altrimenti
 */
bool mode_vetri_save_to_session(mode_vetri_state_t *state);

/**
 * @brief Invia misura via Bluetooth ad app Android
 * 
 * Formato JSON:
 * {
 *   "larghezza_raw": 1200.0,
 *   "altezza_raw": 1500.0,
 *   "larghezza_netta": 1188.0,
 *   "altezza_netta": 1488.0,
 *   "materiale": "Alluminio",
 *   "gioco": 12.0
 * }
 * 
 * @param state Stato modalità
 * @return true se invio OK, false altrimenti
 */
bool mode_vetri_send_bluetooth(const mode_vetri_state_t *state);

/**
 * @brief Avanza al prossimo step wizard
 * 
 * @param state Stato modalità
 */
void mode_vetri_next_step(mode_vetri_state_t *state);

/**
 * @brief Torna allo step precedente wizard
 * 
 * @param state Stato modalità
 */
void mode_vetri_prev_step(mode_vetri_state_t *state);

/**
 * @brief Resetta wizard
 * 
 * @param state Stato modalità
 */
void mode_vetri_reset(mode_vetri_state_t *state);

/**
 * @brief Ottieni configurazione materiale
 * 
 * @param material Tipo materiale
 * @return Puntatore a configurazione materiale
 */
const material_config_t* mode_vetri_get_material_config(material_type_t material);

/**
 * @brief Calcola gioco totale per materiale
 * 
 * @param material Tipo materiale
 * @return Gioco totale in mm (per due lati)
 */
float mode_vetri_get_total_gioco(material_type_t material);

#endif // MODE_VETRI_H
