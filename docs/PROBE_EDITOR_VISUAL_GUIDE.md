# Editor Puntali Avanzato - Guida Visiva

## Layout Interfaccia

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          ✏️ Editor Grafico Puntale Avanzato con Snap                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌────────────────────────────────────────────────────────────────────────────┐
│ Toolbar Riga 1: Strumenti Disegno                                         │
├────────────────────────────────────────────────────────────────────────────┤
│ Disegno: [📏 Linea] ⬆️ ⬇️ ⬅️ ➡️   Contatto: [🟢 INT] [🟣 EST]   ↶ ↷ 🗑️   │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ Toolbar Riga 2: Snap e Vincoli                                            │
├────────────────────────────────────────────────────────────────────────────┤
│ Snap: ☑Grid ☑Endpoint ☑Midpoint ☐Perp  Vincoli: ☐Ortho ☐45°  Grid: 20px │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│  Canvas Area (Sfondo: #f5f5f5 - Grigio Chiaro)                           │
│  ╔══════════════════════════════════════════════════════════════════╗    │
│  ║ · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · · · · · · · · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · · · · · · · · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · ┏━━━━━━━┓· · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · ┃       ┃· · · · · ⬆️ · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · ┃   🟢  ┃· · · · · · · · · · · · · · ║    │
│  ║ ━━━━━━━━━━━━━━━━━━━╋━━━━┻━━━━━━━┛· · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · · · · · · · · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · · · · · · · · · · · · · · · · · · · · ║    │
│  ║ · · · · · · · · · ·┃· · · · · · · · · · · · · · · · · · · · · ║    │
│  ╚══════════════════════════════════════════════════════════════════╝    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ Status Bar                                                                 │
├────────────────────────────────────────────────────────────────────────────┤
│ Pos: (250, 180) | Snap: Grid ✕ | Elementi: 5 linee, 2 frecce, 1 contatti│
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ [💾 Salva Puntale]  [📂 Carica Puntale]                          [Chiudi] │
└────────────────────────────────────────────────────────────────────────────┘
```

## Indicatori Snap Visivi

### Grid Snap (Arancione)
```
    |
  ──✕──
    |
```
**Colore:** #ff8800 (Arancione)  
**Quando appare:** Mouse vicino a un punto della griglia  
**Scorciatoia:** Attiva/disattiva con checkbox "Grid"

### Endpoint Snap (Rosso)
```
  ┌───┐
  │   │
  └───┘
```
**Colore:** #ff0000 (Rosso)  
**Quando appare:** Mouse vicino all'estremo di una linea  
**Scorciatoia:** Attiva/disattiva con checkbox "Endpoint"

### Midpoint Snap (Verde)
```
    ▲
   ╱ ╲
  ╱___╲
```
**Colore:** #00ff00 (Verde)  
**Quando appare:** Mouse vicino al punto medio di una linea  
**Scorciatoia:** Attiva/disattiva con checkbox "Midpoint"

### Perpendicular Snap (Blu)
```
    |
  ──┼
    |
```
**Colore:** #0088ff (Blu)  
**Quando appare:** Disegno perpendicolare a linea esistente  
**Scorciatoia:** Attiva/disattiva con checkbox "Perp"

## Modalità Disegno

### 1. Disegno Libero
```
Punto A ────────────> Punto B
        (qualsiasi angolo)
```
**Come:** Clicca e trascina senza premere tasti

### 2. Disegno Ortogonale (Shift)
```
Punto A ─────────────> Punto B  (0° o 180°)

Punto A               
   │                  (90° o 270°)
   │
   ▼
Punto B
```
**Come:** Tieni premuto **Shift** durante il disegno

### 3. Disegno 45° (Ctrl)
```
Punto A
   ╲
    ╲  45°
     ╲
      ▼
   Punto B
```
**Come:** Tieni premuto **Ctrl** durante il disegno

## Elementi Puntale

### Linee (📏)
```
P1 ━━━━━━━━━━━━━━━ P2
```
**Uso:** Definisce la geometria del puntale  
**Strumento:** Pulsante "📏 Linea"  
**Disegno:** Clicca punto iniziale, trascina, rilascia punto finale

### Frecce Direzionali (⬆️⬇️⬅️➡️)
```
      ⬆️
      ║
      ║
    ═════
```
**Uso:** Indica direzioni di misurazione o applicazione forza  
**Strumento:** Pulsanti freccia  
**Disegno:** Clicca posizione dove posizionare la freccia

### Appoggio Interno (🟢 INT)
```
    ╔═════╗
    ║ INT ║
    ║  🟢 ║
    ╚═════╝
```
**Uso:** Marca punto di appoggio interno del puntale  
**Colore:** Verde (#00ff00)  
**Strumento:** Pulsante "🟢 INT"

### Appoggio Esterno (🟣 EST)
```
    ╔═════╗
    ║ EST ║
    ║  🟣 ║
    ╚═════╝
```
**Uso:** Marca punto di appoggio esterno del puntale  
**Colore:** Magenta (#ff00ff)  
**Strumento:** Pulsante "🟣 EST"

## Info Dimensionali Durante Disegno

Mentre disegni una linea, vedi in tempo reale:

```
           125.3px @ 45.0°
              ↓
    P1 ─────────────────── P2
```

- **125.3px**: Lunghezza della linea
- **45.0°**: Angolo rispetto all'orizzontale (positivo in senso antiorario)

## Scorciatoie Tastiera

| Tasto | Azione | Descrizione |
|-------|--------|-------------|
| **Shift** | Ortho | Vincolo ortogonale temporaneo |
| **Ctrl** | 45° | Vincolo 45° temporaneo |
| **Ctrl+Z** | Undo | Annulla ultima operazione |
| **Ctrl+Y** | Redo | Ripristina operazione annullata |

## Workflow Tipico

### 1. Disegna Contorno Puntale
```
1. Seleziona strumento "📏 Linea"
2. Abilita "Grid" e "Endpoint" snap
3. Clicca punto iniziale
4. Trascina con Shift per linee ortogonali
5. Rilascia su punto snap (apparirà indicatore)
6. Ripeti per completare contorno
```

### 2. Aggiungi Direzioni
```
1. Seleziona freccia appropriata (⬆️⬇️⬅️➡️)
2. Clicca su punto puntale dove indicare direzione
3. Freccia appare automaticamente
```

### 3. Marca Punti Appoggio
```
1. Seleziona "🟢 INT" per appoggio interno
2. Clicca sul punto di contatto interno
3. Seleziona "🟣 EST" per appoggio esterno
4. Clicca sul punto di contatto esterno
```

### 4. Salva Puntale
```
1. Clicca "💾 Salva Puntale"
2. Scegli nome file (es: "puntale_cilindrico.probe.json")
3. File salvato in formato JSON
```

## Esempi Visuali

### Puntale Cilindrico
```
     ⬆️ Direzione Misura
     ║
     ║
  ┏━━╋━━┓
  ┃  ║  ┃
  ┃ 🟢  ┃ ← Appoggio Interno
  ┃  ║  ┃
  ┗━━╋━━┛
     ║
```

### Puntale a Sfera
```
       ⬆️
       ║
    ╱━━╋━━╲
   ╱   ║   ╲
  │   🟢    │
   ╲   ║   ╱
    ╲━━╋━━╱
       ║
```

### Puntale Piatto
```
  ⬅️═══════════════════════════➡️
  ┃                           ┃
  ┃          🟢              ┃
  ┃                           ┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
          Appoggio
```

## Palette Colori

| Elemento | Colore | Hex | RGB |
|----------|--------|-----|-----|
| Sfondo Canvas | Grigio Chiaro | #f5f5f5 | (245, 245, 245) |
| Linee | Nero | #1a1a1a | (26, 26, 26) |
| Griglia | Grigio | #d0d0d0 | (208, 208, 208) |
| Assi | Blu | #0088ff | (0, 136, 255) |
| Snap Grid | Arancione | #ff8800 | (255, 136, 0) |
| Snap Endpoint | Rosso | #ff0000 | (255, 0, 0) |
| Snap Midpoint | Verde | #00ff00 | (0, 255, 0) |
| Snap Perp | Blu | #0088ff | (0, 136, 255) |
| Appoggio INT | Verde | #00ff00 | (0, 255, 0) |
| Appoggio EST | Magenta | #ff00ff | (255, 0, 255) |
| Frecce | Rosso | #ff0000 | (255, 0, 0) |

## Tips e Trucchi

### 🎯 Per Disegno Preciso
1. Usa snap "Grid" per allineamento generale
2. Usa snap "Endpoint" per connettere linee
3. Usa snap "Midpoint" per simmetria

### ⚡ Per Velocità
1. Usa tasti Shift/Ctrl invece di checkbox per vincoli temporanei
2. Tieni premuto Shift per linee perfettamente orizzontali/verticali
3. Usa Ctrl+Z frequentemente - non aver paura di sperimentare

### 🎨 Per Precisione CAD
1. Imposta griglia piccola (5-10px) per dettagli fini
2. Abilita tutti gli snap per massima cattura
3. Guarda le info dimensionali in tempo reale

### 💾 Per Riutilizzo
1. Salva puntali standard come template
2. Usa nomi descrittivi (es: "puntale_cilindrico_d5mm.probe.json")
3. Carica e modifica puntali esistenti invece di ricreare da zero

---

## Supporto

Per problemi o domande:
- Consulta `docs/PROBE_EDITOR_IMPROVEMENTS.md` per dettagli tecnici
- Verifica test in `configurator/tests/test_probe_editor_*.py`
- Tutti i file puntale sono in formato JSON leggibile
