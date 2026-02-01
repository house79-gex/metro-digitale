# Modalità Operative - Metro Digitale v2.0

Questo documento descrive in dettaglio le 4 modalità operative del Metro Digitale v2.0.

## 1. Modalità Calibro Avanzato

Modalità di misura universale con funzionalità professionali.

### Caratteristiche
- **Tipi di misura**: Esterna, Interna (NO profondità)
- **Unità supportate**: mm, cm, inch, pollici frazionari (1/64")
- **Precisione**: ±0.01mm su 1000mm
- **Statistiche**: Min, Max, Media, Deviazione Standard in tempo reale

### Funzioni

#### Zero Assistito
1. Tocca pulsante "ZERO"
2. Segui wizard 5 step:
   - Welcome: introduzione
   - Prepare: pulizia puntali
   - Position: conferma posizione zero
   - Verify: test accuratezza
   - Complete: conferma successo
3. Calibrazione salvata su NVS

#### Hold (Blocco Misura)
- Blocca valore corrente
- Salva automaticamente in statistiche
- Icona cambia colore quando attivo

#### Statistiche Real-Time
- **Min**: Valore minimo rilevato
- **Max**: Valore massimo rilevato
- **Avg**: Media aritmetica
- **Std Dev**: Deviazione standard
- **Count**: Numero misure acquisite
- Reset con pulsante "RESET"

#### Tolleranza
- Imposta limiti superiore/inferiore
- LED virtuale verde/rosso indica stato
- Animazione pulse quando fuori tolleranza

### Workflow Operativo

```
1. Avvia modalità Calibro
   ↓
2. Seleziona tipo misura (Esterna/Interna)
   ↓
3. Scegli unità di misura
   ↓
4. Posiziona strumento su pezzo
   ↓
5. Premi SEND per salvare
   ↓
6. Verifica statistiche
```

### Conversioni Unità

| Da mm | A | Formula |
|-------|---|---------|
| mm | cm | mm × 0.1 |
| mm | inch | mm × 0.0393701 |
| mm | 1/64" | (mm × 0.0393701) × 64 |

### Formule Calcolo

**Misura Esterna:**
```
Distanza = Encoder - Zero + Offset_Usura
```

**Misura Interna:**
```
Distanza = Encoder - Zero + Diametro_SX + Diametro_DX + Offset_Usura
```

## 2. Modalità Vetri L×H

Wizard guidato per misura vetri con compensazione automatica gioco materiale.

### Materiali Predefiniti

| Materiale | Gioco per lato | Totale | Colore |
|-----------|---------------|--------|--------|
| Alluminio | 6mm | -12mm | Silver |
| Legno | 3mm | -6mm | Brown |
| PVC | 5mm | -10mm | White |
| Custom | 0mm | 0mm | Orange |

### Wizard Step

#### Step 1: Selezione Materiale
- Card visuali per ogni materiale
- Mostra gioco automatico
- Icona materiale

#### Step 2: Misura Larghezza
- Display live encoder
- Pulsante "📏 Misura L"
- Calcolo automatico netto

#### Step 3: Misura Altezza
- Display live encoder
- Pulsante "📏 Misura H"
- Calcolo automatico netto

#### Step 4: Review
- Mostra valori:
  - Larghezza grezza
  - Larghezza netta
  - Altezza grezza
  - Altezza netta
- Pulsanti: Conferma / Ripeti

#### Step 5: Salvataggio
- Salvataggio automatico su SD
- Invio JSON a app Android via BLE
- Conferma completamento

### Workflow Operativo

```
1. Seleziona materiale (es. Alluminio)
   ↓
2. Misura larghezza luce vano
   ↓
3. Premi "MISURA L"
   ↓
4. Misura altezza luce vano
   ↓
5. Premi "MISURA H"
   ↓
6. Rivedi misure (raw → netto)
   ↓
7. Salva su SD + invia BLE
```

### Calcoli Automatici

```
Larghezza_Netta = Larghezza_Grezza - Gioco_Totale
Altezza_Netta = Altezza_Grezza - Gioco_Totale

Dove:
Gioco_Totale = Gioco_Per_Lato × 2
```

### Esempio Pratico

```
Materiale: Alluminio (gioco 6mm/lato)
Larghezza misurata: 1200.0mm
Altezza misurata: 1500.0mm

Risultato:
Larghezza netta: 1200.0 - 12.0 = 1188.0mm
Altezza netta: 1500.0 - 12.0 = 1488.0mm
```

### Output JSON (App Android)

```json
{
  "larghezza_raw": 1200.0,
  "altezza_raw": 1500.0,
  "larghezza_netta": 1188.0,
  "altezza_netta": 1488.0,
  "materiale": "Alluminio",
  "quantita": 1,
  "gioco": 12.0,
  "timestamp": 1706800000
}
```

## 3. Modalità Astine

Gestione profili astine organizzati per gruppi con offset personalizzabili.

### Gruppi e Profili

#### Gruppo Anta Ribalta 🟣 (Viola)
1. **Inferiore AR**: -15mm
2. **Superiore AR**: -18mm
3. **Laterale AR**: -12mm
4. **Cremonese AR**: -25mm

#### Gruppo Persiana 🔵 (Blu)
5. **Inferiore Persiana**: -10mm
6. **Superiore Persiana**: -10mm

#### Gruppo Cremonese 🟢 (Verde)
7. **Cremonese Std**: -22mm
8. **Cremonese Corta**: -16mm

#### Gruppo Personalizzato 🟡 (Giallo)
9. **Custom 1**: 0mm (disattivo)
10. **Custom 2**: 0mm (disattivo)

### Workflow Operativo

```
1. Seleziona gruppo (tab)
   ↓
2. Seleziona profilo dalla griglia
   ↓
3. Misura lunghezza grezza vano
   ↓
4. Visualizza: Grezza → Taglio
   ↓
5. Premi "SALVA"
   ↓
6. Misura salvata su SD
```

### Calcolo Lunghezza Taglio

```
Lunghezza_Taglio = Lunghezza_Grezza + Offset_Profilo

Nota: Offset è negativo per accorciare
```

### Esempio Pratico

```
Profilo: Superiore AR (offset -18mm)
Lunghezza grezza: 1200.0mm

Calcolo:
Lunghezza taglio = 1200.0 + (-18.0) = 1182.0mm
```

### UI Elements

- **Tabs gruppi**: Navigazione rapida per gruppo
- **Grid profili**: 2 colonne, card selezionabili
- **Display doppio**: Grezza ← → Taglio con freccia colorata
- **Border attivo**: Colore del gruppo

## 4. Modalità Fermavetri

Invio diretto misure a troncatrice Blitz CNC con trigger automatico.

### Caratteristiche
- **Invio BLE**: Diretto a dispositivo Blitz
- **Auto-start**: Trigger automatico taglio
- **Modalità**: Semi-automatico / Automatico

### Workflow Operativo

```
1. Avvia modalità Fermavetri
   ↓
2. Imposta auto-start (ON/OFF)
   ↓
3. Misura fermavetro
   ↓
4. Premi SEND (o auto)
   ↓
5. Invio JSON a Blitz via BLE
   ↓
6. Troncatrice esegue taglio (se auto-start)
```

### Protocollo JSON per Blitz

```json
{
  "type": "fermavetro",
  "misura_mm": 1250.5,
  "auto_start": true,
  "mode": "semi_auto",
  "timestamp": 1706800000
}
```

### Modalità Semi-Automatica
- Misura inviata automaticamente
- Operatore conferma taglio su troncatrice
- Maggiore controllo

### Modalità Automatica
- Misura inviata + trigger taglio automatico
- Troncatrice parte subito
- Massima velocità

## Best Practices

### Calibrazione Puntali
- Eseguire calibrazione ogni inizio turno
- Pulire puntali prima di ogni calibrazione
- Verificare usura dopo 1000 misure

### Precisione Misure
- Posizionare puntali perpendicolarmente
- Evitare pressione eccessiva
- Controllare temperatura ambiente (±2°C per max precisione)

### Manutenzione
- Pulizia puntali giornaliera
- Lubrificazione encoder ogni 6 mesi
- Backup configurazioni settimanale

### Storage Ottimale
- SD card: Class 10 o superiore
- Export CSV settimanale per analisi
- Backup NVS prima di aggiornamenti firmware

## Troubleshooting

### Misure Instabili
1. Verificare pulizia puntali
2. Controllare calibrazione zero
3. Verificare fissaggio encoder

### Hold Non Funziona
1. Verificare che calibrazione sia completata
2. Controllare stato modalità

### Export CSV Fallisce
1. Verificare spazio SD card
2. Controllare formato file
3. Testare con lettore PC

### BLE Non Connette
1. Verificare Bluetooth abilitato
2. Controllare distanza dispositivi (<10m)
3. Restart modulo BLE
