"""
Canvas widget per design UI drag & drop
Simula display 800x480 del Metro Digitale
"""

from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush


class CanvasWidget(QGraphicsView):
    """Canvas per design interfaccia con drag & drop"""
    
    selection_changed = pyqtSignal(list)
    
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
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Abilita scroll
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Centra view
        self.centerOn(self.DISPLAY_WIDTH / 2, self.DISPLAY_HEIGHT / 2)
    
    def drawBackground(self, painter, rect):
        """Disegna sfondo con griglia"""
        super().drawBackground(painter, rect)
        
        if not self.show_grid:
            return
        
        # Disegna griglia
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
        
        # Bordo display
        painter.setPen(QPen(QColor("#00ff88"), 2))
        painter.drawRect(0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
    
    def clear(self):
        """Pulisce il canvas"""
        self.scene.clear()
        self.selected_items = []
        self.selection_changed.emit([])
    
    def toggle_grid(self, show: bool):
        """Mostra/nascondi griglia"""
        self.show_grid = show
        self.viewport().update()
    
    def set_grid_size(self, size: int):
        """Imposta dimensione griglia"""
        self.grid_size = max(5, min(50, size))
        self.viewport().update()
    
    def zoom_in(self):
        """Zoom in"""
        self.scale(1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out"""
        self.scale(1 / 1.2, 1 / 1.2)
    
    def zoom_reset(self):
        """Reset zoom"""
        self.resetTransform()
    
    def fit_in_view(self):
        """Adatta alla vista"""
        self.fitInView(0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, 
                      Qt.AspectRatioMode.KeepAspectRatio)
    
    def wheelEvent(self, event):
        """Gestisce zoom con rotella mouse"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom con Ctrl + rotella
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
