"""
Test per icon_browser con nuova API Iconify
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.icon_browser import IconifyClient, IconInfo


def test_icon_info_creation():
    """Test creazione IconInfo"""
    icon = IconInfo("home", "mdi")
    assert icon.name == "home"
    assert icon.prefix == "mdi"
    assert icon.full_name == "mdi:home"


def test_fallback_icons():
    """Test icone fallback"""
    client = IconifyClient()
    assert len(client.FALLBACK_ICONS) == 15
    
    # Test empty query returns fallback
    results = client.search("", limit=5)
    assert len(results) == 5
    assert all(isinstance(icon, IconInfo) for icon in results)


def test_fallback_search():
    """Test ricerca fallback"""
    client = IconifyClient()
    
    # Cerca 'home' nei fallback
    results = client._search_fallback("home", limit=10)
    assert len(results) > 0
    assert any("home" in icon.name.lower() for icon in results)
    
    # Cerca qualcosa che non esiste
    results = client._search_fallback("zzznonexistent", limit=10)
    # Dovrebbe ritornare tutti i fallback come default
    assert len(results) == 10


def test_icon_sets():
    """Test lista icon sets"""
    client = IconifyClient()
    sets = client.get_icon_sets()
    assert len(sets) == 9
    assert ("mdi", "Material Design Icons") in sets
    assert ("tabler", "Tabler Icons") in sets


def test_search_returns_icon_info():
    """Test che search ritorna sempre IconInfo objects"""
    client = IconifyClient()
    results = client.search("button", limit=5)
    assert isinstance(results, list)
    assert all(isinstance(icon, IconInfo) for icon in results)


def test_svg_requires_colon():
    """Test che get_svg richiede formato prefix:name"""
    client = IconifyClient()
    
    # Senza ':' dovrebbe ritornare None
    svg = client.get_svg("home")
    assert svg is None


if __name__ == "__main__":
    print("Running icon_browser tests...")
    test_icon_info_creation()
    print("✓ test_icon_info_creation")
    
    test_fallback_icons()
    print("✓ test_fallback_icons")
    
    test_fallback_search()
    print("✓ test_fallback_search")
    
    test_icon_sets()
    print("✓ test_icon_sets")
    
    test_search_returns_icon_info()
    print("✓ test_search_returns_icon_info")
    
    test_svg_requires_colon()
    print("✓ test_svg_requires_colon")
    
    print("\n✓ All icon_browser tests passed!")
