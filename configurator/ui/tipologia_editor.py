"""
Editor tipologie infisso
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QToolButton
)
from PyQt6.QtCore import Qt
from typing import List

from core.config_model import TipologiaInfisso


class TipologiaEditor(QWidget):
    """Editor per tipologie infisso"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_add = QToolButton()
        self.btn_add.setText("+")
        self.btn_add.setToolTip("Aggiungi tipologia")
        self.btn_add.clicked.connect(self._on_add_tipologia)
        toolbar.addWidget(self.btn_add)
        
        self.btn_remove = QToolButton()
        self.btn_remove.setText("−")
        self.btn_remove.setToolTip("Rimuovi tipologia")
        self.btn_remove.clicked.connect(self._on_remove_tipologia)
        toolbar.addWidget(self.btn_remove)
        
        toolbar.addStretch()
        
        self.btn_edit = QPushButton("Modifica")
        self.btn_edit.clicked.connect(self._on_edit_tipologia)
        toolbar.addWidget(self.btn_edit)
        
        layout.addLayout(toolbar)
        
        # Lista tipologie
        self.list = QListWidget()
        layout.addWidget(self.list)
        
        self.tipologie = []
    
    def load_tipologie(self, tipologie: List[TipologiaInfisso]):
        """Carica tipologie nell'editor"""
        self.tipologie = tipologie
        self._update_list()
    
    def get_tipologie(self) -> List[TipologiaInfisso]:
        """Ottiene tipologie dall'editor"""
        return self.tipologie
    
    def _update_list(self):
        """Aggiorna lista visualizzata"""
        self.list.clear()
        for tip in self.tipologie:
            self.list.addItem(f"{tip.nome} ({tip.categoria})")
    
    def _on_add_tipologia(self):
        """Aggiungi nuova tipologia"""
        tipologia = TipologiaInfisso(
            id=f"tip_{len(self.tipologie)}",
            nome="Nuova Tipologia",
            icona="mdi:window",
            categoria="Generica"
        )
        self.tipologie.append(tipologia)
        self._update_list()
    
    def _on_remove_tipologia(self):
        """Rimuovi tipologia selezionata"""
        current_row = self.list.currentRow()
        if current_row >= 0:
            del self.tipologie[current_row]
            self._update_list()
    
    def _on_edit_tipologia(self):
        """Modifica tipologia selezionata"""
        current_row = self.list.currentRow()
        if current_row >= 0:
            # TODO: Apri dialog editing tipologia
            pass
