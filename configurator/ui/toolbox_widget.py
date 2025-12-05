"""
Toolbox widget con elementi trascinabili
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QScrollArea
)
from PyQt6.QtCore import Qt


class ToolboxWidget(QWidget):
    """Toolbox con categorie di elementi trascinabili"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titolo
        title = QLabel("Elementi")
        title.setProperty("heading", True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tree widget con categorie
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree)
        
        self._populate_tree()
    
    def _populate_tree(self):
        """Popola albero con categorie elementi"""
        
        # Categoria Layout
        layout_cat = QTreeWidgetItem(self.tree, ["Layout"])
        QTreeWidgetItem(layout_cat, ["Panel"])
        QTreeWidgetItem(layout_cat, ["Frame"])
        QTreeWidgetItem(layout_cat, ["Separator"])
        
        # Categoria Testo
        text_cat = QTreeWidgetItem(self.tree, ["Testo"])
        QTreeWidgetItem(text_cat, ["Label"])
        QTreeWidgetItem(text_cat, ["MeasureDisplay"])
        QTreeWidgetItem(text_cat, ["FormulaResult"])
        
        # Categoria Controlli
        controls_cat = QTreeWidgetItem(self.tree, ["Controlli"])
        QTreeWidgetItem(controls_cat, ["Button"])
        QTreeWidgetItem(controls_cat, ["IconButton"])
        QTreeWidgetItem(controls_cat, ["ToggleButton"])
        
        # Categoria Input
        input_cat = QTreeWidgetItem(self.tree, ["Input"])
        QTreeWidgetItem(input_cat, ["NumberInput"])
        QTreeWidgetItem(input_cat, ["Slider"])
        QTreeWidgetItem(input_cat, ["Dropdown"])
        
        # Categoria Speciali
        special_cat = QTreeWidgetItem(self.tree, ["Speciali"])
        QTreeWidgetItem(special_cat, ["TipologiaWidget"])
        QTreeWidgetItem(special_cat, ["AstinaSelector"])
        
        # Espandi tutto
        self.tree.expandAll()
