"""
Dialog browser icone Iconify
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QLabel, QComboBox,
    QListWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, QSize, QByteArray, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
import io

try:
    from PyQt6.QtSvg import QSvgRenderer
    HAS_SVG = True
except ImportError:
    HAS_SVG = False

from core.icon_browser import IconifyClient


class IconBrowserDialog(QDialog):
    """Dialog per selezionare icone da Iconify"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.client = IconifyClient()
        self.selected_icon = None
        
        self.setWindowTitle("Browser Icone Iconify")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Barra ricerca
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca icone...")
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        
        self.set_combo = QComboBox()
        self.set_combo.addItem("Tutti i set", "")
        for prefix, name in self.client.RECOMMENDED_SETS:
            self.set_combo.addItem(name, prefix)
        search_layout.addWidget(self.set_combo)
        
        search_btn = QPushButton("Cerca")
        search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Suggerimenti rapidi
        suggestions_layout = QHBoxLayout()
        suggestions_layout.addWidget(QLabel("Suggerimenti:"))
        
        for category, keywords in [
            ("Finestre", "window"),
            ("Porte", "door"),
            ("Strumenti", "ruler"),
            ("Azioni", "save")
        ]:
            btn = QPushButton(category)
            btn.clicked.connect(lambda checked, kw=keywords: self._quick_search(kw))
            suggestions_layout.addWidget(btn)
        
        suggestions_layout.addStretch()
        layout.addLayout(suggestions_layout)
        
        # Lista risultati
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(48, 48))
        self.results_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.results_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.results_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.results_list)
        
        # Status
        self.status_label = QLabel("Cerca un'icona per iniziare")
        layout.addWidget(self.status_label)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Usa questa icona")
        select_btn.setProperty("primary", True)
        select_btn.clicked.connect(self._on_select)
        buttons_layout.addWidget(select_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_search(self):
        """Esegue ricerca icone"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        icon_set = self.set_combo.currentData()
        
        self.status_label.setText("Ricerca in corso...")
        self.results_list.clear()
        
        # Cerca icone
        results = self.client.search(query, limit=64, prefix=icon_set if icon_set else None)
        
        if not results:
            self.status_label.setText("Nessuna icona trovata")
            return
        
        # Mostra risultati con anteprima icone
        for icon_info in results:
            item = QListWidgetItem(icon_info.name)
            item.setData(Qt.ItemDataRole.UserRole, icon_info)
            
            # Carica e mostra icona SVG
            try:
                svg_data = self.client.get_icon_svg(icon_info.full_name)
                if svg_data:
                    pixmap = self._svg_to_pixmap(svg_data, 48, 48)
                    item.setIcon(QIcon(pixmap))
            except Exception as e:
                # Fallback: crea un'icona segnaposto colorata
                pixmap = self._create_placeholder_icon(icon_info.name[0].upper())
                item.setIcon(QIcon(pixmap))
            
            self.results_list.addItem(item)
        
        self.status_label.setText(f"Trovate {len(results)} icone")
    
    def _quick_search(self, keyword: str):
        """Ricerca rapida con keyword"""
        self.search_input.setText(keyword)
        self._on_search()
    
    def _on_item_double_clicked(self, item):
        """Doppio click su icona"""
        self.selected_icon = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
    
    def _on_select(self):
        """Seleziona icona corrente"""
        current = self.results_list.currentItem()
        if current:
            self.selected_icon = current.data(Qt.ItemDataRole.UserRole)
            self.accept()
    
    def get_selected_icon(self):
        """Ottiene icona selezionata"""
        return self.selected_icon
    
    def _svg_to_pixmap(self, svg_data: str, width: int, height: int) -> QPixmap:
        """Converte SVG in QPixmap"""
        if not HAS_SVG:
            # Fallback se SVG non disponibile
            return self._create_placeholder_icon("?")
        
        try:
            svg_bytes = QByteArray(svg_data.encode('utf-8'))
            renderer = QSvgRenderer(svg_bytes)
            
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return pixmap
        except Exception:
            return self._create_placeholder_icon("?")
    
    def _create_placeholder_icon(self, letter: str) -> QPixmap:
        """Crea icona segnaposto con lettera"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor("#00ff88"))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("#000000"))
        
        # Fix: Ottieni font, modifica e imposta
        font = painter.font()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, letter)
        painter.end()
        
        return pixmap
