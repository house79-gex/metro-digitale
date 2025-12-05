"""
Preview widget per anteprima live display
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class PreviewWidget(QWidget):
    """Widget per anteprima display 800x480"""
    
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        self.setMaximumSize(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
    
    def paintEvent(self, event):
        """Disegna preview"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Sfondo
        painter.fillRect(self.rect(), QColor("#16213e"))
        
        # Bordo
        painter.setPen(QPen(QColor("#00ff88"), 2))
        painter.drawRect(0, 0, self.DISPLAY_WIDTH - 1, self.DISPLAY_HEIGHT - 1)
        
        # Placeholder testo
        painter.setPen(QColor("#888888"))
        font = QFont("Arial", 20)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Anteprima Display 800×480"
        )
