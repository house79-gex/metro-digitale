#ifndef STORAGE_H
#define STORAGE_H

#include "esp_err.h"

// Inizializzazione storage NVS
esp_err_t storage_init(void);

// Funzioni per salvare/caricare configurazione
// (Utilizzano le funzioni in config.c)

#endif // STORAGE_H
