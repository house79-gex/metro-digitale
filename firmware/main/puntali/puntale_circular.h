#ifndef PUNTALE_CIRCULAR_H
#define PUNTALE_CIRCULAR_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file puntale_circular.h
 * @brief Sistema completo per puntali circolari da 30mm
 * 
 * Supporta misure esterne e interne con compensazione automatica diametro.
 * RIMUOVE il supporto per misure di profondità (non più supportate in v2.0).
 */

// Configurazione singolo puntale circolare
typedef struct {
    float diametro_mm;           // Diametro puntale (default 30.0mm)
    float offset_usura_mm;       // Offset per compensazione usura
    uint32_t contatore_utilizzi; // Contatore numero misure effettuate
    char nome[32];               // Nome identificativo (es. "Fisso SX", "Mobile DX")
    bool attivo;                 // Puntale attivo/disattivo
} puntale_config_t;

// Coppia di puntali (fisso sinistro + mobile destro)
typedef struct {
    puntale_config_t fisso_sx;   // Puntale fisso (sinistro)
    puntale_config_t mobile_dx;  // Puntale mobile (destro)
    float distanza_zero_mm;      // Distanza di riferimento quando a contatto (calibrazione)
    bool calibrato;              // Flag calibrazione completata
    uint32_t timestamp_calibrazione; // Timestamp ultima calibrazione
} puntale_pair_t;

/**
 * @brief Calcola distanza esterna tra puntali
 * 
 * Per misure esterne, la distanza reale è quella letta dall'encoder
 * (non si aggiungono i diametri).
 * 
 * @param pair Coppia di puntali
 * @param encoder_distance_mm Distanza letta dall'encoder
 * @return Distanza esterna in mm
 */
float puntale_calculate_external_distance(const puntale_pair_t *pair, float encoder_distance_mm);

/**
 * @brief Calcola distanza interna tra puntali
 * 
 * Per misure interne, si aggiungono i diametri di entrambi i puntali
 * alla distanza letta dall'encoder.
 * 
 * @param pair Coppia di puntali
 * @param encoder_distance_mm Distanza letta dall'encoder
 * @return Distanza interna in mm
 */
float puntale_calculate_internal_distance(const puntale_pair_t *pair, float encoder_distance_mm);

/**
 * @brief Calibrazione assistita dello zero
 * 
 * Esegue la calibrazione guidata per impostare la distanza zero quando
 * i puntali sono a contatto completo.
 * 
 * @param pair Coppia di puntali
 * @param encoder_reading_mm Lettura encoder quando puntali a contatto
 * @return true se calibrazione OK, false altrimenti
 */
bool puntale_calibrate_zero(puntale_pair_t *pair, float encoder_reading_mm);

/**
 * @brief Salva configurazione puntali su NVS
 * 
 * @param pair Coppia di puntali
 * @param nvs_namespace Namespace NVS (es. "puntali")
 * @return true se salvataggio OK, false altrimenti
 */
bool puntale_save_to_nvs(const puntale_pair_t *pair, const char *nvs_namespace);

/**
 * @brief Carica configurazione puntali da NVS
 * 
 * @param pair Coppia di puntali (output)
 * @param nvs_namespace Namespace NVS (es. "puntali")
 * @return true se caricamento OK, false altrimenti
 */
bool puntale_load_from_nvs(puntale_pair_t *pair, const char *nvs_namespace);

/**
 * @brief Inizializza coppia puntali con valori default
 * 
 * @param pair Coppia di puntali (output)
 */
void puntale_init_defaults(puntale_pair_t *pair);

/**
 * @brief Incrementa contatore utilizzi per entrambi i puntali
 * 
 * @param pair Coppia di puntali
 */
void puntale_increment_usage(puntale_pair_t *pair);

/**
 * @brief Ottieni stato calibrazione
 * 
 * @param pair Coppia di puntali
 * @return true se calibrati, false altrimenti
 */
bool puntale_is_calibrated(const puntale_pair_t *pair);

/**
 * @brief Resetta calibrazione
 * 
 * @param pair Coppia di puntali
 */
void puntale_reset_calibration(puntale_pair_t *pair);

/**
 * @brief Imposta offset usura puntale fisso
 * 
 * @param pair Coppia di puntali
 * @param offset_mm Offset usura in mm
 */
void puntale_set_fisso_wear_offset(puntale_pair_t *pair, float offset_mm);

/**
 * @brief Imposta offset usura puntale mobile
 * 
 * @param pair Coppia di puntali
 * @param offset_mm Offset usura in mm
 */
void puntale_set_mobile_wear_offset(puntale_pair_t *pair, float offset_mm);

#endif // PUNTALE_CIRCULAR_H
