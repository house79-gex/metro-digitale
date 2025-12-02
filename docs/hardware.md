# Hardware - Metro Digitale Multifunzione

## Lista Componenti

### Componenti Principali

#### 1. Microcontrollore
- **ESP32-S3-WROOM-1** (8MB Flash + 8MB PSRAM)
  - Dual-core Xtensa LX7 fino a 240MHz
  - WiFi 802.11 b/g/n
  - Bluetooth 5.0 BLE
  - [Link acquisto](https://www.espressif.com/en/products/modules/esp32-s3)
  - Prezzo: ~€8-12

#### 2. Display Touch
- **Display TFT LCD 5" 800x480 Capacitivo**
  - Controller: ILI9488 o ST7796
  - Touch: GT911 capacitivo
  - Interfaccia: SPI (display) + I2C (touch)
  - Brightness: 350 cd/m²
  - [Esempio link](https://www.waveshare.com/5inch-capacitive-touch-display.htm)
  - Prezzo: ~€35-50

#### 3. Encoder Magnetico Lineare
- **Encoder magnetico ad alta precisione**
  - Risoluzione: 0.005mm (5µm)
  - Corsa: 0-2000mm o superiore
  - Output: Quadratura A/B
  - Alimentazione: 5V
  - Opzioni:
    - Encoder magnetico incrementale con nastro magnetico
    - Sistema ottico lineare (più costoso ma più preciso)
  - [Esempio encoder magnetico](https://www.aliexpress.com/item/magnetic-encoder.html)
  - Prezzo: ~€80-150

### Alimentazione

#### 4. Sistema di Alimentazione
- **Batteria LiPo 3.7V 2000-3000mAh**
  - Protezione sovraccarico/scarica integrata
  - Connettore JST-PH 2.0mm
  - Prezzo: ~€10-15

- **Modulo di Ricarica TP4056**
  - Ricarica LiPo via USB-C
  - Protezione batteria
  - LED status carica
  - Prezzo: ~€2-3

- **Regolatore Step-Down LM2596**
  - Input: 3.7-12V
  - Output: 3.3V @ 3A
  - Efficienza >90%
  - Prezzo: ~€3-5

### Componenti Accessori

#### 5. Pulsanti e Interruttori
- **Pulsante Power con LED** (x1)
- **Pulsanti funzione** (x3-5)
- **Encoder rotativo** (opzionale, per navigazione menu)
- Prezzo totale: ~€5-10

#### 6. LED di Status
- **LED RGB** (x2) - Status generale e Bluetooth
- **LED Power** (x1) - Indicatore alimentazione
- Resistori limitatori corrente
- Prezzo: ~€2-3

#### 7. Connettori
- **USB-C per ricarica e programmazione**
- **JST-PH connettori** per batteria e alimentazione
- **Pin header** per connessioni encoder
- Prezzo: ~€5-8

### Case e Meccanica

#### 8. Custodia
- **Case stampato 3D** o alluminio CNC
  - Dimensioni: ~150x90x25mm
  - Montaggio display frontale
  - Aperture per pulsanti e USB
  - Vano batteria
- File STL disponibili nel progetto (da creare)
- Costo stampa 3D: ~€10-20
- Costo case alluminio: ~€40-60

#### 9. Protezione Display
- **Vetro temperato** 5" con oleofobico
- Prezzo: ~€5-10

### Accessori Opzionali

#### 10. Componenti Extra
- **Speaker piezo** per feedback audio
- **Vibration motor** per feedback tattile
- **Slot SD card** per logging dati
- **Connettore per alimentazione esterna** 12V DC
- Prezzo totale: ~€10-15

## Costo Totale Stimato

| Categoria | Costo |
|-----------|-------|
| Componenti principali | €123-212 |
| Alimentazione | €15-23 |
| Accessori | €12-21 |
| Case e meccanica | €15-30 |
| **TOTALE** | **€165-286** |

*Note: Prezzi indicativi al 2024, possono variare in base al fornitore*

## Fornitori Consigliati

### Italia
- **Mouser Electronics** - Componenti elettronici professionali
- **RS Components** - Ampia gamma di componenti
- **Farnell** - Componenti e kit di sviluppo

### Internazionale
- **DigiKey** - Vasto catalogo componenti
- **AliExpress** - Display, encoder, case (tempi spedizione lunghi)
- **Amazon** - Componenti comuni con consegna rapida

### Specializzati
- **Espressif** (diretto) - Moduli ESP32-S3
- **Waveshare** - Display touch di qualità
- **Renishaw/Heidenhain** - Encoder professionali (alta precisione)

## Note Tecniche

### Encoder Magnetico
Per applicazioni professionali si consiglia:
- Encoder con compensazione temperatura
- Protezione IP65 o superiore
- Nastro magnetico con banda adesiva di qualità
- Testina di lettura con cuscinetti a sfera

### Display
Considerazioni per scelta display:
- Visibilità alla luce solare: minimo 350 cd/m²
- Touch capacitivo preferibile a resistivo
- Angolo di visione ampio (IPS)
- Protezione vetro temperato obbligatoria

### Batteria
Autonomia stimata con batteria 2500mAh:
- Display sempre acceso: ~4-6 ore
- Con sleep mode: ~12-20 ore
- Tempo ricarica: ~2-3 ore

## Schema a Blocchi

```
┌─────────────────┐
│   ESP32-S3      │
│   (Core 0+1)    │
└────────┬────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
┌───┴────┐                 ┌──────┴─────┐
│Display │                 │  Encoder   │
│ Touch  │                 │  Magnetico │
│  SPI   │                 │    PCNT    │
│  I2C   │                 │  (GPIO)    │
└────────┘                 └────────────┘
    │                             │
    └─────────┬───────────────────┘
              │
        ┌─────┴──────┐
        │  Batteria  │
        │   LiPo     │
        │   3.7V     │
        └────────────┘
              │
        ┌─────┴──────┐
        │ Regolatori │
        │    3.3V    │
        └────────────┘
```

## Prossimi Passi

1. Acquisire componenti dalla lista
2. Consultare [wiring.md](wiring.md) per collegamenti
3. Assemblare su breadboard per test
4. Programmare firmware
5. Testare funzionalità
6. Realizzare PCB custom (opzionale)
7. Assemblaggio finale in case
