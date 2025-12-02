# 📐 Metro Digitale Multifunzione

[![ESP32](https://img.shields.io/badge/ESP32-S3-blue.svg)](https://www.espressif.com/en/products/socs/esp32-s3)
[![LVGL](https://img.shields.io/badge/LVGL-8.3-green.svg)](https://lvgl.io/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue.svg)](https://flutter.dev/)
[![Bluetooth](https://img.shields.io/badge/Bluetooth-BLE-lightblue.svg)](https://www.bluetooth.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Metro digitale professionale multifunzione basato su ESP32-S3 con display touch da 5" (800x480) e encoder magnetico lineare ad alta precisione (0.005mm).

## ✨ Funzionalità Principali

- ✅ **Modalità Fermavetro**: Rileva misure fermavetri e invia alla troncatrice CNC via Bluetooth
- ✅ **Modalità Vetri**: Misura Larghezza × Altezza con gioco automatico per materiale (Alluminio -12mm, Legno -6mm, PVC -10mm)
- ✅ **Modalità Astine**: Profili configurabili organizzati per gruppi con offset personalizzabili
- ✅ **Modalità Calibro**: Interfaccia minimale ed essenziale per uso come calibro digitale puro
- ✅ **Comunicazione BLE**: Invio dati a troncatrice CNC e app Android
- ✅ **App Android**: Raggruppa misure simili e genera report PDF

## 🔧 Hardware Richiesto

### Componenti Principali
- **ESP32-S3-WROOM-1** (modulo con 8MB Flash, 8MB PSRAM)
- **Display Touch 5"** capacitivo 800x480 con controller GT911
- **Encoder Magnetico Lineare** ad alta precisione (risoluzione 0.005mm)
  - Esempio: encoder magnetico con interfaccia quadratura
- **Batteria LiPo** 3.7V 2000mAh con circuito di ricarica
- **Pulsanti** e **LED** di stato

### Collegamenti Principali
- Display: SPI + I2C (touch)
- Encoder: GPIO con PCNT (Pulse Counter)
- Bluetooth: integrato ESP32-S3
- Alimentazione: LiPo con regolatore 3.3V

Per dettagli completi vedere [docs/hardware.md](docs/hardware.md) e [docs/wiring.md](docs/wiring.md).

## 🚀 Quick Start

### Firmware ESP32-S3

```bash
# Installare ESP-IDF v5.0+
cd firmware

# Configurare il progetto
idf.py set-target esp32s3
idf.py menuconfig

# Compilare e flashare
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

### App Android (Flutter)

```bash
cd app_android

# Installare dipendenze
flutter pub get

# Eseguire su dispositivo
flutter run
```

### Integrazione Troncatrice BLITZ

```bash
cd blitz_integration

# Installare dipendenze Python
pip install -r requirements.txt

# Eseguire il receiver Bluetooth
python bluetooth_receiver.py
```

## 📱 Modalità Operative

### 1. Modalità Fermavetro
Misura rapida di fermavetri con invio automatico alla troncatrice CNC via Bluetooth.
- Supporto per puntali fissi/mobili configurabili
- Compensazione automatica offset puntali
- Trigger START troncatrice

### 2. Modalità Vetri
Misura Larghezza × Altezza con gestione giochi materiali.
- **Alluminio**: -12mm (6mm per lato)
- **Legno**: -6mm (3mm per lato)
- **PVC**: -10mm (5mm per lato)
- Invio misure a app Android per raggruppamento e report PDF

### 3. Modalità Astine
Gestione profili astine per serramenti organizzati per gruppi:
- **Anta Ribalta** (viola): Inferiore AR, Superiore AR, Laterale AR, Cremonese AR
- **Persiana** (blu): Inferiore Persiana, Superiore Persiana
- **Cremonese Normale** (verde): Cremonese Std, Cremonese Corta
- **Personalizzati** (giallo): Profili custom configurabili

Ogni profilo ha offset personalizzabile e può essere attivato/disattivato.

### 4. Modalità Calibro
Interfaccia minimale per uso come calibro digitale di precisione.
- Display grande e chiaro
- Zero rapido
- Lettura in mm con precisione 0.01mm

## 📊 Protocollo Comunicazione BLE

### UUID Servizio
`12345678-1234-1234-1234-123456789abc`

### Formato JSON

**Invio a troncatrice CNC:**
```json
{
  "type": "fermavetro",
  "misura_mm": 1250.5,
  "auto_start": true,
  "mode": "semi_auto"
}
```

**Invio a app Android:**
```json
{
  "larghezza_raw": 1200.0,
  "altezza_raw": 1500.0,
  "larghezza_netta": 1188.0,
  "altezza_netta": 1488.0,
  "materiale": "Alluminio",
  "quantita": 1,
  "gioco": 12.0
}
```

Vedere [docs/protocol.md](docs/protocol.md) per documentazione completa.

## 🎨 Anteprima Interfaccia

Un'anteprima HTML interattiva completa dell'interfaccia è disponibile in:
```
preview/ui_preview.html
```

Aprire il file in un browser per esplorare tutte le schermate e funzionalità.

## 📖 Documentazione

- [Hardware e Componenti](docs/hardware.md)
- [Schema Collegamenti](docs/wiring.md)
- [Protocollo Comunicazione](docs/protocol.md)
- [Integrazione BLITZ](blitz_integration/README.md)

## 🏗️ Struttura Progetto

```
metro-digitale/
├── README.md                    # Documentazione principale
├── LICENSE                      # MIT License
├── firmware/                    # Codice ESP32-S3 con LVGL
│   ├── CMakeLists.txt
│   ├── sdkconfig.defaults
│   └── main/                    # Codice sorgente principale
├── app_android/                 # App Flutter
│   ├── pubspec.yaml
│   └── lib/                     # Codice Dart
├── blitz_integration/           # Integrazione troncatrice BLITZ
│   ├── bluetooth_receiver.py
│   └── semi_auto_bluetooth_mixin.py
├── docs/                        # Documentazione tecnica
│   ├── hardware.md
│   ├── wiring.md
│   └── protocol.md
└── preview/                     # Anteprima interfaccia
    └── ui_preview.html
```

## 🤝 Contribuire

I contributi sono benvenuti! Per favore:
1. Fork del repository
2. Creare un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Aprire una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedere il file [LICENSE](LICENSE) per i dettagli.

## 👨‍💻 Autore

Progetto Metro Digitale Multifunzione

## 🙏 Ringraziamenti

- ESP-IDF framework by Espressif
- LVGL graphics library
- Flutter framework by Google
- Comunità open source

---

**Nota**: Questo è un progetto professionale per uso in ambiente industriale. Testare accuratamente prima dell'uso in produzione.
