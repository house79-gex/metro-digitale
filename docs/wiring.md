# Schema Collegamenti - Metro Digitale

## Pinout ESP32-S3

### Display Touch 5" (800x480)

#### Interfaccia SPI Display
| ESP32-S3 Pin | Segnale | Display Pin | Note |
|--------------|---------|-------------|------|
| GPIO 12 | MOSI | SDI/MOSI | Dati SPI |
| GPIO 13 | SCK | SCK | Clock SPI |
| GPIO 14 | CS | CS | Chip Select |
| GPIO 15 | DC | DC/RS | Data/Command |
| GPIO 16 | RST | RESET | Reset display |
| GPIO 17 | BL | LED | Backlight (PWM) |
| 3.3V | VCC | VCC | Alimentazione |
| GND | GND | GND | Ground |

#### Interfaccia I2C Touch (GT911)
| ESP32-S3 Pin | Segnale | Touch Pin | Note |
|--------------|---------|-----------|------|
| GPIO 21 | SDA | SDA | Dati I2C |
| GPIO 22 | SCL | SCL | Clock I2C |
| GPIO 18 | INT | INT | Interrupt |
| GPIO 19 | RST | RST | Reset touch |
| 3.3V | VCC | VCC | Alimentazione |
| GND | GND | GND | Ground |

### Encoder Magnetico Lineare

#### Segnali Quadratura
| ESP32-S3 Pin | Segnale | Encoder Pin | Note |
|--------------|---------|-------------|------|
| GPIO 4 | PCNT_A | Channel A | Segnale quadratura A |
| GPIO 5 | PCNT_B | Channel B | Segnale quadratura B |
| 5V | VCC | VCC | Alimentazione encoder |
| GND | GND | GND | Ground |

**Note:**
- Utilizzare pull-up da 10kΩ su canali A e B
- Eventuale condensatore 100nF tra segnali e GND per filtraggio
- Per encoder 5V: usare level shifter 5V→3.3V o resistori partitori

#### Level Shifter (se necessario)
```
Encoder 5V → Level Shifter → ESP32-S3 3.3V
    A → HV1 ─── LV1 → GPIO 4
    B → HV2 ─── LV2 → GPIO 5
```

### Pulsanti

| ESP32-S3 Pin | Funzione | Collegamento |
|--------------|----------|--------------|
| GPIO 0 | BOOT/Flash | Pulsante BOOT (interno) |
| GPIO 33 | BTN_ZERO | Pulsante Zero (pull-up) |
| GPIO 34 | BTN_MODE | Pulsante Modalità (pull-up) |
| GPIO 35 | BTN_SEND | Pulsante Invio (pull-up) |

**Schema Pulsante:**
```
         3.3V
          │
         ┌┴┐
         │R│ 10kΩ (pull-up)
         └┬┘
          │
          ├─────── GPIO
          │
         [S] Pulsante
          │
         GND
```

### GPIO Esposti su Pin Header VIEWE Board

La scheda VIEWE espone i seguenti GPIO su pin header per espansioni:

| Pin | GPIO | Funzione Metro Digitale | Note |
|-----|------|------------------------|------|
| 1   | 5V   | Alimentazione da UPS | Power in |
| 2   | GND  | Ground comune | Massa |
| 3   | IO35 | Encoder Channel A | Via TXS0108E level shifter |
| 4   | IO36 | Encoder Channel B | Via TXS0108E level shifter |
| 12  | IO46 | **Buzzer Passivo PWM** | **← NUOVO (GPIO 46)** |
| 13  | IO47 | Pulsante SEND fisico | Pull-up 10kΩ |
| 15  | 3.3V | Alimentazione TXS0108E VCCA | Power out |
| 16  | GND  | Ground | Massa |

**Note importanti:**
- GPIO 46 è dedicato al buzzer passivo e non deve essere usato per altre funzioni
- GPIO 46 utilizza LEDC_TIMER_0 e LEDC_CHANNEL_0
- Resistore 100Ω consigliato in serie con il buzzer

### LED Status

| ESP32-S3 Pin | Funzione | Note |
|--------------|----------|------|
| GPIO 38 | LED_PWR | LED Power (verde) |
| GPIO 39 | LED_BT | LED Bluetooth (blu) |
| GPIO 40 | LED_ERR | LED Errore (rosso) |

**Schema LED:**
```
GPIO ────┬────R (330Ω)────[LED]────GND
         │
      (opzionale transistor per correnti >20mA)
```

### Alimentazione

#### Schema Alimentazione Completo
```
[LiPo 3.7V 2500mAh]
         │
    ┌────┴────┐
    │ TP4056  │ ← USB-C (5V ricarica)
    │ Charge  │
    │ Module  │
    └────┬────┘
         │
    ┌────┴────┐
    │Protection│
    │  Board  │
    └────┬────┘
         │
         ├──────────┐
         │          │
    ┌────┴────┐     │
    │ LM2596  │     │ (5V per encoder)
    │ 3.3V    │     │
    └────┬────┘     │
         │          │
    ESP32-S3    Encoder 5V
    Display 3.3V
```

#### Pinout Alimentazione
| Componente | Input | Output |
|------------|-------|--------|
| TP4056 | USB-C 5V | LiPo 3.7V |
| LM2596 | LiPo 3.7V | 3.3V @ 3A |
| ESP32-S3 | 3.3V | - |
| Display | 3.3V | - |
| Encoder | 5V (diretto da LiPo+boost) | - |

### USB-C per Programmazione

| ESP32-S3 Pin | USB-UART Pin | Note |
|--------------|--------------|------|
| GPIO 43 | TXD | UART TX |
| GPIO 44 | RXD | UART RX |
| EN | DTR | Auto-reset |
| GPIO 0 | RTS | Auto-boot |

**Opzioni:**
1. Usare modulo CH340G/CP2102 integrato
2. Usare programmer esterno FTDI

### Connessioni Opzionali

#### SD Card (se utilizzata)
| ESP32-S3 Pin | SD Card Pin | Note |
|--------------|-------------|------|
| GPIO 36 | CS | Chip Select |
| GPIO 37 | MOSI | Dati |
| GPIO 38 | CLK | Clock |
| GPIO 39 | MISO | Dati |

#### Speaker/Buzzer
| ESP32-S3 Pin | Componente | Note |
|--------------|------------|------|
| GPIO 46 | Buzzer Passivo + | PWM audio (NUOVO) |
| GND | Buzzer - | Ground |

**Schema Collegamento Buzzer:**
```
ESP32-S3 Board VIEWE:
┌────────────────────────────────────┐
│  Pin Header:                       │
│                                    │
│  IO46 (pin 12) ───┬─── 100Ω ───┬──→ Buzzer (+) Rosso
│                   │             │
│  GND (pin 2/16) ──┼─────────────┴──→ Buzzer (-) Nero
└───────────────────┘
```

#### Vibration Motor
| ESP32-S3 Pin | Componente | Note |
|--------------|------------|------|
| GPIO 45 | Motor (via MOSFET) | Controllo PWM |

## Schema Completo ASCII

```
                    ┌─────────────────────────┐
                    │      ESP32-S3-WROOM     │
                    │                         │
    [Display]       │  GPIO 12-17 ─────────┐  │
    SPI/I2C ────────┤  GPIO 21-22 ───────┐ │  │
                    │  GPIO 18-19 ─────┐ │ │  │
                    │                  │ │ │  │
    [Encoder]       │  GPIO 4-5 ─────┐ │ │ │  │
    Quadrature ─────┤                │ │ │ │  │
                    │                │ │ │ │  │
    [Buttons]       │  GPIO 33-35 ─┐ │ │ │ │  │
    Zero/Mode ──────┤              │ │ │ │ │  │
                    │              │ │ │ │ │  │
    [LEDs]          │  GPIO 38-40 ─┤ │ │ │ │  │
    Status ─────────┤              │ │ │ │ │  │
                    │              │ │ │ │ │  │
    [Power]         │  3.3V        │ │ │ │ │  │
    LM2596 ─────────┤  GND         │ │ │ │ │  │
                    │              │ │ │ │ │  │
                    └──────────────┴─┴─┴─┴─┴──┘
```

## Checklist Collegamento

Prima di alimentare, verificare:

- [ ] Alimentazione 3.3V corretta su ESP32-S3
- [ ] GND comune tra tutti i componenti
- [ ] Condensatori di disaccoppiamento (100nF) vicino a VCC
- [ ] Pull-up sui pulsanti
- [ ] Level shifter corretto per encoder 5V
- [ ] Connessioni SPI corrette (MOSI, MISO, SCK)
- [ ] Connessioni I2C corrette (SDA, SCL)
- [ ] Resistori limitatori su LED
- [ ] USB-UART collegato correttamente
- [ ] Polarità batteria LiPo corretta

## Test Iniziale

1. **Test Alimentazione**
   - Misurare 3.3V su pin VCC ESP32-S3
   - Verificare consumo a riposo (<100mA)

2. **Test Programmazione**
   - Connettere USB
   - Programmare sketch blink LED
   - Verificare caricamento corretto

3. **Test Display**
   - Eseguire esempio LVGL
   - Verificare output grafico
   - Testare touch screen

4. **Test Encoder**
   - Eseguire test PCNT
   - Verificare conteggio su movimento
   - Controllare direzione

5. **Test Bluetooth**
   - Avviare advertising
   - Scansionare con smartphone
   - Verificare connessione

6. **Test Buzzer** (NUOVO)
   - Eseguire `buzzer_test_all_patterns()`
   - Verificare 10 pattern sonori diversi
   - Testare slider volume in UI Settings
   - Controllare polarità (+ su IO46, - su GND)

## Note di Sicurezza

⚠️ **ATTENZIONE:**
- Non invertire polarità batteria LiPo
- Non cortocircuitare uscite GPIO
- Usare resistori limitatori su LED
- Verificare tensioni prima di collegare
- Non superare 3.3V su pin GPIO
- Batteria LiPo: maneggiare con cura

## Risorse Aggiuntive

- [ESP32-S3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [ESP32-S3 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf)
- [LVGL Display Driver Guide](https://docs.lvgl.io/master/porting/display.html)

## Troubleshooting Collegamenti

### Display non funziona
- Verificare VCC e GND
- Controllare CS, DC, RST
- Provare a invertire MOSI/MISO
- Ridurre frequenza SPI

### Encoder non conta
- Verificare segnali A e B con oscilloscopio
- Controllare pull-up
- Testare level shifter
- Verificare configurazione PCNT

### Touch non risponde
- Verificare I2C scan (indirizzo 0x5D o 0x14)
- Controllare pin INT e RST
- Verificare VCC touch controller
- Testare con esempio GT911

### Bluetooth non si connette
- Verificare antenna WiFi/BT
- Controllare configurazione SDK
- Verificare memoria disponibile
- Testare esempio BLE scan

### Buzzer non emette suono (NUOVO)
- Verificare polarità buzzer (+ su IO46, - su GND)
- Controllare resistore 100Ω in serie
- Verificare volume in Settings (deve essere >0%)
- Testare con `buzzer_test_all_patterns()`
- Verificare che GPIO 46 non sia usato per altro
- Controllare connessioni su pin header (pin 12)
- Misurare tensione PWM su GPIO 46 con oscilloscopio
