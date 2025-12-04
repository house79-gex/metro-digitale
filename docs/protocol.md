# Protocollo Comunicazione BLE - Metro Digitale

## Overview

Il Metro Digitale utilizza Bluetooth Low Energy (BLE) per comunicare con:
- **Troncatrice CNC BLITZ** (Raspberry Pi)
- **App Android** (Flutter)

La comunicazione avviene tramite **GATT** (Generic Attribute Profile) con scambio di messaggi **JSON**.

## UUIDs

### Servizio Principale
```
Service UUID: 12345678-1234-1234-1234-123456789abc
```

### Caratteristiche

| Caratteristica | UUID | Proprietà | Descrizione |
|----------------|------|-----------|-------------|
| TX (Trasmissione) | 12345678-1234-1234-1234-123456789abd | Notify | Metro → Client |
| RX (Ricezione) | 12345678-1234-1234-1234-123456789abe | Write | Client → Metro |

## Formato Messaggi

Tutti i messaggi sono in formato **JSON UTF-8**.

### 1. Modalità Fermavetro → Troncatrice

**Direzione:** Metro Digitale → Troncatrice BLITZ

**Trigger:** Pulsante "Invia" premuto in modalità Fermavetro

```json
{
  "type": "fermavetro",
  "misura_mm": 1250.5,
  "auto_start": true,
  "mode": "semi_auto",
  "timestamp": "2024-12-02T15:30:45Z"
}
```

**Campi:**
- `type` (string): Tipo di misura, sempre "fermavetro"
- `misura_mm` (float): Misura netta in millimetri
- `auto_start` (bool): Se `true`, troncatrice avvia taglio automaticamente
- `mode` (string): Modalità operativa ("semi_auto", "full_auto")
- `timestamp` (string, optional): ISO 8601 timestamp

**Esempio Python (receiver):**
```python
import json

data = json.loads(message)
if data['type'] == 'fermavetro':
    misura = data['misura_mm']
    if data['auto_start']:
        start_taglio(misura)
```

### 2. Modalità Rilievi Speciali → Troncatrice

**Direzione:** Metro Digitale → Troncatrice BLITZ

**Trigger:** Invio elemento da Tipologia Infisso

```json
{
  "type": "rilievo_speciale",
  "dest": "troncatrice",
  "tipologia": "Finestra 2 Ante",
  "elemento": "Traversa Anta",
  "formula": "(L+6)/2",
  "misura_mm": 603.0,
  "num_pezzi": 4,
  "auto_start": false,
  "timestamp": 1701234567890
}
```

**Campi:**
- `type` (string): Tipo di misura, sempre "rilievo_speciale"
- `dest` (string): Destinazione del messaggio ("troncatrice")
- `tipologia` (string): Nome tipologia infisso (es. "Finestra 2 Ante")
- `elemento` (string): Nome elemento calcolato (es. "Traversa Anta")
- `formula` (string): Formula usata per il calcolo (es. "(L+6)/2")
- `misura_mm` (float): Misura calcolata in millimetri
- `num_pezzi` (int): Numero di pezzi da tagliare (default: 1)
- `auto_start` (bool): Se `true`, troncatrice avvia taglio automaticamente
- `timestamp` (number): Unix timestamp in millisecondi

**Esempio Python (receiver - BLITZ integration):**
```python
import json

data = json.loads(message)
if data['type'] == 'rilievo_speciale':
    misura = data['misura_mm']
    num_pezzi = data.get('num_pezzi', 1)
    
    # Popola campo misura
    self.ext_len.setText(f"{misura:.1f}")
    
    # Popola contapezzi
    if hasattr(self, 'spin_count'):
        self.spin_count.setValue(num_pezzi)
    
    if data.get('auto_start'):
        self._start_positioning()
```

### 3. Modalità Vetri → App Android

**Direzione:** Metro Digitale → App Android

**Trigger:** Completamento misura Larghezza × Altezza

```json
{
  "type": "vetro",
  "larghezza_raw": 1200.0,
  "altezza_raw": 1500.0,
  "larghezza_netta": 1188.0,
  "altezza_netta": 1488.0,
  "materiale": "Alluminio",
  "quantita": 1,
  "gioco": 12.0,
  "timestamp": "2024-12-02T15:30:45Z"
}
```

**Campi:**
- `type` (string): Tipo di misura, sempre "vetro"
- `larghezza_raw` (float): Larghezza misurata grezza (mm)
- `altezza_raw` (float): Altezza misurata grezza (mm)
- `larghezza_netta` (float): Larghezza netta dopo sottrazione gioco (mm)
- `altezza_netta` (float): Altezza netta dopo sottrazione gioco (mm)
- `materiale` (string): Tipo materiale ("Alluminio", "Legno", "PVC")
- `quantita` (int): Quantità pezzi (default: 1)
- `gioco` (float): Gioco applicato in mm
- `timestamp` (string, optional): ISO 8601 timestamp

**Esempio Dart (Flutter):**
```dart
final data = jsonDecode(message);
if (data['type'] == 'vetro') {
  final misura = MisuraVetro(
    larghezzaNetta: data['larghezza_netta'],
    altezzaNetta: data['altezza_netta'],
    materiale: data['materiale'],
    // ...
  );
  provider.aggiungiMisura(misura);
}
```

### 4. Comandi da Client → Metro

**Direzione:** Client → Metro Digitale

**Caratteristica:** RX (Write)

#### 4.1 Zero Encoder
```json
{
  "command": "zero",
  "position": 0.0
}
```

#### 4.2 Cambio Modalità
```json
{
  "command": "set_mode",
  "mode": "calibro"
}
```
Valori `mode`: "fermavetro", "vetro", "astina", "calibro", "rilievi_speciali"

#### 4.3 Cambio Materiale
```json
{
  "command": "set_materiale",
  "materiale_idx": 0
}
```

#### 4.4 Cambio Astina
```json
{
  "command": "set_astina",
  "astina_idx": 3
}
```

#### 4.5 Cambio Tipologia Infisso
```json
{
  "command": "set_tipologia",
  "tipologia_idx": 1
}
```

#### 4.6 Request Status
```json
{
  "command": "get_status"
}
```

**Risposta:**
```json
{
  "type": "status",
  "mode": "vetro",
  "position_mm": 1234.56,
  "is_zeroed": true,
  "bt_connected": true,
  "battery_percent": 85
}
```

## Sequenze Tipiche

### Sequenza 1: Misura Fermavetro

```
Metro                          Troncatrice
  │                                │
  │  1. Utente misura fermavetro   │
  │  2. Preme "Invia"               │
  │                                │
  │──── {"type":"fermavetro"} ────>│
  │       "misura_mm": 1250.5      │
  │       "auto_start": true       │
  │                                │
  │                                │ 3. Inserisce misura
  │                                │ 4. Preme START (auto)
  │                                │ 5. Esegue taglio
  │                                │
```

### Sequenza 2: Misura Vetro

```
Metro                          App Android
  │                                │
  │  1. Utente misura larghezza    │
  │  2. Preme "Salva Larghezza"    │
  │  3. Misura altezza             │
  │  4. Preme "Salva Misura"       │
  │                                │
  │──── {"type":"vetro"} ──────────>│
  │       "larghezza_netta": 1188  │
  │       "altezza_netta": 1488    │
  │       "materiale": "Alluminio" │
  │                                │
  │                                │ 5. Raggruppa con misure
  │                                │    simili (tolleranza 2mm)
  │                                │ 6. Incrementa quantità o
  │                                │    aggiunge nuova riga
  │                                │
```

### Sequenza 3: Configurazione Remota

```
App/Client                     Metro
  │                                │
  │──── {"command":"set_mode"} ───>│
  │       "mode": "calibro"        │
  │                                │
  │                                │ 1. Cambia modalità
  │                                │ 2. Aggiorna UI
  │                                │
  │<─── {"type":"status"} ─────────│
  │       "mode": "calibro"        │
  │                                │
```

## Gestione Errori

### Errori di Formato

Se il Metro riceve JSON malformato:
```json
{
  "type": "error",
  "code": "JSON_PARSE_ERROR",
  "message": "Invalid JSON format"
}
```

### Errori di Comando

Se il comando non è riconosciuto:
```json
{
  "type": "error",
  "code": "UNKNOWN_COMMAND",
  "message": "Command 'xyz' not recognized"
}
```

### Errori di Valore

Se un valore è fuori range:
```json
{
  "type": "error",
  "code": "VALUE_OUT_OF_RANGE",
  "message": "Position must be between 0 and 2000mm"
}
```

## Codici di Errore

| Codice | Descrizione |
|--------|-------------|
| JSON_PARSE_ERROR | JSON malformato |
| UNKNOWN_COMMAND | Comando non riconosciuto |
| VALUE_OUT_OF_RANGE | Valore fuori range |
| MODE_NOT_AVAILABLE | Modalità non disponibile |
| ENCODER_ERROR | Errore encoder |
| STORAGE_ERROR | Errore salvataggio NVS |

## MTU e Dimensione Messaggi

- **MTU predefinito:** 23 bytes (20 bytes payload)
- **MTU negoziato:** fino a 512 bytes
- **Dimensione massima messaggio JSON:** ~400 bytes
- **Chunking:** Non implementato (messaggi devono stare in un singolo pacchetto)

Se necessario inviare dati più grandi, implementare chunking:
```json
{
  "chunk": 1,
  "total_chunks": 3,
  "data": "parte_del_messaggio..."
}
```

## Sicurezza

### Attuale
- ✅ Nessuna autenticazione (dispositivo aperto)
- ✅ Pairing opzionale
- ❌ Encryption: No

### Futura (opzionale)
- 🔒 Pairing obbligatorio
- 🔒 PIN code
- 🔒 BLE Security Level 2 (encryption)

## Implementazione Client

### Python (bleak)
```python
from bleak import BleakClient
import json

SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
CHAR_RX_UUID = "12345678-1234-1234-1234-123456789abe"

async def notification_handler(sender, data):
    message = json.loads(data.decode('utf-8'))
    print(f"Ricevuto: {message}")

async with BleakClient(device_address) as client:
    await client.start_notify(CHAR_RX_UUID, notification_handler)
    await asyncio.sleep(60)
```

### Dart/Flutter (flutter_blue_plus)
```dart
final characteristic = /* ... */;
await characteristic.setNotifyValue(true);
characteristic.lastValueStream.listen((data) {
  final json = jsonDecode(utf8.decode(data));
  print('Ricevuto: $json');
});
```

### JavaScript (Web Bluetooth)
```javascript
const service = await device.gatt.getPrimaryService(SERVICE_UUID);
const characteristic = await service.getCharacteristic(CHAR_RX_UUID);

await characteristic.startNotifications();
characteristic.addEventListener('characteristicvaluechanged', (event) => {
  const decoder = new TextDecoder('utf-8');
  const json = JSON.parse(decoder.decode(event.target.value));
  console.log('Ricevuto:', json);
});
```

## Testing

### Tool Consigliati
- **nRF Connect** (Android/iOS) - Test manuale BLE
- **LightBlue** (iOS) - Inspector BLE
- **bluetoothctl** (Linux) - CLI Bluetooth
- **bleak** (Python) - Scripting automatizzato

### Test Checklist
- [ ] Scansione e discovery
- [ ] Connessione stabile
- [ ] Invio comandi
- [ ] Ricezione notifiche
- [ ] Parsing JSON corretto
- [ ] Gestione disconnessione
- [ ] Riconnessione automatica
- [ ] Test con MTU ridotto
- [ ] Test con latenza elevata
- [ ] Test durata batteria

## Versioning

**Versione corrente protocollo:** 1.0

Future versioni includeranno campo:
```json
{
  "protocol_version": "1.1",
  // ... resto dei dati
}
```

## Riferimenti

- [Bluetooth SIG - GATT Specifications](https://www.bluetooth.com/specifications/gatt/)
- [ESP32-S3 Bluetooth API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/bluetooth/index.html)
- [JSON Schema](https://json-schema.org/)
