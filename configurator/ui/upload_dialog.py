"""
Dialog upload configurazione su ESP32
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QProgressBar, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.esp_uploader import ESPUploader
from core.config_model import ProgettoConfigurazione


class UploadThread(QThread):
    """Thread per upload configurazione"""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)
    log_message = pyqtSignal(str)
    
    def __init__(self, uploader, config):
        super().__init__()
        self.uploader = uploader
        self.config = config
    
    def run(self):
        """Esegue upload"""
        self.log_message.emit("Inizio upload configurazione...")
        
        try:
            success = self.uploader.upload_config(
                self.config,
                progress_callback=lambda p: self.progress.emit(p)
            )
            
            if success:
                self.log_message.emit("✓ Upload completato con successo")
            else:
                self.log_message.emit("✗ Upload fallito")
            
            self.finished.emit(success)
            
        except Exception as e:
            self.log_message.emit(f"✗ Errore: {e}")
            self.finished.emit(False)


class UploadDialog(QDialog):
    """Dialog per upload su ESP32"""
    
    def __init__(self, project: ProgettoConfigurazione, parent=None):
        super().__init__(parent)
        
        self.project = project
        self.uploader = ESPUploader()
        self.upload_thread = None
        
        self.setWindowTitle("Upload ESP32")
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Selezione porta
        port_group = QGroupBox("Connessione")
        port_layout = QHBoxLayout()
        
        port_layout.addWidget(QLabel("Porta:"))
        
        self.port_combo = QComboBox()
        port_layout.addWidget(self.port_combo)
        
        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedWidth(40)
        refresh_btn.setToolTip("Aggiorna lista porte")
        refresh_btn.clicked.connect(self._refresh_ports)
        port_layout.addWidget(refresh_btn)
        
        self.connect_btn = QPushButton("Connetti")
        self.connect_btn.clicked.connect(self._on_connect)
        port_layout.addWidget(self.connect_btn)
        
        self.status_label = QLabel("⚫ Non connesso")
        port_layout.addWidget(self.status_label)
        
        port_group.setLayout(port_layout)
        layout.addWidget(port_group)
        
        # Info configurazione
        info_group = QGroupBox("Contenuto")
        info_layout = QVBoxLayout()
        
        info_layout.addWidget(QLabel(f"Progetto: {project.nome}"))
        info_layout.addWidget(QLabel(f"Menu: {len(project.menus)}"))
        info_layout.addWidget(QLabel(f"Tipologie: {len(project.tipologie)}"))
        info_layout.addWidget(QLabel(f"Astine: {len(project.astine)}"))
        info_layout.addWidget(QLabel(f"Fermavetri: {len(project.fermavetri)}"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log
        log_label = QLabel("Log operazioni:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.close_btn = QPushButton("Chiudi")
        self.close_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.close_btn)
        
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setProperty("primary", True)
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self._on_upload)
        buttons_layout.addWidget(self.upload_btn)
        
        layout.addLayout(buttons_layout)
        
        # Inizializza
        self._refresh_ports()
    
    def _refresh_ports(self):
        """Aggiorna lista porte disponibili"""
        self.port_combo.clear()
        devices = self.uploader.find_devices()
        
        if not devices:
            self.port_combo.addItem("Nessun dispositivo trovato")
            self._log("Nessun dispositivo ESP32 trovato")
        else:
            for port, desc in devices:
                self.port_combo.addItem(f"{port} - {desc}", port)
            self._log(f"Trovati {len(devices)} dispositivi")
    
    def _on_connect(self):
        """Connetti a dispositivo"""
        if self.uploader.is_connected():
            # Disconnetti
            self.uploader.disconnect()
            self.status_label.setText("⚫ Non connesso")
            self.connect_btn.setText("Connetti")
            self.upload_btn.setEnabled(False)
            self._log("Disconnesso")
        else:
            # Connetti
            port = self.port_combo.currentData()
            if not port:
                return
            
            if self.uploader.connect(port):
                self.status_label.setText("🟢 Connesso")
                self.connect_btn.setText("Disconnetti")
                self.upload_btn.setEnabled(True)
                self._log(f"Connesso a {port}")
                
                # Ottieni info dispositivo
                info = self.uploader.get_device_info()
                if info:
                    self._log(f"Dispositivo: {info}")
            else:
                self.status_label.setText("🔴 Errore connessione")
                self._log("Errore di connessione")
    
    def _on_upload(self):
        """Avvia upload"""
        if not self.uploader.is_connected():
            return
        
        self.upload_btn.setEnabled(False)
        self.connect_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Avvia thread upload
        self.upload_thread = UploadThread(self.uploader, self.project)
        self.upload_thread.progress.connect(self.progress_bar.setValue)
        self.upload_thread.log_message.connect(self._log)
        self.upload_thread.finished.connect(self._on_upload_finished)
        self.upload_thread.start()
    
    def _on_upload_finished(self, success: bool):
        """Upload completato"""
        self.upload_btn.setEnabled(True)
        self.connect_btn.setEnabled(True)
        
        if success:
            self._log("Upload completato!")
        else:
            self._log("Upload fallito")
    
    def _log(self, message: str):
        """Aggiunge messaggio al log"""
        self.log_text.append(message)
    
    def closeEvent(self, event):
        """Gestisce chiusura dialog"""
        if self.uploader.is_connected():
            self.uploader.disconnect()
        event.accept()
