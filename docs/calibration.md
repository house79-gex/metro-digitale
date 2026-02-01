# Procedura Calibrazione - Metro Digitale v2.0

Guida completa alla calibrazione del Metro Digitale con puntali circolari da 30mm.

## Quando Calibrare

### Calibrazione Obbligatoria
- ✅ Prima accensione dopo installazione
- ✅ Dopo sostituzione puntali
- ✅ Ogni inizio turno di lavoro
- ✅ Dopo urto/caduta strumento
- ✅ Se misure mostrano deriva costante

### Calibrazione Consigliata
- 📅 Settimanale: verifica zero
- 📅 Mensile: test accuratezza con calibro di riferimento
- 📅 Trimestrale: compensazione usura puntali

## Preparazione

### Materiali Necessari
- Metro Digitale v2.0
- Panno morbido/microfibra
- Calibro di riferimento (opzionale, per verifica)
- Blocchetti campione (opzionale)

### Condizioni Ambientali
- **Temperatura**: 20°C ± 2°C
- **Umidità**: 40-60%
- **Vibrazioni**: Minime (tavolo stabile)
- **Illuminazione**: Buona per ispezione visiva

## Wizard Azzeramento (5 Step)

### Step 1: Welcome - Introduzione

**Cosa fa:**
- Presenta la procedura
- Stima tempo: 2-3 minuti
- Mostra prerequisiti

**Azioni utente:**
- Leggere istruzioni
- Toccare "Avanti"

### Step 2: Prepare - Preparazione

**Istruzioni visualizzate:**
```
1. Pulire accuratamente entrambi i puntali
2. Rimuovere polvere, trucioli, sporco
3. Asciugare con panno morbido
4. Verificare assenza graffi/danni
```

**Checklist:**
- [ ] Puntale fisso SX pulito
- [ ] Puntale mobile DX pulito
- [ ] Nessun danno visibile
- [ ] Movimento scorrevole

**Azioni utente:**
- Eseguire pulizia
- Verificare stato puntali
- Toccare "Avanti" quando pronto

### Step 3: Position - Posizione Zero

**Istruzioni visualizzate:**
```
1. Portare puntali a contatto completo
2. Applicare pressione moderata
3. Verificare contatto uniforme
4. Mantenere posizione
5. Confermare zero
```

**Display mostra:**
- Lettura encoder corrente (live)
- Icona puntali a contatto
- Pulsante "CONFERMA ZERO"

**Azioni utente:**
- Chiudere puntali fino a contatto
- Verificare visivamente contatto
- Toccare "CONFERMA ZERO"

**Sistema salva:**
```c
encoder_reading_zero = 0.123mm  // Lettura encoder attuale
puntali_calibrati = true
timestamp_calibrazione = now()
```

### Step 4: Verify - Verifica

**Istruzioni visualizzate:**
```
1. Aprire puntali (~50mm)
2. Richiudere fino a contatto
3. Verificare lettura zero (±0.1mm)
4. Se OK → Completa
5. Se NO → Ripeti da Step 2
```

**Display mostra:**
- Lettura encoder corrente
- Differenza da zero (Δ)
- LED verde/rosso (tolleranza ±0.1mm)

**Verifica automatica:**
```c
if (abs(current_reading - zero_reading) <= 0.1mm) {
    // OK - Passa a Step 5
} else {
    // Errore - Ripeti da Step 2
    show_error("Tolleranza superata, ripeti calibrazione");
}
```

**Azioni utente:**
- Aprire e richiudere puntali
- Verificare LED verde
- Toccare "Avanti" se OK

### Step 5: Complete - Completamento

**Messaggio visualizzato:**
```
✅ Calibrazione completata con successo!

Zero salvato: 0.123mm
Timestamp: 2024-02-01 10:30:15
Tolleranza verificata: ±0.05mm

Prossima calibrazione consigliata:
2024-02-02 08:00:00
```

**Sistema salva su NVS:**
- Distanza zero
- Timestamp calibrazione
- Flag calibrato = true

**Azioni utente:**
- Leggere conferma
- Toccare "Completa"
- Tornare a modalità operativa

## Progress Bar Wizard

Durante il wizard, una barra di progresso mostra l'avanzamento:

```
Step 1: Welcome     [▰▱▱▱▱] 20%
Step 2: Prepare     [▰▰▱▱▱] 40%
Step 3: Position    [▰▰▰▱▱] 60%
Step 4: Verify      [▰▰▰▰▱] 80%
Step 5: Complete    [▰▰▰▰▰] 100%
```

## Feedback Buzzer

Il buzzer fornisce feedback audio per ogni step:

- **Step avanzato**: Beep singolo (100ms)
- **Zero confermato**: Doppio beep (2×100ms)
- **Verifica OK**: Triplo beep (3×100ms)
- **Errore**: Beep lungo (500ms)

## Calibrazione Manuale Veloce

### Double Click Pulsante SEND

Alternativa rapida al wizard (per utenti esperti):

1. **Pulire puntali** (manualmente)
2. **Portare a contatto**
3. **Double click SEND** (<400ms tra click)
4. **Verifica automatica** (tolleranza ±0.1mm)
5. **Conferma** (beep triplo)

**Nota**: Non mostra wizard, ma esegue stessa verifica.

## Test Accuratezza

### Test con Calibro di Riferimento

Dopo calibrazione, verificare accuratezza con calibro campione:

1. **Azzerare entrambi** (Metro Digitale + Calibro riferimento)
2. **Misurare oggetto noto** (es. blocchetto 100.00mm)
3. **Confrontare letture**:
   ```
   Metro Digitale: 100.02mm
   Calibro riferimento: 100.00mm
   Differenza: +0.02mm ✅ (OK)
   ```
4. **Ripetere 5 volte** in posizioni diverse
5. **Calcolare media e deviazione**

### Tolleranze Accettabili

| Dimensione | Tolleranza Max |
|------------|----------------|
| 0-100mm | ±0.02mm |
| 100-500mm | ±0.05mm |
| 500-1000mm | ±0.10mm |
| 1000-2000mm | ±0.20mm |

### Test con Blocchetti Campione

Set blocchetti raccomandati:
- 10.00mm
- 50.00mm
- 100.00mm
- 200.00mm

Procedura per ogni blocchetto:
1. Azzerare Metro Digitale
2. Misurare blocchetto 3 volte
3. Calcolare media
4. Verificare differenza ≤ ±0.02mm

## Compensazione Usura Puntali

### Quando Necessaria

Dopo ~1000 misure o quando si rileva deriva costante.

### Procedura

1. **Menu Settings** → "Puntali" → "Compensazione Usura"
2. **Misurare blocchetto campione** (es. 100.00mm)
3. **Inserire valore nominale**: 100.00mm
4. **Sistema calcola offset usura**:
   ```c
   offset_usura = valore_nominale - valore_misurato
   offset_usura = 100.00 - 100.15 = -0.15mm
   ```
5. **Salvare offset** su NVS
6. **Ri-verificare** misurando blocchetto

### Limiti Usura

- **Accettabile**: ±0.3mm
- **Attenzione**: ±0.5mm (pianificare sostituzione)
- **Critico**: >±0.8mm (sostituire immediatamente)

## Risoluzione Problemi

### Zero Instabile (±0.5mm)

**Cause possibili:**
- Puntali sporchi → Pulire accuratamente
- Temperatura variabile → Stabilizzare ambiente
- Encoder danneggiato → Controllare collegamenti

**Soluzione:**
1. Pulizia approfondita puntali
2. Attendere stabilizzazione temperatura (10 min)
3. Ripetere calibrazione
4. Se persiste → Verificare hardware

### Deriva Costante (+0.2mm ogni misura)

**Cause possibili:**
- Usura puntali → Compensare offset
- Encoder non fissato → Stringere fissaggio
- Temperatura in variazione → Stabilizzare

**Soluzione:**
1. Eseguire test accuratezza
2. Applicare compensazione usura
3. Verificare fissaggio meccanico
4. Controllare temperatura

### Tolleranza Verifica Fallisce

**Messaggio:** "Tolleranza superata, ripeti calibrazione"

**Cause possibili:**
- Contatto puntali non perfetto → Riprovare
- Encoder instabile → Attendere stabilizzazione
- Hardware difettoso → Test diagnostico

**Soluzione:**
1. Verificare pulizia puntali
2. Applicare pressione uniforme
3. Attendere 2 secondi prima di confermare
4. Ripetere Step 3 del wizard

## Manutenzione Periodica

### Giornaliera
- ✅ Pulizia puntali con panno morbido
- ✅ Verifica visiva danni/graffi
- ✅ Test zero rapido

### Settimanale
- ✅ Calibrazione completa wizard
- ✅ Test accuratezza con blocchetto
- ✅ Backup configurazioni

### Mensile
- ✅ Test con set blocchetti completo
- ✅ Verifica usura puntali
- ✅ Pulizia encoder (aria compressa)

### Trimestrale
- ✅ Compensazione usura puntali
- ✅ Taratura con calibro riferimento
- ✅ Aggiornamento firmware (se disponibile)

## Registro Calibrazioni

Tenere un registro delle calibrazioni per tracciabilità:

```
Data       | Operatore | Tipo          | Zero (mm) | Δ (mm) | Note
-----------|-----------|---------------|-----------|--------|------------------
2024-02-01 | Mario R.  | Wizard        | 0.123     | +0.02  | Prima calibrazione
2024-02-02 | Luigi B.  | Double Click  | 0.118     | +0.01  | Routine giornaliera
2024-02-08 | Mario R.  | Wizard        | 0.125     | +0.05  | Dopo pulizia
```

## Certificazione

Per uso in ambiente con requisiti metrologici:

1. **Calibrazione iniziale** da tecnico qualificato
2. **Certificato di taratura** con tracciabilità campioni
3. **Ricalibrazioni annuali** da laboratorio accreditato
4. **Registro verifiche** intermedie documentate

## Contatti Supporto

Per problemi di calibrazione non risolvibili:

- 📧 Email: support@metrodigitale.example
- 📞 Telefono: +39 XXX XXX XXXX
- 🌐 Web: https://support.metrodigitale.example
- 💬 Forum: https://forum.metrodigitale.example
