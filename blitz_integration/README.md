# Integrazione Metro Digitale con Troncatrice BLITZ

Questa integrazione permette di ricevere misure dal Metro Digitale via Bluetooth e triggerare automaticamente il taglio sulla troncatrice CNC BLITZ.

## Requisiti

- Raspberry Pi con Bluetooth
- Python 3.8+
- Software troncatrice BLITZ installato

## Installazione

```bash
# Installare dipendenze Python
pip install -r requirements.txt

# Verificare Bluetooth
hciconfig
```

## File

### bluetooth_receiver.py
Classe standalone per ricevere dati Bluetooth dal Metro Digitale.

**Utilizzo standalone:**
```python
from bluetooth_receiver import BluetoothCalibroReceiver

receiver = BluetoothCalibroReceiver()

def on_misura(data):
    print(f"Misura ricevuta: {data['misura_mm']} mm")
    if data.get('auto_start'):
        print("Avvio taglio automatico...")

receiver.on_misura_received = on_misura
receiver.start()
```

### semi_auto_bluetooth_mixin.py
Mixin da aggiungere alla classe `SemiAutoPage` del software BLITZ per integrare la ricezione Bluetooth.

**Integrazione:**
```python
# Nel file semi_auto.py della troncatrice BLITZ:

from blitz_integration.semi_auto_bluetooth_mixin import SemiAutoBluetoothMixin

class SemiAutoPage(SemiAutoBluetoothMixin, BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_bluetooth()  # Inizializza Bluetooth
    
    # Il resto del codice esistente...
```

## Protocollo

Il Metro Digitale invia messaggi JSON via Bluetooth:

```json
{
  "type": "fermavetro",
  "misura_mm": 1250.5,
  "auto_start": true,
  "mode": "semi_auto"
}
```

Quando `auto_start` è `true`, la troncatrice riceve la misura e trigge automaticamente il pulsante START.

## Configurazione

Modificare le costanti nel file `bluetooth_receiver.py`:

```python
SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
DEVICE_NAME_FILTER = "Metro-Digitale"
```

## Test

```bash
# Eseguire il receiver in modalità test
python bluetooth_receiver.py

# Output atteso:
# Ricerca dispositivo Metro-Digitale...
# Connesso a Metro-Digitale
# In attesa di misure...
```

## Troubleshooting

### Bluetooth non funziona
```bash
# Verificare stato Bluetooth
sudo systemctl status bluetooth

# Riavviare servizio
sudo systemctl restart bluetooth
```

### Dispositivo non trovato
- Verificare che il Metro Digitale sia acceso e in modalità pairing
- Controllare che il nome dispositivo corrisponda
- Provare a eseguire `bluetoothctl` e `scan on`

### Permessi insufficienti
```bash
# Aggiungere utente al gruppo bluetooth
sudo usermod -a -G bluetooth $USER
sudo usermod -a -G dialout $USER
```

## Note

- Il receiver Bluetooth gira in un thread separato per non bloccare l'interfaccia
- La connessione viene automaticamente ristabilita in caso di disconnessione
- I dati ricevuti vengono validati prima dell'uso
