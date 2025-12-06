"""
Test per TooltipManager - senza GUI
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_tooltips_file_exists():
    """Test che il file tooltips esista"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    assert tooltips_path.exists(), "tooltips.json not found"


def test_tooltips_file_valid():
    """Test che il file tooltips sia JSON valido"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert 'tooltips' in data


def test_tooltips_has_elements():
    """Test che ci siano tooltip per elementi"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tooltips = data['tooltips']
    assert 'elements' in tooltips
    
    # Verifica alcuni elementi base
    elements = tooltips['elements']
    assert 'Button' in elements
    assert 'Label' in elements
    assert 'MeasureDisplay' in elements


def test_tooltips_element_structure():
    """Test struttura tooltip elemento"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    button_tooltip = data['tooltips']['elements']['Button']
    assert 'title' in button_tooltip
    assert 'description' in button_tooltip


def test_tooltips_has_menus():
    """Test che ci siano tooltip per menu"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tooltips = data['tooltips']
    assert 'menus' in tooltips
    
    menus = tooltips['menus']
    assert 'file' in menus
    assert 'edit' in menus


def test_tooltips_has_hardware():
    """Test che ci siano tooltip per hardware"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tooltips = data['tooltips']
    assert 'hardware' in tooltips
    
    hardware = tooltips['hardware']
    assert 'encoder' in hardware
    assert 'puntale' in hardware
    assert 'bluetooth' in hardware


def test_tooltips_has_shortcuts():
    """Test che ci siano shortcuts"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tooltips = data['tooltips']
    assert 'shortcuts' in tooltips
    
    shortcuts = tooltips['shortcuts']
    assert 'global' in shortcuts
    assert 'canvas' in shortcuts


def test_tooltips_has_guides():
    """Test che ci siano guide"""
    base_dir = Path(__file__).parent.parent
    tooltips_path = base_dir / "resources" / "guides" / "tooltips.json"
    
    with open(tooltips_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert 'guides' in data
    guides = data['guides']
    assert 'getting_started' in guides
    assert 'best_practices' in guides


if __name__ == "__main__":
    print("Running tooltip manager tests...")
    
    test_tooltips_file_exists()
    print("✓ test_tooltips_file_exists")
    
    test_tooltips_file_valid()
    print("✓ test_tooltips_file_valid")
    
    test_tooltips_has_elements()
    print("✓ test_tooltips_has_elements")
    
    test_tooltips_element_structure()
    print("✓ test_tooltips_element_structure")
    
    test_tooltips_has_menus()
    print("✓ test_tooltips_has_menus")
    
    test_tooltips_has_hardware()
    print("✓ test_tooltips_has_hardware")
    
    test_tooltips_has_shortcuts()
    print("✓ test_tooltips_has_shortcuts")
    
    test_tooltips_has_guides()
    print("✓ test_tooltips_has_guides")
    
    print("\n✓ All tooltip tests passed!")
