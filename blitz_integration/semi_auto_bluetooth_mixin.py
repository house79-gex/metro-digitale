"""
Mixin per integrare Bluetooth nel software troncatrice BLITZ

Questo mixin aggiunge funzionalità Bluetooth alla pagina Semi-Auto
della troncatrice, permettendo di ricevere misure dal Metro Digitale
e triggerare automaticamente il taglio.

Utilizzo:
    class SemiAutoPage(SemiAutoBluetoothMixin, BasePage):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.init_bluetooth()

Autore: Metro Digitale Project
Licenza: MIT
"""

import threading
import logging
from typing import Dict, Any, Optional
from bluetooth_receiver import BluetoothCalibroReceiver

logger = logging.getLogger(__name__)


class SemiAutoBluetoothMixin:
    """
    Mixin per aggiungere supporto Bluetooth alla SemiAutoPage.
    
    Fornisce:
    - Ricezione misure via Bluetooth
    - Aggiornamento automatico campo misura
    - Trigger automatico pulsante START
    - Gestione connessione in background
    """
    
    def init_bluetooth(self):
        """
        Inizializza il sistema Bluetooth.
        
        Chiamare nel __init__ della classe che eredita il mixin.
        """
        self.bt_receiver: Optional[BluetoothCalibroReceiver] = None
        self.bt_thread: Optional[threading.Thread] = None
        self.bt_enabled = True
        
        if self.bt_enabled:
            self._start_bluetooth_receiver()
    
    def _start_bluetooth_receiver(self):
        """Avvia il receiver Bluetooth in un thread separato."""
        try:
            self.bt_receiver = BluetoothCalibroReceiver()
            self.bt_receiver.on_misura_received = self._on_bluetooth_misura_received
            
            # Avvia in thread separato per non bloccare UI
            self.bt_thread = threading.Thread(
                target=self.bt_receiver.start,
                daemon=True,
                name="BluetoothReceiver"
            )
            self.bt_thread.start()
            
            logger.info("Bluetooth receiver avviato")
            self._update_bt_status("In attesa connessione...")
            
        except Exception as e:
            logger.error(f"Errore avvio Bluetooth: {e}")
            self._update_bt_status("Errore Bluetooth")
    
    def _on_bluetooth_misura_received(self, data: Dict[str, Any]):
        """
        Callback chiamata quando viene ricevuta una misura via Bluetooth.
        
        Args:
            data: Dizionario con i dati della misura
        """
        try:
            logger.info(f"Misura Bluetooth ricevuta: {data}")
            
            # Verifica tipo misura
            msg_type = data.get('type', 'fermavetro')
            if msg_type not in ['fermavetro', 'rilievo_speciale']:
                logger.warning(f"Tipo misura non supportato: {msg_type}")
                return
            
            misura_mm = data.get('misura_mm')
            auto_start = data.get('auto_start', False)
            num_pezzi = data.get('num_pezzi', 1)
            
            if misura_mm is None:
                logger.warning("Misura non valida")
                return
            
            # Aggiorna UI (deve essere chiamato nel thread principale)
            self._schedule_ui_update(misura_mm, auto_start, num_pezzi)
            
        except Exception as e:
            logger.error(f"Errore gestione misura Bluetooth: {e}")
    
    def _schedule_ui_update(self, misura_mm: float, auto_start: bool, num_pezzi: int = 1):
        """
        Pianifica l'aggiornamento dell'UI nel thread principale.
        
        Args:
            misura_mm: Misura ricevuta in millimetri
            auto_start: Se True, trigge automaticamente START
            num_pezzi: Numero di pezzi da tagliare
        """
        # Usa after() di tkinter per eseguire nel thread principale
        if hasattr(self, 'after'):
            self.after(0, lambda: self._update_misura_and_start(misura_mm, auto_start, num_pezzi))
        else:
            # Fallback se after() non disponibile
            self._update_misura_and_start(misura_mm, auto_start, num_pezzi)
    
    def _update_misura_and_start(self, misura_mm: float, auto_start: bool, num_pezzi: int = 1):
        """
        Aggiorna il campo misura e opzionalmente avvia il taglio.
        
        Args:
            misura_mm: Misura da inserire
            auto_start: Se True, preme il pulsante START
            num_pezzi: Numero di pezzi da tagliare
        """
        try:
            # Aggiorna campo misura
            # NOTA: Adattare i nomi dei widget alla tua implementazione
            if hasattr(self, 'entry_misura'):
                self.entry_misura.delete(0, 'end')
                self.entry_misura.insert(0, f"{misura_mm:.1f}")
                logger.info(f"Misura aggiornata: {misura_mm:.1f} mm")
            
            # Popola contapezzi se presente e num_pezzi > 1
            if hasattr(self, 'spin_count') and num_pezzi > 1:
                self.spin_count.delete(0, 'end')
                self.spin_count.insert(0, str(num_pezzi))
                logger.info(f"Contapezzi aggiornato: {num_pezzi} pz")
            
            # Aggiorna status
            status_msg = f"Ricevuto: {misura_mm:.1f} mm"
            if num_pezzi > 1:
                status_msg += f" × {num_pezzi} pz"
            self._update_bt_status(status_msg)
            
            # Trigger START se richiesto
            if auto_start:
                self._trigger_start_button()
            
        except Exception as e:
            logger.error(f"Errore aggiornamento UI: {e}")
    
    def _trigger_start_button(self):
        """
        Simula la pressione del pulsante START.
        
        NOTA: Implementare secondo la tua architettura software.
        Potrebbe essere necessario chiamare direttamente il metodo
        associato al pulsante START o simulare un evento click.
        """
        try:
            # Metodo 1: Chiama direttamente il metodo
            if hasattr(self, 'on_start_clicked'):
                logger.info("Trigger START automatico...")
                self.on_start_clicked()
            
            # Metodo 2: Simula click sul pulsante
            elif hasattr(self, 'btn_start'):
                self.btn_start.invoke()
            
            # Metodo 3: Genera evento
            elif hasattr(self, 'btn_start'):
                self.btn_start.event_generate('<Button-1>')
            
            else:
                logger.warning("Metodo START non trovato, implementare _trigger_start_button()")
            
        except Exception as e:
            logger.error(f"Errore trigger START: {e}")
    
    def _update_bt_status(self, status: str):
        """
        Aggiorna il widget di status Bluetooth.
        
        Args:
            status: Testo da visualizzare
        """
        try:
            # NOTA: Adattare al tuo widget di status
            if hasattr(self, 'label_bt_status'):
                self.label_bt_status.config(text=f"BT: {status}")
        except Exception as e:
            logger.error(f"Errore aggiornamento status: {e}")
    
    def stop_bluetooth(self):
        """
        Ferma il receiver Bluetooth.
        
        Chiamare quando si chiude la pagina o l'applicazione.
        """
        if self.bt_receiver:
            logger.info("Stop Bluetooth receiver...")
            self.bt_receiver.stop()
            
        if self.bt_thread and self.bt_thread.is_alive():
            self.bt_thread.join(timeout=2.0)
    
    def get_bluetooth_status(self) -> Dict[str, Any]:
        """
        Restituisce lo stato della connessione Bluetooth.
        
        Returns:
            Dizionario con informazioni sullo stato
        """
        if not self.bt_receiver:
            return {
                'enabled': False,
                'connected': False,
                'device': None
            }
        
        return {
            'enabled': self.bt_enabled,
            'connected': self.bt_receiver.is_connected,
            'device': self.bt_receiver.device_name if self.bt_receiver.is_connected else None
        }


# Esempio di utilizzo completo
"""
# Nel file semi_auto.py della troncatrice BLITZ:

from tkinter import *
from tkinter import ttk
from blitz_integration.semi_auto_bluetooth_mixin import SemiAutoBluetoothMixin

class SemiAutoPage(SemiAutoBluetoothMixin, ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # UI esistente
        self.entry_misura = ttk.Entry(self)
        self.btn_start = ttk.Button(self, text="START", command=self.on_start_clicked)
        self.label_bt_status = ttk.Label(self, text="BT: Non inizializzato")
        
        # Layout...
        
        # Inizializza Bluetooth (IMPORTANTE!)
        self.init_bluetooth()
    
    def on_start_clicked(self):
        # Logica esistente per avviare il taglio
        misura = float(self.entry_misura.get())
        print(f"Avvio taglio: {misura} mm")
        # ... resto del codice ...
    
    def destroy(self):
        # Ferma Bluetooth prima di distruggere
        self.stop_bluetooth()
        super().destroy()
"""
