# Metro Digitale Configurator

Applicazione Windows per configurazione visuale del Metro Digitale ESP32.

## Caratteristiche

- 🎨 **Editor Visuale**: Drag & drop per design interfaccia display 800x480
- 📐 **Editor Formule**: Parser matematico con validazione e test
- 🎯 **Browser Icone**: Accesso a 200,000+ icone gratuite da Iconify
- 🎨 **Palette Colori**: Generatore palette con preset predefiniti
- 📤 **Upload ESP32**: Caricamento configurazione via USB seriale
- 💾 **Gestione Progetti**: Salvataggio/caricamento file .mdp
- 📋 **Menu Editor**: Gestione menu gerarchici ad albero
- 🪟 **Tipologie Infisso**: Configurazione tipologie con formule

## Installazione

### Requisiti

- Python 3.8+
- Windows 10/11 (o Linux/macOS con modifiche minori)

### Setup

```bash
cd configurator

# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente (Windows)
venv\Scripts\activate

# Attiva ambiente (Linux/macOS)
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

## Utilizzo

```bash
# Avvia applicazione
python main.py
```

## Struttura Progetto

```
configurator/
├── main.py                      # Entry point
├── requirements.txt             # Dipendenze
├── README.md                    # Questa documentazione
│
├── core/                        # Logica core
│   ├── config_model.py          # Modelli dati
│   ├── formula_parser.py        # Parser formule
│   ├── project_manager.py       # Gestione progetti
│   ├── esp_uploader.py          # Upload ESP32
│   ├── icon_browser.py          # Client Iconify
│   └── color_palette.py         # Generatore colori
│
├── ui/                          # Interfaccia utente
│   ├── main_window.py           # Finestra principale
│   ├── canvas_widget.py         # Canvas drag & drop
│   ├── toolbox_widget.py        # Toolbox elementi
│   ├── properties_panel.py      # Pannello proprietà
│   ├── menu_editor.py           # Editor menu
│   ├── formula_editor.py        # Editor formule
│   ├── tipologia_editor.py      # Editor tipologie
│   ├── icon_browser_dialog.py   # Dialog icone
│   ├── color_picker_dialog.py   # Dialog colori
│   ├── upload_dialog.py         # Dialog upload
│   └── preview_widget.py        # Preview display
│
├── widgets/                     # Widget custom
│   └── (draggable widgets)
│
├── resources/                   # Risorse
│   ├── icons/                   # Icone applicazione
│   ├── styles/                  # Stylesheet
│   │   └── dark_theme.qss       # Tema dark
│   └── templates/               # Template progetti
│       └── standard_serramenti.mdp
│
└── tests/                       # Test unitari
    └── test_*.py
```

## Funzionalità Principali

### 1. Canvas Drag & Drop

- Display simulato 800x480 pixel
- Griglia magnetica per allineamento
- Selezione multipla con Ctrl+click
- Zoom con Ctrl+rotella mouse
- Copia/incolla elementi

### 2. Editor Formule

- Supporto operatori: `+`, `-`, `*`, `/`, `(`, `)`
- Variabili: `L`, `H`, `B`, `S` (personalizzabili)
- Funzioni: `round()`, `abs()`, `min()`, `max()`
- Validazione real-time
- Test con valori di esempio

Esempio formula:
```
(L + 6) / 2
```

### 3. Browser Icone

- 200,000+ icone gratuite da Iconify
- Set raccomandati: Material Design, Tabler, Lucide, Phosphor
- Ricerca per keyword
- Suggerimenti per serramenti:
  - **Finestre**: window, frame, glass
  - **Porte**: door, entrance, gate
  - **Strumenti**: ruler, measure, tool
  - **Azioni**: save, send, settings

### 4. Upload ESP32

- Auto-detect dispositivi ESP32
- Progress bar upload
- Log operazioni
- Protocollo seriale 115200 baud

## Keyboard Shortcuts

- `Ctrl+N`: Nuovo progetto
- `Ctrl+O`: Apri progetto
- `Ctrl+S`: Salva progetto
- `Ctrl+Z`: Annulla
- `Ctrl+Y`: Ripeti
- `Ctrl+C`: Copia
- `Ctrl+V`: Incolla
- `Delete`: Elimina
- `Ctrl+rotella`: Zoom canvas

## Formato File .mdp

I progetti sono salvati in formato JSON con estensione `.mdp`:

```json
{
  "version": "1.0.0",
  "nome": "Progetto Esempio",
  "created": "2024-01-01T00:00:00",
  "modified": "2024-01-01T00:00:00",
  "menus": [...],
  "tipologie": [...],
  "astine": [...],
  "fermavetri": [...],
  "impostazioni": {}
}
```

## Build Executable

Per creare eseguibile Windows:

```bash
# Installa PyInstaller
pip install pyinstaller

# Build
pyinstaller --onefile --windowed --name="MetroDigitaleConfigurator" main.py
```

L'eseguibile sarà in `dist/MetroDigitaleConfigurator.exe`

## Protocollo ESP32

Comunicazione seriale 115200 baud:

1. `CONFIG_START\n` - Inizia upload
2. JSON configurazione a blocchi (1024 bytes)
3. `CONFIG_END\n` - Fine upload
4. Attesa `ACK`
5. `CONFIG_SAVE\n` - Salva su NVS

## Test

```bash
# Esegui test unitari
pytest tests/
```

## Troubleshooting

### ESP32 non rilevato

- Verificare driver USB CH340/CP2102
- Controllare porta COM in Gestione Dispositivi
- Provare cavo USB diverso

### Icone non caricate

- Verificare connessione internet
- Cache icone in `~/.metro_digitale/icons`
- Cancellare cache e riprovare

### Errore avvio applicazione

- Verificare Python 3.8+
- Reinstallare dipendenze: `pip install -r requirements.txt --force-reinstall`
- Controllare conflitti librerie Qt

## Licenza

MIT License - Vedere file LICENSE nel repository principale

## Autore

Progetto Metro Digitale Multifunzione

## Supporto

Per problemi o suggerimenti, aprire issue su GitHub.
