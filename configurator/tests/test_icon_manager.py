"""
Test per IconManager
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
import tempfile
import shutil
from core.icon_manager import IconManager


def test_icon_manager_initialization():
    """Test inizializzazione IconManager"""
    with tempfile.TemporaryDirectory() as tmpdir:
        icons_dir = Path(tmpdir) / "icons"
        manager = IconManager(icons_dir=icons_dir)
        
        # Verifica creazione directory
        assert icons_dir.exists()
        
        # Verifica file catalogo
        catalog_file = icons_dir / "icons.json"
        assert catalog_file.exists()


def test_icon_manager_import_svg():
    """Test import file SVG"""
    with tempfile.TemporaryDirectory() as tmpdir:
        icons_dir = Path(tmpdir) / "icons"
        manager = IconManager(icons_dir=icons_dir)
        
        # Crea file SVG test
        svg_content = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
        test_file = Path(tmpdir) / "test.svg"
        with open(test_file, 'w') as f:
            f.write(svg_content)
        
        # Import
        icon_id = manager.import_file(test_file)
        
        assert icon_id is not None
        assert icon_id in manager.catalog
        
        # Verifica file copiato
        icon_info = manager.get_icon_info(icon_id)
        assert icon_info is not None
        assert icon_info['format'] == 'svg'


def test_icon_manager_list_icons():
    """Test lista icone locali"""
    with tempfile.TemporaryDirectory() as tmpdir:
        icons_dir = Path(tmpdir) / "icons"
        manager = IconManager(icons_dir=icons_dir)
        
        # Crea e importa alcuni file
        for i in range(3):
            test_file = Path(tmpdir) / f"icon_{i}.svg"
            with open(test_file, 'w') as f:
                f.write(f'<svg><text>{i}</text></svg>')
            
            manager.import_file(test_file, icon_id=f"icon_{i}")
        
        # Lista icone
        icons = manager.list_local_icons()
        assert len(icons) == 3
        assert "icon_0" in icons
        assert "icon_1" in icons
        assert "icon_2" in icons


def test_icon_manager_delete_icon():
    """Test eliminazione icona"""
    with tempfile.TemporaryDirectory() as tmpdir:
        icons_dir = Path(tmpdir) / "icons"
        manager = IconManager(icons_dir=icons_dir)
        
        # Import icona
        test_file = Path(tmpdir) / "test.svg"
        with open(test_file, 'w') as f:
            f.write('<svg></svg>')
        
        icon_id = manager.import_file(test_file)
        assert icon_id in manager.catalog
        
        # Elimina
        success = manager.delete_icon(icon_id)
        assert success
        assert icon_id not in manager.catalog


def test_icon_manager_metadata():
    """Test gestione metadata"""
    with tempfile.TemporaryDirectory() as tmpdir:
        icons_dir = Path(tmpdir) / "icons"
        manager = IconManager(icons_dir=icons_dir)
        
        # Import con metadata
        test_file = Path(tmpdir) / "test.svg"
        with open(test_file, 'w') as f:
            f.write('<svg></svg>')
        
        metadata = {
            'category': 'custom',
            'tags': ['test', 'example']
        }
        
        icon_id = manager.import_file(test_file, metadata=metadata)
        
        # Verifica metadata
        icon_info = manager.get_icon_info(icon_id)
        assert icon_info['metadata'] == metadata
        
        # Aggiorna metadata
        new_metadata = {'category': 'updated'}
        manager.update_metadata(icon_id, new_metadata)
        
        icon_info = manager.get_icon_info(icon_id)
        assert icon_info['metadata'] == new_metadata


if __name__ == "__main__":
    print("Running IconManager tests...")
    
    test_icon_manager_initialization()
    print("✓ test_icon_manager_initialization")
    
    test_icon_manager_import_svg()
    print("✓ test_icon_manager_import_svg")
    
    test_icon_manager_list_icons()
    print("✓ test_icon_manager_list_icons")
    
    test_icon_manager_delete_icon()
    print("✓ test_icon_manager_delete_icon")
    
    test_icon_manager_metadata()
    print("✓ test_icon_manager_metadata")
    
    print("\nAll tests passed!")
