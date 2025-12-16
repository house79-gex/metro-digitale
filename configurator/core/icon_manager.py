"""
Gestore icone locali per Metro Digitale Configurator
Supporta import e caching di icone SVG, PNG, JPG
"""

import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize, Qt


class IconManager:
    """Gestisce icone locali con import, registry e caching"""
    
    def __init__(self, resources_path: Optional[Path] = None):
        """
        Inizializza gestore icone
        
        Args:
            resources_path: Path alla directory resources. Se None, usa default.
        """
        if resources_path is None:
            # Default: resources/ relativo a questo file
            base_dir = Path(__file__).parent.parent
            resources_path = base_dir / "resources"
        
        self.resources_path = Path(resources_path)
        self.icons_path = self.resources_path / "icons"
        self.registry_path = self.icons_path / "icons.json"
        
        # Crea directory se non esiste
        self.icons_path.mkdir(parents=True, exist_ok=True)
        
        # Cache per pixmap
        self._pixmap_cache: Dict[str, QPixmap] = {}
        self._svg_cache: Dict[str, QSvgRenderer] = {}
        
        # Carica o crea registry
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Carica registry icone da JSON"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Errore caricamento registry icone: {e}")
        
        # Registry vuoto di default
        return {
            "version": "1.0.0",
            "icons": {}
        }
    
    def _save_registry(self):
        """Salva registry icone su JSON"""
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Errore salvataggio registry icone: {e}")
    
    def import_file(self, source_path: Path, icon_id: Optional[str] = None,
                   category: str = "custom", description: str = "") -> Optional[str]:
        """
        Importa file icona in resources/icons/
        
        Args:
            source_path: Path al file sorgente (SVG/PNG/JPG)
            icon_id: ID univoco per l'icona. Se None, usa nome file.
            category: Categoria icona (es: "custom", "probe", "material")
            description: Descrizione opzionale
        
        Returns:
            ID icona se successo, None altrimenti
        """
        source_path = Path(source_path)
        
        # Valida estensione
        valid_extensions = {'.svg', '.png', '.jpg', '.jpeg'}
        if source_path.suffix.lower() not in valid_extensions:
            print(f"Estensione non supportata: {source_path.suffix}")
            return None
        
        # Genera ID se non fornito
        if icon_id is None:
            icon_id = source_path.stem
        
        # Verifica duplicati
        if icon_id in self.registry["icons"]:
            print(f"ID icona già esistente: {icon_id}")
            return None
        
        # Copia file in resources/icons/
        dest_filename = f"{icon_id}{source_path.suffix.lower()}"
        dest_path = self.icons_path / dest_filename
        
        try:
            shutil.copy2(source_path, dest_path)
        except IOError as e:
            print(f"Errore copia file: {e}")
            return None
        
        # Aggiungi al registry
        self.registry["icons"][icon_id] = {
            "filename": dest_filename,
            "category": category,
            "description": description,
            "format": source_path.suffix.lower()[1:],  # senza il punto
            "size": dest_path.stat().st_size
        }
        
        self._save_registry()
        
        print(f"Icona importata: {icon_id} -> {dest_filename}")
        return icon_id
    
    def list_local_icons(self, category: Optional[str] = None) -> List[Dict]:
        """
        Elenca icone locali
        
        Args:
            category: Filtra per categoria. Se None, mostra tutte.
        
        Returns:
            Lista di dict con info icone
        """
        icons = []
        
        for icon_id, info in self.registry["icons"].items():
            if category is None or info.get("category") == category:
                icons.append({
                    "id": icon_id,
                    "filename": info.get("filename", ""),
                    "category": info.get("category", ""),
                    "description": info.get("description", ""),
                    "format": info.get("format", ""),
                    "size": info.get("size", 0)
                })
        
        return icons
    
    def get_icon_path(self, icon_id: str) -> Optional[Path]:
        """
        Ottieni path completo di un'icona
        
        Args:
            icon_id: ID icona
        
        Returns:
            Path al file o None se non trovato
        """
        if icon_id not in self.registry["icons"]:
            return None
        
        filename = self.registry["icons"][icon_id].get("filename")
        if not filename:
            return None
        
        path = self.icons_path / filename
        return path if path.exists() else None
    
    def get_pixmap(self, icon_id: str, size: Optional[Tuple[int, int]] = None) -> Optional[QPixmap]:
        """
        Ottieni QPixmap di un'icona con caching
        
        Args:
            icon_id: ID icona
            size: Tupla (width, height) per resize. Se None, dimensione originale.
        
        Returns:
            QPixmap o None se non trovato
        """
        # Chiave cache include dimensione
        cache_key = f"{icon_id}_{size[0] if size else 'orig'}x{size[1] if size else 'orig'}"
        
        # Controlla cache
        if cache_key in self._pixmap_cache:
            return self._pixmap_cache[cache_key]
        
        # Carica da file
        icon_path = self.get_icon_path(icon_id)
        if not icon_path:
            return None
        
        # Determina formato
        icon_format = self.registry["icons"][icon_id].get("format", "")
        
        if icon_format == "svg":
            # Render SVG
            pixmap = self._render_svg(icon_path, size)
        else:
            # Carica PNG/JPG
            pixmap = QPixmap(str(icon_path))
            
            # Resize se richiesto
            if size and not pixmap.isNull():
                pixmap = pixmap.scaled(
                    size[0], size[1],
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation
                )
        
        # Cache e ritorna
        if pixmap and not pixmap.isNull():
            self._pixmap_cache[cache_key] = pixmap
            return pixmap
        
        return None
    
    def _render_svg(self, svg_path: Path, size: Optional[Tuple[int, int]] = None) -> Optional[QPixmap]:
        """
        Render SVG a QPixmap
        
        Args:
            svg_path: Path al file SVG
            size: Dimensione output. Se None, usa dimensione SVG.
        
        Returns:
            QPixmap o None
        """
        try:
            renderer = QSvgRenderer(str(svg_path))
            
            if not renderer.isValid():
                return None
            
            # Determina dimensione
            if size:
                width, height = size
            else:
                svg_size = renderer.defaultSize()
                width = svg_size.width()
                height = svg_size.height()
            
            # Crea pixmap e render
            pixmap = QPixmap(width, height)
            pixmap.fill(0)  # Trasparente
            
            from PyQt6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return pixmap
        except Exception as e:
            print(f"Errore render SVG {svg_path}: {e}")
            return None
    
    def get_svg(self, icon_id: str) -> Optional[QSvgRenderer]:
        """
        Ottieni QSvgRenderer di un'icona SVG con caching
        
        Args:
            icon_id: ID icona
        
        Returns:
            QSvgRenderer o None se non SVG o non trovato
        """
        # Controlla cache
        if icon_id in self._svg_cache:
            return self._svg_cache[icon_id]
        
        # Verifica formato
        if icon_id not in self.registry["icons"]:
            return None
        
        if self.registry["icons"][icon_id].get("format") != "svg":
            return None
        
        # Carica SVG
        icon_path = self.get_icon_path(icon_id)
        if not icon_path:
            return None
        
        try:
            renderer = QSvgRenderer(str(icon_path))
            if renderer.isValid():
                self._svg_cache[icon_id] = renderer
                return renderer
        except Exception as e:
            print(f"Errore caricamento SVG {icon_id}: {e}")
        
        return None
    
    def get_icon(self, icon_id: str, size: Optional[Tuple[int, int]] = None) -> Optional[QIcon]:
        """
        Ottieni QIcon di un'icona
        
        Args:
            icon_id: ID icona
            size: Dimensione pixmap. Se None, usa originale.
        
        Returns:
            QIcon o None
        """
        pixmap = self.get_pixmap(icon_id, size)
        if pixmap:
            return QIcon(pixmap)
        return None
    
    def delete_icon(self, icon_id: str) -> bool:
        """
        Elimina un'icona dal registry e dal filesystem
        
        Args:
            icon_id: ID icona da eliminare
        
        Returns:
            True se eliminata, False altrimenti
        """
        if icon_id not in self.registry["icons"]:
            return False
        
        # Rimuovi file
        icon_path = self.get_icon_path(icon_id)
        if icon_path and icon_path.exists():
            try:
                icon_path.unlink()
            except OSError as e:
                print(f"Errore eliminazione file {icon_path}: {e}")
                return False
        
        # Rimuovi da cache
        self._pixmap_cache = {k: v for k, v in self._pixmap_cache.items() if not k.startswith(icon_id)}
        if icon_id in self._svg_cache:
            del self._svg_cache[icon_id]
        
        # Rimuovi da registry
        del self.registry["icons"][icon_id]
        self._save_registry()
        
        print(f"Icona eliminata: {icon_id}")
        return True
    
    def get_categories(self) -> List[str]:
        """
        Ottieni lista categorie uniche
        
        Returns:
            Lista categorie
        """
        categories = set()
        for info in self.registry["icons"].values():
            category = info.get("category", "custom")
            categories.add(category)
        return sorted(list(categories))
    
    def clear_cache(self):
        """Pulisce cache pixmap e SVG"""
        self._pixmap_cache.clear()
        self._svg_cache.clear()
        print("Cache icone pulita")


# Istanza singleton
_icon_manager_instance = None


def get_icon_manager() -> IconManager:
    """Ottieni istanza singleton del gestore icone"""
    global _icon_manager_instance
    if _icon_manager_instance is None:
        _icon_manager_instance = IconManager()
    return _icon_manager_instance
