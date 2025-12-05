"""
Gestione salvataggio/caricamento progetti Metro Digitale (.mdp)
"""

import json
import os
from typing import Optional
from datetime import datetime
from .config_model import ProgettoConfigurazione


class ProjectManager:
    """Gestisce operazioni su file progetto (.mdp)"""
    
    FILE_EXTENSION = ".mdp"
    
    def __init__(self):
        self.current_file: Optional[str] = None
        self.current_project: Optional[ProgettoConfigurazione] = None
        self.modified: bool = False
    
    def new_project(self, nome: str = "Nuovo Progetto") -> ProgettoConfigurazione:
        """
        Crea un nuovo progetto vuoto
        
        Args:
            nome: Nome del progetto
            
        Returns:
            Nuovo progetto
        """
        self.current_project = ProgettoConfigurazione(nome=nome)
        self.current_file = None
        self.modified = False
        return self.current_project
    
    def save_project(self, filepath: str, project: ProgettoConfigurazione) -> bool:
        """
        Salva un progetto su file
        
        Args:
            filepath: Percorso file di destinazione
            project: Progetto da salvare
            
        Returns:
            True se salvato con successo
            
        Raises:
            IOError: Se impossibile salvare
        """
        try:
            # Assicura estensione corretta
            if not filepath.endswith(self.FILE_EXTENSION):
                filepath += self.FILE_EXTENSION
            
            # Aggiorna timestamp modifica
            project.modified = datetime.now()
            
            # Serializza in JSON
            data = project.to_dict()
            
            # Salva su file con indentazione
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.current_file = filepath
            self.current_project = project
            self.modified = False
            
            return True
            
        except Exception as e:
            raise IOError(f"Impossibile salvare il progetto: {e}")
    
    def load_project(self, filepath: str) -> ProgettoConfigurazione:
        """
        Carica un progetto da file
        
        Args:
            filepath: Percorso file da caricare
            
        Returns:
            Progetto caricato
            
        Raises:
            IOError: Se impossibile caricare
            ValueError: Se formato non valido
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File non trovato: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = ProgettoConfigurazione.from_dict(data)
            
            self.current_file = filepath
            self.current_project = project
            self.modified = False
            
            return project
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Formato file non valido: {e}")
        except Exception as e:
            raise IOError(f"Impossibile caricare il progetto: {e}")
    
    def export_json(self, filepath: str, project: ProgettoConfigurazione) -> bool:
        """
        Esporta progetto come JSON generico
        
        Args:
            filepath: Percorso file di destinazione
            project: Progetto da esportare
            
        Returns:
            True se esportato con successo
        """
        try:
            data = project.to_dict()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            raise IOError(f"Impossibile esportare: {e}")
    
    def mark_modified(self):
        """Marca il progetto come modificato"""
        self.modified = True
    
    def is_modified(self) -> bool:
        """Verifica se il progetto è stato modificato"""
        return self.modified
    
    def get_project_name(self) -> str:
        """Ottiene il nome del progetto corrente"""
        if self.current_project:
            return self.current_project.nome
        return "Nessun progetto"
    
    def get_file_path(self) -> Optional[str]:
        """Ottiene il percorso del file corrente"""
        return self.current_file
