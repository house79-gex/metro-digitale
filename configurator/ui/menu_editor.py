"""
Editor menu gerarchico ad albero
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QPushButton, QToolButton
)
from PyQt6.QtCore import Qt
from typing import List

from core.config_model import MenuItem


class MenuEditor(QWidget):
    """Editor per menu gerarchico"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_add = QToolButton()
        self.btn_add.setText("+")
        self.btn_add.setToolTip("Aggiungi menu")
        self.btn_add.clicked.connect(self._on_add_menu)
        toolbar.addWidget(self.btn_add)
        
        self.btn_add_child = QToolButton()
        self.btn_add_child.setText("⤷")
        self.btn_add_child.setToolTip("Aggiungi sottomenu")
        self.btn_add_child.clicked.connect(self._on_add_submenu)
        toolbar.addWidget(self.btn_add_child)
        
        self.btn_remove = QToolButton()
        self.btn_remove.setText("−")
        self.btn_remove.setToolTip("Rimuovi menu")
        self.btn_remove.clicked.connect(self._on_remove_menu)
        toolbar.addWidget(self.btn_remove)
        
        toolbar.addStretch()
        
        self.btn_edit = QPushButton("Modifica")
        self.btn_edit.clicked.connect(self._on_edit_menu)
        toolbar.addWidget(self.btn_edit)
        
        layout.addLayout(toolbar)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nome", "Icona", "Azione"])
        self.tree.setColumnWidth(0, 200)
        layout.addWidget(self.tree)
    
    def load_menus(self, menus: List[MenuItem]):
        """Carica menu nell'editor"""
        self.tree.clear()
        for menu in sorted(menus, key=lambda m: m.ordine):
            self._add_menu_item(menu, self.tree)
    
    def _add_menu_item(self, menu: MenuItem, parent):
        """Aggiunge item menu all'albero"""
        item = QTreeWidgetItem(parent)
        item.setText(0, menu.nome)
        item.setText(1, menu.icona)
        item.setText(2, menu.azione)
        item.setData(0, Qt.ItemDataRole.UserRole, menu)
        
        # Aggiungi figli
        for child in sorted(menu.figli, key=lambda m: m.ordine):
            self._add_menu_item(child, item)
        
        return item
    
    def get_menus(self) -> List[MenuItem]:
        """Ottiene menu dall'editor"""
        menus = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            menu = item.data(0, Qt.ItemDataRole.UserRole)
            if menu:
                menus.append(menu)
        return menus
    
    def _on_add_menu(self):
        """Aggiungi nuovo menu"""
        menu = MenuItem(
            id=f"menu_{self.tree.topLevelItemCount()}",
            nome="Nuovo Menu",
            icona="mdi:menu",
            ordine=self.tree.topLevelItemCount()
        )
        self._add_menu_item(menu, self.tree)
    
    def _on_add_submenu(self):
        """Aggiungi sottomenu"""
        current = self.tree.currentItem()
        if not current:
            return
        
        parent_menu = current.data(0, Qt.ItemDataRole.UserRole)
        submenu = MenuItem(
            id=f"{parent_menu.id}_sub_{len(parent_menu.figli)}",
            nome="Nuovo Sottomenu",
            icona="mdi:arrow-right",
            ordine=len(parent_menu.figli)
        )
        parent_menu.figli.append(submenu)
        self._add_menu_item(submenu, current)
    
    def _on_remove_menu(self):
        """Rimuovi menu selezionato"""
        current = self.tree.currentItem()
        if not current:
            return
        
        parent = current.parent()
        if parent:
            parent.removeChild(current)
        else:
            index = self.tree.indexOfTopLevelItem(current)
            self.tree.takeTopLevelItem(index)
    
    def _on_edit_menu(self):
        """Modifica menu selezionato"""
        current = self.tree.currentItem()
        if not current:
            return
        
        # TODO: Apri dialog editing menu
        pass
