# Schema Configurazione Metro Digitale

Versione: 1.0.0

## Panoramica

Questo documento descrive lo schema JSON utilizzato per la configurazione del Metro Digitale.

## Struttura Principale

```json
{
  "schema_version": "1.0.0",
  "version": "1.0.0",
  "nome": "Nome Progetto",
  "created": "2025-12-09T12:00:00",
  "modified": "2025-12-09T12:00:00",
  "hardware": { ... },
  "modes": [ ... ],
  "ui_layout": { ... },
  "icons": { ... },
  "menus": [ ... ],
  "tipologie": [ ... ],
  "astine": [ ... ],
  "fermavetri": [ ... ],
  "impostazioni": { ... }
}
```

## Campi

### schema_version
**Tipo**: `string`  
**Obbligatorio**: Sì  
**Descrizione**: Versione dello schema configurazione. Usato per migrazione.  
**Esempio**: `"1.0.0"`

### hardware
**Tipo**: `object`  
**Descrizione**: Configurazione hardware del dispositivo.

Struttura:
```json
{
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
    "auto_connect": false,
    "destinations": []
  },
  "display": {
    "width": 800,
    "height": 480,
    "brightness": 100
  }
}
```

### modes
**Tipo**: `array`  
**Descrizione**: Lista di modalità di misura configurabili.

Struttura elemento:
```json
{
  "id": "finestra_2_ante",
  "name": "Finestra 2 Ante",
  "category": "Finestre",
  "icon": "mdi:window-closed",
  "description": "Misura finestra a 2 ante",
  "workflow": [
    {
      "step": 1,
      "variable": "L",
      "description": "Larghezza",
      "probe_type": "interno",
      "required": true
    }
  ],
  "workflow_notes": "Note aggiuntive",
  "formula": "L + H - 5.0",
  "unit": "mm",
  "decimals": 2,
  "bt_enabled": false,
  "bt_format": "JSON",
  "bt_prefix": "",
  "bt_suffix": "",
  "bt_payload_template": "{\"result\": {result}}"
}
```

### ui_layout
**Tipo**: `object`  
**Descrizione**: Configurazione layout interfaccia utente.

Struttura:
```json
{
  "theme": "dark",
  "units": "mm",
  "decimals": 2,
  "language": "it",
  "screen_config": {
    "calibro": { ... },
    "configurazione": { ... },
    "tipi_misura": { ... }
  }
}
```

### icons
**Tipo**: `object`  
**Descrizione**: Riferimenti al catalogo icone locali.

Struttura:
```json
{
  "catalog_path": "resources/icons/icons.json",
  "default_icon": "mdi:ruler"
}
```

## Architettura a 3 Schermate

### 1. Calibro
Schermata principale per misurazioni in tempo reale:
- Display misura corrente
- Selettore tipo puntale (interno/esterno/profondità/battuta)
- Pulsanti Zero, Hold, Unità
- Quick Send via Bluetooth
- Toggle Bluetooth

### 2. Configurazione
Schermata impostazioni hardware e sistema:
- **Encoder**: Risoluzione, impulsi/mm, debounce, pin, direzione
- **Puntali**: Offset, colore, icona, descrizione
- **Bluetooth**: Nome, UUID, auto-connect, destinazioni
- **Display**: Unità, decimali, tema
- **Materiali**: Offset materiali
- **Preset**: Import/Export configurazione

### 3. Tipi di Misura
Schermata gestione modalità:
- Elenco modalità raggruppate per categoria
- Editor modalità con workflow
- Formula editor con preview
- Toggle invio Bluetooth per modalità

## Import/Export

### Misure
- **JSONL**: Un oggetto JSON per riga (append-safe)
- **CSV**: Formato CSV standard con intestazioni

Esempio JSONL:
```jsonl
{"id": 1, "timestamp": "2025-12-09T12:00:00", "value": 1234.56, "unit": "mm", "probe_type": "interno"}
{"id": 2, "timestamp": "2025-12-09T12:01:00", "value": 567.89, "unit": "mm", "probe_type": "esterno"}
```

### Configurazioni
- **JSON**: Schema completo con backup automatico
- **Migrazione**: Supporto automatico migrazione schema

## Path microSD e USB-C OTG

### Firmware ESP32
- microSD: `/sd/`
- USB MSC: `/usb/`

### Esempi Path
```
/sd/measures.jsonl
/sd/config.json
/usb/backup/config_20251209.json
```

## Icone Locali

Le icone locali sono gestite tramite `icon_manager`:
- Import SVG/PNG/JPG
- Catalogo in `resources/icons/icons.json`
- Caching automatico

Struttura catalogo:
```json
{
  "custom_icon_1": {
    "filename": "custom_icon_1.svg",
    "format": "svg",
    "original_name": "myicon.svg",
    "metadata": {
      "category": "custom",
      "tags": ["door", "window"]
    }
  }
}
```

## Migrazione Schema

Il sistema supporta migrazione automatica tra versioni schema:

- **0.0.0 → 1.0.0**: Aggiunge campi `hardware`, `modes`, `ui_layout`, `icons`

Migrazione gestita da `io_manager.import_config()` con parametro `migrate=True`.

## Note

- Tutti i file devono essere UTF-8
- Timestamp in formato ISO 8601
- Valori float per misure
- Colori in formato hex (#RRGGBB)
