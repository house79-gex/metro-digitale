"""
Client per Iconify API - accesso a 200,000+ icone gratuite
"""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
import os
import json
from pathlib import Path


@dataclass
class IconInfo:
    """Informazioni su un'icona"""
    name: str
    set: str
    width: int = 24
    height: int = 24
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def full_name(self) -> str:
        """Nome completo icona (set:name)"""
        return f"{self.set}:{self.name}"


class IconifyClient:
    """Client per Iconify API"""
    
    BASE_URL = "https://api.iconify.design"
    
    # Set di icone raccomandati per Metro Digitale
    RECOMMENDED_SETS = [
        "mdi",          # Material Design Icons (7000+)
        "tabler",       # Tabler Icons (4600+)
        "lucide",       # Lucide (1400+)
        "phosphor",     # Phosphor (7000+)
        "carbon",       # IBM Carbon (2000+)
        "fluent",       # Microsoft Fluent (4000+)
        "fa6-solid",    # Font Awesome 6
    ]
    
    # Suggerimenti per serramenti
    WINDOW_SUGGESTIONS = {
        "finestre": ["window", "frame", "glass", "rectangle"],
        "porte": ["door", "entrance", "gate", "exit"],
        "strumenti": ["ruler", "measure", "tool", "wrench"],
        "azioni": ["send", "save", "settings", "home", "menu"],
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Inizializza client Iconify
        
        Args:
            cache_dir: Directory per cache locale (default: ~/.metro_digitale/icons)
        """
        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), ".metro_digitale", "icons")
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetroDigitaleConfigurator/1.0'
        })
    
    def search(self, query: str, limit: int = 64, icon_set: Optional[str] = None) -> List[IconInfo]:
        """
        Cerca icone su Iconify
        
        Args:
            query: Termine di ricerca
            limit: Numero massimo risultati
            icon_set: Set specifico (es: "mdi") o None per tutti
            
        Returns:
            Lista di IconInfo
        """
        try:
            # Usa API di ricerca Iconify
            params = {
                'query': query,
                'limit': limit,
            }
            
            if icon_set:
                params['prefix'] = icon_set
            
            # Nota: Iconify non ha API di ricerca pubblica diretta
            # Usiamo endpoint collection per ottenere icone di un set
            results = []
            
            sets_to_search = [icon_set] if icon_set else self.RECOMMENDED_SETS
            
            for iset in sets_to_search:
                # Prova a caricare la collection
                try:
                    collection = self._load_collection(iset)
                    if collection:
                        # Filtra icone che matchano la query
                        icons = collection.get('icons', {})
                        for icon_name in icons:
                            if query.lower() in icon_name.lower():
                                info = IconInfo(
                                    name=icon_name,
                                    set=iset,
                                    width=icons[icon_name].get('width', 24),
                                    height=icons[icon_name].get('height', 24)
                                )
                                results.append(info)
                                
                                if len(results) >= limit:
                                    return results
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Errore ricerca icone: {e}")
            return []
    
    def _load_collection(self, icon_set: str) -> Optional[Dict]:
        """Carica metadata collection da cache o API"""
        cache_file = os.path.join(self.cache_dir, f"{icon_set}.json")
        
        # Prova cache locale
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Scarica da API
        try:
            url = f"{self.BASE_URL}/{icon_set}.json"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Salva in cache
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
                return data
        except:
            pass
        
        return None
    
    def get_svg(self, icon_name: str, color: str = "#000000", size: int = 24) -> Optional[str]:
        """
        Ottiene SVG di un'icona
        
        Args:
            icon_name: Nome completo icona (set:name)
            color: Colore hex
            size: Dimensione in pixel
            
        Returns:
            Stringa SVG o None
        """
        try:
            # Cache file
            cache_file = os.path.join(
                self.cache_dir, 
                f"{icon_name.replace(':', '_')}_{size}_{color.replace('#', '')}.svg"
            )
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return f.read()
            
            # Scarica da API
            url = f"{self.BASE_URL}/{icon_name}.svg"
            params = {
                'color': color,
                'width': size,
                'height': size
            }
            
            response = self.session.get(url, params=params, timeout=5)
            if response.status_code == 200:
                svg_data = response.text
                
                # Salva in cache
                with open(cache_file, 'w') as f:
                    f.write(svg_data)
                
                return svg_data
            
            return None
            
        except Exception as e:
            print(f"Errore download SVG: {e}")
            return None
    
    def get_suggested_icons(self, category: str) -> List[str]:
        """
        Ottiene suggerimenti di ricerca per categoria
        
        Args:
            category: Categoria (finestre, porte, strumenti, azioni)
            
        Returns:
            Lista di termini suggeriti
        """
        return self.WINDOW_SUGGESTIONS.get(category.lower(), [])
    
    def clear_cache(self):
        """Svuota la cache delle icone"""
        try:
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
        except Exception as e:
            print(f"Errore pulizia cache: {e}")
