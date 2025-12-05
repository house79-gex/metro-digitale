"""
Editor formule con validazione e test
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QFormLayout, QDoubleSpinBox, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

from core.formula_parser import FormulaParser


class FormulaEditor(QWidget):
    """Editor per formule matematiche con test"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parser = FormulaParser()
        
        layout = QVBoxLayout(self)
        
        # Gruppo formula
        formula_group = QGroupBox("Formula")
        formula_layout = QVBoxLayout()
        
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("Es: (L + 6) / 2")
        self.formula_input.textChanged.connect(self._on_formula_changed)
        formula_layout.addWidget(self.formula_input)
        
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        formula_layout.addWidget(self.validation_label)
        
        formula_group.setLayout(formula_layout)
        layout.addWidget(formula_group)
        
        # Gruppo variabili disponibili
        var_group = QGroupBox("Variabili Disponibili")
        var_layout = QVBoxLayout()
        
        self.var_list = QListWidget()
        self.var_list.addItems(["L", "H", "B", "S"])
        self.var_list.itemDoubleClicked.connect(self._on_var_double_click)
        var_layout.addWidget(self.var_list)
        
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)
        
        # Gruppo test
        test_group = QGroupBox("Test Formula")
        test_layout = QFormLayout()
        
        self.test_inputs = {}
        for var in ["L", "H", "B", "S"]:
            spin = QDoubleSpinBox()
            spin.setRange(0, 10000)
            spin.setValue(1000 if var in ["L", "H"] else 50)
            spin.valueChanged.connect(self._on_test_values_changed)
            self.test_inputs[var] = spin
            test_layout.addRow(f"{var}:", spin)
        
        self.result_label = QLabel("Risultato: -")
        self.result_label.setProperty("heading", True)
        test_layout.addRow(self.result_label)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addStretch()
    
    def _on_formula_changed(self, text):
        """Validazione real-time formula"""
        if not text.strip():
            self.validation_label.setText("")
            self.result_label.setText("Risultato: -")
            return
        
        # Valida formula
        variables = ["L", "H", "B", "S"]
        valid, message = self.parser.validate(text, variables)
        
        if valid:
            self.validation_label.setText("✓ Formula valida")
            self.validation_label.setProperty("error", False)
            self.validation_label.style().polish(self.validation_label)
            
            # Testa con valori correnti
            self._update_test_result()
        else:
            self.validation_label.setText(f"✗ {message}")
            self.validation_label.setProperty("error", True)
            self.validation_label.style().polish(self.validation_label)
            self.result_label.setText("Risultato: -")
    
    def _on_test_values_changed(self):
        """Aggiorna risultato test"""
        self._update_test_result()
    
    def _update_test_result(self):
        """Calcola e mostra risultato"""
        formula = self.formula_input.text().strip()
        if not formula:
            return
        
        # Raccogli valori test
        test_values = {
            var: spin.value() 
            for var, spin in self.test_inputs.items()
        }
        
        # Calcola risultato
        success, result = self.parser.test_formula(formula, test_values)
        
        if success:
            self.result_label.setText(f"Risultato: {result:.2f}")
            self.result_label.setProperty("error", False)
        else:
            self.result_label.setText(f"Errore: {result}")
            self.result_label.setProperty("error", True)
        
        self.result_label.style().polish(self.result_label)
    
    def _on_var_double_click(self, item):
        """Inserisce variabile nella formula"""
        var_name = item.text()
        current_text = self.formula_input.text()
        cursor_pos = self.formula_input.cursorPosition()
        
        new_text = current_text[:cursor_pos] + var_name + current_text[cursor_pos:]
        self.formula_input.setText(new_text)
        self.formula_input.setCursorPosition(cursor_pos + len(var_name))
        self.formula_input.setFocus()
    
    def set_formula(self, formula: str):
        """Imposta formula da editare"""
        self.formula_input.setText(formula)
    
    def get_formula(self) -> str:
        """Ottiene formula corrente"""
        return self.formula_input.text().strip()
