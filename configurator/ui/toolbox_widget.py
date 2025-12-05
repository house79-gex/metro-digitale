"""
Toolbox widget con elementi trascinabili
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtCore import Qt, QMimeData, QByteArray
from PyQt6.QtGui import QDrag
import json


class DraggableTreeWidget(QTreeWidget):
    """TreeWidget with drag support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.DragOnly)
        self._element_icons = set()
    
    def set_element_icons(self, icons):
        """Set the list of icon prefixes used in elements"""
        self._element_icons = set(icons)
    
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item is None or item.parent() is None:
            return
        
        element_type = item.data(0, Qt.ItemDataRole.UserRole)
        if not element_type:
            element_type = item.text(0)
            # Remove any icon prefix from the element name
            for prefix in self._element_icons:
                if element_type.startswith(prefix):
                    element_type = element_type[len(prefix):]
                    break
        
        category = item.parent().text(0) if item.parent() else ""
        
        mime_data = QMimeData()
        data = {'type': element_type, 'category': category}
        mime_data.setData('application/x-metro-element', QByteArray(json.dumps(data).encode('utf-8')))
        mime_data.setText(element_type)
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)


class ToolboxWidget(QWidget):
    """Toolbox con categorie di elementi trascinabili"""
    
    ELEMENTS = {
        "Layout": [
            {"name": "Panel", "icon": "□", "desc": "Pannello contenitore"},
            {"name": "Frame", "icon": "▢", "desc": "Cornice con bordo"},
            {"name": "Separator", "icon": "─", "desc": "Linea separatrice"},
        ],
        "Testo": [
            {"name": "Label", "icon": "Aa", "desc": "Etichetta testo"},
            {"name": "MeasureDisplay", "icon": "📏", "desc": "Display misura grande"},
            {"name": "FormulaResult", "icon": "fx", "desc": "Risultato formula"},
        ],
        "Controlli": [
            {"name": "Button", "icon": "▣", "desc": "Pulsante standard"},
            {"name": "IconButton", "icon": "🔘", "desc": "Pulsante con icona"},
            {"name": "ToggleButton", "icon": "◐", "desc": "Pulsante on/off"},
        ],
        "Input": [
            {"name": "NumberInput", "icon": "123", "desc": "Campo numerico"},
            {"name": "Slider", "icon": "──●──", "desc": "Cursore valore"},
            {"name": "Dropdown", "icon": "▼", "desc": "Menu a tendina"},
        ],
        "Speciali": [
            {"name": "TipologiaWidget", "icon": "🪟", "desc": "Selettore tipologia"},
            {"name": "AstinaSelector", "icon": "📐", "desc": "Selettore astina"},
            {"name": "MaterialSelector", "icon": "🧱", "desc": "Selettore materiale"},
        ],
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        title = QLabel("📦 Elementi")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff88; padding: 8px; background: #0f3460; border-radius: 4px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        hint = QLabel("Trascina elementi sul canvas →")
        hint.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        
        self.tree = DraggableTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setAnimated(True)
        layout.addWidget(self.tree)
        
        # Collect all icon prefixes from elements
        icon_prefixes = {'📁 '}  # Category icon
        for elements in self.ELEMENTS.values():
            for elem in elements:
                icon_prefixes.add(elem['icon'] + ' ')
        self.tree.set_element_icons(icon_prefixes)
        
        self._populate_tree()
    
    def _populate_tree(self):
        for category, elements in self.ELEMENTS.items():
            cat_item = QTreeWidgetItem(self.tree, [f"📁 {category}"])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            for elem in elements:
                elem_item = QTreeWidgetItem(cat_item, [f"{elem['icon']} {elem['name']}"])
                elem_item.setToolTip(0, elem['desc'])
                elem_item.setData(0, Qt.ItemDataRole.UserRole, elem['name'])
        self.tree.expandAll()
