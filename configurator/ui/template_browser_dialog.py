"""
Dialog browser template con anteprime visive
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QListWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
import json
from pathlib import Path
from typing import Optional, Dict, Any


class TemplateInfo:
    """Informazioni su un template"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.data = None
        self.load()
    
    def load(self):
        """Carica dati template da JSON"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Errore caricamento template {self.filepath} ({type(e).__name__}): {e}")
            self.data = {
                "name": self.filepath.stem,
                "description": "Template non valido",
                "elements": []
            }
    
    @property
    def name(self) -> str:
        return self.data.get("name", self.filepath.stem)
    
    @property
    def description(self) -> str:
        return self.data.get("description", "")
    
    @property
    def version(self) -> str:
        return self.data.get("version", "1.0.0")
    
    @property
    def element_count(self) -> int:
        return len(self.data.get("elements", []))


class TemplateBrowserDialog(QDialog):
    """Dialog per selezionare template preimpostati"""
    
    def __init__(self, parent=None, templates_dir: Optional[Path] = None):
        super().__init__(parent)
        
        if templates_dir is None:
            # Default: resources/templates relativo a questo file
            base_dir = Path(__file__).parent.parent
            templates_dir = base_dir / "resources" / "templates"
        
        self.templates_dir = templates_dir
        self.selected_template = None
        self.templates = []
        
        self.setWindowTitle("Browser Template")
        self.resize(800, 600)
        
        self._init_ui()
        self._load_templates()
    
    def _init_ui(self):
        """Inizializza interfaccia"""
        layout = QHBoxLayout(self)
        
        # Pannello sinistro: lista template
        left_panel = QVBoxLayout()
        
        title = QLabel("📋 Template Disponibili")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff88; padding: 8px;")
        left_panel.addWidget(title)
        
        self.template_list = QListWidget()
        self.template_list.setIconSize(QSize(120, 90))
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        left_panel.addWidget(self.template_list)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        load_btn = QPushButton("Carica Template")
        load_btn.setProperty("primary", True)
        load_btn.clicked.connect(self._on_load_template)
        buttons_layout.addWidget(load_btn)
        
        left_panel.addLayout(buttons_layout)
        
        # Pannello destro: anteprima e dettagli
        right_panel = QVBoxLayout()
        
        preview_label = QLabel("🔍 Anteprima")
        preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff88; padding: 8px;")
        right_panel.addWidget(preview_label)
        
        # Area preview grafica
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(400, 240)
        self.preview_label.setMaximumSize(400, 240)
        self.preview_label.setStyleSheet("border: 2px solid #00ff88; background: #16213e;")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setText("Seleziona un template per visualizzare l'anteprima")
        right_panel.addWidget(self.preview_label)
        
        # Dettagli template
        details_label = QLabel("ℹ️ Dettagli")
        details_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff88; padding: 8px;")
        right_panel.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        right_panel.addWidget(self.details_text)
        
        right_panel.addStretch()
        
        # Aggiungi pannelli al layout principale
        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 1)
    
    def _load_templates(self):
        """Carica template dalla directory"""
        if not self.templates_dir.exists():
            return
        
        # Trova tutti i file JSON nella directory
        for filepath in self.templates_dir.glob("*.json"):
            template_info = TemplateInfo(filepath)
            self.templates.append(template_info)
            
            # Crea item nella lista
            item = QListWidgetItem(template_info.name)
            item.setData(Qt.ItemDataRole.UserRole, template_info)
            
            # Genera anteprima miniatura
            thumbnail = self._generate_thumbnail(template_info)
            item.setIcon(thumbnail)
            
            self.template_list.addItem(item)
    
    def _generate_thumbnail(self, template_info: TemplateInfo) -> QPixmap:
        """Genera miniatura preview del template"""
        width, height = 120, 90
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#16213e"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Bordo
        painter.setPen(QColor("#00ff88"))
        painter.drawRect(0, 0, width - 1, height - 1)
        
        # Simula elementi del template come rettangoli
        elements = template_info.data.get("elements", [])
        scale_x = width / 800.0
        scale_y = height / 480.0
        
        for i, elem in enumerate(elements[:20]):  # Max 20 elementi per performance
            x = int(elem.get("x", 0) * scale_x)
            y = int(elem.get("y", 0) * scale_y)
            w = int(elem.get("width", 50) * scale_x)
            h = int(elem.get("height", 30) * scale_y)
            
            # Colore basato sul tipo
            elem_type = elem.get("type", "")
            if "Button" in elem_type:
                color = QColor("#00ff88")
            elif "Display" in elem_type or "Measure" in elem_type:
                color = QColor("#0088ff")
            elif "Panel" in elem_type or "Frame" in elem_type:
                color = QColor("#333333")
            else:
                color = QColor("#888888")
            
            painter.setBrush(color)
            painter.setPen(QColor("#222222"))
            painter.drawRect(x, y, w, h)
        
        # Numero elementi in basso
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.drawText(5, height - 5, f"{len(elements)} elementi")
        
        painter.end()
        return pixmap
    
    def _on_template_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Gestisce selezione template"""
        if not current:
            return
        
        template_info = current.data(Qt.ItemDataRole.UserRole)
        
        # Aggiorna preview grande
        preview_pixmap = self._generate_large_preview(template_info)
        self.preview_label.setPixmap(preview_pixmap)
        
        # Aggiorna dettagli
        details_html = f"""
        <h3 style="color: #00ff88;">{template_info.name}</h3>
        <p><b>Versione:</b> {template_info.version}</p>
        <p><b>Elementi:</b> {template_info.element_count}</p>
        <p><b>Descrizione:</b></p>
        <p>{template_info.description}</p>
        """
        self.details_text.setHtml(details_html)
    
    def _generate_large_preview(self, template_info: TemplateInfo) -> QPixmap:
        """Genera preview grande del template"""
        width, height = 400, 240
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#16213e"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Bordo display
        painter.setPen(QColor("#00ff88"))
        painter.drawRect(0, 0, width - 1, height - 1)
        
        # Render elementi con più dettagli
        elements = template_info.data.get("elements", [])
        scale_x = width / 800.0
        scale_y = height / 480.0
        
        for elem in elements:
            x = int(elem.get("x", 0) * scale_x)
            y = int(elem.get("y", 0) * scale_y)
            w = int(elem.get("width", 50) * scale_x)
            h = int(elem.get("height", 30) * scale_y)
            
            # Colore e stile basati sul tipo
            elem_type = elem.get("type", "")
            props = elem.get("properties", {})
            
            if "Button" in elem_type:
                painter.setBrush(QColor("#00ff88"))
                painter.setPen(QColor("#000000"))
                painter.drawRoundedRect(x, y, w, h, 3, 3)
                # Testo
                text = props.get("text", elem_type)
                painter.setPen(QColor("#000000"))
                painter.setFont(QFont("Arial", 6))
                painter.drawText(x, y, w, h, Qt.AlignmentFlag.AlignCenter, text[:15])
            elif "Display" in elem_type or "Measure" in elem_type:
                painter.setBrush(QColor("#0088ff"))
                painter.setPen(QColor("#333333"))
                painter.drawRect(x, y, w, h)
                # Mostra valore simulato
                painter.setPen(QColor("#ffffff"))
                painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
                painter.drawText(x, y, w, h, Qt.AlignmentFlag.AlignCenter, "1234.56")
            elif "Label" in elem_type:
                painter.setPen(QColor("#ffffff"))
                painter.setFont(QFont("Arial", 6))
                text = props.get("text", "Label")
                painter.drawText(x, y, w, h, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text[:20])
            elif "Panel" in elem_type or "Frame" in elem_type:
                painter.setBrush(QColor("#1a1a2e"))
                painter.setPen(QColor("#00ff88"))
                painter.drawRect(x, y, w, h)
            else:
                painter.setBrush(QColor("#333333"))
                painter.setPen(QColor("#666666"))
                painter.drawRect(x, y, w, h)
        
        painter.end()
        return pixmap
    
    def _on_load_template(self):
        """Carica template selezionato"""
        current = self.template_list.currentItem()
        if current:
            self.selected_template = current.data(Qt.ItemDataRole.UserRole)
            self.accept()
    
    def get_selected_template(self) -> Optional[TemplateInfo]:
        """Ottiene template selezionato"""
        return self.selected_template
