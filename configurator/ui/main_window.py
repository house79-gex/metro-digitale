"""
Finestra principale Metro Digitale Configurator
Layout con dock widgets e toolbar
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDockWidget, QToolBar, QStatusBar, QMessageBox,
    QFileDialog, QLabel, QTabWidget
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from core.project_manager import ProjectManager
from core.config_model import ProgettoConfigurazione
from .canvas_widget import DisplayPreviewWidget
from .toolbox_widget import ToolboxWidget
from .properties_panel import PropertiesPanel
from .menu_editor import MenuEditor
from .formula_editor import FormulaEditor
from .tipologia_editor import TipologiaEditor


class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione"""
    
    project_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.project_manager = ProjectManager()
        self.current_project = self.project_manager.new_project()
        
        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_docks()
        self._create_statusbar()
        
        self.setWindowTitle("Metro Digitale Configurator")
        self.resize(1400, 900)
        self.showMaximized()
    
    def _init_ui(self):
        """Inizializza UI centrale"""
        # Widget centrale: Display Preview with Canvas
        self.display_preview = DisplayPreviewWidget()
        self.canvas = self.display_preview.canvas
        self.setCentralWidget(self.display_preview)
        
        # Connect signals
        self.canvas.selection_changed.connect(self._on_selection_changed)
        self.canvas.open_properties_requested.connect(self._on_open_properties)
    
    def _create_actions(self):
        """Crea azioni per menu e toolbar"""
        # File
        self.action_new = QAction("&Nuovo", self)
        self.action_new.setShortcut(QKeySequence.StandardKey.New)
        self.action_new.setStatusTip("Crea nuovo progetto")
        self.action_new.triggered.connect(self._on_new_project)
        
        self.action_open = QAction("&Apri", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.setStatusTip("Apri progetto esistente")
        self.action_open.triggered.connect(self._on_open_project)
        
        self.action_save = QAction("&Salva", self)
        self.action_save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save.setStatusTip("Salva progetto")
        self.action_save.triggered.connect(self._on_save_project)
        
        self.action_save_as = QAction("Salva &con nome...", self)
        self.action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.action_save_as.triggered.connect(self._on_save_as_project)
        
        self.action_export = QAction("&Esporta JSON", self)
        self.action_export.triggered.connect(self._on_export_json)
        
        self.action_exit = QAction("E&sci", self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_exit.triggered.connect(self.close)
        
        # Edit
        self.action_undo = QAction("&Annulla", self)
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.action_undo.setEnabled(False)
        
        self.action_redo = QAction("&Ripeti", self)
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.action_redo.setEnabled(False)
        
        self.action_cut = QAction("&Taglia", self)
        self.action_cut.setShortcut(QKeySequence.StandardKey.Cut)
        
        self.action_copy = QAction("&Copia", self)
        self.action_copy.setShortcut(QKeySequence.StandardKey.Copy)
        
        self.action_paste = QAction("&Incolla", self)
        self.action_paste.setShortcut(QKeySequence.StandardKey.Paste)
        
        self.action_delete = QAction("&Elimina", self)
        self.action_delete.setShortcut(QKeySequence.StandardKey.Delete)
        
        # View
        self.action_toggle_toolbox = QAction("&Toolbox", self)
        self.action_toggle_toolbox.setCheckable(True)
        self.action_toggle_toolbox.setChecked(True)
        
        self.action_toggle_properties = QAction("&Proprietà", self)
        self.action_toggle_properties.setCheckable(True)
        self.action_toggle_properties.setChecked(True)
        
        self.action_toggle_editors = QAction("&Editor", self)
        self.action_toggle_editors.setCheckable(True)
        self.action_toggle_editors.setChecked(True)
        
        # Tools
        self.action_upload = QAction("&Upload ESP32", self)
        self.action_upload.setStatusTip("Carica configurazione su ESP32")
        self.action_upload.triggered.connect(self._on_upload_esp32)
        
        self.action_icon_browser = QAction("Browser &Icone", self)
        self.action_icon_browser.triggered.connect(self._on_icon_browser)
        
        self.action_test_formulas = QAction("&Test Formule", self)
        self.action_test_formulas.triggered.connect(self._on_test_formulas)
        
        self.action_template_browser = QAction("Browser &Template", self)
        self.action_template_browser.setStatusTip("Carica template preimpostati")
        self.action_template_browser.triggered.connect(self._on_template_browser)
        
        self.action_simulation = QAction("🎮 Modalità &Simulazione", self)
        self.action_simulation.setStatusTip("Simula funzionamento dispositivo")
        self.action_simulation.triggered.connect(self._on_simulation_mode)
        
        self.action_probe_editor = QAction("✏️ Editor &Puntali", self)
        self.action_probe_editor.setStatusTip("Editor grafico forma puntali")
        self.action_probe_editor.triggered.connect(self._on_probe_editor)
        
        # Help
        self.action_documentation = QAction("&Documentazione", self)
        self.action_documentation.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.action_documentation.triggered.connect(self._on_documentation)
        
        self.action_about = QAction("&Info", self)
        self.action_about.triggered.connect(self._on_about)
    
    def _create_menus(self):
        """Crea menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.action_new)
        file_menu.addAction(self.action_open)
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.action_export)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Modifica")
        edit_menu.addAction(self.action_undo)
        edit_menu.addAction(self.action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_cut)
        edit_menu.addAction(self.action_copy)
        edit_menu.addAction(self.action_paste)
        edit_menu.addAction(self.action_delete)
        
        # View Menu
        view_menu = menubar.addMenu("&Visualizza")
        view_menu.addAction(self.action_toggle_toolbox)
        view_menu.addAction(self.action_toggle_properties)
        view_menu.addAction(self.action_toggle_editors)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Strumenti")
        tools_menu.addAction(self.action_upload)
        tools_menu.addAction(self.action_icon_browser)
        tools_menu.addAction(self.action_template_browser)
        tools_menu.addSeparator()
        tools_menu.addAction(self.action_simulation)
        tools_menu.addAction(self.action_probe_editor)
        tools_menu.addSeparator()
        tools_menu.addAction(self.action_test_formulas)
        
        # Help Menu
        help_menu = menubar.addMenu("&Aiuto")
        help_menu.addAction(self.action_documentation)
        help_menu.addSeparator()
        help_menu.addAction(self.action_about)
    
    def _create_toolbars(self):
        """Crea toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.action_upload)
    
    def _create_docks(self):
        """Crea dock widgets"""
        # Dock Toolbox (sinistra)
        self.dock_toolbox = QDockWidget("Toolbox", self)
        self.toolbox = ToolboxWidget()
        self.dock_toolbox.setWidget(self.toolbox)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_toolbox)
        self.action_toggle_toolbox.triggered.connect(
            lambda checked: self.dock_toolbox.setVisible(checked)
        )
        
        # Dock Properties (destra)
        self.dock_properties = QDockWidget("Proprietà", self)
        self.properties_panel = PropertiesPanel()
        self.dock_properties.setWidget(self.properties_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_properties)
        self.action_toggle_properties.triggered.connect(
            lambda checked: self.dock_properties.setVisible(checked)
        )
        
        # Dock Editors (basso)
        self.dock_editors = QDockWidget("Editor", self)
        self.editor_tabs = QTabWidget()
        
        self.menu_editor = MenuEditor()
        self.formula_editor = FormulaEditor()
        self.tipologia_editor = TipologiaEditor()
        
        self.editor_tabs.addTab(self.menu_editor, "Menu")
        self.editor_tabs.addTab(self.tipologia_editor, "Tipologie")
        self.editor_tabs.addTab(self.formula_editor, "Formule")
        
        self.dock_editors.setWidget(self.editor_tabs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_editors)
        self.action_toggle_editors.triggered.connect(
            lambda checked: self.dock_editors.setVisible(checked)
        )
    
    def _create_statusbar(self):
        """Crea status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.status_label = QLabel("Pronto")
        self.statusbar.addWidget(self.status_label)
        
        self.project_label = QLabel("Nessun progetto")
        self.statusbar.addPermanentWidget(self.project_label)
    
    def _on_selection_changed(self, selected_items):
        """Gestisce cambio selezione nel canvas"""
        if selected_items:
            # Mostra proprietà del primo elemento selezionato
            self.properties_panel.set_item(selected_items[0])
        else:
            self.properties_panel.clear()
    
    def _on_open_properties(self, element):
        """Apre pannello proprietà per elemento"""
        self.properties_panel.set_item(element)
        self.dock_properties.show()
        self.dock_properties.raise_()
    
    def _on_new_project(self):
        """Crea nuovo progetto"""
        if self.project_manager.is_modified():
            reply = QMessageBox.question(
                self,
                "Salva modifiche?",
                "Il progetto corrente ha modifiche non salvate. Salvare?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._on_save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.current_project = self.project_manager.new_project()
        self.canvas.clear()
        self._update_ui()
        self.statusbar.showMessage("Nuovo progetto creato", 3000)
    
    def _on_open_project(self):
        """Apri progetto esistente"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Apri Progetto",
            "",
            "Metro Digitale Project (*.mdp);;All Files (*)"
        )
        
        if filename:
            try:
                self.current_project = self.project_manager.load_project(filename)
                self._load_project_to_ui()
                self._update_ui()
                self.statusbar.showMessage(f"Progetto caricato: {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile aprire progetto:\n{e}")
    
    def _on_save_project(self):
        """Salva progetto"""
        if self.project_manager.get_file_path():
            try:
                self._save_ui_to_project()
                self.project_manager.save_project(
                    self.project_manager.get_file_path(),
                    self.current_project
                )
                self._update_ui()
                self.statusbar.showMessage("Progetto salvato", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile salvare:\n{e}")
        else:
            self._on_save_as_project()
    
    def _on_save_as_project(self):
        """Salva progetto con nome"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Progetto",
            "",
            "Metro Digitale Project (*.mdp);;All Files (*)"
        )
        
        if filename:
            try:
                self._save_ui_to_project()
                self.project_manager.save_project(filename, self.current_project)
                self._update_ui()
                self.statusbar.showMessage(f"Progetto salvato: {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile salvare:\n{e}")
    
    def _on_export_json(self):
        """Esporta come JSON"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                self._save_ui_to_project()
                self.project_manager.export_json(filename, self.current_project)
                self.statusbar.showMessage(f"Esportato: {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile esportare:\n{e}")
    
    def _on_upload_esp32(self):
        """Apri dialog upload ESP32"""
        from .upload_dialog import UploadDialog
        dialog = UploadDialog(self.current_project, self)
        dialog.exec()
    
    def _on_icon_browser(self):
        """Apri browser icone"""
        from .icon_browser_dialog import IconBrowserDialog
        dialog = IconBrowserDialog(self)
        if dialog.exec():
            selected_icon = dialog.get_selected_icon()
            self.statusbar.showMessage(f"Icona selezionata: {selected_icon}", 3000)
    
    def _on_test_formulas(self):
        """Apri test formule"""
        self.editor_tabs.setCurrentWidget(self.formula_editor)
        self.dock_editors.show()
    
    def _on_template_browser(self):
        """Apri browser template"""
        from .template_browser_dialog import TemplateBrowserDialog
        dialog = TemplateBrowserDialog(self)
        if dialog.exec():
            template = dialog.get_selected_template()
            if template:
                self._load_template(template)
                self.statusbar.showMessage(f"Template caricato: {template.name}", 3000)
    
    def _on_simulation_mode(self):
        """Apri modalità simulazione"""
        from .simulation_dialog import SimulationDialog
        dialog = SimulationDialog(self)
        dialog.exec()
    
    def _on_probe_editor(self):
        """Apri editor grafico puntali"""
        from .probe_editor_dialog import ProbeEditorDialog
        dialog = ProbeEditorDialog(self)
        dialog.exec()
    
    def _on_documentation(self):
        """Mostra documentazione"""
        from .tooltip_manager import get_tooltip_manager
        manager = get_tooltip_manager()
        guide_html = manager.format_guide_html('getting_started')
        
        QMessageBox.information(
            self,
            "Guida Rapida",
            guide_html
        )
    
    def _on_about(self):
        """Mostra info applicazione"""
        QMessageBox.about(
            self,
            "Metro Digitale Configurator",
            "<h3>Metro Digitale Configurator</h3>"
            "<p>Versione 1.0.0</p>"
            "<p>Configuratore visuale per Metro Digitale ESP32</p>"
            "<p>© 2024 Metro Digitale</p>"
        )
    
    def _load_project_to_ui(self):
        """Carica progetto nella UI"""
        # Carica menu
        self.menu_editor.load_menus(self.current_project.menus)
        
        # Carica tipologie
        self.tipologia_editor.load_tipologie(self.current_project.tipologie)
        
        # TODO: Carica altri elementi nel canvas
    
    def _save_ui_to_project(self):
        """Salva stato UI nel progetto"""
        # Salva menu
        self.current_project.menus = self.menu_editor.get_menus()
        
        # Salva tipologie
        self.current_project.tipologie = self.tipologia_editor.get_tipologie()
        
        # TODO: Salva elementi canvas
    
    def _load_template(self, template_info):
        """Carica template nel canvas"""
        from .canvas_widget import CanvasElement
        
        # Pulisci canvas
        self.canvas.scene.clear()
        
        # Carica elementi dal template
        for elem_data in template_info.data.get("elements", []):
            elem_type = elem_data.get("type", "Button")
            x = elem_data.get("x", 0)
            y = elem_data.get("y", 0)
            
            # Crea elemento sul canvas
            element = CanvasElement(elem_type, x, y, self.canvas)
            self.canvas.scene.addItem(element)
        
        self.statusbar.showMessage(f"Caricati {len(template_info.data.get('elements', []))} elementi dal template", 3000)
    
    def _update_ui(self):
        """Aggiorna UI con stato progetto"""
        project_name = self.project_manager.get_project_name()
        file_path = self.project_manager.get_file_path()
        modified = self.project_manager.is_modified()
        
        # Aggiorna titolo finestra
        title = f"Metro Digitale Configurator - {project_name}"
        if modified:
            title += " *"
        if file_path:
            title += f" [{file_path}]"
        self.setWindowTitle(title)
        
        # Aggiorna status bar
        self.project_label.setText(project_name)
        
        self.project_changed.emit()
    
    def closeEvent(self, event):
        """Gestisce chiusura finestra"""
        if self.project_manager.is_modified():
            reply = QMessageBox.question(
                self,
                "Salva modifiche?",
                "Il progetto corrente ha modifiche non salvate. Salvare prima di uscire?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._on_save_project()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
