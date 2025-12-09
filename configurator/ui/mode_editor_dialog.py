"""
Editor Modalità per Metro Digitale
Permette di creare/modificare modalità con workflow e formule
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QCheckBox, QComboBox, QListWidget, QGroupBox, QTabWidget,
    QWidget, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any, List, Optional


class WorkflowStepWidget(QWidget):
    """Widget per definire un passo del workflow"""
    
    def __init__(self, step_number: int, parent=None):
        super().__init__(parent)
        
        self.step_number = step_number
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Intestazione
        header = QLabel(f"Passo {step_number}")
        header.setStyleSheet("font-weight: bold; color: #00ff88;")
        layout.addWidget(header)
        
        # Form
        form = QFormLayout()
        
        self.variable_input = QLineEdit()
        self.variable_input.setPlaceholderText("es: L, H, D")
        form.addRow("Variabile:", self.variable_input)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("es: Larghezza porta")
        form.addRow("Descrizione:", self.description_input)
        
        self.probe_combo = QComboBox()
        self.probe_combo.addItems(["Interno", "Esterno", "Profondità", "Battuta"])
        form.addRow("Tipo puntale:", self.probe_combo)
        
        self.required_check = QCheckBox("Obbligatoria")
        self.required_check.setChecked(True)
        form.addRow("", self.required_check)
        
        layout.addLayout(form)
    
    def get_data(self) -> Dict[str, Any]:
        """Ottiene dati del passo"""
        return {
            'step': self.step_number,
            'variable': self.variable_input.text(),
            'description': self.description_input.text(),
            'probe_type': self.probe_combo.currentText().lower(),
            'required': self.required_check.isChecked()
        }
    
    def set_data(self, data: Dict[str, Any]):
        """Imposta dati del passo"""
        self.variable_input.setText(data.get('variable', ''))
        self.description_input.setText(data.get('description', ''))
        
        probe_type = data.get('probe_type', 'interno')
        index = self.probe_combo.findText(probe_type.capitalize())
        if index >= 0:
            self.probe_combo.setCurrentIndex(index)
        
        self.required_check.setChecked(data.get('required', True))


class ModeEditorDialog(QDialog):
    """Dialog per creare/modificare modalità di misura"""
    
    def __init__(self, parent=None, mode_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        
        self.mode_data = mode_data or {}
        self.workflow_steps: List[WorkflowStepWidget] = []
        
        self.setWindowTitle("🔧 Editor Modalità di Misura")
        self.resize(700, 650)
        
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """Inizializza interfaccia"""
        layout = QVBoxLayout(self)
        
        # Titolo
        title = QLabel("🔧 Editor Modalità di Misura")
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
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Informazioni generali
        info_tab = self._create_info_tab()
        tabs.addTab(info_tab, "ℹ️ Informazioni")
        
        # Tab 2: Workflow
        workflow_tab = self._create_workflow_tab()
        tabs.addTab(workflow_tab, "📋 Workflow")
        
        # Tab 3: Formula
        formula_tab = self._create_formula_tab()
        tabs.addTab(formula_tab, "🔢 Formula")
        
        # Tab 4: Bluetooth
        bt_tab = self._create_bluetooth_tab()
        tabs.addTab(bt_tab, "📡 Bluetooth")
        
        layout.addWidget(tabs)
        
        # Pulsanti
        buttons = QHBoxLayout()
        
        preview_btn = QPushButton("👁️ Anteprima")
        preview_btn.clicked.connect(self._preview_mode)
        buttons.addWidget(preview_btn)
        
        buttons.addStretch()
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Salva Modalità")
        save_btn.setProperty("primary", True)
        save_btn.clicked.connect(self._save_mode)
        buttons.addWidget(save_btn)
        
        layout.addLayout(buttons)
    
    def _create_info_tab(self) -> QWidget:
        """Crea tab informazioni generali"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        form = QFormLayout()
        
        # ID
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("es: finestra_2_ante")
        form.addRow("ID Modalità:*", self.id_input)
        
        # Nome
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("es: Finestra 2 Ante")
        form.addRow("Nome Visualizzato:*", self.name_input)
        
        # Categoria
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Finestre", "Porte", "Persiane", "Grate", 
            "Zanzariere", "Misure Generiche", "Custom"
        ])
        form.addRow("Categoria:", self.category_combo)
        
        # Icona
        icon_layout = QHBoxLayout()
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("mdi:window-closed")
        icon_layout.addWidget(self.icon_input)
        
        browse_icon_btn = QPushButton("🔍 Sfoglia")
        browse_icon_btn.clicked.connect(self._browse_icon)
        icon_layout.addWidget(browse_icon_btn)
        
        form.addRow("Icona:", icon_layout)
        
        # Descrizione
        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText("Descrizione della modalità...")
        self.description_text.setMaximumHeight(80)
        form.addRow("Descrizione:", self.description_text)
        
        layout.addLayout(form)
        layout.addStretch()
        
        return tab
    
    def _create_workflow_tab(self) -> QWidget:
        """Crea tab editor workflow"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Intestazione
        header = QLabel("Definisci i passi del workflow di misura:")
        header.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(header)
        
        # Lista passi
        self.steps_list = QListWidget()
        self.steps_list.setMaximumHeight(300)
        layout.addWidget(self.steps_list)
        
        # Pulsanti gestione passi
        steps_buttons = QHBoxLayout()
        
        add_step_btn = QPushButton("➕ Aggiungi Passo")
        add_step_btn.clicked.connect(self._add_workflow_step)
        steps_buttons.addWidget(add_step_btn)
        
        remove_step_btn = QPushButton("➖ Rimuovi Passo")
        remove_step_btn.clicked.connect(self._remove_workflow_step)
        steps_buttons.addWidget(remove_step_btn)
        
        steps_buttons.addStretch()
        
        layout.addLayout(steps_buttons)
        
        # Note workflow
        notes_label = QLabel("Note Workflow:")
        layout.addWidget(notes_label)
        
        self.workflow_notes = QTextEdit()
        self.workflow_notes.setPlaceholderText("Note aggiuntive sul workflow...")
        self.workflow_notes.setMaximumHeight(60)
        layout.addWidget(self.workflow_notes)
        
        layout.addStretch()
        
        return tab
    
    def _create_formula_tab(self) -> QWidget:
        """Crea tab editor formula"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Intestazione
        header = QLabel("Formula di calcolo:")
        header.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(header)
        
        # Editor formula
        self.formula_input = QTextEdit()
        self.formula_input.setPlaceholderText(
            "es: L + H + B - 5.0\n"
            "Variabili disponibili: L, H, D, B\n"
            "Operatori: +, -, *, /, (), sqrt(), abs()"
        )
        self.formula_input.setFont(QFont("Courier New", 11))
        layout.addWidget(self.formula_input)
        
        # Opzioni formula
        options_group = QGroupBox("Opzioni Visualizzazione")
        options_layout = QFormLayout()
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["mm", "cm", "m", "in", "ft"])
        options_layout.addRow("Unità:", self.unit_combo)
        
        self.decimals_spin = QSpinBox()
        self.decimals_spin.setRange(0, 4)
        self.decimals_spin.setValue(2)
        options_layout.addRow("Decimali:", self.decimals_spin)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Preview formula
        preview_group = QGroupBox("Anteprima Calcolo")
        preview_layout = QVBoxLayout()
        
        test_layout = QFormLayout()
        
        self.test_values = {}
        for var in ['L', 'H', 'D', 'B']:
            spin = QSpinBox()
            spin.setRange(0, 10000)
            spin.setValue(1000)
            spin.setSuffix(" mm")
            test_layout.addRow(f"{var}:", spin)
            self.test_values[var] = spin
        
        preview_layout.addLayout(test_layout)
        
        calc_btn = QPushButton("🔢 Calcola")
        calc_btn.clicked.connect(self._calculate_formula_preview)
        preview_layout.addWidget(calc_btn)
        
        self.formula_result = QLabel("Risultato: -")
        self.formula_result.setStyleSheet("""
            background: #1a1a2e; 
            color: #00ff88; 
            padding: 10px; 
            font-size: 16px; 
            font-weight: bold;
            border-radius: 5px;
        """)
        self.formula_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.formula_result)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        return tab
    
    def _create_bluetooth_tab(self) -> QWidget:
        """Crea tab configurazione Bluetooth"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toggle invio BT
        self.bt_send_check = QCheckBox("Invia risultato via Bluetooth")
        self.bt_send_check.setChecked(False)
        self.bt_send_check.stateChanged.connect(self._toggle_bt_options)
        layout.addWidget(self.bt_send_check)
        
        # Opzioni BT
        self.bt_options_group = QGroupBox("Opzioni Bluetooth")
        bt_layout = QFormLayout()
        
        self.bt_format_combo = QComboBox()
        self.bt_format_combo.addItems(["JSON", "CSV", "Testo Semplice", "Custom"])
        bt_layout.addRow("Formato:", self.bt_format_combo)
        
        self.bt_prefix_input = QLineEdit()
        self.bt_prefix_input.setPlaceholderText("es: RESULT:")
        bt_layout.addRow("Prefisso:", self.bt_prefix_input)
        
        self.bt_suffix_input = QLineEdit()
        self.bt_suffix_input.setPlaceholderText("es: \\r\\n")
        bt_layout.addRow("Suffisso:", self.bt_suffix_input)
        
        # Payload template
        payload_label = QLabel("Template Payload:")
        bt_layout.addRow(payload_label)
        
        self.bt_payload_template = QTextEdit()
        self.bt_payload_template.setPlaceholderText(
            '{"mode": "{mode_id}", "result": {result}, "unit": "{unit}"}'
        )
        self.bt_payload_template.setMaximumHeight(80)
        bt_layout.addRow(self.bt_payload_template)
        
        self.bt_options_group.setLayout(bt_layout)
        self.bt_options_group.setEnabled(False)
        layout.addWidget(self.bt_options_group)
        
        layout.addStretch()
        
        return tab
    
    def _toggle_bt_options(self, state):
        """Abilita/disabilita opzioni BT"""
        self.bt_options_group.setEnabled(bool(state))
    
    def _browse_icon(self):
        """Apre browser icone"""
        # TODO: Integrare con IconBrowserDialog
        QMessageBox.information(
            self,
            "Browser Icone",
            "Funzionalità browser icone non ancora implementata.\n"
            "Usa formato: mdi:icon-name o iconify:collection:icon"
        )
    
    def _add_workflow_step(self):
        """Aggiunge passo al workflow"""
        step_number = len(self.workflow_steps) + 1
        step_widget = WorkflowStepWidget(step_number, self)
        
        # Crea item lista
        item = QListWidgetItem(self.steps_list)
        item.setSizeHint(step_widget.sizeHint())
        self.steps_list.addItem(item)
        self.steps_list.setItemWidget(item, step_widget)
        
        self.workflow_steps.append(step_widget)
    
    def _remove_workflow_step(self):
        """Rimuove passo dal workflow"""
        current_row = self.steps_list.currentRow()
        if current_row >= 0:
            self.steps_list.takeItem(current_row)
            self.workflow_steps.pop(current_row)
            
            # Rinumera passi
            for i, step in enumerate(self.workflow_steps, 1):
                step.step_number = i
    
    def _calculate_formula_preview(self):
        """Calcola anteprima formula con parser sicuro"""
        formula = self.formula_input.toPlainText().strip()
        
        if not formula:
            self.formula_result.setText("Risultato: Inserisci una formula")
            return
        
        # Sostituisci variabili con valori test
        test_formula = formula
        for var, spin in self.test_values.items():
            test_formula = test_formula.replace(var, str(spin.value()))
        
        try:
            # Usa parser sicuro formula invece di eval
            from core.formula_parser import FormulaParser
            parser = FormulaParser()
            
            # Crea contesto con variabili
            context = {var: spin.value() for var, spin in self.test_values.items()}
            
            # Valuta formula in modo sicuro
            result = parser.evaluate(formula, context)
            
            # Formatta risultato
            decimals = self.decimals_spin.value()
            unit = self.unit_combo.currentText()
            self.formula_result.setText(f"Risultato: {result:.{decimals}f} {unit}")
        except Exception as e:
            self.formula_result.setText(f"Errore: {str(e)}")
    
    def _preview_mode(self):
        """Mostra anteprima modalità"""
        data = self._get_form_data()
        
        preview_text = f"""
=== ANTEPRIMA MODALITÀ ===

ID: {data['id']}
Nome: {data['name']}
Categoria: {data['category']}
Icona: {data['icon']}

Workflow ({len(data['workflow'])} passi):
"""
        
        for step in data['workflow']:
            preview_text += f"  {step['step']}. {step['variable']}: {step['description']} ({step['probe_type']})\n"
        
        preview_text += f"\nFormula: {data['formula']}\n"
        preview_text += f"Unità: {data['unit']}, Decimali: {data['decimals']}\n"
        preview_text += f"Invio BT: {'Sì' if data['bt_enabled'] else 'No'}\n"
        
        QMessageBox.information(self, "Anteprima Modalità", preview_text)
    
    def _save_mode(self):
        """Salva modalità"""
        data = self._get_form_data()
        
        # Validazione
        if not data['id']:
            QMessageBox.warning(self, "Validazione", "ID modalità obbligatorio")
            return
        
        if not data['name']:
            QMessageBox.warning(self, "Validazione", "Nome modalità obbligatorio")
            return
        
        if not data['workflow']:
            QMessageBox.warning(self, "Validazione", "Workflow vuoto: aggiungi almeno un passo")
            return
        
        self.mode_data = data
        self.accept()
    
    def _get_form_data(self) -> Dict[str, Any]:
        """Ottiene dati dal form"""
        return {
            'id': self.id_input.text(),
            'name': self.name_input.text(),
            'category': self.category_combo.currentText(),
            'icon': self.icon_input.text(),
            'description': self.description_text.toPlainText(),
            'workflow': [step.get_data() for step in self.workflow_steps],
            'workflow_notes': self.workflow_notes.toPlainText(),
            'formula': self.formula_input.toPlainText(),
            'unit': self.unit_combo.currentText(),
            'decimals': self.decimals_spin.value(),
            'bt_enabled': self.bt_send_check.isChecked(),
            'bt_format': self.bt_format_combo.currentText(),
            'bt_prefix': self.bt_prefix_input.text(),
            'bt_suffix': self.bt_suffix_input.text(),
            'bt_payload_template': self.bt_payload_template.toPlainText()
        }
    
    def _load_data(self):
        """Carica dati esistenti"""
        if not self.mode_data:
            return
        
        self.id_input.setText(self.mode_data.get('id', ''))
        self.name_input.setText(self.mode_data.get('name', ''))
        
        category = self.mode_data.get('category', '')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.icon_input.setText(self.mode_data.get('icon', ''))
        self.description_text.setPlainText(self.mode_data.get('description', ''))
        
        # Workflow
        for step_data in self.mode_data.get('workflow', []):
            self._add_workflow_step()
            self.workflow_steps[-1].set_data(step_data)
        
        self.workflow_notes.setPlainText(self.mode_data.get('workflow_notes', ''))
        
        # Formula
        self.formula_input.setPlainText(self.mode_data.get('formula', ''))
        
        unit = self.mode_data.get('unit', 'mm')
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        
        self.decimals_spin.setValue(self.mode_data.get('decimals', 2))
        
        # Bluetooth
        self.bt_send_check.setChecked(self.mode_data.get('bt_enabled', False))
        
        bt_format = self.mode_data.get('bt_format', 'JSON')
        index = self.bt_format_combo.findText(bt_format)
        if index >= 0:
            self.bt_format_combo.setCurrentIndex(index)
        
        self.bt_prefix_input.setText(self.mode_data.get('bt_prefix', ''))
        self.bt_suffix_input.setText(self.mode_data.get('bt_suffix', ''))
        self.bt_payload_template.setPlainText(self.mode_data.get('bt_payload_template', ''))
    
    def get_mode_data(self) -> Dict[str, Any]:
        """Ottiene dati modalità salvati"""
        return self.mode_data
