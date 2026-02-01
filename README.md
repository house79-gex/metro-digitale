# 📐 Metro Digitale Multifunzione v2.0

## Panoramica
Metro digitale professionale con **puntali circolari da 30mm** per misure di distanza esterne e interne. Basato su ESP32-S3 con display touch 5" (800×480) integrato e encoder magnetico lineare ad alta precisione (0.005mm).

## ✨ Caratteristiche Principali
- ✅ **Puntali Circolari 30mm**: Misure esterne e interne con compensazione automatica diametro
- ✅ **4 Modalità Operative**: Calibro Avanzato, Vetri L×H, Astine con Profili, Fermavetri
- ✅ **Wizard Assistiti**: Azzeramento guidato passo-passo con verifica
- ✅ **Storage Multi-Target**: SD Card, Export Bluetooth, USB OTG (pendrive)
- ✅ **UI Touch Avanzata**: Gesture swipe, animazioni, feedback tattile
- ✅ **Statistiche Real-Time**: Min, Max, Media, Deviazione Standard
- ✅ **Export Multipli**: JSON, CSV (Excel), Binary
- ✅ **Integrazione BLE**: App Android + Troncatrice Blitz CNC

## 🔧 Hardware

### Componenti Principali
- **Modulo ESP32-S3 5" integrato** (display + touch inclusi)
  - CPU: Dual-core Xtensa @ 240MHz
  - RAM: 8MB PSRAM + 512KB SRAM
  - Flash: 16MB
  - Display: 5" TFT 800×480 RGB parallelo
  - Touch: GT911 capacitivo I2C
  
- **Encoder Magnetico Lineare**
  - Modello: SINO HYMSEANN o compatibile
  - Risoluzione: 0.005mm (5µm)
  - Output: Quadratura A/B (5V TTL)
  - Corsa: 0-2000mm
  
- **Puntali Circolari**
  - Diametro: 30mm
  - Materiale: Acciaio temprato
  - Coppia: Fisso (SX) + Mobile (DX)
  
- **Level Shifter TXS0108E**
  - 8 canali bidirezionali 3.3V ↔ 5V
  - Per interfaccia encoder 5V → ESP32 3.3V
  
- **Modulo UPS Type-C 18650**
  - Batterie: 2× 18650 Li-Ion (6000mAh)
  - Output: 5V @ 3A
  - UPS seamless (0ms switchover)
  - Autonomia: 3.5-4 ore uso intenso

### Schema Collegamenti
```
[Modulo UPS] 5V OUT ──┬──→ TXS0108E VCCB
                      ├──→ Encoder VCC (5V)
                      └──→ ESP32-S3 VIN (5V)
                           ↓ LDO interno
                           3.3V OUT ──→ TXS0108E VCCA

[Encoder] A (5V) ──→ TXS0108E B1 → A1 ──→ ESP32 GPIO 21
[Encoder] B (5V) ──→ TXS0108E B2 → A2 ──→ ESP32 GPIO 43

[Pulsante SEND] ──→ ESP32 GPIO 47 (pull-up 10kΩ)
```

## 🚀 Quick Start

### 1. Firmware ESP32-S3
```bash
cd firmware
idf.py set-target esp32s3
idf.py menuconfig  # Configura PSRAM, Flash 16MB, Partition table
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

### 2. Calibrazione Iniziale
1. Accendi il dispositivo
2. Tocca "⚙️ Impostazioni" → "🧙 Calibra Puntali"
3. Segui il wizard azzeramento:
   - Pulisci puntali
   - Porta a contatto completo
   - Conferma zero
   - Verifica (muovi e ritorna a zero)
4. Conferma completamento

### 3. Prima Misura
1. Tocca "📐 Calibro" nella bottom nav
2. Seleziona tipo: "◉ Esterna" o "○ Interna"
3. Posiziona lo strumento sul pezzo
4. Premi pulsante fisico "SEND" per salvare
5. Visualizza statistiche con "📊 STAT"

## 📱 Modalità Operative

### 1. Calibro Avanzato
Modalità misura universale con statistiche professionali.
- **Misure Supportate**: Esterna, Interna
- **Unità**: mm, cm, inch, frazionari (1/64")
- **Funzioni**: Hold, Zero assistito, Statistiche, Tolleranza
- **Export**: Salvataggio automatico su SD + invio BLE

### 2. Vetri L×H
Misura dimensioni vetri con gioco materiale automatico.
- **Materiali**: Alluminio (-12mm), Legno (-6mm), PVC (-10mm)
- **Wizard**: Selezione materiale → Misura L → Misura H → Review → Save
- **Output**: Dimensioni lorde + nette calcolate
- **Invio**: JSON a app Android per report PDF

### 3. Astine
Gestione profili astine con offset personalizzabili.
- **Gruppi**: Anta Ribalta (4 profili), Persiana (2), Cremonese (2), Custom (2)
- **Calcolo**: Lunghezza grezza + offset profilo = lunghezza taglio
- **Colori**: Viola (AR), Blu (Persiana), Verde (Cremonese), Giallo (Custom)

### 4. Fermavetri
Invio diretto misure a troncatrice Blitz CNC.
- **Auto-start**: Trigger automatico taglio su Blitz
- **Modalità**: Semi-automatico o Automatico
- **Protocollo**: JSON BLE specifico per Blitz

## 💾 Storage e Export

### Storage Disponibili
- **SD Card**: Salvataggio automatico JSONL append-mode
- **Bluetooth**: Transfer sessioni a smartphone/PC
- **USB OTG**: Export su pendrive USB-C
- **NVS Interno**: Configurazioni e calibrazioni

### Formati Export
- **JSON**: Human-readable, completo di metadati
- **CSV**: Excel-compatible, per analisi dati
- **Binary**: Compatto, per backup

### Struttura Directory SD
```
/sd/
├── sessions/       # Misure giornaliere (YYYYMMDD.jsonl)
├── exports/        # Export manuali (CSV, JSON)
└── backup/         # Backup configurazioni
```

## 🎮 Controlli

### Pulsante Fisico SEND
- **Click**: Salva misura + invio BLE
- **Long Press (>1s)**: Menu rapido
- **Double Click**: Zero veloce (senza wizard)

### Gesture Touch
- **Swipe Left/Right**: Cambio modalità
- **Swipe Up**: Menu impostazioni
- **Swipe Down**: Quick actions
- **Long Press Display**: Zero rapido

## 📊 Specifiche Tecniche

### Precisione
- Risoluzione encoder: 0.00125mm (dopo decodifica x4)
- Precisione sistema: ±0.01mm su 1000mm
- Ripetibilità: ±0.005mm

### Performance
- Refresh display: 30 FPS
- Sampling encoder: 100Hz
- Touch sampling: 50Hz
- BLE latency: <50ms

### Alimentazione
- Batterie: 2× 18650 (6000mAh @ 3.7V)
- Consumo: ~4W (uso intenso)
- Autonomia: 3.5-4 ore
- Ricarica: USB-C 5V/3A (2-3 ore)

## 🔗 Integrazioni

### App Android (Flutter)
- Ricezione misure via BLE
- Raggruppamento automatico misure simili
- Generazione report PDF
- Export e condivisione

### Troncatrice Blitz CNC
- Invio misure direct-to-machine
- Trigger automatico taglio
- Modalità semi-auto e automatica

## 📖 Documentazione Completa
- [Hardware Dettagliato](docs/hardware.md)
- [Schema Collegamenti](docs/wiring.md)
- [Protocollo BLE](docs/protocol.md)
- [Modalità Operative](docs/modes.md)
- [Storage e Export](docs/storage.md)

## 🛠️ Troubleshooting
Vedi [docs/troubleshooting.md](docs/troubleshooting.md)

## 📄 Licenza
MIT License - Vedi [LICENSE](LICENSE)

---

**Versione 2.0** - Architettura completamente ridefinita con puntali circolari, storage multi-target e UI touch avanzata.
