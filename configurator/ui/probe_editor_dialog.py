"""
Editor Grafico Puntali
Permette di disegnare la forma dei puntali e indicare punti di appoggio
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QWidget, QToolBar, QSpinBox, QComboBox,
    QColorDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QPolygonF
from typing import List, Optional
import json
from pathlib import Path


class ProbeShape:
    """Rappresenta una forma di puntale disegnata"""
    
    def __init__(self):
        self.lines: List[tuple] = []  # Lista di (p1, p2)
        self.arrows: List[dict] = []  # Lista di {pos, direction, label}
        self.contact_points: List[dict] = []  # {pos, type: 'interno'/'esterno'}
        self.name = "Nuovo Puntale"
        self.notes = ""
    
    def add_line(self, p1: QPointF, p2: QPointF):
        """Aggiunge linea"""
        self.lines.append((p1, p2))
    
    def add_arrow(self, pos: QPointF, direction: str, label: str = ""):
        """Aggiunge freccia indicatore"""
        self.arrows.append({"pos": pos, "direction": direction, "label": label})
    
    def add_contact_point(self, pos: QPointF, contact_type: str):
        """Aggiunge punto di contatto (interno/esterno)"""
        self.contact_points.append({"pos": pos, "type": contact_type})
    
    def to_dict(self) -> dict:
        """Serializza in dizionario"""
        return {
            "name": self.name,
            "notes": self.notes,
            "lines": [{"x1": l[0].x(), "y1": l[0].y(), "x2": l[1].x(), "y2": l[1].y()} 
                     for l in self.lines],
            "arrows": [{"x": a["pos"].x(), "y": a["pos"].y(), 
                       "direction": a["direction"], "label": a.get("label", "")} 
                      for a in self.arrows],
            "contact_points": [{"x": cp["pos"].x(), "y": cp["pos"].y(), "type": cp["type"]} 
                              for cp in self.contact_points]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProbeShape':
        """Deserializza da dizionario"""
        shape = cls()
        shape.name = data.get("name", "Puntale")
        shape.notes = data.get("notes", "")
        
        for line in data.get("lines", []):
            p1 = QPointF(line["x1"], line["y1"])
            p2 = QPointF(line["x2"], line["y2"])
            shape.lines.append((p1, p2))
        
        for arrow in data.get("arrows", []):
            pos = QPointF(arrow["x"], arrow["y"])
            shape.arrows.append({
                "pos": pos,
                "direction": arrow["direction"],
                "label": arrow.get("label", "")
            })
        
        for cp in data.get("contact_points", []):
            pos = QPointF(cp["x"], cp["y"])
            shape.contact_points.append({"pos": pos, "type": cp["type"]})
        
        return shape


class ProbeCanvas(QWidget):
    """Canvas per disegno puntale"""
    
    shape_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background: white; border: 2px solid #00ff88;")
        
        # Stato disegno
        self.shape = ProbeShape()
        self.current_tool = "line"  # line, arrow, contact_interno, contact_esterno
        self.drawing = False
        self.start_point: Optional[QPointF] = None
        self.current_point: Optional[QPointF] = None
        
        # Stile
        self.line_color = QColor("#000000")
        self.line_width = 2
        self.grid_size = 20
        self.show_grid = True
        
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """Disegna canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Griglia
        if self.show_grid:
            self._draw_grid(painter)
        
        # Assi centrali
        self._draw_axes(painter)
        
        # Disegna shape salvata
        self._draw_shape(painter)
        
        # Disegna linea in corso
        if self.drawing and self.start_point and self.current_point:
            painter.setPen(QPen(self.line_color, self.line_width, Qt.PenStyle.DashLine))
            painter.drawLine(self.start_point, self.current_point)
    
    def _draw_grid(self, painter: QPainter):
        """Disegna griglia"""
        painter.setPen(QPen(QColor("#e0e0e0"), 1))
        
        width = self.width()
        height = self.height()
        
        # Linee verticali
        x = 0
        while x < width:
            painter.drawLine(x, 0, x, height)
            x += self.grid_size
        
        # Linee orizzontali
        y = 0
        while y < height:
            painter.drawLine(0, y, width, y)
            y += self.grid_size
    
    def _draw_axes(self, painter: QPainter):
        """Disegna assi centrali"""
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        painter.setPen(QPen(QColor("#0088ff"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(center_x, 0, center_x, self.height())
        painter.drawLine(0, center_y, self.width(), center_y)
        
        # Etichette assi
        painter.setPen(QColor("#0088ff"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(int(center_x + 5), 15, "Y")
        painter.drawText(int(self.width() - 15), int(center_y - 5), "X")
    
    def _draw_shape(self, painter: QPainter):
        """Disegna shape puntale"""
        # Linee
        painter.setPen(QPen(self.line_color, self.line_width))
        for p1, p2 in self.shape.lines:
            painter.drawLine(p1, p2)
            # Punti terminali
            painter.setBrush(QColor("#ff8800"))
            painter.drawEllipse(p1, 3, 3)
            painter.drawEllipse(p2, 3, 3)
        
        # Frecce
        for arrow in self.shape.arrows:
            self._draw_arrow(painter, arrow)
        
        # Punti di contatto
        for cp in self.shape.contact_points:
            self._draw_contact_point(painter, cp)
    
    def _draw_arrow(self, painter: QPainter, arrow: dict):
        """Disegna freccia indicatore"""
        pos = arrow["pos"]
        direction = arrow["direction"]
        label = arrow.get("label", "")
        
        # Colore freccia
        painter.setPen(QPen(QColor("#ff0000"), 2))
        painter.setBrush(QColor("#ff0000"))
        
        # Lunghezza freccia
        arrow_length = 40
        
        # Calcola endpoint basato su direzione
        if direction == "up":
            end = QPointF(pos.x(), pos.y() - arrow_length)
        elif direction == "down":
            end = QPointF(pos.x(), pos.y() + arrow_length)
        elif direction == "left":
            end = QPointF(pos.x() - arrow_length, pos.y())
        elif direction == "right":
            end = QPointF(pos.x() + arrow_length, pos.y())
        else:
            end = pos
        
        # Disegna linea freccia
        painter.drawLine(pos, end)
        
        # Punta freccia
        arrow_head = QPolygonF()
        if direction == "up":
            arrow_head << QPointF(end.x(), end.y())
            arrow_head << QPointF(end.x() - 5, end.y() + 10)
            arrow_head << QPointF(end.x() + 5, end.y() + 10)
        elif direction == "down":
            arrow_head << QPointF(end.x(), end.y())
            arrow_head << QPointF(end.x() - 5, end.y() - 10)
            arrow_head << QPointF(end.x() + 5, end.y() - 10)
        elif direction == "left":
            arrow_head << QPointF(end.x(), end.y())
            arrow_head << QPointF(end.x() + 10, end.y() - 5)
            arrow_head << QPointF(end.x() + 10, end.y() + 5)
        elif direction == "right":
            arrow_head << QPointF(end.x(), end.y())
            arrow_head << QPointF(end.x() - 10, end.y() - 5)
            arrow_head << QPointF(end.x() - 10, end.y() + 5)
        
        painter.drawPolygon(arrow_head)
        
        # Etichetta
        if label:
            painter.setPen(QColor("#ff0000"))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(int(end.x() + 10), int(end.y() - 10), label)
    
    def _draw_contact_point(self, painter: QPainter, cp: dict):
        """Disegna punto di contatto"""
        pos = cp["pos"]
        contact_type = cp["type"]
        
        if contact_type == "interno":
            color = QColor("#00ff00")
            label = "INT"
        else:  # esterno
            color = QColor("#ff00ff")
            label = "EST"
        
        # Cerchio grande
        painter.setBrush(color)
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawEllipse(pos, 12, 12)
        
        # Etichetta
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(int(pos.x() - 10), int(pos.y() + 4), label)
        
        # Descrizione sotto
        painter.setPen(color)
        painter.setFont(QFont("Arial", 9))
        text = "Appoggio Interno" if contact_type == "interno" else "Appoggio Esterno"
        painter.drawText(int(pos.x() - 40), int(pos.y() + 25), text)
    
    def mousePressEvent(self, event):
        """Inizia disegno"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            if self.current_tool == "line":
                self.drawing = True
                self.start_point = QPointF(pos)
                self.current_point = QPointF(pos)
            elif self.current_tool in ["arrow_up", "arrow_down", "arrow_left", "arrow_right"]:
                direction = self.current_tool.replace("arrow_", "")
                self.shape.add_arrow(QPointF(pos), direction)
                self.shape_changed.emit()
                self.update()
            elif self.current_tool in ["contact_interno", "contact_esterno"]:
                contact_type = self.current_tool.replace("contact_", "")
                self.shape.add_contact_point(QPointF(pos), contact_type)
                self.shape_changed.emit()
                self.update()
    
    def mouseMoveEvent(self, event):
        """Aggiorna disegno in corso"""
        if self.drawing:
            pos = event.position().toPoint()
            self.current_point = QPointF(pos)
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Completa disegno"""
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            pos = event.position().toPoint()
            self.current_point = QPointF(pos)
            
            # Costante per lunghezza minima linea
            MIN_LINE_LENGTH = 5
            
            if self.start_point and self.current_point:
                # Aggiungi linea solo se non è troppo corta
                if (self.start_point - self.current_point).manhattanLength() > MIN_LINE_LENGTH:
                    self.shape.add_line(self.start_point, self.current_point)
                    self.shape_changed.emit()
            
            self.drawing = False
            self.start_point = None
            self.current_point = None
            self.update()
    
    def clear(self):
        """Pulisce canvas"""
        self.shape = ProbeShape()
        self.shape_changed.emit()
        self.update()
    
    def undo_last(self):
        """Annulla ultima operazione"""
        if self.shape.lines:
            self.shape.lines.pop()
            self.shape_changed.emit()
            self.update()
        elif self.shape.arrows:
            self.shape.arrows.pop()
            self.shape_changed.emit()
            self.update()
        elif self.shape.contact_points:
            self.shape.contact_points.pop()
            self.shape_changed.emit()
            self.update()


class ProbeEditorDialog(QDialog):
    """Dialog editor grafico puntali"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("✏️ Editor Grafico Puntali")
        self.resize(800, 700)
        
        self._init_ui()
    
    def _init_ui(self):
        """Inizializza interfaccia"""
        layout = QVBoxLayout(self)
        
        # Titolo
        title = QLabel("✏️ Editor Grafico Forma Puntale")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
            padding: 10px;
            background: #0f3460;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # IMPORTANTE: Creare canvas PRIMA della toolbar
        self.canvas = ProbeCanvas()
        self.canvas.shape_changed.connect(self._on_shape_changed)
        
        # Toolbar (ora self.canvas esiste)
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # Aggiungere canvas al layout
        layout.addWidget(self.canvas)
        
        # Info
        self.info_label = QLabel("Strumento: Linea | Clicca e trascina per disegnare")
        self.info_label.setStyleSheet("background: #1a1a2e; color: #ffffff; padding: 5px;")
        layout.addWidget(self.info_label)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Salva Puntale")
        save_btn.clicked.connect(self._save_probe)
        buttons_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📂 Carica Puntale")
        load_btn.clicked.connect(self._load_probe)
        buttons_layout.addWidget(load_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _create_toolbar(self) -> QWidget:
        """Crea toolbar strumenti"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Strumenti disegno
        tools_label = QLabel("Strumento:")
        toolbar_layout.addWidget(tools_label)
        
        line_btn = QPushButton("📏 Linea")
        line_btn.clicked.connect(lambda: self._set_tool("line", "Linea | Clicca e trascina"))
        toolbar_layout.addWidget(line_btn)
        
        arrow_up_btn = QPushButton("⬆️ Freccia Su")
        arrow_up_btn.clicked.connect(lambda: self._set_tool("arrow_up", "Freccia Su | Clicca per posizionare"))
        toolbar_layout.addWidget(arrow_up_btn)
        
        arrow_down_btn = QPushButton("⬇️ Freccia Giù")
        arrow_down_btn.clicked.connect(lambda: self._set_tool("arrow_down", "Freccia Giù | Clicca per posizionare"))
        toolbar_layout.addWidget(arrow_down_btn)
        
        contact_int_btn = QPushButton("🟢 Appoggio Interno")
        contact_int_btn.clicked.connect(lambda: self._set_tool("contact_interno", "Appoggio Interno | Clicca per posizionare"))
        toolbar_layout.addWidget(contact_int_btn)
        
        contact_ext_btn = QPushButton("🟣 Appoggio Esterno")
        contact_ext_btn.clicked.connect(lambda: self._set_tool("contact_esterno", "Appoggio Esterno | Clicca per posizionare"))
        toolbar_layout.addWidget(contact_ext_btn)
        
        toolbar_layout.addStretch()
        
        # Azioni
        undo_btn = QPushButton("↶ Annulla")
        undo_btn.clicked.connect(self.canvas.undo_last)
        toolbar_layout.addWidget(undo_btn)
        
        clear_btn = QPushButton("🗑️ Pulisci")
        clear_btn.clicked.connect(self._clear_canvas)
        toolbar_layout.addWidget(clear_btn)
        
        return toolbar_widget
    
    def _set_tool(self, tool: str, description: str):
        """Imposta strumento corrente"""
        self.canvas.current_tool = tool
        self.info_label.setText(f"Strumento: {description}")
    
    def _on_shape_changed(self):
        """Gestisce cambio shape"""
        lines = len(self.canvas.shape.lines)
        arrows = len(self.canvas.shape.arrows)
        contacts = len(self.canvas.shape.contact_points)
        status = f"Elementi: {lines} linee, {arrows} frecce, {contacts} punti di contatto"
        
        # Aggiorna solo la parte finale del testo
        current = self.info_label.text()
        if "|" in current:
            tool_part = current.split("|")[1]
            self.info_label.setText(f"{status} | {tool_part}")
        else:
            self.info_label.setText(status)
    
    def _clear_canvas(self):
        """Pulisce canvas"""
        self.canvas.clear()
        self.info_label.setText("Strumento: Linea | Canvas pulito - inizia a disegnare")
    
    def _save_probe(self):
        """Salva puntale su file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Salva Puntale", "",
            "File Puntale (*.probe.json)"
        )
        
        if filename:
            if not filename.endswith('.probe.json'):
                filename += '.probe.json'
            
            try:
                data = self.canvas.shape.to_dict()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                self.info_label.setText(f"✅ Puntale salvato: {Path(filename).name}")
            except Exception as e:
                self.info_label.setText(f"❌ Errore salvataggio: {e}")
    
    def _load_probe(self):
        """Carica puntale da file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Carica Puntale", "",
            "File Puntale (*.probe.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.canvas.shape = ProbeShape.from_dict(data)
                self.canvas.update()
                self.canvas.shape_changed.emit()
                
                self.info_label.setText(f"✅ Puntale caricato: {Path(filename).name}")
            except Exception as e:
                self.info_label.setText(f"❌ Errore caricamento: {e}")
