"""
Canvas widget per design UI drag & drop
Simula display 800x480 del Metro Digitale con cornice realistica
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QLinearGradient,
    QFont, QDragEnterEvent, QDragMoveEvent, QDropEvent
)
import json


class CanvasElement(QGraphicsRectItem):
    """Elemento grafico sul canvas"""
    
    ELEMENT_STYLES = {
        "Button": {"color": "#00ff88", "text_color": "#000", "default_size": (100, 40)},
        "IconButton": {"color": "#0088ff", "text_color": "#fff", "default_size": (60, 60)},
        "ToggleButton": {"color": "#ff8800", "text_color": "#fff", "default_size": (100, 40)},
        "Label": {"color": "#ffffff", "text_color": "#fff", "default_size": (120, 30)},
        "MeasureDisplay": {"color": "#00ff88", "text_color": "#000", "default_size": (200, 80)},
        "FormulaResult": {"color": "#88ff00", "text_color": "#000", "default_size": (150, 50)},
        "Panel": {"color": "#1a1a2e", "text_color": "#fff", "default_size": (200, 150)},
        "Frame": {"color": "#2a2a3e", "text_color": "#fff", "default_size": (180, 120)},
        "Separator": {"color": "#00ff88", "text_color": "#fff", "default_size": (200, 2)},
        "NumberInput": {"color": "#ffffff", "text_color": "#000", "default_size": (100, 35)},
        "Slider": {"color": "#00ff88", "text_color": "#fff", "default_size": (150, 30)},
        "Dropdown": {"color": "#ffffff", "text_color": "#000", "default_size": (120, 35)},
        "TipologiaWidget": {"color": "#8800ff", "text_color": "#fff", "default_size": (200, 150)},
        "AstinaSelector": {"color": "#ff0088", "text_color": "#fff", "default_size": (180, 100)},
        "MaterialSelector": {"color": "#00ff88", "text_color": "#000", "default_size": (180, 100)},
    }
    
    def __init__(self, element_type: str, x: float, y: float):
        style = self.ELEMENT_STYLES.get(element_type, {"color": "#888888", "text_color": "#fff", "default_size": (100, 50)})
        width, height = style["default_size"]
        
        super().__init__(0, 0, width, height)
        
        self.element_type = element_type
        self.is_selected = False
        
        # Stile elemento
        self.setBrush(QBrush(QColor(style["color"])))
        self.setPen(QPen(QColor("#333333"), 2))
        
        # Posizione
        self.setPos(x, y)
        
        # Flags
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Testo
        self.text_item = QGraphicsTextItem(element_type, self)
        self.text_item.setDefaultTextColor(QColor(style["text_color"]))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.text_item.setFont(font)
        
        # Centra testo
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            (width - text_rect.width()) / 2,
            (height - text_rect.height()) / 2
        )
    
    def set_selected(self, selected: bool):
        """Imposta selezione con bordo arancione"""
        self.is_selected = selected
        if selected:
            self.setPen(QPen(QColor("#ff8800"), 3))
        else:
            self.setPen(QPen(QColor("#333333"), 2))
    
    def contextMenuEvent(self, event):
        """Menu contestuale"""
        menu = QMenu()
        delete_action = menu.addAction("Elimina")
        duplicate_action = menu.addAction("Duplica")
        menu.addSeparator()
        properties_action = menu.addAction("Proprietà")
        
        action = menu.exec(event.screenPos())
        
        if action == delete_action:
            if self.scene():
                self.scene().removeItem(self)
        elif action == duplicate_action:
            if self.scene():
                new_elem = CanvasElement(self.element_type, self.x() + 20, self.y() + 20)
                self.scene().addItem(new_elem)
        elif action == properties_action:
            # TODO: Apri dialog proprietà
            pass


class CanvasWidget(QGraphicsView):
    """Canvas per design interfaccia con drag & drop"""
    
    selection_changed = pyqtSignal(list)
    mouse_position_changed = pyqtSignal(int, int)
    
    # Dimensioni display Metro Digitale
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._init_scene()
        self._init_view()
        
        self.selected_items = []
        self.grid_size = 10
        self.show_grid = True
        self.snap_to_grid = True
        
        # Abilita drop
        self.setAcceptDrops(True)
    
    def _init_scene(self):
        """Inizializza scene grafica"""
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        self.scene.setBackgroundBrush(QBrush(QColor("#16213e")))
        self.setScene(self.scene)
    
    def _init_view(self):
        """Configura view"""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Scroll
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    
    def drawBackground(self, painter, rect):
        """Disegna sfondo con griglia opzionale"""
        super().drawBackground(painter, rect)
        
        if self.show_grid:
            # Griglia punteggiata
            painter.setPen(QPen(QColor("#1a1a2e"), 1, Qt.PenStyle.DotLine))
            
            left = int(rect.left()) - (int(rect.left()) % self.grid_size)
            top = int(rect.top()) - (int(rect.top()) % self.grid_size)
            
            # Linee verticali
            x = left
            while x < rect.right():
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
                x += self.grid_size
            
            # Linee orizzontali
            y = top
            while y < rect.bottom():
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)
                y += self.grid_size
        
        # Bordo display verde
        painter.setPen(QPen(QColor("#00ff88"), 3))
        painter.drawRect(0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
    
    def drawForeground(self, painter, rect):
        """Disegna indicatori dimensioni"""
        super().drawForeground(painter, rect)
        
        # Font per dimensioni
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor("#00ff88")))
        
        # Larghezza (top)
        painter.drawText(QRectF(0, -15, self.DISPLAY_WIDTH, 15), 
                        Qt.AlignmentFlag.AlignCenter, f"{self.DISPLAY_WIDTH}px")
        
        # Altezza (left)
        painter.save()
        painter.translate(0, self.DISPLAY_HEIGHT)
        painter.rotate(-90)
        painter.drawText(QRectF(0, -20, self.DISPLAY_HEIGHT, 15), 
                        Qt.AlignmentFlag.AlignCenter, f"{self.DISPLAY_HEIGHT}px")
        painter.restore()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accetta drop da toolbox"""
        if event.mimeData().hasFormat('application/x-metro-element'):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        """Valida posizione drop (solo dentro display)"""
        if event.mimeData().hasFormat('application/x-metro-element'):
            pos = self.mapToScene(event.position().toPoint())
            if 0 <= pos.x() <= self.DISPLAY_WIDTH and 0 <= pos.y() <= self.DISPLAY_HEIGHT:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Crea elemento sul canvas"""
        if event.mimeData().hasFormat('application/x-metro-element'):
            data = json.loads(event.mimeData().data('application/x-metro-element').data().decode('utf-8'))
            element_type = data.get('type', 'Button')
            
            # Posizione drop
            pos = self.mapToScene(event.position().toPoint())
            x, y = pos.x(), pos.y()
            
            # Snap to grid
            if self.snap_to_grid:
                x = round(x / self.grid_size) * self.grid_size
                y = round(y / self.grid_size) * self.grid_size
            
            # Crea elemento
            element = CanvasElement(element_type, x, y)
            self.scene.addItem(element)
            
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def mouseMoveEvent(self, event):
        """Emetti coordinate mouse"""
        pos = self.mapToScene(event.pos())
        self.mouse_position_changed.emit(int(pos.x()), int(pos.y()))
        super().mouseMoveEvent(event)
    
    def clear(self):
        """Pulisce il canvas"""
        self.scene.clear()
        self.selected_items = []
        self.selection_changed.emit([])
    
    def toggle_grid(self, show: bool):
        """Mostra/nascondi griglia"""
        self.show_grid = show
        self.viewport().update()
    
    def toggle_snap(self, snap: bool):
        """Abilita/disabilita snap to grid"""
        self.snap_to_grid = snap
    
    def set_grid_size(self, size: int):
        """Imposta dimensione griglia"""
        self.grid_size = max(5, min(50, size))
        self.viewport().update()
    
    def set_zoom(self, zoom_percent: int):
        """Imposta zoom (50-200%)"""
        scale = zoom_percent / 100.0
        self.resetTransform()
        self.scale(scale, scale)


class DisplayPreviewWidget(QWidget):
    """Widget contenitore con header, canvas e footer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Canvas container con cornice
        canvas_container = self._create_canvas_container()
        layout.addWidget(canvas_container, 1)
        
        # Footer
        footer = self._create_footer()
        layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Crea header con info display e zoom"""
        header = QWidget()
        header.setStyleSheet("background: #0f3460; padding: 8px;")
        header_layout = QHBoxLayout(header)
        
        # Info display
        info_label = QLabel("📺 Display 5\" (800x480) - Metro Digitale ESP32")
        info_label.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(info_label)
        
        header_layout.addStretch()
        
        # Zoom control
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #fff;")
        header_layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #16213e;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ff88;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        header_layout.addWidget(self.zoom_slider)
        
        self.zoom_value_label = QLabel("100%")
        self.zoom_value_label.setStyleSheet("color: #fff; min-width: 40px;")
        header_layout.addWidget(self.zoom_value_label)
        
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        
        return header
    
    def _create_canvas_container(self) -> QWidget:
        """Crea container con cornice 3D e canvas"""
        container = QWidget()
        container.setStyleSheet("background: #0a0e1a;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Frame con cornice 3D
        frame = QWidget()
        frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #4a4a5a, stop:0.5 #6a6a7a, stop:1 #3a3a4a);
            border: 3px solid #2a2a3a;
            border-radius: 8px;
            padding: 15px;
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        
        # Canvas
        self.canvas = CanvasWidget()
        self.canvas.setStyleSheet("border: 3px solid #00ff88; background: #16213e;")
        frame_layout.addWidget(self.canvas)
        
        container_layout.addWidget(frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        return container
    
    def _create_footer(self) -> QWidget:
        """Crea footer con coordinate mouse"""
        footer = QWidget()
        footer.setStyleSheet("background: #0f3460; padding: 4px 8px;")
        footer_layout = QHBoxLayout(footer)
        
        self.coords_label = QLabel("Mouse: (0, 0)")
        self.coords_label.setStyleSheet("color: #888; font-size: 11px;")
        footer_layout.addWidget(self.coords_label)
        
        footer_layout.addStretch()
        
        grid_label = QLabel("Grid: 10px | Snap: ON")
        grid_label.setStyleSheet("color: #888; font-size: 11px;")
        footer_layout.addWidget(grid_label)
        
        self.canvas.mouse_position_changed.connect(self._on_mouse_moved)
        
        return footer
    
    def _on_zoom_changed(self, value):
        """Gestisce cambio zoom"""
        self.zoom_value_label.setText(f"{value}%")
        self.canvas.set_zoom(value)
    
    def _on_mouse_moved(self, x, y):
        """Aggiorna coordinate mouse"""
        self.coords_label.setText(f"Mouse: ({x}, {y})")
