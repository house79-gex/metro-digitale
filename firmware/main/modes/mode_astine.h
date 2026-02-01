#ifndef MODE_ASTINE_H
#define MODE_ASTINE_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/**
 * @file mode_astine.h
 * @brief Modalità astine con profili predefiniti
 * 
 * Gestione profili astine organizzati per gruppi con offset personalizzabili.
 */

// Gruppi astine
typedef enum {
    GRUPPO_ANTA_RIBALTA = 0,
    GRUPPO_PERSIANA,
    GRUPPO_CREMONESE,
    GRUPPO_PERSONALIZZATO
} astina_gruppo_t;

// Profilo astina
typedef struct {
    uint8_t id;                  // ID univoco profilo (0-9)
    char nome[48];               // Nome profilo
    astina_gruppo_t gruppo;      // Gruppo appartenenza
    float offset_mm;             // Offset lunghezza (negativo = taglia più corta)
    bool attivo;                 // Profilo attivo
    uint32_t color_hex;          // Colore gruppo
} astina_profile_t;

// Misura astina completa
typedef struct {
    const astina_profile_t *profile;  // Profilo utilizzato
    float lunghezza_grezza_mm;        // Lunghezza grezza misurata
    float lunghezza_taglio_mm;        // Lunghezza taglio (grezza + offset)
    float posizione_foro_mm;          // Posizione foro (opzionale)
    uint32_t timestamp;               // Timestamp misura
    char note[64];                    // Note aggiuntive
} astina_measurement_t;

// Stato modalità astine
typedef struct {
    uint8_t selected_profile_id;      // ID profilo selezionato
    astina_measurement_t current_measure;
    bool measurement_saved;
} mode_astine_state_t;

// Array profili predefiniti (10 profili)
extern astina_profile_t g_astine_profiles[10];

/**
 * @brief Inizializza modalità astine
 * 
 * Carica profili predefiniti.
 * 
 * @param state Stato modalità (output)
 */
void mode_astine_init(mode_astine_state_t *state);

/**
 * @brief Seleziona profilo
 * 
 * @param state Stato modalità
 * @param profile_id ID profilo (0-9)
 */
void mode_astine_select_profile(mode_astine_state_t *state, uint8_t profile_id);

/**
 * @brief Misura astina
 * 
 * Calcola automaticamente lunghezza taglio con offset profilo.
 * 
 * @param state Stato modalità
 * @param encoder_mm Lettura encoder
 */
void mode_astine_measure(mode_astine_state_t *state, float encoder_mm);

/**
 * @brief Salva misura su storage
 * 
 * @param state Stato modalità
 * @return true se salvato OK, false altrimenti
 */
bool mode_astine_save_to_session(mode_astine_state_t *state);

/**
 * @brief Invia misura via Bluetooth
 * 
 * @param state Stato modalità
 * @return true se invio OK, false altrimenti
 */
bool mode_astine_send_bluetooth(const mode_astine_state_t *state);

/**
 * @brief Ottieni profili per gruppo
 * 
 * @param gruppo Gruppo astine
 * @param profiles Array output profili (allocato dal chiamante)
 * @param max_profiles Dimensione massima array
 * @return Numero profili trovati
 */
uint8_t mode_astine_get_profiles(astina_gruppo_t gruppo,
                                astina_profile_t **profiles,
                                uint8_t max_profiles);

/**
 * @brief Ottieni profilo per ID
 * 
 * @param profile_id ID profilo
 * @return Puntatore a profilo, NULL se non trovato
 */
astina_profile_t* mode_astine_get_profile_by_id(uint8_t profile_id);

/**
 * @brief Imposta offset profilo personalizzato
 * 
 * @param profile_id ID profilo
 * @param offset_mm Nuovo offset in mm
 * @return true se impostato OK, false altrimenti
 */
bool mode_astine_set_profile_offset(uint8_t profile_id, float offset_mm);

/**
 * @brief Abilita/disabilita profilo
 * 
 * @param profile_id ID profilo
 * @param attivo true per attivo, false per disattivo
 * @return true se impostato OK, false altrimenti
 */
bool mode_astine_set_profile_active(uint8_t profile_id, bool attivo);

/**
 * @brief Resetta misura corrente
 * 
 * @param state Stato modalità
 */
void mode_astine_reset(mode_astine_state_t *state);

/**
 * @brief Ottieni nome gruppo
 * 
 * @param gruppo Gruppo astine
 * @return Nome gruppo
 */
const char* mode_astine_get_gruppo_name(astina_gruppo_t gruppo);

/**
 * @brief Ottieni colore gruppo
 * 
 * @param gruppo Gruppo astine
 * @return Colore hex
 */
uint32_t mode_astine_get_gruppo_color(astina_gruppo_t gruppo);

#endif // MODE_ASTINE_H
