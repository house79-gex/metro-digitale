"""
Gestore Import/Export per Metro Digitale
Gestisce import/export misure (JSONL/CSV) e configurazioni (JSON) su microSD/USB-C OTG
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import shutil


class IOManager:
    """Gestisce import/export di misure e configurazioni"""
    
    def __init__(self):
        """Inizializza gestore I/O"""
        self.default_sd_path = Path("/sd")  # Path microSD su ESP32
        self.default_usb_path = Path("/usb")  # Path USB MSC su ESP32
    
    @staticmethod
    def _sanitize_path(filepath: Path, base_path: Path) -> Path:
        """
        Sanitizza path per prevenire directory traversal
        
        Args:
            filepath: Path da sanitizzare
            base_path: Path base consentito
            
        Returns:
            Path sanitizzato
            
        Raises:
            ValueError: Se path tenta directory traversal
        """
        # Risolvi path assoluto
        resolved = filepath.resolve()
        base_resolved = base_path.resolve()
        
        # Verifica che sia sotto base_path
        try:
            resolved.relative_to(base_resolved)
        except ValueError:
            raise ValueError(f"Path non consentito: {filepath} non è sotto {base_path}")
        
        return resolved
    
    # ==================== MISURE ====================
    
    def export_measures_jsonl(self, measures: List[Dict[str, Any]], filepath: Path, 
                              append: bool = False) -> bool:
        """
        Esporta misure in formato JSONL (una riga per misura)
        
        Args:
            measures: Lista di misure da esportare
            filepath: Percorso file di destinazione
            append: Se True, appende a file esistente (append-safe)
            
        Returns:
            True se esportate con successo
        """
        try:
            mode = 'a' if append else 'w'
            with open(filepath, mode, encoding='utf-8') as f:
                for measure in measures:
                    # Aggiungi timestamp se non presente
                    if 'timestamp' not in measure:
                        measure['timestamp'] = datetime.now().isoformat()
                    
                    json_line = json.dumps(measure, ensure_ascii=False)
                    f.write(json_line + '\n')
            
            return True
        except IOError as e:
            print(f"Errore export JSONL: {e}")
            return False
    
    def import_measures_jsonl(self, filepath: Path) -> Optional[List[Dict[str, Any]]]:
        """
        Importa misure da formato JSONL
        
        Args:
            filepath: Percorso file sorgente
            
        Returns:
            Lista di misure o None se errore
        """
        if not filepath.exists():
            print(f"File non trovato: {filepath}")
            return None
        
        measures = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Salta linee vuote
                        continue
                    
                    try:
                        measure = json.loads(line)
                        measures.append(measure)
                    except json.JSONDecodeError as e:
                        print(f"Errore parsing linea {line_num}: {e}")
                        # Continua con le altre linee
            
            return measures
        except IOError as e:
            print(f"Errore import JSONL: {e}")
            return None
    
    def export_measures_csv(self, measures: List[Dict[str, Any]], filepath: Path, 
                           fields: Optional[List[str]] = None) -> bool:
        """
        Esporta misure in formato CSV
        
        Args:
            measures: Lista di misure da esportare
            filepath: Percorso file di destinazione
            fields: Lista campi da includere (default: tutti)
            
        Returns:
            True se esportate con successo
        """
        if not measures:
            print("Nessuna misura da esportare")
            return False
        
        try:
            # Determina campi se non specificati
            if fields is None:
                # Usa tutti i campi dalla prima misura
                fields = list(measures[0].keys())
            
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()
                
                for measure in measures:
                    # Aggiungi timestamp se non presente
                    if 'timestamp' not in measure and 'timestamp' in fields:
                        measure['timestamp'] = datetime.now().isoformat()
                    
                    writer.writerow(measure)
            
            return True
        except (IOError, csv.Error) as e:
            print(f"Errore export CSV: {e}")
            return False
    
    def import_measures_csv(self, filepath: Path) -> Optional[List[Dict[str, Any]]]:
        """
        Importa misure da formato CSV
        
        Args:
            filepath: Percorso file sorgente
            
        Returns:
            Lista di misure o None se errore
        """
        if not filepath.exists():
            print(f"File non trovato: {filepath}")
            return None
        
        measures = []
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Converti valori numerici
                    measure = {}
                    for key, value in row.items():
                        # Prova a convertire in float
                        try:
                            measure[key] = float(value)
                        except (ValueError, TypeError):
                            measure[key] = value
                    
                    measures.append(measure)
            
            return measures
        except (IOError, csv.Error) as e:
            print(f"Errore import CSV: {e}")
            return None
    
    # ==================== CONFIGURAZIONI ====================
    
    def export_config(self, config: Dict[str, Any], filepath: Path, 
                     create_backup: bool = True) -> bool:
        """
        Esporta configurazione in formato JSON
        
        Args:
            config: Dizionario configurazione
            filepath: Percorso file di destinazione
            create_backup: Se True, crea backup del file esistente
            
        Returns:
            True se esportata con successo
        """
        try:
            # Crea backup se richiesto e file esiste
            if create_backup and filepath.exists():
                backup_path = filepath.with_suffix('.json.bak')
                shutil.copy2(filepath, backup_path)
            
            # Assicura schema_version
            if 'schema_version' not in config:
                config['schema_version'] = '1.0.0'
            
            # Aggiungi metadata export
            config['_export_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'version': config.get('schema_version', '1.0.0')
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        except IOError as e:
            print(f"Errore export config: {e}")
            return False
    
    def import_config(self, filepath: Path, migrate: bool = True) -> Optional[Dict[str, Any]]:
        """
        Importa configurazione da file JSON
        
        Args:
            filepath: Percorso file sorgente
            migrate: Se True, esegue migrazione schema se necessario
            
        Returns:
            Dizionario configurazione o None se errore
        """
        if not filepath.exists():
            print(f"File non trovato: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Rimuovi metadata export se presente
            if '_export_metadata' in config:
                del config['_export_metadata']
            
            # Migrazione schema se richiesta
            if migrate:
                config = self._migrate_config_schema(config)
            
            return config
        except (IOError, json.JSONDecodeError) as e:
            print(f"Errore import config: {e}")
            return None
    
    def _migrate_config_schema(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Esegue migrazione schema configurazione
        
        Args:
            config: Configurazione da migrare
            
        Returns:
            Configurazione migrata
        """
        current_version = config.get('schema_version', '0.0.0')
        target_version = '1.0.0'
        
        if current_version == target_version:
            return config
        
        # Migrazione 0.0.0 -> 1.0.0
        if current_version == '0.0.0':
            # Aggiungi campi richiesti per v1.0.0
            if 'hardware' not in config:
                config['hardware'] = {
                    'encoder': {},
                    'probes': [],
                    'bluetooth': {},
                    'display': {}
                }
            
            if 'modes' not in config:
                config['modes'] = []
            
            if 'ui_layout' not in config:
                config['ui_layout'] = {
                    'theme': 'dark',
                    'units': 'mm',
                    'decimals': 2
                }
            
            if 'icons' not in config:
                config['icons'] = {}
            
            config['schema_version'] = '1.0.0'
        
        return config
    
    # ==================== UTILITY ====================
    
    def get_sd_path(self, filename: str) -> Path:
        """
        Ottiene path completo su microSD
        
        Args:
            filename: Nome file
            
        Returns:
            Path completo
        """
        return self.default_sd_path / filename
    
    def get_usb_path(self, filename: str) -> Path:
        """
        Ottiene path completo su USB
        
        Args:
            filename: Nome file
            
        Returns:
            Path completo
        """
        return self.default_usb_path / filename
    
    def check_sd_available(self) -> bool:
        """
        Verifica se microSD è disponibile
        
        Returns:
            True se disponibile
        """
        return self.default_sd_path.exists()
    
    def check_usb_available(self) -> bool:
        """
        Verifica se USB è disponibile
        
        Returns:
            True se disponibile
        """
        return self.default_usb_path.exists()
    
    def list_files(self, directory: Path, pattern: str = "*") -> List[Path]:
        """
        Elenca file in directory
        
        Args:
            directory: Directory da esplorare
            pattern: Pattern glob (default: tutti)
            
        Returns:
            Lista di path file
        """
        if not directory.exists():
            return []
        
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            print(f"Errore listing files: {e}")
            return []
    
    def create_example_measures(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Crea misure di esempio per testing
        
        Args:
            count: Numero di misure da creare
            
        Returns:
            Lista di misure
        """
        measures = []
        for i in range(count):
            measures.append({
                'id': i + 1,
                'timestamp': datetime.now().isoformat(),
                'value': 100.0 + i * 10.5,
                'unit': 'mm',
                'probe_type': 'interno' if i % 2 == 0 else 'esterno',
                'material': 'alluminio',
                'notes': f'Misura test {i + 1}'
            })
        
        return measures
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida configurazione
        
        Args:
            config: Configurazione da validare
            
        Returns:
            Tupla (valida, lista_errori)
        """
        errors = []
        
        # Verifica campi obbligatori
        required_fields = ['schema_version', 'hardware', 'modes', 'ui_layout']
        for field in required_fields:
            if field not in config:
                errors.append(f"Campo obbligatorio mancante: {field}")
        
        # Verifica schema_version
        if 'schema_version' in config:
            version = config['schema_version']
            if not isinstance(version, str):
                errors.append("schema_version deve essere una stringa")
        
        # Verifica hardware
        if 'hardware' in config:
            hw = config['hardware']
            if not isinstance(hw, dict):
                errors.append("hardware deve essere un dizionario")
        
        # Verifica modes
        if 'modes' in config:
            modes = config['modes']
            if not isinstance(modes, list):
                errors.append("modes deve essere una lista")
        
        return len(errors) == 0, errors
