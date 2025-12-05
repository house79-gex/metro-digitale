"""
Dialog selettore colori con palette predefinite
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QColorDialog, QGridLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.color_palette import ColorPaletteGenerator


class ColorPickerDialog(QDialog):
    """Dialog per selezionare colori con palette"""
    
    color_selected = pyqtSignal(str)
    
    def __init__(self, initial_color: str = "#00ff88", parent=None):
        super().__init__(parent)
        
        self.selected_color = initial_color
        self.palette_gen = ColorPaletteGenerator()
        
        self.setWindowTitle("Seleziona Colore")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Colore corrente
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Colore selezionato:"))
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(100, 40)
        self.color_preview.setStyleSheet(f"background-color: {initial_color}; border: 1px solid #3b4b5a;")
        current_layout.addWidget(self.color_preview)
        
        self.color_hex_label = QLabel(initial_color)
        current_layout.addWidget(self.color_hex_label)
        current_layout.addStretch()
        
        custom_btn = QPushButton("Colore personalizzato...")
        custom_btn.clicked.connect(self._on_custom_color)
        current_layout.addWidget(custom_btn)
        
        layout.addLayout(current_layout)
        
        # Palette predefinite
        presets_group = QGroupBox("Palette Predefinite")
        presets_layout = QVBoxLayout()
        
        for name, colors in self.palette_gen.PRESETS.items():
            preset_layout = QHBoxLayout()
            preset_layout.addWidget(QLabel(name))
            
            for color in colors:
                btn = QPushButton()
                btn.setFixedSize(40, 30)
                btn.setStyleSheet(f"background-color: {color}; border: 1px solid #3b4b5a;")
                btn.clicked.connect(lambda checked, c=color: self._on_color_selected(c))
                preset_layout.addWidget(btn)
            
            preset_layout.addStretch()
            presets_layout.addLayout(preset_layout)
        
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        layout.addStretch()
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setProperty("primary", True)
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_color_selected(self, color: str):
        """Gestisce selezione colore"""
        self.selected_color = color
        self.color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid #3b4b5a;")
        self.color_hex_label.setText(color)
        self.color_selected.emit(color)
    
    def _on_custom_color(self):
        """Apri dialog colore personalizzato"""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            hex_color = color.name()
            self._on_color_selected(hex_color)
    
    def get_color(self) -> str:
        """Ottiene colore selezionato"""
        return self.selected_color
