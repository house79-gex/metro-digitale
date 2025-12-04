#ifndef BLUETOOTH_H
#define BLUETOOTH_H

#include <stdbool.h>
#include "esp_err.h"

// UUID del servizio BLE
#define BLE_SERVICE_UUID        "12345678-1234-1234-1234-123456789abc"
#define BLE_CHAR_TX_UUID        "12345678-1234-1234-1234-123456789abd"
#define BLE_CHAR_RX_UUID        "12345678-1234-1234-1234-123456789abe"

// Inizializzazione Bluetooth
esp_err_t bluetooth_init(void);

// Gestione connessione
bool bluetooth_is_connected(void);
const char* bluetooth_get_peer_address(void);

// Invio dati
esp_err_t bluetooth_send_fermavetro(float misura_mm, bool auto_start);
esp_err_t bluetooth_send_vetro(float larghezza_raw, float altezza_raw,
                                float larghezza_netta, float altezza_netta,
                                const char *materiale, uint32_t quantita, float gioco);
esp_err_t bluetooth_send_rilievo_speciale(const char *tipologia, const char *elemento,
                                          const char *formula, float misura_mm,
                                          uint8_t num_pezzi, bool auto_start);
esp_err_t bluetooth_send_json(const char *json_str);

// Task Bluetooth
void bluetooth_task(void *pvParameters);

#endif // BLUETOOTH_H
