"""
Editor Grafico Puntali Avanzato con Snap e Vincoli Ortogonali
Permette di disegnare la forma dei puntali con sistema snap professionale
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QWidget, QSpinBox, QCheckBox, QFileDialog
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from typing import List, Optional, Tuple
from enum import Enum
import json
import math
from pathlib import Path


class SnapType(Enum):
    """Tipi di snap disponibili"""
    NONE = 0
    GRID = 1
    ENDPOINT = 2
    MIDPOINT = 3
    PERPENDICULAR = 4
    INTERSECTION = 5


class SnapManager:
    """Gestisce il sistema di snap per il disegno CAD"""
    
    def __init__(self):
        self.enabled_snaps = {
            SnapType.GRID: True,
            SnapType.ENDPOINT: True,
            SnapType.MIDPOINT: True,
            SnapType.PERPENDICULAR: False,
            SnapType.INTERSECTION: False,
        }
        self.snap_radius = 15  # pixel
    
    def set_snap_enabled(self, snap_type: SnapType, enabled: bool):
        """Abilita/disabilita un tipo di snap"""
        self.enabled_snaps[snap_type] = enabled
    
    def find_snap(self, pos: QPointF, lines: List, grid_size: int) -> Tuple[Optional[QPointF], SnapType]:
        """
        Trova il punto snap più vicino
        
        Args:
            pos: Posizione corrente del mouse
            lines: Lista di linee esistenti [(p1, p2), ...]
            grid_size: Dimensione griglia
            
        Returns:
            Tupla (punto_snap, tipo_snap) o (None, SnapType.NONE)
        """
        best_snap = None
        best_type = SnapType.NONE
        best_dist = self.snap_radius
        
        # Snap Grid
        if self.enabled_snaps[SnapType.GRID]:
            grid_x = round(pos.x() / grid_size) * grid_size
            grid_y = round(pos.y() / grid_size) * grid_size
            dist = math.sqrt((grid_x - pos.x())**2 + (grid_y - pos.y())**2)
            if dist < best_dist:
                best_snap = QPointF(grid_x, grid_y)
                best_type = SnapType.GRID
                best_dist = dist
        
        # Snap Endpoint
        if self.enabled_snaps[SnapType.ENDPOINT]:
            for p1, p2 in lines:
                for point in [p1, p2]:
                    dist = math.sqrt((point.x() - pos.x())**2 + (point.y() - pos.y())**2)
                    if dist < best_dist:
                        best_snap = point
                        best_type = SnapType.ENDPOINT
                        best_dist = dist
        
        # Snap Midpoint
        if self.enabled_snaps[SnapType.MIDPOINT]:
            for p1, p2 in lines:
                mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
                dist = math.sqrt((mid.x() - pos.x())**2 + (mid.y() - pos.y())**2)
                if dist < best_dist:
                    best_snap = mid
                    best_type = SnapType.MIDPOINT
                    best_dist = dist
        
        return best_snap, best_type


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
    """Canvas per disegno puntale con snap avanzato"""
    
    shape_changed = pyqtSignal()
    mouse_moved = pyqtSignal(QPointF, SnapType)  # Posizione e tipo snap
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(600, 400)
        # Sfondo chiaro stile CAD
        self.setStyleSheet("background: #f5f5f5; border: 2px solid #00ff88;")
        
        # Stato disegno
        self.shape = ProbeShape()
        self.current_tool = "line"  # line, arrow_*, contact_*
        self.drawing = False
        self.start_point: Optional[QPointF] = None
        self.current_point: Optional[QPointF] = None
        self.snapped_point: Optional[QPointF] = None
        self.current_snap_type: SnapType = SnapType.NONE
        
        # Stile CAD
        self.line_color = QColor("#1a1a1a")  # Linee scure
        self.line_width = 2
        self.grid_size = 20
        self.show_grid = True
        
        # Snap e vincoli
        self.snap_manager = SnapManager()
        self.ortho_mode = False  # Vincolo ortogonale
        self.angle_45_mode = False  # Vincolo 45°
        
        # Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        
        self.setMouseTracking(True)
    
    def set_snap(self, snap_type: SnapType, enabled: bool):
        """Abilita/disabilita un tipo di snap"""
        self.snap_manager.set_snap_enabled(snap_type, enabled)
        self.update()
    
    def set_grid_size(self, size: int):
        """Imposta dimensione griglia"""
        self.grid_size = size
        self.update()
    
    def apply_constraints(self, start: QPointF, current: QPointF) -> QPointF:
        """
        Applica vincoli di disegno (ortogonale o 45°)
        
        Args:
            start: Punto iniziale
            current: Punto corrente
            
        Returns:
            Punto con vincoli applicati
        """
        if not start:
            return current
        
        dx = current.x() - start.x()
        dy = current.y() - start.y()
        
        if self.ortho_mode:
            # Forza 0°, 90°, 180°, 270°
            if abs(dx) > abs(dy):
                return QPointF(current.x(), start.y())
            else:
                return QPointF(start.x(), current.y())
        
        if self.angle_45_mode:
            # Forza multipli di 45°
            angle = math.atan2(dy, dx)
            snap_angle = round(angle / (math.pi / 4)) * (math.pi / 4)
            length = math.sqrt(dx*dx + dy*dy)
            return QPointF(
                start.x() + length * math.cos(snap_angle),
                start.y() + length * math.sin(snap_angle)
            )
        
        return current
    
    def paintEvent(self, event):
        """Disegna canvas con snap indicators"""
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
            # Applica vincoli
            constrained_point = self.apply_constraints(self.start_point, self.current_point)
            
            painter.setPen(QPen(self.line_color, self.line_width, Qt.PenStyle.DashLine))
            painter.drawLine(self.start_point, constrained_point)
            
            # Mostra distanza e angolo
            self._draw_dimension_info(painter, self.start_point, constrained_point)
        
        # Indicatore snap
        if self.snapped_point and self.current_snap_type != SnapType.NONE:
            self._draw_snap_indicator(painter, self.snapped_point, self.current_snap_type)
    
    def _draw_grid(self, painter: QPainter):
        """Disegna griglia stile CAD"""
        painter.setPen(QPen(QColor("#d0d0d0"), 1, Qt.PenStyle.DotLine))
        
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
    
    def _draw_snap_indicator(self, painter: QPainter, pos: QPointF, snap_type: SnapType):
        """Disegna indicatore snap visivo"""
        size = 8
        
        if snap_type == SnapType.GRID:
            # Croce arancione
            painter.setPen(QPen(QColor("#ff8800"), 2))
            painter.drawLine(int(pos.x() - size), int(pos.y()), 
                           int(pos.x() + size), int(pos.y()))
            painter.drawLine(int(pos.x()), int(pos.y() - size), 
                           int(pos.x()), int(pos.y() + size))
        
        elif snap_type == SnapType.ENDPOINT:
            # Quadrato rosso
            painter.setPen(QPen(QColor("#ff0000"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(int(pos.x() - size), int(pos.y() - size), size*2, size*2)
        
        elif snap_type == SnapType.MIDPOINT:
            # Triangolo verde
            painter.setPen(QPen(QColor("#00ff00"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            points = [
                QPointF(pos.x(), pos.y() - size),
                QPointF(pos.x() - size, pos.y() + size),
                QPointF(pos.x() + size, pos.y() + size)
            ]
            painter.drawPolygon(QPolygonF(points))
        
        elif snap_type == SnapType.PERPENDICULAR:
            # Simbolo perpendicolare blu
            painter.setPen(QPen(QColor("#0088ff"), 2))
            painter.drawLine(int(pos.x() - size), int(pos.y()), 
                           int(pos.x() + size), int(pos.y()))
            painter.drawLine(int(pos.x()), int(pos.y() - size), 
                           int(pos.x()), int(pos.y() + size//2))
    
    def _draw_dimension_info(self, painter: QPainter, start: QPointF, end: QPointF):
        """Disegna info dimensionali (distanza e angolo)"""
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.degrees(math.atan2(-dy, dx))  # -dy perché Y cresce verso il basso
        
        # Posizione testo
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2
        
        painter.setPen(QColor("#0088ff"))
        painter.setFont(QFont("Arial", 9))
        
        info_text = f"{distance:.1f}px @ {angle:.1f}°"
        painter.drawText(int(mid_x + 10), int(mid_y - 10), info_text)
    
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
        """Inizia disegno con snap"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = QPointF(event.position())
            
            # Trova snap
            snap_point, snap_type = self.snap_manager.find_snap(
                pos, self.shape.lines, self.grid_size
            )
            
            if snap_point:
                pos = snap_point
            
            if self.current_tool == "line":
                self.drawing = True
                self.start_point = pos
                self.current_point = pos
                # Salva stato per undo
                self._save_undo_state()
            elif self.current_tool in ["arrow_up", "arrow_down", "arrow_left", "arrow_right"]:
                direction = self.current_tool.replace("arrow_", "")
                self.shape.add_arrow(pos, direction)
                self._save_undo_state()
                self.shape_changed.emit()
                self.update()
            elif self.current_tool in ["contact_interno", "contact_esterno"]:
                contact_type = self.current_tool.replace("contact_", "")
                self.shape.add_contact_point(pos, contact_type)
                self._save_undo_state()
                self.shape_changed.emit()
                self.update()
    
    def mouseMoveEvent(self, event):
        """Aggiorna disegno in corso con snap"""
        pos = QPointF(event.position())
        
        # Trova snap
        snap_point, snap_type = self.snap_manager.find_snap(
            pos, self.shape.lines, self.grid_size
        )
        
        if snap_point:
            self.snapped_point = snap_point
            self.current_snap_type = snap_type
        else:
            self.snapped_point = None
            self.current_snap_type = SnapType.NONE
        
        # Emetti segnale per aggiornare status bar
        display_pos = snap_point if snap_point else pos
        self.mouse_moved.emit(display_pos, snap_type)
        
        if self.drawing:
            self.current_point = snap_point if snap_point else pos
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Completa disegno con snap"""
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            pos = QPointF(event.position())
            
            # Trova snap
            snap_point, _ = self.snap_manager.find_snap(
                pos, self.shape.lines, self.grid_size
            )
            
            if snap_point:
                pos = snap_point
            
            # Applica vincoli
            self.current_point = self.apply_constraints(self.start_point, pos)
            
            # Costante per lunghezza minima linea
            MIN_LINE_LENGTH = 5
            
            if self.start_point and self.current_point:
                dx = self.current_point.x() - self.start_point.x()
                dy = self.current_point.y() - self.start_point.y()
                length = math.sqrt(dx*dx + dy*dy)
                
                # Aggiungi linea solo se non è troppo corta
                if length > MIN_LINE_LENGTH:
                    self.shape.add_line(self.start_point, self.current_point)
                    self.shape_changed.emit()
            
            self.drawing = False
            self.start_point = None
            self.current_point = None
            self.snapped_point = None
            self.current_snap_type = SnapType.NONE
            self.update()
    
    def keyPressEvent(self, event):
        """Gestisce tasti per vincoli temporanei"""
        if event.key() == Qt.Key.Key_Shift:
            self.ortho_mode = True
            self.update()
        elif event.key() == Qt.Key.Key_Control:
            self.angle_45_mode = True
            self.update()
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Rilascia vincoli temporanei"""
        if event.key() == Qt.Key.Key_Shift:
            self.ortho_mode = False
            self.update()
        elif event.key() == Qt.Key.Key_Control:
            self.angle_45_mode = False
            self.update()
        super().keyReleaseEvent(event)
    
    def clear(self):
        """Pulisce canvas"""
        self._save_undo_state()
        self.shape = ProbeShape()
        self.shape_changed.emit()
        self.update()
    
    def _save_undo_state(self):
        """Salva stato corrente per undo"""
        # Serializza lo stato corrente
        state = {
            'lines': [(p1.x(), p1.y(), p2.x(), p2.y()) for p1, p2 in self.shape.lines],
            'arrows': [{'x': a['pos'].x(), 'y': a['pos'].y(), 
                       'direction': a['direction'], 'label': a.get('label', '')} 
                      for a in self.shape.arrows],
            'contact_points': [{'x': cp['pos'].x(), 'y': cp['pos'].y(), 'type': cp['type']} 
                              for cp in self.shape.contact_points]
        }
        self.undo_stack.append(state)
        # Pulisci redo stack quando aggiungiamo nuove azioni
        self.redo_stack.clear()
        # Limita dimensione stack
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
    
    def _restore_state(self, state):
        """Ripristina stato da dizionario"""
        self.shape = ProbeShape()
        
        for line_data in state['lines']:
            p1 = QPointF(line_data[0], line_data[1])
            p2 = QPointF(line_data[2], line_data[3])
            self.shape.lines.append((p1, p2))
        
        for arrow_data in state['arrows']:
            pos = QPointF(arrow_data['x'], arrow_data['y'])
            self.shape.arrows.append({
                'pos': pos,
                'direction': arrow_data['direction'],
                'label': arrow_data.get('label', '')
            })
        
        for cp_data in state['contact_points']:
            pos = QPointF(cp_data['x'], cp_data['y'])
            self.shape.contact_points.append({'pos': pos, 'type': cp_data['type']})
    
    def undo_last(self):
        """Annulla ultima operazione"""
        if len(self.undo_stack) > 0:
            # Salva stato corrente in redo
            current_state = {
                'lines': [(p1.x(), p1.y(), p2.x(), p2.y()) for p1, p2 in self.shape.lines],
                'arrows': [{'x': a['pos'].x(), 'y': a['pos'].y(), 
                           'direction': a['direction'], 'label': a.get('label', '')} 
                          for a in self.shape.arrows],
                'contact_points': [{'x': cp['pos'].x(), 'y': cp['pos'].y(), 'type': cp['type']} 
                                  for cp in self.shape.contact_points]
            }
            self.redo_stack.append(current_state)
            
            # Ripristina stato precedente
            previous_state = self.undo_stack.pop()
            self._restore_state(previous_state)
            
            self.shape_changed.emit()
            self.update()
    
    def redo_last(self):
        """Ripristina operazione annullata"""
        if len(self.redo_stack) > 0:
            # Salva stato corrente in undo
            current_state = {
                'lines': [(p1.x(), p1.y(), p2.x(), p2.y()) for p1, p2 in self.shape.lines],
                'arrows': [{'x': a['pos'].x(), 'y': a['pos'].y(), 
                           'direction': a['direction'], 'label': a.get('label', '')} 
                          for a in self.shape.arrows],
                'contact_points': [{'x': cp['pos'].x(), 'y': cp['pos'].y(), 'type': cp['type']} 
                                  for cp in self.shape.contact_points]
            }
            self.undo_stack.append(current_state)
            
            # Ripristina stato redo
            redo_state = self.redo_stack.pop()
            self._restore_state(redo_state)
            
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
        """Inizializza interfaccia avanzata"""
        layout = QVBoxLayout(self)
        
        # Titolo
        title = QLabel("✏️ Editor Grafico Puntale Avanzato con Snap")
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
        self.canvas.mouse_moved.connect(self._update_status)
        
        # Toolbar avanzata (ora self.canvas esiste)
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # Aggiungere canvas al layout
        layout.addWidget(self.canvas)
        
        # Status bar
        self.status_label = QLabel("Pronto | Seleziona uno strumento")
        self.status_label.setStyleSheet("""
            background: #1a1a2e; 
            color: #ffffff; 
            padding: 5px;
            font-family: 'Courier New', monospace;
        """)
        layout.addWidget(self.status_label)
        
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
        """Crea toolbar avanzata con snap e vincoli"""
        toolbar_widget = QWidget()
        main_layout = QVBoxLayout(toolbar_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Riga 1: Strumenti disegno
        draw_row = QHBoxLayout()
        draw_row.addWidget(QLabel("Disegno:"))
        
        line_btn = QPushButton("📏 Linea")
        line_btn.setCheckable(True)
        line_btn.setChecked(True)
        line_btn.clicked.connect(lambda: self._set_tool("line"))
        draw_row.addWidget(line_btn)
        
        # Frecce
        for direction, icon in [("up", "⬆️"), ("down", "⬇️"), ("left", "⬅️"), ("right", "➡️")]:
            btn = QPushButton(icon)
            btn.setFixedWidth(40)
            btn.clicked.connect(lambda _, d=direction: self._set_tool(f"arrow_{d}"))
            draw_row.addWidget(btn)
        
        draw_row.addSpacing(20)
        draw_row.addWidget(QLabel("Contatto:"))
        
        int_btn = QPushButton("🟢 INT")
        int_btn.clicked.connect(lambda: self._set_tool("contact_interno"))
        draw_row.addWidget(int_btn)
        
        ext_btn = QPushButton("🟣 EST")
        ext_btn.clicked.connect(lambda: self._set_tool("contact_esterno"))
        draw_row.addWidget(ext_btn)
        
        draw_row.addStretch()
        
        # Azioni
        undo_btn = QPushButton("↶")
        undo_btn.setToolTip("Annulla (Ctrl+Z)")
        undo_btn.clicked.connect(self.canvas.undo_last)
        draw_row.addWidget(undo_btn)
        
        redo_btn = QPushButton("↷")
        redo_btn.setToolTip("Ripeti (Ctrl+Y)")
        redo_btn.clicked.connect(self.canvas.redo_last)
        draw_row.addWidget(redo_btn)
        
        clear_btn = QPushButton("🗑️")
        clear_btn.setToolTip("Pulisci tutto")
        clear_btn.clicked.connect(self._clear_canvas)
        draw_row.addWidget(clear_btn)
        
        main_layout.addLayout(draw_row)
        
        # Riga 2: Snap e vincoli
        snap_row = QHBoxLayout()
        snap_row.addWidget(QLabel("Snap:"))
        
        self.snap_grid_cb = QCheckBox("Grid")
        self.snap_grid_cb.setChecked(True)
        self.snap_grid_cb.stateChanged.connect(
            lambda s: self.canvas.set_snap(SnapType.GRID, bool(s))
        )
        snap_row.addWidget(self.snap_grid_cb)
        
        self.snap_endpoint_cb = QCheckBox("Endpoint")
        self.snap_endpoint_cb.setChecked(True)
        self.snap_endpoint_cb.stateChanged.connect(
            lambda s: self.canvas.set_snap(SnapType.ENDPOINT, bool(s))
        )
        snap_row.addWidget(self.snap_endpoint_cb)
        
        self.snap_midpoint_cb = QCheckBox("Midpoint")
        self.snap_midpoint_cb.setChecked(True)
        self.snap_midpoint_cb.stateChanged.connect(
            lambda s: self.canvas.set_snap(SnapType.MIDPOINT, bool(s))
        )
        snap_row.addWidget(self.snap_midpoint_cb)
        
        self.snap_perp_cb = QCheckBox("Perp")
        self.snap_perp_cb.stateChanged.connect(
            lambda s: self.canvas.set_snap(SnapType.PERPENDICULAR, bool(s))
        )
        snap_row.addWidget(self.snap_perp_cb)
        
        snap_row.addSpacing(20)
        snap_row.addWidget(QLabel("Vincoli:"))
        
        self.ortho_cb = QCheckBox("Ortho (Shift)")
        self.ortho_cb.stateChanged.connect(
            lambda s: setattr(self.canvas, 'ortho_mode', bool(s))
        )
        snap_row.addWidget(self.ortho_cb)
        
        self.angle45_cb = QCheckBox("45° (Ctrl)")
        self.angle45_cb.stateChanged.connect(
            lambda s: setattr(self.canvas, 'angle_45_mode', bool(s))
        )
        snap_row.addWidget(self.angle45_cb)
        
        snap_row.addSpacing(20)
        snap_row.addWidget(QLabel("Griglia:"))
        
        self.grid_spin = QSpinBox()
        self.grid_spin.setRange(5, 50)
        self.grid_spin.setValue(20)
        self.grid_spin.setSuffix(" px")
        self.grid_spin.valueChanged.connect(self.canvas.set_grid_size)
        snap_row.addWidget(self.grid_spin)
        
        snap_row.addStretch()
        main_layout.addLayout(snap_row)
        
        return toolbar_widget
    
    def _set_tool(self, tool: str):
        """Imposta strumento corrente"""
        self.canvas.current_tool = tool
        
        tool_names = {
            "line": "Linea",
            "arrow_up": "Freccia Su",
            "arrow_down": "Freccia Giù",
            "arrow_left": "Freccia Sinistra",
            "arrow_right": "Freccia Destra",
            "contact_interno": "Appoggio Interno",
            "contact_esterno": "Appoggio Esterno"
        }
        
        tool_name = tool_names.get(tool, tool)
        self._update_status_tool(tool_name)
    
    def _update_status_tool(self, tool_name: str):
        """Aggiorna status bar con nome strumento"""
        current = self.status_label.text()
        if "|" in current:
            parts = current.split("|")
            if len(parts) >= 2:
                self.status_label.setText(f"{parts[0]} | Strumento: {tool_name}")
        else:
            self.status_label.setText(f"Pronto | Strumento: {tool_name}")
    
    def _update_status(self, pos: QPointF, snap_type: SnapType):
        """Aggiorna status bar con posizione e snap"""
        snap_names = {
            SnapType.NONE: "Nessuno",
            SnapType.GRID: "Grid ✕",
            SnapType.ENDPOINT: "Endpoint ▢",
            SnapType.MIDPOINT: "Midpoint △",
            SnapType.PERPENDICULAR: "Perp ⊥",
            SnapType.INTERSECTION: "Intersezione ◇"
        }
        
        lines = len(self.canvas.shape.lines)
        arrows = len(self.canvas.shape.arrows)
        contacts = len(self.canvas.shape.contact_points)
        
        self.status_label.setText(
            f"Pos: ({int(pos.x())}, {int(pos.y())}) | "
            f"Snap: {snap_names.get(snap_type, 'N/A')} | "
            f"Elementi: {lines} linee, {arrows} frecce, {contacts} contatti"
        )
    
    def _on_shape_changed(self):
        """Gestisce cambio shape"""
        # Aggiorna status se necessario
        pass
    
    def _clear_canvas(self):
        """Pulisce canvas"""
        self.canvas.clear()
        self.status_label.setText("Canvas pulito - inizia a disegnare")
    
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
