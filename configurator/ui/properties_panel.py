"""
Pannello proprietà elemento selezionato
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QScrollArea,
    QGroupBox, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PropertiesPanel(QWidget):
    """Pannello per editare proprietà elementi selezionati"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titolo
        title = QLabel("Proprietà")
        title.setProperty("heading", True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area per proprietà
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        
        scroll.setWidget(self.properties_widget)
        layout.addWidget(scroll)
        
        self.current_item = None
        
        self._show_empty_message()
    
    def _show_empty_message(self):
        """Mostra messaggio quando nessun elemento selezionato"""
        self._clear_layout()
        
        label = QLabel("Nessun elemento selezionato")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("text-secondary", True)
        self.properties_layout.addWidget(label)
        self.properties_layout.addStretch()
    
    def _clear_layout(self):
        """Pulisce layout proprietà"""
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_item(self, item):
        """Imposta elemento da mostrare"""
        self.current_item = item
        self._update_properties()
    
    def clear(self):
        """Pulisce pannello"""
        self.current_item = None
        self._show_empty_message()
    
    def _update_properties(self):
        """Aggiorna proprietà mostrate"""
        self._clear_layout()
        
        if not self.current_item:
            self._show_empty_message()
            return
        
        # Gruppo posizione
        pos_group = QGroupBox("Posizione e Dimensione")
        pos_layout = QFormLayout()
        
        x_spin = QSpinBox()
        x_spin.setRange(0, 800)
        x_spin.setValue(0)
        pos_layout.addRow("X:", x_spin)
        
        y_spin = QSpinBox()
        y_spin.setRange(0, 480)
        y_spin.setValue(0)
        pos_layout.addRow("Y:", y_spin)
        
        width_spin = QSpinBox()
        width_spin.setRange(10, 800)
        width_spin.setValue(100)
        pos_layout.addRow("Larghezza:", width_spin)
        
        height_spin = QSpinBox()
        height_spin.setRange(10, 480)
        height_spin.setValue(50)
        pos_layout.addRow("Altezza:", height_spin)
        
        pos_group.setLayout(pos_layout)
        self.properties_layout.addWidget(pos_group)
        
        # Gruppo aspetto
        style_group = QGroupBox("Aspetto")
        style_layout = QFormLayout()
        
        color_btn = QPushButton("Scegli colore...")
        color_btn.clicked.connect(self._choose_color)
        style_layout.addRow("Colore:", color_btn)
        
        style_group.setLayout(style_layout)
        self.properties_layout.addWidget(style_group)
        
        self.properties_layout.addStretch()
    
    def _choose_color(self):
        """Apri color picker"""
        color = QColorDialog.getColor(QColor("#00ff88"), self)
        if color.isValid():
            # Applica colore
            pass
