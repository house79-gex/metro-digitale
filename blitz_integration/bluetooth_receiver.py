"""
Bluetooth Calibro Receiver per Troncatrice BLITZ

Riceve misure dal Metro Digitale via Bluetooth BLE e le rende disponibili
per l'integrazione con il software della troncatrice.

Autore: Metro Digitale Project
Licenza: MIT
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from bleak import BleakClient, BleakScanner

# Configurazione
SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
CHAR_TX_UUID = "12345678-1234-1234-1234-123456789abd"
CHAR_RX_UUID = "12345678-1234-1234-1234-123456789abe"
DEVICE_NAME_FILTER = "Metro-Digitale"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BluetoothCalibroReceiver:
    """
    Receiver Bluetooth per Metro Digitale.
    
    Gestisce la connessione BLE, riceve misure e notifica tramite callback.
    """

    def __init__(self, device_name: str = DEVICE_NAME_FILTER):
        """
        Inizializza il receiver.
        
        Args:
            device_name: Nome (o parte del nome) del dispositivo da cercare
        """
        self.device_name = device_name
        self.client: Optional[BleakClient] = None
        self.is_connected = False
        self.on_misura_received: Optional[Callable[[Dict[str, Any]], None]] = None
        self._running = False
        
    async def _find_device(self):
        """Cerca il dispositivo Metro Digitale."""
        logger.info(f"Ricerca dispositivo {self.device_name}...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        for device in devices:
            if self.device_name in (device.name or ""):
                logger.info(f"Dispositivo trovato: {device.name} ({device.address})")
                return device
        
        logger.warning(f"Dispositivo {self.device_name} non trovato")
        return None
    
    def _notification_handler(self, sender, data: bytearray):
        """
        Handler per notifiche BLE.
        
        Args:
            sender: Caratteristica che ha inviato i dati
            data: Dati ricevuti (bytearray)
        """
        try:
            # Decodifica JSON
            json_str = data.decode('utf-8')
            logger.debug(f"Dati ricevuti: {json_str}")
            
            payload = json.loads(json_str)
            
            # Valida payload
            if not self._validate_payload(payload):
                logger.warning(f"Payload non valido: {payload}")
                return
            
            # Chiama callback se configurato
            if self.on_misura_received:
                self.on_misura_received(payload)
            else:
                logger.info(f"Misura ricevuta: {payload}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Errore parsing JSON: {e}")
        except Exception as e:
            logger.error(f"Errore handler notifiche: {e}")
    
    def _validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Valida il payload ricevuto.
        
        Args:
            payload: Dati ricevuti dal Metro Digitale
            
        Returns:
            True se valido, False altrimenti
        """
        # Verifica campi richiesti per fermavetro
        if payload.get('type') == 'fermavetro':
            return 'misura_mm' in payload
        
        # Verifica campi per vetri
        if 'larghezza_raw' in payload and 'altezza_raw' in payload:
            return True
        
        return False
    
    async def connect(self):
        """Connette al dispositivo Metro Digitale."""
        try:
            # Trova dispositivo
            device = await self._find_device()
            if not device:
                return False
            
            # Connetti
            self.client = BleakClient(device.address)
            await self.client.connect()
            
            if not self.client.is_connected:
                logger.error("Connessione fallita")
                return False
            
            logger.info(f"Connesso a {device.name}")
            self.is_connected = True
            
            # Subscribe alle notifiche
            await self.client.start_notify(CHAR_RX_UUID, self._notification_handler)
            logger.info("Sottoscritto alle notifiche")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore connessione: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnette dal dispositivo."""
        if self.client and self.client.is_connected:
            try:
                await self.client.stop_notify(CHAR_RX_UUID)
                await self.client.disconnect()
                logger.info("Disconnesso")
            except Exception as e:
                logger.error(f"Errore disconnessione: {e}")
        
        self.is_connected = False
        self.client = None
    
    async def run(self):
        """Loop principale del receiver."""
        self._running = True
        
        while self._running:
            if not self.is_connected:
                success = await self.connect()
                if not success:
                    logger.info("Riprovo tra 5 secondi...")
                    await asyncio.sleep(5)
                    continue
            
            # Mantieni connessione attiva
            try:
                if not self.client or not self.client.is_connected:
                    logger.warning("Connessione persa, riconnessione...")
                    self.is_connected = False
                    continue
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Errore nel loop: {e}")
                self.is_connected = False
                await asyncio.sleep(2)
    
    def start(self):
        """Avvia il receiver (blocking)."""
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            logger.info("Interruzione utente")
        finally:
            self.stop()
    
    def stop(self):
        """Ferma il receiver."""
        self._running = False
        if self.is_connected:
            asyncio.run(self.disconnect())


# Esempio di utilizzo standalone
if __name__ == "__main__":
    receiver = BluetoothCalibroReceiver()
    
    def on_misura(data: Dict[str, Any]):
        """Callback esempio."""
        print(f"\n{'='*50}")
        print(f"Misura ricevuta:")
        print(f"  Tipo: {data.get('type', 'N/A')}")
        
        if 'misura_mm' in data:
            print(f"  Misura: {data['misura_mm']:.2f} mm")
            print(f"  Auto-start: {data.get('auto_start', False)}")
        
        if 'larghezza_raw' in data:
            print(f"  Larghezza: {data['larghezza_netta']:.1f} mm")
            print(f"  Altezza: {data['altezza_netta']:.1f} mm")
            print(f"  Materiale: {data['materiale']}")
        
        print(f"{'='*50}\n")
    
    receiver.on_misura_received = on_misura
    
    print("Bluetooth Calibro Receiver avviato")
    print(f"Ricerca dispositivo: {DEVICE_NAME_FILTER}")
    print("Premi Ctrl+C per terminare\n")
    
    receiver.start()
