"""
Pannello proprietà elemento selezionato - Versione avanzata con tutte le proprietà
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QScrollArea,
    QGroupBox, QColorDialog, QComboBox, QCheckBox,
    QDoubleSpinBox, QSlider, QHBoxLayout, QTextEdit,
    QFontComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class PropertiesPanel(QWidget):
    """Pannello per editare proprietà elementi selezionati con funzionalità complete"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titolo
        title = QLabel("Proprietà")
        title.setProperty("heading", True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area per proprietà
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        
        scroll.setWidget(self.properties_widget)
        layout.addWidget(scroll)
        
        self.current_item = None
        
        self._show_empty_message()
    
    def _show_empty_message(self):
        """Mostra messaggio quando nessun elemento selezionato"""
        self._clear_layout()
        
        label = QLabel("Nessun elemento selezionato")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setProperty("text-secondary", True)
        self.properties_layout.addWidget(label)
        self.properties_layout.addStretch()
    
    def _clear_layout(self):
        """Pulisce layout proprietà"""
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_item(self, item):
        """Imposta elemento da mostrare"""
        self.current_item = item
        self._update_properties()
    
    def clear(self):
        """Pulisce pannello"""
        self.current_item = None
        self._show_empty_message()
    
    def _update_properties(self):
        """Aggiorna proprietà mostrate con tutte le opzioni avanzate"""
        self._clear_layout()
        
        if not self.current_item:
            self._show_empty_message()
            return
        
        # Ottieni valori correnti dall'elemento
        current_rect = self.current_item.rect()
        current_pos = self.current_item.pos()
        
        # 1. Gruppo Posizione e Dimensione
        pos_group = self._create_position_group(current_pos, current_rect)
        self.properties_layout.addWidget(pos_group)
        
        # 2. Gruppo Sfondo
        bg_group = self._create_background_group()
        self.properties_layout.addWidget(bg_group)
        
        # 3. Gruppo Bordo
        border_group = self._create_border_group()
        self.properties_layout.addWidget(border_group)
        
        # 4. Gruppo Effetti 3D
        effects_group = self._create_effects_group()
        self.properties_layout.addWidget(effects_group)
        
        # 5. Gruppo Testo
        text_group = self._create_text_group()
        self.properties_layout.addWidget(text_group)
        
        # 6. Gruppo Icona
        icon_group = self._create_icon_group()
        self.properties_layout.addWidget(icon_group)
        
        self.properties_layout.addStretch()
    
    def _create_position_group(self, pos, rect):
        """Crea gruppo proprietà posizione e dimensione"""
        group = QGroupBox("📐 Posizione e Dimensione")
        layout = QFormLayout()
        
        x_spin = QSpinBox()
        x_spin.setRange(0, 800)
        x_spin.setValue(int(pos.x()))
        x_spin.valueChanged.connect(lambda v: self._update_position('x', v))
        layout.addRow("X:", x_spin)
        
        y_spin = QSpinBox()
        y_spin.setRange(0, 480)
        y_spin.setValue(int(pos.y()))
        y_spin.valueChanged.connect(lambda v: self._update_position('y', v))
        layout.addRow("Y:", y_spin)
        
        width_spin = QSpinBox()
        width_spin.setRange(10, 800)
        width_spin.setValue(int(rect.width()))
        width_spin.valueChanged.connect(lambda v: self._update_size('width', v))
        layout.addRow("Larghezza:", width_spin)
        
        height_spin = QSpinBox()
        height_spin.setRange(10, 480)
        height_spin.setValue(int(rect.height()))
        height_spin.valueChanged.connect(lambda v: self._update_size('height', v))
        layout.addRow("Altezza:", height_spin)
        
        group.setLayout(layout)
        return group
    
    def _create_background_group(self):
        """Crea gruppo proprietà sfondo"""
        group = QGroupBox("🎨 Sfondo")
        layout = QFormLayout()
        
        # Colore
        color_layout = QHBoxLayout()
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(40, 25)
        self.bg_color_btn.setStyleSheet("background: #00ff88; border: 1px solid #333;")
        self.bg_color_btn.clicked.connect(lambda: self._choose_color('background'))
        color_layout.addWidget(self.bg_color_btn)
        color_layout.addWidget(QLabel("#00ff88"))
        color_layout.addStretch()
        layout.addRow("Colore:", color_layout)
        
        # Opacità
        opacity_spin = QDoubleSpinBox()
        opacity_spin.setRange(0.0, 1.0)
        opacity_spin.setSingleStep(0.1)
        opacity_spin.setValue(1.0)
        opacity_spin.valueChanged.connect(lambda v: self._update_opacity(v))
        layout.addRow("Opacità:", opacity_spin)
        
        # Gradiente
        gradient_check = QCheckBox("Abilita gradiente")
        gradient_check.stateChanged.connect(lambda s: self._toggle_gradient(s))
        layout.addRow("", gradient_check)
        
        gradient_combo = QComboBox()
        gradient_combo.addItems(["Verticale", "Orizzontale", "Diagonale", "Radiale"])
        gradient_combo.setEnabled(False)
        layout.addRow("Tipo:", gradient_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_border_group(self):
        """Crea gruppo proprietà bordo"""
        group = QGroupBox("🔲 Bordo")
        layout = QFormLayout()
        
        # Colore bordo
        border_color_layout = QHBoxLayout()
        self.border_color_btn = QPushButton()
        self.border_color_btn.setFixedSize(40, 25)
        self.border_color_btn.setStyleSheet("background: #333333; border: 1px solid #333;")
        self.border_color_btn.clicked.connect(lambda: self._choose_color('border'))
        border_color_layout.addWidget(self.border_color_btn)
        border_color_layout.addWidget(QLabel("#333333"))
        border_color_layout.addStretch()
        layout.addRow("Colore:", border_color_layout)
        
        # Spessore
        thickness_spin = QSpinBox()
        thickness_spin.setRange(0, 20)
        thickness_spin.setValue(2)
        thickness_spin.valueChanged.connect(lambda v: self._update_border_thickness(v))
        layout.addRow("Spessore:", thickness_spin)
        
        # Raggio smusso
        radius_spin = QSpinBox()
        radius_spin.setRange(0, 50)
        radius_spin.setValue(0)
        radius_spin.valueChanged.connect(lambda v: self._update_border_radius(v))
        layout.addRow("Raggio smusso:", radius_spin)
        
        # Stile
        style_combo = QComboBox()
        style_combo.addItems(["Solido", "Tratteggiato", "Punteggiato", "Doppio"])
        style_combo.currentTextChanged.connect(lambda s: self._update_border_style(s))
        layout.addRow("Stile:", style_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_effects_group(self):
        """Crea gruppo effetti 3D"""
        group = QGroupBox("✨ Effetti 3D")
        layout = QFormLayout()
        
        # Ombra
        shadow_check = QCheckBox("Abilita ombra")
        shadow_check.stateChanged.connect(lambda s: self._toggle_shadow(s))
        layout.addRow("", shadow_check)
        
        shadow_offset = QSpinBox()
        shadow_offset.setRange(0, 20)
        shadow_offset.setValue(5)
        shadow_offset.setEnabled(False)
        layout.addRow("Offset ombra:", shadow_offset)
        
        # Rilievo
        emboss_check = QCheckBox("Effetto rilievo")
        emboss_check.stateChanged.connect(lambda s: self._toggle_emboss(s))
        layout.addRow("", emboss_check)
        
        # Incassato
        inset_check = QCheckBox("Effetto incassato")
        inset_check.stateChanged.connect(lambda s: self._toggle_inset(s))
        layout.addRow("", inset_check)
        
        group.setLayout(layout)
        return group
    
    def _create_text_group(self):
        """Crea gruppo proprietà testo"""
        group = QGroupBox("📝 Testo")
        layout = QFormLayout()
        
        # Contenuto
        text_edit = QLineEdit()
        if hasattr(self.current_item, 'text_item'):
            text_edit.setText(self.current_item.text_item.toPlainText())
        text_edit.textChanged.connect(lambda t: self._update_text(t))
        layout.addRow("Contenuto:", text_edit)
        
        # Font
        font_combo = QFontComboBox()
        font_combo.currentFontChanged.connect(lambda f: self._update_font(f))
        layout.addRow("Font:", font_combo)
        
        # Dimensione
        size_spin = QSpinBox()
        size_spin.setRange(6, 72)
        size_spin.setValue(10)
        size_spin.valueChanged.connect(lambda s: self._update_font_size(s))
        layout.addRow("Dimensione:", size_spin)
        
        # Colore testo
        text_color_layout = QHBoxLayout()
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(40, 25)
        self.text_color_btn.setStyleSheet("background: #ffffff; border: 1px solid #333;")
        self.text_color_btn.clicked.connect(lambda: self._choose_color('text'))
        text_color_layout.addWidget(self.text_color_btn)
        text_color_layout.addWidget(QLabel("#ffffff"))
        text_color_layout.addStretch()
        layout.addRow("Colore:", text_color_layout)
        
        # Stile
        style_layout = QHBoxLayout()
        bold_check = QCheckBox("B")
        bold_check.setFixedWidth(40)
        bold_check.stateChanged.connect(lambda s: self._update_text_bold(s))
        style_layout.addWidget(bold_check)
        
        italic_check = QCheckBox("I")
        italic_check.setFixedWidth(40)
        italic_check.stateChanged.connect(lambda s: self._update_text_italic(s))
        style_layout.addWidget(italic_check)
        style_layout.addStretch()
        layout.addRow("Stile:", style_layout)
        
        # Allineamento
        align_combo = QComboBox()
        align_combo.addItems(["Sinistra", "Centro", "Destra", "Giustificato"])
        align_combo.currentTextChanged.connect(lambda a: self._update_text_alignment(a))
        layout.addRow("Allineamento:", align_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_icon_group(self):
        """Crea gruppo selettore icona"""
        group = QGroupBox("🎭 Icona")
        layout = QVBoxLayout()
        
        # Anteprima icona
        icon_preview = QLabel()
        icon_preview.setFixedSize(64, 64)
        icon_preview.setStyleSheet("""
            background: #1a1a2e;
            border: 2px solid #333;
            border-radius: 4px;
        """)
        icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_preview.setText("N/A")
        layout.addWidget(icon_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Pulsante seleziona icona
        select_icon_btn = QPushButton("📂 Seleziona icona...")
        select_icon_btn.clicked.connect(self._select_icon)
        layout.addWidget(select_icon_btn)
        
        group.setLayout(layout)
        return group
    
    # Metodi di callback per aggiornare le proprietà
    
    def _update_position(self, axis, value):
        """Aggiorna posizione elemento"""
        if self.current_item:
            pos = self.current_item.pos()
            if axis == 'x':
                self.current_item.setPos(value, pos.y())
            else:
                self.current_item.setPos(pos.x(), value)
    
    def _update_size(self, dimension, value):
        """Aggiorna dimensione elemento"""
        if self.current_item:
            rect = self.current_item.rect()
            if dimension == 'width':
                self.current_item.setRect(rect.x(), rect.y(), value, rect.height())
            else:
                self.current_item.setRect(rect.x(), rect.y(), rect.width(), value)
    
    def _choose_color(self, color_type):
        """Apri color picker per diversi tipi di colore"""
        initial_color = QColor("#00ff88")
        if color_type == 'border':
            initial_color = QColor("#333333")
        elif color_type == 'text':
            initial_color = QColor("#ffffff")
        
        color = QColorDialog.getColor(initial_color, self)
        if color.isValid():
            color_hex = color.name()
            if color_type == 'background' and self.current_item:
                from PyQt6.QtGui import QBrush
                self.current_item.setBrush(QBrush(color))
                self.bg_color_btn.setStyleSheet(f"background: {color_hex}; border: 1px solid #333;")
            elif color_type == 'border' and self.current_item:
                from PyQt6.QtGui import QPen
                pen = self.current_item.pen()
                pen.setColor(color)
                self.current_item.setPen(pen)
                self.border_color_btn.setStyleSheet(f"background: {color_hex}; border: 1px solid #333;")
            elif color_type == 'text' and self.current_item and hasattr(self.current_item, 'text_item'):
                self.current_item.text_item.setDefaultTextColor(color)
                self.text_color_btn.setStyleSheet(f"background: {color_hex}; border: 1px solid #333;")
    
    def _update_opacity(self, value):
        """Aggiorna opacità elemento"""
        if self.current_item:
            self.current_item.setOpacity(value)
    
    def _toggle_gradient(self, state):
        """Abilita/disabilita gradiente"""
        # TODO: Implementare gradiente
        pass
    
    def _update_border_thickness(self, value):
        """Aggiorna spessore bordo"""
        if self.current_item:
            from PyQt6.QtGui import QPen
            pen = self.current_item.pen()
            pen.setWidth(value)
            self.current_item.setPen(pen)
    
    def _update_border_radius(self, value):
        """Aggiorna raggio smusso"""
        # TODO: Implementare bordi smussati con QGraphicsPathItem
        pass
    
    def _update_border_style(self, style):
        """Aggiorna stile bordo"""
        if self.current_item:
            from PyQt6.QtGui import QPen
            from PyQt6.QtCore import Qt
            pen = self.current_item.pen()
            style_map = {
                "Solido": Qt.PenStyle.SolidLine,
                "Tratteggiato": Qt.PenStyle.DashLine,
                "Punteggiato": Qt.PenStyle.DotLine,
                "Doppio": Qt.PenStyle.SolidLine  # Approssimazione
            }
            pen.setStyle(style_map.get(style, Qt.PenStyle.SolidLine))
            self.current_item.setPen(pen)
    
    def _toggle_shadow(self, state):
        """Abilita/disabilita ombra"""
        # TODO: Implementare con QGraphicsDropShadowEffect
        pass
    
    def _toggle_emboss(self, state):
        """Abilita/disabilita effetto rilievo"""
        # TODO: Implementare effetto rilievo
        pass
    
    def _toggle_inset(self, state):
        """Abilita/disabilita effetto incassato"""
        # TODO: Implementare effetto incassato
        pass
    
    def _update_text(self, text):
        """Aggiorna contenuto testo"""
        if self.current_item and hasattr(self.current_item, 'text_item'):
            self.current_item.text_item.setPlainText(text)
    
    def _update_font(self, font):
        """Aggiorna font testo"""
        if self.current_item and hasattr(self.current_item, 'text_item'):
            current_font = self.current_item.text_item.font()
            current_font.setFamily(font.family())
            self.current_item.text_item.setFont(current_font)
    
    def _update_font_size(self, size):
        """Aggiorna dimensione font"""
        if self.current_item and hasattr(self.current_item, 'text_item'):
            font = self.current_item.text_item.font()
            font.setPointSize(size)
            self.current_item.text_item.setFont(font)
    
    def _update_text_bold(self, state):
        """Aggiorna grassetto"""
        if self.current_item and hasattr(self.current_item, 'text_item'):
            font = self.current_item.text_item.font()
            font.setBold(state == Qt.CheckState.Checked)
            self.current_item.text_item.setFont(font)
    
    def _update_text_italic(self, state):
        """Aggiorna corsivo"""
        if self.current_item and hasattr(self.current_item, 'text_item'):
            font = self.current_item.text_item.font()
            font.setItalic(state == Qt.CheckState.Checked)
            self.current_item.text_item.setFont(font)
    
    def _update_text_alignment(self, alignment):
        """Aggiorna allineamento testo"""
        # TODO: Implementare allineamento
        pass
    
    def _select_icon(self):
        """Apri browser icone"""
        from .icon_browser_dialog import IconBrowserDialog
        dialog = IconBrowserDialog(self)
        if dialog.exec():
            selected_icon = dialog.get_selected_icon()
            # TODO: Applicare icona all'elemento
            pass
