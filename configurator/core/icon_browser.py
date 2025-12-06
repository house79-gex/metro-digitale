"""
Client per Iconify API - accesso a 200,000+ icone gratuite
"""

import requests
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
import os
import json
from pathlib import Path


@dataclass
class IconInfo:
    """Informazioni su un'icona"""
    name: str
    prefix: str
    width: int = 24
    height: int = 24
    tags: List[str] = field(default_factory=list)
    
    @property
    def full_name(self) -> str:
        return f"{self.prefix}:{self.name}"


class IconifyClient:
    """Client per Iconify API con ricerca funzionante"""
    
    SEARCH_URL = "https://api.iconify.design/search"
    ICON_URL = "https://api.iconify.design"
    
    RECOMMENDED_SETS = [
        ("mdi", "Material Design Icons"),
        ("tabler", "Tabler Icons"),
        ("lucide", "Lucide"),
        ("phosphor", "Phosphor"),
        ("carbon", "IBM Carbon"),
        ("fluent", "Microsoft Fluent"),
        ("fa6-solid", "Font Awesome 6"),
        ("heroicons", "Heroicons"),
        ("bi", "Bootstrap Icons"),
    ]
    
    FALLBACK_ICONS = [
        IconInfo("window-maximize", "mdi"),
        IconInfo("door", "mdi"),
        IconInfo("ruler", "mdi"),
        IconInfo("cog", "mdi"),
        IconInfo("home", "mdi"),
        IconInfo("send", "mdi"),
        IconInfo("content-save", "mdi"),
        IconInfo("arrow-left", "mdi"),
        IconInfo("arrow-right", "mdi"),
        IconInfo("plus", "mdi"),
        IconInfo("minus", "mdi"),
        IconInfo("check", "mdi"),
        IconInfo("close", "mdi"),
        IconInfo("menu", "mdi"),
        IconInfo("dots-vertical", "mdi"),
    ]
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), ".metro_digitale", "icons")
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetroDigitaleConfigurator/1.0',
            'Accept': 'application/json'
        })
    
    def search(self, query: str, limit: int = 64, prefix: Optional[str] = None) -> List[IconInfo]:
        if not query or not query.strip():
            return self.FALLBACK_ICONS[:limit]
        
        try:
            params = {
                'query': query.strip(),
                'limit': min(limit, 999),
            }
            if prefix:
                params['prefix'] = prefix
            else:
                params['prefixes'] = ','.join([s[0] for s in self.RECOMMENDED_SETS])
            
            response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
            
            if response.status_code != 200:
                return self._search_fallback(query, limit)
            
            data = response.json()
            results = []
            
            for icon_full_name in data.get('icons', []):
                if ':' in icon_full_name:
                    prefix_part, name_part = icon_full_name.split(':', 1)
                    results.append(IconInfo(name=name_part, prefix=prefix_part))
            
            return results[:limit] if results else self._search_fallback(query, limit)
            
        except Exception as e:
            print(f"Errore ricerca icone: {e}")
            return self._search_fallback(query, limit)
    
    def _search_fallback(self, query: str, limit: int) -> List[IconInfo]:
        query_lower = query.lower()
        results = [icon for icon in self.FALLBACK_ICONS if query_lower in icon.name.lower()]
        return results[:limit] if results else self.FALLBACK_ICONS[:limit]
    

    
    def get_svg(self, icon_name: str, color: str = "#ffffff", size: int = 24) -> Optional[str]:
        if ':' not in icon_name:
            return None
        try:
            safe_name = icon_name.replace(':', '_').replace('/', '_')
            cache_file = os.path.join(self.cache_dir, f"{safe_name}_{size}_{color.replace('#', '')}.svg")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            prefix, name = icon_name.split(':', 1)
            url = f"{self.ICON_URL}/{prefix}/{name}.svg"
            params = {'color': color.replace('#', '%23'), 'width': str(size), 'height': str(size)}
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                svg_data = response.text
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(svg_data)
                return svg_data
            return None
        except Exception as e:
            print(f"Errore download SVG: {e}")
            return None
    
    def get_icon_svg(self, icon_name: str, color: str = "#ffffff", size: int = 48) -> Optional[str]:
        """Alias per get_svg con dimensione default più grande per preview"""
        return self.get_svg(icon_name, color, size)
    
    def get_icon_sets(self) -> List[Tuple[str, str]]:
        return self.RECOMMENDED_SETS.copy()
    
    def clear_cache(self):
        try:
            for file in os.listdir(self.cache_dir):
                os.unlink(os.path.join(self.cache_dir, file))
        except Exception as e:
            print(f"Errore pulizia cache: {e}")
