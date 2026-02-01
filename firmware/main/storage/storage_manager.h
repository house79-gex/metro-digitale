#ifndef STORAGE_MANAGER_H
#define STORAGE_MANAGER_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

/**
 * @file storage_manager.h
 * @brief Sistema storage unificato con supporto multi-target
 * 
 * Supporta salvataggio su:
 * - SD Card (JSONL append-mode)
 * - USB OTG (pendrive)
 * - Bluetooth (chunked transfer)
 * - NVS interno (configurazioni)
 * 
 * Formati export: JSON, CSV, Binary
 */

// Target di storage disponibili
typedef enum {
    STORAGE_TARGET_SD_CARD = 0,    // SD Card principale
    STORAGE_TARGET_USB_OTG,        // USB OTG (pendrive)
    STORAGE_TARGET_BLUETOOTH,      // Transfer via BLE
    STORAGE_TARGET_INTERNAL_NVS    // NVS interno ESP32
} storage_target_t;

// Formati di export
typedef enum {
    EXPORT_FORMAT_JSON = 0,        // JSON human-readable
    EXPORT_FORMAT_CSV,             // CSV Excel-compatible
    EXPORT_FORMAT_BINARY           // Binary compatto
} export_format_t;

// Modalità misura
typedef enum {
    MEASURE_MODE_CALIBRO = 0,
    MEASURE_MODE_VETRI,
    MEASURE_MODE_ASTINE,
    MEASURE_MODE_FERMAVETRI
} measure_mode_t;

// Record singola misura
typedef struct {
    uint32_t timestamp;            // Unix timestamp
    measure_mode_t mode;           // Modalità operativa
    float value_mm;                // Valore principale in mm
    float value2_mm;               // Valore secondario (es. altezza per vetri)
    char material[32];             // Materiale (per vetri)
    char profile[48];              // Profilo (per astine)
    char notes[64];                // Note aggiuntive
    uint32_t crc32;                // CRC32 per integrità
} measurement_record_t;

// Sessione di misure (gruppo)
typedef struct {
    char session_id[32];           // ID sessione (YYYYMMDD_HHMMSS)
    uint32_t start_timestamp;      // Inizio sessione
    uint32_t end_timestamp;        // Fine sessione
    uint16_t count;                // Numero misure nella sessione
    measurement_record_t *records; // Array misure
} measurement_session_t;

// Informazioni storage
typedef struct {
    bool available;                // Storage disponibile
    uint64_t total_bytes;          // Spazio totale
    uint64_t used_bytes;           // Spazio usato
    uint64_t free_bytes;           // Spazio libero
    uint32_t file_count;           // Numero file salvati
} storage_info_t;

/**
 * @brief Inizializza storage manager
 * 
 * - Mount automatico SD card
 * - Creazione directory: /sd/sessions, /sd/exports, /sd/backup
 * - Inizializzazione NVS
 * 
 * @return true se OK, false altrimenti
 */
bool storage_manager_init(void);

/**
 * @brief Verifica disponibilità target storage
 * 
 * @param target Target da verificare
 * @return true se disponibile, false altrimenti
 */
bool storage_is_available(storage_target_t target);

/**
 * @brief Ottieni informazioni storage
 * 
 * @param target Target storage
 * @param info Struct output con informazioni
 * @return true se OK, false altrimenti
 */
bool storage_get_info(storage_target_t target, storage_info_t *info);

/**
 * @brief Salva misura su storage
 * 
 * Salvataggio automatico in formato JSONL append-mode.
 * File giornaliero: /sd/sessions/YYYYMMDD.jsonl
 * 
 * @param record Record misura da salvare
 * @param target Target storage (default SD_CARD)
 * @return true se salvato OK, false altrimenti
 */
bool storage_save_measurement(const measurement_record_t *record, storage_target_t target);

/**
 * @brief Export sessione su file
 * 
 * @param session Sessione da esportare
 * @param format Formato export (JSON/CSV/BINARY)
 * @param filename Nome file output
 * @param target Target storage
 * @return true se export OK, false altrimenti
 */
bool storage_export_to_file(const measurement_session_t *session, 
                            export_format_t format,
                            const char *filename,
                            storage_target_t target);

/**
 * @brief Export CSV Excel-compatible
 * 
 * Formato CSV con header:
 * Timestamp,Mode,Value(mm),Value2(mm),Material,Profile,Notes
 * 
 * @param session Sessione da esportare
 * @param filename Nome file CSV output
 * @return true se export OK, false altrimenti
 */
bool storage_export_csv(const measurement_session_t *session, const char *filename);

/**
 * @brief Invia sessione via Bluetooth (chunked transfer)
 * 
 * @param session Sessione da inviare
 * @param device_address Indirizzo BLE del dispositivo destinatario
 * @return true se invio OK, false altrimenti
 */
bool storage_send_via_bluetooth(const measurement_session_t *session, 
                                const char *device_address);

/**
 * @brief Lista file salvati
 * 
 * @param directory Directory da listare (es. "/sd/sessions")
 * @param files Array output nomi file (allocato dal chiamante)
 * @param max_files Dimensione massima array
 * @return Numero file trovati
 */
uint32_t storage_list_files(const char *directory, char **files, uint32_t max_files);

/**
 * @brief Mount USB OTG
 * 
 * @return true se mount OK, false altrimenti
 */
bool storage_usb_mount(void);

/**
 * @brief Unmount USB OTG
 * 
 * @return true se unmount OK, false altrimenti
 */
bool storage_usb_unmount(void);

/**
 * @brief Crea record misura
 * 
 * Helper per creare un record con CRC32 automatico.
 * 
 * @param mode Modalità misura
 * @param value_mm Valore principale
 * @param value2_mm Valore secondario (0 se non usato)
 * @param material Materiale (NULL se non applicabile)
 * @param profile Profilo (NULL se non applicabile)
 * @param notes Note (NULL se non applicabile)
 * @return Record creato
 */
measurement_record_t storage_create_record(measure_mode_t mode,
                                          float value_mm,
                                          float value2_mm,
                                          const char *material,
                                          const char *profile,
                                          const char *notes);

/**
 * @brief Calcola CRC32 di un record
 * 
 * @param record Record per cui calcolare CRC
 * @return CRC32 calcolato
 */
uint32_t storage_calculate_crc32(const measurement_record_t *record);

/**
 * @brief Verifica integrità record
 * 
 * @param record Record da verificare
 * @return true se CRC OK, false se corrotto
 */
bool storage_verify_record(const measurement_record_t *record);

/**
 * @brief Deinizializza storage manager
 */
void storage_manager_deinit(void);

#endif // STORAGE_MANAGER_H
