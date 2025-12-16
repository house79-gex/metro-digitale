# Schema Configurazione Metro Digitale

Documentazione dello schema JSON per la configurazione del Metro Digitale ESP32.

## Versione Schema: 2.0.0

## Struttura Principale

```json
{
  "version": "1.0.0",
  "schema_version": "2.0.0",
  "nome": "Nome Progetto",
  "created": "2024-01-01T00:00:00",
  "modified": "2024-01-01T00:00:00",
  "menus": [...],
  "tipologie": [...],
  "astine": [...],
  "fermavetri": [...],
  "modes": [...],
  "hardware": {...},
  "ui_layout": {...},
  "icons": {...},
  "impostazioni": {...}
}
```

## Campi Root

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `version` | string | Versione progetto (legacy) |
| `schema_version` | string | Versione schema configurazione |
| `nome` | string | Nome del progetto |
| `created` | string | Data/ora creazione (ISO 8601) |
| `modified` | string | Data/ora ultima modifica (ISO 8601) |
| `menus` | array | Struttura menu principale |
| `tipologie` | array | Tipologie di infisso configurate |
| `astine` | array | Profili astina disponibili |
| `fermavetri` | array | Profili fermavetro disponibili |
| `modes` | array | **NUOVO** - Modalità di misura |
| `hardware` | object | **NUOVO** - Configurazione hardware |
| `ui_layout` | object | **NUOVO** - Layout interfaccia utente |
| `icons` | object | **NUOVO** - Registry icone locali |
| `impostazioni` | object | Impostazioni generali |

---

## modes - Modalità di Misura

Array di oggetti `MeasureMode` che definiscono le modalità di misura disponibili.

### Struttura MeasureMode

```json
{
  "id": "finestra_2_ante",
  "nome": "Finestra 2 Ante",
  "categoria": "Finestre",
  "icona": "mdi:window-closed",
  "workflow": [
    {
      "id": "step_1",
      "description": "Misura larghezza totale",
      "variable": "L",
      "probe_type": "internal",
      "constraints": {
        "min": 500,
        "max": 3000
      }
    },
    {
      "id": "step_2",
      "description": "Misura altezza totale",
      "variable": "H",
      "probe_type": "internal",
      "constraints": {
        "min": 500,
        "max": 2500
      }
    }
  ],
  "formule": {
    "Telaio Esterno": "(L + 6) / 2",
    "Altezza Anta": "H - 10"
  },
  "send_bt": true,
  "bt_payload_template": "{mode},{L},{H},{results}",
  "unita": "mm",
  "decimali": 2
}
```

### Campi MeasureMode

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | string | Identificatore univoco |
| `nome` | string | Nome visualizzato |
| `categoria` | string | Categoria (es: "Finestre", "Porte") |
| `icona` | string | Riferimento icona Iconify o locale |
| `workflow` | array | Sequenza passi di misura |
| `formule` | object | Mappa nome→formula calcoli |
| `send_bt` | boolean | Invio automatico Bluetooth |
| `bt_payload_template` | string | Template payload BT |
| `unita` | string | Unità di misura ("mm", "cm", "inch") |
| `decimali` | integer | Numero decimali visualizzati |

### ModeWorkflowStep

Passo nel workflow di acquisizione misure.

```json
{
  "id": "step_1",
  "description": "Misura larghezza",
  "variable": "L",
  "probe_type": "internal",
  "constraints": {
    "min": 0,
    "max": 5000,
    "required": true
  }
}
```

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | string | ID passo |
| `description` | string | Descrizione mostrata utente |
| `variable` | string | Nome variabile (L, H, B, S, etc.) |
| `probe_type` | string | Tipo puntale: "internal", "external", "depth", "step" |
| `constraints` | object | Vincoli opzionali (min, max, required) |

---

## hardware - Configurazione Hardware

Parametri hardware del dispositivo.

```json
{
  "encoder": {
    "resolution": 0.01,
    "pulses_per_mm": 100,
    "debounce_ms": 5,
    "pin_a": 4,
    "pin_b": 5,
    "invert_direction": false
  },
  "probes": {
    "internal": {
      "offset": 0.0,
      "color": "#00ff88",
      "icon": "local:probe_internal",
      "description": "Puntali interni"
    },
    "external": {
      "offset": 0.0,
      "color": "#ff8800",
      "icon": "local:probe_external",
      "description": "Puntali esterni"
    },
    "depth": {
      "offset": 0.0,
      "color": "#0088ff",
      "icon": "local:probe_depth",
      "description": "Asta profondità"
    },
    "step": {
      "offset": 0.0,
      "color": "#ff0088",
      "icon": "local:probe_step",
      "description": "Battuta"
    }
  },
  "bluetooth": {
    "enabled": true,
    "name": "MetroDigitale",
    "uuid": "00001101-0000-1000-8000-00805F9B34FB",
    "auto_connect": true,
    "destinations": ["PC", "Tablet", "App"]
  },
  "display": {
    "width": 800,
    "height": 480,
    "brightness": 80,
    "orientation": "landscape"
  },
  "materials": {
    "alluminio": {"offset": -0.5, "color": "#c0c0c0"},
    "legno": {"offset": 0.0, "color": "#8b4513"},
    "pvc": {"offset": 0.2, "color": "#ffffff"}
  }
}
```

### encoder

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `resolution` | float | Risoluzione mm |
| `pulses_per_mm` | integer | Impulsi encoder per mm |
| `debounce_ms` | integer | Debounce in millisecondi |
| `pin_a` | integer | GPIO pin A encoder |
| `pin_b` | integer | GPIO pin B encoder |
| `invert_direction` | boolean | Inverti direzione conteggio |

### probes

Configurazione per ogni tipo di puntale.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `offset` | float | Offset calibrazione (mm) |
| `color` | string | Colore HEX visualizzazione |
| `icon` | string | Riferimento icona |
| `description` | string | Descrizione |

### bluetooth

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `enabled` | boolean | Bluetooth abilitato |
| `name` | string | Nome dispositivo Bluetooth |
| `uuid` | string | UUID servizio |
| `auto_connect` | boolean | Connessione automatica |
| `destinations` | array | Lista destinazioni predefinite |

### display

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `width` | integer | Larghezza pixel |
| `height` | integer | Altezza pixel |
| `brightness` | integer | Luminosità (0-100) |
| `orientation` | string | "landscape" o "portrait" |

### materials

Mappa materiale → offset/colore.

```json
{
  "nome_materiale": {
    "offset": 0.0,
    "color": "#rrggbb"
  }
}
```

---

## ui_layout - Layout Interfaccia

Configurazione UI e preferenze visualizzazione.

```json
{
  "theme": "dark",
  "units": "mm",
  "decimals": 2,
  "screen_mode": "calibro",
  "shortcuts": {
    "zero": "BTN_ZERO",
    "hold": "BTN_HOLD",
    "unit": "BTN_UNIT"
  },
  "presets": [
    {
      "id": "preset_1",
      "name": "Standard Alluminio",
      "settings": {
        "material": "alluminio",
        "probe": "internal"
      }
    }
  ]
}
```

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `theme` | string | "dark" o "light" |
| `units` | string | "mm", "cm", "inch" |
| `decimals` | integer | Decimali visualizzati |
| `screen_mode` | string | Schermata iniziale: "calibro", "config", "modes" |
| `shortcuts` | object | Mappa shortcut → azione |
| `presets` | array | Preset configurazione rapidi |

---

## icons - Registry Icone Locali

Registry delle icone SVG/PNG/JPG importate localmente.

```json
{
  "probe_internal": {
    "filename": "probe_internal.svg",
    "category": "probe",
    "description": "Puntali interni",
    "format": "svg",
    "size": 2048
  },
  "custom_logo": {
    "filename": "custom_logo.png",
    "category": "custom",
    "description": "Logo personalizzato",
    "format": "png",
    "size": 15360
  }
}
```

### Campi Icona

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `filename` | string | Nome file in resources/icons/ |
| `category` | string | Categoria icona |
| `description` | string | Descrizione |
| `format` | string | "svg", "png", "jpg" |
| `size` | integer | Dimensione file bytes |

---

## Migrazione da Schema 1.0

Lo schema 2.0 mantiene compatibilità con 1.0. Campi mancanti vengono aggiunti automaticamente con valori di default durante l'import.

### Processo Migrazione

1. Carica JSON schema 1.0
2. Rileva assenza `schema_version`
3. Aggiunge campi nuovi:
   - `schema_version: "2.0.0"`
   - `modes: []`
   - `hardware: {...defaults...}`
   - `ui_layout: {...defaults...}`
   - `icons: {}`
4. Preserva tutti i campi esistenti

### Esempio Migrazione

**Schema 1.0 Input:**
```json
{
  "version": "1.0.0",
  "nome": "Progetto Vecchio",
  "menus": [...],
  "tipologie": [...]
}
```

**Schema 2.0 Output:**
```json
{
  "version": "1.0.0",
  "schema_version": "2.0.0",
  "nome": "Progetto Vecchio",
  "menus": [...],
  "tipologie": [...],
  "modes": [],
  "hardware": {
    "encoder": {...defaults...},
    "bluetooth": {...defaults...},
    "display": {...defaults...}
  },
  "ui_layout": {
    "theme": "dark",
    "units": "mm",
    "decimals": 2
  },
  "icons": {}
}
```

---

## Esempi Completi

### Configurazione Minima

```json
{
  "version": "1.0.0",
  "schema_version": "2.0.0",
  "nome": "Configurazione Base",
  "created": "2024-12-09T12:00:00",
  "modified": "2024-12-09T12:00:00",
  "menus": [],
  "tipologie": [],
  "astine": [],
  "fermavetri": [],
  "modes": [],
  "hardware": {
    "encoder": {
      "resolution": 0.01,
      "pulses_per_mm": 100
    }
  },
  "ui_layout": {
    "theme": "dark",
    "units": "mm"
  },
  "icons": {},
  "impostazioni": {}
}
```

### Configurazione Completa Serramenti

Esempio completo disponibile in:
`configurator/resources/templates/serramenti_completo.json`

---

## Import/Export

### Formato Export Misure (JSONL)

```jsonl
{"timestamp":"2024-12-09T12:00:00","mode":"finestra_2_ante","L":1200,"H":1500,"results":{"Telaio":603}}
{"timestamp":"2024-12-09T12:05:00","mode":"porta_singola","L":900,"H":2100,"results":{"Telaio":453}}
```

Ogni linea è un JSON completo (append-safe).

### Formato Export Configurazione

```json
{
  "export_version": "1.0.0",
  "export_date": "2024-12-09T12:00:00",
  "config": {
    ...configurazione completa...
  }
}
```

---

## Note Implementazione

### Path Standard Dispositivi

- **microSD**: `/sd/` (mount point ESP32)
- **USB OTG**: `/usb/` (mount point ESP32)
- **Locale**: Path utente Windows/Linux

### Backup Automatico

Export configurazione crea automaticamente backup:
```
config.json
config.backup_20241209_120000.json
```

### Validazione

Il configuratore valida:
- Formato JSON
- Campi obbligatori
- Tipi dati
- Range valori (encoder, display, etc.)
- Riferimenti icone
- Sintassi formule

---

## Riferimenti

- [core/config_model.py](../configurator/core/config_model.py) - Modelli dati Python
- [core/io_manager.py](../configurator/core/io_manager.py) - Import/Export
- [core/icon_manager.py](../configurator/core/icon_manager.py) - Gestione icone

---

**Versione Documento**: 1.0  
**Data**: 2024-12-09  
**Autore**: Metro Digitale Team
