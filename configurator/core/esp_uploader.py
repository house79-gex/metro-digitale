"""
Uploader configurazione su ESP32 via USB seriale
"""

import serial
import serial.tools.list_ports
import json
import time
from typing import List, Tuple, Dict, Callable, Optional
from .config_model import ProgettoConfigurazione


class ESPUploader:
    """Gestisce upload configurazione su ESP32"""
    
    BAUD_RATE = 115200
    TIMEOUT = 2.0
    CHUNK_SIZE = 1024
    
    # Comandi protocollo
    CMD_CONFIG_START = "CONFIG_START\n"
    CMD_CONFIG_END = "CONFIG_END\n"
    CMD_CONFIG_SAVE = "CONFIG_SAVE\n"
    CMD_CONFIG_READ = "CONFIG_READ\n"
    CMD_DEVICE_INFO = "DEVICE_INFO\n"
    
    # Risposte attese
    ACK = "ACK"
    NACK = "NACK"
    
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self.connected: bool = False
    
    def find_devices(self) -> List[Tuple[str, str]]:
        """
        Trova dispositivi ESP32 connessi
        
        Returns:
            Lista di tuple (porta, descrizione)
        """
        devices = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Cerca dispositivi con VID/PID ESP32
            # ESP32 VID: 0x10C4 (Silicon Labs) o 0x1A86 (CH340)
            if port.vid in [0x10C4, 0x1A86, 0x303A]:  # 0x303A è Espressif
                devices.append((port.device, port.description))
            # Cerca anche per nome descrizione
            elif any(keyword in port.description.lower() for keyword in ['esp32', 'uart', 'usb-serial']):
                devices.append((port.device, port.description))
        
        return devices
    
    def connect(self, port: str) -> bool:
        """
        Connette a dispositivo ESP32
        
        Args:
            port: Nome porta seriale (es: COM3, /dev/ttyUSB0)
            
        Returns:
            True se connesso con successo
        """
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.BAUD_RATE,
                timeout=self.TIMEOUT,
                write_timeout=self.TIMEOUT
            )
            
            # Attendi stabilizzazione
            time.sleep(0.5)
            
            # Pulisci buffer
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Errore connessione: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnette da dispositivo"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connected = False
    
    def _send_command(self, command: str) -> bool:
        """Invia comando e attende ACK"""
        if not self.connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(command.encode('utf-8'))
            self.serial_port.flush()
            
            # Leggi risposta
            response = self.serial_port.readline().decode('utf-8').strip()
            return response == self.ACK
            
        except Exception as e:
            print(f"Errore invio comando: {e}")
            return False
    
    def _send_data_chunk(self, data: str) -> bool:
        """Invia chunk di dati"""
        if not self.connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(data.encode('utf-8'))
            self.serial_port.flush()
            return True
        except Exception as e:
            print(f"Errore invio dati: {e}")
            return False
    
    def upload_config(self, config: ProgettoConfigurazione, 
                     progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Upload configurazione su ESP32
        
        Args:
            config: Configurazione da caricare
            progress_callback: Callback per progresso (0-100)
            
        Returns:
            True se upload completato con successo
        """
        if not self.connected:
            return False
        
        try:
            # 1. Invia comando start
            if progress_callback:
                progress_callback(10)
            
            if not self._send_command(self.CMD_CONFIG_START):
                return False
            
            # 2. Serializza configurazione
            if progress_callback:
                progress_callback(20)
            
            config_json = json.dumps(config.to_dict(), ensure_ascii=False)
            
            # 3. Invia dati a blocchi
            total_bytes = len(config_json)
            sent_bytes = 0
            
            for i in range(0, total_bytes, self.CHUNK_SIZE):
                chunk = config_json[i:i + self.CHUNK_SIZE]
                
                if not self._send_data_chunk(chunk):
                    return False
                
                sent_bytes += len(chunk)
                
                if progress_callback:
                    progress = 20 + int((sent_bytes / total_bytes) * 60)
                    progress_callback(progress)
                
                # Piccola pausa tra chunk
                time.sleep(0.01)
            
            # 4. Invia comando end
            if progress_callback:
                progress_callback(85)
            
            if not self._send_command(self.CMD_CONFIG_END):
                return False
            
            # 5. Salva su NVS
            if progress_callback:
                progress_callback(90)
            
            if not self._send_command(self.CMD_CONFIG_SAVE):
                return False
            
            if progress_callback:
                progress_callback(100)
            
            return True
            
        except Exception as e:
            print(f"Errore upload: {e}")
            return False
    
    def read_config(self) -> Optional[ProgettoConfigurazione]:
        """
        Legge configurazione da ESP32
        
        Returns:
            Configurazione letta o None
        """
        if not self.connected:
            return None
        
        try:
            # Invia comando read
            if not self._send_command(self.CMD_CONFIG_READ):
                return None
            
            # Leggi JSON (multiline)
            json_lines = []
            while True:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line == "END_CONFIG":
                    break
                json_lines.append(line)
                
                # Timeout dopo 100 righe
                if len(json_lines) > 1000:
                    break
            
            # Parse JSON
            config_json = '\n'.join(json_lines)
            config_dict = json.loads(config_json)
            
            return ProgettoConfigurazione.from_dict(config_dict)
            
        except Exception as e:
            print(f"Errore lettura config: {e}")
            return None
    
    def get_device_info(self) -> Dict:
        """
        Ottiene informazioni dispositivo
        
        Returns:
            Dizionario con info dispositivo
        """
        if not self.connected:
            return {}
        
        try:
            if not self._send_command(self.CMD_DEVICE_INFO):
                return {}
            
            # Leggi risposta JSON
            response = self.serial_port.readline().decode('utf-8').strip()
            return json.loads(response)
            
        except Exception as e:
            print(f"Errore lettura info: {e}")
            return {}
    
    def is_connected(self) -> bool:
        """Verifica se connesso"""
        return self.connected and self.serial_port and self.serial_port.is_open
