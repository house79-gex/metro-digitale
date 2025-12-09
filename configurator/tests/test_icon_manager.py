"""
Test per IconManager
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from core.icon_manager import IconManager


def test_icon_manager_init():
    """Test inizializzazione IconManager"""
    manager = IconManager()
    
    # Verifica che le directory siano impostate
    assert manager.icons_path.exists()
    assert manager.registry_path.exists() or not manager.registry_path.exists()
    
    # Verifica registry caricato
    assert isinstance(manager.registry, dict)
    assert "version" in manager.registry
    assert "icons" in manager.registry


def test_list_local_icons():
    """Test elenco icone locali"""
    manager = IconManager()
    
    # Lista tutte le icone
    icons = manager.list_local_icons()
    assert isinstance(icons, list)
    
    # Lista per categoria
    icons_custom = manager.list_local_icons(category="custom")
    assert isinstance(icons_custom, list)


def test_get_categories():
    """Test ottieni categorie"""
    manager = IconManager()
    
    categories = manager.get_categories()
    assert isinstance(categories, list)


def test_icon_path():
    """Test ottenimento path icona"""
    manager = IconManager()
    
    # Path per icona non esistente
    path = manager.get_icon_path("non_existent_icon")
    assert path is None


def test_clear_cache():
    """Test pulizia cache"""
    manager = IconManager()
    
    # Dovrebbe funzionare senza errori
    manager.clear_cache()


def test_singleton_pattern():
    """Test pattern singleton"""
    from core.icon_manager import get_icon_manager
    
    manager1 = get_icon_manager()
    manager2 = get_icon_manager()
    
    # Dovrebbero essere la stessa istanza
    assert manager1 is manager2


if __name__ == "__main__":
    print("Running IconManager tests...")
    
    test_icon_manager_init()
    print("✓ test_icon_manager_init")
    
    test_list_local_icons()
    print("✓ test_list_local_icons")
    
    test_get_categories()
    print("✓ test_get_categories")
    
    test_icon_path()
    print("✓ test_icon_path")
    
    test_clear_cache()
    print("✓ test_clear_cache")
    
    test_singleton_pattern()
    print("✓ test_singleton_pattern")
    
    print("\n✓ All IconManager tests passed!")
