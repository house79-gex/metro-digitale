"""
Gestore Import/Export per Metro Digitale
Supporta export/import di misure (JSONL, CSV) e configurazioni (JSON)
con supporto per microSD e USB-C OTG
"""

import json
import csv
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import shutil


class IOManager:
    """Gestisce import/export di misure e configurazioni"""
    
    # Percorsi standard per dispositivi
    SD_MOUNT_PATH = "/sd"  # Path standard per microSD su ESP32
    USB_MOUNT_PATH = "/usb"  # Path standard per USB OTG
    
    def __init__(self):
        """Inizializza gestore I/O"""
        self.last_export_path = None
        self.last_import_path = None
    
    # =====================================================================
    # EXPORT/IMPORT MISURE
    # =====================================================================
    
    def export_measures_jsonl(self, measures: List[Dict], output_path: Path,
                              append: bool = True) -> bool:
        """
        Esporta misure in formato JSONL (JSON Lines)
        Append-safe per registrazione continua
        
        Args:
            measures: Lista di dict misure
            output_path: Path file output
            append: Se True, appende al file esistente
        
        Returns:
            True se successo, False altrimenti
        """
        output_path = Path(output_path)
        
        try:
            # Crea directory se non esiste
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Modalità append o write
            mode = 'a' if append and output_path.exists() else 'w'
            
            with open(output_path, mode, encoding='utf-8') as f:
                for measure in measures:
                    # Aggiungi timestamp se non presente
                    if 'timestamp' not in measure:
                        measure['timestamp'] = datetime.now().isoformat()
                    
                    # Scrivi una linea JSON per misura
                    json_line = json.dumps(measure, ensure_ascii=False)
                    f.write(json_line + '\n')
            
            self.last_export_path = str(output_path)
            print(f"Esportate {len(measures)} misure in {output_path}")
            return True
            
        except (IOError, OSError) as e:
            print(f"Errore export misure JSONL: {e}")
            return False
    
    def import_measures_jsonl(self, input_path: Path,
                             max_lines: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Importa misure da formato JSONL
        
        Args:
            input_path: Path file input
            max_lines: Numero massimo linee da leggere. None = tutte.
        
        Returns:
            Lista misure o None se errore
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"File non trovato: {input_path}")
            return None
        
        try:
            measures = []
            
            with open(input_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if max_lines and i >= max_lines:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        measure = json.loads(line)
                        measures.append(measure)
                    except json.JSONDecodeError as e:
                        print(f"Errore parse linea {i+1}: {e}")
                        continue
            
            self.last_import_path = str(input_path)
            print(f"Importate {len(measures)} misure da {input_path}")
            return measures
            
        except (IOError, OSError) as e:
            print(f"Errore import misure JSONL: {e}")
            return None
    
    def export_measures_csv(self, measures: List[Dict], output_path: Path,
                           fields: Optional[List[str]] = None) -> bool:
        """
        Esporta misure in formato CSV
        
        Args:
            measures: Lista dict misure
            output_path: Path file output
            fields: Lista campi da esportare. Se None, usa tutti i campi.
        
        Returns:
            True se successo, False altrimenti
        """
        output_path = Path(output_path)
        
        if not measures:
            print("Nessuna misura da esportare")
            return False
        
        try:
            # Determina campi
            if fields is None:
                # Usa tutti i campi della prima misura
                fields = list(measures[0].keys())
            
            # Crea directory se non esiste
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                
                for measure in measures:
                    # Aggiungi timestamp se non presente
                    if 'timestamp' not in measure and 'timestamp' in fields:
                        measure['timestamp'] = datetime.now().isoformat()
                    
                    writer.writerow(measure)
            
            self.last_export_path = str(output_path)
            print(f"Esportate {len(measures)} misure in CSV: {output_path}")
            return True
            
        except (IOError, OSError, csv.Error) as e:
            print(f"Errore export misure CSV: {e}")
            return False
    
    def import_measures_csv(self, input_path: Path) -> Optional[List[Dict]]:
        """
        Importa misure da CSV
        
        Args:
            input_path: Path file input
        
        Returns:
            Lista misure o None se errore
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"File non trovato: {input_path}")
            return None
        
        try:
            measures = []
            
            with open(input_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    measures.append(dict(row))
            
            self.last_import_path = str(input_path)
            print(f"Importate {len(measures)} misure da CSV: {input_path}")
            return measures
            
        except (IOError, OSError, csv.Error) as e:
            print(f"Errore import misure CSV: {e}")
            return None
    
    # =====================================================================
    # EXPORT/IMPORT CONFIGURAZIONI
    # =====================================================================
    
    def export_config(self, config: Dict, output_path: Path,
                     create_backup: bool = True) -> bool:
        """
        Esporta configurazione in formato JSON
        
        Args:
            config: Dict configurazione
            output_path: Path file output
            create_backup: Se True, crea backup del file esistente
        
        Returns:
            True se successo, False altrimenti
        """
        output_path = Path(output_path)
        
        try:
            # Backup file esistente
            if create_backup and output_path.exists():
                backup_path = output_path.with_suffix(f'.backup_{datetime.now():%Y%m%d_%H%M%S}.json')
                shutil.copy2(output_path, backup_path)
                print(f"Backup creato: {backup_path}")
            
            # Aggiungi metadata
            export_data = {
                "export_version": "1.0.0",
                "export_date": datetime.now().isoformat(),
                "config": config
            }
            
            # Crea directory se non esiste
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Scrivi JSON con indent per leggibilità
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.last_export_path = str(output_path)
            print(f"Configurazione esportata in: {output_path}")
            return True
            
        except (IOError, OSError) as e:
            print(f"Errore export configurazione: {e}")
            return False
    
    def import_config(self, input_path: Path,
                     migrate: bool = True) -> Optional[Dict]:
        """
        Importa configurazione da JSON
        
        Args:
            input_path: Path file input
            migrate: Se True, migra automaticamente versioni vecchie
        
        Returns:
            Dict configurazione o None se errore
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"File non trovato: {input_path}")
            return None
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Estrai configurazione
            if "config" in data:
                # Formato con metadata
                config = data["config"]
                export_version = data.get("export_version", "unknown")
                print(f"Import da versione: {export_version}")
            else:
                # Formato legacy senza metadata
                config = data
            
            # Migrazione se richiesta
            if migrate:
                config = self._migrate_config(config)
            
            self.last_import_path = str(input_path)
            print(f"Configurazione importata da: {input_path}")
            return config
            
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Errore import configurazione: {e}")
            return None
    
    def _migrate_config(self, config: Dict) -> Dict:
        """
        Migra configurazione da versioni vecchie
        
        Args:
            config: Configurazione da migrare
        
        Returns:
            Configurazione migrata
        """
        # Determina schema_version
        schema_version = config.get("schema_version", config.get("version", "1.0.0"))
        
        print(f"Migrazione da schema {schema_version}")
        
        # Aggiungi campi mancanti con default
        if "schema_version" not in config:
            config["schema_version"] = "2.0.0"
        
        if "hardware" not in config:
            config["hardware"] = {
                "encoder": {
                    "resolution": 0.01,
                    "pulses_per_mm": 100,
                    "debounce_ms": 5,
                    "pin_a": 4,
                    "pin_b": 5,
                    "invert_direction": False
                },
                "bluetooth": {
                    "enabled": True,
                    "name": "MetroDigitale",
                    "uuid": "00001101-0000-1000-8000-00805F9B34FB",
                    "auto_connect": True
                },
                "display": {
                    "width": 800,
                    "height": 480,
                    "brightness": 80
                }
            }
        
        if "modes" not in config:
            config["modes"] = []
        
        if "ui_layout" not in config:
            config["ui_layout"] = {
                "theme": "dark",
                "units": "mm",
                "decimals": 2
            }
        
        if "icons" not in config:
            config["icons"] = {}
        
        print(f"Configurazione migrata a schema {config['schema_version']}")
        return config
    
    # =====================================================================
    # UTILITY PERCORSI
    # =====================================================================
    
    def get_sd_path(self, filename: str = "") -> Path:
        """
        Ottieni path su microSD
        
        Args:
            filename: Nome file opzionale
        
        Returns:
            Path completo
        """
        return Path(self.SD_MOUNT_PATH) / filename
    
    def get_usb_path(self, filename: str = "") -> Path:
        """
        Ottieni path su USB
        
        Args:
            filename: Nome file opzionale
        
        Returns:
            Path completo
        """
        return Path(self.USB_MOUNT_PATH) / filename
    
    def is_sd_available(self) -> bool:
        """Verifica se microSD è disponibile"""
        return Path(self.SD_MOUNT_PATH).exists()
    
    def is_usb_available(self) -> bool:
        """Verifica se USB è disponibile"""
        return Path(self.USB_MOUNT_PATH).exists()
    
    def list_export_destinations(self) -> List[Dict[str, Any]]:
        """
        Elenca destinazioni disponibili per export
        
        Returns:
            Lista dict con info destinazioni
        """
        destinations = []
        
        # Sempre disponibile: path locale
        destinations.append({
            "type": "local",
            "name": "File Locale",
            "path": str(Path.home()),
            "available": True
        })
        
        # microSD
        destinations.append({
            "type": "sd",
            "name": "microSD",
            "path": self.SD_MOUNT_PATH,
            "available": self.is_sd_available()
        })
        
        # USB OTG
        destinations.append({
            "type": "usb",
            "name": "USB",
            "path": self.USB_MOUNT_PATH,
            "available": self.is_usb_available()
        })
        
        return destinations


# Istanza singleton
_io_manager_instance = None


def get_io_manager() -> IOManager:
    """Ottieni istanza singleton del gestore I/O"""
    global _io_manager_instance
    if _io_manager_instance is None:
        _io_manager_instance = IOManager()
    return _io_manager_instance
