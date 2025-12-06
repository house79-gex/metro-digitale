"""
Modalità Simulazione/Preview Interattiva
Simula il funzionamento reale del Metro Digitale con interazioni
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
import random
from typing import Optional


class SimulatedDisplay(QFrame):
    """Widget che simula il display del Metro Digitale"""
    
    button_clicked = pyqtSignal(str)  # Emette il nome del pulsante cliccato
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(800, 480)
        self.setMaximumSize(800, 480)
        self.setStyleSheet("background: #16213e; border: 3px solid #00ff88;")
        
        # Stato simulazione
        self.current_mode = "HOME"  # HOME, CALIBRO, VETRI, ASTINE, TIPOLOGIE
        self.measurement_value = 0.0
        self.is_measuring = False
        self.is_hold = False
        
        # Timer per aggiornamento misure simulate
        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self._update_measurement)
        self.measurement_timer.setInterval(100)  # Aggiorna ogni 100ms
        
        # Pulsanti simulati (aree cliccabili)
        self.buttons = []
        self._setup_mode()
    
    def _setup_mode(self):
        """Configura pulsanti per modalità corrente"""
        self.buttons.clear()
        
        if self.current_mode == "HOME":
            self.buttons = [
                {"rect": QRectF(50, 120, 150, 50), "text": "Calibro", "action": "goto_calibro"},
                {"rect": QRectF(220, 120, 150, 50), "text": "Vetri", "action": "goto_vetri"},
                {"rect": QRectF(390, 120, 150, 50), "text": "Astine", "action": "goto_astine"},
                {"rect": QRectF(560, 120, 150, 50), "text": "Tipologie", "action": "goto_tipologie"},
                {"rect": QRectF(300, 380, 200, 60), "text": "Impostazioni", "action": "goto_settings"},
            ]
        elif self.current_mode == "CALIBRO":
            self.buttons = [
                {"rect": QRectF(50, 380, 120, 50), "text": "Zero", "action": "zero"},
                {"rect": QRectF(190, 380, 120, 50), "text": "Hold", "action": "hold"},
                {"rect": QRectF(330, 380, 120, 50), "text": "Misura", "action": "measure"},
                {"rect": QRectF(470, 380, 120, 50), "text": "Salva", "action": "save"},
                {"rect": QRectF(610, 380, 120, 50), "text": "Indietro", "action": "goto_home"},
            ]
        elif self.current_mode == "VETRI":
            self.buttons = [
                {"rect": QRectF(50, 300, 150, 50), "text": "Misura L", "action": "measure_width"},
                {"rect": QRectF(250, 300, 150, 50), "text": "Misura A", "action": "measure_height"},
                {"rect": QRectF(450, 300, 150, 50), "text": "Salva", "action": "save"},
                {"rect": QRectF(620, 380, 120, 50), "text": "Indietro", "action": "goto_home"},
            ]
        
        self.update()
    
    def paintEvent(self, event):
        """Disegna interfaccia simulata"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.current_mode == "HOME":
            self._draw_home_screen(painter)
        elif self.current_mode == "CALIBRO":
            self._draw_calibro_screen(painter)
        elif self.current_mode == "VETRI":
            self._draw_vetri_screen(painter)
        else:
            self._draw_placeholder(painter)
    
    def _draw_home_screen(self, painter: QPainter):
        """Disegna schermata home"""
        # Titolo
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 40, 800, 60, Qt.AlignmentFlag.AlignCenter, "Metro Digitale")
        
        # Sottotitolo
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(QColor("#888888"))
        painter.drawText(0, 80, 800, 30, Qt.AlignmentFlag.AlignCenter, "Seleziona modalità operativa")
        
        # Pulsanti
        for btn in self.buttons:
            self._draw_button(painter, btn)
    
    def _draw_calibro_screen(self, painter: QPainter):
        """Disegna schermata calibro"""
        # Titolo
        painter.setPen(QColor("#00ff88"))
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 30, 800, 40, Qt.AlignmentFlag.AlignCenter, "CALIBRO DIGITALE")
        
        # Display misura grande
        display_rect = QRectF(100, 100, 600, 150)
        painter.setBrush(QColor("#0088ff"))
        painter.setPen(QPen(QColor("#333333"), 2))
        painter.drawRoundedRect(display_rect, 5, 5)
        
        # Valore misura
        painter.setPen(QColor("#000000"))
        font.setPointSize(48)
        font.setBold(True)
        painter.setFont(font)
        value_text = f"{self.measurement_value:.2f} mm"
        if self.is_hold:
            value_text += " [HOLD]"
        painter.drawText(display_rect, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Indicatore misura attiva
        if self.is_measuring:
            painter.setPen(QColor("#ff8800"))
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(110, 270, "● MISURA IN CORSO")
        
        # Statistiche
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(100, 300, f"Min: {self.measurement_value - 5.23:.2f} mm")
        painter.drawText(300, 300, f"Max: {self.measurement_value + 3.45:.2f} mm")
        painter.drawText(500, 300, f"Conteggio: {random.randint(15, 45)}")
        
        # Pulsanti
        for btn in self.buttons:
            self._draw_button(painter, btn)
    
    def _draw_vetri_screen(self, painter: QPainter):
        """Disegna schermata vetri"""
        # Titolo
        painter.setPen(QColor("#00ff88"))
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 30, 800, 40, Qt.AlignmentFlag.AlignCenter, "MISURA VETRI (L x A)")
        
        # Due display per larghezza e altezza
        # Larghezza
        painter.setPen(QColor("#ffffff"))
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(100, 90, "Larghezza:")
        
        display_l = QRectF(100, 100, 280, 80)
        painter.setBrush(QColor("#0088ff"))
        painter.setPen(QPen(QColor("#333333"), 2))
        painter.drawRect(display_l)
        
        painter.setPen(QColor("#000000"))
        font.setPointSize(28)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(display_l, Qt.AlignmentFlag.AlignCenter, f"{self.measurement_value:.1f} mm")
        
        # Altezza
        painter.setPen(QColor("#ffffff"))
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(420, 90, "Altezza:")
        
        display_a = QRectF(420, 100, 280, 80)
        painter.setBrush(QColor("#0088ff"))
        painter.setPen(QPen(QColor("#333333"), 2))
        painter.drawRect(display_a)
        
        painter.setPen(QColor("#000000"))
        font.setPointSize(28)
        font.setBold(True)
        painter.setFont(font)
        height_value = self.measurement_value * 1.3  # Simula valore diverso
        painter.drawText(display_a, Qt.AlignmentFlag.AlignCenter, f"{height_value:.1f} mm")
        
        # Risultato
        painter.setPen(QColor("#ffffff"))
        font.setPointSize(14)
        painter.setFont(font)
        result = f"{self.measurement_value:.1f} x {height_value:.1f} mm"
        painter.drawText(0, 220, 800, 40, Qt.AlignmentFlag.AlignCenter, result)
        
        # Pulsanti
        for btn in self.buttons:
            self._draw_button(painter, btn)
    
    def _draw_placeholder(self, painter: QPainter):
        """Disegna placeholder per altre modalità"""
        painter.setPen(QColor("#888888"))
        font = QFont("Arial", 16)
        painter.setFont(font)
        painter.drawText(0, 0, 800, 480, Qt.AlignmentFlag.AlignCenter, 
                        f"Modalità {self.current_mode}\n(In sviluppo)")
    
    def _draw_button(self, painter: QPainter, btn: dict):
        """Disegna un pulsante simulato"""
        rect = btn["rect"]
        text = btn["text"]
        
        # Sfondo pulsante
        painter.setBrush(QColor("#00ff88"))
        painter.setPen(QPen(QColor("#333333"), 2))
        painter.drawRoundedRect(rect, 5, 5)
        
        # Testo
        painter.setPen(QColor("#000000"))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def mousePressEvent(self, event):
        """Gestisce click sui pulsanti simulati"""
        pos = event.pos()
        
        for btn in self.buttons:
            if btn["rect"].contains(pos.x(), pos.y()):
                self._handle_button_action(btn["action"])
                break
    
    def _handle_button_action(self, action: str):
        """Gestisce azione pulsante"""
        if action.startswith("goto_"):
            mode = action.replace("goto_", "").upper()
            self.current_mode = mode
            self._setup_mode()
            if mode == "HOME":
                self.stop_measurement()
        elif action == "zero":
            self.measurement_value = 0.0
            self.update()
        elif action == "hold":
            self.is_hold = not self.is_hold
            if self.is_hold:
                self.stop_measurement()
            self.update()
        elif action in ["measure", "measure_width", "measure_height"]:
            if not self.is_hold:
                self.start_measurement()
        elif action == "save":
            # Simula salvataggio
            pass
        
        self.button_clicked.emit(action)
    
    def start_measurement(self):
        """Avvia simulazione misura"""
        self.is_measuring = True
        self.measurement_timer.start()
    
    def stop_measurement(self):
        """Ferma simulazione misura"""
        self.is_measuring = False
        self.measurement_timer.stop()
    
    def _update_measurement(self):
        """Aggiorna valore misurato simulato"""
        if self.is_measuring and not self.is_hold:
            # Simula variazione casuale
            change = random.uniform(-0.5, 0.5)
            self.measurement_value += change
            
            # Mantieni in range ragionevole
            self.measurement_value = max(0.0, min(3000.0, self.measurement_value))
            
            self.update()


class SimulationDialog(QDialog):
    """Dialog per modalità simulazione interattiva"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("🎮 Simulazione Interattiva - Metro Digitale")
        self.resize(900, 650)
        
        self._init_ui()
    
    def _init_ui(self):
        """Inizializza interfaccia"""
        layout = QVBoxLayout(self)
        
        # Titolo
        title = QLabel("🎮 Modalità Simulazione Interattiva")
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
        
        # Istruzioni
        instructions = QLabel(
            "💡 Clicca sui pulsanti per simulare l'uso reale del dispositivo. "
            "I valori di misura cambiano in tempo reale."
        )
        instructions.setStyleSheet("color: #888; padding: 5px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Display simulato
        self.simulated_display = SimulatedDisplay()
        self.simulated_display.button_clicked.connect(self._on_button_action)
        layout.addWidget(self.simulated_display, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Log azioni
        self.log_label = QLabel("Azioni: Pronto per simulazione")
        self.log_label.setStyleSheet("""
            background: #1a1a2e;
            color: #00ff88;
            padding: 8px;
            border: 1px solid #00ff88;
            border-radius: 3px;
            font-family: monospace;
        """)
        layout.addWidget(self.log_label)
        
        # Pulsanti controllo
        control_layout = QHBoxLayout()
        
        reset_btn = QPushButton("🔄 Reset Simulazione")
        reset_btn.clicked.connect(self._reset_simulation)
        control_layout.addWidget(reset_btn)
        
        control_layout.addStretch()
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        control_layout.addWidget(close_btn)
        
        layout.addLayout(control_layout)
    
    def _on_button_action(self, action: str):
        """Gestisce azione dal display simulato"""
        action_names = {
            "goto_home": "Torna a Home",
            "goto_calibro": "Apri Calibro",
            "goto_vetri": "Apri Misura Vetri",
            "goto_astine": "Apri Astine",
            "goto_tipologie": "Apri Tipologie",
            "goto_settings": "Apri Impostazioni",
            "zero": "Azzera misura",
            "hold": "Hold/Rilascia",
            "measure": "Avvia misura",
            "measure_width": "Misura larghezza",
            "measure_height": "Misura altezza",
            "save": "Salva misura",
        }
        
        action_text = action_names.get(action, action)
        self.log_label.setText(f"Azione: {action_text}")
    
    def _reset_simulation(self):
        """Reset simulazione allo stato iniziale"""
        self.simulated_display.current_mode = "HOME"
        self.simulated_display.measurement_value = 0.0
        self.simulated_display.is_measuring = False
        self.simulated_display.is_hold = False
        self.simulated_display.stop_measurement()
        self.simulated_display._setup_mode()
        self.log_label.setText("Azioni: Simulazione resettata")
