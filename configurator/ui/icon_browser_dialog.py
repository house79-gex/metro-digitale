"""
Dialog browser icone con supporto Iconify e icone locali
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QLabel, QComboBox,
    QListWidgetItem, QProgressBar, QTabWidget, QFileDialog,
    QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QByteArray, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent
import io
from pathlib import Path

try:
    from PyQt6.QtSvg import QSvgRenderer
    HAS_SVG = True
except ImportError:
    HAS_SVG = False

from core.icon_browser import IconifyClient
from core.icon_manager import IconManager


class IconBrowserDialog(QDialog):
    """Dialog per selezionare icone da Iconify o locali"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.client = IconifyClient()
        self.icon_manager = IconManager()
        self.selected_icon = None
        self.selected_icon_source = None  # 'iconify' o 'local'
        
        self.setWindowTitle("Browser Icone")
        self.resize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Iconify
        iconify_tab = self._create_iconify_tab()
        self.tabs.addTab(iconify_tab, "🌐 Iconify")
        
        # Tab 2: Locali
        local_tab = self._create_local_tab()
        self.tabs.addTab(local_tab, "💾 Locali")
        
        # Tab 3: Importa
        import_tab = self._create_import_tab()
        self.tabs.addTab(import_tab, "📥 Importa")
        
        layout.addWidget(self.tabs)
        
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
    
    def _create_iconify_tab(self) -> QWidget:
        """Crea tab Iconify"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        self.results_list.itemDoubleClicked.connect(self._on_iconify_double_clicked)
        layout.addWidget(self.results_list)
        
        # Status
        self.iconify_status_label = QLabel("Cerca un'icona per iniziare")
        layout.addWidget(self.iconify_status_label)
        
        return tab
    
    def _create_local_tab(self) -> QWidget:
        """Crea tab icone locali"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Intestazione
        header = QLabel("Icone importate localmente:")
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Lista icone locali
        self.local_list = QListWidget()
        self.local_list.setIconSize(QSize(64, 64))
        self.local_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.local_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.local_list.itemDoubleClicked.connect(self._on_local_double_clicked)
        layout.addWidget(self.local_list)
        
        # Pulsanti gestione
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Aggiorna")
        refresh_btn.clicked.connect(self._refresh_local_icons)
        buttons_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("🗑️ Elimina")
        delete_btn.clicked.connect(self._delete_local_icon)
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Status
        self.local_status_label = QLabel("Nessuna icona locale")
        layout.addWidget(self.local_status_label)
        
        # Carica icone locali
        self._refresh_local_icons()
        
        return tab
    
    def _create_import_tab(self) -> QWidget:
        """Crea tab import icone"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Intestazione
        header = QLabel("Importa icone locali (SVG, PNG, JPG)")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Area drag & drop
        self.drop_area = QLabel("📎 Trascina file qui o usa il pulsante sotto")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 3px dashed #00ff88;
                border-radius: 10px;
                padding: 50px;
                background: #1a1a2e;
                color: #00ff88;
                font-size: 16px;
            }
        """)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.dragEnterEvent = self._drag_enter_event
        self.drop_area.dropEvent = self._drop_event
        layout.addWidget(self.drop_area)
        
        # Pulsante sfoglia
        browse_btn = QPushButton("📂 Sfoglia File...")
        browse_btn.clicked.connect(self._browse_import_file)
        browse_btn.setMinimumHeight(50)
        layout.addWidget(browse_btn)
        
        # Info formati
        info_label = QLabel(
            "Formati supportati:\n"
            "• SVG (scalabili, consigliati)\n"
            "• PNG (trasparenti)\n"
            "• JPG/JPEG"
        )
        info_label.setStyleSheet("color: #aaa; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return tab
    
    def _on_search(self):
        """Esegue ricerca icone Iconify"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        icon_set = self.set_combo.currentData()
        
        self.iconify_status_label.setText("Ricerca in corso...")
        self.results_list.clear()
        
        # Cerca icone (aumentato limite a 100 per visualizzare più icone)
        results = self.client.search(query, limit=100, prefix=icon_set if icon_set else None)
        
        if not results:
            self.iconify_status_label.setText("Nessuna icona trovata")
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
        
        self.iconify_status_label.setText(f"Trovate {len(results)} icone")
    
    def _quick_search(self, keyword: str):
        """Ricerca rapida con keyword"""
        self.search_input.setText(keyword)
        self._on_search()
    
    def _on_iconify_double_clicked(self, item):
        """Doppio click su icona Iconify"""
        self.selected_icon = item.data(Qt.ItemDataRole.UserRole)
        self.selected_icon_source = 'iconify'
        self.accept()
    
    def _on_local_double_clicked(self, item):
        """Doppio click su icona locale"""
        self.selected_icon = item.data(Qt.ItemDataRole.UserRole)
        self.selected_icon_source = 'local'
        self.accept()
    
    def _on_select(self):
        """Seleziona icona corrente"""
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:  # Iconify
            current = self.results_list.currentItem()
            if current:
                self.selected_icon = current.data(Qt.ItemDataRole.UserRole)
                self.selected_icon_source = 'iconify'
                self.accept()
        elif current_tab == 1:  # Locali
            current = self.local_list.currentItem()
            if current:
                self.selected_icon = current.data(Qt.ItemDataRole.UserRole)
                self.selected_icon_source = 'local'
                self.accept()
    
    def _refresh_local_icons(self):
        """Aggiorna lista icone locali"""
        self.local_list.clear()
        
        local_icons = self.icon_manager.list_local_icons()
        
        if not local_icons:
            self.local_status_label.setText("Nessuna icona locale trovata")
            return
        
        for icon_id in local_icons:
            icon_info = self.icon_manager.get_icon_info(icon_id)
            
            item = QListWidgetItem(icon_id)
            item.setData(Qt.ItemDataRole.UserRole, icon_id)
            item.setToolTip(f"File: {icon_info['filename']}")
            
            # Carica icona
            pixmap = self.icon_manager.get_pixmap(icon_id, QSize(64, 64))
            if pixmap:
                item.setIcon(QIcon(pixmap))
            
            self.local_list.addItem(item)
        
        self.local_status_label.setText(f"{len(local_icons)} icone locali")
    
    def _delete_local_icon(self):
        """Elimina icona locale selezionata"""
        current = self.local_list.currentItem()
        if not current:
            return
        
        icon_id = current.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Eliminare l'icona '{icon_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.icon_manager.delete_icon(icon_id):
                self._refresh_local_icons()
                QMessageBox.information(self, "Successo", "Icona eliminata")
            else:
                QMessageBox.warning(self, "Errore", "Impossibile eliminare l'icona")
    
    def _drag_enter_event(self, event: QDragEnterEvent):
        """Gestisce drag enter per import"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def _drop_event(self, event: QDropEvent):
        """Gestisce drop per import"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self._import_files(files)
    
    def _browse_import_file(self):
        """Sfoglia file da importare"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleziona Icone da Importare",
            "",
            "Immagini (*.svg *.png *.jpg *.jpeg);;Tutti i file (*)"
        )
        
        if files:
            self._import_files(files)
    
    def _import_files(self, filepaths: list):
        """Importa file icone"""
        imported_count = 0
        
        for filepath in filepaths:
            filepath = Path(filepath)
            
            # Importa icona
            icon_id = self.icon_manager.import_file(filepath)
            
            if icon_id:
                imported_count += 1
        
        if imported_count > 0:
            QMessageBox.information(
                self,
                "Import Completato",
                f"{imported_count} icone importate con successo"
            )
            
            # Aggiorna lista e passa al tab locali
            self._refresh_local_icons()
            self.tabs.setCurrentIndex(1)
        else:
            QMessageBox.warning(
                self,
                "Errore Import",
                "Nessuna icona importata. Verifica i formati."
            )
    
    def get_selected_icon(self):
        """Ottiene icona selezionata"""
        return self.selected_icon
    
    def get_selected_icon_source(self):
        """Ottiene sorgente icona selezionata"""
        return self.selected_icon_source
    
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
