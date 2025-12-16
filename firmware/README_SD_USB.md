# Metro Digitale - Supporto microSD e USB-C OTG

## Panoramica

Il firmware Metro Digitale supporta l'import/export di misure e configurazioni tramite:
- **microSD**: Slot SD card per storage persistente
- **USB-C OTG**: Modalità Mass Storage Class (MSC) per accesso diretto da PC

## Path Filesystem

### microSD
- **Mount Point**: `/sd`
- **Esempi**:
  - `/sd/measures.jsonl` - Misure in formato JSONL
  - `/sd/config.json` - Configurazione completa
  - `/sd/backup/config_20251209.json` - Backup configurazione

### USB-C OTG (MSC)
- **Mount Point**: `/usb`
- **Esempi**:
  - `/usb/import/measures.jsonl` - Importa misure
  - `/usb/export/config.json` - Esporta configurazione

## Formati File

### Misure (JSONL)
File `measures.jsonl` - Un oggetto JSON per riga (append-safe):

```jsonl
{"id": 1, "timestamp": "2025-12-09T12:00:00", "value": 1234.56, "unit": "mm", "probe_type": "interno", "material": "alluminio"}
{"id": 2, "timestamp": "2025-12-09T12:01:00", "value": 567.89, "unit": "mm", "probe_type": "esterno", "material": "pvc"}
```

**Campi**:
- `id` (int): ID misura progressivo
- `timestamp` (string): Timestamp ISO 8601
- `value` (float): Valore misura
- `unit` (string): Unità di misura (mm, cm, m, in, ft)
- `probe_type` (string): Tipo puntale (interno, esterno, profondità, battuta)
- `material` (string): Materiale (opzionale)
- `notes` (string): Note aggiuntive (opzionale)

### Misure (CSV)
File `measures.csv` - Formato CSV standard:

```csv
id,timestamp,value,unit,probe_type,material,notes
1,2025-12-09T12:00:00,1234.56,mm,interno,alluminio,
2,2025-12-09T12:01:00,567.89,mm,esterno,pvc,
```

### Configurazione (JSON)
File `config.json` - Configurazione completa:

```json
{
  "schema_version": "1.0.0",
  "version": "1.0.0",
  "nome": "Metro Digitale",
  "created": "2025-12-09T00:00:00",
  "modified": "2025-12-09T12:00:00",
  "hardware": {
    "encoder": {
      "resolution": 0.01,
      "pulses_per_mm": 100,
      "debounce": 10,
      "pin_a": 4,
      "pin_b": 5,
      "direction": "normal"
    },
    "probes": [
      {
        "id": "interno",
        "name": "Interno",
        "offset": 0.0,
        "color": "#00ff88",
        "icon": "mdi:ruler"
      }
    ],
    "bluetooth": {
      "name": "MetroDigitale",
      "uuid": "",
      "auto_connect": false
    },
    "display": {
      "width": 800,
      "height": 480,
      "brightness": 100
    }
  },
  "modes": [],
  "ui_layout": {
    "theme": "dark",
    "units": "mm",
    "decimals": 2,
    "language": "it"
  },
  "icons": {}
}
```

## Operazioni

### Import Misure

1. **Da microSD**:
   ```c
   // Leggi file JSONL dalla SD
   FILE* f = fopen("/sd/measures.jsonl", "r");
   // Parse linee JSON
   ```

2. **Da USB**:
   ```c
   // Leggi file da USB OTG
   FILE* f = fopen("/usb/import/measures.jsonl", "r");
   ```

### Export Misure

1. **Su microSD (append)**:
   ```c
   // Append misura a file JSONL
   FILE* f = fopen("/sd/measures.jsonl", "a");
   fprintf(f, "{\"id\": %d, \"value\": %.2f}\n", id, value);
   fclose(f);
   ```

2. **Su USB**:
   ```c
   // Export completo su USB
   FILE* f = fopen("/usb/export/measures.jsonl", "w");
   // Scrivi tutte le misure
   fclose(f);
   ```

### Import/Export Configurazione

1. **Import con backup**:
   ```c
   // Backup config esistente
   rename("/sd/config.json", "/sd/config.json.bak");
   
   // Import nuova config
   FILE* f = fopen("/usb/config.json", "r");
   // Parse JSON e applica
   ```

2. **Export con validazione**:
   ```c
   // Valida config
   if (validate_config(&config)) {
       // Export su SD
       FILE* f = fopen("/sd/config.json", "w");
       // Scrivi JSON
       fclose(f);
   }
   ```

## Schema Migrazione

Il sistema supporta migrazione automatica tra versioni schema:

- **0.0.0 → 1.0.0**: Aggiunge campi `hardware`, `modes`, `ui_layout`, `icons`
- **1.0.0 → 1.1.0**: (Future migrations)

La migrazione è gestita automaticamente dal configuratore Windows all'import.

## Hardware Requirements

### microSD
- **Slot**: SD/MMC standard
- **Filesystem**: FAT32 (consigliato) o exFAT
- **Capacità**: 1GB - 32GB
- **Pin ESP32**:
  - CMD: GPIO 15
  - CLK: GPIO 14
  - D0: GPIO 2
  - D1: GPIO 4
  - D2: GPIO 12
  - D3: GPIO 13

### USB-C OTG
- **Modalità**: USB Host + MSC
- **Connettore**: USB-C con supporto OTG
- **Pin ESP32**:
  - D+: GPIO 19
  - D-: GPIO 18
- **Alimentazione**: 5V via USB o batteria

## API Firmware

### Funzioni Base

```c
// Inizializzazione SD
bool sd_init(void);

// Inizializzazione USB OTG
bool usb_init(void);

// Mount filesystem
bool mount_sd(const char* mount_point);
bool mount_usb(const char* mount_point);

// Import/Export misure
int import_measures_jsonl(const char* filepath);
int export_measures_jsonl(const char* filepath, measure_t* measures, int count);

// Import/Export config
config_t* import_config(const char* filepath);
bool export_config(const char* filepath, config_t* config);
```

### Gestione Errori

```c
typedef enum {
    SD_OK = 0,
    SD_ERROR_MOUNT,
    SD_ERROR_READ,
    SD_ERROR_WRITE,
    SD_ERROR_FORMAT,
    USB_OK = 0,
    USB_ERROR_NOT_CONNECTED,
    USB_ERROR_NO_DEVICE,
    USB_ERROR_MOUNT
} storage_error_t;
```

## Sicurezza

- **Validazione JSON**: Sempre validare JSON prima di applicare configurazione
- **Backup automatico**: Backup config prima di import
- **Limiti dimensione**: Limitare dimensione file import (max 1MB per config)
- **Sanitizzazione path**: Validare path per evitare directory traversal

## Testing

### Test SD Card
```bash
# Mount SD
mount /sd

# Test scrittura
echo "test" > /sd/test.txt

# Test lettura
cat /sd/test.txt

# Cleanup
rm /sd/test.txt
```

### Test USB OTG
```bash
# Collega USB device
# Mount dovrebbe essere automatico

# Test lettura
ls /usb

# Test import config
cat /usb/config.json
```

## Troubleshooting

### SD Card non montata
- Verificare connessioni hardware
- Verificare formato filesystem (FAT32)
- Controllare log errori ESP32

### USB OTG non funzionante
- Verificare cavo USB-C supporta OTG
- Controllare alimentazione (min 5V 500mA)
- Verificare driver USB host ESP32

### Errori import/export
- Verificare permessi file
- Controllare formato JSON/JSONL
- Verificare spazio disponibile

## Riferimenti

- [ESP-IDF SD/MMC Driver](https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/storage/sdmmc.html)
- [ESP-IDF USB Host](https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/usb_host.html)
- [JSON Schema Documentation](../docs/config_schema.md)
