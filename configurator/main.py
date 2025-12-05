"""
Metro Digitale Configurator - Entry Point
Applicazione PyQt6 per configurazione visuale Metro Digitale ESP32
"""

import sys
import os
from pathlib import Path

# Aggiungi directory parent al path per import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """Entry point applicazione"""
    
    # Abilita High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Metro Digitale Configurator")
    app.setOrganizationName("MetroDigitale")
    app.setApplicationVersion("1.0.0")
    
    # Carica stylesheet dark theme
    stylesheet_path = Path(__file__).parent / "resources" / "styles" / "dark_theme.qss"
    if stylesheet_path.exists():
        with open(stylesheet_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    # Crea e mostra finestra principale
    window = MainWindow()
    window.show()
    
    # Esegui applicazione
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
