# Troubleshooting - Metro Digitale v2.0

Guida alla risoluzione dei problemi comuni.

## Problemi Hardware

### Display Non Si Accende

**Sintomi:**
- Schermo nero
- Nessuna retroilluminazione
- Nessuna risposta touch

**Soluzioni:**
1. **Verificare alimentazione**
   - Controllare cavo USB-C connesso
   - LED batteria acceso?
   - Voltaggio batteria >3.5V

2. **Test retroilluminazione**
   - Verificare GPIO 45 (BL pin)
   - Test PWM backlight
   ```bash
   idf.py monitor
   # Cercare: "Display backlight: XX%"
   ```

3. **Reset hardware**
   - Tenere premuto RESET 5 secondi
   - Riavvio automatico
   - Verificare boot log

**Se persiste:** Hardware difettoso, contattare supporto.

### Encoder Non Funziona

**Sintomi:**
- Lettura sempre 0.000mm
- Nessun cambiamento muovendo puntali
- Errore "Encoder not responding"

**Soluzioni:**
1. **Verificare collegamenti**
   - Pin A → GPIO 21
   - Pin B → GPIO 43
   - VCC → 5V
   - GND → GND

2. **Test level shifter TXS0108E**
   - VCCA = 3.3V
   - VCCB = 5V
   - OE = HIGH

3. **Verificare alimentazione encoder**
   - Voltaggio 5V ±0.2V
   - Corrente <100mA

4. **Test manuale**
   ```bash
   idf.py monitor
   # Muovere puntali
   # Cercare: "Encoder count: XXXX"
   ```

**Diagnosi avanzata:**
```c
// In monitor seriale, cercare:
PCNT unit 0 count: XXX  // Deve variare
```

### Touch Non Risponde

**Sintomi:**
- Nessuna risposta a tocchi
- Touch parzialmente funzionante
- Coordinate errate

**Soluzioni:**
1. **Verificare I2C**
   - SDA → GPIO 18
   - SCL → GPIO 8
   - INT → GPIO 4

2. **Test comunicazione**
   ```bash
   i2cdetect -y 0
   # Deve rilevare GT911 a indirizzo 0x5D o 0x14
   ```

3. **Calibrazione touch**
   - Menu Settings → Display → Touch Calibration
   - Seguire procedura 5 punti

4. **Pulizia display**
   - Rimuovere polvere/sporco
   - Asciugare da umidità
   - Verificare protezione schermo

### SD Card Non Rilevata

**Sintomi:**
- Errore "SD card mount failed"
- Directory `/sd` non esiste
- Impossibile salvare misure

**Soluzioni:**
1. **Verificare inserimento**
   - Card inserita correttamente
   - Click di blocco sentito
   - Contatti puliti

2. **Verificare formato**
   - Filesystem: FAT32 (consigliato)
   - Dimensione: ≤32GB
   - Classe: 10 o superiore

3. **Test con PC**
   - Leggere/scrivere file
   - Verificare errori filesystem
   - Formattare se necessario

4. **Verificare pin SPI**
   - CS → GPIO 10
   - MOSI → GPIO 11
   - MISO → GPIO 13
   - SCK → GPIO 12

**Format SD Card (da PC):**
```bash
# Linux
sudo mkfs.vfat -F 32 /dev/sdX1

# Windows
# Disk Management → Format → FAT32
```

## Problemi Software

### Firmware Non Si Carica

**Sintomi:**
- Errore durante flash
- "Failed to connect"
- Timeout comunicazione

**Soluzioni:**
1. **Verificare porta seriale**
   ```bash
   ls /dev/ttyUSB* # o /dev/ttyACM*
   # Verificare permessi
   sudo chmod 666 /dev/ttyUSB0
   ```

2. **Entrare in boot mode**
   - Tenere premuto BOOT
   - Premere RESET
   - Rilasciare RESET
   - Rilasciare BOOT dopo 2 sec

3. **Erase flash completo**
   ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   idf.py flash
   ```

4. **Verificare driver USB**
   - Windows: CP210x o CH340 driver
   - Linux: kernel driver automatico
   - macOS: verificare kext caricato

### Boot Loop Continuo

**Sintomi:**
- Reboot ogni 5-10 secondi
- Log mostra "Rebooting..."
- Impossibile usare dispositivo

**Soluzioni:**
1. **Analizzare crash log**
   ```bash
   idf.py monitor
   # Cercare:
   # - Guru Meditation Error
   # - Stack trace
   # - Backtrace
   ```

2. **Erase NVS**
   ```bash
   idf.py erase-nvs
   idf.py flash monitor
   ```

3. **Factory reset**
   - Menu Settings → Advanced → Factory Reset
   - O via seriale:
   ```bash
   nvs_flash_erase()
   esp_restart()
   ```

### Bluetooth Non Connette

**Sintomi:**
- Dispositivo non visibile in scan
- Connessione fallisce
- Disconnect improvviso

**Soluzioni:**
1. **Verificare BLE abilitato**
   ```bash
   idf.py menuconfig
   # Component config → Bluetooth → Enabled
   ```

2. **Reset stack Bluetooth**
   - Menu Settings → Bluetooth → Reset BT
   - Riavvio dispositivo

3. **Verificare distanza**
   - Max 10 metri senza ostacoli
   - Evitare interferenze 2.4GHz
   - Allontanare da WiFi

4. **Test con app generica**
   - LightBlue (iOS)
   - nRF Connect (Android)
   - Verificare servizio UUID visibile

## Problemi Misure

### Letture Instabili

**Sintomi:**
- Valore oscilla ±1mm
- Impossibile ottenere lettura stabile
- Deriva continua

**Soluzioni:**
1. **Calibrazione zero**
   - Eseguire wizard completo
   - Verificare pulizia puntali
   - Test con blocchetto

2. **Verificare fissaggio**
   - Encoder ben fissato
   - Nessun gioco meccanico
   - Viti strette

3. **Condizioni ambientali**
   - Temperatura stabile (20°C ±2°C)
   - Nessuna vibrazione
   - Tavolo stabile

### Offset Costante

**Sintomi:**
- Tutte le misure +/- X.Xmm
- Blocchetto 100mm → legge 100.5mm
- Errore sistematico

**Soluzioni:**
1. **Ri-calibrare zero**
   - Wizard completo
   - Verifica tolleranza

2. **Compensazione usura**
   - Menu Settings → Puntali → Offset Usura
   - Misurare blocchetto noto
   - Sistema calcola offset

3. **Verificare temperatura**
   - Dilatazione termica
   - Attendere stabilizzazione
   - Usare a temperatura costante

### Hold Non Funziona

**Sintomi:**
- Pulsante HOLD non blocca
- Valore continua a cambiare
- Statistiche non si aggiornano

**Soluzioni:**
1. **Verificare calibrazione**
   - Must be calibrated first
   - Eseguire wizard zero

2. **Reset modalità**
   - Uscire e rientrare in Calibro
   - Oppure reboot dispositivo

3. **Update firmware**
   - Verificare ultima versione
   - Flash se disponibile update

## Problemi Storage

### Salvataggio Fallisce

**Sintomi:**
- Errore "Save failed"
- Misure non appaiono in sessioni
- File JSONL vuoto

**Soluzioni:**
1. **Verificare SD card**
   - Card inserita
   - Spazio disponibile >100MB
   - Filesystem integro

2. **Test scrittura manuale**
   ```bash
   # In monitor seriale
   storage_save_measurement(&test_record, STORAGE_TARGET_SD_CARD);
   # Verificare return value
   ```

3. **Verificare permessi**
   - Directory `/sd/sessions` esistente
   - Permessi scrittura OK

### Export CSV Corrotto

**Sintomi:**
- File CSV non si apre in Excel
- Caratteri strani
- Colonne disallineate

**Soluzioni:**
1. **Verificare encoding**
   - Deve essere UTF-8
   - Excel: Importa da testo/CSV

2. **Verificare separatori**
   - Virgola `,` come separatore
   - Quote `"` per campi con virgole

3. **Re-export**
   - Cancellare file corrotto
   - Eseguire nuovo export
   - Verificare con editor testo

## Diagnostica Avanzata

### Abilita Logging Debug

```bash
idf.py menuconfig
# Component config → Log output → Default log level → Debug

# Oppure in codice:
esp_log_level_set("*", ESP_LOG_DEBUG);
```

### Monitor Seriale con Filtri

```bash
# Solo errori
idf.py monitor | grep "E ("

# Solo tag specifico
idf.py monitor | grep "CALIBRO"

# Salva log su file
idf.py monitor > debug.log
```

### Dump Configurazione

```bash
# In monitor seriale, comando:
config_dump()

# Output:
# Mode: CALIBRO
# Encoder: 1234 pulses, 123.45mm
# Puntali: calibrati=true, zero=0.123mm
# SD: montata, 12.3GB liberi
```

### Test Hardware

Menu Settings → Diagnostics → Hardware Test:

1. **Encoder Test**
   - Muovere puntali 100mm
   - Verificare count ~80000 pulses

2. **Display Test**
   - Pattern RGB
   - Verifica pixel morti

3. **Touch Test**
   - Griglia 5×5 punti
   - Toccare tutti i punti

4. **SD Card Test**
   - Write test: 1MB file
   - Read test: verify CRC32

5. **Bluetooth Test**
   - Scan devices
   - Test pairing

## Reset e Recovery

### Soft Reset

```bash
# Da codice
esp_restart();

# Da menu
Menu → Settings → System → Reboot
```

### Factory Reset (Keep Calibration)

```bash
# Cancella configurazioni, mantiene calibrazione
Menu → Settings → Advanced → Reset Settings
```

### Full Factory Reset

```bash
# Cancella tutto inclusa calibrazione
Menu → Settings → Advanced → Factory Reset

# Oppure da seriale:
nvs_flash_erase();
esp_restart();
```

### Recovery Mode

Se dispositivo non bootable:

1. **Erase flash completo**
   ```bash
   esptool.py erase_flash
   ```

2. **Flash partition table**
   ```bash
   esptool.py write_flash 0x8000 partition-table.bin
   ```

3. **Flash bootloader + firmware**
   ```bash
   idf.py flash
   ```

## Log Comuni e Significati

### OK - Normale
```
I (123) MAIN: Boot complete, version 2.0.0
I (456) ENCODER: Initialized, resolution 0.005mm
I (789) STORAGE: SD card mounted successfully
```

### Warning - Attenzione
```
W (111) PUNTALE: Not calibrated, accuracy reduced
W (222) SD_CARD: Low space, <100MB available
W (333) BLE: Connection unstable, RSSI -85dBm
```

### Error - Errore
```
E (444) ENCODER: No pulses detected!
E (555) STORAGE: Write failed, SD full
E (666) TOUCH: I2C communication error
```

## Contatti Supporto

### Prima di Contattare

Preparare le seguenti informazioni:

- **Versione firmware**: Menu → About
- **Log seriale**: ultimi 100 righe
- **Foto problema**: se visivo
- **Step riproducibili**: per replicare

### Canali Supporto

- 📧 **Email**: support@metrodigitale.example
- 📞 **Telefono**: +39 XXX XXX XXXX (Lun-Ven 9-18)
- 💬 **Forum**: https://forum.metrodigitale.example
- 🐛 **Bug Report**: https://github.com/house79-gex/metro-digitale/issues

### Tempi di Risposta

- **Critico** (dispositivo inutilizzabile): 4 ore
- **Alto** (funzionalità principale non funzionante): 24 ore
- **Medio** (funzionalità secondaria): 3 giorni
- **Basso** (domanda generica): 7 giorni

## FAQ - Domande Frequenti

**Q: Quanto dura la batteria?**  
A: 3.5-4 ore uso intenso, 6-8 ore uso normale.

**Q: Posso usare puntali diversi?**  
A: Sì, ma devono essere circolari Ø30mm. Ricalibrare dopo sostituzione.

**Q: SD card massima supportata?**  
A: 32GB (FAT32). Card >32GB usare exFAT.

**Q: Precisione garantita?**  
A: ±0.01mm su 1000mm dopo calibrazione corretta.

**Q: Impermeabilità?**  
A: NO. Evitare acqua/umidità. Solo uso interno.

**Q: Aggiornamenti firmware?**  
A: Check updates in Menu → About → Check Updates
