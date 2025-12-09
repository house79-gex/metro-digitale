"""
Gestore icone locali per Metro Digitale Configurator
Importa, cataloga e gestisce icone SVG/PNG/JPG locali
"""

import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize


class IconManager:
    """Gestisce icone locali con import, caching e catalogazione"""
    
    def __init__(self, icons_dir: Optional[Path] = None, catalog_file: Optional[Path] = None):
        """
        Inizializza gestore icone
        
        Args:
            icons_dir: Directory dove salvare le icone (default: resources/icons/)
            catalog_file: File JSON catalogo icone (default: resources/icons/icons.json)
        """
        if icons_dir is None:
            base_dir = Path(__file__).parent.parent
            icons_dir = base_dir / "resources" / "icons"
        
        if catalog_file is None:
            catalog_file = icons_dir / "icons.json"
        
        self.icons_dir = Path(icons_dir)
        self.catalog_file = Path(catalog_file)
        
        # Assicura esistenza directory
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache in memoria
        self._pixmap_cache: Dict[str, QPixmap] = {}
        self._svg_cache: Dict[str, QSvgRenderer] = {}
        
        # Carica catalogo
        self.catalog: Dict[str, Dict[str, Any]] = self._load_catalog()
    
    def _load_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Carica catalogo icone da JSON"""
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Errore caricamento catalogo icone: {e}")
        
        # Catalogo vuoto
        return {}
    
    def _save_catalog(self):
        """Salva catalogo icone su JSON"""
        try:
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Errore salvataggio catalogo icone: {e}")
    
    def import_file(self, source_path: Path, icon_id: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Importa file icona e registra nel catalogo
        
        Args:
            source_path: Percorso file sorgente (SVG/PNG/JPG)
            icon_id: ID univoco (default: nome file)
            metadata: Metadati opzionali (tags, categoria, descrizione)
            
        Returns:
            ID icona importata o None se errore
        """
        source_path = Path(source_path)
        
        # Verifica esistenza file
        if not source_path.exists():
            print(f"File non trovato: {source_path}")
            return None
        
        # Verifica estensione
        ext = source_path.suffix.lower()
        if ext not in ['.svg', '.png', '.jpg', '.jpeg']:
            print(f"Formato non supportato: {ext}")
            return None
        
        # Genera ID se non fornito
        if icon_id is None:
            icon_id = source_path.stem
        
        # Genera nome file univoco se già esistente
        dest_filename = f"{icon_id}{ext}"
        dest_path = self.icons_dir / dest_filename
        counter = 1
        while dest_path.exists():
            dest_filename = f"{icon_id}_{counter}{ext}"
            dest_path = self.icons_dir / dest_filename
            counter += 1
        
        # Copia file
        try:
            shutil.copy2(source_path, dest_path)
        except IOError as e:
            print(f"Errore copia file: {e}")
            return None
        
        # Registra nel catalogo
        final_id = dest_filename.rsplit('.', 1)[0]  # Nome senza estensione
        self.catalog[final_id] = {
            'filename': dest_filename,
            'format': ext[1:],  # Senza il punto
            'original_name': source_path.name,
            'metadata': metadata or {}
        }
        
        self._save_catalog()
        
        return final_id
    
    def list_local_icons(self, category: Optional[str] = None) -> List[str]:
        """
        Elenca icone locali disponibili
        
        Args:
            category: Filtra per categoria (opzionale)
            
        Returns:
            Lista di ID icone
        """
        if category:
            return [
                icon_id for icon_id, data in self.catalog.items()
                if data.get('metadata', {}).get('category') == category
            ]
        
        return list(self.catalog.keys())
    
    def get_icon_info(self, icon_id: str) -> Optional[Dict[str, Any]]:
        """
        Ottiene informazioni su icona
        
        Args:
            icon_id: ID icona
            
        Returns:
            Dizionario con info o None se non trovata
        """
        return self.catalog.get(icon_id)
    
    def get_pixmap(self, icon_id: str, size: Optional[QSize] = None) -> Optional[QPixmap]:
        """
        Ottiene QPixmap per icona con caching
        
        Args:
            icon_id: ID icona
            size: Dimensione desiderata (opzionale, per SVG)
            
        Returns:
            QPixmap o None se errore
        """
        icon_info = self.catalog.get(icon_id)
        if not icon_info:
            return None
        
        filename = icon_info['filename']
        filepath = self.icons_dir / filename
        
        if not filepath.exists():
            return None
        
        # Cache key con dimensione
        cache_key = f"{icon_id}_{size.width()}x{size.height()}" if size else icon_id
        
        # Verifica cache
        if cache_key in self._pixmap_cache:
            return self._pixmap_cache[cache_key]
        
        # Carica in base al formato
        if icon_info['format'] == 'svg':
            pixmap = self._load_svg_pixmap(filepath, size)
        else:
            pixmap = QPixmap(str(filepath))
            if size and not pixmap.isNull():
                pixmap = pixmap.scaled(size, aspectRatioMode=1)  # KeepAspectRatio
        
        # Salva in cache
        if pixmap and not pixmap.isNull():
            self._pixmap_cache[cache_key] = pixmap
            return pixmap
        
        return None
    
    def _load_svg_pixmap(self, filepath: Path, size: Optional[QSize]) -> Optional[QPixmap]:
        """Carica SVG come QPixmap"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                svg_data = f.read()
            
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            
            if not renderer.isValid():
                return None
            
            # Usa dimensione di default se non specificata
            if size is None:
                size = renderer.defaultSize()
            
            pixmap = QPixmap(size)
            pixmap.fill(0x00000000)  # Trasparente
            
            from PyQt6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return pixmap
        except Exception as e:
            print(f"Errore caricamento SVG {filepath}: {e}")
            return None
    
    def get_svg_renderer(self, icon_id: str) -> Optional[QSvgRenderer]:
        """
        Ottiene QSvgRenderer per icona SVG con caching
        
        Args:
            icon_id: ID icona
            
        Returns:
            QSvgRenderer o None se errore o non SVG
        """
        icon_info = self.catalog.get(icon_id)
        if not icon_info or icon_info['format'] != 'svg':
            return None
        
        # Verifica cache
        if icon_id in self._svg_cache:
            return self._svg_cache[icon_id]
        
        filename = icon_info['filename']
        filepath = self.icons_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                svg_data = f.read()
            
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            
            if renderer.isValid():
                self._svg_cache[icon_id] = renderer
                return renderer
        except Exception as e:
            print(f"Errore caricamento SVG renderer {filepath}: {e}")
        
        return None
    
    def get_qicon(self, icon_id: str, size: Optional[QSize] = None) -> Optional[QIcon]:
        """
        Ottiene QIcon per uso in UI
        
        Args:
            icon_id: ID icona
            size: Dimensione (opzionale)
            
        Returns:
            QIcon o None se errore
        """
        pixmap = self.get_pixmap(icon_id, size)
        if pixmap:
            return QIcon(pixmap)
        return None
    
    def delete_icon(self, icon_id: str) -> bool:
        """
        Elimina icona dal catalogo e dal filesystem
        
        Args:
            icon_id: ID icona da eliminare
            
        Returns:
            True se eliminata con successo
        """
        icon_info = self.catalog.get(icon_id)
        if not icon_info:
            return False
        
        filename = icon_info['filename']
        filepath = self.icons_dir / filename
        
        # Rimuovi da filesystem
        try:
            if filepath.exists():
                filepath.unlink()
        except IOError as e:
            print(f"Errore eliminazione file: {e}")
            return False
        
        # Rimuovi da catalogo
        del self.catalog[icon_id]
        self._save_catalog()
        
        # Rimuovi da cache
        self._pixmap_cache = {k: v for k, v in self._pixmap_cache.items() if not k.startswith(icon_id)}
        if icon_id in self._svg_cache:
            del self._svg_cache[icon_id]
        
        return True
    
    def clear_cache(self):
        """Pulisce cache in memoria"""
        self._pixmap_cache.clear()
        self._svg_cache.clear()
    
    def update_metadata(self, icon_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Aggiorna metadati icona
        
        Args:
            icon_id: ID icona
            metadata: Nuovi metadati
            
        Returns:
            True se aggiornati con successo
        """
        if icon_id not in self.catalog:
            return False
        
        self.catalog[icon_id]['metadata'] = metadata
        self._save_catalog()
        return True
