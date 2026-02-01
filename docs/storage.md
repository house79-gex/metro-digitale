# Storage e Export - Metro Digitale v2.0

Sistema storage unificato con supporto multi-target e formati multipli.

## Architettura Storage

### Target Disponibili

1. **SD Card** (Primario)
   - Salvataggio automatico JSONL
   - Export manuali CSV/JSON
   - Backup configurazioni

2. **Bluetooth** (Transfer)
   - Chunked transfer a smartphone/PC
   - Sessioni complete
   - JSON/CSV via BLE

3. **USB OTG** (Export)
   - Pendrive USB-C
   - Export rapidi
   - Backup offline

4. **NVS Interno** (Configurazioni)
   - Calibrazioni puntali
   - Profili personalizzati
   - Impostazioni sistema

## Formato File JSONL

### Salvataggio Automatico

File giornaliero: `/sd/sessions/YYYYMMDD.jsonl`

Ogni misura è una riga JSON (JSON Lines format):

```jsonl
{"timestamp":1706800100,"mode":"calibro","value":123.45,"value2":0.0,"material":"","profile":"","notes":"","crc32":3245678901}
{"timestamp":1706800200,"mode":"vetri","value":1188.0,"value2":1488.0,"material":"Alluminio","profile":"","notes":"","crc32":4567891234}
{"timestamp":1706800300,"mode":"astine","value":1182.0,"value2":0.0,"material":"","profile":"Superiore AR","notes":"","crc32":5678912345}
```

### Struttura Record

```c
typedef struct {
    uint32_t timestamp;      // Unix timestamp
    char mode[16];           // "calibro", "vetri", "astine", "fermavetri"
    float value;             // Valore principale (mm)
    float value2;            // Valore secondario (mm) - 0 se non usato
    char material[32];       // Materiale (per vetri)
    char profile[48];        // Profilo (per astine)
    char notes[64];          // Note aggiuntive
    uint32_t crc32;          // CRC32 per integrità
} measurement_record_t;
```

### Vantaggi JSONL

- ✅ **Append-mode**: Scritture veloci senza riscrittura file
- ✅ **Streaming**: Lettura riga per riga senza caricare tutto in RAM
- ✅ **Fault-tolerant**: Corruzione di una riga non invalida file intero
- ✅ **Human-readable**: Debug facile
- ✅ **Standard**: Supportato da molti tool

## Export CSV

### Formato Excel-Compatible

File: `/sd/exports/export_YYYYMMDD_HHMMSS.csv`

```csv
Timestamp,Mode,Value(mm),Value2(mm),Material,Profile,Notes
2024-02-01 10:15:00,Calibro,123.45,0.00,,,
2024-02-01 10:16:00,Vetri,1188.00,1488.00,Alluminio,,
2024-02-01 10:17:00,Astine,1182.00,0.00,,Superiore AR,
```

### Caratteristiche

- **Header**: Prima riga con nomi colonne
- **Separatore**: Virgola (`,`)
- **Quote**: Campi con virgole/newline tra `"`
- **Encoding**: UTF-8
- **Newline**: `\n` (Unix style)

### Utilizzo

```c
// Esporta sessione in CSV
measurement_session_t session = {...};
storage_export_csv(&session, "export_20240201.csv");
```

### Import in Excel

1. Apri Excel
2. Dati → Da testo/CSV
3. Seleziona file `.csv`
4. Encoding: UTF-8
5. Separatore: Virgola
6. Importa

## Export JSON

### Formato Completo

File: `/sd/exports/session_YYYYMMDD_HHMMSS.json`

```json
{
  "session_id": "20240201_101500",
  "start_timestamp": 1706800100,
  "end_timestamp": 1706800500,
  "count": 3,
  "records": [
    {
      "timestamp": 1706800100,
      "mode": "calibro",
      "value_mm": 123.45,
      "value2_mm": 0.0,
      "material": "",
      "profile": "",
      "notes": "",
      "crc32": 3245678901
    },
    {
      "timestamp": 1706800200,
      "mode": "vetri",
      "value_mm": 1188.0,
      "value2_mm": 1488.0,
      "material": "Alluminio",
      "profile": "",
      "notes": "",
      "crc32": 4567891234
    }
  ]
}
```

### Utilizzo

```c
// Esporta sessione in JSON
storage_export_to_file(&session, EXPORT_FORMAT_JSON, 
                      "session.json", STORAGE_TARGET_SD_CARD);
```

## Transfer Bluetooth

### Chunked Transfer

Per sessioni grandi (>4KB MTU BLE), il transfer è diviso in chunk:

```c
bool storage_send_via_bluetooth(const measurement_session_t *session, 
                                const char *device_address);
```

### Protocollo

1. **Header Chunk**:
```json
{
  "type": "session_start",
  "session_id": "20240201_101500",
  "total_chunks": 10,
  "total_bytes": 45678
}
```

2. **Data Chunks** (1-N):
```json
{
  "type": "data_chunk",
  "chunk_id": 1,
  "data": "base64_encoded_data..."
}
```

3. **End Chunk**:
```json
{
  "type": "session_end",
  "crc32": 1234567890
}
```

### App Android

L'app Android riceve i chunk e:
1. Riassembla la sessione
2. Verifica CRC32
3. Salva in database locale
4. Genera report PDF

## Struttura Directory SD Card

```
/sd/
├── sessions/                    # Misure giornaliere
│   ├── 20240201.jsonl          # 156 KB
│   ├── 20240202.jsonl          # 203 KB
│   └── 20240203.jsonl          # 178 KB
│
├── exports/                     # Export manuali
│   ├── export_20240201_1030.csv    # 45 KB
│   ├── session_20240201.json       # 67 KB
│   └── backup_20240205.bin         # 234 KB (binary)
│
└── backup/                      # Backup configurazioni
    ├── config_20240201.json    # 12 KB
    ├── profiles_20240201.json  # 8 KB
    └── calibration_20240201.json # 4 KB
```

### Gestione Spazio

- **Rotazione automatica**: File >30 giorni archiviati
- **Compressione**: File vecchi compressi con gzip
- **Limite**: Alert quando SD <100MB liberi

## API Storage Manager

### Inizializzazione

```c
// Init storage manager (mount SD, crea directory)
bool storage_manager_init(void);
```

### Salvataggio Misure

```c
// Crea record
measurement_record_t record = storage_create_record(
    MEASURE_MODE_CALIBRO,
    123.45,  // value_mm
    0.0,     // value2_mm
    NULL,    // material
    NULL,    // profile
    "Test"   // notes
);

// Salva su SD (append a file giornaliero)
bool saved = storage_save_measurement(&record, STORAGE_TARGET_SD_CARD);
```

### Export Sessione

```c
// Carica sessione da file JSONL
measurement_session_t session;
load_session_from_file("20240201.jsonl", &session);

// Export CSV
storage_export_csv(&session, "export_20240201.csv");

// Export JSON completo
storage_export_to_file(&session, EXPORT_FORMAT_JSON, 
                      "session_20240201.json",
                      STORAGE_TARGET_SD_CARD);

// Transfer Bluetooth
storage_send_via_bluetooth(&session, "AA:BB:CC:DD:EE:FF");
```

### Verifica Integrità

```c
// Verifica CRC32 record
if (!storage_verify_record(&record)) {
    ESP_LOGE(TAG, "Record corrotto!");
    // Handle error
}
```

## USB OTG

### Mount Pendrive

```c
// Mount USB OTG
if (storage_usb_mount()) {
    // USB disponibile su /usb
    
    // Copia file
    copy_file("/sd/exports/export.csv", "/usb/export.csv");
    
    // Unmount quando finito
    storage_usb_unmount();
}
```

### Requisiti Hardware

- Connettore USB-C OTG
- Alimentazione: 5V/500mA per pendrive
- Filesystem: FAT32/exFAT

## Backup e Restore

### Backup Configurazioni

```bash
# Backup completo (JSON)
{
  "version": "2.0",
  "timestamp": 1706800000,
  "puntali": {
    "fisso_sx": {...},
    "mobile_dx": {...},
    "calibrato": true,
    "distanza_zero_mm": 0.005
  },
  "profiles": [...],
  "settings": {...}
}
```

### Procedura Backup

1. Menu Settings → "💾 Export Backup"
2. Seleziona target (SD/USB)
3. Conferma export
4. File salvato in `/backup/`

### Procedura Restore

1. Copia file backup su SD
2. Menu Settings → "📥 Import Backup"
3. Seleziona file backup
4. Conferma import
5. Reboot dispositivo

## Performance

### Scrittura JSONL

- **Latency**: <5ms per record
- **Throughput**: >100 record/sec
- **Buffer**: 4KB RAM buffer

### Export CSV

- **100 records**: ~50ms
- **1000 records**: ~500ms
- **10000 records**: ~5sec

### Transfer BLE

- **MTU**: 512 bytes
- **Chunk size**: 400 bytes payload
- **Throughput**: ~20KB/sec
- **Latency**: 50ms/chunk

## Troubleshooting

### SD Card Non Rilevata

1. Verificare inserimento card
2. Controllare formato (FAT32)
3. Testare con lettore PC
4. Provare card diversa

### File JSONL Corrotto

```bash
# Verifica integrità ogni riga
cat 20240201.jsonl | while read line; do
    echo $line | jq . >/dev/null || echo "Riga corrotta: $line"
done
```

### Export CSV Errore

1. Verificare spazio disponibile
2. Controllare permessi directory
3. Verificare formato date/time

### BLE Transfer Fallisce

1. Controllare connessione BLE
2. Verificare MTU sufficiente (>512)
3. Ridurre dimensione sessione
4. Retry con timeout maggiore

## Best Practices

### Performance

- Usa JSONL per salvataggi real-time
- Export CSV solo per analisi offline
- Limita sessioni BLE a <100 record

### Affidabilità

- Backup settimanale su USB
- Verifica CRC32 sempre
- Mantieni <80% spazio SD utilizzato

### Manutenzione

- Archivia file vecchi mensilmente
- Comprimi sessioni >1MB
- Test restore backup trimestralmente
